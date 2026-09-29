# Findings and proposals

A **finding** is one instance a routine's run observed — not a theme, not a tally: seventeen occurrences of the same
weed are seventeen findings, each with its own locus and its own id. A **garden proposal** is a proposed response to the
findings behind it — it may name none at all (§A proposal's findings are optional). Both are durable hub entities, first
class the way an artifact is, and both persist as evidence whether or not anyone ever acts. Part of the
[domain model](./index.md); the machinery both ride is `blizzard-product:/delivered/garden/machinery.md`, which this
does not restate.

## Identity is the hub's to assign

A finding is minted only at delivery, with its own hub-assigned id — an agent never invents one, since a run names what
it means by reference rather than recomputing whether two observations are the same finding — and with its own scope,
one per finding, fixed at that mint. A delivered list becomes its own **finding set**, one per artifact, pointing back
at the run that delivered it and carrying the per-repository revisions the run read and the routine's own measurement —
properties of the list, not of any single finding inside it. The set declares one scope as well — the run's own
effective scope, no other — and the declaration is a constraint, not a grouping laid over the findings from outside:
every op naming an existing finding must name one recorded under that same scope, and one op naming a finding under
another scope refuses the whole delivery.

## A finding can also be raised by a delivery lane's review

Minting is not a run's alone: a delivery lane's own review round can raise a finding too, at the chunk's landing. A
review-sourced finding carries no routine lineage — it answers to no routine's delta-diffing history, only to the scope
it was filed under — and carries its own `severity`, blizzard's own closed vocabulary (`blocking`/`should-fix`), unlike
the deployment-opaque `class`/`locus` every finding also carries. It also names the chunk whose review raised it. It is
visible to every routine run sweeping that same scope, exactly as if that routine had raised it itself, and a run may
answer it with `observed`/`gone` like any other. It arrives in no finding set — the one exception to the finding set's
own "one per artifact" rule above — because a review delta spans whatever scopes its entries name and has no run behind
it to measure.

## A run emits a delta, not a state

What a run delivers is not the routine's new standing state; it is the change to apply to it. Emitting nothing about a
finding is never a claim about it — a finding outside a run's scope keeps its last word, and a scoped or delta run stays
honest without asking anything of an agent's discipline.

## Liveness is derived, and reversible

Whether a finding is live is never a stored state; it is the newest thing a run said about it. A run reporting a finding
**gone** does not ordinarily close it — it flags the finding for a person, because leaving the live set is a human
judgment, never a pass's word alone. A later run observing the same finding again restores it — but only while it is
merely `gone`. Once a person has exited it, a run's own ops go no further: a run cannot revive what a person closed,
only a person's own `reopened` can, the same authority that closed it in the first place.

One state is recorded by no hand at the moment it lands, and it is not an exit: delivery of the item an accepted garden
proposal minted closes that proposal's still-live findings to **delivered**, carrying the accepter's own authority —
[Closing a proposal](#closing-a-proposal-pass-or-accept) owns the mechanics. `delivered` is neither `live` nor one of
the five exits below; nobody has confirmed the delivery's claim yet. It stays visible to the routine that owns the
finding, and only that routine's own next run clears it — a `gone` op against a `delivered` finding is the one case
where a run's own word does settle it for good, completing the exit to **resolved** that the delivery only claimed; an
`observed` op against one instead reads as the delivery having been wrong or premature, and restores it to `live`,
exactly like reviving a merely-`gone` finding.

A person closes that loop with one of five exit verbs — **resolved**, **gone-confirmed**, **wont-fix**,
**not-a-finding**, **superseded** — and **reopened** undoes any of them, the same append-only fact the way `gone` and
`observed` already are: never a stored column, always a newest-fact-wins read. **superseded** is the one verb that names
another finding: the one absorbing it, which must itself be live and is never the finding being exited. The five split
into two kinds of exit. **Outflow** — resolved, gone-confirmed — is the ground itself changing: work landed, or a person
confirmed by hand that the finding no longer reproduces, the same kind of event a `gone` fact already reports, just said
with a person's authority instead of a run's. **Withdrawn** — wont-fix, not-a-finding, superseded — is a judgment call
about the finding itself, never the code: the ground hasn't moved, a person has decided the finding doesn't merit
standing regardless. Both are exits and both leave the live set for good — the split exists because what a fleet later
reports about outflow and withdrawal answers different questions, not because one exit outranks another.

## `class` and `locus` are opaque

Both a finding's `class` and a proposal's `class` are the deployment's own vocabulary — a kind of weed, a kind of
response. The hub indexes and counts them, and never interprets either: it can tell how often a class recurs without
knowing what the name means, which is what any case for mechanizing a judgment rests on. A finding's `locus` is where it
lives, read and stored the same way.

## A proposal's findings are optional

A garden proposal may name no findings at all: the hub enforces no minimum, empty or not. Whether a graph's own routine
requires one is that graph's own decision to make, never the hub's — the hub only stores, groups, and counts whatever a
proposal names. Grouping findings under one response is still the proposal's whole job when it names any; a finding
itself never groups.

## A proposal's origin: a routine's run, or an operator

A garden proposal is minted from one of two origins, a fact fixed at mint and never inferred from an absent routine: a
**routine's run**, raised by its own delivery, or an **operator**, authored directly by a person through the hub API or
CLI. An operator-authored proposal may name a routine or none — the routine is optional there, the way it never is for a
routine-run proposal — and when it names findings, they may come from any routines and scopes at once: a proposal
carries no scope of its own, so nothing about its origin narrows which findings it may group. A finding may belong to
more than one proposal, of either origin, open or closed — grouping is not exclusive.

A routine's run is shown every finding it may cite: its routine's non-exited findings in every scope, plus
review-sourced ones on its own scope. Its proposals may cite any of them, while its finding set's `observed` and `gone`
ops stay within its own scope.

## A proposal may be edited while it is open

Title, class, body, and the findings a proposal names may all change while the proposal is still open, regardless of its
origin — a routine-run proposal is exactly as editable as an operator-authored one. Closure makes it immutable: once
passed or accepted, no further edit, attach, or detach reaches it. This is a plain in-place replacement, not an
append-only history — the newest edit is the only one that survives, never a superseded trail of prior versions.

## Never confused with a work-item proposal

A garden proposal and a work-item proposal (`domain/work.md`) are unrelated entities that happen to share a word. Both
are always named in full — `garden proposal` for this one — so neither inherits an unqualified `proposal` the other
could be mistaken for.

## Closing a proposal: pass or accept

A garden proposal carries two closing verbs, and both leave a durable record — closure is terminal, exactly like a work
item's own (`domain/work.md`). **Passing** is not a dismissal: it is the note that stops a later run raising the same
response as though it were new, and it wants a reason more than accepting does. **Accepting** records agreement, and
most acceptances mint work — a self-sourced hub work item, linked to the proposal in the same act, its body the
proposal's own (or the accept's override) wrapped in a template naming the findings behind it, when it names any, so the
worker the item reaches can tell which findings it answers; a proposal naming none mints an item whose body carries no
such template at all. Minting stays the default; declining to mint is the deliberate act, because a spurious backlog
item is visible and deletable while a real commission that silently mints nothing is a decision nobody can find again.

Acceptance does not promote the item it mints — it rests behind the ordinary promote gate a person still has to open —
and it does not move the findings behind the proposal: work being under way is not an observation that the ground
changed. The item landing is. When the item an accepted proposal minted is delivered, the proposal's findings that are
still live are closed to **delivered** in that same act — carrying the accepter's authority and naming the proposal it
answered, but not yet an exit — while a finding a run has since reported gone, or a person has already exited, is left
exactly as it stands. The closure lands once per proposal: a retry of the delivery never redoes it. What settles a
`delivered` finding for good is the owning routine's own next run, not the delivery itself (§Liveness is derived, and
reversible) — a later `reopened` on one that has already settled to `resolved` is a person's word that only a person can
answer again. Until that delivery, an accepted proposal's findings stay live unless a run reports them gone or a person
exits them.

## What the hub does not do

The hub never resolves what a class or a locus means, never judges whether a finding is worth having, and never turns a
proposal into work on its own — a person decides that. Holding the vocabulary is not reading it, exactly as indexing a
class is not interpreting one.
