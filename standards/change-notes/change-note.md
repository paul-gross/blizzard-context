# A noticeable change owes a note (`bzh:change-note`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

Every change an operator would notice commits one change note in the same change, one per noticeable change rather than
per commit. *Noticeable* is anything the people who run blizzard can see, set, or must do differently after taking the
release: a CLI verb, flag, or output; a configuration key or its default; an HTTP route or field; a board surface they
use; how the fleet claims, lands, spends, or recovers; a fix to something they could have hit; a change to an operator
document's procedure. No note is owed for a refactor, a test, a CI or tooling change, a change to `blizzard-context`, or
a fix to a defect that never reached a release.

The body is one to three sentences in the present tense, in the operator's vocabulary
([../operator-vocabulary.md](../operator-vocabulary.md)), saying what is now true for them and naming the verb, key,
route, or surface they would recognise. It names no module, and no chunk, issue, or pull request. A `fixed` note names
the symptom the operator saw, not the cause. The file's location, id, fields, and headings are `blizzard`'s
`changes/README.md`.

## Why

The release body is assembled from these notes alone, so a change with no note never reaches the operator who must react
to it, and a note describing the implementation tells that operator nothing they can act on.

## Detect

A change touching a surface the Rule lists, with no added note under `changes/unreleased/` (`blizzard:change-notes`
already fails a changed contract document with none, so a reviewer reads for the rest); a note whose body names a
module, a cause, or the work item it came from; a note on a change no operator can notice; two notes for one change.

## Do

A `fixed` note: *"The board no longer shows a finished chunk as running after a reload."* An `added` note: *"Adds
`blizzard runner status`, which prints the runner's current lease."*

## Don't

*"Refactors `LeaseStore` to batch heartbeats"* — an implementation. *"Fixes a race in the reaper"* — a cause, where the
operator saw a symptom.

## See also

- [./upgrade-note.md](./upgrade-note.md) — what the note's `## Upgrade` section holds.
- [./deprecation-note.md](./deprecation-note.md) — the notes a deprecation, postponement, and removal write.
- [../../workflows/change-notes.md](../../workflows/change-notes.md) — the procedure that applies this rule.
