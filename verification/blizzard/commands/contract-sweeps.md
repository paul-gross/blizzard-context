# Contract and restatement sweep detail (`bzh:matrix-command-contracts`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

The sweeps that gate a shape rather than a behavior — the SSE frame contract, and the restated-fact sweep. Read
[`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to every other method's detail.

### blizzard:sse-contract

`mise run sse-contract` — gates the SSE frame shape contract (issue #235) against the golden corpus `contracts/sse/`
(`manifest.json`, `README.md`'s forward-compatibility policy, and one `<kind>.json` per frame kind with named cases
pinning field optionality): first the Python producer+parse half (`tests/test_sse_contract.py`,
`blizzard:component-test`) — every case drives the real `EventBroker.publish_*` helper and asserts
`json.loads(event.data) == payload` (a producer-side field rename/add/drop goes red), then validates the same golden
against its `blizzard.wire.sse` model (`extra="forbid"`, so an undeclared field also goes red) and round-trips it
losslessly; then the board's half (`web/projects/fleet/src/lib/sse/sse-contract.spec.ts`, `web:unit-test`) — a stubbed
`fetch` feeds every golden, framed exactly as its owning daemon frames it (plus that daemon's own reserved comment and
an interleaved keepalive), through the **real** `SseService`/`FetchEventSource` byte-stream reader, asserting on what
reaches `SseHandle.events` rather than a hand-parsed object; a compile-time frame-field-spec descriptor per scope
(`HUB_FRAME_FIELD_SPECS`, keyed off `fleet-live.ts`'s exported per-kind interfaces; `RUNNER_FRAME_FIELD_SPECS`, keyed
off `runner-events.ts`'s) also fails to compile the moment either scope's interface field is renamed or dropped, and its
runtime half cross-checks each golden's key set against its own scope's spec. Both suites read the **same physical
files** — no per-side copy — so moving a golden reddens whichever side has not caught up, and changing a side's shape
without moving the golden reddens that side.

The golden corpus is **two self-contained scopes**, not one: the **hub** scope at `contracts/sse/`'s top level (eight
frame kinds, `blizzard.hub.events.broker`) and the **runner** scope at `contracts/sse/runner/` (six frame kinds,
`blizzard.runner.events.broker`), each with its own `manifest.json`, its own framing constants, and its own reserved
open-of-stream comment — the two daemons' streams do not open with the same text. `tests/test_sse_contract.py` and
`sse-contract.spec.ts` each drive **both** scopes; there is no separate runner-only test module or spec basename, so the
method's surface — "exactly these two files" — is unchanged even though what they cover broadened. Each scope carries
its own closure assertions (that scope's on-disk kind set == that scope's `manifest.json` kind list == that daemon's own
`EVENT_TYPES` tuple on the Python side == that daemon's own event-type tuple on the TS side); a kind added to one daemon
without a golden in that daemon's own scope goes red, and a golden misfiled under the wrong daemon's scope goes red on
both sides too. `blizzard:manual-sse-probe` remains the method for what only a live socket proves — framing and timing,
not field shape — over either daemon's stream.

### blizzard:restatement-sweep

```bash
uv run python scripts/restated_invariants.py check --strict --owners --context-root ../blizzard-context src tests docs README.md web/projects ../blizzard-mock/src
```

The check (`mise run restatement-check` for short) fails when a fact in the committed census
`scripts/restated-invariants.json` is stated at a site the census does not declare (`new`), when a declared site is no
longer observed (`stale`), when a declared non-owner site carries no reason, or when a designated owner does not state
its fact ([../../standards/one-prose-home.md](../../../standards/one-prose-home.md)). A `new`/`stale` finding is
refreshed with `measure --write-sites` (rewrites `sites[]` to the observed tree, never by hand) plus a `reason` on any
new non-owner site; `measure --write-sites` itself refuses to run against a partial scan (a file skipped as unreadable
or unparsable), unless `--force`; `check` instead reports a skipped file as an informational `skipped` finding beside
its verdict without failing, so a `restatement sweep: clean` next to a `skipped:` line claims only the files that were
scanned. Local-only in its `--context-root` half: the sweep also reads the sibling `../blizzard-mock` checkout, but that
one is already a CI sibling the upper-tiers workflow checks out for other tiers; `../blizzard-context` is not checked
out anywhere in CI, which is the actual local-only cause. An unresolved `--context-root` refuses a green rather than
skipping silently.
