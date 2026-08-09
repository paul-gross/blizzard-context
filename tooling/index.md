# Tooling

The external tools a blizzard agent drives beyond the winter CLI, and the surface that owns each one.
The winter CLI itself is workspace-owned (`workspace:/context/winter-cli/index.md`) and is not re-routed here.

Parent: [../index.md](../index.md).

| Tool surface | When to read |
|--------------|--------------|
| [./mise.md](./mise.md) | Running a repo task or discovering a code repo's command surface — the `mise` front door `blizzard` and `blizzard-mock` share |
| [./store-seeding.md](./store-seeding.md) | Seeding a hub/runner store to develop or demo the board against — the direct `blizzard-mock-data` path (recommended) and the real work-source/ingest wire path, and when to reach for each |
| [../verification/blizzard.md#tools](../verification/blizzard.md#tools) | Standing up the scenario a verification needs — the setup tools the matrix owns |
| The `blizzard` repo's `docs/ci.md` | Watching or debugging a GitHub Actions run with `gh` — the in-repo operator reference for the `gh run` commands |
| `winter-github:/context/gh-cli.md#viewing-an-existing-issue` | Reading a blizzard issue with `gh` before implementing it — a bare `gh issue view <N>` exits 1 here on `GraphQL: Projects (classic) is being deprecated … repository.issue.projectCards`, the one symptom that section's `--json` form is the cure for |
| `winter-github:/index.md` | Filing or refining a GitHub issue with `gh` — the issue skills and conventions |
