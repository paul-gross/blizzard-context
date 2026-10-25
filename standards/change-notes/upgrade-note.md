# An operator-facing step is an upgrade section (`bzh:upgrade-note`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

What a release asks of an operator travels as the change note's `## Upgrade` section, in the operator's terms: what to
upgrade first, what to set or remove, and what they will see if they skip it. A breaking note and a removal carry one.
Any other note carries one when its release asks something without breaking anything — a key worth setting before the
first start, a slow migration to plan around.

A step a work item's `## Landing and deployment` section would ask of whoever deploys the change — a key to set, a
halves-in-order restart, a command to run before the first start — is an operator-facing step: the change writes it as
its note's upgrade section, not only in the work item.

A crossing that needs more than a paragraph — an upgrade order, a failure mode, a way back — gets a boundary section in
`docs/upgrade.md`, added under `## Upgrading to the next release` in the same change. The note's upgrade section then
says in a sentence or two what the crossing asks and sets `upgrade-guide` to the section's anchor; it never restates the
section. The format of both is `blizzard`'s `changes/README.md`.

## Why

The release's **Upgrade notes** are the one place an operator, blizzard's own instance among them, reads what taking the
release demands; a step left in a work item is a step the release never mentions.

## Detect

A change whose work item or description asks something of whoever deploys it, with no `## Upgrade` section on its note;
a boundary section whose content is repeated in the note; a boundary no note links through `upgrade-guide`; an upgrade
section on a breaking or removal note that is missing.

## Do

*"Set `[runner.throttle.budget]` before the first start, or the runner refuses the dollar-budget lever."* — a short step
in the note; a long crossing as a `docs/upgrade.md` boundary the note links.

## Don't

An `## Upgrade` section that says *"see the issue"*, or that copies a boundary section's paragraphs.

## See also

- [./change-note.md](./change-note.md) — what the note's body says.
- [./deprecation-note.md](./deprecation-note.md) — a removal's upgrade section.
