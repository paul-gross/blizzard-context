# Subscription credentials

This spoke owns a subscription credential file's read/write boundary — sampling, and renewal; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A subscription credential file is never written (`bzh:subscriptions-no-write`)

**Rule.** Nothing under `runner/subscriptions/` opens a subscription credential file for writing. A sampler reads it; a
renewer asks the vendor CLI to refresh it, through an injected seam, and reads the outcome. Renewal is the vendor's own
flow — its lock, its atomic write, its refresh-token rotation — reached only as `bzh:pluggable-seams` reaches any
external system.

**Why.** The file is shared with every worker the runner spawns and with the vendor CLI itself. A second writer can
corrupt it mid-refresh, and an in-process refresh that rotates the refresh token can invalidate the login the vendor
just renewed. Delegating keeps one owner of the write.

**Detect.** A `.write_text(`, `.write_bytes(`, or write-mode `open(` under `runner/subscriptions/`; a renewer binding
that parses a refresh response and stores its tokens itself.

**Do.** The OpenAI renewer drives `codex app-server` over a one-shot subprocess seam and reports `renewed`, `not due`,
or `failed` with a cause; the refreshed tokens land on disk as the vendor's side effect.

**Don't.** A renewer that calls the provider's token endpoint and rewrites `auth.json` — blizzard now owns a write it
cannot coordinate with the vendor's lock.

`bzh:subscriptions-no-write` is tooled by `blizzard:structural-gate`'s ast-grep scan
([../../verification/blizzard.md](../../verification/blizzard.md)), scoped to `runner/subscriptions/`; no exemption
stands.
