# Mutation testing command detail (`bzh:matrix-command-mutation`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:mutation` heading and its cited code spans — the `mise run mutation` task name and `mutants/report.json` path — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:mutation

`mise run mutation <scope> [--budget SECONDS]` runs mutation testing (mutmut) over one
[garden scope](../../../garden/architecture.md) of `src/blizzard`: `hub-daemon`, `runner-daemon`, `shared-spine`, or
`cli-surface`. `scripts/mutation.py`'s scope table is the one home for each slug's mutate globs and test selection —
paths are not restated here. An unknown slug exits non-zero and lists the valid ones before any mutant tree is touched.
The task runs in its own project environment (`.mutation-env`, `UV_PROJECT_ENVIRONMENT`), never `.venv`, so `rich` and
`mutmut` never reach the environment `mise run test` uses.

A run mutates only the scope's source, runs only the `unit`-tier tests import analysis selects for it — a test file with
no `unit`-marked test is left out — and writes `mutants/report.json`: per-status mutant counts (killed, survived,
timeout, no-tests, and mutmut's other statuses) plus one entry per survivor with its mutant name, file, function,
enclosing class (null for a free function), and unified diff. A completed run exits 0 whatever it finds — survivors are
advisory, never a gate. Exit is non-zero only for an unknown slug, a failure inside mutmut itself (e.g. the clean-test
or forced-fail baseline), or an expired `--budget`.

Resume follows mutmut's own persistence: a mutant already carrying a verdict is skipped on the next invocation. The tree
records its owning scope and the test selection computed when it was built, and a repeat of the same scope reuses both —
mutmut fingerprints the selection and discards every cached verdict when it changes, so a test file added between
invocations is not picked up until `mutants/` is deleted. A frozen test file since deleted is dropped, which does reset
the verdicts. A scope switch, or a tree with no scope record, clears the tree and selects afresh. `--budget SECONDS`
bounds only the mutation loop: mutant generation, the coverage map (`mutants/mutmut-stats.json`), and the clean and
forced-fail test runs always complete first — mutmut persists the map only at the very end of its phase, so an
interrupted mapping run is lost. An expired budget then stops the run through mutmut's own SIGINT/`KeyboardInterrupt`
path and exits the caller-facing budget exit code; any mutant left "not checked" or "check was interrupted" is re-run,
never reported as a verdict, on the next invocation. A `.meta` left unreadable by an interrupted write is discarded, so
that file's mutants re-run.

Measured wall time, mutant count, and test-file count. `cli-surface` is one clean run under the current configuration.
`hub-daemon` and `runner-daemon` were taken with `unit or component` selected and a timeout multiplier of 3, and are
partial or fragmented, so neither is comparable to it:

| Scope           | Mapping | Mutant execution                     | Total   | Mutants | Test files |
| --------------- | ------- | ------------------------------------ | ------- | ------- | ---------- |
| `cli-surface`   | 34s     | 111s                                 | 146s    | 2386    | 43         |
| `hub-daemon`    | ~1341s  | ~62593s (estimated, not a wall time) | ~63934s | 28405   | 386        |
| `runner-daemon` | —       | stopped early                        | ~3690s  | 32532   | —          |
| `shared-spine`  | —       | not run                              | —       | —       | —          |

`hub-daemon` ran to completion (23271 killed, 4892 survived, 224 no tests, 17 timeout, 1 segfault) but across many
resumed sessions, so no clean wall time exists: mapping is a timed re-run over cached mutants, and mutant execution is
summed per-mutant durations divided by 18 workers. `runner-daemon` was interrupted at about 23,600 of 32,532 mutants
after roughly an hour (13933 killed, 5883 survived, 3349 no tests, 479 timeout, remainder unchecked); no report was
written. Wall time is dominated by the expensive tail and by timeouts, not by the mutant count: the early mutants finish
fast and the remainder slow sharply, and each timeout costs its full multiplied budget (mutmut's `timeout_multiplier`).

The method cannot see: any tier above `unit` (`blizzard:component-test`, `blizzard:service-test`, `blizzard:e2e`,
`blizzard:journey`, `blizzard:crash-sweep` all stay unmutated), `src/blizzard/tools/`, which no garden scope names, and
the paths `[tool.mutmut].do_not_mutate` excludes from every scope. A survivor is a candidate, not a confirmed gap; no
standard yet classifies one.
