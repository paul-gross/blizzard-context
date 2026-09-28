# Mutation testing command detail (`bzh:matrix-command-mutation`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:mutation` heading and its cited code spans — the `mise run mutation` task name and `mutants/report.json` path — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:mutation

`mise run mutation <scope> [--budget SECONDS]` runs mutation testing (mutmut) over one garden scope of `src/blizzard`:
`hub-daemon`, `runner-daemon`, `shared-spine`, or `cli-surface`. `scripts/mutation.py`'s scope table is the one home for
each slug's mutate globs and test selection — paths are not restated here. An unknown slug exits non-zero and lists the
four valid ones before anything is copied or synced. The task runs in its own project environment (`.mutation-env`,
`UV_PROJECT_ENVIRONMENT`), never `.venv`, so `rich` and `mutmut` never reach the environment `mise run test` uses.

A run mutates only the scope's source, runs only the fast-tier (`unit or component`) tests import analysis selects for
it, and writes `mutants/report.json`: per-status mutant counts (killed, survived, timeout, no-tests, and mutmut's other
statuses) plus one entry per survivor with its mutant name, file, function, and unified diff. A completed run exits 0
whatever it finds — survivors are advisory, never a gate. Exit is non-zero only for an unknown slug, a failure inside
mutmut itself (e.g. the clean-test or forced-fail baseline), or an expired `--budget`.

Resume follows mutmut's own persistence: a mutant already carrying a verdict is skipped on the next invocation, and the
coverage map (`mutants/mutmut-stats.json`) is rebuilt only when the tree was last built for a different scope — the tree
records its owning scope and is cleared on a scope switch, never on a repeat of the same one. `--budget SECONDS` bounds
only mutant execution: the coverage-mapping phase always runs to completion first, since mutmut only persists that map
at the very end of the phase and an interrupted mapping run is lost. Once the map exists, an expired budget stops the
run through mutmut's own SIGINT/`KeyboardInterrupt` path and exits the caller-facing budget exit code; any mutant left
"not checked" or "check was interrupted" is re-run, never reported as a verdict, on the next invocation.

Measured wall time, mutant count, and test-file count. Only `cli-surface` finished as one clean run; the others are
partial or fragmented and are not comparable to it:

| Scope           | Mapping | Mutant execution                     | Total   | Mutants | Test files |
| --------------- | ------- | ------------------------------------ | ------- | ------- | ---------- |
| `cli-surface`   | 75s     | 660s                                 | 735s    | 2336    | 52         |
| `hub-daemon`    | ~1341s  | ~62593s (estimated, not a wall time) | ~63934s | 28405   | 386        |
| `runner-daemon` | —       | stopped early                        | ~3690s  | 32532   | —          |
| `shared-spine`  | —       | not run                              | —       | —       | —          |

`hub-daemon` ran to completion (23271 killed, 4892 survived, 224 no tests, 17 timeout, 1 segfault) but across many
resumed sessions, so no clean wall time exists: mapping is a timed re-run over cached mutants, and mutant execution is
summed per-mutant durations divided by 18 workers. `runner-daemon` was interrupted at about 23,600 of 32,532 mutants
after roughly an hour (13933 killed, 5883 survived, 3349 no tests, 479 timeout, remainder unchecked); no report was
written. Wall time is dominated by the expensive tail and by timeouts, not by the mutant count: the early mutants finish
fast and the remainder slow sharply, and each timeout costs its full multiplied budget (`timeout_multiplier = 3`).
Completing `runner-daemon` and `shared-spine` waits on structural fixes tracked separately.

The method cannot see: any tier above `unit`/`component` (`blizzard:service-test`, `blizzard:e2e`, `blizzard:journey`,
`blizzard:crash-sweep` all stay unmutated), `src/blizzard/tools/`, which no garden scope names, and the migrations
directories every scope excludes (`src/blizzard/*/store/migrations/versions/*`). A survivor is a candidate, not a
confirmed gap — the garden routine and the survivor-classification standard that would judge one are a later change.
