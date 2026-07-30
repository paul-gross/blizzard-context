# Release (`bzh:release`)

**Rule.** Cut a blizzard release by pushing a `v*` tag at a proven-green `master` tip — pushing the tag *is* the release, and no other path publishes a *release* build. A `master` push does publish dogfood artifacts (the dev wheel, and the `edge` / `sha-*` image channel), but never a release: the version tags and `latest` move only here.

**Why.** The branch-and-release model is trunk-based with milestones as tags: the tag triggers the `release` workflow, which runs the full verification suite, builds the wheel with the embedded frontend, builds and pushes a multi-arch hub container image to GHCR, and publishes a GitHub Release with the wheel attached — so the sequence below is the whole ceremony.

## The sequence

1. **Confirm `master` is green.** The `push`-workflow run for the tip you will tag passed (`blizzard:ci`, [../verification/blizzard.md](../verification/blizzard.md)), and your worktree sits at exactly that commit — nothing local, nothing unpushed.
2. **Rehearse the release-only and local-only tiers.** The tag run is the only remote execution of the e2e tier and the FULL crash sweep (`blizzard:e2e`, `blizzard:crash-sweep`) — run them locally first so the tag build is never the first execution of either. Run the capstone journey (`blizzard:journey`) too: no CI workflow runs it, so this rehearsal is its only pre-release execution. Also run `blizzard:image-smoke` and `blizzard:compose-smoke` — both are **local-only**. Every `master` push now builds and pushes the same multi-arch image from the same Dockerfile, so the tag run's image *build* is continuously rehearsed and a build-level break surfaces long before the tag; but nothing in CI ever *boots* the image it publishes, so these two remain the only proof it runs, and this step is still the image's only pre-publish runtime check.
3. **Pick the version and bump `pyproject.toml`.** The scheme, what counts as breaking, and the supported hub↔runner skew are the `blizzard` repo's `docs/versioning.md` — the single owner, not restated here. Bump `pyproject.toml`'s `[project] version` to the chosen version in a release-prep commit, pushed to `master` **before** tagging: the `release` job's first step (after the `gate` suite it `needs:`) asserts the tag and this value agree (`scripts/check-version-tag.sh`) and fails before building anything if they don't.
4. **Tag and push the tag.** The tag names exactly the version just bumped to.

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

5. **Watch the release run and verify the publish.** Watch the `release.yml` run to green (`blizzard:ci`), then confirm the GitHub Release exists with the wheel attached: `gh release view v0.1.0 --repo paul-gross/blizzard`. Also confirm the published image: `docker pull ghcr.io/paul-gross/blizzard-hub:v0.1.0` succeeds **anonymously** (no `docker login`) — the GHCR push has no local method (no `docker buildx` on the dev machine), so this pull is the only proof it worked, and package visibility is a one-time repo setting a workflow can't assert (`docs/ci.md`'s "The image publish" section).
6. **Write the Upgrade notes, when this release asks something of the operator.** The generated release notes (`scripts/release-notes.sh`) always carry a placeholder **Upgrade notes** heading, after any **Breaking changes** section. Whenever this release asks something of the operator (`docs/versioning.md` names what counts), replace the placeholder with real prose: `gh release edit v0.1.0 --repo paul-gross/blizzard --notes-file <edited-notes.md>` (or the web UI). Skip this step when the release asks nothing of the operator.
7. **Repair forward.** A red release run is fixed on `master` and cut again as the next tag (`-rc.N+1`, or the next patch) — a pushed tag is immutable.

**Gap.** No `v*` tag has yet exercised the `release` workflow end to end (the matrix names this open piece — [../verification/blizzard.md](../verification/blizzard.md)); the first cut also verifies the release pipeline itself, so shepherd it rather than fire-and-forget.

## Don't

- Tag a commit whose `push`-workflow run isn't green, or tag from a worktree ahead of or behind `origin/master` — the tag must name a state the remote gate already proved.
- Skip the local rehearsal and let the tag run be the first execution of a release-only tier.
- Re-point, delete, or reuse a tag after a failed run — the next tag is the fix.
- Publish a wheel or image by hand (uploading an artifact, hand-crafting a Release) — a build no tag produced is a build no gate proved. (Editing a *published* Release's notes to fill in step 6's Upgrade notes is not this — the build itself is untouched.)

## See also

- [./feature-delivery.md](./feature-delivery.md) — how the green `master` this sequence starts from is produced.
- The `blizzard` repo's `docs/ci.md` — the in-repo operator reference for the workflows the tag triggers and the `gh run` commands to watch them.
- The `blizzard` repo's `docs/versioning.md` — the versioning scheme, what counts as breaking, and the supported hub↔runner skew, owned there and only linked here.
