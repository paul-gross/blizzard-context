# Routines and scopes

A **scope** is an operator-named bucket — a slug and a description, findings and proposals grouped into it. A
**routine** is an operator-named pointer at a graph its runs execute, a default scope, and default run preferences
(model, effort); a run is the routine acting, addressed at itself and an effective scope. Part of the
[domain model](./index.md).

## Mint-on-name

A scope comes into existence the moment its slug is first named — either an operator naming it directly, or a routine
naming a default scope no scope yet holds. Naming an already-existing slug again is not an error and does not overwrite
what is already recorded against it: minting is idempotent, and a scope's description is changed only by explicitly
editing it.

## The name is a routine's lineage

A routine's name, not its id, is what a run, a finding, or a proposal is understood to belong to across the routine's
whole life. The name is fixed at mint and never changes; editing a routine may change which graph it points at, its
default scope, or its run preferences, but never what it is named.

## The retired brake

A scope carries the same reversible, append-only retirement brake a graph does: retiring one and re-enabling it are both
facts recorded over time, never a destructive edit, and either direction leaves the scope's slug and description
untouched.

## A run is an act of the pair

`blizzard hub routine run <name>` mints, ingests, and promotes a work item in one act, addressed at the routine and an
effective scope — the routine's own default, or an explicit override minted the same way a bare scope name is. A `full`
run always proceeds; a `delta` run runs against the routine/scope pair's own recorded revision, and downgrades to `full`
— on the record, never refused — when the pair has recorded none yet. What the pair carries between runs is
`blizzard-product:/plans/garden/machinery.md`'s own fact; this states only the run's behavior over it.

## A run is readable independent of delivery

A run is enumerable the moment it is minted, whether or not it ever delivers — an escalated run that never wrote a
finding is as much a run as a delivered one, and both are read from the same act's own record, never from what
delivery produced. A run's outcome is the same derived chunk status every other chunk carries
(`architecture/system-shape/store-facts.md`'s `bzh:facts-not-status`), not a garden-specific status of its own. A
fanned-out survey's run can deliver more than one finding set in the same act — several scopes swept together, several
lists published — and each stays its own set, distinguishable from the others, never merged into one.

## What the hub does not do

The hub stores a scope's slug and hands it back — to a routine's default, to a list, to a lookup — without ever
interpreting what the slug names. Resolving a scope into whatever it actually denotes is entirely outside the hub's
knowledge.
