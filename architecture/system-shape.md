# System shape

Blizzard's macro-shape architecture invariants: this file states the two rules every other macro-shape rule rests on and
routes the rest to spoke files by the reader's task. The parent hub is [./index.md](./index.md). Every rule here follows
the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

| Spoke                                                                            | Read when…                                                                                                                   |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [system-shape/store-facts.md](./system-shape/store-facts.md)                     | Designing a store schema — what may be persisted, and what closes an open fact                                               |
| [system-shape/worker-boundary.md](./system-shape/worker-boundary.md)             | Changing what crosses the runner–worker seam — the spawned child's environment, and git mutation                             |
| [system-shape/graphs.md](./system-shape/graphs.md)                               | Authoring or minting a workflow graph — what it may know, and where its declarations are read from                           |
| [system-shape/artifact-scopes.md](./system-shape/artifact-scopes.md)             | Reading or writing an artifact through `--scope system`, or reasoning about why a graph-scope and a system-scope read differ |
| [system-shape/transcript-read-plane.md](./system-shape/transcript-read-plane.md) | Adding or widening a read of transcript data for runner consumption — which plane may serve it                               |

## Deterministic shell (`bzh:deterministic-shell`)

**Rule.** Coordination — the runner tick, the hub coordinator, workflow transitions, and store reads and writes — is
deterministic code with no model calls; intelligent work is confined to the leaf where a worker runs, behind the harness
seam.

**Why.** Crash correctness depends on the loop being a pure function of store, clock, and seams — a deterministic shell
is replayable, unit-testable without tokens, and crash-recoverable, while model judgement in the coordinator would break
replay and spend tokens on control flow.

**Detect.** A model call, prompt, or LLM client inside a runner loop step, the hub coordinator, a transition, or a store
method; or orchestration logic branching on freshly generated model output rather than on a parsed verdict fact.

**Do.** The worker produces a verdict; the coordinator reads the parsed verdict fact from the store and picks the
workflow edge deterministically.

**Don't.** A coordinator that prompts a model to choose the next node — it cannot be replayed under the crash sweep.

## Pluggable seams (`bzh:pluggable-seams`)

**Rule.** Every external system is reached only through a seam — a Protocol interface — whose concrete bindings are
swappable adapters selected by configuration. A seam is the external-system application of dependency inversion
(`bzh:dependency-inversion`).

**Why.** Seams let tests bind the blizzard-mock fleet in place of the real stack — the entire service and e2e strategy
runs seams-mocked, spending no tokens and touching no network.

**Detect.** A vendor SDK, the GitHub API, or a claude/harness binary invoked directly from a loop step, the domain, or a
store rather than through an injected seam Protocol; or a test that cannot run without a real external system because no
seam exists to bind a mock to.

**Do.** The runner depends on `IWorkspaceProvider`, `IHarness`, and the forge seam; production binds winter, Claude
Code, and GitHub, while tests bind the blizzard-mock fleet. The reference seam stack: the work source (at the hub), the
workspace provider, the coding harness, delivery (the forge), and the human channel are the seam Protocols.

**Don't.** A FILL step that shells out to the `claude` binary directly — the loop can no longer be exercised against the
mock harness.

### Recorded positions

Stated so a reviewer need not re-derive them:

- The built-in hub work source, `HubWorkSource`, implements the `IWorkSource` seam, but its binding is in-process and
  always seated — never a `[[work_source]]` config entry with a credential — because the hub's own store is the item's
  system of record: there is no external system for a config entry to point at. Its concrete wiring stays at the
  composition root, `hub/app.py::build_hosted_app`, per `bzh:dependency-injection`; only the walk that seats it differs
  — outside the configured-entry loop, in `WorkSourceEntry.registry` — not the seam itself.
- The hub work source's editor capability, `IWorkEditor`, is seated the same always-on in-process way, and it is
  structural rather than a configurable opt-in because every `IWorkEditor` method returns the hub repository's own
  record types — `WorkItemRecord` for `list`, `get`, `edit`, and `withdraw`, and `CreatedWorkItem` for `create`, which
  alone also mints a chunk — types no binding without a hub-owned store behind it could render, unlike
  `IWorkSource.fetch`'s seam-local `WorkItem` dataclass. The editor gate also covers the read verbs `list` and `get`,
  because `IWorkSource` declares no enumeration method, so no non-hub binding could serve them anyway; the read half is
  what splits out of `IWorkEditor` the day a binding gains a real enumeration capability, and not before. Consequently
  `editor(name) is None` means structurally never edited for every source but the hub, not merely not opted in.

## See also

- [./crash-correctness.md](./crash-correctness.md) owns the daemon-loop requirements built on `bzh:deterministic-shell`
  and `bzh:facts-not-status`.
- [../standards/persistence.md](../standards/persistence.md) owns `bzh:sql-portable`, the portable-SQL rule the
  facts-only stores are held to.
