import os
import time
import serial
from datetime import datetime, UTC

DEVICE_NAME = "boron-test"
SERIAL_PORT = "/dev/serial/by-id/usb-Particle_Boron_CDC_Mode_e00fce688e592afaf23ac4fb-if00"
BAUD_RATE = 115200
LOG_FILE = f"/var/log/serial-forwarder/{DEVICE_NAME}.log"

last_state = None


def utc_now():
    return datetime.now(UTC).isoformat()


def write_log(event_type, message):
    entry = f"{utc_now()} {DEVICE_NAME} {event_type} {message}"
    print(entry, flush=True)
    with open(LOG_FILE, "a", buffering=1) as f:
        f.write(entry + "\n")


while True:
    if not os.path.exists(SERIAL_PORT):
        if last_state != "missing":
            write_log("SERIAL_MISSING", SERIAL_PORT)
            last_state = "missing"
        time.sleep(2)
        continue

    try:
        write_log("SERIAL_CONNECTING", SERIAL_PORT)
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            write_log("SERIAL_CONNECTED", SERIAL_PORT)
            last_state = "connected"

            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode(errors="replace").strip()
                if line:
                    write_log("LOG", line)

    except Exception as e:
        write_log("SERIAL_DISCONNECTED", repr(e))
        last_state = "disconnected"
        time.sleep(2)
