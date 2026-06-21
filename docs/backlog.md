Backlog

Near term

Reliability

* add POST retry/backoff
* add local queue for failed cloud sends
* add health heartbeat event
* add collector self-status event

⸻

Parsing

* parse log severity
* parse reset cause
* parse modem health
* parse queue depth
* parse connect timing

⸻

Fleet scale

* expand from 2 to 4 devices
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

