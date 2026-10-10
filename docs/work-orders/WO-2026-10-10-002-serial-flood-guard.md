# WO-2026-10-10-002: Serial flood guard (AWS side only)

Repo: chipmc/local-serial-log-forwarder. Base: `main` at e27bce8.
Author: architect (Claude, app). Owner and approver: Chip.
Spec: `WO-2026-10-10-002-handover.md` (same folder). The handover holds the evidence, decisions and constraints. This WO adds scope, budget, roles and the stages.
ID note: WO-2026-10-10-001 is the fleet-ops evidence WO. This repo uses -002 so the two never collide.

## Goal (one sentence)

When the device repeats the same message, AWS gets the first line, one `[forwarder] INFO: previous line repeated N times` summary, and the last line. The Pi's local log file and stdout keep every line, unchanged.

## Governing workflow

`AI_DEVELOPMENT_WORKFLOW.md`, "Preferred Development Workflow" (Understand → Design → Document → Implement → Validate → Commit) and "Development Principles" (small incremental changes, simplicity over cleverness).

That doc predates the current roles. It names ChatGPT as architect and has no Step 0 or second-agent verification. For this WO only, these four points override it:

1. **Roles.** The roles are as listed under "Who does what" below, not the doc's "AI Roles" section.
2. **Configuration.** "Configuration over hard-coded values" is set aside here. Handover decision 4 (no new config, flags or files) is Chip's edge-case constraint. The two constants (key length 80, minimum run length 3) stay hard-coded, each with a one-line comment.
3. **Git.** "Git Workflow" describes committing to `main` on the Pi. Instead, work on branch `wo/2026-10-10-002-serial-flood-guard`, push the record after each stage, and open a PR after the architect's final review. Chip merges.
4. **Hardware testing.** The "Testing Expectations" real-hardware checks are done by Chip after he deploys, as stage 5.

Updating the workflow doc itself is not part of this WO.

## Who does what

| Stage | Who | Model / reasoning | Output |
|---|---|---|---|
| 1. Step 0: verify the handover's §3 facts against code; answer the three §6 points in one line each; state the key and flush rules | Claude Code | Opus 5.5, high | Step 0 section appended below, pushed to the branch. **Stop. Chip approves before any code.** |
| 2. Implement and test | Claude Code | Opus 5.5, high | Diff and tests on the branch |
| 3. Independent verification | Codex | 5.6, high | Verdict in the record. Codex runs each listed mutation and confirms a test fails. |
| 4. Architect review against the handover | Claude (app) | n/a | Chip forwards the record and diff |
| 5. Merge, deploy to the Pi, watch a real run | Chip | n/a | One note in the closing record |

Model choice: the change is small but stateful, and its edge cases (silence, disconnect, lifecycle events mid-run) are where these bugs hide. Opus is warranted for that. Verification is mechanical (run the mutations), so Codex at high reasoning is enough.

## AUTHORIZATION SCOPE

**Pre-authorized:** read the repo; run Python and the tests locally; edit `src/serial_reader.py`; add a test file under `tests/`; edit this WO record, `CHANGELOG.md` and `docs/operations.md` (one short paragraph on the guard); commit and push to the WO branch; open the PR after stage 4.

**Not authorized:** push to `main`; merge; any change to the posted payload shape, the Lambda, API Gateway or alarms; any Pi or device operation; reading `/etc/serial-forwarder.env` or printing any secret value; adding dependencies.

**Project guardrails:** every file:line reference and number in the record is checked against the source, not copied from the handover. A test that cannot fail is a finding. If the design grows a gate, flag or config option, stop and ask Chip to pare it back.

## Budget (record budget vs actual at close)

| Item | Budget |
|---|---|
| `src/serial_reader.py` | +40 net lines |
| `tests/test_flood_guard.py` (stdlib `unittest` only; fake `serial.Serial` and `requests.post`) | 150 lines |
| Docs (`operations.md` paragraph + `CHANGELOG.md` line) | 15 lines |
| This record (Step 0 + closing sections) | 60 lines |

Any raise needs Chip's OK with the reason, and the record must log it.

## Acceptance

- All seven test cases in handover §7 pass. Each asserts on the posted sequence, and that the local file holds every line.
- First fixture: the three real TimeDiag lines in handover §7. These were checked by the architect: under the suggested key (digits → `#`, first 80 chars) all three map to one key.
- **Mutations (Codex must show each one fails a test):**
  - (a) post every line, i.e. the guard is bypassed;
  - (b) drop the held last line;
  - (c) the summary count is off by one;
  - (d) the summary is posted after the last line instead of before;
  - (e) a disconnect does not flush the pending run;
  - (f) silence does not flush the pending run;
  - (g) the guard is applied to the local file write.
- The summary text contains `INFO` as its first severity word and does not quote the collapsed line (handover §5).

## Out of scope

Handover §8 applies. The two new backlog items (POST decoupling, `devices.json` reconcile) are also out of scope, even though the guard touches the same seam.

---

## Step 0 (Claude Code fills in)

## Closing record (budget vs actual, verdicts, Chip's deploy note)
