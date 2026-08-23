# Declared sessions

A graph may declare named sessions — a top-level sibling of the node set, not a node facet (graph definition:
[../graphs.md](../graphs.md)). A declaration names one shared lineage of agent context and its policy; nodes reference
it via `fresh:<session>` and `resume:<session>`. All four declaration fields are optional: model preference, effort,
compaction window, rotation bounds. Definitional — a taxonomy of those fields and their resolution (`canon:rule-shape`
§File kinds). Part of the [domain model](../index.md).

## Resolution and pools

Session and node names share one namespace: `resume:<name>` resolves declared-session first, node second, and a
declaration colliding with a node name is rejected. `fresh:<name>` resolves against declarations only — fresh always
mints, so a node name would name nothing there. `fresh:<session>` is a forced rotation point — it starts a new session
that later `resume:<session>` members continue — so a cycle re-entering it begins each iteration on clean context while
downstream members stay on that lineage.

A pool holds one session at a time, scoped to one chunk on one runner; a chunk picked up elsewhere starts with empty
pools.

## Model preference

The model preference is an ordered list of opaque strings — namespaced capability tiers (`blizzard:frontier`,
`blizzard:advanced`, `blizzard:basic`) or harness-native model names. Tiers are unordered roles, not a scale — nothing
substitutes downward — so the list is the only fallback and every degradation is author-written. The graph states a
preference, never a model the fleet must have: tier-to-model mapping is runner configuration, keeping a graph
harness-agnostic (`bzh:app-agnostic-graphs` in
[../../architecture/system-shape.md](../../architecture/system-shape.md)).

Model resolution is left-to-right; an unresolvable entry is skipped, and a wholly unresolvable list falls back to the
runner's default. Model changes take effect only where a pool starts a session, never on a resume: a mid-chunk edit
rotates the pool at its next member rather than switching a running session's model.

## Effort

Effort is a single value, not a list — every harness maps an ordinal somewhere. `low|medium|high|max` is the well-known
vocabulary, extended by runner configuration.

## Compaction window

The compaction window is a tuning knob, not a preference: an opaque string the harness adapter passes straight through
(Claude Code's `--autocompact`), hub-checked only for non-emptiness, reasserted on every invocation — unlike model,
trusted only at mint — and declaration-only, with no chunk-level default.

The window is commensurable only with `rotate.max_context_tokens` (both in tokens, unlike the other bounds): compaction
shrinks context within a step, rotation ends the lineage across steps. A window below `max_context_tokens` means
compaction fires first and keeps firing — the lineage survives, but the worker pays working context mid-task per firing.
A window at or above `max_context_tokens` means rotation ends the lineage first; the window survives only as a ceiling
on the one invocation outgrowing it before the next resume is measured. Their relative order decides which of the pair
bounds an ordinary lineage — declaring both chooses that deliberately, and neither ordering is a default.

## Rotation bounds

Rotation bounds make a lineage finite: a session continues only while every measurable declared bound is under
threshold; past one, the next member starts a new session in the same pool. Bounds cover context size, transcript size,
and harness invocations — the last counting spawns, resumes, judgements, and nudges, so a node-step spends two or three.
An unmeasurable bound is not a breach; a missing measurement leaves the session standing.
