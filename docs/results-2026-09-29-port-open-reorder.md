# Results: Port-Open Reorder (2026-09-29)

Measured effect of commit 7312c16, which opens the serial port before posting SERIAL_CONNECTING and SERIAL_CONNECTED. Also records where the "..." seen on long serial lines comes from.

⸻

Summary

On sleep wakes, the port now opens a median 1.17 s after USB enumeration, down from 2.54 s. The first captured line is emitted about 1.3 to 1.6 s sooner. Short wakes (the device leaves within about 2 s) now show up as sessions with no captured lines instead of failed opens, and the share of connect attempts that capture nothing fell from 21.8% to 12.7%. There were no POST failures, crashes, or restarts after the change.

Wakes that end within about 2 seconds are still missed. This change was not expected to fix those.

⸻

Method

* Before: 2026-09-21 00:00 UTC to the restart at 2026-09-28 05:34:11 UTC (old code).
* After: 2026-09-28 05:34:11 UTC to 2026-09-29 05:34:11 UTC (new code).
* Devices: Boron-Dev-09, Boron-Dev-11, Boron-Dev-14.
* Sources: /var/log/serial-forwarder/*.log*, the kernel log for USB enumeration times (journalctl -k, "new full-speed" and "SerialNumber" lines), and the service journal.
* Port-open marker: SERIAL_CONNECTED before the change, SERIAL_CONNECTING after it (see "Missing Log Line: Device or Forwarder?" in operations.md).
* Emission time of a line comes from the device's 10-digit millisecond prefix, converted to wall time with the smallest (wall time minus millis) offset seen in the session. That prefix keeps counting through sleep and resets only on a cold boot.

⸻

Results

Medians, all three devices. Figures for Dev-09 and Dev-11 alone are in brackets, because Dev-14 was nearly idle in the after window.

| Metric | Before | After | Change |
|---|---|---|---|
| USB enumeration to port open (sleep wakes) | 2.54 s (2.52), n=1301 | 1.17 s (1.33), n=87 | -1.37 s |
| USB enumeration to first line emitted (sleep wakes) | 4.83 s (4.84) | 3.55 s (3.25) | -1.28 s |
| SERIAL_CONNECTING to first line emitted | 3.39 s (3.46) | 2.06 s (1.98) | -1.33 s |
| SERIAL_CONNECTING to first line read by the Pi | 3.52 s (3.62) | 2.66 s (2.55) | -0.86 s |
| SERIAL_CONNECTING to SERIAL_CONNECTED | 1.02 s | 1.21 s (1.20) | +0.19 s |
| Port open to first line emitted | 2.18 s (2.31) | 2.06 s (1.98) | about the same |

p90, USB enumeration to port open: 3.64 s before, 2.13 s after. p90, USB enumeration to first line emitted: 9.91 s before, 4.85 s after.

The SERIAL_CONNECTING rows are not directly comparable, because that event now marks the port opening rather than about 1 s before it. SERIAL_CONNECTING to SERIAL_CONNECTED is now exactly one POST. It was slightly slower in the after window, which is network variation.

Cold boots: 34 clean boots before, 1 after. The one boot reached port open 2.30 s after power-up (median before: 3.63 s). Power-up to USB enumeration is typically about 0.8 s.

Other checks:

* Failed opens: 339 before, 0 after. All 339 were "could not open port ... [Errno 2]": the device disappeared during the POST that used to come before the open.
* Sessions with no captured lines: 37 before, 13 after. These are the same short wakes, now reaching an open port.
* After the change: 0 AWS_POST_FAILED, 0 THREAD_CRASH or tracebacks, 0 service restarts.

Limits: the after window had about half the usual wake rate (102 sessions against about 192 per day before), no Dev-11 out-of-memory storm, and only 87 sleep wakes. Medians are reasonably stable; p90 and max values are loose.

⸻

Long Lines Ending in "..."

Long serial lines are stored in full. The "..." is added only when the telemetry CLI in particle-fleet-operations displays them: any line over 160 characters is shown as its first 157 characters plus "...". Use telemetry serial --raw (or --full) to see whole lines.

Checked by comparing three lines of 165 to 182 characters between the local log and DynamoDB. The logLine and serialLogLine fields both matched the local log exactly.

The ingestion Lambda caps the derived serialLogLine field at 500 characters with a plain cut. The raw logLine field has no cap. The longest line seen in the after window was 182 characters, so the cap has not been reached.

A line ending in "~" was shortened by the device firmware before it was sent. It is stored as the device sent it.
