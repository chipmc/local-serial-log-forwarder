# Serial Forwarder Engineering Handoff

**Repository:** `chipmc/local-serial-log-forwarder`

**Purpose**

The Serial Forwarder is the edge collection component of the See Insights telemetry platform. It runs on a Raspberry Pi and continuously monitors the USB serial output of connected Particle devices. Its primary responsibilities are to:

- Maintain reliable USB serial connections.
- Capture raw serial output without modification.
- Generate connection lifecycle events.
- Preserve local forensic logs.
- Forward structured events to the Unified Telemetry Platform.

The Serial Forwarder intentionally performs no cloud analytics or fleet intelligence. It should be treated as a lightweight edge collector whose only responsibility is reliable acquisition and forwarding of serial telemetry.

---

# System Architecture

```
Particle Firmware
        │
        │ USB Serial
        ▼
+---------------------------+
| Raspberry Pi              |
| Serial Forwarder          |
|                           |
| • Device discovery        |
| • Serial monitoring       |
| • Local logging           |
| • Event generation        |
| • HTTP forwarding         |
+---------------------------+
        │
        │ HTTPS POST
        ▼
+---------------------------+
| Unified Telemetry Platform|
|                           |
| • Ingestion               |
| • Storage                 |
| • Fleet APIs              |
| • Analytics               |
+---------------------------+
```

---

# Engineering Boundaries

The project is intentionally separated into three independent engineering repositories.

## Particle Firmware

Responsible for:

- Device behavior
- Power management
- Sensor logic
- Logging
- Telemetry generation

## Serial Forwarder

Responsible for:

- USB device management
- Stable device identity
- Serial capture
- Local logging
- Event generation
- Reliable forwarding

## Unified Telemetry Platform

Responsible for:

- Cloud ingestion
- Event storage
- Fleet intelligence
- Device timelines
- Analytics
- Dashboards

The Serial Forwarder treats the Unified Telemetry Platform as an external HTTP API and should not contain cloud business logic.

---

# Current Implementation

The current implementation consists of:

- Raspberry Pi 4
- Python 3.13
- One monitoring thread per configured device
- Stable `/dev/serial/by-id` device mapping
- Local per-device log files
- Immediate HTTPS POST of every event
- systemd-managed service
- Configuration stored in `config/devices.json`
- Secrets stored outside the repository in `/etc/serial-forwarder.env`

---

# Repository Layout

```
/opt/serial-forwarder
├── config/
│   └── devices.json
├── docs/
│   ├── architecture.md
│   ├── backlog.md
│   └── serial-forwarder-handoff.md
├── src/
│   └── serial_reader.py        
├── README.md
└── venv/  
```

# Raspberry Pi Environment

## Runtime Environment

The Serial Forwarder is installed directly on a Raspberry Pi and managed as a long-running system service.

| Item | Value |
|------|-------|
| Hostname | `serial-forwarder` |
| User | `chip` |
| Repository | `/opt/serial-forwarder` |
| Python | 3.13 |
| Node.js | Not required |
| Virtual Environment | `/opt/serial-forwarder/venv` |

The repository should always be accessed from:

```bash
cd /opt/serial-forwarder
```

---

# Service Management

The forwarder runs under **systemd**.

Main service:

```text
/etc/systemd/system/serial-forwarder.service
```

Environment overrides:

```text
/etc/systemd/system/serial-forwarder.service.d/override.conf
```

Secrets:

```text
/etc/serial-forwarder.env
```

Current environment variables:

- `PARTICLE_WEBHOOK_SECRET`

Secrets are intentionally stored outside the Git repository.

---

# Startup

At boot:

1. Raspberry Pi starts.
2. Network becomes available.
3. systemd launches the Serial Forwarder.
4. Configuration is loaded.
5. One monitoring thread starts for every configured device.

If the process exits unexpectedly, systemd automatically restarts it after five seconds.

---

# Repository Structure

```
/opt/serial-forwarder
├── config/
│   └── devices.json
│
├── docs/
│   ├── architecture.md
│   ├── backlog.md
│   └── serial-forwarder-handoff.md
│
├── src/
│   └── serial_reader.py
│
├── venv/
│
└── README.md
```

## config/

Contains runtime configuration.

Current configuration:

```
config/devices.json
```

This file defines every monitored device.

---

## src/

Contains the Serial Forwarder application.

Current entry point:

```
src/serial_reader.py
```

The application is intentionally small and currently consists of a single executable module.

---

## docs/

Project documentation.

- architecture
- backlog
- engineering handoff
- operational procedures

---

## venv/

Python virtual environment.

This directory is installation-specific and is not considered source code.

---

# Runtime Model

The current implementation is intentionally simple.

```
Read configuration
        │
        ▼
One thread per device
        │
        ▼
Monitor USB serial
        │
        ▼
Generate events
        │
        ▼
Write local log
        │
        ▼
POST to AWS
```

# Raspberry Pi Environment

## Runtime Environment

The Serial Forwarder is installed directly on a Raspberry Pi and managed as a long-running system service.

| Item | Value |
|------|-------|
| Hostname | `serial-forwarder` |
| User | `chip` |
| Repository | `/opt/serial-forwarder` |
| Python | 3.13 |
| Node.js | Not required |
| Virtual Environment | `/opt/serial-forwarder/venv` |

The repository should always be accessed from:

```bash
cd /opt/serial-forwarder
```

---

# Service Management

The forwarder runs under **systemd**.

Main service:

```text
/etc/systemd/system/serial-forwarder.service
```

Environment overrides:

```text
/etc/systemd/system/serial-forwarder.service.d/override.conf
```

Secrets:

```text
/etc/serial-forwarder.env
```

Current environment variables:

- `PARTICLE_WEBHOOK_SECRET`

Secrets are intentionally stored outside the Git repository.

---

# Startup

At boot:

1. Raspberry Pi starts.
2. Network becomes available.
3. systemd launches the Serial Forwarder.
4. Configuration is loaded.
5. One monitoring thread starts for every configured device.

If the process exits unexpectedly, systemd automatically restarts it after five seconds.

---

# Repository Structure

```
/opt/serial-forwarder
├── config/
│   └── devices.json
│
├── docs/
│   ├── architecture.md
│   ├── backlog.md
│   └── serial-forwarder-handoff.md
│
├── src/
│   └── serial_reader.py
│
├── venv/
│
└── README.md
```

## config/

Contains runtime configuration.

Current configuration:

```
config/devices.json
```

This file defines every monitored device.

---

## src/

Contains the Serial Forwarder application.

Current entry point:

```
src/serial_reader.py
```

The application is intentionally small and currently consists of a single executable module.

---

## docs/

Project documentation.

- architecture
- backlog
- engineering handoff
- operational procedures

---

## venv/

Python virtual environment.

This directory is installation-specific and is not considered source code.

---

# Runtime Model

The current implementation is intentionally simple.

```
Read configuration
        │
        ▼
One thread per device
        │
        ▼
Monitor USB serial
        │
        ▼
Generate events
        │
        ▼
Write local log
        │
        ▼
POST to AWS
```

Each configured device operates independently in its own daemon thread.

A problem with one serial device does not stop monitoring of the remaining devices.

The current implementation performs synchronous HTTP POST operations from each device thread. Future versions may decouple serial capture from cloud forwarding through an internal queue.

# Device Configuration

The Serial Forwarder monitors devices explicitly listed in:

```
config/devices.json
```

Each configured device has:

- A human-readable device name.
- A stable USB serial path.

Example:

```json
[
    {
        "name": "Boron-Dev-14",
        "path": "/dev/serial/by-id/usb-Particle_Boron_CDC_Mode_e00fce688e592afaf23ac4fb-if00"
    },
    {
        "name": "Photon2-Dev-01",
        "path": "/dev/serial/by-id/usb-Particle_Photon_2_0a10aced202194944a043e7c-if01"
    },
    {
        "name": "Boron-Dev-11",
        "path": "/dev/serial/by-id/usb-Particle_Boron_CDC_Mode_e00fce683f6063bf254283dd-if00"
    }
]
```

The configured `name` is used consistently for:

- Local log filenames
- systemd journal output
- Event payloads sent to the Unified Telemetry Platform

---

# Device Naming Standard

Use a consistent naming convention that matches firmware development and fleet telemetry.

## Boron

```
Boron-Dev-09
Boron-Dev-11
Boron-Dev-14
```

## Photon 2

```
Photon2-Dev-01
Photon2-Dev-02
```

Avoid temporary names such as:

```
boron-soak-1
test-device
new-boron
```

Consistent names eliminate translation between firmware logs, serial logs, and cloud telemetry.

---

# Stable USB Device Identity

Always configure devices using:

```
/dev/serial/by-id/
```

Never use:

```
/dev/ttyACM0
/dev/ttyACM1
```

The Linux kernel may renumber `/dev/ttyACM*` devices after:

- reboot
- reconnect
- USB hub changes
- multiple connected devices

The `/dev/serial/by-id` symlink remains stable because it incorporates the Particle USB identity.

---

# Standard Operating Procedure — Add a New Device

## Step 1

Connect the Particle device using a USB **data** cable.

Allow the device to boot completely.

---

## Step 2

Verify Linux detects the device.

```bash
ls -la /dev/serial/by-id/
```

Example:

```
usb-Particle_Boron_CDC_Mode_e00fce683f6063bf254283dd-if00
```

---

## Step 3

Edit:

```
config/devices.json
```

Add a new entry.

---

## Step 4

Validate the JSON.

```bash
python3 -m json.tool config/devices.json
```

Do **not** restart the service until validation succeeds.

---

## Step 5

Restart the service.

```bash
sudo systemctl restart serial-forwarder.service
```

---

## Step 6

Verify connection.

```bash
journalctl -u serial-forwarder.service -n 40 --no-pager -l
```

Expected:

```
SERIAL_CONNECTING
SERIAL_CONNECTED
```

---

## Step 7

Verify local logging.

```bash
tail -f /var/log/serial-forwarder/<device>.log
```

---

## Step 8

Verify cloud forwarding.

Check for POST failures.

```bash
journalctl -u serial-forwarder.service \
    --since "10 minutes ago" \
    | grep AWS_POST_FAILED
```

No output indicates no forwarding failures were logged during the selected period.

---

# Renaming a Device

Changing the `name` field changes:

- Local logfile name
- Journal output
- Cloud event `deviceName`

It does **not** change:

- Particle Device ID
- USB identity
- Historical cloud events
- Historical local logfiles

Rename devices deliberately and keep names aligned with firmware labels.

---

# Replacing Hardware

When replacing a Particle device:

1. Connect the replacement.
2. Determine the new `/dev/serial/by-id` path.
3. Update `config/devices.json`.
4. Restart the service.
5. Verify connection.
6. Verify local logging.
7. Verify cloud forwarding.

Remember that a replacement device will almost always have a different Particle Device ID.

---

# Removing a Device

To permanently remove a device:

1. Delete the entry from `config/devices.json`.
2. Validate the JSON.
3. Restart the service.
4. Confirm no further events are generated.
5. Preserve historical logfiles if required.

---

# Common Mistakes

Do not:

- Use `/dev/ttyACM0`
- Duplicate device names
- Duplicate serial paths
- Forget to validate JSON
- Forget to restart the service
- Assume a sleeping Boron has disappeared

A `SERIAL_MISSING` event often means the device is asleep rather than disconnected.

# Runtime Operation

## Overview

Once started, the Serial Forwarder operates continuously as a long-running service.

The current implementation follows a simple event pipeline:

```
Load configuration
        │
        ▼
Start one thread per device
        │
        ▼
Monitor USB serial port
        │
        ▼
Generate lifecycle events
        │
        ▼
Write local log
        │
        ▼
Forward event to AWS
```

Each configured device is monitored independently.

---

# Connection Lifecycle

Each device continuously cycles through one of four connection states.

```
            Device Missing
                  ▲
                  │
                  │
          SERIAL_MISSING
                  │
                  │
                  ▼
SERIAL_CONNECTING
        │
        ▼
SERIAL_CONNECTED
        │
        ▼
        LOG
        │
        ▼
SERIAL_DISCONNECTED
        │
        └───────────────► Retry
```

The forwarder automatically attempts to reconnect every two seconds.

No operator intervention is normally required.

---

# Event Types

The forwarder currently generates five event types.

## SERIAL_CONNECTING

Generated immediately before attempting to open the configured USB serial port.

Typical payload:

```
SERIAL_CONNECTING
/dev/serial/by-id/usb-Particle_Boron...
```

---

## SERIAL_CONNECTED

Generated after the serial port has been successfully opened.

This confirms that the device is available for monitoring.

---

## LOG

Generated for every non-empty serial line.

Example:

```
0000012993 [ncp.client] ERROR: Failed to power off
```

The forwarder preserves the line exactly as received (after UTF-8 decoding with replacement for invalid bytes).

No parsing or enrichment is currently performed.

---

## SERIAL_DISCONNECTED

Generated whenever the serial port closes unexpectedly.

Common causes include:

- device enters sleep
- USB cable disconnected
- device reset
- USB hub reset
- serial exception

The exception text is included in the event.

Example:

```
SerialException(
    'device reports readiness to read but returned no data...'
)
```

---

## SERIAL_MISSING

Generated when the configured USB path no longer exists.

Typical causes:

- device sleeping
- USB unplugged
- cable failure
- hardware failure

Only one event is generated when entering the missing state.

The service continues checking every two seconds until the device returns.

---

# Local Logging

Every event is written to:

```
/var/log/serial-forwarder/
```

Each device has its own logfile.

Example:

```
Boron-Dev-14.log

Photon2-Dev-01.log

Boron-Dev-11.log
```

Each log entry has the format:

```
Timestamp
Device Name
Event Type
Message
```

Example:

```
2026-07-14T13:15:39Z
Boron-Dev-14
SERIAL_CONNECTED
/dev/serial/by-id/...
```

---

# Log Rotation

The Raspberry Pi uses logrotate to archive historical logs.

Compressed archives are retained automatically.

Typical files:

```
Boron-Dev-14.log

Boron-Dev-14.log.1.gz

Boron-Dev-14.log.2.gz
```

Historical logs remain available for forensic investigation.

---

# Cloud Forwarding

Every event is immediately forwarded to the Unified Telemetry Platform.

Current implementation:

```
HTTP POST

JSON payload

3 second timeout

Authentication:
x-particle-webhook-secret
```

If the POST succeeds:

- processing continues

If the POST fails:

```
AWS_POST_FAILED
```

is written to the journal.

---

# Current Delivery Characteristics

Current behaviour:

✔ Immediate forwarding

✔ One POST per event

✔ Local log written first

✔ Secret stored outside Git

Current limitations:

✘ No retry queue

✘ No exponential backoff

✘ No batching

✘ No replay after network outage

✘ HTTP send blocks the device thread until completion or timeout

These are known design limitations and are tracked in the project backlog.

---

# Failure Recovery

The current implementation automatically recovers from:

- device sleep
- USB reconnect
- Raspberry Pi reboot
- service restart

Recovery requires no operator action.

Future versions should additionally support:

- durable message queue

- offline replay

- collector health monitoring

- cloud connectivity metrics

# Operations & Troubleshooting

This section contains the day-to-day operational commands used to manage and diagnose the Serial Forwarder.

---

# Repository

Always begin work from the repository root.

```bash
cd /opt/serial-forwarder
```

---

# Service Status

Check that the service is running.

```bash
systemctl status serial-forwarder.service --no-pager
```

Expected:

```
Active: active (running)
```

---

# Restart Service

Restart after:

- changing `devices.json`
- updating source code
- changing environment variables

```bash
sudo systemctl restart serial-forwarder.service
```

---

# Stop Service

```bash
sudo systemctl stop serial-forwarder.service
```

---

# Start Service

```bash
sudo systemctl start serial-forwarder.service
```

---

# Follow Live Logs

View the Serial Forwarder output in real time.

```bash
journalctl -u serial-forwarder.service -f -l
```

---

# Recent Service Activity

Display the last 100 log entries.

```bash
journalctl -u serial-forwarder.service \
    -n 100 \
    --no-pager \
    -l
```

---

# Watch a Device Log

Example:

```bash
tail -f /var/log/serial-forwarder/Boron-Dev-14.log
```

---

# List Configured Devices

```bash
python3 -m json.tool config/devices.json
```

---

# Validate Configuration

Always validate before restarting.

```bash
python3 -m json.tool config/devices.json
```

---

# View Stable USB Devices

Never use `/dev/ttyACM*`.

Always inspect:

```bash
ls -la /dev/serial/by-id/
```

---

# View Git Status

```bash
git status
```

---

# Pull Latest Changes

```bash
git pull
```

---

# View Recent Commit History

```bash
git log --oneline -10
```

---

# Cloud Forwarding Diagnostics

Check for forwarding failures.

```bash
journalctl -u serial-forwarder.service \
    --since "30 minutes ago" \
    | grep AWS_POST_FAILED
```

No output indicates no forwarding failures were logged during the selected period.

---

# Common Problems

## Device Shows SERIAL_MISSING

Possible causes:

- device asleep
- USB cable disconnected
- USB hub power issue
- incorrect path in `devices.json`
- hardware failure

Verify:

```bash
ls -la /dev/serial/by-id/
```

---

## Device Connects then Disconnects

Possible causes:

- normal firmware sleep cycle
- firmware reset
- USB instability
- another application opened the serial port

Review:

```bash
journalctl -u serial-forwarder.service -n 100 -l
```

---

## No Local Log

Verify:

```bash
ls -lah /var/log/serial-forwarder
```

If the logfile does not exist:

- confirm the device is configured
- confirm the device has connected
- confirm the service is running

---

## Logs Local but Missing in AWS

Check:

```bash
journalctl -u serial-forwarder.service \
    --since "30 minutes ago" \
    | grep AWS_POST_FAILED
```

Then verify:

- Internet connectivity
- webhook secret
- AWS endpoint availability
- Unified Telemetry Platform

---

## Configuration Changes Have No Effect

The configuration is loaded only when the service starts.

Restart:

```bash
sudo systemctl restart serial-forwarder.service
```

---

## Service Will Not Start

Check:

```bash
systemctl status serial-forwarder.service

journalctl -u serial-forwarder.service -n 100 -l
```

Then validate:

```bash
python3 -m json.tool config/devices.json
```

Most startup failures are caused by invalid JSON or configuration errors.

---

# Operational Checklist

After any change:

- [ ] Validate configuration
- [ ] Restart service
- [ ] Confirm service is running
- [ ] Verify USB device detected
- [ ] Verify `SERIAL_CONNECTED`
- [ ] Verify local logfile
- [ ] Verify no `AWS_POST_FAILED`
- [ ] Verify events visible in Unified Telemetry Platform

Following this checklist after every configuration or code change helps catch problems early and keeps the forwarder in a known-good operational state.

# Engineering Principles & Roadmap

## Design Philosophy

The Serial Forwarder is intentionally a small, reliable edge collector.

Its primary objective is not to be "smart."

Its primary objective is to **never lose useful serial telemetry**.

Whenever possible:

- preserve raw data
- recover automatically
- remain simple
- fail safely
- keep responsibilities clearly separated

---

# Engineering Boundaries

The overall See Insights platform consists of three independent engineering projects.

## 1. Particle Firmware

Responsible for:

- sensor logic
- counting
- occupancy
- power management
- diagnostics
- serial output
- cloud telemetry

Firmware owns **what** is logged.

---

## 2. Serial Forwarder

Responsible for:

- USB device management
- stable device identity
- serial capture
- local persistence
- lifecycle events
- reliable forwarding

The forwarder owns **how** logs are collected.

---

## 3. Unified Telemetry Platform

Responsible for:

- authentication
- ingestion
- storage
- timelines
- fleet intelligence
- analytics
- dashboards
- AI

The cloud owns **what happens after the events arrive**.

---

# What Does NOT Belong Here

The Serial Forwarder should never become responsible for:

- fleet intelligence
- dashboards
- analytics
- Particle API enrichment
- DeviceCurrentState
- business logic
- Ubidots
- reporting
- cloud storage

Those belong in the Unified Telemetry Platform.

Likewise, firmware-specific fixes belong in the firmware repository rather than the forwarder.

---

# Development Principles

When implementing new features:

1. Keep serial capture independent from cloud availability.
2. Preserve raw log fidelity.
3. Prefer configuration over hard-coded values.
4. Keep secrets outside Git.
5. Design for unattended operation.
6. Prefer automatic recovery over operator intervention.
7. Keep changes small and testable.
8. Update documentation before or alongside implementation.

---

# Current Priorities

The next engineering improvements should focus on reliability.

## High Priority

- Configuration validation
- Duplicate device detection
- Collector configuration via environment variables
- HTTP retry with exponential backoff
- Local delivery queue
- Durable replay after network outages

## Medium Priority

- Structured log parsing
- Collector health metrics
- Hot-plug support
- Dynamic device discovery
- Additional collector metadata

## Future

- Local web dashboard
- Live streaming console
- Multiple Raspberry Pi collectors
- Automatic collector registration
- Containerized deployment

---

# AI Development Guidance

Before making changes:

1. Read this document.
2. Read `architecture.md`.
3. Read `backlog.md`.
4. Understand the current implementation.
5. Distinguish current behaviour from future roadmap items.

AI assistants should avoid making architectural changes without explicit direction.

The preferred workflow is:

```
Understand
      ↓
Document
      ↓
Implement
      ↓
Validate
      ↓
Commit
```

Documentation is considered part of the implementation, not an afterthought.

---

# Documentation Status

This document reflects the implementation verified on the live Raspberry Pi.

It documents the current production behaviour of the Serial Forwarder.

Future enhancements should update this document as part of the same change.

The objective is for this document to remain the authoritative engineering reference for the Serial Forwarder project.

