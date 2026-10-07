# System shape

Blizzard's macro-shape architecture invariants: this file states the two rules every other macro-shape rule rests on and
routes the rest to spoke files by the reader's task. The parent hub is [./index.md](./index.md). Every rule here follows
the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

| Spoke                                                                                  | Read when…                                                                                                                                                                                              |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [system-shape/store-facts.md](./system-shape/store-facts.md)                           | Designing a store schema — what may be persisted, and what closes an open fact                                                                                                                          |
| [system-shape/worker-boundary.md](./system-shape/worker-boundary.md)                   | Changing what crosses the runner–worker seam — the spawned child's environment, and git mutation                                                                                                        |
| [system-shape/graphs.md](./system-shape/graphs.md)                                     | Authoring or minting a workflow graph — what it may know, and where its declarations are read from                                                                                                      |
| [system-shape/artifact-scopes.md](./system-shape/artifact-scopes.md)                   | Reading or writing an artifact through `--scope system`, or reasoning about why a graph-scope and a system-scope read differ                                                                            |
| [system-shape/transcript-read-plane.md](./system-shape/transcript-read-plane.md)       | Adding or widening a read of transcript data for runner consumption — which plane may serve it                                                                                                          |
| [system-shape/seam-size.md](./system-shape/seam-size.md)                               | Adding a method to a Protocol, or deciding whether one has grown wide enough to split or register as an exception                                                                                       |
| [system-shape/seam-positions.md](./system-shape/seam-positions.md)                     | Deciding whether a reach into an external system — the forge above all — must go through a configured seam, or why the hub work source and editor are always seated                                     |
| [system-shape/subscription-credentials.md](./system-shape/subscription-credentials.md) | Reading, sampling, or renewing a subscription credential file                                                                                                                                           |
| [system-shape/fleet-wire.md](./system-shape/fleet-wire.md)                             | Changing a route, schema, or enum a runner reaches on the hub — what a hub change may do to it across the skew window                                                                                   |
| [system-shape/exclusive-writes.md](./system-shape/exclusive-writes.md)                 | Adding or reviewing a write enforcing an exactly-one-wins decision, or a write another such decision's guard reads consult                                                                              |
| [system-shape/configuration.md](./system-shape/configuration.md)                       | Adding or changing a configured record, its routes or CLI verbs, a document the hub ingests, a secret's handling, or a read of configuration — the verb set, patch meaning, codec seam, and read-on-use |

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
(`bzh:dependency-inversion`). The seam's core never imports an adapter, one adapter never imports another, and nothing
in the seam's package imports the loop that consumes it. House each adapter by the modules that belong to it alone:

- An adapter of several modules gets a package of its own, named only by the seam's wiring module and the composition
  roots — the harness seam's `harness/claude_code/` and `harness/opencode/`, named by `harness/wiring.py`.
- An adapter of one module stays a module in the seam's `internal/` package, imported only by the seam's factory and the
  composition roots; a helper several adapters share sits in a module of its own beside them — the shape of
  `hub/work_sources/internal/` and `hub/auth/oauth/internal/`.

**Why.** Seams let tests bind the blizzard-mock fleet in place of the real stack — the entire service and e2e strategy
runs seams-mocked, spending no tokens and touching no network. An adapter kept apart from the core and its siblings
stays replaceable: neither changes when it does.

**Exception.** The runner workspace-provider seam's winter adapter spans `winter_provider.py` and `winter_cli.py`, flat
beside `basic_provider.py` and the shared `git.py` in `runner/environments/internal/`, selected by
`environments/factory.py` rather than held in a package of its own.

**Detect.** A vendor SDK, the GitHub API, or a claude/harness binary invoked directly from a loop step, the domain, or a
store rather than through an injected seam Protocol; or a test that cannot run without a real external system because no
seam exists to bind a mock to. For the harness seam,
`test_adapters_are_named_only_by_the_harness_wiring_and_the_composition_roots` in `blizzard/tests/test_layering.py`
fails the unit tier, resolving relative imports, on each breach:

- a harness-core module importing `harness/claude_code/` or `harness/opencode/`;
- one adapter importing the other;
- any module but `harness/wiring.py` and a composition root importing either adapter;
- a harness module other than `harness/wiring.py` importing `wiring.py`, which reaches every adapter through it;
- a module under `harness/` importing `runner/loop/` or the loop's composition root, `runner/loop_wiring.py`.

`test_adapter_isolation_catches_every_breach` proves the check catches each form. On every other seam a reviewer asks
whether an adapter imports a sibling, or has grown a second module of its own while still flat in `internal/`.

**Do.** The runner depends on `IWorkspaceProvider` and `IHarnessAdapter`; production selects winter or the built-in
basic workspace provider by configuration, and every enabled harness the catalog declares (Claude Code, OpenCode), while
tests bind the blizzard-mock fleet. The hub reaches its external systems through `IWorkSource` and its capability
family, `IOAuthProvider`, and `IHubCommandRunner`/`IHubWorkdir`. `blizzard/src/blizzard/runner/harness/wiring.py` is the
one module naming both harness adapters; the harness core reaches them only through `IHarnessDeclaration` and
`HarnessSection`.

**Don't.** A FILL step that shells out to the `claude` binary directly — the loop can no longer be exercised against the
mock harness. Nor a harness-core module importing an adapter's constant — a denied-tool list, a section kind — so the
core changes whenever that adapter does.

**See also.** [./system-shape/seam-positions.md](./system-shape/seam-positions.md) owns this rule's recorded positions —
the always-seated hub work source and editor, and every path that reaches the forge.

### Seams answer their binding's facts (`bzh:seam-answers-binding-facts`)

**Rule.** A seam answers its binding's specific facts itself, and no consumer compares a binding's config name — a
`workspace_provider` value or a harness id — outside the selection point that picks the binding.

**Why.** A consumer that branches on a binding's name hard-codes that binding's behavior where the seam cannot see it:
the branch is silently wrong for every other binding, and adding a binding means finding every such branch by hand
rather than implementing one declaration.

**Detect.** The ast-grep rule in `blizzard/contracts/ast-grep/rules/seam-answers-binding-facts.yml` (run by
`blizzard:structural-gate`) flags a comparison of `workspace_provider` or of a harness-id string literal outside the
selection points, the bindings' own modules, and migrations. By eye: an `if … == "winter"` or `== "claude_code"`
anywhere a seam is already injected.

**Do.** Ask the seam. The workspace provider reports where a worker is spawned (`IWorkspaceProvider.spawn_root`), how
many environments it may hold (`capacity`), and its environment pool (`pool`), in
`blizzard/src/blizzard/runner/environments/provider.py`; the selection point is the factory registry in
`runner/environments/factory.py`, whose builders take a `WorkspaceSettings` (built by
`RunnerConfig.workspace_settings`), not `RunnerConfig`. Harnesses are iterated, never named:
`blizzard/src/blizzard/runner/harness/wiring.py` holds the cached `harness_catalog()` of `IHarnessDeclaration`s and its
walks (`declared`, `enabled`, `declared_normalizer_versions`, `declared_telemetry_names`, `combined_telemetry_plan`),
`declared` and `enabled` pairing each declaration with its `HarnessSection` (both in `harness/declaration.py`). A
binding's own telemetry — the names it arrives under and what the runner does with each exporter — is answered by its
declaration (`telemetry_names`, `telemetry_plan`), never named by the composition root or the tracing receiver.
Importing `wiring.py` loads only each adapter's section module; an adapter's declaration loads on the catalog's first
call. A third harness is a new declaration and section kind added to the catalog, not a new branch in its consumers.

**Don't.** Pick a worker's cwd with `if workspace_provider == "winter"` in the runner, or add a harness by threading a
second `opencode_*` parameter through the composition root, the probes, and the CLI beside the Claude Code one.

#### Recorded positions

- The hub's analytics dialect registry (`DIALECTS` in
  `blizzard/src/blizzard/hub/domain/observability/analytics/dialects.py`) stays hub-owned and keyed by the wire's
  `normalizer_version`, not built from the runner catalog: it must interpret historical segments from runners and
  harness versions that no longer exist, and the hub never imports `blizzard.runner` (`bzh:domain-core`). Adding a
  harness without a dialect is made un-forgettable by guard instead —
  `blizzard/tests/test_analytics_dialect_corpus_guard.py` iterates the catalog's `declared_normalizer_versions()` and
  fails on any without a `DIALECTS` entry.

## See also

- [./crash-correctness.md](./crash-correctness.md) owns the daemon-loop requirements built on `bzh:deterministic-shell`
  and `bzh:facts-not-status`.
- [../standards/persistence.md](../standards/persistence.md) owns `bzh:sql-portable`, the portable-SQL rule the
  facts-only stores are held to.
