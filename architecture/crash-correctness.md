# Crash correctness

MVP acceptance criterion 4 promises that `kill -9` at every step boundary is **a tested operation, not a hope**. That
promise imposes four requirements on daemon code — built in from the first commit, because each is cheap on day one and
expensive to retrofit. Crash correctness is an orthogonal dimension, not a fifth test tier
([../verification/blizzard.md](../verification/blizzard.md)): the requirements below are *architecture*; the kill-9
sweep that exercises them is a verification method (`blizzard:crash-sweep`) in the matrix. Each rule follows the slot
skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A steppable loop (`bzh:steppable-loop`)

**Rule.** The daemon loop's phases — the runner's REAP, PULL, FILL, ADVANCE, and the hub's coordinator loop — are
individually callable step functions, each a pure function of (store, clock, seam clients); the tick timer is merely one
driver of them.

**Why.** Tests drive the same step functions directly, one at a time, stopping exactly at a boundary — which is how
boundary-order and recovery logic get cheap in-process coverage and how the sweep arms a precise crash point. A loop
welded to its timer can only be tested by waiting on wall-clock ticks and cannot be stopped mid-step.

**Detect.** Loop phases reachable only through the tick timer or a `while True`; a step that reads the clock or a seam
from a module global rather than its parameters.

**Do.** `def fill(store, clock, seams) -> None` callable standalone; the tick driver calls `reap`, `pull`, `fill`,
`advance` in turn.

**Don't.** A single `tick()` that inlines all four phases with no separately callable boundary — no test can stop
between FILL and ADVANCE.

## An injected clock (`bzh:injected-clock`)

**Rule.** All time flows through a clock abstraction wired at the composition root (`bzh:dependency-injection`); no
direct `time.time()` / `datetime.now()` appears in loop, store, or domain code — **including SQLAlchemy column
defaults**.

**Why.** An injected clock lets tests advance time virtually, so lease TTLs, reap staleness thresholds, and an
"overnight" wait pass in milliseconds and deterministically; a direct `datetime.now()` anywhere — especially a column
default — reintroduces wall-clock non-determinism the sweep cannot control.

**Detect.** `datetime.now()`, `datetime.utcnow()`, `time.time()`, or `func.now()` / `server_default=func.now()` in loop,
store, domain, or model code; a timestamp written from anything but the injected clock.

**Do.** The clock is injected; timestamps come from `clock.now()`, and column values are set by the writing code from
that clock — not by a database default.

**Don't.** `created_at = Column(DateTime, default=datetime.utcnow)` — the store now stamps wall-clock time the virtual
clock can't move.

## A crash-point registry (`bzh:crash-point-registry`)

**Rule.** The dangerous windows carry stable names in a code-owned, **enumerable** registry — e.g.
`fill.after-env-acquire.before-claim`, `advance.after-buffer.before-flush`, `hubnode.after-step.before-marker`,
`reap.after-kill.before-expire`; under test scaffolding a daemon subprocess SIGKILLs itself on reaching the armed point,
selected via an environment variable and fenced so it can never fire outside a test-marked environment. The segment
before the point's first `.` is the **boundary family** the sweep partitions the registry on — it resolves which
scenario (the generic `build → deliver` sweep, or a dedicated scenario such as `resume.`, `abandon.`, `pause.`,
`hubnode.`) is the one that arms and reaches that point — so name a point for the boundary its reaching scenario opens,
never for the step whose source happens to call `.reached()`.

**Why.** An enumerable registry is what the sweep iterates — one run per armed point — and it doubles as the
authoritative list of windows the design claims are safe, so a newly-introduced dangerous window is a registry entry,
not a silent gap. The family prefix is what routes a point to the scenario that actually reaches its window, so naming
it for the wrong family leaves the registry entry with no real coverage behind it.

**Detect.** A crash-recovery claim about a window with no corresponding registry entry; a self-kill hook not gated
behind the test-environment fence; crash points hard-coded in the test rather than enumerated from the registry; a new
point prefixed with a family that already has coverage from an unrelated sibling point, when the point's own window only
opens under a dedicated scenario — the family-coverage check passes on the sibling's strength while the new point's
window goes unswept.

**Do.** Add the window's stable name to the registry, prefixed for the scenario that reaches it —
`pause.after-kill.before-park`, not `pull.after-pause-kill.before-park`, even though the call site sits inside the PULL
step's code; the sweep enumerates the registry and arms each in turn; the daemon self-kills only when the test fence is
set.

**Don't.** Assert a window is crash-safe in prose without a registry entry the sweep can arm — the claim is untested.
Prefix a new point `pull.after-pause-kill.before-park` because that's where its `.reached()` call sits, instead of
`pause.after-kill.before-park` for the scenario whose window it actually guards.

### Recorded exemptions — durable state the sweep does not arm

Not every durable write earns a point in this registry, and which reason applies must be a *stated* position rather than
an implicit one (the "Don't" above bars asserting a window *safe without arming it*; these are the distinct cases of a
window that need not be armed). Two grounds are admitted:

- **No window at all.** The write has no unsafe partial-write span — it is one transaction, or its halves are
  independently harmless — so there is nothing for the sweep to arm.
- **A real window whose whole loss is accepted and named.** The span exists and a crash inside it loses something, but
  what it loses is bounded, non-durable in consequence, and recoverable by other means. An entry on this ground states
  the loss, why it is tolerable, and how an operator reaches what was lost — a bar the first ground does not owe.

Either way the write earns no `bzh:crash-point-registry` entry, and earns a new `bzh:invariant-checker` assertion only
when it introduces a derived cross-fact invariant; a constraint the engine enforces, or a single-transaction insert, is
not one. Record the decision in the file below that owns the writer when a change adds durable state a reviewer would
otherwise expect a sweep point for.

A register entry is a standing statement about the write as it currently stands: the writer, the shape of its
transaction, the ground claimed, and — on the accepted-loss ground — the loss, why it is tolerable, and the operator's
recovery path. It carries no provenance for the change that added or reshaped it: no issue, review round, or superseded
design, and no contrast with an earlier shape of the same write. An entry that reads as a record of a build rather than
of a write is rewritten; a write whose window no longer exists in code earns no entry at all, so the entry leaves with
the window rather than staying to say it was retired.

The transcript lane is split out of both daemon files: a runner-side or hub-side write that belongs to it is recorded in
`transcripts.md`, not in the daemon's own register.

| File                                                                     | Read when the write you are judging is…            |
| ------------------------------------------------------------------------ | -------------------------------------------------- |
| [`crash-correctness/runner.md`](./crash-correctness/runner.md)           | …the runner's own, outside the transcript lane     |
| [`crash-correctness/hub.md`](./crash-correctness/hub.md)                 | …the hub's own, outside the transcript lane        |
| [`crash-correctness/transcripts.md`](./crash-correctness/transcripts.md) | …anywhere in the transcript lane, on either daemon |

## A facts-level invariant checker (`bzh:invariant-checker`)

**Rule.** A checker of assertions evaluated over both stores' facts after any crash → restart → recover cycle holds the
durable invariants: no duplicate env binding, at most one accepted transition per node-step epoch, no double delivery
with per-repo lands idempotent and per-repo `pr.opened` idempotent, every derived status computable with exactly one
match, a gapless outbound-buffer sequence, and usage attributed exactly once per `(lease, generation, kind)`.

**Why.** Because both stores are facts-only (`bzh:facts-not-status`), the checker is essentially a library of SQL
assertions plus the status-derivation queries themselves — and a failure names the exact violated invariant rather than
a vague corruption. It is the assertion the sweep runs after every armed crash, alongside the scenario's own expected
outcome.

**Detect.** A crash test that asserts only "the process restarted" or "the chunk eventually landed" without checking the
facts-level invariants; a new durable invariant added to the design with no assertion in the checker.

**Do.** After restart-and-recover, run the checker's SQL assertions over both stores; a violation reports which
invariant broke.

**Don't.** Rely on the scenario's happy-path outcome alone — a double-delivery or duplicate-binding bug can leave the
chunk looking landed while an invariant is silently violated.

## See also

- [./system-shape.md](./system-shape.md) — `bzh:deterministic-shell`, and, through its
  [store-facts spoke](./system-shape/store-facts.md), `bzh:facts-not-status` — the invariants these requirements rest
  on.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:crash-sweep`, the method that composes the four
  requirements into the criterion-4 proof, and the division of labor with the unit and component tiers.
