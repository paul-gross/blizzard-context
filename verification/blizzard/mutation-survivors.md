# Sorting a surviving mutant (`bzh:mutation-survivor-classification`)

`blizzard:mutation` reports a survivor as a candidate; this file owns what a candidate is sorted into and what each
class obliges. Written at file-per-rule granularity in the slot skeleton `winter-canon:/rule-shape.md` owns
(`canon:rule-shape`): the classes table is the contract the Rule slot requires, not skeleton drift.

## Rule

Sort every survivor `blizzard:mutation` reports into exactly one class below, then carry out that class's remedy; a
survivor is closed by its remedy, never by being read and set aside. Ask the two questions in order — does the mutant
change anything a caller could observe, and, if it does, does a selected test execute the mutated line — and the answers
pick the class.

| Class                | Signature                                                                                                                                                                                                                                                                   | Remedy                                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Weak assertion**   | The mutant changes observable behavior, and a selected test executes the mutated line yet stays green — the test observes the path but not the value the mutation moves                                                                                                     | Name the test and the assertion that would kill the mutant, and add that assertion to that test     |
| **Unreached**        | The mutant changes observable behavior, and no selected test executes the mutated line — the tests enter the function but never take that branch. A mutant in a function no test enters is counted under `no tests` rather than listed, and is this class at function grain | Add a case that takes the branch, at a gating tier                                                  |
| **Superfluous code** | The mutant changes nothing observable because nothing observable depends on the code — a re-copy no caller mutates, a guard on a state no input produces, a default no reader consults                                                                                      | Delete the code; the mutation showed it does nothing                                                |
| **Equivalent**       | The mutant changes nothing observable, and the code is still needed — the mutated form computes the same thing along every path that reaches it                                                                                                                             | Suppress it once, at the line, with the reason stated: `# pragma: no mutate (equivalent: <reason>)` |

The suppression marker is mutmut's own, so a suppressed line is never mutated again and never returns as a survivor; the
parenthesized reason is what keeps the marker honest, and a marker with no reason is a survivor hidden rather than
sorted. One line per marker: the region forms mutmut also reads (`block`, `start`, `end`) and the `do_not_mutate` globs
in `blizzard/pyproject.toml` exclude ground no run should mutate, which is a different decision from one mutant's
equivalence and is not made here.

## Why

A survivor is the one report a green suite cannot give — the exact line whose regression the suite would let land — but
it names a line, not a cause, and each cause has a different remedy: the wrong remedy either leaves the gap open or
deletes a test that was pinning something. Sorting first is what turns a survivor list into work that closes.

## Detect

`blizzard:mutation` is the mechanical detector: `mise run mutation <scope>` writes every survivor, with its diff, to
`mutants/report.json`, and each entry there is a candidate this rule sorts. The signatures a reviewer reads a candidate
for:

- **Equivalent, the patterns already observed on this target.** A value assigned on a line a higher-precedence branch
  overrides before it is read; `None` substituted for `False` where the consumer reads only truthiness; a fallback no
  input reaches past the guard above it; a second read of a value nothing wrote between the reads. Each is equivalent
  only under the stated condition — the same substitution of `None` for `True` flips truthiness and is a real gap.
- **A type-invalid mutant is not therefore noise.** `stale=None` on a parameter typed `bool` fails the type checker and
  still lands green in the suite when nothing asserts on the stale side — a real gap wearing a type error. Reading
  survivors through a type check drops that class unread, which is why `type_check_command` stays unset in
  `blizzard/pyproject.toml`'s `[tool.mutmut]` and why a survivor is sorted from its diff, never from whether pyright
  would have rejected it.
- **A marker with no reason, or a reason the diff contradicts** — the marker asserts equivalence and the diff shows a
  branch that a caller could observe. The fix is to remove the marker and sort the survivor.
- **A survivor closed by a duplicated body** — a new case whose body matches its sibling's kills nothing the sibling did
  not, and `bzh:case-pins-its-own-name` already fails it.

## Do

One survivor per class, sorted and closed:

```text
weak assertion:  the reap case executes `lease.expired = True` and asserts only the return value
                 → assert the re-read lease's `expired` is true, in that case
unreached:       no unit case takes the `if budget <= 0:` branch of fill
                 → add the case that exhausts the budget and asserts fill declines
superfluous:     `seen = set(seen)` re-copies a set no caller mutates
                 → delete the line
equivalent:      `count > 0` → `count >= 0` where zero was rejected by the guard above
                 → `# pragma: no mutate (equivalent: zero never reaches this comparison)`
```

## Don't

- Close a Weak assertion survivor by deleting the test that reached the line: the test was reaching a production path,
  and the gap was the assertion, not the case.
- Suppress a survivor with a bare `# pragma: no mutate`, or by adding its file to `do_not_mutate`, because the diff was
  hard to read — an unreadable diff is a candidate not yet sorted, not an equivalent.
- Pre-filter `mutants/report.json` through pyright and sort only what passes.

## See also

- `bzh:mutation-review-selection` in [`./evidence.md`](./evidence.md) — what a survivor is evidence of, and the litmus
  this rule's Detect clause runs mechanically.
- `bzh:case-pins-its-own-name` in [`./evidence.md`](./evidence.md) — the guard that fails a Weak assertion closed by a
  copied body.
- `bzh:gating-tier-pins-production-paths` in [`./evidence.md`](./evidence.md) — why an Unreached remedy lands at a
  gating tier and not above it.
- `bzh:matrix-command-mutation` in [`./commands/mutation.md`](./commands/mutation.md) — what the detector runs, writes,
  and cannot see.
- [`../../garden/mutation-testing.md`](../../garden/mutation-testing.md) — the standing pass that applies this rule
  scope by scope and records the trend.
