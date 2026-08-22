# Declared sessions

The agent-context lineage several nodes of one graph share, and the policy it runs under. Part of the graph definition
([../graphs.md](../graphs.md)).

A graph may declare **named sessions** beside its nodes — a top-level sibling of the node set, not a node facet. A
declaration names one **lineage of agent context** that several nodes share, and states the policy that lineage runs
under; nodes reference it by name with `fresh:<session>` / `resume:<session>`. A graph declaring none is complete: the
bare `fresh`/`resume`/`resume:<node>` vocabulary needs no declaration and is unaffected.

Session names and node names share **one reference namespace** — `resume:<name>` resolves to a declared session first
and a node second — so a declaration whose name collides with a node's is rejected. `fresh:<name>` resolves against
declarations *only*: `fresh` always mints, and a session minted at another node is not in this node's implicit lineage,
so a node name there would name nothing.

A declaration carries four things, all optional:

- **A prioritized model preference.** An ordered list of opaque preference strings — a namespaced capability *tier*
  (`blizzard:frontier` / `blizzard:advanced` / `blizzard:basic`) or a harness-native model name. The graph states a
  preference; it never states a model the fleet must have. Which name a tier resolves to is each runner's own
  configuration, which is what keeps a graph harness-agnostic (`bzh:app-agnostic-graphs`) — a runner driving a different
  coding harness maps the same tiers to its own models. Resolution is left-to-right, an entry that resolves nowhere is
  skipped rather than failing a spawn, and a list that resolves nowhere at all falls back to the runner's default. The
  tiers are **unordered roles, not a scale**: nothing substitutes downward, so the list is the only fallback mechanism
  and every degradation is author-written.
- **An effort.** Model's twin, as a single value rather than a list — every harness can map an ordinal somewhere, so
  there is no "unrecognized, try the next" case. `low|medium|high|max` is the well-known vocabulary, extended by runner
  configuration.
- **A compaction window (blizzard#343).** A tuning knob, not a preference — an opaque string a harness's own adapter
  interprets and passes straight through (Claude Code's `--autocompact <auto|tokens>`). Like `effort`, the hub checks
  only well-formedness (non-empty), never the vocabulary itself — that recognition is the adapter's alone. Reasserted on
  every invocation, unlike `model`'s mint-only trust in a resume. Shaped like rotation bounds below rather than like
  model/effort: declaration-only, with no chunk-level default to fall back to.
- **Rotation bounds.** What makes a lineage finite. A pool's current session is continued only while every declared
  bound it can measure is under threshold; past one, the next member starts a new session in the same pool. Bounds are
  stated over context size, transcript size, and **harness invocations** — the last counting spawns, resumes, judgements
  and nudges, so one node-step spends two or three of them. A bound that cannot be measured is not a breach: a missing
  measurement leaves the session standing. A compaction window and `rotate.max_context_tokens` are not independent — the
  one commensurable pair, both counted in tokens: compaction shrinks a session's context **in step**, rotation ends a
  lineage **across steps**. Their order picks which of the two actually bounds an ordinary lineage, so a graph declaring
  both chooses that order deliberately. Below the bound, compaction fires first and keeps firing — the lineage survives,
  but the worker pays working context mid-task once per firing. At or above it, rotation ends the lineage first and the
  window survives only as a ceiling on the one invocation that outgrows it before the next resume is measured. Neither
  ordering is the default. The comparison is against `max_context_tokens` specifically, not `max_invocations` or
  `max_transcript_bytes`, which measure different things.

A pool holds **one session at a time**. `fresh:<session>` is a *forced rotation point* — it always starts a new one,
which every later `resume:<session>` member then continues — so a cyclic graph re-entering that node begins each
iteration on clean context while its downstream members stay on the iteration's own lineage. A pool is scoped to one
chunk on one runner; a chunk another runner picks up starts its pools empty.

Model changes take effect **only where a pool starts a session**, never on a resume. A declaration edited mid-chunk
rotates the pool at its next member rather than switching a running session's model, so the cost of a model change is
paid where fresh context is being built anyway.
