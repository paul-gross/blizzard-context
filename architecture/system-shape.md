# System shape

Blizzard's macro-shape architecture invariants: this file states the two rules every other macro-shape rule rests on and
routes the rest to spoke files by the reader's task. The parent hub is [./index.md](./index.md). Every rule here follows
the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

| Spoke                                                                                  | Read when…                                                                                                                   |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [system-shape/store-facts.md](./system-shape/store-facts.md)                           | Designing a store schema — what may be persisted, and what closes an open fact                                               |
| [system-shape/worker-boundary.md](./system-shape/worker-boundary.md)                   | Changing what crosses the runner–worker seam — the spawned child's environment, and git mutation                             |
| [system-shape/graphs.md](./system-shape/graphs.md)                                     | Authoring or minting a workflow graph — what it may know, and where its declarations are read from                           |
| [system-shape/artifact-scopes.md](./system-shape/artifact-scopes.md)                   | Reading or writing an artifact through `--scope system`, or reasoning about why a graph-scope and a system-scope read differ |
| [system-shape/transcript-read-plane.md](./system-shape/transcript-read-plane.md)       | Adding or widening a read of transcript data for runner consumption — which plane may serve it                               |
| [system-shape/seam-size.md](./system-shape/seam-size.md)                               | Adding a method to a Protocol, or deciding whether one has grown wide enough to split or register as an exception            |
| [system-shape/subscription-credentials.md](./system-shape/subscription-credentials.md) | Reading, sampling, or renewing a subscription credential file                                                                |
| [system-shape/fleet-wire.md](./system-shape/fleet-wire.md)                             | Changing a route, schema, or enum a runner reaches on the hub — what a hub change may do to it across the skew window        |

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

**Do.** The runner depends on `IWorkspaceProvider` and `IHarnessAdapter`; production selects winter or the built-in
basic workspace provider by configuration, alongside Claude Code, while tests bind the blizzard-mock fleet. The hub
reaches its external systems through `IWorkSource` and its capability family, `IOAuthProvider`, and
`IHubCommandRunner`/`IHubWorkdir`.

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
- No single forge seam Protocol exists; the forge is reached through several of the seams already named above, plus one
  path outside the Rule entirely. `IWorkSource`, `IWorkCloser`, and `IWorkAnnotator` — three of the work-source
  capability family's Protocols — and `IOAuthProvider` are real Protocol seams that happen to reach the forge:
  `IWorkSource` for work items and branch links, `IWorkCloser` for closing work items, `IWorkAnnotator` for the periodic
  forge-status annotation sweep, and `IOAuthProvider` for login. The family's fourth member, `IWorkEditor`, never
  reaches it — only the built-in hub source seats one, per the recorded position above, and that source has no external
  forge behind it. `GitHubCommitResolver` reaches it behind the `garden_delivery.CommitResolver` callable: an injected,
  composition-root-selected seam whose interface is a one-call type alias rather than a Protocol, satisfying the Rule's
  swappability intent without being one. Graph land scripts reach it directly through the `run:` env contract's
  `BZ_FORGE_*` variables, outside the Rule's sites (a loop step, domain, or store) because the script is the landing
  policy ([../verification/blizzard/tier-rules.md](../verification/blizzard/tier-rules.md) owns how tests bind the mock
  forge for this path). Land scripts and `GitHubCommitResolver` share the hub's one configured forge endpoint
  (`BZ_FORGE_URL`/`BZ_FORGE_TOKEN`/`BZ_FORGE_OWNER`); the work-source family and the OAuth provider each declare their
  own endpoint through their own config entry instead. The garden commit resolver sees only bare repo names, so it
  always qualifies by `BZ_FORGE_OWNER`, defaulting to `hub/app.py::DEFAULT_FORGE_OWNER` when unset; delivery instead
  qualifies a repo from the `git_commit` artifact's recorded origin before a land script ever runs, and the script falls
  back to `BZ_FORGE_OWNER` only when that origin was still a bare name; and a chunk whose first pointer is a `hub:` item
  gets no branch links, because `HubWorkSource.branch_url` is always `None`.

## See also

- [./crash-correctness.md](./crash-correctness.md) owns the daemon-loop requirements built on `bzh:deterministic-shell`
  and `bzh:facts-not-status`.
- [../standards/persistence.md](../standards/persistence.md) owns `bzh:sql-portable`, the portable-SQL rule the
  facts-only stores are held to.
