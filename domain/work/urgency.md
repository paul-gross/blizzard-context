# Urgency

How pressing a tenant's work is, as an ordered set of urgencies the tenant configures, one of them its default, and
every chunk carrying exactly one. Spoke of the [work hub](../work.md).

## An urgency

An urgency is a tenant-wide configured record: a handle fixed when it is created, a display name free to change, and a
mark and color a person reads it by. Its handle is unique in its tenant, retired urgencies included, and never changes,
so an urgency has no former handles and a retired one cannot be shadowed by a newcomer. It belongs to the tenant, not to
a project: every project of the tenant chooses from one set ([../projects.md](../projects.md)).

## The set's order

The tenant's urgencies form one order, most urgent first, which an operator sets as a whole or adjusts by moving one
urgency just after another, or to the front. A new urgency lands at the least urgent end unless its creation names where
it goes. Only a change of place changes the order, and every reorder that moves something is recorded with who made it.
A retired urgency keeps its place, so one brought back returns where it stood.

## The default

Every tenant has exactly one default urgency, held in the tenant's settings, and it is never absent. A new tenant starts
with one urgency, `standard`, as its default ([../tenancy.md](../tenancy.md)). Every chunk takes an urgency when it is
minted, and a chunk whose mint names none takes the tenant's default as it stands at that moment.

- **Only a live urgency is the default.** Pointing the default at a retired urgency, or at one the tenant does not hold,
  is refused.
- **Changing the default moves no chunk.** It decides only what is minted from then on.

## Retiring, with the work moved

Retiring an urgency takes it out of the set people choose from. Open work carrying it is never left on a retired
urgency: the operator names where it goes, and the retire moves it there. A retire is refused, in this order:

1. when the urgency is the tenant's default — the default must point elsewhere first;
2. when open chunks carry it and the operator names no destination — the refusal says how many, so the operator can
   choose one;
3. when the destination is not a live urgency of the tenant, or is the urgency being retired.

A retire that clears these moves every open chunk carrying the urgency to the destination, each keeping its rank
([./ranking.md](./ranking.md)), and records how many moved. Nothing can take up the retiring urgency while the retire
runs, so no chunk is left behind on it. A retire with no open work behind it moves nothing, and retiring an urgency
already retired changes nothing. Moving open work is editing chunks, so a retire that moves any needs the permission
editing a chunk asks for, beside the one every configuration change asks for.

A finished chunk is not open: it keeps the urgency it ran under, retired or not.

The same retire clears every routine's default urgency and every chore's override that names the retiring urgency
([../routines-and-scopes.md](../routines-and-scopes.md), [../cadences.md](../cadences.md)), each recorded as that
routine's or cadence's own change, so their runs fall through to the next urgency the chain names
([./chunk.md](./chunk.md#urgency)). Enabling the urgency again restores none of them.

## Enabling

Enabling brings a retired urgency back, meaning what it meant, at its standing place in the order, choosable again. It
is never refused for want of anything, and it moves no chunk back: the work it once carried went where the operator sent
it.

## See also

- [./chunk.md](./chunk.md) — the chunk that carries an urgency.
- [../../architecture/system-shape/configuration.md](../../architecture/system-shape/configuration.md) — the urgency's
  and the tenant settings' departures from the shared configured-record verb set.
