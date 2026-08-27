# Contract and restatement sweep detail (`bzh:matrix-command-contracts`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test-filename code spans, and `mise run` task names are machine-checked — keep them verbatim, in their sections. -->

These sweeps gate a shape rather than a behavior. Read [`../../blizzard.md`](../../blizzard.md) first for the short
command and the method-id inventory; [`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:sse-contract

`mise run sse-contract` gates the SSE frame shape against the golden corpus `contracts/sse/`: `manifest.json`,
`README.md`'s forward-compatibility policy, and one `<kind>.json` per frame kind. The corpus is two self-contained
scopes — hub at `contracts/sse/`'s top level (`blizzard.hub.events.broker`), runner at `contracts/sse/runner/`
(`blizzard.runner.events.broker`) — each with its own `manifest.json`, framing constants, and reserved open-of-stream
comment. Each scope asserts its own closure: the on-disk kind set, the `manifest.json` kind list, that daemon's Python
`EVENT_TYPES` tuple, and its TS event-type tuple must all be equal.

Both suites read the same physical goldens — no per-side copy — so moving a golden reddens the side that has not caught
up, and changing a side's shape without moving the golden reddens that side. Each drives both scopes; no runner-only
test module or spec basename exists — the method's surface is exactly these two files:

- The Python half, `tests/test_sse_contract.py` (`blizzard:component-test`), drives the real `EventBroker.publish_*`
  helper per case and asserts `json.loads(event.data) == payload`, then validates the same golden against its
  `blizzard.wire.sse` model (`extra="forbid"`) and round-trips it losslessly.
- The board half, `web/projects/fleet/src/lib/sse/sse-contract.spec.ts` (`web:unit-test`), feeds every golden — framed
  exactly as its owning daemon frames it — through a stubbed `fetch` into the real `SseService`/`FetchEventSource`
  byte-stream reader and asserts on what reaches `SseHandle.events`.

Per-scope compile-time frame-field-spec descriptors — `HUB_FRAME_FIELD_SPECS` off `fleet-live.ts`'s exported per-kind
interfaces, `RUNNER_FRAME_FIELD_SPECS` off `runner-events.ts`'s — stop compiling when an interface field is renamed or
dropped, and at runtime cross-check each golden's key set against its scope's spec. The compile-time half holds only
because each slot is authored through the spec's own exactness helper: a bare `Record<Keys<T>, true>` degrades to `{}`
when a kind has no fields in that slot, and TypeScript excess-property-checks nothing against `{}`, so a stale key there
would otherwise compile clean.

The runner scope carries a third assertion the hub scope has no counterpart for: each case of a kind that carries a
`cause` is named for that cause and must actually carry it. Four runner kinds' cases are key-set-identical, so the
key-set check alone cannot tell one from another and the case name would pin nothing
([`../evidence.md`](../evidence.md), `bzh:case-pins-its-own-name`).

`blizzard:manual-sse-probe` remains the method for what only a live socket proves — framing and timing, not field shape
— over either daemon's stream.

### blizzard:restatement-sweep

The check fails on a census fact (`scripts/restated-invariants.json`) stated at an undeclared site (`new`), a declared
site no longer observed (`stale`), a declared non-owner site carrying no reason, or a designated owner not stating its
fact ([`../../../standards/one-prose-home.md`](../../../standards/one-prose-home.md)). The full command —
`mise run restatement-check` for short:

```bash
uv run python scripts/restated_invariants.py check --strict --owners --context-root ../blizzard-context src tests docs README.md web/projects ../blizzard-mock/src
```

Local-only via `--context-root`: `../blizzard-mock` is already a CI sibling, but `../blizzard-context` is checked out
nowhere in CI, and an unresolved `--context-root` refuses a green rather than skipping silently.

Refresh a `new`/`stale` finding with `measure --write-sites`, which rewrites `sites[]` to the observed tree — never by
hand — plus a `reason` on any new non-owner site. `measure --write-sites` refuses a partial scan (a file skipped as
unreadable or unparsable) unless `--force`; `check` instead reports a skipped file as an informational `skipped` finding
without failing, so a clean verdict claims only the scanned files.
