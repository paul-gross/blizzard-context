# `blizzard:unit-test` detail (`bzh:matrix-tier-unit`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

One class or function in isolation, and the sweep guards that ride the tier. Spoke of the
[test-tier hub](../test-tiers.md).

Read [`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:unit-test

`uv run pytest -m unit` — one class or function in isolation. Bare `uv run pytest` runs the unit-plus-component default
suite; the tier roster is [`../../tier-rules.md`](../../tier-rules.md#test-tiers).

The git-commit declare-and-verify round trip (`test_artifacts_storage.py`, plus the `_verify_and_collect_git_commits`
coverage in `test_runner_loop.py`/`test_runner_gates.py`) pins the worker-declares/runner-verifies split: a fake
`IWorktreeGit.verify` drives ADVANCE's collection — a verified declaration becomes a `GIT_COMMIT` `SubmittedArtifact`
carrying its manifest-named origin, and an unverified one is dropped and reported as a `command-failed` the worker can
act on — and `GitCommitArtifact`/`ArtifactRow` round-trip losslessly with `forge` carried. Reporting rather than only
dropping the unverified declaration is deliberate: a silent drop lets a chunk reach `done` having delivered nothing.

The produces-coverage agreement guard (`test_produces_coverage_agreement.py`) drives the hub's backstop
(`check_produces`) and the runner's nudge check (`_missing_produces`) over one scenario matrix and asserts both return
the same, and the expected, verdict — the anti-drift guard on the shared `wire.completion.produces_coverage` predicate.
Neither side's own tests can observe a disagreement — `test_produces_auth.py` sees only the hub, and the component
tier's `test_runner_nudge.py` only the runner — and the expected-verdict assertions also catch identical re-forks.

Four sweep guards are each the mechanical signature of a defect class otherwise caught only by hand in review:

- `test_config_keys_reach_a_gating_tier.py` fails on any key of an operator-written config dataclass — the
  `RunnerConfig`/`HubConfig` roots and the nested blocks a `[[work_source]]` or `[[auth.oauth.provider]]` binds — that
  no gating-tier test names (`bzh:gating-tier-pins-production-paths`). That is a floor; `test_runner_loop_build.py` pins
  the actual threading of the keys it covers.
- `test_no_duplicate_test_bodies.py` fails on two cases sharing a body, module constants folded into the key so two
  files reading their own same-named constant are not duplicates (`bzh:case-pins-its-own-name`).
- `test_openapi_descriptions.py` scans both committed specs, and the `wire/` models no spec reaches, for prose an
  external API consumer cannot resolve (`bzh:comment-locality`'s generated-docstring clause).
- `test_web_test_targets.py` pins that every Angular `test` target excludes `**/*.shell-sweep.spec.ts` — the premise
  `web:structural-gate`'s real-timer scoping rests on; a missing exclude would run a real-Chromium spec inside the merge
  gate while exempting it from the sweep.

The packaged-prompt declaration guard (`test_packaged_prompts_attach.py`): for every packaged graph
(`src/blizzard/hub/graphs/*/graph.yaml`), every runner node declaring `produces:` must have its inlined prompt name the
kind-appropriate declaration verb — `blizzard runner artifact create --name <that-exact-name>` for an `asset` entry,
`blizzard runner artifact commit` for a `git_commit` entry — and no packaged prompt may name the deprecated
`blizzard runner attach` alias. The guard exists because a prompt is opaque prose to the parser: a dropped or mistyped
declaration instruction, or a revert to `attach`, fails no graph-load or validation test.

The packaged graph-artifact guard (`test_adw_docket.py`) covers the same `src/blizzard/hub/graphs/*` surface on the
graph-scope half: the adv-dwf `graph.yaml` declares its `docket` under the top-level `artifacts:` map, not as a node
facet; the `PACKAGED` loader bakes the referenced file's text into the doc verbatim, and every prompt restating a slice
of the findings-docket format also names `blizzard runner artifact get docket --scope graph`. The docket guard's prompt
set is a vocabulary match against raw prompt text, not an authored list — a prompt growing docket vocabulary without the
pointer goes red — and `test_the_docket_vocabulary_census_is_exactly_ten_files` pins the matched set by name, the guard
on the guard against a pattern that silently stops matching. No docket assertion reaches content agreement: editing the
docket format obliges re-checking each restatement against `docket.md` by hand.
