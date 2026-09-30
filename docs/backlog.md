Backlog

Near term

Reliability

* add health heartbeat event
* add collector self-status event

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

