# The `mutation-testing` axis

The gardening axis that holds blizzard's fast tiers to what they pin rather than what they run. A spoke of the
[garden registry](./index.md); the four fields below are the shape `canon:gardening-axes` requires.

## Evaluates

Behavior the fast tiers execute but never check — surfaced as mutants that survive them: a single alteration
`blizzard:mutation` makes to a line while every `unit`-tier test it selects stays green. The command reports a survivor
as a candidate, not a finding. Concretely, on this target:

- A test that executes the mutated line and asserts nothing the mutation changes.
- A production branch no selected test takes, so the mutant on it is never observed.
- Code whose mutation is invisible because nothing observable depends on the code.
- An equivalent mutant left unsuppressed on a line the marker could take, returning as noise on every run.

This axis and the `tests` axis blizzard's garden plan names are opposite readings of the same suite: this one finds what
is unpinned — the behavior a green suite would let regress — where `tests` prunes what is excess — the duplicate, the
ceremony, the case welded to an implementation. A finding here names an assertion to add; a finding there names a case
to remove. A test that executes a line and asserts nothing about it is in range for both, and the split is by remedy:
naming the assertion that would kill the mutant is this axis's, and judging whether the test earns its place once it
asserts something is the other's.

## Scope

The slugs `mise run mutation` accepts, one per scope row in `blizzard/scripts/mutation.py` — that table is the one home
for each slug's mutate globs and test selection, so a slug here means exactly the ground it means there.

| Slug            | Ground                                                                                                |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| `hub-daemon`    | The hub's domain, stores, API, delivery, graphs, and work sources, less its command surface           |
| `runner-daemon` | The runner's domain, loop, stores, API, harness, environments, and selftest, less its command surface |
| `shared-spine`  | The daemon-neutral layer both daemons depend on, the wire models, and the shared auth core            |
| `cli-surface`   | The hub and runner command surfaces and the shared CLI entry package                                  |

A delta run's ground is the slug's functions changed since the baseline revision, per `--since` in
[`../verification/blizzard/commands/mutation.md`](../verification/blizzard/commands/mutation.md).

No `web-suite` slug: `blizzard:mutation` mutates `src/blizzard` only, and the Angular suite has no mutation method.

## Criteria

The two ids below, and the files that own them, which are the only home for their prose:

- `bzh:mutation-review-selection` in [`../verification/blizzard/evidence.md`](../verification/blizzard/evidence.md) —
  what a surviving mutant is evidence of, and the litmus by which a check that passes without the change is a mutant
  rather than evidence.
- `bzh:mutation-survivor-classification` in
  [`../verification/blizzard/mutation-survivors.md`](../verification/blizzard/mutation-survivors.md) — the classes a
  survivor is sorted into, the remedy each class obliges, and how an equivalent mutant is suppressed so no later run
  reports it again.

Where a command already judges the same question, it owns that judgement and this axis does not
(`winter-canon:/enforcement-channels.md`):

- Whether a mutant is killed is `blizzard:mutation`'s verdict, not this axis's — a run reads `mutants/report.json` and
  judges only the survivors it lists.
- What the method cannot see — the tiers above `unit`, the trees no scope names, the paths its configuration excludes,
  the decorated function bodies mutmut skips — is out of range here;
  [`../verification/blizzard/commands/mutation.md`](../verification/blizzard/commands/mutation.md) states that reach,
  and a production path pinned only above `unit` is `bzh:gating-tier-pins-production-paths`'s, judged per change.

## Measurement

Every run records, findings or none:

- Mutants generated, killed, and surviving, per scope swept — the per-status counts `mutants/report.json` carries.
- Survivors the run left unclassified, per scope swept — the backlog a bounded pass hands the next one, which a count of
  findings alone hides.
- Findings opened, per class.
