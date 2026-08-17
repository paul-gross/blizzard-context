# Artifacts and delivery

What work produces and how it lands, what a graph declares for its workers to read, and delivery: the artifact scopes
and kinds, the chunk's artifact series, and the delivery model. Definitions, with the enforceable invariant written in
the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`). Part of the [domain model](./index.md).

## Artifact

Work the `artifact` verb group reads, and — at node scope only — writes, in one of two **scopes**:

- **Node scope.** A node-step's durable output, stored at the hub and fed into later nodes' work.
- **Graph scope.** Definition text a graph's top-level `artifacts:` map bakes into the mint once
  ([graphs.md](./graphs.md)); every chunk pinned to that mint reads back the identical, immutable content, and no worker
  ever produces it. A node reads it on demand through the same lease-scoped verbs, scope-qualified
  ([standards/worker-nodes.md](../standards/worker-nodes.md)) — never injected as prompt content
  ([execution.md](./execution.md)). What that read costs is `bzh:graph-scope-reads-local` in
  [architecture/system-shape.md](../architecture/system-shape.md).

Two kinds — commit pointer and asset — though a graph-scope entry is always the asset kind (`bzh:never-code` below):

| Kind           | Carries                                                                                                                                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| commit pointer | A repository, a branch name, and a commit hash — the branch is pushed to the forge **before** the artifact is submitted, so the pointer never dangles. A chunk touching five repos submits five pointers.                           |
| asset          | Text or a blob — a review's findings, a spike write-up. A worker node's asset is normally submitted by an explicit worker declaration, per the node's `produces:` list ([standards/worker-nodes.md](../standards/worker-nodes.md)). |

- **The hash is authoritative.** Branches move, so the hash pins the state that was actually verified; the branch name
  serves only to detect work committed ahead of it. There is deliberately no fencing at the branch ref: a zombie
  clobbering a branch can lose work, never land wrong work (`bzh:epoch-fencing` in [execution.md](./execution.md)).
- **Provenance is the scope discriminator.** A node-scope artifact is self-describing — it knows the chunk, the exact
  node, and the attempt that produced it. A graph-scope artifact carries none of that: its only provenance is the graph
  mint that baked it, identical for every chunk and every attempt pinned to that mint.

## Never code (`bzh:never-code`)

**Rule.** The hub stores **references** to work, never the work: a commit pointer is the closest any hub-side model gets
to code. Transcripts are the one deliberate exception, and only through the **transcript lane**: the hub retains
normalized turn slices of an agent session — never files, diffs, or patches — bounded by the lane's own per-record,
per-chunk, and per-runner-day caps, and readable only under the transcript-read permission. No *artifact* carries either
one.

**Why.** The forge is already the durable owner of code, so a hub holding only references stays small, safe to
centralize, and safe to expose to the board. Transcripts earn their exception because the thing an operator most needs
to see — what the agent actually did — exists nowhere else once a runner's machine rotates its session files; the caps
and the permission gate are what keep that exception from reintroducing the size and exposure the rule exists to
prevent.

**Scope.** A graph's `artifacts:` declaration is authored definition text, not work product — the same class of thing as
an inlined `prompt:`, prose the graph mint already stores. The rule is not engaged by baking it in, but the boundary
still binds: the *name* "artifact" invites treating a diff or a generated patch as declarable content, and that is
exactly the work-product this rule bars.

**Detect.** A design or schema persisting file contents, diffs, or patches at the hub; an artifact carrying code or a
transcript instead of a pointer to it; a work item's contents stored rather than read through; transcript content
reaching the hub **outside** the lane — uncapped, unpermissioned, or attached to something other than a segment; a
graph's `artifacts:` entry holding a diff, a patch, or other generated output rather than authored prose.

**Do.** Push the branch to the forge, then submit the repository, branch, and commit hash as the pointer artifact. Let
the transcript lane carry conversation, on its own caps.

**Don't.** Attach a diff or the worker's transcript as an asset artifact "for review convenience" — the review reads the
pushed branch, and the conversation is already on the lane. Declare `artifacts: {fix: ./fix.diff}` naming a diff as a
graph's baked-in content — the graph mint stores only what its author wrote, never work a chunk produced.

## The chunk's artifact series

A **node-scope** artifact accumulates as an **append-only, versioned series** per node and artifact name — append and
resolve-newest, exactly as the rules below state. A **graph-scope** artifact carries no series at all: the mint bakes
each declared entry once, immutable for that mint's whole life, superseded only by a fresh mint under a new `graph_id`.

- **Committed with the step, atomically.** A worker step's artifacts land in the same fenced write as the movement they
  belong to — its transition, its gate decision, or the migration recorded in place of a transition when that step takes
  the chunk off its graph — so a rejected step's artifacts never exist and can never drift from the movement record.
  There is no separate submission for them. A **hub** node is the deliberate exception the delivery below rests on: it
  records its own progress and marker artifacts as it goes, outside any movement, because a script that has landed one
  repo of five must leave a durable trace of that before any transition exists to carry it.
- **Append, never overwrite.** Re-running a node adds new entries under the new attempt; earlier entries remain as
  history.
- **Reads resolve to the newest entry.** Later nodes fetching a node-scope artifact by name get the latest attempt's
  version; the shadowed history stays available.
- **Series key on the node *name*.** After a migration or a re-published graph, a re-run of `build` keeps appending to
  the same series (`bzh:ids-exact-names-correlate` in [graphs.md](./graphs.md)); the exact producing node is on each
  artifact's provenance.

## Delivery

Delivery is not built-in engine machinery — it is graph-authored content, a generic hub command node (`executor: hub` +
`run:`, [graphs.md](./graphs.md) §Node) like any other, whose declared script IS the delivery policy. Several policies
ship, and which one a chunk gets is a fact about the graph it travels rather than about the engine: the shipped lanes'
`deliver` nodes either fast-forward each repo's base branch onto the chunk's own commit, or open a pull request per repo
and watch each to a clean merge. Even chunk-atomicity — checking every repo merges before pushing any — is one script's
construction, not a property of delivery: the fast-forward policy advances repos one at a time and accepts a partial
land, and the per-repo reconciliation below is what recovers it.

- **Fleet-wide serialization is a generic fact, not a delivery-only lane.** One fleet-wide execution slot admits one
  chunk's hub node — any hub node, not delivery specifically — at a time; a chunk finding it held elsewhere simply tries
  again on a later tick.
- **Per-repo landing with reconciliation is the script's own property, read by one shared convention.** A shipped
  delivery script lands a multi-repo chunk serially per repo, recording its own `merged/<repo>` marker immediately after
  each push; a re-run — after a crash, or a kicked-back redelivery — skips every repo whose marker is already durable.
  The engine imposes no per-repo landing *shape* of its own — a differently-authored script could land however it
  chooses — but it does read the `merged/<repo>` marker convention to tell a fully-landed continuation apart from a
  genuinely incomplete delivery ([standards/hub-nodes.md](../standards/hub-nodes.md)).
- **Conflict is a judged, authored outcome, never an engine special case.** A dirty repo is one of the script's own
  outcome choices, routed like any other node's choice to whatever edge the graph authors — ordinarily back into
  `build`, carrying the retained partial lands for the next attempt's reconciliation.
- **"PR mode" is an authored alternative policy, not a built-in mode.** Opening a pull request per repo and waiting for
  it to go cleanly mergeable, instead of advancing the base branch directly, is one shipped script — the plan-gated
  lane's `deliver` node — among however many an operator wants, adopted by minting a graph naming that node in place of
  another's, never by an engine switch.
- The holding runner **keeps the chunk's environments throughout delivery**, until the outcome is known.

## Landing is not necessarily terminal

A hub node's script authors its outcome choices exactly like a worker node's judgement ([graphs.md](./graphs.md)
§Judgement and choices). A `deliver` node's `landed` choice may route straight to the graph's reserved terminal — but
that routing is authored, not fixed, and every shipped lane in fact routes it into a further **runner** node, run in the
holding runner's still-held environment after every repo has merged, before that node's own choice finally reaches the
terminal. Landing is therefore informational, not itself a terminal condition — only the graph's reserved terminal
(`done`, [work.md](./work.md) §Statuses) is.

## See also

- [./work.md](./work.md) — the transition an artifact commits with, and the `done` status delivery derives.
- [../standards/hub-nodes.md](../standards/hub-nodes.md) — the technical authoring contract a hub command node like
  `deliver` is held to.
- [../standards/worker-nodes.md](../standards/worker-nodes.md) — the technical authoring contract a worker node's
  declared asset is held to.
