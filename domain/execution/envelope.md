# What a worker receives

A worker session never discovers its work — the runner primes it with the **node envelope**, assembled by the hub for
the chunk's current node:

- **The node's prompt and configuration** — the base prompt plus the taken edge's arrival context
  ([graphs/nodes.md](../graphs/nodes.md)), plus, when the node declares `produces:`, a procedurally-generated
  required-artifacts table naming each entry's kind and the fleet-protocol verb that declares it
  ([standards/worker-nodes/declarations.md](../../standards/worker-nodes/declarations.md)))
- **The chunk's relevant artifacts** — earlier steps' outputs, resolved newest-first from the artifact series
  ([artifacts.md](../artifacts.md)). Its graph mint's own declarations travel too, but as something to fetch rather than
  content to read here — a node that wants one asks for it by name ([artifacts.md](../artifacts.md) §Artifact).
- **The runner's machine-local context** — which environments the chunk holds and where they live on this machine; the
  hub contributes none of this.

Prompting is **two-phase**: the envelope's content instructs the work, and when the worker declares done, the judgement
prompt is delivered into the same session to elicit the verdict ([graphs/edges.md](../graphs/edges.md)). The envelope is
also how change reaches a worker rather than being inferred: a migration shows up as the next envelope's new graph and
node ([work/migration.md](../work/migration.md)), and an answered ask re-enters as the session resuming with the answer
delivered into it ([humans/asks.md](../humans/asks.md)).
