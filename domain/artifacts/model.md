# Artifact

An artifact is work the `artifact` verb group reads and — at node scope only — writes. A spoke of the
[artifacts hub](../artifacts.md).

## Kinds

| Kind               | What it carries                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| **Commit pointer** | A repository, a branch name, and a commit hash.                                                 |
| **Asset**          | Text or a blob — a graph's baked-in definition text, or a delivery marker like `merged/<repo>`. |

A chunk submits one commit pointer per repository it touches, and the branch behind a pointer is pushed to the forge
before the artifact is submitted, so the pointer never dangles. The hash is authoritative: branches move, so the hash
pins the state actually verified, and the branch name serves only to detect work committed ahead of it. There is
deliberately no fencing at the branch ref — a zombie clobbering a branch can lose work, never land wrong work
(`bzh:epoch-fencing`, [fencing](../execution/fencing.md)).

A worker node's asset is normally submitted by explicit worker declaration per the node's `produces:` list
([declarations](../../standards/worker-nodes/declarations.md)).

## Scopes

**Node scope** — a node-step's durable output, stored at the hub and fed into later nodes' work.

**Graph scope** — definition text a graph's top-level `artifacts:` map bakes into the mint once
([declared artifacts](../graphs/declared-artifacts.md)); every chunk pinned to that mint reads back the identical,
immutable content, and no worker ever produces it. A graph-scope entry is always the asset kind (`bzh:never-code`, owned
by [never-code.md](./never-code.md)). A node reads graph-scope content on demand through the same lease-scoped verbs,
scope-qualified ([declarations](../../standards/worker-nodes/declarations.md)) — never injected as prompt content
([envelope](../execution/envelope.md)). What a graph-scope read costs is owned by `bzh:graph-scope-reads-local` in
[artifact-scopes](../../architecture/system-shape/artifact-scopes.md).

**System scope** — a global, slash-bearing name that is not per-graph: blizzard itself publishes the content, once, in a
namespace every graph and every chunk reads the same copy of. It is read-only the same way graph scope is — no worker
ever produces a system artifact, and `create`, `commit`, and `staged` all refuse it — but unlike graph scope, every read
is a live hub call, never answered from anything the runner mirrors locally. What that liveness costs, and why it binds
system scope and not graph scope, is owned by `bzh:system-scope-reads-live` in
[artifact-scopes](../../architecture/system-shape/artifact-scopes.md).

Provenance discriminates the scopes: a node-scope artifact knows the chunk, the exact node, and the attempt that
produced it; a graph-scope artifact's only provenance is the mint that baked it; and a system-scope artifact's only
provenance is blizzard's own release, not any chunk or any mint.
