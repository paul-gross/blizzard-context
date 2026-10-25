# A deprecation names its removal line (`bzh:deprecation-note`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

A deprecation is a note of kind `deprecated` whose `removes-in` names the line that will remove the surface: a major
from 1.0 on, a minor before it. A released deprecation's `removes-in` is never edited; moving it to a later line is a
new `changed` note that `postpones` the deprecation and names the new line in its own `removes-in`, so a moved date is
itself announced. The change that removes a deprecated surface writes a `removed` note with `breaking: true`, an upgrade
section ([./upgrade-note.md](./upgrade-note.md)), and `retires` naming the deprecation's id. A break with no prior
deprecation is a `changed` or `removed` breaking note naming what breaks in `breaks`, with a `!` commit subject. Fields
and their validation are `blizzard`'s `changes/README.md`; whether a break is allowed at all is
`bzh:released-surface-additive`
([../../architecture/system-shape/released-surfaces.md](../../architecture/system-shape/released-surfaces.md)).

## Why

An operator plans around a removal only if the release that announced it named when it would land, and the release that
delivers it can be traced to that announcement.

## Detect

A `deprecated` note with no removal line; an edit to a released deprecation's `removes-in`; a postponement that is not a
note; a removal that retires nothing and was not a declared break; a removal or breaking commit whose subject lacks the
`!`.

## Do

*"The `[legacy]` section of the hub configuration is deprecated; use `[hub]`."* with `removes-in: "2"`; later, *"Removes
the `[legacy]` section"* with `retires` naming that note and an `## Upgrade` section moving each setting.

## Don't

Rewriting a released note's `removes-in` to push the date out, or dropping a deprecated field with no `retires` note.

## See also

- [./change-note.md](./change-note.md) — the judgement every note shares.
- [../persistence.md](../persistence.md) — `bzh:store-expand-contract`, the same break discipline for stores.
