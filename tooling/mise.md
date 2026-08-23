# mise (`bzh:mise`)

`blizzard` and `blizzard-mock` each carry a `mise.toml` at the repo root that pins the toolchain and declares every
routine command as a named task. Tasks are repo-local and every mise command runs from that repo's root; there is no
workspace-level mise surface, and `blizzard-context` and `blizzard-discovery` carry none.

- `mise tasks` lists a repo's tasks.
- `mise run <task>` runs one task.

When mise reports a fresh worktree's config untrusted, run `mise trust` once in that repo root.

What a verification task asserts, and its stable method id, is owned by
[`../verification/blizzard.md`](../verification/blizzard.md). The mapping from tasks to the remote CI gates is owned by
the `blizzard` repo's `docs/ci.md`.
