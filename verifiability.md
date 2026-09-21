# Verifiability matrix — blizzard-context

This file inventories the verification methods a change to blizzard-context's own conventions, routing, or prose is
verified by. This document's shape conforms to `winter-canon:/verifiability-matrix.md` (`canon:verifiability-matrix`).

## Commands

Every command method below runs from the repo root.

| Method                                  | Command                                                                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `blizzard-context:markdown-format`      | `dprint check`                                                                                           |
| `blizzard-context:markdown-lint`        | `rumdl check .`                                                                                          |
| `blizzard-context:markdown-prose-lint`  | `vale --output=line .`                                                                                   |
| `blizzard-context:registry-drift`       | `python3 scripts/check-registry-drift.py --blizzard ../blizzard --blizzard-mock ../blizzard-mock --gate` |
| `blizzard-context:registry-drift-tests` | `python3 tests/test_check_registry_drift.py`                                                             |
| `blizzard-context:lint-script-tests`    | `python3 tests/test_lint_markdown_style.py`                                                              |
| `blizzard-context:ci-workflows`         | `mise x actionlint@1.7.12 -- actionlint` over `.github/workflows/`                                       |

`blizzard-context:markdown-format` is the format gate `dprint.json` declares; `dprint fmt` writes the fix, and both
forms need the `dprint` binary on `PATH`. `blizzard-context:markdown-lint` is the structural markdown lint `.rumdl.toml`
declares; `rumdl check . --fix` applies the autofixable subset, and both need the `rumdl` binary on `PATH`.
`blizzard-context:markdown-prose-lint` is the process-reference prose gate `.vale.ini` and `styles/Blizzard/` declare;
it needs the `vale` binary on `PATH` (`mise use -g vale`). A document whose subject is the reference notation itself
(`canon:no-process-refs`'s Exception) exempts a site with Vale's own inline marker,
`<!-- vale Blizzard.ProcessReference = NO -->` before the exhibited example and `= YES` after it, rather than a
repo-wide `TokenIgnores` entry.

`.github/workflows/{pr,push}.yml` run `blizzard-context:markdown-format`, `:markdown-lint`, `:markdown-prose-lint`,
`:registry-drift-tests`, and `:lint-script-tests` as the `gate / dprint + rumdl + vale` and
`gate / registry-drift + lint-markdown-style script tests` checks, each tool pinned to an exact version inside the
workflow (no `mise.toml` in this repo — see the Tools note below). Passing `--gate` to the registry-drift check refuses
a green on any skipped check, not only on a `fail`. `blizzard-context:registry-drift` is local-only and **deliberately
excluded from the PR gate**: it needs the sibling `blizzard` checkout with its `.venv` and the sibling `blizzard-mock`
checkout, which a feature env supplies and a single-repo CI runner does not; running it against their `master` would
also redden a PR whenever a chunk changes a citation here together with the sibling repo it cites, before that sibling
half has landed. `blizzard-context:registry-drift-tests` exercises every check against stdlib-only fixtures and needs no
blizzard checkout, so it runs in CI even though `registry-drift` itself does not.

`blizzard-context:lint-script-tests` exercises the `winter lint` check this extension contributes
(`scripts/lint-markdown-style.py`, wired through `winter-ext.toml`'s `lint` field) against stubbed binaries, so none of
the three tools need be installed.

`blizzard-context:ci-workflows` is this repo's own workflow-lint method (no declared method proved a GitHub Actions
workflow file before it). This repo carries no `mise.toml`: it installs into a workspace as `.winter/ext/context/`,
where a mise config would trip the workspace's per-worktree trust prompts, so `dprint`, `rumdl`, `vale`, and
`actionlint` are each installed and pinned inline in the workflow (`mise x <tool>@<version> --`) rather than declared as
`[tools]`.

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

**Gap.** No check reaching into the sibling trees has a trigger where its sites live — check F's census declares sites
in `blizzard/` and `blizzard-mock/`, and check C2's spec roster is bidirectional against `blizzard/`, so a spec added
there owes an edit here. Neither sibling repo runs the check, so those sites are swept only when blizzard-context itself
changes.

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
