# Envelope

What a worker session is primed with, and how a change reaches it. Spoke of the [execution hub](../execution.md).

A worker session never discovers its work: the runner primes it with the node envelope the hub assembles for the chunk's
current node. An ended chunk — `stopped`, or `done` whether by a transition or by an operator — primes no session:
reading its envelope is refused.

## What it carries

- The node's prompt and configuration: base prompt plus the taken edge's arrival context
  ([../graphs/nodes.md](../graphs/nodes.md)).
- The chunk's relevant artifacts: earlier steps' outputs, newest-first from the artifact series
  ([../artifacts/series.md](../artifacts/series.md)).
- Graph-mint declarations as fetchable, not inlined content: a node asks for one by name
  ([../artifacts/model.md](../artifacts/model.md)).
- For a node declaring `produces:`, a generated required-artifacts table: each entry's kind and the fleet-protocol verb
  declaring it ([../../standards/worker-nodes/declarations.md](../../standards/worker-nodes/declarations.md)).
- The runner's machine-local context: which environments the chunk holds and where they live on that machine.

## Standing instructions

Ahead of the envelope, a session is primed with two standing instructions that hold for every step: blizzard's own
worker instructions, and the standing prompt of the workspace the chunk was claimed through ([./hosts.md](./hosts.md)
§Workspaces). A chunk claimed through no workspace is primed with the first alone.

A workspace states its standing prompt one way at a time — as text, as a file, or as a packaged sample — so stating it
one way replaces whichever stood before. A workspace stating none has no standing prompt, and clearing the prompt
returns it to exactly that: nothing stands behind a workspace's prompt to fall back to. An edit needs no restart, and
reaches every session started after the host takes it up.

## Two phases, one session

Prompting is two-phase: the envelope instructs the work; when the worker declares done, the judgement prompt is
delivered into the same session for the verdict ([../graphs/edges.md](../graphs/edges.md)).

## How change arrives

Change reaches a worker through the envelope: a migration appears as the next envelope's new graph and node
([../work/migration.md](../work/migration.md)); an answered ask resumes the session with the answer delivered into it
([../humans/asks.md](../humans/asks.md)).

Standing instructions reach a reused session by comparison with what that session was last sent, each of the two judged
on its own. A new session is sent both in full. A node entry that reuses a session
([../graphs/nodes.md](../graphs/nodes.md), `session`) is told one of three things about each:

- Unchanged: acknowledged as still in force, its text not sent again.
- Changed: sent in full under a notice that the instructions have been updated and the text that follows supersedes what
  the session was handed earlier.
- Withdrawn — a workspace's standing prompt that is no longer there: announced as withdrawn and no longer in effect,
  since silence would read as unchanged to a worker still holding it.

A difference in surrounding whitespace alone is no change.
