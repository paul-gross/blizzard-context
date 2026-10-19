# `web:story-render` detail (`bzh:matrix-command-web-story-render`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading and `npm run` script names are machine-checked — keep each verbatim, inside the section. -->

The detail spoke for the check that every workshop story compiles and renders, under the Angular workspace hub,
[`../web.md`](../web.md). Read [`../../../blizzard.md`](../../../blizzard.md) first for the short command and the
method-id inventory; [`../../commands.md`](../../commands.md) routes to the other methods' detail.

### web:story-render

`npm run story-render` in `web/` runs three steps and stops at the first that fails. `tsc --noEmit` over
`projects/fleet/.storybook/tsconfig.json` type-checks every story with the parts and builders it imports, since the
workshop's own build checks no types. `npm run storybook:build` builds the workshop in development mode, so Angular logs
what it logs only there, such as a story template binding an input its part does not have. Then
`web/scripts/story-render-check.js` serves `dist/storybook` and opens every story in headless Chromium, judging each by
the verdict the preview announces on its channel and by anything the page logs, throws, or fails to load meanwhile. It
prints each failing story's id and title with the message, and a count of stories rendered.

Before it opens a story, the script serves planted pages that speak the same channel — one that renders cleanly and four
that must fail — and refuses to run when it misjudges one, so a green run is a check that was shown able to fail. It
cannot pass on an empty index: a build whose `index.json` holds no story fails.

It proves a story compiles and renders, and nothing about what it shows: no pixels, no DOM, no `play`. A story whose
appearance is wrong passes. It is in no `ng test` target and not in `npm run test`: a build check over stories, not a
second runner. It runs in the `frontend` job of `.github/workflows/gate.yml`, after a Chromium install, and in
`blizzard:gate`.
