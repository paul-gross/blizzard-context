# Pointing a worker at a graph- or system-scoped declaration

What a prompt owes when it sends the worker to read a graph-scoped or system-scoped artifact declaration.

Parent: [../worker-nodes.md](../worker-nodes.md).

## A pointer names its fallback (`bzh:graph-artifact-pointer-fallback`)

**Rule.** A prompt that points a worker at a graph-scoped declaration or a system-scoped one —
`blizzard runner artifact get <name> --scope graph` or `--scope system` — must also tell the worker what to do when that
read does not answer, and the instruction must carry the node-step to completion without the declaration's text. The
pointer is therefore always additive: the declaration is only the fuller source of what the prompt itself already
states.

**Why.** A graph-scope read can miss because a pinned mint's declarations reach the runner's own store at spawn: a lease
already in flight when a runner restarts onto a build that introduces a declaration holds a pin with nothing in it. That
accepted window is bounded by `bzh:graph-scope-reads-local`
([../../architecture/system-shape/artifact-scopes.md](../../architecture/system-shape/artifact-scopes.md)) and by the
runner's graph-artifact mirror entry in
[../../architecture/crash-correctness/runner.md](../../architecture/crash-correctness/runner.md). A system-scope read
misses for an unrelated reason: it crosses the hub on every call, with no local pin to fall back on
(`bzh:system-scope-reads-live`), so a hub outage fails it outright rather than answering from anything the runner
mirrors.

**Scope.** Binds every prompt naming a graph-scope read or a system-scope read, on a worker node or its judgement prompt
alike — two different failure modes (an empty local pin; a hub the call cannot reach) owing the same fallback
obligation. It says nothing about node-scope reads: a node-scope miss means an upstream node produced nothing — a real
condition of the chunk rather than a window in the runner's own state or a hub outage.

**Detect.** A fallback conditioned only on an empty result. Graph scope's two verbs already fail differently —
`artifact list --scope graph` answers empty, while `artifact get <name> --scope graph` exits non-zero with a `404` named
on stderr — so an empty-only condition leaves the `get` case, the one a pointer at a named declaration actually takes,
uncovered. System scope adds a third shape neither of those is: on a hub outage, `artifact list --scope system` and
`artifact get --scope system` both fail non-empty with the proxied request's own failure — neither an empty answer nor a
named `404` — so a fallback that treats "not empty and not a 404" as success will not catch it either.

**Do.** *"The full docket this restates is retrievable directly:
`blizzard runner artifact get docket --scope graph --content`. If that read fails or comes back empty, proceed on the
restatement above."*

**Don't.** *"The rules for folding findings are in the `docket` graph artifact — read it before you fold."*
