# Blizzard manual-method detail (`bzh:matrix-manual-detail`)

<!-- the flat `###` shape is this file's stated contract, shared with its sibling spokes. -->
<!-- rumdl-disable MD001 -->

Full detail for the `blizzard:` manual methods [../blizzard.md](../blizzard.md)'s Manual testing table names — one
`### <method-id>` section per row, in table order. The `blizzard-mock:` methods are
[./manual-mock.md](./manual-mock.md).

### blizzard:manual — the acceptance loop end-to-end

Surface: the walking skeleton — one chunk traveling ingest → acquire → mock-scripted commit → deliver → landed in a bare
origin, with `done` derived from facts. Setup: a fixture-workspace env (`tool:fixture-workspace`) with the hub, the
runner, and the mock fleet bound; sqlite up via each daemon's embedded store (`tool:service-up` also brings up postgres,
unused in P6). Pass: the chunk lands in the bare origin and the hub's facts derive `done`, run fully locally with no
tokens and no network. **Automated as of P6** — this loop *is* the walking skeleton and now runs (extended in P7 wave 1
to the full `build → review → deliver` shape, joined by the review-fail-cycle and escalation scenarios, in wave 2 by the
ask/answer and human-gate scenarios, and in wave 3 by the browser-driven board scenario) as the standing smoke suite
`blizzard:e2e` (`mise run e2e`), which self-manages the stack; run it there rather than by hand. Two live-service ways
to drive it manually: (a) `winter service up <env> --wait` (forge + hub + runner), then mint a fixture
(`blizzard-mock-fixture reset --env <env>`), drop the harness fence marker in its `workspace/`, file a forge issue, and
`POST /api/chunks` — the hosted runner ticks it to `done`; (b) read the `mise run e2e` source for the exact in-process
sequence. The P4 precursor `blizzard-mock:e2e` still exercises the ingest-less push→PR→merge→land arc with the mock
fleet alone (no `blizzard` code).

### blizzard:manual-sse-probe — the live SSE wire probe

Surface: **narrowed by issue #235** — `blizzard:sse-contract` now gates frame-level shape statically (every optional
field's presence-vs-omission, `event-logged`'s present-`null` `chunk_id`, and both sides' agreement on the field set)
against the golden corpus `contracts/sse/`, so this method's remaining, load-bearing surface is what only a live socket
can show: **timing and framing over the wire** — the reserved open-of-stream comment, the periodic keepalive comment,
and the `id`/reconnect-replay behavior actually observed on a real `GET /api/events/stream` connection — distinct from
what the component tier's replay-tail read shows (an event was **recorded**, not what a subscriber actually
**received**) and from `blizzard:service-test`'s live-fan-out proof (count and timing of frames, not their field-level
shape, which `blizzard:sse-contract` now covers instead of this method). Not hub-only: the runner serves the identical
stream shape at its own `GET /api/events/stream`, with its own reserved open-of-stream comment and its own keepalive
cadence, so a probe run is scoped to **one daemon at a time** — nothing here needs both up at once. Setup: the daemon
under test, hosted on a scratch port — `blizzard hub init <dir>` then `blizzard hub host --dir <dir> --port <p>`, or
`blizzard runner init <dir>` then `blizzard runner host --dir <dir> --port <p>`. Both daemons take the same shape:
`init` scopes by a **positional** directory (it has no `--dir`), `host` by either the positional or `--dir`, and only
`host` binds `--port`.

Steps:

1. start the daemon under test — hub or runner — on the scratch port
2. hold an SSE subscription open against that daemon's `GET /api/events/stream` (`curl -N` or a streaming HTTP client)
   before driving the act
3. drive each publish site over HTTP — the endpoint or CLI call behind the `broker.publish_*` call under test, on the
   same daemon
4. assert the reserved comment opens the stream (the hub's and the runner's read different literal text — check the one
   the daemon under test actually owns), a keepalive comment arrives on an idle connection within the documented
   cadence, and the frame(s)' `id`/reconnect-replay behavior on a live socket — the field-level shape of the frame
   `data:` itself is `blizzard:sse-contract`'s claim, not re-asserted here.

Pass: the framing/timing behavior above holds over a real connection, for every call driven.

### blizzard:manual-rollback-drill — the compose deployment's rollback promise, run for real

Surface: `docs/rollback.md` (the `blizzard` app repo's own doc) walked verbatim against a live compose deployment
(`docs/install.md`, same repo) — stop the hub, `docker compose run --rm hub blizzard-hub migrate --dir … --down <rev>`
on the **still-current (new)** image (it carries the `downgrade()` steps the older image's tree never heard of), then
swap to the previous image tag and bring the hub back up — proving the operator-facing procedure actually works, not
just that the underlying downgrade code does. Setup: a running compose stack (`docker compose up -d`,
`packaging/docker/compose.yaml`) on at least two published image tags (or two locally-built ones), so there is a real
"previous" tag to roll back to. Pass: after the drill, the hub serves at the previous tag's version (`GET /api/health` →
the older `version`) and `GET /api/ready` reports `ready: true` — the store landed at exactly the older revision, not
merely "some earlier one". The downgrade mechanism itself — that every shipped revision has a working `downgrade()` — is
proven mechanically and continuously by `blizzard:unit-test`'s
`tests/test_store_migrations.py::test_migrate_up_and_down`; this drill is the operator-facing procedure wrapped around
that guarantee, run by hand since no CI tier stands up a real compose deployment. Run it at least once per DISTRIB slice
landing (issue #191/#192); re-run whenever `docs/rollback.md`'s commands change.

### blizzard:manual-external-usage-probe — the vendor's real OAuth-usage response shape, proven live

Surface: no CI tier can prove the vendor's real `/api/oauth/usage` response shape — the tier rules forbid service/e2e
tests from touching the network at all, and the endpoint is undocumented and unversioned, so its shape can drift under
blizzard with no changelog to catch it. Every CI-tier test exercises Claude Code's external-subscription-usage sampling
against a stubbed transport (the fixtures the unit/component tiers bind); this manual method is what ties that stub back
to what the vendor actually returns. Setup: the runner machine's own real Claude Code OAuth credentials
(`~/.claude/.credentials.json`), a working `blizzard runner` binary.

Steps:

1. run `blizzard runner external-usage probe` (issue #218's phase-1 diagnostic subcommand — read-only, no store write,
   no enqueue)
2. separately run `claude`'s own `/usage` command against the same account
3. compare the two.

Pass: the probe's parsed 5h/7d utilization percentages and reset times match what `claude /usage` itself reports for the
same account, within the natural few-second sampling skew. This is a deliberately-built method closing a real, permanent
gap, not a placeholder for a future CI tier — the same shape as `blizzard:manual-rollback-drill`: no tier will ever be
added to replace it, because the thing it proves (an external vendor's live, undocumented response shape) is
structurally outside what a hermetic, network-free CI tier can ever see. (`blizzard:manual-sse-probe` was once a similar
case; issue #235's `blizzard:sse-contract` has since automated its field-shape half, leaving only framing/timing manual
— a reminder that "structurally unreachable by CI" should be checked afresh each time a surface like this comes up, not
assumed permanent by analogy.)

### blizzard:manual-autocompact-window — a declared window compacts a real session, not the model maximum

Surface: no CI tier can observe *effective* harness behavior here — the same structural gap
[the session-stickiness gap](./gaps.md) describes (the mock façade sees argv, never actual context accounting) — so what
only a live session can prove is the flag's own **effect**, not its presence: a session spawned with a declared
`--autocompact <window>` compacts near that value rather than growing toward the model's own maximum context. Setup: a
real Claude Code CLI (`claude 2.1.234` or newer, the version this feature's tested assumptions were measured against), a
workdir it can run non-interactively in (`-p`), and turns substantial enough to grow context by tens of thousands of
tokens each (e.g. asking it to read and summarize a large file), so a handful of turns crosses a low declared window.

Steps:

1. Mint a session with a low window near the CLI's own floor —
   `claude --autocompact 100k -p "<turn 1>"
   --output-format json` — and record the printed session id.
2. Resume it repeatedly with the flag reasserted each time —
   `claude --resume <session-id> --autocompact 100k -p
   "<turn N>" --output-format json` — each turn large enough to
   add tens of thousands of tokens, until cumulative context should exceed 100k.
3. After each turn, read that turn's context size the same way the runner already does: the main-chain record's
   `message.usage.input_tokens + cache_read_input_tokens + cache_creation_input_tokens` in
   `~/.claude/projects/<project>/<session-id>.jsonl` (`ClaudeCodeTranscriptSource.context_tokens`,
   `claude_code_transcript.py`).
4. Repeat steps 1-3 with `--autocompact` omitted, same prompts, same turn count.

Pass: the declared-window run's context size drops sharply — back toward a small fraction of 100k — within a turn or two
of first crossing it, and stays down on the next turn; the undeclared run's context size keeps climbing past 100k
without dropping. That contrast is the compaction event itself: no other mechanism resets a session's context
mid-lineage.

### blizzard:manual-standing-idp — auth-gated behavior verified live, in a running env

Surface: `blizzard:e2e`'s login-session scenario proves the full OAuth dance and its role-dependent UI, but only for a
pytest fixture's lifetime — the process pair it stands up is gone the moment the test returns. No method proves the same
behavior against a **standing** hub a human or a `frontend-verifier` agent can point a real browser at outside a test
run, in a provisioned feature env (`auth.mode = "none"` is the default a `winter service up <env>`-started hub scaffolds
via `blizzard hub init`, so a running env's own service stack serves everything unauthenticated unless this method's
setup is applied to it). This is what closes that gap.

Setup:

1. start the stub IdP standing (`blizzard-mock/src/blizzard_mock/idp/README.md`'s "Standing instance" section —
   `blizzard-mock-idp --host 127.0.0.1 --port <idp-port>`, confirm `GET /healthz`)
2. a hub runtime dir — a scratch dir, or a provisioned env's own `$BZ_HUB_RUNTIME` if you intend that env's hub to run
   in `oauth` mode — with `[auth] mode = "oauth"` and one `[[auth.oauth.provider]] type = "oidc"` entry pointing
   `issuer` at the standing IdP (`hub/config.py`'s `AUTH_MODE_OAUTH`; note the mode is `"oauth"`, not `"oidc"` — `oidc`
   is the provider `type`)
3. `mise run web-build` so the hub serves the built board.

Steps:

1. start the hub (`blizzard hub host --dir <hub-dir> --port <hub-port>`)
2. drive a real browser to `http://127.0.0.1:<hub-port>/`, confirm the `/login` gate renders the configured provider's
   button, click it, and confirm the dance lands authenticated (a fresh identity mints `pending`)
3. `PUT /_levers/profile` on the IdP before a login to script a specific identity, or flip it between two logins (fresh
   browser context each time) to prove two distinct identities
4. set a role directly in `<hub-dir>/data/hub.db`'s `users` table (the same seam `blizzard:e2e`'s login-session scenario
   uses ahead of a role-assignment API) and reload (same session cookie, no re-login) to confirm role-dependent UI —
   e.g. a seeded not-ready chunk's Promote control present for `contributor`, absent for `guest`.

Pass: the browser reaches an authenticated board through the standing IdP, and at least two roles are observed rendering
visibly different UI on the same underlying state. This is a manual method by the matrix's own
[bootstrap convention](../blizzard.md): no automated tier drives a real browser against a standing, out-of-fixture
process pair, and building one would mean giving the e2e tier a persistent-process mode it does not otherwise need — the
cost is not worth it for a surface a human or a `frontend-verifier` agent can already reach by hand. Whether this
method's setup becomes a standing, opt-in feature of the winter workspace's own per-env service stack (rather than
assembled by hand each time) is a workspace-manifest question outside any project repo's scope — see blizzard#236's
comment for the follow-on discussion.
