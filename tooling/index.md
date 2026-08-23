# Tooling

This file routes to the surface owning each external tool a blizzard agent drives beyond the winter CLI. The winter CLI
itself is workspace-owned at `workspace:/context/winter-cli/index.md` and is not re-routed here. The parent hub is
[`../index.md`](../index.md).

| Surface                                                                  | Read when…                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`./mise.md`](./mise.md)                                                 | You are running a repo task or discovering a code repo's command surface — the `mise` front door `blizzard` and `blizzard-mock` share                                                                                        |
| [`./store-seeding.md`](./store-seeding.md)                               | You are seeding a hub or runner store to develop or demo the board against, and choosing which seeding path the task calls for                                                                                               |
| [`../verification/blizzard.md#tools`](../verification/blizzard.md#tools) | You are standing up the scenario a verification needs — the setup tools the matrix owns                                                                                                                                      |
| `winter-github:/index.md`                                                | You are filing or refining a GitHub issue with `gh` — the issue skills and conventions                                                                                                                                       |
| `winter-github:/context/gh-cli.md#viewing-an-existing-issue`             | You are reading a blizzard issue with `gh`: a bare `gh issue view <N>` exits 1 here on `GraphQL: Projects (classic) is being deprecated … repository.issue.projectCards`, the one symptom that section's `--json` form cures |
| The `blizzard` repo's `docs/ci.md`                                       | You are watching or debugging a GitHub Actions run with `gh` — the in-repo operator reference for the `gh run` commands                                                                                                      |
