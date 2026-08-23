# `blizzard:unit-test` detail (`bzh:matrix-tier-unit`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The unit spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:unit-test

`uv run pytest -m unit` runs one class or function in isolation, plus the sweep guards that ride the tier. Bare
`uv run pytest` runs the unit-plus-component default suite; the tier roster is owned by
[`../../tier-rules.md#test-tiers`](../../tier-rules.md#test-tiers).

The four sweep guards, each the mechanical signature of a defect class otherwise caught only by hand in review:

- `test_config_keys_reach_a_gating_tier.py` — fails on any key of an operator-written config dataclass — the
  `RunnerConfig`/`HubConfig` roots and the nested blocks a `[[work_source]]` or `[[auth.oauth.provider]]` binds — that
  no gating-tier test names (`bzh:gating-tier-pins-production-paths`). A floor only, since `test_runner_loop_build.py`
  pins the actual threading of the keys it covers.
- `test_no_duplicate_test_bodies.py` — fails on two cases sharing a body, module constants folded into the key so two
  files reading their own same-named constant are not duplicates (`bzh:case-pins-its-own-name`).
- `test_openapi_descriptions.py` — scans both committed specs, and the `wire/` models no spec reaches, for prose an
  external API consumer cannot resolve (`bzh:comment-locality`'s generated-docstring clause).
- `test_web_test_targets.py` — pins that every Angular `test` target excludes `**/*.shell-sweep.spec.ts` — the premise
  of `web:structural-gate`'s real-timer scoping; a missing exclude would run a real-Chromium spec inside the merge gate
  while exempting it from the sweep.

The tier's other named coverage:

- `test_produces_coverage_agreement.py` — drives the hub backstop (`Produces.rejection`, `hub/domain/produces_auth.py`)
  and the runner nudge check (`ProducesReconciler.missing`, `runner/loop/produces.py`) over one scenario matrix,
  asserting both return the same, and the expected, verdict — the anti-drift guard on the shared
  `wire.completion.Coverage` predicate. Neither side's own tests can see such a disagreement — `test_produces_auth.py`
  sees only the hub, the component-tier `test_runner_nudge.py` only the runner — and the expected-verdict assertions
  also catch identical re-forks.
- `test_artifacts_storage.py` — with the git-commit coverage in `test_runner_loop.py` and `test_runner_gates.py`, pins
  the worker-declares/runner-verifies split: a fake `IWorktreeGit.verify` drives ADVANCE's collection, and
  `GitCommitArtifact`/`ArtifactRow` round-trip losslessly with `forge` carried. A verified declaration becomes a
  `GIT_COMMIT` `SubmittedArtifact` carrying its manifest-named origin; an unverified one is dropped and reported as a
  `command-failed` the worker can act on — reported deliberately, since a silent drop lets a chunk reach `done` having
  delivered nothing.
- `test_packaged_prompts_attach.py` — in every packaged graph (`src/blizzard/hub/graphs/*/graph.yaml`), a runner node
  declaring `produces:` must have its inlined prompt name the kind-appropriate verb —
  `blizzard runner artifact create --name <that-exact-name>` for an `asset` entry, `blizzard runner artifact commit` for
  a `git_commit` entry — and no packaged prompt may name the deprecated `blizzard runner attach` alias. A prompt is
  opaque prose to the parser, so a dropped or mistyped instruction fails no graph-load or validation test.
- `test_adw_docket.py` — the same packaged-graph surface's graph-scope half: the adv-dwf `graph.yaml` declares its
  `docket` under the top-level `artifacts:` map, not as a node facet, and every prompt restating a slice of the
  findings-docket format also names `blizzard runner artifact get docket --scope graph` (the `PACKAGED` loader bakes the
  referenced file's text into the doc verbatim). The guard's prompt set is a vocabulary match on raw prompt text, not an
  authored list — a prompt growing docket vocabulary without the pointer goes red — and, distinct from that firing
  condition, `test_the_docket_vocabulary_census_is_exactly_ten_files` pins the matched set by name: the guard on the
  guard against a pattern silently ceasing to match. No docket assertion reaches content agreement: editing the docket
  format means re-checking each restatement against `docket.md` by hand.
