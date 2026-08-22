# System shape

The macro-shape invariants of the running system — the split between the deterministic code that coordinates and the
intelligent work it drives, the seam every external system sits behind, and the store-schema rule that makes crash
recovery correct. These are the foundations the daemon loops (`bzh:steppable-loop` … in
[./crash-correctness.md](./crash-correctness.md)) are built on. Each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Deterministic shell, intelligent core (`bzh:deterministic-shell`)

**Rule.** Coordination — the runner tick, the hub coordinator, the workflow transitions, the store reads and writes — is
**deterministic** code with no model calls; the **intelligent** work (the harness doing a node-step) is confined to the
leaf where a worker runs, behind the harness seam. Orchestration decides *what* to run and *where*; it never itself
reasons with an LLM.

**Why.** A deterministic shell is replayable, unit-testable without tokens, and crash-recoverable — the whole
crash-correctness harness depends on the loop being a pure function of (store, clock, seams). Pushing model judgement
into the coordinator would make the loop non-deterministic and untestable, and would spend tokens on control flow.

**Detect.** A model call, a prompt, or an LLM client inside a runner loop step, the hub coordinator, a transition, or a
store method; orchestration logic that branches on freshly-generated model output rather than on a parsed verdict fact.

**Do.** The worker (harness seam) produces a verdict; the coordinator reads the parsed verdict fact from the store and
picks the workflow edge deterministically.

**Don't.** The coordinator prompts a model to decide the next node — control flow is now non-deterministic and cannot be
replayed under the crash sweep.

## Every external system behind a seam (`bzh:pluggable-seams`)

**Rule.** Every external system is reached only through an interface — a seam — with the reference stack as its first
binding: the work source (at the hub), the workspace provider, the coding harness, delivery (the forge), and the human
channel are all Protocols, and their concrete bindings (GitHub, winter, Claude Code) are swappable adapters selected by
configuration. A seam is the external-system application of dependency inversion (`bzh:dependency-inversion`).

**Why.** A seam is what lets tests bind the mock fleet in place of the real stack — the entire service and e2e strategy
runs seams-mocked, spending no tokens and touching no network — and lets a runner swap winter worktrees for plain
worktrees without touching the loop. Code that calls a vendor SDK directly cannot be tested without that vendor and
cannot be re-bound.

**Detect.** A vendor SDK, the GitHub API, or a `claude`/harness binary invoked directly from a loop step, the domain, or
a store — rather than through an injected seam Protocol; a test that cannot run without a real external system because
no seam exists to bind a mock to.

**Do.** The runner depends on `IWorkspaceProvider`, `IHarness`, and the forge seam; production binds winter / Claude
Code / GitHub, tests bind the `blizzard-mock` fleet.

**Don't.** A FILL step that shells out to `claude -p` directly — the loop can no longer be exercised against the mock
harness and every service test now needs real tokens.

**Recorded positions** — a case that looks like it might need a configured, external binding but does not, stated so a
reviewer does not have to re-derive the same judgement:

- **The built-in `hub` work source (issue #357).** `HubWorkSource` still implements `IWorkSource` — the seam this rule
  requires — but its binding is in-process and always seated, never a `[[work_source]]` entry with a credential: its own
  store *is* the item's system of record, not a cache of an external one, so there is no external system for a config
  entry to point at. The concrete wiring stays at the composition root (`hub/app.py::build_hosted_app`) exactly as
  `bzh:dependency-injection` requires for every other binding — only the walk that seats it differs (outside the
  configured-entry loop, in `WorkSourceEntry.registry`), not the seam itself. Its **editor** capability (`IWorkEditor`,
  blizzard#358) is seated the same way and carries the same judgement one step further, on two counts.

  First, *why it is structural rather than an opt-in*: `annotate`/`close` are each a configured source's own opt-in key,
  but no `[[work_source]]` field could ever opt a source into editing. The reason is not that editing reaches the hub's
  own store — `annotate`/`close` are configured opt-ins that also write to an external store, so store locality alone
  doesn't distinguish editing from them. What actually closes the seam is the *return type*: every `IWorkEditor` method
  returns the hub repository's own record type or a value built from it — `WorkItemRecord` (a `wi_<ulid>` id, a
  hub-user-or-fleet author, a closure) for `list`/`get`/`edit`/`withdraw`, and `create`'s own `CreatedWorkItem`
  (blizzard#359) for `create` — the pairing `create` alone needs, since only it also mints a chunk no external binding
  could ever supply a `Graph` parameter for. Unlike `IWorkSource.fetch`, which returns a seam-local `WorkItem` dataclass
  any binding can answer, nothing here is renderable by a binding with no hub-owned store behind it.
  `editor(name) is None` is therefore *structurally never edited* for every source but `hub`, not merely *not opted in*
  — a capability seated with no flag at all is still one seam, one composition root, no different in kind from the
  source itself.

  Second, *why the same gate also covers `list`/`get`* (the read half) rather than only the three write verbs:
  `IWorkSource` itself declares no enumeration method at all, so today no non-`hub` binding — including the configured
  GitHub adapter, whose `fetch` answers one pointer at a time — has any way to serve `list()`/`get()` regardless of the
  editor gate. Gating reads alongside writes changes nothing observable while that holds; the day a binding gains a real
  enumeration capability, the read half is what splits out of `IWorkEditor`, not before.

## The remaining rules, by what you are changing

The rules above are the two every other one rests on. The rest of the macro shape is split by the reader question it
answers; each spoke carries its rules whole, in the same slot skeleton.

| Spoke                                                                  | Read when you are…                                                                                  |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| [`system-shape/store-facts.md`](./system-shape/store-facts.md)         | …designing a store schema — what may be persisted, and what closes an open fact                     |
| [`system-shape/worker-boundary.md`](./system-shape/worker-boundary.md) | …changing what crosses the runner–worker seam — the spawned child's environment, and git mutation   |
| [`system-shape/graphs.md`](./system-shape/graphs.md)                   | …authoring or minting a workflow graph — what it may know, and where its declarations are read from |

## See also

- [./crash-correctness.md](./crash-correctness.md) — the daemon requirements built on `bzh:facts-not-status` and
  `bzh:deterministic-shell`.
- [../standards/persistence.md](../standards/persistence.md) — `bzh:sql-portable`, the portable-SQL rule the facts-only
  stores are held to.
