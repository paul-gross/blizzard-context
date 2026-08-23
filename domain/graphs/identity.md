# Graph identity

A graph pairs an immutable definition with mutable operational metadata; every edit creates a new graph rather than
changing an existing one, so anything pinned to one can trust it forever. Definitional — a taxonomy of a graph's
identity and its mutable operational surfaces (`canon:rule-shape` §File kinds); the definition's content is routed from
[../graphs.md](../graphs.md). Part of the [domain model](../index.md).

## Standalone graphs

There is no graph family or version tree: graphs are standalone, and nothing links a graph to a successor. Any graph may
migrate its chunks to any graph so long as the node mapping gets them over — apparent workflow versions are just
migrations onto a graph sharing the name, emergent rather than modeled. [../work/migration.md](../work/migration.md)
owns how and when a chunk migrates and what `follow-latest` actually does.

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
