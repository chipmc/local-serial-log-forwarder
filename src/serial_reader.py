import os
import time
import json
import serial
import threading
import requests
from datetime import datetime, UTC

CONFIG_FILE = "/opt/serial-forwarder/config/devices.json"
WEBHOOK_SECRET = os.environ.get("PARTICLE_WEBHOOK_SECRET")
API_KEY = os.environ.get("AWS_API_KEY")
BAUD_RATE = 115200

API_URL = "https://ingest.seeinsights.com/particle/log"

COLLECTOR_ID = "serial-forwarder-pi-01"


def utc_now():
    return datetime.now(UTC).isoformat()

def post_to_api(device_name, device_id, event_type, message):
    payload = {
        "event": "serialLog",
        "sourceType": "serial-forwarder",
        "collectorId": COLLECTOR_ID,
        "transport": "usb-serial",
        "deviceName": device_name,
        "deviceId": device_id,
        "eventType": event_type,
        "timestamp": utc_now(),
        "logLine": message
    }

    headers = {}

    if WEBHOOK_SECRET:
        headers["x-particle-webhook-secret"] = WEBHOOK_SECRET

    if API_KEY:
        headers["x-api-key"] = API_KEY

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=3
        )

        if response.status_code >= 300:
            print(
                f"AWS_POST_FAILED: status={response.status_code} body={response.text[:200]}",
                flush=True
            )

    except Exception as e:
        print(f"AWS_POST_FAILED: {e}", flush=True)


def write_log(device_name, device_id, event_type, message):
    log_file = f"/var/log/serial-forwarder/{device_name}.log"
    entry = f"{utc_now()} {device_name} {event_type} {message}"

    print(entry, flush=True)

    with open(log_file, "a", buffering=1) as f:
        f.write(entry + "\n")

    post_to_api(device_name, device_id, event_type, message)


def monitor_device(device):
    name = device["name"]
    path = device["path"]
    device_id = path.split("_")[-1].replace("-if00", "").replace("-if01", "")
    last_state = None

    while True:
        if not os.path.exists(path):
            if last_state != "missing":
                write_log(name, device_id, "SERIAL_MISSING", path)
                last_state = "missing"
            time.sleep(2)
            continue

        try:
            write_log(name, device_id, "SERIAL_CONNECTING", path)

            with serial.Serial(path, BAUD_RATE, timeout=1) as ser:
                write_log(name, device_id, "SERIAL_CONNECTED", path)
                last_state = "connected"

                while True:
                    raw = ser.readline()
                    if not raw:
                        continue

                    line = raw.decode(errors="replace").strip()
                    if line:
                        write_log(name, device_id, "LOG", line)

        except Exception as e:
            write_log(name, device_id, "SERIAL_DISCONNECTED", repr(e))
            last_state = "disconnected"
            time.sleep(2)


def safe_monitor_device(device):
    """Wrap device monitoring to catch thread crashes and log them prominently.

    One device's failure must not cascade to other devices. If this thread crashes,
    log the error clearly so operators can discover it via standard monitoring commands,
    then exit to trigger systemd auto-restart.
    """
    name = device["name"]
    try:
        monitor_device(device)
    except Exception as e:
        error_msg = f"THREAD_CRASH: {name} monitoring thread exited: {type(e).__name__}: {e}"
        print(error_msg, flush=True)

        # Also try to write to device log (if write_log itself works)
        try:
            device_id = device["path"].split("_")[-1].replace("-if00", "").replace("-if01", "")
            write_log(name, device_id, "THREAD_CRASH", str(e))
        except Exception as write_error:
            # If write_log is broken, at least the print() went to journalctl
            print(f"WARNING: Could not write THREAD_CRASH to device log: {write_error}", flush=True)

        # Re-raise so systemd notices the process exited abnormally and restarts
        raise


with open(CONFIG_FILE) as f:
    devices = json.load(f)

threads = []

for device in devices:
    t = threading.Thread(target=safe_monitor_device, args=(device,), daemon=True)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
