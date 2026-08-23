# Tool detail (`bzh:matrix-tool-detail`)

Full per-tool detail for the Tools rows of [../blizzard.md](../blizzard.md) marked "(more)" — one flat `###` section per
tool id, in table order.

<!-- The flat `###` shape is a contract shared with the sibling spokes; this directive suppresses the MD001 lint it trips. -->

<!-- rumdl-disable MD001 -->

### tool:service-up

`winter service up <env> --wait` brings the env's verification stack up in order (forge → hub → runner via
`depends_on`), each service health-gated on a real readiness check, port-band isolated so parallel envs never collide.
The stack: per-env postgres on its own band port, the mock GitHub forge at band +1 from the env's blizzard-mock worktree
fronting `$BZ_FORGE_REPOS_DIR` (the fixture workspace's per-env bare origins), and the blizzard hub (band +2) and runner
(band +3) in tmux slots. Hub and runner run on their embedded sqlite stores; the per-env postgres runs but the daemons
do not use it. The runner drives the per-env blizzard-mock fixture workspace and spawns the fenced mock-claude-code
façade.

### tool:mock-fleet

The blizzard-mock fleet: the mock GitHub forge (blizzard-mock-forge), the fixture-workspace scaffold, and the
prompt-is-the-program harness mocks (mock-claude-code, mock-codex, mock-opencode), bound at the seams so scenarios run
with no tokens or network. It also has the mock hub (blizzard-mock-hub) and mock runner (blizzard-mock-runner), the
counterparts `blizzard:service-test` drives the real daemons against. Each mock carries a `_levers`
response-distortion/capture plane and a control/drive plane for seeding; each mock's README.md owns its lever catalog.

The claude_code façade records each turn's `--model`/`--effort` flags on per-session state, acting on neither — the
observable for asserting blizzard's mint-only model contract; the shape is owned at
`src/blizzard_mock/harness/README.md`. It executes the `--settings` document's hook commands as real subprocesses, so a
fleet-tier worker fires its own hooks; semantics owned at `src/blizzard_mock/harness/README.md` §"Hook execution". It
also mints a real Claude-Code-shaped JSONL transcript per run; the mechanism, and why codex/opencode mint nothing, is
owned at `src/blizzard_mock/harness/README.md` §"Conversation transcripts". A scenario can therefore assert
`GET /api/leases/{lease_id}/transcript` serves turns from a mock-produced file — at `blizzard:service-test`, which
reaches the runner's local HTTP API without `blizzard:e2e`'s delivery/browser machinery.

The stub OAuth IdP (blizzard-mock-idp) login-dances the hub's `hub/auth/oauth/` seam over a real wire with no tokens or
network: both provider shapes (OIDC and github-style) at one origin, no login UI (authorize redirects straight back with
a code for the levered profile), and a `/_levers` identity-scripting plane; contract at
`src/blizzard_mock/idp/README.md`.

### tool:fixture-workspace

The blizzard-mock-fixture scaffold: mints bare `file://` origins plus a generated disposable winter workspace — the
environment the service tier, e2e tier, and sweep run against.

### tool:mock-data

The blizzard-mock-data CLI seeds hub and runner stores into a known world by reflecting the live schema at runtime,
importing nothing from blizzard. Every write runs a drift guard: schema drift fails loud with `SchemaDriftError` naming
the table and columns. Whether to seed the store directly versus drive the real work-source/ingest wire path is a choice
owned by [../../tooling/store-seeding.md](../../tooling/store-seeding.md).

- `reset --store hub|runner` is an FK-safe delete-all, the workhorse every scenario starts from.
- `create` has one verb per seedable concept; the root verb `chunk` composes the exact fact rows `derive_chunk_status`
  reads, never a status column; `lease`/`usage` switch composer per `--store` where the schemas differ.
- `scenario` seeds a whole world per command: `board` (hub store) and `fleet` (composes a board and mirrors it into the
  runner store under one pinned runner id, so the runner's local panel renders beside it); the exact contents,
  `--stress` included, are owned at `src/blizzard_mock/mock_data/README.md`. `scenario fleet` takes hub and runner
  stores as two independent required targets; neither defaults from the other.
- `fixture list|apply` is a stub; `scenario` is the delivered preset surface.
