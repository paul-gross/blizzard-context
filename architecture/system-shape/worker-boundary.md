# The runner–worker boundary

What the runner may hand a worker, and what only the worker may do: the environment a spawned child is built from, and
the git mutation that lives on the worker's side of the harness seam. [`../system-shape.md`](../system-shape.md) owns
the macro-shape invariants these two rules sit under, and each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Worker environments are allowlisted, never inherited (`bzh:worker-env-allowlist`)

**Rule.** A worker/judge/resume child environment is built from an explicit allowlist — a fixed base set plus deliberate
additions (locale variables) plus the operator's declared passthrough — never from a full copy of the daemon's own
`os.environ`.

**Why.** The runner process holds daemon credentials (a hub bearer token, forge tokens); a child built by copying the
parent environment carries any such secret into every worker/judge/resume invocation by default, where a still-untrusted
harness prompt or transcript can leak it. Building the child from an allowlist makes a daemon credential's absence
structural rather than a property some filter has to remember to apply.

**Scope.** Governs the spawn/judge/resume environment construction on the runner side of the harness seam
(`bzh:pluggable-seams`); it does not bound what a harness binary itself may read from its own process environment once
launched.

**Detect.** `os.environ` (or `env=None`/omitted `env=`, which inherits the parent) passed directly into a `subprocess`
call that launches a worker, judge, or resume harness process, rather than through the one allowlist-building function.

**Do.** `_allowlisted_env(passthrough)` in `blizzard/runner/harness/internal/claude_code_adapter.py` builds every child
env from the base allowlist + `LC_*` + `env_passthrough`; identity variables (`BLIZZARD_LEASE_ID`, …) are then added
explicitly per spawn.

**Don't.** `subprocess.Popen(cmd, env=os.environ)` (or a bare `env=dict(os.environ)`) handed to a worker launch — the
child now inherits `BZ_HUB_TOKEN` and every other daemon secret by accident.

## Git mutation lives in the worker seam (`bzh:git-write-in-worker-seam`)

**Rule.** Only the worker mutates git — it commits its work and pushes its branch. The runner's own git surface is
**read-only**: it confirms what the worker declared (`git ls-remote` against the origin the environment's repo manifest
names), it never commits and never pushes. The worker declares what it pushed — `(env, repo, branch, commit)`, through
the runner's local declaration channel — and the runner's read-only verify is what turns that declaration into a
submitted artifact.

**Why.** The runner is the deterministic shell (`bzh:deterministic-shell`) and holds the only credentialed copy of the
leased environment, but it cannot know what a worker's turn actually produced without either trusting the worker's
say-so blindly or **inferring** it from git residue — and residue is lossy: a detached worktree's
`git rev-parse --abbrev-ref HEAD` returns the literal string `HEAD`, which a runner that both infers *and* pushes turns
into a wedge the instant it tries to push a branch named `HEAD`. Splitting the two roles — the worker states a fact
about what it did, the runner independently confirms that fact against the forge it can already see — gets both
properties at once: the runner never fabricates a pointer from ambiguous residue, and it never merely trusts an
unverified claim either.

**Scope.** Governs the runner's `IWorktreeGit` seam (`runner/loop/worktree.py`) and its ADVANCE collection step. The
runner still holds the only credentialed copy of the leased environment; it is only the git mutation *within* that
environment that moves to the worker.

**Detect.** A runner-side `git push`, `git commit`, or any git call that resolves *which* branch/commit to act on from
repository state (`git rev-parse --abbrev-ref HEAD`, "HEAD is ahead of base") rather than from a declaration the worker
made through the local API.

**Do.** The worker pushes its branch, then declares it —
`blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>` — and the runner's
`IWorktreeGit.verify(origin_url, branch, commit)` confirms it read-only (`git ls-remote`, no working directory
consulted) before submitting the `GIT_COMMIT` artifact. The `origin_url` comes from the environment's repo manifest,
which the workspace provider owns (`IWorkspaceProvider.repos`), never from the worker and never from whatever directory
the caller happens to stand in.

**Don't (the second inference).** Deriving a repo's origin from the *caller's* cwd rather than from the manifest. The
verb once defaulted `--forge` to `git remote get-url origin` in the worker's process cwd; workers are spawned at the
workspace root, so git walked up past the environment and returned the enclosing workspace repo for every repo alike — a
plausible-looking wrong value rather than an error, which failed the comparison and dropped every declaration. Reading
`origin` from a directory nobody chose is the same lossy-residue mistake as reading `HEAD` from one, and the fix is the
same shape: look the fact up where it is owned instead of inferring it from ambient state.

**Don't.** A runner step that walks the leased environment's repo worktrees looking for one whose `HEAD` is ahead of the
base branch and pushes whatever it finds — inference from residue this shape avoids.
