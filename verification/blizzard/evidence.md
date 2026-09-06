# Whether a green run proves anything (`bzh:matrix-evidence`)

The suite is green. This file owns the separate question of whether it actually pins the behavior its name claims.

What follows binds the evidence a verification claim rests on, not the inner loop: a dev-test iteration may run narrower
checks or defer a gate entirely, so long as the full declared method runs green before the work is called verified, and
a narrowed run is a convenience rather than claim evidence.

## An assertion is worth only what it observes

A negative assertion is worth only the window it is made over: a fixed sleep shorter than the subject's own cadence
proves nothing. A write that looks idempotent from the code alone is only provably idempotent once the suite performs it
twice and re-reads the resulting state.

## Choosing a mutation, and when its claim is admissible (`bzh:mutation-review-selection`)

**Rule.** Mutate a candidate line — flip a condition, drop a guard, invert a comparison — and re-run the suite; reading
a diff line by line cannot tell you which lines the suite would catch a regression on. A guard test that passes with its
guard deleted is not a guard, so mutate it to find out. Choose the candidate by who authored the load-bearing decision:
when the change authored it, mutate the change's own new branch or predicate — the one the acceptance criteria turn on,
defended by the plan; when it pre-exists the change, reach first for a decision defended by a comment long enough to
argue for itself, which is the decision easiest to silently revert. Justify the mutation against the symbol you actually
mutated, whichever you picked.

**Why.** The same litmus generalizes to any verification check — a runbook step, a CI gate, a deploy health probe: ask
whether it would still pass had the change never happened, and if it would, it is a surviving mutant rather than
evidence.

**Detect.** A mutation whose stated justification names a different symbol than the line mutated — a defect in the plan,
not a stylistic quibble.

**Do.** Make the claim per-assertion, naming the assertion that fired.

**Don't.** Rest the claim on the suite's exit status. "The suite fails against the pre-fix code" is a claim about the
aggregate exit code, and an aggregate red can be true because an unrelated assertion tripped while the one that matters
kept passing — leaving the claim vacuous for the case it was meant to cover.

## A case pins what its own name claims (`bzh:case-pins-its-own-name`)

**Rule.** Write each case so its own body observes what its own name claims.

**Why.** A test whose body matches a sibling's asserts only what the sibling already asserts, so its name is a claim
nothing observes, and the behavior that name promises goes unpinned while both cases read as covered.

**Detect.** `tests/test_no_duplicate_test_bodies.py` fails on any two cases sharing a body; a deliberate cross-tier
re-run is declared in that file rather than tolerated.

**Don't.** `test_reap_expires_a_stale_lease` written by copying `test_reap_skips_a_fresh_lease` and changing only the
name — the guard fails on the shared body, and past it the stale-lease behavior the name promises stays unobserved.

## A gating tier pins the production path (`bzh:gating-tier-pins-production-paths`)

**Rule.** Pin every production path at a gating tier — a path the gate never drives is unpinned, whatever the upper
tiers show.

**Why.** `blizzard:e2e` and `blizzard:journey` gate no PR and no push, so a path covered only there can be deleted with
every merge gate green.

**Detect.** A config key read from the operator's toml and dropped before its consumer changes nothing any tier can see.
`tests/test_config_keys_reach_a_gating_tier.py` is the floor for the config-key half — every key of every
operator-written config dataclass, nested blocks included, must be named by a gating-tier test, and the guard's own
inventory is at [`./commands.md`](./commands/test-tiers/unit.md#blizzardunit-test). Naming a key is weaker than pinning
its threading, which `tests/test_runner_loop_build.py` does case by case for the keys it covers.

**Do.** Where production takes one route and the gating tests drive a test-convenient other route, extend a gating case
onto the production route rather than trusting the upper tier.

**Don't.** A config key — say a new `[queue]` knob — whose only test is a browser scenario under `tests/e2e/` watching
the board: the gate never runs it, so the key can stop reaching FILL with every merge gate green.

## Plan against the claims a change falsifies (`bzh:falsified-claims-grep`)

**Rule.** Plan against the claims a change falsifies, not only the files it touches: enumerate the claims the change
invalidates, then grep each phrasing across both the app and the harness, opening every hit rather than stopping at the
first.

**Why.** A plan's surface inventory answers which files a change touches, a different question from which existing
claims the change makes false — a doc statement, a comment, a field name, or a test's premise can go stale in a file the
change never opens.

**Do.** Sweep the app side, then the harness side, whose path resolves via the workspace's `# Winter Extensions` block:

```bash
grep -rn '<falsified phrasing>' src/ docs/ openapi/ web/
grep -rn '<falsified phrasing>' <blizzard-context worktree>
```

**Don't.** Plan from `git diff --stat` alone — a docstring in a module the change never opens still asserts the old
default, lands with the change, and lies from its first read.

## Plan against the claims a change owes (`bzh:owed-claims-landed`)

**Rule.** Plan against the claims a change newly owes, not only the claims it falsifies: a change that grows a surface a
graph author meets names the domain statement that surface now owes and lands the statement in the same change — in the
domain file owning the concept, or in the standard that file routes to for the facet's detail. The surfaces that owe
one:

- A key an author writes — a node facet, a declaration field, a choice attribute the parser reads — owes the entry
  naming it and what it governs.
- A default an omitted declaration resolves to owes the statement of what omission resolves to, where the sibling facets
  state theirs.
- A rejection or warning an author sees at mint owes the statement that the outcome exists and what triggers it, where
  the domain owner of that part's mint-time validation speaks.

**Why.** The domain hub concedes that code is current where the two disagree, so a surface the code grows and the model
never claims is a divergence no gate reports and no later reader is placed to notice — the change that grew it is the
one moment its author knows what it means.

**Detect.** A hunk under `src/blizzard/hub/domain/` or `src/blizzard/runner/loop/` that reads a new literal key,
resolves an omitted value against a configured or constant default, or appends a mint-time error or warning, with no
companion hunk under `domain/` naming the same key, resolution, or outcome. The question to ask of the hunk: could a
graph author, reading only `domain/`, predict what it does?

**Do.** One planning line per surface, naming the statement and its home, so the domain hunk is planned rather than
remembered:

```text
owes: node key `on_reap:` → domain/graphs/nodes.md gains an `on_reap` facet naming what it governs
owes: `on_reap:` omitted → the same facet states what omission resolves to
```

**Don't.** A change landing the parser read, the resolution, or the mint-time outcome alone, the model left silent:

- A new node key parsed, stored, and served, with no facet in `domain/graphs/nodes.md` naming it — an author cannot
  learn it exists, and nothing later reports that it should.
- A node declaring no `retries:` resolving to a runner-configured budget, while the `retries` facet describes the budget
  and never says what an omission resolves to.
- A mint rejecting a `sessions:` entry that carries an unknown key, while the declared-sessions taxonomy says only which
  fields are optional — an author with a typo'd key learns the rule from the error, never from the model.

**See also.**

- `bzh:falsified-claims-grep` above — the mirror sweep, over the claims a change makes false.
- `bzh:one-prose-home` in [`../../standards/one-prose-home.md`](../../standards/one-prose-home.md) — the statement lives
  in the domain file, and the code site points at it.
