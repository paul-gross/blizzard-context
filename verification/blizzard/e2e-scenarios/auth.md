# e2e scenarios — browser auth (`bzh:e2e-auth`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The scenarios that drive a real browser through the human-auth surfaces — the hub's own login dance and the multi-daemon
runner SSO bounce.

## test_login_session_e2e

The **browser login dance + mid-stream session-expiry redirect** (#93, epic #89 human auth; the role ladder reshaped by
#210): a real Chromium over the served board under `auth.mode = "oauth"` against the real `blizzard-mock` **stub IdP**
(`blizzard-mock-idp`, the #92 counterpart), every seam real, no network beyond the two local subprocesses.

- `test_browser_login_dance_and_mid_stream_session_expiry` — proves, in one loaded page: an **unauthenticated** hit is
  gated to `/login` by the app's own 401 seam, rendering the configured provider button (`login-provider-<name>`) and
  **no** board chrome (`board-header` absent) — never an auto-redirect for a single provider; clicking it drives the
  **real OAuth authorize→callback dance** against the stub IdP and lands back authenticated as a freshly-minted
  `pending` identity — the bottom, no-access role (#210) — which renders the **pending lobby** ("signed in, awaiting
  access", `pending-lobby-username` = the handle) rather than a board silently 403ing every read — itself the proof the
  dance produced a real, working session cookie; then, promoted to `guest` directly in the hub store (the #94
  role-assignment API's stand-in, the same "mint what no API yet exposes" pattern the suite uses for fixture state) and
  reloaded, it reaches the **live board** with its SSE stream open (`board-shell`, `pending-lobby` gone) over a seeded
  not-ready chunk whose card renders with **no Promote control** — the end-to-end proof that a `guest` reads everything
  and mutates nothing, not merely a unit-tier claim; promoted again to `contributor` and reloaded, that same card's
  Promote control is present; and finally, with every `sessions` row deleted (an unambiguous stand-in for expiry — the
  resolve path treats missing and expired identically) and the hub restarted, the restart **force-drops the open SSE
  stream** and the client's own reconnect — the fetch-based transport's one seam that can read a status code
  (`sse.service.ts`, the `authFailed` channel) — receives a **401** and the app routes back to `/login`, proving the
  auth-failure channel end to end rather than an unbounded retry loop (AC 5). That redirect's wait is bounded loosely
  (45s, its own named constant rather than the file's 20s default) to clear `SseService`'s backoff ladder
  (1s/2s/4s/8s/16s/30s, ~30s cumulative) plus the restarted hub's startup — the same reconnect-driven shape
  `test_runner_session_reacquisition_e2e` bounds at its own, separately-chosen 40s inline literal: the reconnects racing
  a daemon that is still coming up are refused rather than answered `401`, so **which** attempt carries the 401 is not
  fixed, and a deadline under the ladder fails a working redirect. Needs the built bundle `blizzard hub host` serves
  (hence `mise run e2e`'s `depends = ["web-build"]`) + the sibling provisioned `blizzard-mock` worktree with its stub
  IdP + an installed Chromium; it skips cleanly without `BLIZZARD_E2E=1` or without the provisioned worktree/stub IdP,
  but takes no `chromium_available` guard — a missing Chromium or an unbuilt bundle both fail loudly instead of
  skipping.

## test_runner_federation_e2e

The **multi-daemon runner SSO bounce** (#95, epic #89 human auth): a hub (`auth.mode = "oauth"`) against the
`blizzard-mock` **stub IdP** and **two** registered runners (A, B), each with its own federation identity, all real
subprocesses.

- `test_multi_daemon_sso_bounce` — a real Chromium navigates to runner A with no session and is bounced runner A → hub →
  (no hub session yet, so on through) the stub-IdP provider dance → back into a runner-A-domain session on runner A's
  own served page — the whole round trip with no manual navigation, the hub-signed token delivered by the hub's
  auto-submitting `form_post` page and **never in a query string** (asserted across every request URL Chromium makes).
  The token Chromium's own `POST /api/auth/callback` carried is then replayed against runner B (**rejected** —
  audience-bound `aud`) and against runner A a second time (**rejected** — single-use `jti`); a mismatched `state` is
  **rejected**; and a mid-run hub key rotation (`POST /api/auth/rotate-signing-key`) is **picked up by a live second
  browser bounce into runner B with no restart** of either daemon (the runner's JWKS cache refetches on the unknown
  `kid`). The runner's own three-lane gating is pinned at the lower tiers — the served web mount + its human-lane JSON
  API session-gated under an oauth-mode hub, the worker-hook lane and CLI-socket lane ungated
  (`tests/test_runner_route_gating.py`, `tests/test_runner_federation.py`); this scenario proves the browser-navigated
  bounce end to end. Needs the built bundle the runner itself serves + the sibling provisioned `blizzard-mock` worktree
  with its stub IdP + an installed Chromium; it skips cleanly without `BLIZZARD_E2E=1` or without the provisioned
  worktree/stub IdP, but takes no `chromium_available` guard — a missing Chromium or an unbuilt bundle both fail loudly
  instead of skipping.
- `test_runner_session_reacquisition_e2e` (blizzard#312) — the runner webapp's own session-recovery seam, proven against
  a **single** federated runner (no runner A/B pair, unlike the scenario above): a real Chromium authenticates into its
  panel, then the runner is **restarted in place** (same directory, same port, no re-registration) rather than reloaded
  or cookie-edited — its session secret is minted fresh per start (`app.py`), so the restart invalidates the still-open
  tab's session while leaving the hub's own session, and the tab itself, untouched, reproducing the redeploy that
  triggers this in practice. With no `page.goto`/`page.reload` from the test, the trigger is the panel's own reconnect
  to the restarted runner's SSE stream (`auth.query.ts` itself keeps no poll of its own — a reconnect's own `401` is
  what catches exactly this restart case; an in-place expiry with no reconnect is instead caught by whichever
  backstop-polled read next re-authenticates, since the runner's stream auth resolves once at connect, not per frame):
  once the stream reconnects and the restarted daemon's fresh session secret invalidates the old cookie, the stream's
  `401` drives `SessionRecovery.recoverFromUnauthenticated()` directly — the shared seam the generated-client
  interceptor also calls on its own `401`, invoked here without one since the stream's transport is a raw `fetch` the
  interceptor never sees — silently through `GET /api/auth/login` against the still-live hub session, landing back with
  a fresh runner session — proven by that request actually firing (not by a DOM-visibility check: the identity control's
  text is the same username before and after, and the round trip against a still-live hub session completes fast enough
  that a hidden window in between is too transient to reliably catch) and by the session cookie's value changing. The
  wait for that request is bounded loosely enough to clear `SseService`'s own exponential reconnect backoff
  (1s/2s/4s/8s/16s/30s, `~30s` cumulative to a `401`) plus the restarted daemon's own startup, rather than racing it.
  Fails if `provideSessionRecovery()` is removed from the runner app's `app.config.ts`. Needs the same built bundle +
  installed Chromium as `test_multi_daemon_sso_bounce`, and skips the same way; no `blizzard-mock` stub IdP dependency
  beyond what `_oauth_hub`/`require_stub_idp` already need.
