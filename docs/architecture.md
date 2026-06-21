Architecture

Objective

Provide persistent raw forensic telemetry for Particle devices independent of Particle Cloud.

⸻

Components

Collector

Raspberry Pi 4

Responsibilities:

* maintain serial connections
* detect sleep/wake disconnects
* capture logs
* forward to AWS

⸻

Device Identity

Uses:

/dev/serial/by-id/

Never:

/dev/ttyACM*

This provides stable identity across reconnects.

⸻

Runtime

Python:

src/serial_reader.py

Thread model:

one thread per device

⸻

Service Management

systemd:

/etc/systemd/system/serial-forwarder.service

Environment:

/etc/serial-forwarder.env

⸻

Storage

Local:

/var/log/serial-forwarder/

Cloud:

S3 raw archive

DynamoDB event index

⸻

Event Types

Lifecycle:

* SERIAL_CONNECTING
* SERIAL_CONNECTED
* SERIAL_DISCONNECTED
* SERIAL_MISSING

Telemetry:

* LOG

⸻

Failure Modes

Device sleeps

Expected:

SERIAL_DISCONNECTED
SERIAL_MISSING

Recovery:

automatic reconnect

⸻

Pi reboot

Expected:

systemd restarts collector

⸻

Network unavailable

Expected:

AWS POST failures

Local logs preserved.
