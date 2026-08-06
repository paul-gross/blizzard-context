# Verifiability matrix

The verification methods available for blizzard-context itself — how a change to this repo's own conventions, routing, or prose is verified. Shape per `winter-canon:/verifiability-matrix.md` (`canon:verifiability-matrix`).

## Commands

Run from the repo root.

| Method | Command |
|--------|---------|
| `blizzard-context:registry-drift` | `python3 scripts/check-registry-drift.py --blizzard ../blizzard --blizzard-mock ../blizzard-mock --gate` — local-only: needs the sibling `blizzard` checkout (with its `.venv`) and `blizzard-mock` checkout, which a feature env satisfies and a standalone `.winter/ext/context/` install does not; `--gate` refuses a green on any skipped check, not only a `fail`. |
| `blizzard-context:registry-drift-tests` | `python3 tests/test_check_registry_drift.py` — exercises every check against stdlib-only fixtures, needing no blizzard checkout. Mirrors `winter-workflow:lint-tests`. |

## Manual testing

### blizzard-context:manual-reference-check — by-hand reference and routing pass

The by-hand pre-push pass [CONTRIBUTING.md](./CONTRIBUTING.md) §Pre-push expectations already requires. Surface: every `blizzard-context:` / `winter-canon:` / `workspace:` notation and every relative link in the changed files. Pass: each resolves to a file with the claimed shape, every cited `bzh:` id is defined, and every new or moved leaf has a row in its nearest hub. Carries the standing **Gap** that no automated markdown lint — path-notation, routing-reference, anchor checks — ships in this repo.

### blizzard-context:manual-cold-eval — cold-spawn behavioral eval

The cold-spawn behavioral eval `canon:cold-eval` owes for a rule addition, trigger broadening, or routing change. Setup: a fresh subagent given only the cue and the production discovery chain. Steps: declare each behavioral expectation as a scenario; spawn; record `reached` and `behaved` per scenario. Pass: every declared expectation both reached and behaved. A copyedit that changes no claim owes nothing; only a session that can spawn cold subagents may run it, and a non-spawning agent hands it up.

## Tools

`tool:eval-fixture` — a scratch directory of freshly written fixture prose exhibiting the anti-pattern under test, created under the session scratchpad, never by copying a convention's own examples.
