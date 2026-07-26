# Artifacts and delivery

What work produces and how it lands: the artifact kinds, the chunk's artifact series, and delivery.
Definitions, with the enforceable invariant written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).
Part of the [domain model](./index.md).

## Artifact

A node-step's durable output, stored at the hub and fed into later nodes' work.
Two kinds:

| Kind | Carries |
|------|---------|
| commit pointer | A repository, a branch name, and a commit hash — the branch is pushed to the forge **before** the artifact is submitted, so the pointer never dangles. A chunk touching five repos submits five pointers. |
| asset | Text or a blob — a review's findings, a spike write-up. A worker node's asset is normally submitted by an explicit worker declaration, per the node's `produces:` list ([standards/worker-nodes.md](../standards/worker-nodes.md)). |

- **The hash is authoritative.** Branches move, so the hash pins the state that was actually verified; the branch name serves only to detect work committed ahead of it. There is deliberately no fencing at the branch ref: a zombie clobbering a branch can lose work, never land wrong work (`bzh:epoch-fencing` in [execution.md](./execution.md)).
- **Self-describing provenance.** An artifact knows the chunk, the exact node, and the attempt that produced it.

## Never code, never transcripts (`bzh:never-code`)

**Rule.** The hub stores **references** to work, never the work: a commit pointer is the closest any hub-side model gets to code, and no model anywhere stores agent-session transcripts.

**Why.** The forge is already the durable owner of code and the runner's machine of its sessions; a hub that holds only references stays small, safe to centralize, and safe to expose to the board.

**Detect.** A design or schema persisting file contents, diffs, patches, or session transcripts at the hub; an artifact carrying code instead of a pointer to it; a work item's contents stored rather than read through.

**Do.** Push the branch to the forge, then submit the repository, branch, and commit hash as the pointer artifact.

**Don't.** Attach a diff or the worker's transcript as an asset artifact "for review convenience" — the review reads the pushed branch instead.

## The chunk's artifact series

A chunk's artifacts accumulate as an **append-only, versioned series** per node and artifact name.

- **Committed with the step, atomically.** Artifacts land in the same fenced write as the step's transition — or its gate decision — so a rejected step's artifacts never exist and can never drift from the movement record. There is no separate artifact submission.
- **Append, never overwrite.** Re-running a node adds new entries under the new attempt; earlier entries remain as history.
- **Reads resolve to the newest entry.** Later nodes fetching an artifact by name get the latest attempt's version; the shadowed history stays available.
- **Series key on the node *name*.** After a migration or a re-published graph, a re-run of `build` keeps appending to the same series (`bzh:ids-exact-names-correlate` in [graphs.md](./graphs.md)); the exact producing node is on each artifact's provenance.

## Delivery

Delivery is not built-in engine machinery — it is graph-authored content, a generic hub command node (`executor: hub` + `run:`, [graphs.md](./graphs.md) §Node) like any other, whose declared script IS the delivery policy. The shipped `deliver` node's script fetches every repo the chunk submitted a commit-pointer artifact for, verifies all of them merge cleanly, then pushes all of them — a chunk-atomic land, by the script's own construction.

- **Fleet-wide serialization is a generic fact, not a delivery-only lane.** One fact (`hub_exec_slot`) admits one chunk's hub node — any hub node, not delivery specifically — at a time; a chunk finding it held elsewhere simply tries again on a later tick.
- **Per-repo landing with reconciliation is the script's own property, read by one shared convention.** The shipped delivery script lands a multi-repo chunk serially per repo, recording its own `merged/<repo>` marker immediately after each push; a re-run — after a crash, or a kicked-back redelivery — skips every repo whose marker is already durable. The engine imposes no per-repo landing *shape* of its own — a differently-authored script could land however it chooses — but it does read the `merged/<repo>` marker convention to tell a fully-landed continuation apart from a genuinely incomplete delivery ([standards/hub-nodes.md](../standards/hub-nodes.md)).
- **Conflict is a judged, authored outcome, never an engine special case.** A dirty repo is one of the script's own outcome choices, routed like any other node's choice to whatever edge the graph authors — ordinarily back into `build`, carrying the retained partial lands for the next attempt's reconciliation.
- **"PR mode" is an authored alternative policy, not a built-in mode.** Opening a pull request per repo and waiting for it to go cleanly mergeable, instead of merging directly, is one shipped example script (the `delivery-pr-ci` graph's `deliver` node) among however many an operator wants — adopted by minting a graph naming that node in place of the default's, never by an engine switch.
- The holding runner **keeps the chunk's environments throughout delivery**, until the outcome is known.

## Landing is not necessarily terminal

A hub node's script authors its outcome choices exactly like a worker node's judgement ([graphs.md](./graphs.md) §Judgement and choices). The shipped `deliver` node's `landed` choice ordinarily routes straight to the graph's reserved terminal — but that routing is authored, not fixed: a graph may instead route `landed` into a further **runner** node, run in the holding runner's still-held environment after every repo has merged, before that node's own choice finally reaches the terminal. Landing is therefore informational, not itself a terminal condition — only the graph's reserved terminal (`done`, [work.md](./work.md) §Statuses) is.

## See also

- [./work.md](./work.md) — the transition an artifact commits with, and the `done` status delivery derives.
- [../standards/hub-nodes.md](../standards/hub-nodes.md) — the technical authoring schema for a hub command node like `deliver`: the `run:` step shape, the injected env-var contract, the outcome protocol, and the per-step idempotence rule its script is held to.
- [../standards/worker-nodes.md](../standards/worker-nodes.md) — the technical authoring contract for a worker node's asset: the prompt's declaration instruction, the judgement-assessment fallback, and the `produces_mode` enforcement backstop.
