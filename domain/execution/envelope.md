# Envelope

What a worker session is primed with, and how a change reaches it. Spoke of the [execution hub](../execution.md).

A worker session never discovers its work: the runner primes it with the node envelope the hub assembles for the chunk's
current node.

## What it carries

- The node's prompt and configuration: base prompt plus the taken edge's arrival context
  ([../graphs/nodes.md](../graphs/nodes.md)).
- The chunk's relevant artifacts: earlier steps' outputs, newest-first from the artifact series
  ([../artifacts.md](../artifacts.md)).
- Graph-mint declarations as fetchable, not inlined content: a node asks for one by name
  ([../artifacts.md#artifact](../artifacts.md#artifact)).
- For a node declaring `produces:`, a generated required-artifacts table: each entry's kind and the fleet-protocol verb
  declaring it ([../../standards/worker-nodes/declarations.md](../../standards/worker-nodes/declarations.md)).
- The runner's machine-local context: which environments the chunk holds and where they live on that machine.

## Two phases, one session

Prompting is two-phase: the envelope instructs the work; when the worker declares done, the judgement prompt is
delivered into the same session for the verdict ([../graphs/edges.md](../graphs/edges.md)).

## How change arrives

Change reaches a worker through the envelope: a migration appears as the next envelope's new graph and node
([../work/migration.md](../work/migration.md)); an answered ask resumes the session with the answer delivered into it
([../humans/asks.md](../humans/asks.md)).
