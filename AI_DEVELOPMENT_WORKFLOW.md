AI Development Workflow

Purpose

This document defines the preferred engineering workflow for developing the Raspberry Pi Serial Forwarder.

The goal is to maintain a high-quality, well-documented codebase while taking advantage of AI-assisted development.

This workflow applies to all future enhancements, bug fixes, documentation updates, and operational improvements.

⸻

Project Scope

The Serial Forwarder is an edge collection service.

Its responsibilities are intentionally limited to:

* USB serial device management
* Device discovery
* Stable device identification
* Serial monitoring
* Local logging
* Event generation
* Reliable forwarding to the Unified Telemetry Platform

The forwarder is not responsible for analytics, dashboards, fleet intelligence, or cloud business logic.

⸻

System Architecture

Particle Firmware
        │
        ▼
USB Serial
        │
        ▼
Serial Forwarder
        │
        ▼
Unified Telemetry Platform

Each layer owns a distinct responsibility.

Changes should remain within the appropriate repository whenever possible.

⸻

Repository Boundaries

Firmware Repository

Owns:

* Device behavior
* Sensor logic
* Power management
* Logging
* Telemetry generation

⸻

Serial Forwarder Repository

Owns:

* USB connectivity
* Serial capture
* Local persistence
* Lifecycle events
* HTTP forwarding
* Collector configuration

⸻

Unified Telemetry Repository

Owns:

* Authentication
* Cloud ingestion
* Event storage
* Fleet APIs
* Analytics
* Dashboards
* AI

Avoid implementing functionality that belongs in another repository.

⸻

AI Roles

ChatGPT

Primary responsibilities:

* Architecture
* Design reviews
* Documentation
* Operational guidance
* Engineering planning
* Code review
* Troubleshooting

ChatGPT should help determine what should be built and why.

⸻

Claude (Implementation)

Primary responsibilities:

* Implement approved changes
* Refactor code
* Produce clean patches
* Maintain coding consistency

Claude should focus on how to implement approved changes.

⸻

GitHub Copilot

Best suited for:

* Small edits
* Boilerplate
* Simple refactoring
* IDE assistance

⸻

Human Engineer

Final authority for:

* Architecture
* Production deployment
* Code approval
* Git commits
* Operational decisions

⸻

Preferred Development Workflow

Every engineering task should follow this sequence:

Understand
      ↓
Design
      ↓
Document
      ↓
Implement
      ↓
Validate
      ↓
Commit

Documentation is part of the implementation.

⸻

Development Principles

Prefer:

* Small, incremental changes
* Readable code
* Automatic recovery
* Configuration over hard-coded values
* Stable interfaces
* Clear logging
* Simplicity over cleverness

Avoid large refactors unless there is a compelling reason.

⸻

Configuration

Configuration belongs in configuration files or environment variables.

Avoid introducing additional hard-coded values.

Examples:

* Collector ID
* API endpoint
* Retry settings
* Timeouts

Secrets must never be committed to Git.

⸻

Testing Expectations

Before committing:

* Confirm the service starts successfully.
* Confirm all configured devices reconnect.
* Confirm local log files update.
* Confirm no unexpected exceptions appear in journalctl.
* Confirm cloud forwarding succeeds.
* Confirm existing devices continue operating normally.

Whenever practical, validate using real hardware.

⸻

Documentation Expectations

Update documentation whenever:

* Behavior changes
* Configuration changes
* Operational procedures change
* New features are introduced
* New limitations are discovered

Documentation should remain synchronized with the implementation.

⸻

Git Workflow

Typical workflow:

cd /opt/serial-forwarder
git status
git diff

Implement and test changes.

Then:

git add <files>
git commit -m "<description>"

Push separately:

git push origin main

⸻

Definition of Done

A change is considered complete when:

* Code is implemented.
* Configuration has been updated (if required).
* Documentation has been updated.
* The service starts successfully.
* Existing functionality continues to operate.
* New functionality has been validated.
* Changes are committed to Git.

⸻

Current Engineering Priorities

1. Improve reliability.
2. Preserve serial telemetry.
3. Strengthen configuration validation.
4. Improve cloud delivery resilience.
5. Enhance operational observability.

Future enhancements should continue to keep the Serial Forwarder lightweight, reliable, and focused on edge collection rather than cloud processing.
