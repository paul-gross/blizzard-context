# Pluggable seams

This spoke owns the rule that every external system is reached through a configured seam; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Pluggable seams (`bzh:pluggable-seams`)

**Rule.** Every external system is reached only through a seam — a Protocol interface — whose concrete bindings are
swappable adapters selected by configuration. A seam is the external-system application of dependency inversion
(`bzh:dependency-inversion`). The seam's core never imports an adapter, one adapter never imports another, and nothing
in the seam's package imports the loop that consumes it. House each adapter by the modules that belong to it alone:

- An adapter of several modules gets a package of its own, named only by the seam's wiring module and the composition
  roots — the harness seam's `harness/claude_code/` and `harness/opencode/`, named by `harness/wiring.py`.
- When the harness binary's major version needs a separate implementation, that binding is a package of its own beside
  the package its harness id names, held to the same isolation, with a declaration of its own — `harness/opencode_v2/`
  binds OpenCode 2. Configuration still selects the harness; the binary's version selects among the harness id's
  declarations, which the catalog lists together, the first the default. `harness/binding_selection.py` runs the
  configured binary's `--version` once as a runner is composed, names no adapter, and chooses the declaration whose
  admitted range holds it, else the first, whose health then refuses the version. The choice is threaded to everything
  composing that runner — publish, registry, health, runtime init's scaffold — and never swapped while it runs. No walk
  defaults the selection; a caller composing no runner names `first_bindings()` itself.
- An adapter of one module stays a module in the seam's `internal/` package, imported only by the seam's factory and the
  composition roots; a helper several adapters share sits in a module of its own beside them — the shape of
  `hub/work_sources/internal/` and `hub/auth/oauth/internal/`.

**Why.** Seams let tests bind the blizzard-mock fleet in place of the real stack — the entire service strategy runs
seams-mocked, spending no tokens and touching no network. An adapter kept apart from the core and its siblings stays
replaceable: neither changes when it does.

**Exception.** The runner workspace-provider seam's winter adapter spans `winter_provider.py` and `winter_cli.py`, flat
beside `basic_provider.py` and the shared `git.py` in `runner/environments/internal/`, selected by
`environments/factory.py` rather than held in a package of its own.

**Detect.** A vendor SDK, the GitHub API, or a claude/harness binary invoked directly from a loop step, the domain, or a
store rather than through an injected seam Protocol; or a test that cannot run without a real external system because no
seam exists to bind a mock to. For the harness seam, the adapter-isolation check in
`blizzard/tests/guards/test_layering.py` fails the unit tier, resolving relative imports, on each breach:

- a harness-core module importing an adapter package — `harness/claude_code/`, `harness/opencode/`, or
  `harness/opencode_v2/`;
- one adapter importing another, including one major version's binding importing the other's — the one admitted import
  is a version-selected package (`harness/opencode_v2/`) importing its family's `section` module
  (`harness/opencode/section.py`), and nothing else of that family;
- any module but `harness/wiring.py` and a composition root importing an adapter;
- a harness module other than `harness/wiring.py` importing `wiring.py`, which reaches every adapter through it;
- a module under `harness/` importing `runner/loop/` or the loop's composition root, `runner/loop_wiring.py`.

The same module's planted-tree cases prove the check catches each form. On every other seam a reviewer asks whether an
adapter imports a sibling, or has grown a second module of its own while still flat in `internal/`.

**Do.** The runner depends on `IWorkspaceProvider` and `IHarnessAdapter`; production selects winter or the built-in
basic workspace provider by configuration, and every enabled harness the catalog declares (Claude Code, OpenCode), while
tests bind the blizzard-mock fleet. The hub reaches its external systems through `IWorkSource` and its capability family
and `IOAuthProvider`. `blizzard/src/blizzard/runner/harness/wiring.py` is the one module naming the harness adapter
packages; the harness core reaches them only through `IHarnessDeclaration` and `HarnessSection`.

**Don't.** A FILL step that shells out to the `claude` binary directly — the loop can no longer be exercised against the
mock harness. Nor a harness-core module importing an adapter's constant — a denied-tool list, a section kind — so the
core changes whenever that adapter does.

**See also.** [./seam-positions.md](./seam-positions.md) owns this rule's recorded positions — the always-seated hub
work source and editor, and every path that reaches the forge.
