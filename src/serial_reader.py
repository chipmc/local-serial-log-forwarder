import serial
import time
from datetime import datetime

SERIAL_PORT = "/dev/serial/by-id/usb-Particle_Boron_CDC_Mode_e00fce688e592afaf23ac4fb-if00"
BAUD_RATE = 115200
LOG_FILE = "/var/log/serial-forwarder/boron-test.log"


def log_line(line):
    timestamp = datetime.utcnow().isoformat()
    entry = f"{timestamp} {line}"

    print(entry)

    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


while True:
    try:
        print(f"Connecting to {SERIAL_PORT}...")
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print("Connected.")

            while True:
                line = ser.readline().decode(errors="replace").strip()
                if line:
                    log_line(line)

    except Exception as e:
        print(f"Disconnected: {e}")
        time.sleep(5)
