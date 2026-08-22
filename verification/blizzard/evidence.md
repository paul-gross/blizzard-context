# Evidence rules — whether a green run proves anything (`bzh:matrix-evidence`)

A passing suite is not the same as a pinned behavior. These rules govern which lines are worth mutating, which claims a
change falsifies, what a test's name obliges its body to assert, and why a path only the non-gating tiers drive is
unpinned.

- **Mutation selection: a long-comment-defended decision is a decision to mutate, an idempotent-looking write is only
  provably idempotent once re-read, and a mutation claim is admissible only per-assertion
  (`bzh:mutation-review-selection`, issues #149/#157/#158).** Reading a diff line by line cannot tell which lines the
  suite actually catches a regression on — mutating a candidate line (flip a condition, drop a guard, invert a
  comparison) and re-running the suite is the only way to find out, but mutating every line doesn't scale, so selection
  matters: a decision defended by a comment long enough to argue for itself is exactly the decision easiest to silently
  revert, so mutate it first; and a write that looks idempotent from the code alone is only provably idempotent once the
  suite actually performs it twice and re-reads the resulting state — inspecting the code is not a substitute for
  driving the write and observing what landed. Once a mutation is run, the claim it supports is only as good as the
  specific assertion that caught it: "the suite fails against the pre-fix code" is a claim about the aggregate exit
  code, and an aggregate red can be true because an unrelated assertion tripped while the one that matters keeps passing
  — name the assertion that fired, not the suite's exit status, or the claim is vacuous for the case it was meant to
  cover (#157/#158). The same litmus generalizes past test suites to any verification check — a runbook step, a CI gate,
  a deploy health probe: ask whether the check would still pass had the change never happened, and if it would, it is a
  surviving mutant, not evidence.
- **Plan against the claims a change falsifies, not only the files it touches (`bzh:falsified-claims-grep`, issue
  #149).** A plan's surface inventory — which files does this change touch — answers a different question than which
  existing claims does this change make false: a doc statement, a comment, a field name, or a test's premise can go
  stale in a file the change never touches directly. Enumerate the claims the change invalidates, then grep each
  phrasing across the app and the harness, opening every hit rather than stopping at the first:

  ```bash
  grep -rn '<falsified phrasing>' src/ docs/ openapi/ web/
  grep -rn '<falsified phrasing>' <blizzard-context worktree>   # resolve via the workspace's `# Winter Extensions` block
  ```

  This is a rule rather than a note because four of five plan rounds on issue #149 died on exactly this miss, before the
  plan node derived the fix — this grep — unaided.
- **A case pins what its own name claims (`bzh:case-pins-its-own-name`, issue #275).** A test whose body matches a
  sibling's asserts only what the sibling already asserts, so its name is a claim nothing observes and the behavior that
  name promises goes unpinned — the shape that left `enable`'s idempotence and the plain closed-lease case uncovered
  while both read as covered. `tests/test_no_duplicate_test_bodies.py` fails on any two cases sharing a body (module
  constants folded into the key, so two files reading their own same-named constant are not duplicates); a deliberate
  cross-tier re-run is declared there rather than tolerated. The companion habits are the same sweep's other two shapes:
  a negative assertion is worth only the window it is made over (a fixed sleep shorter than the subject's own cadence
  proves nothing), and a guard test that passes with its guard deleted is not a guard — mutate to find out, per
  `bzh:mutation-review-selection`.
- **A production path the gate never drives is unpinned, whatever the upper tiers show
  (`bzh:gating-tier-pins-production-paths`, issue #276).** `blizzard:e2e` and `blizzard:journey` gate no PR and no push,
  so a path covered only there can be deleted with every merge gate green — and a config key read from the operator's
  toml and dropped before its consumer changes nothing *any* tier can see. Where production takes route A and the gating
  tests drive a test-convenient route B, extend a gating case onto route A rather than trusting the upper tier.
  `tests/test_config_keys_reach_a_gating_tier.py` is the floor for the config-key half — every key of every
  operator-written config dataclass, nested blocks included, must be named by a gating-tier test
  ([the guard's own inventory](./commands.md#blizzardunit-test)) — and it is only a floor: naming a key is weaker than
  pinning its threading, which `tests/test_runner_loop_build.py` does case by case for the keys it covers.
