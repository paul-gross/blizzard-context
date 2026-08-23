# Worker boundary

This spoke owns the runner–worker boundary — the spawned child's environment, and git mutation; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Child environments come from an allowlist (`bzh:worker-env-allowlist`)

**Rule.** Build a worker, judge, or resume child environment from an explicit allowlist — a fixed base set, plus
deliberate additions such as locale variables, plus the operator's declared passthrough — never from a full copy of the
daemon's own `os.environ`.

**Why.** The runner holds daemon credentials (a hub bearer token, forge tokens) that a copied parent environment would
carry into every child, where a still-untrusted harness prompt or transcript can leak them. An allowlist makes a
credential's absence structural rather than something a filter must remember to strip.

**Scope.** Governs child-environment construction on the runner side of the harness seam (`bzh:pluggable-seams`); it
does not bound what a harness binary may read from its own environment once launched.

**Detect.** `os.environ`, `env=None`, or an omitted `env=` (all inherit the parent) passed to a subprocess call
launching a worker, judge, or resume harness process instead of going through the one allowlist-building owner.

**Do.** `AllowlistedEnv` in `src/blizzard/runner/harness/env_allowlist.py` builds every child env as the base allowlist
plus `LC_*` plus `env_passthrough`, with identity variables (`BLIZZARD_LEASE_ID`, …) added explicitly per spawn.

**Don't.** `env=os.environ`, or a bare `env=dict(os.environ)` — either hands the child `BZ_HUB_TOKEN` and every other
daemon secret.

## Only the worker mutates git (`bzh:git-write-in-worker-seam`)

**Rule.** Only the worker mutates git — it commits its work and pushes its branch — and the runner's git surface is
read-only: the worker declares what it pushed (env, repo, branch, commit) through the runner's local declaration
channel, and the runner's read-only verification is what turns that declaration into a submitted artifact.

**Why.** The runner cannot know what a worker's turn produced without blind trust or inference from git residue, and
residue is lossy — a detached worktree's `git rev-parse --abbrev-ref HEAD` returns the literal string `HEAD`, so a
runner that both infers and pushes wedges on a branch named `HEAD`. The split means the runner neither fabricates a
pointer from residue nor merely trusts an unverified claim.

**Scope.** Governs the runner's `IWorktreeGit` seam (`src/blizzard/runner/loop/worktree.py`) and its ADVANCE collection
step; the runner still holds the only credentialed copy of the leased environment — only the git mutation within it
belongs to the worker.

**Detect.** A runner-side `git push` or `git commit`, or any runner git call resolving which branch or commit to act on
from repository state rather than from the worker's declaration through the local API.

**Do.** The worker pushes its branch and declares it with
`blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>`, and the runner's
`IWorktreeGit.verify(origin_url, branch, commit)` confirms it via `git ls-remote` — consulting no working directory —
before submitting the `GIT_COMMIT` artifact. The `origin_url` comes from the environment's repo manifest, owned by the
workspace provider (`IWorkspaceProvider.repos`), never from the worker.

**Don't.** Derive a repo's origin from the calling process's cwd — the same lossy-residue mistake: workers are spawned
at the workspace root, so `git remote get-url origin` there walks up past the environment and returns the enclosing
workspace repo for every repo alike, a plausible wrong value rather than an error. Look a fact up where it is owned
instead of inferring it from ambient state.
