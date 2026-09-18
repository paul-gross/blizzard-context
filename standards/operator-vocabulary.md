# Operator-facing copy uses the claim vocabulary (`bzh:operator-vocabulary`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

Operator-facing copy — web UI strings, CLI help text, and `docs/` operator prose — uses the terms
[`domain/execution/claim-vocabulary.md`](../domain/execution/claim-vocabulary.md) (`bzh:claim-vocabulary`) defines, and
never one of that taxonomy's barred internal terms.

## Why

Blizzard has one agreed vocabulary for what a chunk action does to a runner's claim; an operator reading a control's
label or tooltip should never have to learn an internal term — route, lease, epoch, attempt, tenure, or reap — to
understand what it does.

## Scope

Binds only copy a change **authors or edits** — it does not indict copy no change has touched. Known, undischarged by
this rule alone: `docs/deployment/control-verbs.md` outside the sections the claim-vocabulary change corrected,
`blizzard
hub chunk` help text, and the board surfaces beyond the chunk detail dock. A change touching any of those
still owes this rule at the copy it edits.

## Detect

A barred internal term — `route`, `lease`, `epoch`, `attempt`, `tenure`, `reap` — appearing in a UI string, CLI help
text, or operator doc prose the change under review authors or edits; a term the taxonomy defines used with a different
meaning than the table gives it.

## Do

*"Claimed by runner-2"*, *"Releases runner-2's claim: ends the agent's session and releases its environment"* — the
taxonomy's own terms, in its own meanings.

## Don't

*"Route: runner-2"*, *"Detach frees the route"* — internal terms surfaced to an operator.

## See also

- `winter-canon:/enforcement-channels.md` (`canon:enforcement-channels`) — this rule binds through the target's own
  conformance (the chunk detail dock and `MachineDetailHeader`) and the chunk graph's `review` node-step's faceted
  review of blizzard's `standards/` tree; it has no mechanical gate.
