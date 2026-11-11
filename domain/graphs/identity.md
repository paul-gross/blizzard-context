# Graph identity

A graph pairs an immutable definition with mutable operational metadata; every edit creates a new graph rather than
changing an existing one, so anything pinned to one can trust it forever. This file states a graph's identity, what that
identity freezes, the bound on any same-id representation change, the one legacy carry-over admitted outside that bound,
and its mutable operational surfaces; the definition's content is routed from [../graphs.md](../graphs.md). Part of the
[domain model](../index.md).

## Standalone graphs

There is no graph family or version tree: graphs are standalone, and nothing links a graph to a successor. Any graph may
migrate its chunks to any graph so long as the node mapping gets them over — apparent workflow versions are just
migrations onto a graph sharing the name, emergent rather than modeled. [../work/migration.md](../work/migration.md)
owns how and when a chunk migrates and what `follow-latest` actually does.

## What an identity freezes

A graph's identity freezes its authored definition — nodes and their routes, prompts and addenda, model tiers and
session policy, checks, retries and timeouts, each action and the meaning of its arguments, and declared artifact
content — and the original definition text its mint recorded, which is the authoring evidence for that graph. None of it
is editable under an existing graph, node, or choice id: an actual change to any of it is a new definition, minted as a
new graph. Keeping only the recorded text unchanged does not make a changed executable workflow immutable; the
executable view is what the identity vouches for.

An identity freezes the authored definition, not everything around it. The application build that runs a graph, an
external forge, and every independently owned configuration record keep their own contracts and move on their own terms,
so a graph id promises no bit-identical runtime behavior forever — and that qualification permits no authored semantic
edit in place.

## Representation under one identity

Beyond the legacy carry-over [§The admitted legacy carry-over](#the-admitted-legacy-carry-over) admits, any conversion
that changes how a stored definition is represented while keeping its ids is admissible only when it demonstrably
preserves the authored meaning, every graph, node, and choice identity and the history that references them, the
original authoring evidence, and every supported consumer — the release, skew, upgrade, and downgrade contracts in force
included. Recognizing a command name, parser equality, or the conversion's own mapping tests does not discharge that
condition. This bounds a conversion and authorizes none: it licenses no rewrite of history, no widened normalizer, and
no change to what an argument means, and it calls for no equivalence engine, approval registry, or version tree. A
conversion that cannot establish preservation returns a concrete decision — a new mint, a refusal, an escalation —
rather than labeling semantic loss normalization.

## The admitted legacy carry-over

One existing carry-over is admitted under the same ids as a legacy category of its own: it is not held to the
preservation condition [§Representation under one identity](#representation-under-one-identity) sets, and it is not
claimed to meet it. A stored hub node naming no action, whose retired `run:` is a single recognized packaged command,
reads as the action that command named, or as `pass` when its `run:` is empty, with its graph, node, and choice ids and
its chunks' history unchanged. Its original definition text stays the authoring record and may still spell `run:` while
the executable view reads `action:`; that spelling difference under one identity is legal, and pins and recorded history
survive it. The carry-over is a recognized-command lookup, not a preservation proof: it reads only the commands it
recognizes, discards step metadata that has no home on an action, and is not certified lossless here. A `run:` it does
not recognize stays untranslated for comparison, and its stored command is retained beside the node for diagnosis and
human escalation, never executed — an old custom script does not run, and a packaged set naming only actions does not
show the carry-over to be unused. A new graph naming `run:` on a hub node is refused regardless. This section owns why
the carry-over is admitted under the same ids and that it proves no preservation;
[../../standards/hub-nodes/action-shape.md](../../standards/hub-nodes/action-shape.md) owns the escalation a node it
cannot carry takes.

## Comparison at reconciliation

Reconciling a packaged definition against the newest mint of its name reads the stored definition through the admitted
carry-over, then structurally compares the two parsed definitions: a difference is a new definition, minted as a new
graph, and no difference mints nothing. That is parse-and-translate equality, not a judgement of semantic equivalence,
and the translation applies to the stored side alone — nothing normalizes two arbitrary submitted documents toward each
other. Spelling a supported vocabulary the other way — the retired `run:` against the `action:` it names — need not
mint, and need not lift the brake [§Retiring every mint of a name](#retiring-every-mint-of-a-name) describes. A change
outside that admitted translation — to a prompt, a model tier, an argument, or declared artifact content — is a
definition change however it is spelled, and the translation never hides one.
[./declared-artifacts.md](./declared-artifacts.md) §Order owns what the comparison makes of a reordered `artifacts:`
map.

## Operational surfaces

`enabled` and `follow-latest` are the only mutable surfaces, set and re-set without touching the definition. They are
orthogonal: retiring and re-enabling says nothing about whether chunks follow.

- **`enabled`** gates resolution as a migration target: a retired graph is excluded from every name-based resolution and
  refuses an explicitly id-named target too. Retiring blocks only new targeting — the retired graph's own chunks
  continue undisturbed. Graphs are created enabled, and among enabled graphs sharing a name, resolution picks the
  newest.
- **`follow-latest`** states whether the graph's chunks drift to newer mints of its name. It is three-valued — yes, no,
  or unset. Unset is the default and defers to the fleet-wide setting; an explicit value overrides that setting for this
  graph's chunks.

A repeated retire, enable, or `follow-latest` set is legal and appends a duplicate fact, which the newest-fact-wins read
takes as no change.

## Retiring every mint of a name

Work ingested naming no graph lands on the newest enabled mint of the default name. With every mint of that name
retired, an ingest a person drives — a work-item create, a chunk ingest by token, or a garden proposal accept — is
refused rather than minting again over the brake. Reconciling a name whose every mint is retired mints a new, enabled
graph when the definition changed — a new definition is a new graph, so the brake lifts — and mints nothing when it is
unchanged, as [§Comparison at reconciliation](#comparison-at-reconciliation) judges it.
