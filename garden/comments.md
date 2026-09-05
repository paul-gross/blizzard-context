# The `comments` axis

The gardening axis that holds blizzard's code prose to the discipline [`../standards/`](../standards/index.md) declares
for it. A spoke of the [garden registry](./index.md); the four fields below are the shape `canon:gardening-axes`
requires.

## Evaluates

Prose drift — a comment or docstring every gate passes over while it states what the code beside it does not own, or
states it in a vocabulary that is not the code's. Concretely, on this target:

- A block narrating another module's, component's, or repo's behavior, where a pointer at the owner would serve.
- A multi-sentence defence of a decision that no test would fail on if the decision were reverted.
- A seam's contract stated in a caller's or an implementation's vocabulary — a Protocol, wire model, or schema docstring
  naming a party on the other side of the boundary it defines.
- The same contract stated on both sides of a seam, each side's copy free to drift from the other.
- A docstring that paraphrases the code beneath it, or narrates the change that produced it.
- One prose convention answered three ways across a tree, where the divergence — not any one block — is the finding.

## Scope

| Slug            | Ground                                                                      |
| --------------- | --------------------------------------------------------------------------- |
| `hub-daemon`    | The hub's domain, stores, API, delivery, graphs, and work sources           |
| `runner-daemon` | The runner's domain, loop, stores, API, harness, environments, and selftest |
| `shared-spine`  | The daemon-neutral layer both daemons depend on, and the wire models        |
| `cli-surface`   | The hub and runner command surfaces and the shared CLI entry package        |
| `web-suite`     | The Angular libraries and apps                                              |

## Criteria

[`../standards/comments.md`](../standards/comments.md) (`bzh:comment-locality`) and
[`../standards/comment-encapsulation.md`](../standards/comment-encapsulation.md) (`bzh:comment-encapsulation`) own every
rule this axis judges by and are the only home for their prose. Neither has a command, which is what leaves them to this
axis.

Where a command already judges the same prose, it owns that judgement and this axis does not
(`winter-canon:/enforcement-channels.md`):

- `bzh:prose-budget` is out of range entirely — `blizzard:prose-ratchet` judges every block against its cap and every
  change against the committed baseline.
- `bzh:one-prose-home` is in range only for a fact absent from `blizzard:restatement-sweep`'s census. A registered fact
  belongs to that sweep, which sees every site declaring it; a fact nobody registered is invisible to it and visible
  here.
- `bzh:comment-locality`'s generated-docstring clause is out of range for the three shapes
  `blizzard/tests/test_openapi_descriptions.py` scans the committed specs for.

## Measurement

Every run records, findings or none:

- Findings opened, per scope swept.
- How many distinct rule ids the run found at least one violation of — the breadth of drift, which a count of findings
  alone hides when one rule accounts for most of them.
