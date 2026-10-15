# `blizzard:winter-binding` detail (`bzh:matrix-tier-winter-binding`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The winter-binding spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:winter-binding

The tier command is `BLIZZARD_WINTER_BINDING=1 uv run pytest -m winter_binding tests/winter/`
(`mise run winter-binding`) — the winter workspace provider driven against the real `winter` CLI. It runs locally and
nowhere else, and no CI workflow checks out a winter source. The platform tiers (`blizzard:service-test`,
`blizzard:e2e`, `blizzard:crash-sweep`) run on the built-in `basic` provider over a winter-free fixture, so this tier is
the only place the binding is proven.

It needs the sibling provisioned `blizzard-mock` worktree and a winter source — `$BLIZZARD_MOCK_WINTER_SOURCE`, else the
walk up from the blizzard root, discovered only in `tests/winter/support.py`. Unset `BLIZZARD_WINTER_BINDING` skips
every case with a reason naming it; set but with no source found skips naming `BLIZZARD_MOCK_WINTER_SOURCE`.

- `tests/winter/test_winter_provider_real_cli.py` — acquire returns a clean worktree and resets the previous tenant's
  dirt, and a re-acquire recovers stale feature-branch tracking, over a real `winter ws init`.
- `tests/winter/test_winter_chunk_lands.py` — one chunk built, reviewed, and delivered to bare `main` over
  `provider="winter"`, the winter twin of `test_basic_workspace_chunk_lands_without_winter`.

The provider's allocation logic against fake winter and git seams stays at the unit tier.
