Local Serial Log Forwarder

Local USB serial collector for Particle devices.

Captures:

* boot logs
* sleep/wake transitions
* modem lifecycle
* cloud reconnects
* watchdog traces
* runtime diagnostics

Publishes raw serial telemetry into the unified AWS telemetry backbone.

Current topology

Particle Devices
    ↓ USB Serial
Powered USB Hub
    ↓
Raspberry Pi 4
    ↓
systemd service
    ↓
Local rotating logs
    ↓
AWS API Gateway
    ↓
Lambda
    ↓
S3 + DynamoDB

Devices

Current:

* boron-soak-1
* photon2-soak-1

Configured in:

config/devices.json

Service

Managed by:

serial-forwarder.service

Commands:

systemctl status serial-forwarder
journalctl -u serial-forwarder -f
sudo systemctl restart serial-forwarder
sudo reboot

Logs

Location:

/var/log/serial-forwarder/

Rotated daily.

Retention:

14 days compressed.

AWS

Endpoint:

https://dqqrzw16gk.execute-api.us-east-1.amazonaws.com/particle/log

Auth:

x-particle-webhook-secret

Stored in:

/etc/serial-forwarder.env

Repo

GitHub:

git@github.com:chipmc/local-serial-log-forwarder.git
