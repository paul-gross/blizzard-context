# Verifiability matrix

The verification methods available for blizzard-context itself — how a change to this repo's own conventions, routing,
or prose is verified. Shape per `winter-canon:/verifiability-matrix.md` (`canon:verifiability-matrix`).

## Commands

Run from the repo root.

| Method                                  | Command                                                                                                                                                                                                                                                                                                                                                                 |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `blizzard-context:registry-drift`       | `python3 scripts/check-registry-drift.py --blizzard ../blizzard --blizzard-mock ../blizzard-mock --gate` — local-only: needs the sibling `blizzard` checkout (with its `.venv`) and `blizzard-mock` checkout, which a feature env satisfies and a standalone `.winter/ext/context/` install does not; `--gate` refuses a green on any skipped check, not only a `fail`. |
| `blizzard-context:registry-drift-tests` | `python3 tests/test_check_registry_drift.py` — exercises every check against stdlib-only fixtures, needing no blizzard checkout. Mirrors `winter-workflow:lint-tests`.                                                                                                                                                                                                  |
| `blizzard-context:markdown-format`      | `dprint check` — every markdown file matches the format `dprint.json` declares; `dprint fmt` writes the fix. Needs the `dprint` binary on `PATH`.                                                                                                                                                                                                                       |
| `blizzard-context:markdown-lint`        | `rumdl check .` — the structural markdown lint `.rumdl.toml` declares; `rumdl check . --fix` applies the autofixable subset. Needs the `rumdl` binary on `PATH`.                                                                                                                                                                                                        |

## Manual testing

### blizzard-context:manual-reference-check — by-hand reference and routing pass

The by-hand pre-push pass [CONTRIBUTING.md](./CONTRIBUTING.md) §Pre-push expectations already requires. Surface: every
`blizzard-context:` / `winter-canon:` / `workspace:` notation, every repo-root-relative or repo-qualified code pointer
(`bzh:one-prose-home`'s Pointer forms), every relative link, every inbound public URL naming a file in this repo — its
target file and, where given, its heading anchor — and every registry count or enumeration the changed files state.
Pass: each resolves to a file with the claimed shape, every cited `bzh:` id is defined, every new or moved leaf has a
row in its nearest hub with any repointed or deleted row landing in the same change
(`winter-canon:/progressive-disclosure.md`, `canon:index-scrutiny`), and each registry count or enumeration a changed
file states is either reached by check F or dispositioned here by hand against the owner it names. The inbound-URL half
is the price of `bzh:one-prose-home`'s published-surface form: a published surface points at this repo by URL, so
renaming a heading here breaks a document this repo cannot see.

Carries the standing **Gap** that check F's declared residuals — the classes `scripts/check-registry-drift.py`'s own
Declared limitations block enumerates, which owns that list rather than this row — reach across `blizzard/` and
`blizzard-mock/`, trees this pass does not open and no method covers. Carries the standing **Gap** that check F's
sibling-repo half has **no trigger on the side its sites live**: the census declares sites in `blizzard/` and
`blizzard-mock/`, but neither repo runs this check or names it in any gate, so those sites are swept only when someone
changes *this* repo. A reword there passes that repo's own gate whole and surfaces later, in another repo, to an agent
who never touched the file. Closing it means a trigger in those repos, not a wider sweep here. Carries the standing
**Gap** that no automated reference check — path-notation, routing-reference, anchor checks — ships in this repo.

### blizzard-context:manual-cold-eval — cold-spawn behavioral eval

The cold-spawn behavioral eval `canon:cold-eval` owes for a rule addition, trigger broadening, or routing change. Setup:
a fresh subagent given only the cue and the production discovery chain. Steps: declare each behavioral expectation as a
scenario; spawn; record `reached` and `behaved` per scenario. Pass: every declared expectation both reached and behaved.
A copyedit that changes no claim owes nothing; only a session that can spawn cold subagents may run it, and a
non-spawning agent hands it up.

## Tools

`tool:eval-fixture` — a scratch directory of freshly written fixture prose exhibiting the anti-pattern under test,
created under the session scratchpad, never by copying a convention's own examples.
