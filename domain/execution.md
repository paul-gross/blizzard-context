# Execution — runners, tenure, and fencing

Who runs a chunk and how exactly-once holds: the hub/runner responsibility split, acquisition and routes, leases and epochs, and what failure does to each.
Definitions, with the enforceable invariant written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).
Part of the [domain model](./index.md).

## The responsibility split

- **The hub** orchestrates the fleet's work: it owns chunks, graphs, artifacts, and the registry, and it grants work. It never holds code, and holds conversation only as the transcript lane's capped segments (`bzh:never-code` in [artifacts.md](./artifacts.md)); it never reaches into a runner's machine.
- **A runner** executes work on its own machine, bound to one prepared workspace: it claims chunks, acquires environments, drives workers through node-steps, and reports the facts. All contact is runner-initiated — the hub pushes nothing into a dev box.
- **Operator controls are declarative state, not commands.** Pausing appends a fact; there is no directive queue. **Runner-level** pause has **two independent brakes**, because two parties stop a runner for different reasons: the **fleet's**, set at the hub and read by the runner on its own contact, and the runner's **own**, set on its machine — so it holds with the hub unreachable — and reported up to the hub, which never sets it. The two are **not** equally hard: the fleet's stops new claims and nothing else, so a chunk already in flight runs to completion under it; the runner's own additionally starts no process at all — no next attempt, no judgement, no resume of a dormant session — so an in-flight chunk halts at its next step boundary instead, and neither a stalled worker's reap nor an exhausted attempt's escalation fires until it lifts. Effective paused is their OR, each cleared only where it was set. **Per-chunk** pause is a third, independent lever targeting one chunk rather than the whole runner, and it does kill that chunk's in-flight worker while keeping its claim — see [work.md](./work.md) §Statuses (`paused`) for what survives and how resume recovers it.

A runner's registry entry derives everything observable: liveness derives from its most recent contact, and each brake from the newest fact in its own stream — never stored flags (`bzh:facts-not-status` in [../architecture/system-shape.md](../architecture/system-shape.md)).

## Acquisition and the route

**Acquisition** is the hub granting a ready chunk to exactly one runner — the one point of genuine cross-runner contention, and where fleet exactly-once is upheld.
The claim is **claim-by-route**: the runner peeks the hub-ordered queue, acquires the environments, and posts the complete route; the hub accepts exactly one claim per chunk.

The **route** is the locator fact that makes every held chunk findable: chunk → runner → workspace → environment.
The environment identifier is opaque to the hub — it knows *which* environment, never what an environment is.

- **Runner stickiness.** Consecutive node-steps of a chunk run on the holding runner — no re-queue between nodes.
- **A route is released** by the write that gives the chunk's tenure back: **detach** — a superadmin's forcible release — along with the **hub's requeue** of an escalated chunk (§Failure and recovery distinguishes it from the runner's own) and a **migration that re-queues onto another graph**; after each the chunk re-derives `ready` and the old runner is fenced out by the next claim. **Stop** releases it too, but terminally — there is no next claim to fence. So does a **hub** node landing the chunk's terminal.
- **A terminal chunk may still hold a live route, and holding one grants nothing.** A terminal transition authored by a **runner** node — the shape [work.md](./work.md) §Statuses (`done`) allows, where a graph routes further runner work after landing — releases no route, so a `done` chunk can go on carrying the route of the runner that finished it. That is untidy, not unsafe: the claim path refuses a terminal chunk outright, so a retained route confers no tenure on anyone. What it does mean is that **route liveness is not a proxy for "being worked"** — a consumer folding routes into live occupancy must key on status, which is why the chunk summary reports a terminal chunk as unrouted for the fleet registry's claim lines and slot bar, while the chunk detail keeps the raw route fact for the "where was this worked" read.
- **Pause is detach's deliberate counterpart: it keeps the route.** A per-chunk pause kills the chunk's live worker but leaves the lease, route, epoch, environments, and retry budget untouched, so resume respawns the session in place under the unchanged lease/epoch/session id ([work.md](./work.md) §Statuses); detach is the lever that gives the claim away, pause is the one that holds it exactly where it is.
- **The hub, as claim arbiter, refuses a registry-paused runner's claim outright.** A claim from a runner the registry marks paused is denied before the claim race is even run — a distinct `403` denial, not the `409` a claim loses to another claimant on an exactly-once race. The hub enforces this itself, independent of whether the runner has already mirrored the pause flag on its own next pull.

## Lease and epoch

A **lease** is one node-step attempt.
At a runner node that means one agent session, renewed by heartbeat and kept dormant while the chunk parks on a human ([humans.md](./humans.md)); a **hub**-executed node has no session at all, and the hub mints that node's lease itself, in the same write as the exit it records.
It is the executing party's own single-writer bookkeeping — a runner has no rival on its own machine, the hub none over its own nodes — in deliberate contrast to acquisition, the contended grant at the hub.
Distinct concepts: acquisition decides *who holds the chunk*; the lease records *one attempt at one node*.

Each lease mints a fresh **epoch** — a counter that only rises across a chunk's attempts — and the epoch is the fence every state-advancing write is checked against.

The worker's **heartbeat** is a side effect of its tool use — no agent cooperation required — and is what keeps its lease alive.

## Stale attempts are fenced out (`bzh:epoch-fencing`)

**Rule.** Every state-advancing write for a chunk — a transition, a decision, its artifacts — carries the epoch of the lease that produced it, and a write below the chunk's newest epoch is rejected, never recorded; a terminal fact (stopped, delivered) rejects every later state-advancing write regardless of epoch.

**Why.** A worker presumed dead can wake and write after its successor started; fencing makes the successor authoritative — the zombie's late writes bounce — so a zombie can lose work but never land wrong work, without requiring anyone to kill processes reliably.

**Detect.** A state-advancing write path with no epoch check; a reap or reassignment design that assumes the old holder is really dead instead of fencing it out, or a migration recorded at the submitting attempt's own epoch that relies on it rather than on next-claim fencing; the epoch check skipped once a chunk is terminal.

**Do.** Every fresh claim of a re-queued chunk — a reassignment, or a route-released re-queue such as a detach or a migration ([work.md](./work.md) §Migration) — mints new leases above the **hub-supplied** epoch floor: the chunk's newest epoch as the hub knows it, carried on the claim, not whatever local history the claiming runner happens to hold. A runner that never drove the chunk (no local floor of its own) still mints strictly above every prior attempt, so the old holder's in-flight submission is rejected on arrival.

**Don't.** Accept a transition because the submitting runner still holds the route — route tenure is not attempt fencing.

## What a worker receives

A worker session never discovers its work — the runner primes it with the **node envelope**, assembled by the hub for the chunk's current node:

- **The node's prompt and configuration** — the base prompt plus the taken edge's arrival context ([graphs.md](./graphs.md)), plus, when the node declares `produces:`, a procedurally-generated required-artifacts table naming each entry's kind and the fleet-protocol verb that declares it ([standards/worker-nodes.md](../standards/worker-nodes.md)).
- **The chunk's relevant artifacts** — earlier steps' outputs, resolved newest-first from the artifact series ([artifacts.md](./artifacts.md)).
- **The runner's machine-local context** — which environments the chunk holds and where they live on this machine; the hub contributes none of this.

Prompting is **two-phase**: the envelope's content instructs the work, and when the worker declares done, the judgement prompt is delivered into the same session to elicit the verdict ([graphs.md](./graphs.md) §Judgement and choices).
The envelope is also how change reaches a worker rather than being inferred: a migration shows up as the next envelope's new graph and node ([work.md](./work.md) §Migration), and an answered ask re-enters as the session resuming with the answer delivered into it ([humans.md](./humans.md)).

## Failure and recovery

- **Reap** expires a lease with no live work behind it: one minted but never spawned, and one whose worker is still alive but has stopped beating. A worker that has **exited** is never reaped — its exit is its done declaration, and judging it belongs to the step that advances the chunk — **even an `error_during_execution` exit** (wontfix, blizzard#284): the runner never observes a worker's exit status at all, so there is no code to branch on instead — the backstop is exit-status-independent, a node's declared `produces:` plus the delivery-time empty-delivery refusal catching what an errored exit failed to produce. Reap ends the **attempt** — retry, or escalate on exhaustion ([humans.md](./humans.md)) — never by itself the chunk's tenure or its environments.
- **Requeue** is two operations sharing one name. The **hub's** supersedes the escalation *and* releases the route, returning the chunk to the queue for whoever claims it next. The **holding runner's** — the hand-back after a takeover ([humans.md](./humans.md) §Takeover) — keeps route, environments and tenure, and simply re-attempts the current node in place against the retry budget it already had.
- **Reassignment** moves a held chunk to another runner — the supported exception to stickiness: the new runner rebuilds the environment from the chunk's commit artifacts, mints leases above the hub-supplied epoch floor, and may adopt unsubmitted in-progress work it finds ahead of the last submitted artifact commit.
- **Detach** forcibly releases a chunk from its runner: the route is released, the chunk re-derives ready, and the next claim's epoch floor fences the old runner.

## See also

- [./work.md](./work.md) — the transitions these leases produce and the statuses tenure derives.
- [../architecture/crash-correctness.md](../architecture/crash-correctness.md) — how the daemons are built and tested so these semantics survive `kill -9`.
