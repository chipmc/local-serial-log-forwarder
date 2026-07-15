Serial Forwarder Operations Guide

This document is the day-to-day operational runbook for the Raspberry Pi Serial Forwarder. It complements the engineering reference in serial-forwarder-handoff.md and focuses on routine operation, monitoring, and recovery.

⸻

Repository

Always begin work from the repository root.

cd /opt/serial-forwarder

⸻

SSH to the Raspberry Pi

From your Mac:

ssh chip@serial-forwarder.local

If mDNS is unavailable, connect using the Pi’s IP address.

⸻

Service Management

Check Status

cd /opt/serial-forwarder
systemctl status serial-forwarder.service --no-pager -l

Expected:

Active: active (running)

Restart

Restart after:

* Changing config/devices.json
* Updating Python source
* Updating environment variables

cd /opt/serial-forwarder
sudo systemctl restart serial-forwarder.service

Stop

cd /opt/serial-forwarder
sudo systemctl stop serial-forwarder.service

Start

cd /opt/serial-forwarder
sudo systemctl start serial-forwarder.service

⸻

Live Monitoring

Follow Service Logs

cd /opt/serial-forwarder
journalctl -u serial-forwarder.service -f -l

Exit with Ctrl+C.

Show Recent Activity

cd /opt/serial-forwarder
journalctl -u serial-forwarder.service \
    -n 100 \
    --no-pager \
    -l

⸻

Device Management

View Configured Devices

cd /opt/serial-forwarder
python3 -m json.tool config/devices.json

View Connected USB Devices

cd /opt/serial-forwarder
ls -la /dev/serial/by-id/

Always configure devices using the stable /dev/serial/by-id/ path.

Do not use /dev/ttyACM0, /dev/ttyACM1, or other dynamically assigned device names.

⸻

Adding a Device

1. Connect the Particle device with a USB data cable.
2. Verify Linux detects it:

cd /opt/serial-forwarder
ls -la /dev/serial/by-id/

3. Edit:

cd /opt/serial-forwarder
nano config/devices.json

4. Add a new entry:

{
    "name": "Boron-Dev-15",
    "path": "/dev/serial/by-id/usb-Particle_Boron_CDC_Mode_<DEVICE-ID>-if00"
}

5. Validate the JSON:

cd /opt/serial-forwarder
python3 -m json.tool config/devices.json >/dev/null

6. Restart the service:

cd /opt/serial-forwarder
sudo systemctl restart serial-forwarder.service

7. Verify connection:

cd /opt/serial-forwarder
journalctl -u serial-forwarder.service -n 40 --no-pager -l

Expected events:

SERIAL_CONNECTING
SERIAL_CONNECTED
LOG

⸻

Renaming a Device

Edit only the name field in:

config/devices.json

Do not change the USB path unless the hardware has changed.

After editing:

cd /opt/serial-forwarder
python3 -m json.tool config/devices.json >/dev/null
sudo systemctl restart serial-forwarder.service

Renaming affects:

* Local log filename
* Journal output
* Cloud deviceName

It does not change:

* Particle Device ID
* USB identity
* Historical events

⸻

Viewing Logs

Follow a Device Log

tail -f /var/log/serial-forwarder/Boron-Dev-14.log

Recent Entries

tail -n 100 /var/log/serial-forwarder/Boron-Dev-14.log

Search Current Logs

grep -n "ERROR" /var/log/serial-forwarder/Boron-Dev-14.log

Search Archived Logs

zgrep -n "watchdog" /var/log/serial-forwarder/Boron-Dev-14.log.*.gz

⸻

Cloud Forwarding

Check for forwarding failures:

cd /opt/serial-forwarder
journalctl -u serial-forwarder.service \
    --since "30 minutes ago" \
    --no-pager -l \
    | grep AWS_POST_FAILED

No output indicates no forwarding failures were logged during the selected period.

⸻

Common Problems

SERIAL_MISSING

Usually indicates:

* Device is asleep
* USB cable disconnected
* Device is unpowered
* Incorrect USB path
* Hardware replacement

Verify:

ls -la /dev/serial/by-id/

⸻

Repeated Connect / Disconnect

Possible causes:

* Normal firmware sleep
* Firmware reset
* USB cable or hub issue
* Another process using the serial port

Inspect:

journalctl -u serial-forwarder.service -n 100 --no-pager -l

⸻

Local Logs Present but Nothing in AWS

Check for POST failures:

journalctl -u serial-forwarder.service \
    --since "30 minutes ago" \
    --no-pager -l \
    | grep AWS_POST_FAILED

Then verify:

* Network connectivity
* AWS endpoint
* Webhook secret
* Unified Telemetry Platform

⸻

Service Will Not Start

Validate configuration:

cd /opt/serial-forwarder
python3 -m json.tool config/devices.json

Review service status:

systemctl status serial-forwarder.service --no-pager -l

Review recent logs:

journalctl -u serial-forwarder.service -n 100 --no-pager -l

⸻

Git Workflow

Check status:

cd /opt/serial-forwarder
git status

Review changes:

cd /opt/serial-forwarder
git diff

Pull latest changes:

cd /opt/serial-forwarder
git pull

Commit:

cd /opt/serial-forwarder
git add <files>
git commit -m "<description>"

Push (run separately):

cd /opt/serial-forwarder
git push origin main

⸻

Post-Change Checklist

After every configuration or source-code change:

* Validate config/devices.json
* Restart the service
* Confirm the service is running
* Confirm USB devices are detected
* Confirm SERIAL_CONNECTED
* Confirm local logs are updating
* Confirm no unexpected AWS_POST_FAILED
* Confirm events appear in the Unified Telemetry Platform
* Review git diff
* Commit only after successful validation
