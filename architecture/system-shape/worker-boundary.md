# Worker boundary

This spoke owns the runner–worker boundary — every child the runner launches, its environment, and git mutation; the
macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Child environments come from an allowlist (`bzh:worker-env-allowlist`)

**Rule.** Build the environment of every child the runner launches from an explicit allowlist — a fixed base set, plus
deliberate additions such as locale variables, plus the operator's declared passthrough — never from a full copy of the
daemon's own `os.environ`. A tool child (`git`, `winter`, a version probe, a check command) takes the tool profile; a
worker, judge, or resume child takes the worker profile, which adds the per-spawn identity.

**Why.** The runner holds daemon credentials (a hub bearer token, forge tokens) that a copied parent environment would
carry into every child, where a still-untrusted harness prompt, transcript, or check command can leak them. An allowlist
makes a credential's absence structural rather than something a filter must remember to strip.

**Scope.** Governs child-environment construction for every child the runner launches, on the runner side of the harness
seam (`bzh:pluggable-seams`); it does not bound what a harness binary may read from its own environment once launched.
The one exception is takeover's foreground child (`src/blizzard/runner/cli/control.py`): it runs in the operator's
terminal, so its base is the operator's shell layered with the takeover env.

**Detect.** `os.environ`, `env=None`, or an omitted `env=` (all inherit the parent) reaching a child launch instead of
an `AllowlistedEnv` profile; the launch seam's `env` parameter takes only a profile value and has no default, so pyright
(`blizzard:typecheck`) refuses a bare mapping.

**Do.** `AllowlistedEnv` in `src/blizzard/runner/process/child_env.py` builds both profiles. `tool()` is the base
allowlist plus `LC_*` plus `env_passthrough`, with `PATH` led by `[worker] path_prepend`'s configured directories ahead
of the daemon's own; `worker(identity)` is the tool profile plus the per-spawn identity variables (`BLIZZARD_LEASE_ID`,
the lease token, the scratch dir, the tracing exporter). Any other per-launch variable is an explicit `adding(...)` on
the profile value. A tool that needs a daemon variable is named in `env_passthrough`.

**Don't.** `env=os.environ`, or a bare `env=dict(os.environ)` — either hands the child the per-runner token
(`BZ_HUB_TOKEN_<NAME>`) and every other daemon secret. Don't give a tool child the worker profile: it carries the lease
token a tool has no use for.

## Every child launches through one seam (`bzh:runner-child-launch`)

**Rule.** Every child the runner launches goes through the `IChildProcesses` seam in `runner/process`, which gives the
child its own process group, kills the whole group on timeout, and closes stdin unless input is given. A
run-to-completion launch takes a required timeout.

**Why.** A child killed alone leaves its grandchildren running — a `sh -c` check command's forked `sleep` outlives the
shell — and a child holding inherited stdin can block on the daemon's terminal. Either wedges a tick
(`bzh:deterministic-shell`). One seam makes the group, the kill, and the closed stdin structural rather than a
per-call-site flag to remember.

**Scope.** Governs every `subprocess` and `pty` launch under `src/blizzard/runner/**` and `src/blizzard/foundation/**`;
the hub's one sanctioned launch site is `hub/delivery/internal/hub_command_runner.py`. Takeover's foreground child is
the one exception to the group and the timeout: it still goes through the seam's foreground entry, but runs with no new
group and no timeout, because an interactive child must keep the terminal's foreground group.

**Detect.** `bzh:runner-child-launch` is tooled by `blizzard:structural-gate`'s ast-grep scan
(`contracts/ast-grep/rules/runner-child-launch.yml`), which refuses `import subprocess`, `from subprocess import …`, and
`import pty` outside `runner/process/**`, the hub's sanctioned site, and the colocated migration tests
(`bzh:colocated-migration-tests`). `tests/test_tick_subprocess_timeouts.py` (`blizzard:unit-test`) pins that the seam's
run-to-completion timeout is required and non-optional.

**Do.** Take `IChildProcesses` by injection, bound in the runner composition roots, and its driver
(`src/blizzard/runner/process/internal/subprocess_child_processes.py`) is the only module that imports `subprocess` and
`pty`. Read a timeout from the seam's `ChildRun` result value, not from a caught exception. Stop a long-lived child
through the group helpers in `src/blizzard/runner/process/groups.py`.

**Don't.** Import `subprocess` in an adapter for its `DEVNULL` constant — the seam's `Stream` carries the stream
constants. Don't call `proc.kill()` on a timed-out child alone.

## Only the worker mutates git (`bzh:git-write-in-worker-seam`)

**Rule.** Only the worker mutates git — it commits its work and pushes its branch — and the runner's git surface is
read-only: the worker declares what it pushed (env, repo, branch, commit) through the runner's local declaration
channel, and the runner's read-only verification is what turns that declaration into a submitted artifact.

**Why.** The runner cannot know what a worker's turn produced without blind trust or inference from git residue, and
residue is lossy — a detached worktree's `git rev-parse --abbrev-ref HEAD` returns the literal string `HEAD`, so a
runner that both infers and pushes wedges on a branch named `HEAD`. The split means the runner neither fabricates a
pointer from residue nor merely trusts an unverified claim.

**Scope.** Governs the runner's `IWorktreeGit` seam (`src/blizzard/runner/environments/worktree.py`) and its ADVANCE
collection step; the runner still holds the only credentialed copy of the leased environment — only the git mutation
within it belongs to the worker.

**Detect.** A runner-side `git push` or `git commit`, or any runner git call resolving which branch or commit to act on
from repository state rather than from the worker's declaration through the local API.

**Do.** The worker pushes its branch and declares it with
`blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>`, and the runner's
`IWorktreeGit.verify(origin_url, branch, commit)` confirms it via `git ls-remote` — consulting no working directory —
before submitting the `GIT_COMMIT` artifact. The `origin_url` comes from the environment's repo manifest, owned by the
workspace provider (`IWorkspaceProvider.repos`), never from the worker.

**Don't.** Derive a repo's origin from the calling process's cwd — the same lossy-residue mistake: workers are spawned
where the workspace provider says (`IWorkspaceProvider.spawn_root`) — under winter, the workspace root — so
`git remote get-url origin` there walks up past the environment and returns the enclosing workspace repo for every repo
alike, a plausible wrong value rather than an error. Look a fact up where it is owned instead of inferring it from
ambient state.
