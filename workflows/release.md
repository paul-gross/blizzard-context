# Release (`bzh:release`)

**Rule.** Cut a blizzard release by pushing a `v*` tag at a proven-green `master` tip — pushing the tag *is* the release, and no other path publishes a build.

**Why.** The branch-and-release model is trunk-based with milestones as tags: the tag triggers the `release` workflow, which runs the full verification suite, builds the wheel with the embedded frontend, and publishes it as a GitHub Release — so the sequence below is the whole ceremony.

## The sequence

1. **Confirm `master` is green.** The `push`-workflow run for the tip you will tag passed (`blizzard:ci`, [../verification/blizzard.md](../verification/blizzard.md)), and your worktree sits at exactly that commit — nothing local, nothing unpushed.
2. **Rehearse the release-only and local-only tiers.** The tag run is the only remote execution of the e2e tier and the FULL crash sweep (`blizzard:e2e`, `blizzard:crash-sweep`) — run them locally first so the tag build is never the first execution of either. Run the capstone journey (`blizzard:journey`) too: no CI workflow runs it, so this rehearsal is its only pre-release execution.
3. **Pick the version.** `0.<milestone>.<patch>` pre-1.0, candidates as `-rc.N`; the tag is the version prefixed with `v`. That is the whole policy — this step owns it.
4. **Tag and push the tag.**

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

5. **Watch the release run and verify the publish.** Watch the `release.yml` run to green (`blizzard:ci`), then confirm the GitHub Release exists with the wheel attached: `gh release view v0.1.0 --repo paul-gross/blizzard`. Also confirm the published image: `docker pull ghcr.io/paul-gross/blizzard-hub:v0.1.0` succeeds **anonymously** (no `docker login`) — the GHCR push has no local method (no `docker buildx` on the dev machine), so this pull is the only proof it worked, and package visibility is a one-time repo setting a workflow can't assert (`docs/ci.md`'s "The image publish" section).
6. **Repair forward.** A red release run is fixed on `master` and cut again as the next tag (`-rc.N+1`, or the next patch) — a pushed tag is immutable.

**Gap.** No `v*` tag has yet exercised the `release` workflow end to end (the matrix names this open piece — [../verification/blizzard.md](../verification/blizzard.md)); the first cut also verifies the release pipeline itself, so shepherd it rather than fire-and-forget.

## Don't

- Tag a commit whose `push`-workflow run isn't green, or tag from a worktree ahead of or behind `origin/master` — the tag must name a state the remote gate already proved.
- Skip the local rehearsal and let the tag run be the first execution of a release-only tier.
- Re-point, delete, or reuse a tag after a failed run — the next tag is the fix.
- Publish a wheel by hand (uploading an artifact, editing a Release) — a build no tag produced is a build no gate proved.

## See also

- [./feature-delivery.md](./feature-delivery.md) — how the green `master` this sequence starts from is produced.
- The `blizzard` repo's `docs/ci.md` — the in-repo operator reference for the workflows the tag triggers and the `gh run` commands to watch them.
