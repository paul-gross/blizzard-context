# The shared kit as the presentational floor

What a component builds its chrome from. Spoke of the [frontend structure hub](../frontend-structure.md); each rule
follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## The kit is the presentational floor (`bzh:frontend-kit-floor`)

**Rule.** Every presentational component builds its chrome — panel shell, async loading/error/empty state, tone badges,
action buttons, choice chips, tab strips — from `fleet/lib/kit/`, never a re-typed copy. The kit itself depends on
nothing but `@angular/core` (+ common directives) and the token CSS (`design/tokens.css`) — no query, mutation, or
client injection, so it stays presentational and testable by plain inputs at the bottom of the dependency graph.

**Why.** A shared presentational floor is what makes "no duplicated chrome" a structural property rather than a review
habit — every future panel composes the kit instead of re-inventing the `.panel`/`.p-hdr`/`.status` shapes, and a chrome
fix (a token, a state message) lands once. The kit sits *under* every container and presentational component in the
dependency graph; nothing in the kit may depend upward on a feature.

**Detect.** A new component's sibling `.css` file declaring `.panel`/`.p-hdr`/`.p-body`/`.status`/`.lbl` (the retired
chrome classes) outside `fleet/lib/kit/` — caught in review, not by a tool; a kit component (`fleet/lib/kit/*`)
importing a query, mutation, or the generated API client.

**Do.** A new panel imports `KitPanel`/`KitAsyncState`/`KitBadge` from `fleet` and composes them; a status message
renders through `KitAsyncState`'s `loading`/`error`/`empty` states rather than a local `<p class="status">`.

**Don't.** A new panel pastes another `.panel { background: linear-gradient(...); border: 1px solid var(--bezel); }`
block — the exact duplication the kit exists to retire.
