"""Flood guard tests. Stdlib only: serial and requests are faked, nothing touches the Pi."""
import os
import re
import sys
import types
import unittest
from unittest import mock

sys.modules.setdefault("serial", types.ModuleType("serial"))
sys.modules.setdefault("requests", types.ModuleType("requests"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
with mock.patch("builtins.open", mock.mock_open(read_data="[]")):
    import serial_reader as sr  # devices.json is read at import; [] starts no threads


class Stop(BaseException):
    """Ends monitor_device's endless loop; not caught by its `except Exception`."""


def timediag(i, tail=""):
    return f"{291620 + i:010d} [app] INFO: TimeDiag: tz=SGT-8 valid=1 epoch={1791527478 + i} utc=2026-10-09{tail}"


def sensor(i):
    return f"{300000 + i:010d} [app] INFO: Sensor: count={i}"


OTHER = "0000400000 [app] INFO: Battery: soc=87"


def summary(n):
    return f"[forwarder] INFO: previous line repeated {n} times"


class FloodGuardTest(unittest.TestCase):
    def run_sessions(self, *sessions):
        """Each session is one open port: a list of lines, b"" for a silent read,
        or (seconds, line) to set the clock. A session ends with a disconnect."""
        self.posted, self.file, clock, queue = [], [], [0.0], list(sessions)

        class FakeSerial:
            def __init__(self, *args, **kwargs):
                if not queue:
                    raise Stop()
                self.items = list(queue.pop(0))
            def __enter__(self):
                return self
            def __exit__(self, *exc):
                return False
            def readline(self):
                if not self.items:
                    raise OSError("device unplugged")
                item = self.items.pop(0)
                if isinstance(item, tuple):
                    clock[0], item = item
                return item if isinstance(item, bytes) else (item + "\n").encode()

        def post(url, json, headers, timeout):
            self.posted.append((json["eventType"], json["logLine"]))
            return types.SimpleNamespace(status_code=200, text="")

        def fake_open(path, mode, buffering):
            return mock.MagicMock(**{"__enter__.return_value.write": lambda s: self.file.append(s)})

        sr.serial.Serial = FakeSerial
        sr.requests.post = post
        with mock.patch.object(sr, "time", types.SimpleNamespace(sleep=lambda s: None, monotonic=lambda: clock[0])), \
                mock.patch.object(sr.os.path, "exists", return_value=True), \
                mock.patch.object(sr, "open", fake_open, create=True), \
                mock.patch.object(sr, "print", lambda *a, **k: None, create=True), \
                self.assertRaises(Stop):
            sr.monitor_device({"name": "Boron-Test", "path": "/dev/serial/by-id/usb-Particle_e00fce68-if00"})

        sent = list(sessions_lines(sessions))
        self.assertEqual([e.split(" LOG ", 1)[1].rstrip("\n") for e in self.file if " LOG " in e], sent,
                         "local file must keep every line")
        return [line if kind == "LOG" else kind for kind, line in self.posted
                if kind not in ("SERIAL_CONNECTING", "SERIAL_CONNECTED")]

    def test_three_line_run_real_fixture(self):
        lines = [timediag(0), timediag(10), timediag(19)]
        self.assertEqual(self.run_sessions(lines + [OTHER]),
                         [lines[0], summary(1), lines[2], OTHER, "SERIAL_DISCONNECTED"])
        severity = re.search(r"\b(TRACE|INFO|WARN|ERROR)\b", summary(1), re.I).group(1)
        self.assertEqual(severity, "INFO")
        self.assertNotIn("TimeDiag", summary(1))

    def test_thousand_line_run(self):
        lines = [timediag(i) for i in range(1000)]
        self.assertEqual(self.run_sessions(lines + [OTHER]),
                         [lines[0], summary(998), lines[999], OTHER, "SERIAL_DISCONNECTED"])

    def test_run_of_two_sends_both(self):
        self.assertEqual(self.run_sessions([timediag(0), timediag(1), OTHER]),
                         [timediag(0), timediag(1), OTHER, "SERIAL_DISCONNECTED"])

    def test_two_runs_back_to_back(self):
        a, b = [timediag(i) for i in range(5)], [sensor(i) for i in range(4)]
        self.assertEqual(self.run_sessions(a + b + [OTHER]),
                         [a[0], summary(3), a[4], b[0], summary(2), b[3], OTHER, "SERIAL_DISCONNECTED"])

    def test_disconnect_and_reconnect_mid_run(self):
        a = [timediag(i) for i in range(8)]
        self.assertEqual(self.run_sessions(a[:5], a[5:] + [OTHER]),
                         [a[0], summary(3), a[4], "SERIAL_DISCONNECTED",
                          a[5], summary(1), a[7], OTHER, "SERIAL_DISCONNECTED"])

    def test_silence_ends_run(self):
        a = [timediag(i) for i in range(7)]
        self.assertEqual(self.run_sessions(a[:5] + [b""] + a[5:] + [OTHER]),
                         [a[0], summary(3), a[4], a[5], a[6], OTHER, "SERIAL_DISCONNECTED"])

    def test_warn_inside_run_breaks_it(self):
        a = [timediag(i) for i in range(6)]
        warn = "0000291700 [app] WARN: TimeDiag: tz=SGT-8 valid=0 epoch=0 utc=1970-01-01"
        self.assertEqual(self.run_sessions(a[:3] + [warn] + a[3:] + [OTHER]),
                         [a[0], summary(1), a[2], warn, a[3], summary(1), a[5], OTHER, "SERIAL_DISCONNECTED"])

    def test_lines_differing_only_after_char_80_collapse(self):
        a = [timediag(i, tail) for i, tail in enumerate([" src=gps~", " src=ntp~", " src=rtc~"])]
        self.assertEqual(self.run_sessions(a + [OTHER]),
                         [a[0], summary(1), a[2], OTHER, "SERIAL_DISCONNECTED"])

    def test_endless_run_sends_every_60_seconds(self):
        # One line every 0.5 s for 130 s with no silence: 261 lines.
        a = [timediag(i) for i in range(261)]
        self.assertEqual(self.run_sessions([(i * 0.5, line) for i, line in enumerate(a)]),
                         [a[0], summary(119), a[120],     # run starts at 0 s, sent at 60 s
                          a[121], summary(119), a[241],   # 60.5 s to 120.5 s
                          a[242], summary(17), a[260],    # ended by the disconnect
                          "SERIAL_DISCONNECTED"])


def sessions_lines(sessions):
    for session in sessions:
        for item in session:
            line = item[1] if isinstance(item, tuple) else item
            if line != b"":
                yield line


if __name__ == "__main__":
    unittest.main()
