<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Browser-auth e2e scenarios (`bzh:e2e-auth`)

The scenarios driving a real browser through the multi-daemon runner SSO bounce. The hub marks its stub-IdP provider
`emails_authoritative`: an invitation admits an account only on a verified email from a provider so marked. The hub's
own invite-only login dance runs as `tests/ui/auth/login-session.spec.ts`.

The federation module needs the bundle the runner itself serves, the sibling provisioned `blizzard-mock` worktree with
its stub IdP plus installed Chromium, skips cleanly without `BLIZZARD_E2E=1` or the provisioned worktree/stub IdP, and
takes no `chromium_available` guard — missing Chromium or an unbuilt bundle fails loudly. The reacquisition function
adds no stub-IdP need beyond `_oauth_hub`/`require_stub_idp`.

## test_runner_federation_e2e

The multi-daemon runner SSO bounce: a hub under `auth.mode = "oauth"` against the `blizzard-mock` stub IdP and two
runners, A and B, each added by the hub's signed-in superuser — whose first sign-in needs no invitation and claims an
admin membership in the hub's one tenant, which a runner sign-in requires in the runner's tenant — and joined through
`runner init` under the token that add issued, each with its own federation identity, all real subprocesses. The
runner's three-lane gating is pinned at the lower tiers — the served web mount and its human-lane JSON API session-gated
under an oauth-mode hub, the worker-hook and CLI-socket lanes ungated (`tests/test_runner_route_gating.py`,
`tests/test_runner_federation.py`); the e2e scenarios prove the browser-navigated bounce itself.

- `test_multi_daemon_sso_bounce` — proves a sessionless Chromium visit to runner A is bounced runner A → hub → (no hub
  session yet, so on through) the stub-IdP dance → back into a runner-A-domain session on runner A's served page with no
  manual navigation, the hub-signed token delivered by the hub's auto-submitting `form_post` page and never in a query
  string — asserted across every request URL Chromium makes. It then replays the token Chromium's own
  `POST /api/auth/callback` carried: against runner B it is rejected (audience-bound `aud`), against runner A a second
  time rejected (single-use `jti`); a mismatched `state` is rejected; and a mid-run hub key rotation
  (`POST /api/auth/rotate-signing-key`) is picked up by a live second browser bounce into runner B with no restart of
  either daemon, the runner's JWKS cache refetching on the unknown `kid`. A and B share one name, and B's sign-in leaves
  A's session cookie in the same host's jar: the runner's cookie names key on its hub-minted id, never its name.
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
- `test_one_sign_in_at_a_registered_host_reaches_both_runners_pages` — proves a registered host is the panel's one
  sign-in client: the signed-in superuser adds a host at the hub, the host adds two runners under itself with its host
  token, and one `blizzard-runner host` holding that token runs both as `[[runner]]` entries. Sign-in waits until the
  hub has answered the host's report. A sessionless Chromium visit to the first runner's legacy `/runners/<id>/board`
  link, which redirects to the board filtered to that runner, bounces to `authorize` with the host id as `client`, and
  lands holding exactly one runner session cookie, `bz_runner_session_<host id>`. The second runner's
  `/runners/<id>/board` then renders signed in with no second bounce to the hub. That the host signs in only while its
  latest report was answered as itself is pinned at the component tier (`tests/test_runner_federation.py`).
