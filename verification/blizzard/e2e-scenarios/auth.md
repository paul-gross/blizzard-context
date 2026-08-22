<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Browser-auth e2e scenarios (`bzh:e2e-auth`)

The scenarios driving a real browser through the human-auth surfaces — the hub's own login dance and the multi-daemon
runner SSO bounce.

The login module needs the built bundle `blizzard hub host` serves (`mise run e2e` declares `depends = ["web-build"]`),
the federation module the bundle the runner itself serves; both need the sibling provisioned `blizzard-mock` worktree
with its stub IdP plus installed Chromium, skip cleanly without `BLIZZARD_E2E=1` or the provisioned worktree/stub IdP,
and take no `chromium_available` guard — missing Chromium or an unbuilt bundle fails loudly. The reacquisition function
adds no stub-IdP need beyond `_oauth_hub`/`require_stub_idp`.

## test_login_session_e2e

The browser login dance and the mid-stream session-expiry redirect: a real Chromium over the served board under
`auth.mode = "oauth"` against the real `blizzard-mock` stub IdP (`blizzard-mock-idp`), every seam real, no network
beyond the two local subprocesses.

- `test_browser_login_dance_and_mid_stream_session_expiry` — proves the whole sequence below in one loaded page:
  - An unauthenticated hit is gated to `/login` by the app's own 401 seam, rendering the configured provider button
    (`login-provider-<name>`) and no board chrome (`board-header` absent) — never an auto-redirect even for a single
    provider.
  - Clicking the provider button drives the real OAuth authorize-then-callback dance against the stub IdP, landing back
    as a freshly minted `pending` identity — the bottom, no-access role — in the pending lobby ("signed in, awaiting
    access", `pending-lobby-username` showing the handle) rather than a board silently 403ing every read; the lobby
    render itself proves the dance produced a working session cookie.
  - Promoted to `guest` directly in the hub store — the suite's mint-what-no-API-yet-exposes stand-in for a
    role-assignment API — and reloaded, the page reaches the live board with its SSE stream open (`board-shell` present,
    `pending-lobby` gone) over a seeded not-ready chunk whose card renders no Promote control: the end-to-end proof a
    `guest` reads everything and mutates nothing.
  - Promoted again to `contributor` and reloaded, that same card's Promote control is present.
  - With every `sessions` row deleted (an unambiguous expiry stand-in — the resolve path treats missing and expired
    identically) and the hub restarted, the restart force-drops the open SSE stream, the reconnect receives a 401
    through the fetch transport's one status-reading seam (`sse.service.ts`, the `authFailed` channel), and the app
    routes back to `/login` — the auth-failure channel proven end to end rather than an unbounded retry loop.
  - The redirect wait is a named 45s constant (not the file's 20s default), clearing `SseService`'s backoff ladder
    (1s/2s/4s/8s/16s/30s, ~30s cumulative) plus the restarted hub's startup: reconnects racing a still-starting daemon
    are refused rather than answered 401, so which attempt carries the 401 is not fixed, and a deadline under the ladder
    fails a working redirect — the same shape `test_runner_session_reacquisition_e2e` bounds at its own 40s inline
    literal.

## test_runner_federation_e2e

The multi-daemon runner SSO bounce: a hub under `auth.mode = "oauth"` against the `blizzard-mock` stub IdP and two
registered runners, A and B, each with its own federation identity, all real subprocesses. The runner's three-lane
gating is pinned at the lower tiers — the served web mount and its human-lane JSON API session-gated under an oauth-mode
hub, the worker-hook and CLI-socket lanes ungated (`tests/test_runner_route_gating.py`,
`tests/test_runner_federation.py`); the e2e scenarios prove the browser-navigated bounce itself.

- `test_multi_daemon_sso_bounce` — proves a sessionless Chromium visit to runner A is bounced runner A → hub → (no hub
  session yet, so on through) the stub-IdP dance → back into a runner-A-domain session on runner A's served page with no
  manual navigation, the hub-signed token delivered by the hub's auto-submitting `form_post` page and never in a query
  string — asserted across every request URL Chromium makes. It then replays the token Chromium's own
  `POST /api/auth/callback` carried: against runner B it is rejected (audience-bound `aud`), against runner A a second
  time rejected (single-use `jti`); a mismatched `state` is rejected; and a mid-run hub key rotation
  (`POST /api/auth/rotate-signing-key`) is picked up by a live second browser bounce into runner B with no restart of
  either daemon, the runner's JWKS cache refetching on the unknown `kid`.
- `test_runner_session_reacquisition_e2e` — proves the runner webapp's own session-recovery seam against a single
  federated runner (no A/B pair): a real Chromium authenticates into the panel, then the runner is restarted in place —
  same directory, same port, no re-registration, not a reload or cookie edit; its session secret is minted fresh per
  start (`app.py`), so the restart invalidates the still-open tab's session while leaving the hub's session and the tab
  untouched, reproducing the redeploy that triggers this in practice. The test issues no `page.goto` or `page.reload`:
  the trigger is the panel's own reconnect to the restarted runner's SSE stream — `auth.query.ts` keeps no poll, the
  reconnect's 401 catches exactly the restart case, and an in-place expiry with no reconnect falls to whichever
  backstop-polled read next re-authenticates, the stream's auth resolving once at connect, not per frame. The stream's
  401 drives `SessionRecovery.recoverFromUnauthenticated()` directly — the shared seam the generated-client interceptor
  also calls on its own 401, invoked here without one because the stream transport is a raw `fetch` the interceptor
  never sees — silently through `GET /api/auth/login` against the still-live hub session, landing back with a fresh
  runner session. Recovery is proven by that `GET /api/auth/login` request actually firing and the session cookie's
  value changing — not by DOM visibility, the identity text being identical before and after and the round trip too fast
  to reliably catch a hidden window. The wait is bounded loosely enough to clear `SseService`'s exponential reconnect
  backoff (~30s cumulative to a 401) plus the restarted daemon's startup rather than racing it, and the test fails if
  `provideSessionRecovery()` is removed from the runner app's `app.config.ts`.
