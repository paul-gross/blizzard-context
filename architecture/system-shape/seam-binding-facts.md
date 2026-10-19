# Seam binding facts

This spoke owns where a binding-specific fact is answered; the macro-shape hub is
[../system-shape.md](../system-shape.md). The rule follows the slot skeleton owned by `winter-canon:/rule-shape.md`
(`canon:rule-shape`).

## Seams answer their binding's facts (`bzh:seam-answers-binding-facts`)

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
`runner/environments/factory.py`, whose builders take a `WorkspaceSettings` (built by `HostWorkspace.settings`), not
`RunnerConfig`. Harnesses are iterated, never named: `blizzard/src/blizzard/runner/harness/wiring.py` holds the cached
`harness_catalog()` of `IHarnessDeclaration`s and its walks (`declared`, `enabled`, `declared_normalizer_versions`,
`declared_telemetry_names`, `combined_telemetry_plan`), `declared` and `enabled` pairing each declaration with its
`HarnessSection` (both in `harness/declaration.py`). A binding's own telemetry — the names it arrives under and what the
runner does with each exporter — is answered by its declaration (`telemetry_names`, `telemetry_plan`), never named by
the composition root or the tracing receiver. Importing `wiring.py` loads only each adapter's section module; an
adapter's declaration loads on the catalog's first call. A third harness costs three things, and nothing else outside
its own package:

- its declaration and section kind in the catalog (`harness/wiring.py`);
- its own row in `_RUNNER_PACKAGE_LAYERS` in `blizzard/tests/test_layering.py`, whose edges the unused-edge check holds
  to what the binding's imports walk — a binding package without a row fails the undeclared-node check;
- its id in the ast-grep rule's id lists and binding-module `ignores`, held to the catalog by a unit test in the same
  module.

Every other roster derives from the catalog (`HARNESS_SECTION_KINDS`): the layer gate's binding nodes, the adapter
packages, and the runner-home keys a host file refuses at the top level. Not a new branch in a consumer.

**Don't.** Pick a worker's cwd with `if workspace_provider == "winter"` in the runner, or add a harness by threading a
second `opencode_*` parameter through the composition root, the probes, and the CLI beside the Claude Code one.

### Recorded positions

- The hub's analytics dialect registry (`DIALECTS` in
  `blizzard/src/blizzard/hub/domain/observability/analytics/dialects.py`) stays hub-owned and keyed by the wire's
  `normalizer_version`, not built from the runner catalog: it must interpret historical segments from runners and
  harness versions that no longer exist, and the hub never imports `blizzard.runner` (`bzh:domain-core`). Adding a
  harness without a dialect is made un-forgettable by guard instead —
  `blizzard/tests/test_analytics_dialect_corpus_guard.py` iterates the catalog's `declared_normalizer_versions()` and
  fails on any without a `DIALECTS` entry.
