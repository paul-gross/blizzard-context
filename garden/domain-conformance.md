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

One slug per domain hub, each covering that hub, its spokes, and the code implementing them.

| Slug                | Ground                                                                                                            |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `domain-work`       | A unit of work — its identity, derived status, transitions, ranking, restart, and migration                       |
| `domain-graphs`     | The immutable workflow definition a chunk travels — nodes, edges, identity, and what a graph declares beside them |
| `domain-execution`  | Who runs a chunk and what happens to one in flight — acquisition, envelope, fencing, pause, and recovery          |
| `domain-artifacts`  | What work produces and how it lands — the model, the series, delivery, and the never-code rule                    |
| `domain-humans`     | Where a person enters the loop — asks, gates, escalation, and takeover                                            |
| `domain-operations` | Operational visibility — the durable, typed, severity-ranked event log                                            |
| `domain-routines`   | A routine's graph, default scope, and run preference, and a scope's slug and retired brake                        |
| `domain-findings`   | A finding's identity, liveness, and vocabulary, and a proposal's findings list                                    |

## Criteria

[`../domain/`](../domain/index.md) and the tree beneath it declare every behavior this axis judges against, and a
finding names the statement it contradicts.
[`../verification/blizzard/evidence.md`](../verification/blizzard/evidence.md) governs the unpinned-invariant finding:
`bzh:matrix-acceptance-criteria` and `bzh:mutation-review-selection` own what a declared behavior owes a test.

This axis is the standing counterpart to `bzh:falsified-claims-grep`, which sweeps the claims one change falsifies at
the time it lands. A claim that went false without any change noticing is what remains, and is in range here.

Where a command already judges the same agreement, it owns that judgement and this axis does not
(`winter-canon:/enforcement-channels.md`):

- Whether the code satisfies the suite is out of range entirely — every test tier judges it, on every change.
- A count, roster, or enumeration a domain file states is out of range where `blizzard-context:registry-drift` reaches
  it.
- A domain fact restated in code prose is `bzh:one-prose-home`'s, and `blizzard:restatement-sweep` judges it for every
  fact its census carries.

## Measurement

Every run records, findings or none:

- Declared behaviors swept and findings opened, per scope swept.
- How many findings are code-side divergences against how many are doc-side stale claims — which side of the pair is
  drifting, a split a single count of findings hides.
