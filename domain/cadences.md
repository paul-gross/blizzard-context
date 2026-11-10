# Cadences

A **cadence** is a project's bucket of rhythm: when, and how often, the routines it keeps should run. A **chore** is one
routine a cadence keeps, with the scopes it runs over, the mode its runs take, a note each run carries, whether the work
each run makes is admitted to the queue, and optionally its **override**: the urgency its runs take over the routine's
default urgency ([work/chunk.md](./work/chunk.md#urgency)). An **errand** is one chore over one scope. Part of the
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

## When an errand is due

An errand's runs are the runs minted for it, and its last run is the newest of them, whatever became of the work that
first held it. A run started by hand, or minted by another chore, is none of its runs. A last run is settled once it is
finished, stopped, or withdrawn; a run waiting on a person is not settled, so a failure is never quietly retried.

A settled errand is due by its cadence's rhythm. Under a spacing, it is eligible once the spacing has passed since the
last run's chosen moment, and at once when it has never run. Under a schedule, it is due once a moment has fallen since
its last run was minted, or, for an errand that has never run, since it joined its chore — when the chore last set its
scopes or, for an all-scopes chore, when the scope was linked to the routine, whichever is later. Under both, it is due
once a moment has fallen since then and the spacing has passed. Nothing is kept about when an errand is next due: it is
worked out each time it is asked.

A moment the hub did not see is not lost. The errand is owed one run, minted the first time the hub looks after that
moment, however late, and never one run for each moment it missed.

Each due errand's run is minted as a hand-started run is, meeting the same refusals. A chore that admits its work to the
queue admits its run as it is minted; any other chore's run rests behind the promote gate.

## One live run per errand (`bzh:errand-one-live-run`)

**Rule.** An errand whose last run is not settled is never due, whatever its rhythm says; this is judged before any
moment or spacing is read, and judged again as the run is minted.

**Why.** A fleet behind on its queue would otherwise pile up a run for every moment it fell behind; holding one run per
errand keeps a slow fleet and a run waiting on a person to one outstanding run each.

**Do.** An errand whose evening run is still waiting on a person at the next evening's moment mints nothing; once that
run is stopped, the errand is due again and mints one run.

**Don't.** Mint a second run of an errand because a moment fell while its first run was still being worked.

## Linked by slug

A chore names its routine and its scopes by slug, never by anything minted for them, and those names are resolved each
time the cadence is read. A routine's slug is its lineage
([routines-and-scopes.md](./routines-and-scopes.md#the-slug-is-a-routines-lineage)) and a scope's slug is unique in its
project, so a slug holds as steadily as an id would. Naming by slug lets a cadence be declared beside the routine it
keeps, before either exists.

A chore's override is written by the urgency's slug too, but unlike the routine and the scopes it must resolve, and
holds the urgency itself, not the slug: a chore naming an urgency the tenant does not hold, or a retired one, is
refused. Retiring an urgency clears every override naming it
([work/urgency.md](./work/urgency.md#retiring-with-the-work-moved)), and an override found retired at a run names none,
so the run falls through to the routine's default.

## A chore's identity across edits

A chore is keyed within its cadence by its key. An edit that keeps a key keeps the chore, whatever else it changes — its
routine, its scopes, its mode, its note, whether it admits its work, its urgency — so its errands keep their history. An
edit that drops a key ends that chore, and writing the key again later makes a new chore, whose errands have never run.
A key is never renamed: renaming a chore is removing one and adding another.

## The retired brake

A cadence carries the same reversible brake a routine and a scope do
([routines-and-scopes.md](./routines-and-scopes.md#the-retired-brake)): a retired cadence makes no work, and re-enabling
it lets it make work again. Retiring stops nothing already running. A cadence that keeps a chore admitting its work to
the queue is itself an admission, so only someone who may admit work may leave one live with such a chore; retiring one
admits nothing, so it asks no more than any other edit.

## Needs attention, never invalid

A cadence is refused only when its shape cannot mean anything, or a chore's override names no live urgency
([Linked by slug](#linked-by-slug)). What it points at may come and go beside it: a routine nobody holds, a retired
routine, a routine whose graph no longer resolves, a scope unknown, retired, or not linked to the routine, a chore with
no scopes left to run over, and a cadence with no chores are each accepted. Each is shown as attention the cadence
needs, naming the chore and, where it stops one errand only, the scope — the refusals a hand-started run would meet,
shown before the cadence fires. Attention is read as things stand, never kept. A retired cadence needs none.
