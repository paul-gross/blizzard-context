# Graph identity

One graph's identity and the two operational surfaces beside it. The definition itself — its nodes, edges, sessions, and
artifacts — is routed from [../graphs.md](../graphs.md).

One identity, two parts:

- **An immutable definition** — the nodes, edges, prompts, and judgements. Every edit creates a new graph; an existing
  definition never changes, so anything pinned to it can trust it forever.
- **Mutable operational metadata beside it** — `enabled` and `follow-latest`, the graph's only mutable surfaces. Both
  are set, and re-set, without touching the definition.

There is **no graph family or version tree**: graphs are standalone, and any graph may migrate its chunks to any graph
so long as the node mapping gets them over. What looks like "versions of a workflow" is emergent, not modeled: nothing
on a graph links it to a successor — a migration is what moves a chunk onto another graph that happens to share its name
(which one, when several do, is the `enabled` bullet below) ([work/migration.md](../work/migration.md) owns how and when
a chunk migrates).

- **`follow-latest` states whether this graph's chunks drift to newer mints of its name.** Three-valued: it may say yes,
  say no, or **say nothing** — the last being the default for every graph, and meaning it defers to the fleet-wide
  setting. Saying either of the first two overrides that setting for the chunks pinned to this graph. It is orthogonal
  to `enabled`: a graph can be retired and re-enabled any number of times without that saying anything about whether its
  chunks follow. [work/migration.md](../work/migration.md) owns what the policy actually does to a chunk.
- **`enabled` gates being resolved as a migration target.** A retired graph is excluded from every name-based resolution
  (the default pin at mint, an authored choice's `graph:<name>` target, a migration's target-by-name lookup) and refuses
  an explicit id-named target too — its own chunks continue undisturbed; only new targeting is blocked. Among the
  enabled graphs sharing a name, resolution picks the **newest**. Graphs are created enabled.
