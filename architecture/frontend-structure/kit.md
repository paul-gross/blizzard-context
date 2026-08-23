# The kit floor

What a component builds its chrome from. A spoke of the [frontend structure hub](../frontend-structure.md); the rule
follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Chrome comes from the kit (`bzh:frontend-kit-floor`)

**Rule.** Every presentational component builds its chrome — panel shell, async loading/error/empty state, tone badges,
action buttons, choice chips, tab strips — from `fleet/lib/kit/`, never a re-typed copy.

**Why.** A shared floor makes "no duplicated chrome" structural rather than a review habit, and a chrome fix (a token, a
state message) lands once.

**Scope.** The kit depends only on `@angular/core` (plus common directives) and the token CSS (`design/tokens.css`) — no
query, mutation, or client injection — keeping it presentational, testable by plain inputs, and at the bottom of the
dependency graph; nothing in it may depend upward on a feature.

**Detect.** A new component's sibling `.css` declaring the retired chrome classes
`.panel`/`.p-hdr`/`.p-body`/`.status`/`.lbl` outside `fleet/lib/kit/` — caught in review, not by a tool; a kit component
(`fleet/lib/kit/*`) importing a query, mutation, or the generated API client.

**Do.** A new panel imports `KitPanel`/`KitAsyncState`/`KitBadge` from `fleet` and composes them; a status message
renders through `KitAsyncState`'s `loading`/`error`/`empty` states rather than a local `<p class="status">`.

**Don't.** A new panel pasting another `.panel { background: linear-gradient(...); border: 1px solid var(--bezel); }`
block.
