# Cadences

A **cadence** is a project's bucket of rhythm: when, and how often, the routines it keeps should run. A **chore** is one
routine a cadence keeps, with the scopes it runs over, the mode its runs take, a note each run carries, and whether the
work each run makes is admitted to the queue. An **errand** is one chore over one scope. Part of the
[domain model](./index.md).

A cadence belongs to one project ([projects.md](./projects.md)), fixed when it is made, and its slug is unique within
that project, retired cadences included. Its name is a free display name.

## The rhythm

A cadence states a schedule, a spacing, or both. A schedule names the moments the cadence may fire, read as wall-clock
time in a named time zone. A spacing names the least time between two runs of one errand, counted from a moment of that
errand's last run: when it was scheduled, when it started, or when it finished — when it started, unless the cadence
says otherwise. A cadence stating neither would never come due, so it is refused; so is a schedule that names no moment
at all, and a choice of moment to count from with no spacing to count.

## The errand is derived

An errand is never configured. A chore over every scope its routine sweeps holds one errand for each of those scopes, a
chore over listed scopes holds one for each listed scope, and a chore naming no scopes holds one over its routine's
default scope. Linking a scope to the routine, or retiring one, changes which errands an all-scopes chore holds, with no
edit to the cadence.

## Linked by slug

A chore names its routine and its scopes by slug, never by anything minted for them, and those names are resolved each
time the cadence is read. A routine's slug is its lineage
([routines-and-scopes.md](./routines-and-scopes.md#the-slug-is-a-routines-lineage)) and a scope's slug is unique in its
project, so a slug holds as steadily as an id would. Naming by slug lets a cadence be declared beside the routine it
keeps, before either exists.

## A chore's identity across edits

A chore is keyed within its cadence by its key. An edit that keeps a key keeps the chore, whatever else it changes — its
routine, its scopes, its mode, its note, whether it admits its work — so its errands keep their history. An edit that
drops a key ends that chore, and writing the key again later makes a new chore, whose errands have never run. A key is
never renamed: renaming a chore is removing one and adding another.

## The retired brake

A cadence carries the same reversible brake a routine and a scope do
([routines-and-scopes.md](./routines-and-scopes.md#the-retired-brake)): a retired cadence makes no work, and re-enabling
it lets it make work again. Retiring stops nothing already running. A cadence that keeps a chore admitting its work to
the queue is itself an admission, so only someone who may admit work may leave one live with such a chore; retiring one
admits nothing, so it asks no more than any other edit.

## Needs attention, never invalid

A cadence is refused only when its shape cannot mean anything. What it points at may come and go beside it: a routine
nobody holds, a retired routine, a routine whose graph no longer resolves, a scope unknown, retired, or not linked to
the routine, a chore with no scopes left to run over, and a cadence with no chores are each accepted. Each is shown as
attention the cadence needs, naming the chore and, where it stops one errand only, the scope — the refusals a
hand-started run would meet, shown before the cadence fires. Attention is read as things stand, never kept. A retired
cadence needs none.
