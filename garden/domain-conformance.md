# The `domain-conformance` axis

The gardening axis that holds blizzard's code to the behavior [`../domain/`](../domain/index.md) declares. A spoke of
the [garden registry](./index.md); the four fields below are the shape `canon:gardening-axes` requires.

## Evaluates

Disagreement between the declared model and the running system — the drift the domain hub concedes when it rules that
code is current where the two disagree, and which no gate can see, because a domain file has no test and a test cannot
report that it pins the wrong intent. Concretely, on this target:

- A behavior the domain declares that the code contradicts — a derivation whose precedence, condition, or tie-break
  differs from the one stated.
- A behavior the domain declares that the code does not implement at all, in either direction: a stated rule with no
  code behind it, or a rule the code enforces that the model never claims.
- An invariant the domain declares that no test constructs — the case is describable, the suite is silent, and a
  regression against it would land green.
- A claim no longer true of any code path, left standing because the change that falsified it opened a different file.

## Scope

One slug per concept row of [`../domain/index.md`](../domain/index.md) — every row but `no-technical-detail.md`, which
states how the tree is written and no behavior. Each slug covers the file its row names, every spoke that file routes,
and the code implementing them, so a spoke added under a hub is in its slug's ground the moment the hub routes it. A row
added to that index owes a slug here.

| Slug                | Ground                                                             |
| ------------------- | ------------------------------------------------------------------ |
| `domain-work`       | [`work.md`](../domain/work.md)                                     |
| `domain-graphs`     | [`graphs.md`](../domain/graphs.md)                                 |
| `domain-execution`  | [`execution.md`](../domain/execution.md)                           |
| `domain-artifacts`  | [`artifacts.md`](../domain/artifacts.md)                           |
| `domain-humans`     | [`humans.md`](../domain/humans.md)                                 |
| `domain-operations` | [`operations.md`](../domain/operations.md)                         |
| `domain-routines`   | [`routines-and-scopes.md`](../domain/routines-and-scopes.md)       |
| `domain-cadences`   | [`cadences.md`](../domain/cadences.md)                             |
| `domain-findings`   | [`findings-and-proposals.md`](../domain/findings-and-proposals.md) |
| `domain-tenancy`    | [`tenancy.md`](../domain/tenancy.md)                               |
| `domain-projects`   | [`projects.md`](../domain/projects.md)                             |

## Criteria

[`../domain/`](../domain/index.md) and the tree beneath it declare every behavior this axis judges against, and a
finding names the statement it contradicts.
[`../verification/blizzard/evidence.md`](../verification/blizzard/evidence.md) governs the unpinned-invariant finding:
`bzh:matrix-acceptance-criteria` and `bzh:mutation-review-selection` own what a declared behavior owes a test.

This axis is the standing counterpart to the per-change planning rules `bzh:falsified-claims-grep` and
`bzh:owed-claims-landed`, which hold one change, at the time it lands, to the claims it falsifies and the claims it
newly owes. A claim that went false, or a surface that landed owing one, without any change noticing is what remains,
and is in range here.

Where a command already judges the same agreement, it owns that judgement and this axis does not
(`winter-canon:/enforcement-channels.md`):

- Whether the code satisfies the suite is out of range entirely — every test tier judges it, on every change.
- A count, roster, or enumeration a domain file states is out of range where `blizzard-context:registry-drift` reaches
  it.
- A domain fact restated in code prose is `bzh:one-prose-home`'s, and `blizzard:restatement-sweep` judges it for every
  fact its census carries.
- [`../domain/operations.md`](../domain/operations.md) §Event kinds's membership against
  `blizzard.foundation.event_log.EventLogKind` is `blizzard:unit-test`'s `tests/guards/test_event_log_kind_census.py`'s
  — `registry-drift` proves cardinality, never membership, and this is the check that does.

## Measurement

Every run records, findings or none:

- Declared behaviors swept and findings opened, per scope swept.
- How many findings are code-side divergences against how many are doc-side stale claims — which side of the pair is
  drifting, a split a single count of findings hides.
