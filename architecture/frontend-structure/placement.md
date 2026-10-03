# Placement

Where a unit of web code lives — in `fleet` or in an app — and how a view both daemons serve is written once. A spoke of
the [frontend structure hub](../frontend-structure.md); the rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Code lives with the daemons that serve it (`bzh:frontend-placement`)

**Rule.** `fleet` holds only what both apps reach: each direct child of `fleet/src/lib/` — a feature folder or a
top-level module — is reached by the non-spec code of both `hub` and `runner`, and no `fleet` file imports from `hub` or
`runner`. App-local code lives in its app, pages, queries, and components together. A view both daemons serve is written
once in `fleet` and takes the daemon as an injected seam — the generated client, the cache-key plane, and an optional
actions port — rather than being copied per app.

**Why.** A feature folder in `fleet` that one app reaches is that app's code in the wrong place: it widens the shared
surface, hides the app's real boundary from the eager-shell and bundle checks, and invites a per-app mirror when the
other daemon later needs a near copy. A per-app copy of a shared view drifts — the two pages disagree on tabs,
selection, and copy until one is fixed and the other is not.

**Scope.** Binds the direct children of `fleet/src/lib/` and every `fleet` import. A mixed folder reached by both apps
passes at the folder level, so shared infrastructure (`kit/`, `viewport/`, `sse/`) may hold a file only one app uses.
Spec-support (`testing/`, which has its own `fleet/testing` entry) and declaration-free re-export barrels (`format/`)
are exempt, each with its reason named in the sweep.

**Detect.** The placement sweep inside `web:structural-gate`
([`../../verification/blizzard.md`](../../verification/blizzard.md)): it resolves reach to the symbol through the
`fleet` barrels, fails naming a unit and the single app that reaches it (or no app when it is dead), and fails any
`fleet` file importing an app project. Its self-test must-catches a single-app unit and a `fleet`→app import and
must-passes a both-app unit.

**Do.** `ChunkTranscriptsContainer` and the chunk page in `fleet/src/lib/chunk-page/` take their client and plane from
the daemon the route provides; the hub supplies an actions port and the runner supplies none, so one page renders
read-only on the runner. The hub's gardening, graphs, admin, and board reads live under `hub/src/app/`.

**Don't.** A second chunk page in `runner/` that mirrors the hub's, or a gardening folder left in `fleet` because it was
written there first.

**See also.** `bzh:frontend-eager-shell-entry` — the hub modules that moved out of `fleet` still reach `fleet` on the
eager path only through `fleet/shell`.
