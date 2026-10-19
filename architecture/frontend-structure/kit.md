# The kit floor

What a component builds its chrome from. A spoke of the [frontend structure hub](../frontend-structure.md); the rules
follow the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Chrome comes from the kit (`bzh:frontend-kit-floor`)

**Rule.** Every presentational component builds its chrome — panel shell, async loading/error/empty state, tone badges,
action buttons, choice chips, single-select dropdowns, tab strips — from `fleet/lib/kit/`, never a re-typed copy.

**Why.** A shared floor makes "no duplicated chrome" structural rather than a review habit, and a chrome fix (a token, a
state message) lands once.

**Scope.** The kit depends only on `@angular/core`, `@angular/cdk`, and the token CSS (`core/design/tokens.css`) — no
query, mutation, or client injection — keeping it presentational, testable by plain inputs, and at the bottom of the
dependency graph; nothing in it may depend upward on a feature.

**Detect.** `web:lint` refuses a native `<button>`, `<select>`, or `<input>` in application `.html` templates outside
`fleet/src/lib/kit/`, independent of its class name. A genuinely distinct native interaction needs a reasoned
element-level ESLint suppression; the shared kit remains the only general exemption. The ESLint AST probe in
`web/scripts/kit-control-lint-probe.js` pins forbidden tags, kit controls, comments, and the exception form.

A new component's sibling `.css` declaring the retired chrome classes `.panel`/`.p-hdr`/`.p-body`/`.status`/`.lbl` (plus
`KitAsyncState`'s own hand-rolled precursors `.none`/`.hint`/`.rest`) outside `fleet/lib/kit/`, or a sibling `.html`
hand-rolling `KitFactList`'s own `<dl class="kv">` grid — both tooled by `web:structural-gate`'s kit-floor sweep
([`../../verification/blizzard.md`](../../verification/blizzard.md)), with a reasoned exemption list for a site that
genuinely should not convert; a kit component (`fleet/lib/kit/*`) importing a query, mutation, or the generated API
client — this half stays a review question.

**Do.** A new panel imports `KitPanel`/`KitAsyncState`/`KitBadge` from `fleet` and composes them; a status message
renders through `KitAsyncState`'s `loading`/`error`/`empty` states rather than a local `<p class="status">`.

**Don't.** A new panel pasting another `.panel { background: linear-gradient(...); border: 1px solid var(--bezel); }`
block.

## A kit part arrives with its stories (`bzh:frontend-kit-stories`)

**Rule.** Every component or directive the kit exports has stories beside it, showing each meaningful state at the
widths it answers to. A presentational piece in `fleet`'s shared areas, `shell/` and `core/`, has them too.

**Why.** The workshop is only a whole picture of the kit while every part is in it, and a part nobody can see alone is
judged through whichever page shows it.

**Scope.** The kit is held by the build. A presentational piece in `fleet`'s `shell/` or `core/` is held by review. The
expectation reaches no further: a piece in one of `fleet`'s feature folders, such as `chunk/`, `transcripts/`, or
`host/`, or in an app of its own, may have stories, but nothing asks for them.

**Detect.** `web:structural-gate`'s kit-stories sweep, with its reasoned exemption list, and `web:story-render` for a
story that has stopped compiling or rendering.

**Do.** A new kit part lands with a `*.stories.ts` file beside it, named for the part in kebab case, whose
default-exported meta names the part as `component` and is titled `Kit/<name a person calls it>`. The file is Component
Story Format 3: one named `StoryObj` export per state the part's inputs and template select — its ordinary rendering,
each variant, disabled, empty and loading, overflowing, and narrow at `phone` and `phone-sm` where its layout answers to
width. Every input a reader could sensibly change is an `arg`, every output is wired to `fn()`, and a part that takes
projected content renders through a `render` template. A story builds its data from literals, holds no state between
renders, reaches no network, and asserts nothing: no `play`, no `expect`.

**Don't.** Wrap a container in fake providers so that it will render.
