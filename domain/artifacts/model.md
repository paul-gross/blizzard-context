# Artifact

What an artifact is — its kinds, its scopes, and what a graph declares beside its nodes for workers to read. Spoke of
the [artifacts hub](../artifacts.md).

Work the `artifact` verb group reads, and — at node scope only — writes, in one of two **scopes**:

- **Node scope.** A node-step's durable output, stored at the hub and fed into later nodes' work.
- **Graph scope.** Definition text a graph's top-level `artifacts:` map bakes into the mint once
  ([graphs/declared-artifacts.md](../graphs/declared-artifacts.md)); every chunk pinned to that mint reads back the
  identical, immutable content, and no worker ever produces it. A node reads it on demand through the same lease-scoped
  verbs, scope-qualified ([standards/worker-nodes/declarations.md](../../standards/worker-nodes/declarations.md)) —
  never injected as prompt content ([execution/envelope.md](../execution/envelope.md)). What that read costs is
  `bzh:graph-scope-reads-local` in [architecture/system-shape/graphs.md](../../architecture/system-shape/graphs.md).

Two kinds — commit pointer and asset — though a graph-scope entry is always the asset kind (`bzh:never-code` below):

| Kind           | Carries                                                                                                                                                                                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| commit pointer | A repository, a branch name, and a commit hash — the branch is pushed to the forge **before** the artifact is submitted, so the pointer never dangles. A chunk touching five repos submits five pointers.                                                        |
| asset          | Text or a blob — a review's findings, a spike write-up. A worker node's asset is normally submitted by an explicit worker declaration, per the node's `produces:` list ([standards/worker-nodes/declarations.md](../../standards/worker-nodes/declarations.md)). |

- **The hash is authoritative.** Branches move, so the hash pins the state that was actually verified; the branch name
  serves only to detect work committed ahead of it. There is deliberately no fencing at the branch ref: a zombie
  clobbering a branch can lose work, never land wrong work (`bzh:epoch-fencing` in
  [execution/fencing.md](../execution/fencing.md)).
- **Provenance is the scope discriminator.** A node-scope artifact is self-describing — it knows the chunk, the exact
  node, and the attempt that produced it. A graph-scope artifact carries none of that: its only provenance is the graph
  mint that baked it, identical for every chunk and every attempt pinned to that mint.
