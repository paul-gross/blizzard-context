# Routines and scopes

A **scope** is an operator-named bucket — a slug and a description, findings grouped into it. The slug is lowercase
letters, digits, and hyphens, at least one character and nothing else; whatever wants prose goes in the description. A
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
untouched. What retiring does is withdraw the scope from selection — a retired scope is offered to no new run, and a
routine's record of when it last swept each scope covers a retired one only where that routine has already swept it —
while nothing recorded under it moves: its findings keep whatever state they had, and stay queryable, and its membership
in a routine's declared set stands until an explicit unlink. Naming a retired scope again, by minting it or as a
routine's default, is not refused; running against it is ([What refuses](#what-refuses)).

## A routine sweeps a declared set of scopes

A routine's default scope is not the only scope it may sweep: a routine also declares a set of scopes it belongs to, a
many-to-many relationship between routines and scopes, and its default is always a member of that set. The set can only
grow the default's membership, never lose it — a routine may come to declare several scopes, but never fewer than the
one its default names. A scope joins the set only once it exists: unlike a routine's default, which mints the scope it
names, growing the set never mints one, and naming a scope that does not exist is refused
([What refuses](#what-refuses)).

## A run is an act of the pair

`blizzard hub routine run <name>` mints, ingests, and promotes a work item in one act, addressed at the routine and an
effective scope — the routine's own default, or an explicit override minted the same way a bare scope name is. Mode
settles the baseline, never admission: a `full` run needs no baseline, while a `delta` run runs against the
routine/scope pair's own recorded revision, and downgrades to `full` — on the record, never refused — when the pair has
recorded none yet. What turns a run away is [What refuses](#what-refuses). What the pair carries between runs is
`blizzard-product:/plans/garden/machinery.md`'s own fact; this states only the run's behavior over it. A run's own scope
handling is unchanged by a routine's declared set: an effective scope is still freely named or minted regardless of
whether it belongs to that set.

## What refuses

Each of these is refused wherever the act is offered, and refused outright — never quietly absorbed into something
already recorded, never quietly re-addressed at something else: a slug is not normalized, a mint does not hand back what
already holds the name, a management verb does not create what it failed to find, and a run is not sent to another scope
or another graph.

- **A slug outside its shape** — empty, or carrying anything but lowercase letters, digits, and hyphens — wherever a
  scope is named: minting or editing one, a routine's default, a run's override, either verb over a routine's declared
  set.
- **A routine name already taken** — at mint. A routine's name is claimed once, where a scope's slug is not
  ([Mint-on-name](#mint-on-name)): a second routine under a name already held is refused, never merged into the routine
  holding it.
- **A scope that does not exist** — when a routine's declared set is grown to name it, that verb minting nothing of its
  own ([A routine sweeps a declared set of scopes](#a-routine-sweeps-a-declared-set-of-scopes)).
- **A graph that does not resolve** — no enabled graph carries the name, resolution being
  [graphs/identity.md](./graphs/identity.md)'s — both when a routine is authored, create and edit alike, and when it
  runs: a graph may retire after a routine came to point at it, and the run is refused rather than the routine
  repointed.
- **A retired effective scope** — the routine's default or an explicit override — when a run is addressed at it.

Two more refusals guard a field of an existing routine rather than any act above, and are stated where that field is: a
routine's name never changes ([The name is a routine's lineage](#the-name-is-a-routines-lineage)), and its default scope
is never unlinked from its declared set
([A routine sweeps a declared set of scopes](#a-routine-sweeps-a-declared-set-of-scopes)).

## A run is readable independent of delivery

A run is enumerable the moment it is minted, whether or not it ever delivers — an escalated run that never wrote a
finding is as much a run as a delivered one, and both are read from the same act's own record, never from what delivery
produced. A run's outcome is the same derived chunk status every other chunk carries
(`architecture/system-shape/store-facts.md`'s `bzh:facts-not-status`), not a garden-specific status of its own. A
fanned-out survey's run can deliver more than one finding set in the same act — several lists published, every one of
them under the run's own effective scope — and each stays its own set, distinguishable from the others, never merged
into one.

## What the hub does not do

The hub stores a scope's slug and hands it back — to a routine's default, to a list, to a lookup — without ever
interpreting what the slug names. Resolving a scope into whatever it actually denotes is entirely outside the hub's
knowledge.
