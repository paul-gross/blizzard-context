# This harness's prose-authoring conventions bind blizzard-wide (`bzh:prose-authoring-scope`)

**Rule.** Hold `blizzard`'s and `blizzard-mock`'s agent-facing docs and code comments to this harness's conventions too — not only this repo's own files.

**Why.** A convention that only binds this repo's own files leaves the two repos most agents actually write in ungoverned, and a harness whose rules don't reach the code they're meant to shape is theater.

**Scope.** `standards/` conformance — the code-quality rules with a mechanical gate — is enforced by each of those repos' own CI: see [../verification/blizzard.md](../verification/blizzard.md) for the live inventory (ruff and pyright for both; eslint and `web:structural-gate` for `blizzard` alone — `blizzard-mock` carries no Angular workspace and gets neither). The canon's prose-authoring principles (`winter-canon:/principles.md`) bind their agent-facing docs and code comments the same way they bind this repo's own: at judgment only (`winter-canon:/enforcement-channels.md`), since no mechanical gate catches a restated enumeration or a hard-wrapped README there — review is what closes the gap. `blizzard-discovery` is the one repo this harness does not govern: it is a frozen historical record, not maintained to match current code (`workspace:/context/project/index.md`).

**Detect.** A restated enumeration, a hard-wrapped README, or a second owner of a fact, found in `blizzard` or `blizzard-mock` rather than this repo — the same violations this repo's own review would flag, just in a sibling repo's files.

**Do.** Review a `blizzard` or `blizzard-mock` doc/comment change against `winter-canon:/principles.md` exactly as you would this repo's own.

**Don't.** Skip prose review on a `blizzard`/`blizzard-mock` change because "this harness only governs its own repo" — there is no mechanical gate to catch what review skips.
