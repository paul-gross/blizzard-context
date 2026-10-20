# Released surfaces

This spoke owns what a change may do to a surface a supported release already ships; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A change to a released surface is additive, or a break the window admits (`bzh:released-surface-additive`)

**Rule.** A change to any surface the `blizzard` repo's `docs/versioning.md` names — the HTTP API, the hub↔runner wire,
configuration, the store schema, the trace contract, and the egress contract — is additive to every supported release,
or it is a break the compatibility window admits. `docs/versioning.md` owns the window and what counts as breaking;
`blizzard:compat` ([../../verification/blizzard.md](../../verification/blizzard.md)) decides which a change is. A
removed or reshaped surface keeps its old form beside the replacement, marked deprecated, until a later change may
remove it.

**Why.** A deployment moves its hub, its runner hosts, and its clients onto a release at their own pace, so a break
reaches a live consumer with nothing to catch it. Holding the change to the supported releases, not to a neighbouring
branch, makes the check mean the same thing on every trigger, and attributes a break to the change that makes it.

**Detect.** `blizzard:compat` fails the pull request, the push, and the tag whose committed contract documents break a
supported release in a way the window does not admit. A surface that no committed document describes is invisible to it.

**Do.** Add the field, route, key, column, or span beside the old one and deprecate the old with the surface's own mark.
When the break is unavoidable, follow `workflows/judging-a-break.md`
([../../workflows/judging-a-break.md](../../workflows/judging-a-break.md)): it decides between keeping both forms, a
break the window admits, and a break that waits for a later change.

**Don't.** Remove or rename a released surface in the change that deprecates it, or regenerate a contract document to
make a finding disappear.

**See also.** `bzh:fleet-wire-additive` ([./fleet-wire.md](./fleet-wire.md)): the wire's own form of this rule.
`bzh:store-expand-contract` ([../../standards/persistence.md](../../standards/persistence.md)): the store schema's.
