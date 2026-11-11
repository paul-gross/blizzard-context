# The kit floor

What a component builds its chrome from, and how a change a person sees is built against the workshop. A spoke of the
[frontend structure hub](../frontend-structure.md); the rules follow the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Chrome comes from the kit (`bzh:frontend-kit-floor`)

**Rule.** Every presentational component builds its chrome — panel shell, async loading/error/empty state, tone badges,
action buttons, close controls, choice chips, single-select dropdowns, tab strips and their counts, count-tile strips,
section headings, inline mutation-error lines — from `fleet/lib/kit/`, never a re-typed copy.

**Why.** A shared floor makes "no duplicated chrome" structural rather than a review habit, and a chrome fix (a token, a
state message) lands once.

**Exception.** A genuinely distinct native interaction, under a reasoned element-level ESLint suppression on that
element; and a site that genuinely should not convert, on the kit-floor sweep's reasoned exemption list. The shared kit
(`fleet/src/lib/kit/`) itself remains the only general exemption.

**Scope.** The kit depends only on `@angular/core`, `@angular/cdk`, and the token CSS (`core/design/tokens.css`) — no
query, mutation, or client injection — keeping it presentational, testable by plain inputs, and at the bottom of the
dependency graph; nothing in it may depend upward on a feature.

**Detect.** A native control in an application template outside the kit is tooled by `web:lint`
([`../../verification/blizzard/commands/web/static-checks.md`](../../verification/blizzard/commands/web/static-checks.md)
owns what it refuses and its probe); a reviewer asks whether a suppression's reason names a genuinely distinct native
interaction.

A new component's sibling `.css` declaring a chrome class the kit components own —
`.panel`/`.p-hdr`/`.p-body`/`.status`/`.lbl`/`.s-head` — or a local `.none`/`.hint`/`.rest` state line standing in for
`KitAsyncState`, outside `fleet/lib/kit/`, or a sibling `.html` hand-rolling `KitFactList`'s own `<dl class="kv">` grid
— both tooled by `web:structural-gate`'s kit-floor sweep
([`../../verification/blizzard.md`](../../verification/blizzard.md)); a kit component (`fleet/lib/kit/*`) importing a
query, mutation, or the generated API client — this half stays a review question.

**Do.** A new panel imports `KitPanel`/`KitAsyncState`/`KitBadge` from `fleet` and composes them; a status message
renders through `KitAsyncState`'s `loading`/`error`/`empty` states rather than a local `<p class="status">`. A tab's
count is `KitTab`'s `count`, and a failed gesture's inline line is `KitErrorLine`, fed the failure's message.

**Don't.** A new panel pasting another `.panel { background: linear-gradient(...); border: 1px solid var(--bezel); }`
block.

## A kit part arrives with its stories (`bzh:frontend-kit-stories`)

**Rule.** Every component or directive the kit exports has stories beside it, showing each meaningful state at the
widths it answers to. A presentational piece in `fleet`'s shared areas, `shell/` and `core/`, has them too. The stories
are a `*.stories.ts` file beside the part, named for the part in kebab case, in Component Story Format 3: its
default-exported meta names the part as `component` and is titled `Kit/<name a person calls it>`, and it exports one
named `StoryObj` per state the part's inputs and template select — its ordinary rendering, each variant, disabled, empty
and loading, overflowing, and narrow at `phone` and `phone-sm` where its layout answers to width. Every input a reader
could sensibly change is an `arg`, every output is wired to `fn()`, and a part that takes projected content renders
through a `render` template. A story builds its data from literals, holds no state between renders, reaches no network,
and asserts nothing: no `play`, no `expect`.

**Why.** The workshop is only a whole picture of the kit while every part is in it, and a part nobody can see alone is
judged through whichever page shows it.

**Exception.** A kit part that genuinely cannot be shown alone, named with its reason on the kit-stories sweep's
exemption list (`KIT_STORIES_EXEMPT` in `blizzard/web/scripts/structural-gate.js`).

**Scope.** The kit is held by the build. A presentational piece in `fleet`'s `shell/` or `core/` is held by review. The
expectation reaches no further: a piece in one of `fleet`'s feature folders, such as `chunk/`, `transcripts/`, or
`host/`, or in an app of its own, may have stories, but nothing asks for them.

**Detect.** `web:structural-gate`'s kit-stories sweep, and `web:story-render` for a story that has stopped compiling or
rendering.

**Do.** `kit-badge.stories.ts` beside `kit-badge.ts`: a meta titled `Kit/Badge` with `component: KitBadge` and a
`render` template projecting the badge's label, and one `StoryObj` export per variant and per tone, with a few
combinations such as `SoftNeeds`, each setting its `args` by literal, the overflowing `LongLabel` adding its own
`render` for a longer label.

**Don't.** Wrap a container in fake providers so that it will render.

## A visible change is built in the workshop (`bzh:frontend-workshop-first`)

**Rule.** Open the workshop before writing a part when a change alters anything a person sees on the board or the panel:
look first for a part that already does what the change needs and reuse it before inventing another, shape the change
against the part's stories as it is built, and before calling the work done perform `web:manual-workshop` over every
part touched.

**Why.** The workshop shows a part alone in every state its stories carry, so a change shaped there is seen in each
state as it is made, rather than through whichever page happens to compose the part.

**Detect.** Review a change that alters what a person sees on the board or the panel and was called done with no
`web:manual-workshop` pass over the parts it touched, or that adds a part doing what one already in the kit or a shared
piece does.

**Do.** A change giving a badge a new tone opens `Kit/Badge`, reuses `KitBadge` rather than writing a chip, adds the new
tone's story, shapes the change against it, then performs `web:manual-workshop` over the badge's changed stories at
`phone` and `desktop` before it is called done.

**Don't.** A new status chip beside the kit's badge, written against the page that needed it and called done on a jsdom
green.

**See also.**

- `web:manual-workshop` in [`../../verification/blizzard/manual-web.md`](../../verification/blizzard/manual-web.md) —
  the method's setup, steps, and pass condition; this rule names when a build performs it, not how.
- `bzh:frontend-kit-stories` above — the stories a part added or reshaped brings in the same change, so the next build
  finds them.
- `bzh:visual-change-needs-a-render` in
  [`../../verification/blizzard/tier-rules.md`](../../verification/blizzard/tier-rules.md) — the render artifact a
  visual change owes, which a workshop screenshot can be.
