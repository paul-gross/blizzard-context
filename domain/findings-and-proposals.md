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
a pass's word alone. A later run observing the same finding again restores it.

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

## What the hub does not do

The hub never resolves what a class or a locus means, never judges whether a finding is worth having, and never turns a
proposal into work on its own — a person decides that. Holding the vocabulary is not reading it, exactly as indexing a
class is not interpreting one.
