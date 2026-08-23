# Verifiability matrix — blizzard-context

This file inventories the verification methods a change to blizzard-context's own conventions, routing, or prose is
verified by. This document's shape conforms to `winter-canon:/verifiability-matrix.md` (`canon:verifiability-matrix`).

## Commands

Every command method below runs from the repo root.

| Method                                  | Command                                                                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `blizzard-context:markdown-format`      | `dprint check`                                                                                           |
| `blizzard-context:markdown-lint`        | `rumdl check .`                                                                                          |
| `blizzard-context:registry-drift`       | `python3 scripts/check-registry-drift.py --blizzard ../blizzard --blizzard-mock ../blizzard-mock --gate` |
| `blizzard-context:registry-drift-tests` | `python3 tests/test_check_registry_drift.py`                                                             |
| `blizzard-context:lint-script-tests`    | `python3 tests/test_lint_markdown_style.py`                                                              |

`blizzard-context:markdown-format` is the format gate `dprint.json` declares; `dprint fmt` writes the fix, and both
forms need the `dprint` binary on `PATH`. `blizzard-context:markdown-lint` is the structural markdown lint `.rumdl.toml`
declares; `rumdl check . --fix` applies the autofixable subset, and both need the `rumdl` binary on `PATH`.

Passing `--gate` to the registry-drift check refuses a green on any skipped check, not only on a `fail`.
`blizzard-context:registry-drift` is local-only: it needs the sibling `blizzard` checkout with its `.venv` and the
sibling `blizzard-mock` checkout, which a feature env supplies and a standalone `.winter/ext/context/` install does not.
`blizzard-context:registry-drift-tests` exercises every check against stdlib-only fixtures and needs no blizzard
checkout.

`blizzard-context:lint-script-tests` exercises the `winter lint` check this extension contributes
(`scripts/lint-markdown-style.py`, wired through `winter-ext.toml`'s `lint` field) against stubbed binaries, so neither
tool need be installed.

## Manual testing

### `blizzard-context:manual-reference-check`

A by-hand reference and routing pass over the changed files. The surface it covers is every `blizzard-context:` /
`winter-canon:` / `workspace:` path notation, every code pointer in `bzh:one-prose-home`'s Pointer forms, every relative
link, every inbound public URL naming a file here, and every registry count or enumeration the changed files state. The
inbound URLs are on that list because a published surface points at this repo by URL, so renaming a heading here breaks
a document this repo cannot see.

It passes when each reference resolves to a file with the claimed shape and anchor, every cited `bzh:` id is defined,
every new or moved leaf has a hub row and every repointed or deleted row lands in the same change
(`winter-canon:/progressive-disclosure.md`, `canon:index-scrutiny`), and each stated registry count or enumeration is
either reached by check F or dispositioned by hand against its named owner.

**Gap.** No automated path-notation, routing-reference, or anchor check ships in this repo.

**Gap.** Check F's residual classes, enumerated by `scripts/check-registry-drift.py`'s own Declared limitations block,
reach into the `blizzard/` and `blizzard-mock/` trees no method covers and this by-hand pass does not open.

**Gap.** Check F's sibling-repo half has no trigger where its sites live — the census declares sites in `blizzard/` and
`blizzard-mock/`, yet neither repo runs the check, so those sites are swept only when blizzard-context itself changes.

### `blizzard-context:manual-cold-eval`

The cold-spawn behavioral eval `canon:cold-eval` owes for a rule addition, a trigger broadening, or a routing change. A
copyedit that changes no claim owes no cold eval.

Set the eval up by giving a fresh subagent only the cue and the production discovery chain. It declares each behavioral
expectation as a scenario, spawns, and records `reached` and `behaved` per scenario; it passes when every expectation is
both. An agent whose session cannot spawn cold subagents hands this method up rather than running it.

## Tools

### `tool:eval-fixture`

Create a scratch directory under the session scratchpad and write into it fresh fixture prose exhibiting the
anti-pattern under test — never a copy of a convention's own examples.
