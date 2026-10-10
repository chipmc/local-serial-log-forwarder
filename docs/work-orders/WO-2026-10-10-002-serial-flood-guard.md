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

Done 2026-10-10 by Claude Code (Opus 5.5) at e27bce8. Read from the repo only; the Pi's running copy was not checked.

**§3 facts:** all confirmed at the cited lines (`serial_reader.py`, 148 lines): thread per device :73/:143; `timeout=1` :91; `readline` :97; empty-read loop :98-99; decode/strip :101; skip empty :102; `write_log` :103 → print :65, append :67-68, `post_to_api` :70; POST 3 s, no retry :44-49; failure printed and dropped :51-58; `last_state` :77 is the only cross-line state. One more: `THREAD_CRASH` (:128) also goes through `write_log` and is lifecycle.
**§5 facts:** confirmed at fleet-ops 685bd0d, with one correction: `parseSeverity` is `parse.ts:186-188` (handover says 184-188). Serial health branch `current-state.ts:328-330`. Summary text `[forwarder] INFO: previous line repeated N times` parses as INFO (checked against the same regex).
**Fixture:** the three TimeDiag lines are 81 chars and map to one key (`########## [app] INFO: TimeDiag: tz=SGT-# valid=# epoch=########## utc=####-##-#`). They differ only in digits, so they do not exercise the 80-char cut; the reviewer should add one pair that differs only after char 80.

**Key:** `re.sub(r"\d", "#", line)[:80]`, as suggested. No new evidence for a different key.

**Flush rules** (state in `monitor_device`: key, count, held line):
1. Line 1 of a run: post at once. Line 2+: hold it (replacing any earlier held line); not posted yet.
2. Run ends (new key, silence, lifecycle event): count 2 → post the held line; count ≥3 → post summary with N = count − 2 (lines not posted), then the held line. Then reset.
3. A run of 2 therefore still posts both lines, but the second is delayed until the run ends. A run of 3 posts 3 events (no saving), per decision 3.
4. Local file and stdout are written for every line before any of this, unchanged.

**§6 answers:**
- Silence: an empty `readline()` (:98) means ≥1 s with no bytes; flush there. Disconnect: flush first thing in the `except` at :105, before `SERIAL_DISCONNECTED`. `SERIAL_MISSING`/`CONNECTING`/`CONNECTED` start a fresh run state, so nothing can be pending then.
- Truncated tail: ignored automatically: the device truncates at 182 chars, the key stops at 80.
- Order: one thread posts serially and each POST blocks, so AWS receives first → summary → last → next line in that order. Caveat: `timestamp` is set at post time (:31), so the held line carries its flush time, not its read time (up to ~1 s later on silence). Payload shape unchanged.

**Open point for Chip (one decision needed):** "never held indefinitely" is not met by the rules above. If the device repeats one message with gaps under 1 s and nothing else in between, there is no silence and no new key, so the summary and last line wait until the flood stops or the port drops. Two options:
- (A) Accept it. AWS still has the first line and the local log has everything. No extra code.
- (B) Add a third constant: flush the run (summary + held line) after 60 s and keep going. About +3 lines. During an endless flood AWS would get ~3 events a minute.
Recommendation: (B), because it is the only way AWS sees that a flood is still going. Your call; it is the "gate" the WO says to ask about.

**Test harness:** pyserial and requests are not installed locally and the module loads `CONFIG_FILE` and starts threads at import (:137-148). Tests will stub `serial`/`requests` in `sys.modules` and patch `open` to return `[]` during import, so no `__main__` guard is needed and the entry point is untouched.
**Budget:** expect about +25 lines with (A), +28 with (B), inside +40.

**Stopped here. No code until Chip approves the rules and picks A or B.**

**Approved by Chip 2026-10-10 with option B** (60 s periodic send, hard-coded). He added: a test for lines differing only after char 80, a test for the periodic send, mutation (h) "no periodic send", an `operations.md` note on timestamps.

## Closing record (budget vs actual, verdicts, Chip's deploy note)

**Stage 2 (Claude Code, Opus 5.5, 2026-10-10).** `flush_run` and `log_line` added; `write_log` takes `post=True`; three constants (`KEY_LENGTH`, `MIN_RUN`, `RUN_FLUSH_SECONDS`), each with a one-line comment. Payload shape, entry point and file/stdout writes unchanged.
Tests: `python3 -m unittest discover -s tests`, 9 tests, all pass (Python 3.14.6 on the Mac; the Pi runs 3.13). The seven handover §7 cases, plus a run of 2, after-char-80 collapse, and an endless run (261 lines at 0.5 s → flushes at 60 s and 120.5 s, then on disconnect). The only lifecycle event that can fall inside a run is a disconnect, so "lifecycle event mid-run" is a disconnect plus reconnect mid-run. Every test checks the local file holds every line.
Pre-check of mutations by the implementer (Codex still to run them independently): each fails at least one test. (a) 8 tests, (b) 9, (c) 8, (d) 8, (e) 2, (f) 1 `test_silence_ends_run`, (g) 9, (h) 1 `test_endless_run_sends_every_60_seconds`. Extra: a key without the 80-char cut fails `test_lines_differing_only_after_char_80_collapse`.
Correction to the handover: `parseSeverity` is at `lambda/src/utils/parse.ts:186-188` (fleet-ops 685bd0d), not 184-188. `current-state.ts` serial health branch is 328-330.

| Item | Budget | Actual |
|---|---|---|
| `src/serial_reader.py` | +40 net | +38 net (41 added, 3 removed) |
| `tests/test_flood_guard.py` | 150 | 143 |
| Docs (`operations.md` + `CHANGELOG.md`) | 15 | 9 (6 + 3) |
| This record (Step 0 + closing) | 60 | 47 so far (stages 3-5 still to add) |

**Stage 3 (Codex):** pending.
**Stage 4 (architect):** pending.
**Stage 5 (Chip, deploy note):** pending.
