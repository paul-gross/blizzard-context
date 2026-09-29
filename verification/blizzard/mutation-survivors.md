# Sorting a surviving mutant (`bzh:mutation-survivor-classification`)

`blizzard:mutation` reports a survivor as a candidate; this file owns what a candidate is sorted into and what each
class obliges. A change's own survivors reach a delivery as the advisory `mutation-report` from `blizzard:mutation`'s
delta mode; review sorts them here and raises each real gap as `should-fix`, never `blocking`. Written at file-per-rule
granularity in the slot skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`): the classes table is the
contract the Rule slot requires, not skeleton drift.

## Rule

Sort every survivor `blizzard:mutation` reports into exactly one class below, then carry out that class's remedy; a
survivor is closed by its remedy, never by being read and set aside — an Equivalent left unmarked is closed by recording
its class and reason, which is its remedy. Ask first whether the mutant changes anything a caller could observe. If it
does, ask whether a selected test executes the mutated line: yes is Weak assertion, no is Unreached. If it does not, ask
whether the code is still needed — whether deleting it would change anything a caller could observe: yes is Equivalent,
no is Superfluous code.

| Class                | Signature                                                                                                                                                                                                                                                                   | Remedy                                                                                                                                                                                                                                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Weak assertion**   | The mutant changes observable behavior, and a selected test executes the mutated line yet stays green — the test observes the path but not the value the mutation moves                                                                                                     | Name the test and the assertion that would kill the mutant, and add that assertion to that test                                                                                                                                                                                                          |
| **Unreached**        | The mutant changes observable behavior, and no selected test executes the mutated line — the tests enter the function but never take that branch. A mutant in a function no test enters is counted under `no tests` rather than listed, and is this class at function grain | Add a case that takes the branch, at a gating tier                                                                                                                                                                                                                                                       |
| **Superfluous code** | The mutant changes nothing observable because nothing observable depends on the code — a re-copy no caller mutates, a guard on a state no input produces, a default no reader consults                                                                                      | Delete the code; the mutation showed it does nothing                                                                                                                                                                                                                                                     |
| **Equivalent**       | The mutant changes nothing observable, and the code is still needed — the mutated form computes the same thing along every path that reaches it                                                                                                                             | Mark the line once, with the reason stated — `# pragma: no mutate (equivalent: <reason>)` — when the marker costs no other mutant on it, on the line itself or on a statement the expression is split into; otherwise leave it unmarked and record the survivor Equivalent, with its reason, on each run |

The suppression marker is mutmut's own, and it works at line grain: mutmut stops generating every mutant on a marked
line, not only the equivalent one. A survivor of another class on that line leaves the report unsorted, and a mutant a
test kills today stops checking that the test still kills it. So mark a line only when every mutant on it is equivalent
— read the line for what else mutmut alters there, since nearly every token on it is a mutation site: operators,
numbers, strings, keywords, call arguments, and an assignment's value, which mutmut replaces with `None` — and
`mutants/report.json` lists none of the killed ones. mutmut reads a bare marker only as the trailing comment of a
statement, or of a compound statement's header after its colon, and applies it to the line that statement starts on. A
marker on a comment line of its own marks only that comment line, and one on a continuation line inside a parenthesized
expression is never read — either looks placed and suppresses nothing.

When the line carries a mutant that matters, sort and close its other survivors first, then move the equivalent
expression into a statement of its own — bind it to a local — and mark that line only if every mutant on it but the
local's own `= None` is equivalent. That one is the marker's to take: it exists only because of the split, so marking it
drops nothing the code was checked for before. An expression that cannot be separated from its neighbors stays unmarked
and is recorded Equivalent again on each run, the price of keeping them checked. The parenthesized reason is what keeps
the marker honest, and a marker with no reason is a survivor hidden rather than sorted. One line per marker: the region
forms mutmut also reads (`block`, `start`, `end`) and the `do_not_mutate` globs in `blizzard/pyproject.toml` exclude
ground no run should mutate, which is a different decision from one mutant's equivalence and is not made here.

## Why

A survivor is the one report a green suite cannot give — the exact line whose regression the suite would let land — but
it names a line, not a cause, and each cause has a different remedy: the wrong remedy either leaves the gap open or
deletes a test that was pinning something. Sorting first is what turns a survivor list into work that closes.

## Detect

`blizzard:mutation` is the mechanical detector: `mise run mutation <scope>` writes every survivor, with its diff, to
`mutants/report.json`, and each entry there is a candidate this rule sorts. The signatures a reviewer reads a candidate
for:

- **Equivalent, the patterns already observed on this target.** A value a higher-precedence branch overrides before it
  is read; `None` substituted for `False` where the consumer reads only truthiness; a fallback the guard above it
  narrows; a second read of a value nothing wrote between the reads. Each names why the mutation is invisible, not why
  the code is needed, so each is Equivalent only while the code still is: the overridden value is still read on inputs
  the override does not catch, the mutant differing only on those it does; the `False` is still a default callers omit;
  the fallback is still reached by some input, the guard leaving it only inputs on which the mutant computes the same
  result; the re-read is still the only binding in scope where it is used. Where deleting the code is as invisible as
  the mutation, the survivor is Superfluous code whichever pattern it matches — a fallback no input reaches at all is
  Superfluous even where the type checker makes deleting it take a restructure. And each holds only under its condition
  — the same substitution of `None` for `True` flips truthiness and is a real gap.
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
equivalent:      `count > 0` → `count >= 0` where zero was rejected by the guard above; `count > 1` is a
                 mutant of the same line, and the one-item case kills it
                 → leave the line unmarked, since the marker would stop generating `count > 1` too —
                   and splitting cannot help, because `0` → `1` belongs to the same expression and moves
                   with it — and record this survivor Equivalent, with its reason, on each run
```

## Don't

- Close a Weak assertion survivor by deleting the test that reached the line: the test was reaching a production path,
  and the gap was the assertion, not the case.
- Suppress a survivor with a bare `# pragma: no mutate`, or by adding its file to `do_not_mutate`, because the diff was
  hard to read — an unreadable diff is a candidate not yet sorted, not an equivalent.
- Mark a line for its one equivalent mutant while another mutant on it is a survivor of another class or one a test
  kills — the marker drops them with it, and the gap or the pin disappears from every later run unread. A split local's
  own `= None` is the one exception.
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
