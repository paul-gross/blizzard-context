# Findings and proposals

A **finding** is one instance a routine's run observed — not a theme, not a tally: seventeen occurrences of the same
weed are seventeen findings, each with its own locus and its own id. A **garden proposal** is a proposed response to one
or more findings. Both are durable hub entities, first class the way an artifact is, and both persist as evidence
whether or not anyone ever acts. Part of the [domain model](./index.md); the machinery both ride is
`blizzard-product:/plans/garden/machinery.md`, which this does not restate.

## Identity is the hub's to assign

A finding is minted only at delivery, with its own hub-assigned id — an agent never invents one, since a run names what
it means by reference rather than recomputing whether two observations are the same finding. A delivered list becomes
its own **finding set**, one per artifact, pointing back at the run that delivered it and carrying that list's scope,
the per-repository revisions the run read, and the routine's own measurement — properties of the list, not of any single
finding inside it.

## A run emits a delta, not a state

What a run delivers is not the routine's new standing state; it is the change to apply to it. Emitting nothing about a
finding is never a claim about it — a finding outside a run's scope keeps its last word, and a scoped or delta run stays
honest without asking anything of an agent's discipline.

## Liveness is derived, and reversible

Whether a finding is live is never a stored state; it is the newest thing a run said about it. A run reporting a finding
**gone** does not close it — it flags the finding for a person, because leaving the live set is a human judgment, never
a pass's word alone. A later run observing the same finding again restores it — but only while it is merely `gone`. Once
a person has exited it, a run's own ops go no further: a run cannot revive what a person closed, only a person's own
`reopened` can, the same authority that closed it in the first place.

A person closes that loop with one of five exit verbs — **resolved**, **gone-confirmed**, **wont-fix**,
**not-a-finding**, **superseded** — and **reopened** undoes any of them, the same append-only fact the way `gone` and
`observed` already are: never a stored column, always a newest-fact-wins read. The five split into two kinds of exit.
**Outflow** — resolved, gone-confirmed — is the ground itself changing: work landed, or a person confirmed by hand that
the finding no longer reproduces, the same kind of event a `gone` fact already reports, just said with a person's
authority instead of a run's. **Withdrawn** — wont-fix, not-a-finding, superseded — is a judgment call about the finding
itself, never the code: the ground hasn't moved, a person has decided the finding doesn't merit standing regardless.
Both are exits and both leave the live set for good — the split exists because what a fleet later reports about outflow
and withdrawal answers different questions, not because one exit outranks another.

## `class` and `locus` are opaque

Both a finding's `class` and a proposal's `class` are the deployment's own vocabulary — a kind of weed, a kind of
response. The hub indexes and counts them, and never interprets either: it can tell how often a class recurs without
knowing what the name means, which is what any case for mechanizing a judgment rests on. A finding's `locus` is where it
lives, read and stored the same way.

## A proposal needs at least one finding

A garden proposal names every finding it answers, required and non-empty — a proposal with nothing behind it is an
opinion no run was asked for. Grouping findings under one response is the proposal's whole job; a finding itself never
groups.

## Never confused with a work-item proposal

A garden proposal and a work-item proposal (`domain/work.md`) are unrelated entities that happen to share a word. Both
are always named in full — `garden proposal` for this one — so neither inherits an unqualified `proposal` the other
could be mistaken for.

## Closing a proposal: pass or accept

A garden proposal carries two closing verbs, and both leave a durable record — closure is terminal, exactly like a work
item's own (`domain/work.md`). **Passing** is not a dismissal: it is the note that stops a later run raising the same
response as though it were new, and it wants a reason more than accepting does. **Accepting** records agreement, and
most acceptances mint work — a self-sourced hub work item, linked to the proposal in the same act, carrying the
proposal's own body unless the accept supplies a different one. Minting stays the default; declining to mint is the
deliberate act, because a spurious backlog item is visible and deletable while a real commission that silently mints
nothing is a decision nobody can find again.

Acceptance does not promote the item it mints — it rests behind the ordinary promote gate a person still has to open —
and it does not move the findings behind the proposal: work being under way is not an observation that the ground
changed, so an accepted proposal's findings stay live until a run reports them gone or a person withdraws them.

## What the hub does not do

The hub never resolves what a class or a locus means, never judges whether a finding is worth having, and never turns a
proposal into work on its own — a person decides that. Holding the vocabulary is not reading it, exactly as indexing a
class is not interpreting one.
