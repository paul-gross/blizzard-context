# Mutation testing command detail (`bzh:matrix-command-mutation`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:mutation` heading and its cited code spans — the `mise run mutation` task name and `mutants/report.json` path — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:mutation

`mise run mutation <scope> [--budget SECONDS] [--since REV] [--fresh]` runs mutation testing (mutmut) over one
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

`--since REV` narrows a run to the delta: only the functions in the scope's ground whose source differs between `REV`
and `HEAD` are executed and reported, and the report records the `since` revision. Generation and the coverage map still
cover the whole scope. A `REV` that names no commit exits 2 and runs nothing — it never widens to a full run. A scope
with no changed function writes a complete, empty `mutants/report.json` and exits 0, with no mutant generated or run. A
changed function that carries no mutant (a decorated body mutmut skips) is left out, not an error.

`--fresh` discards any existing mutant tree before the run, so no verdict or test selection from an earlier run
survives. A leased worker passes it: a pooled environment keeps its ignored `mutants/` between leases, and its frozen
selection would otherwise date from an older revision. A local resume omits it.

`mutants/report.json` is written whenever the run ends, including on an expired `--budget`: it then carries
`"complete": false`, its counts include the unchecked mutants under `not checked`, and its survivors are only those
found so far. A full-scope run stopped this way is real evidence for how large the survivor backlog is; the run still
exits the budget exit code.

**Delta mode.** `mise run mutation --since REV [--delta-budget SECONDS]` — no scope — is the delivery-time form. It maps
every file under `src/blizzard` that differs between `REV` and `HEAD` to the scopes that own it, and runs each touched
scope fresh, one after another, as its own `<scope> --since REV --fresh` process. A scope whose changed files carry no
changed function is `no-changes` and is not run. Changed files no scope owns — `src/blizzard/tools/` and the global
exclusions — are listed, not run. A `REV` that names no commit exits 2 and runs nothing.

`--delta-budget` is one wall-clock budget for the whole delta, preparation included; its default, 1800 seconds, lives in
`scripts/mutation.py`. It is not `--budget`, which bounds one scope's execution only, and passing both is refused. A
scope still running at the deadline is killed and reported `over-budget`, and a scope not yet started is reported
`over-budget` too; scopes already finished keep their results.

The delta run always writes `mutants/delta-report.json` beside `mutants/report.json` and exits 0 whenever it does. The
report records `since`, the budget, total `elapsed_seconds`, `unscoped_files`, and one entry per touched scope with its
`status` (`complete`, `over-budget`, `failed`, `no-changes`), `reason`, `elapsed_seconds` and `survivors`. A `failed`
scope carries the tail of its run's output, since a mutmut baseline failure writes no `report.json`. Test selection
stays each scope's own: narrowing it to the changed modules would under-select and report false Unreached survivors.

Preparation — generation, the coverage map, and the clean and forced-fail runs — costs more than one tool call's
ten-minute limit on a daemon scope, and no worker setting raises that limit. A worker therefore runs the command in the
background, polls it to completion in short calls, and does not re-invoke it under a small `--budget`, since each
re-invocation pays the clean and forced-fail runs again. The coverage map is not persisted across leases: mutmut re-maps
only test ids it has not seen, never a changed test's reach, so a kept map reports false survivors on exactly the
functions a delta run targets.

Measured wall time, on a shared 20-core host at load 5 to 20, under the current configuration (`unit`-tier selection,
timeout multiplier of 3). Preparation is generation plus the coverage map plus the clean and forced-fail runs; a full
execution of a daemon scope is hours and is not measured:

| Scope           | Generation | Mapping  | Clean + forced-fail | Preparation | Execution       | Mutants | Test files |
| --------------- | ---------- | -------- | ------------------- | ----------- | --------------- | ------- | ---------- |
| `cli-surface`   | 4s         | 37s      | 36s                 | 77s         | 79s             | 2386    | 43         |
| `hub-daemon`    | 29s        | ~4 min   | ~3.7 min            | 8.3 min     | not run in full | 28,698  | 138        |
| `runner-daemon` | 64s        | ~4.5 min | ~4.5 min            | 10.2 min    | not run in full | —       | 115        |
| `shared-spine`  | 3s         | ~3.4 min | ~3.5 min            | ~7 min      | ~11.5 min       | 668     | 157        |

A full `cli-surface` sweep takes 156 to 169s (1454 killed, 693 survived, 226 no tests, 13 timeout) — too many survivors
to sort in one context, which is the designed `excessive` outcome. A prior full `hub-daemon` run across many resumed
sessions left 4892 survivors. Wall time in execution is dominated by the expensive tail and by timeouts, not the mutant
count: each timeout costs its full multiplied budget (mutmut's `timeout_multiplier`).

Delta mode's measured wall time — `mutation --since <base>` over five fleet chunks that touched `src/blizzard`, each the
pull request's base against its head, the delta mode overlaid on each historical head, one at a time on the same shared
host. This is the command alone; the node's session overhead is not in it:

| Chunk diff | Scopes run: survivors                                                                | Wall time |
| ---------- | ------------------------------------------------------------------------------------ | --------- |
| 1 file     | `runner-daemon`: 21                                                                  | 539s      |
| 1 file     | `runner-daemon`: 14                                                                  | 544s      |
| 2 files    | `runner-daemon`: 0                                                                   | 600s      |
| 22 files   | `hub-daemon`: 155, `runner-daemon`: 123, `cli-surface`: 0; `shared-spine` no-changes | 1289s     |
| 10 files   | `hub-daemon`: 318, `cli-surface`: 0; `shared-spine` no-changes                       | 1331s     |

The median is 600s, command only; every run finished under the 1800s default with all scopes `complete`. A change that
touches only one daemon scope costs one preparation (7 to 10 minutes), and each further daemon scope adds another.

The method cannot see: any tier above `unit` (`blizzard:component-test`, `blizzard:service-test`, `blizzard:e2e`,
`blizzard:journey`, `blizzard:crash-sweep` all stay unmutated), `src/blizzard/tools/`, which no garden scope names, the
paths `[tool.mutmut].do_not_mutate` excludes from every scope, and the body of any decorated function other than a lone
`@staticmethod` or `@classmethod` — mutmut's `_skip_node_and_children` skips it because the trampoline copy would repeat
the decorator's side effects. A property is the case that matters; `bzh:property-delegates` keeps decision logic out of
it. A survivor is a candidate, not a confirmed gap; `bzh:mutation-survivor-classification` in
[`../mutation-survivors.md`](../mutation-survivors.md) sorts one.
