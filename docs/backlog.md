Backlog

Near term

Reliability

* add health heartbeat event
* add collector self-status event
* decouple the cloud POST from the serial read loop: each LOG line runs a blocking `requests.post` (3 s timeout, `src/serial_reader.py:44-49`) inside `write_log()` (:70), called from the read loop (:103), so a slow or failing ingest endpoint stalls reading for that device (2026-10-09: ~0.86 s per line on Boron-Dev-09). The flood guard (WO-2026-10-10-002) only helps during repeated-line runs; it does not fix this.

Considered and not justified (investigation of 2026-09-25 to 2026-09-28, see results-2026-09-29-port-open-reorder.md for the follow-up measurement):

* POST retry/backoff and a local queue for failed cloud sends: measured loss between the Pi and AWS on 2026-09-25 was 0 to 0.13% per device, and retrying timed-out posts risks duplicates, because some timed-out posts were stored anyway.

⸻

Parsing

* parse log severity
* parse reset cause
* parse modem health
* parse queue depth
* parse connect timing

⸻

Fleet scale

* support dynamic hot-plug
* add per-device config metadata
* reconcile `config/devices.json` with the Pi's live `/opt/serial-forwarder/config/devices.json`: the repo copy (at e27bce8) still lists P2-Dev-01, which was removed from the forwarder during the soak. Chip confirms which copy is correct, then the repo is made to match.

⸻

Observability

* build unified timeline view
* correlate:
    * serial logs
    * watchdogs
    * status
    * telemetry

⸻

AI

Build OpenClaw agent over:

* S3
* DynamoDB

Use cases:

* soak analysis
* anomaly detection
* modem instability
* watchdog root cause
* battery/connectivity correlation

⸻

Future stretch goals

* websocket live tail
* local dashboard
* local buffering if AWS unavailable
* OTA config updates
* containerized deployment

