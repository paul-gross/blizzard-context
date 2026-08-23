# Cutting a release (`bzh:release`)

**Rule.** A blizzard release is cut by pushing a `v*` tag at a proven-green `master` tip — the tag is itself the
release, and no other path publishes a release build.

**Why.** Development is trunk-based with milestones as tags: a `master` push publishes only dogfood artifacts — the dev
wheel and the `edge` / `sha-<full-git-sha>` image channel — while version tags move only on a release tag and `latest`
only on a stable one.

## Before tagging

- Pick the version from the `blizzard` repo's `docs/versioning.md` — it solely owns the version scheme, what counts as
  breaking, and the supported hub↔runner skew; pick there, never restate it.
- Run `blizzard:e2e` and `blizzard:crash-sweep` locally — the tag run is the only remote execution of the e2e tier and
  the FULL crash sweep, so the tag build must never be their first execution.
- Rehearse `blizzard:journey`, the capstone journey — no CI workflow runs it, so the rehearsal is its only pre-release
  execution.
- Run the local-only `blizzard:image-smoke` and `blizzard:compose-smoke` — nothing in CI ever boots the image it
  publishes, so they are its only pre-publish runtime proof.
- Bump `pyproject.toml`'s `[project] version` in a release-prep commit pushed to `master` — the release job asserts that
  tag and value agree (`scripts/check-version-tag.sh`), failing before anything is built.
- Tag only a state the remote gate already proved: the tip's `push`-workflow run is green (`blizzard:ci`,
  [../verification/blizzard.md](../verification/blizzard.md)) and the worktree sits at exactly that commit — nothing
  local or unpushed.

## Tag and watch

The tag names exactly the bumped version:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The `v*` tag triggers the `release` workflow: the full verification suite, the wheel built with the embedded frontend, a
multi-arch hub image pushed to GHCR, and a GitHub Release with the wheel attached.

## Confirm the cut

- Watch the `release.yml` run to green (`blizzard:ci`), then confirm the Release and its attached wheel:
  `gh release view v0.1.0 --repo paul-gross/blizzard`.
- Confirm the image with an anonymous `docker pull ghcr.io/paul-gross/blizzard-hub:0.1.0` — the GHCR push has no local
  proof, and package visibility is a one-time repo setting no workflow can assert — see `docs/ci.md` §The image publish
  (tag `release` only): a documented gap proven by each real cut, never invented around.
- The generated notes (`scripts/release-notes.sh`) always hold a placeholder **Upgrade notes** heading after any
  **Breaking changes**; when the release asks something of the operator (`docs/versioning.md` names what counts),
  replace it with real prose — `gh release edit v0.1.0 --repo paul-gross/blizzard --notes-file <edited-notes.md>`, or
  the web UI.

## A red run

Repair forward: fix on `master` and cut the next tag (`-rc.N+1`, or the next patch). A pushed tag is immutable — never
re-pointed, deleted, or reused.

**Don't.** Publish a wheel or image by hand — a build no tag produced is a build no gate proved.

**See also.** The `blizzard` repo's `docs/ci.md` — the operator reference for the triggered workflows and the `gh run`
watch commands.
