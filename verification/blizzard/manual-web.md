# Performing a `web:` manual method (`bzh:matrix-manual-web-detail`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

Full detail for the `web:` manual methods named in [`../blizzard.md`](../blizzard.md)'s Manual testing table, one
section per row, in that table's order. The `blizzard:` methods live in [`./manual.md`](./manual.md) and the
`blizzard-mock:` methods in [`./manual-mock.md`](./manual-mock.md).

The methods other than [`web:manual-form-adoption-census`](#webmanual-form-adoption-census), which reads the tree and
runs gates rather than driving a page, are driven by a human, or a `frontend-verifier` agent through Chrome DevTools, in
a real Chromium browser — the pass condition is a rendered view and a gesture's effect, and the evidence is the method's
written report of what it verified, never a screenshot ([`./tier-rules.md`](./tier-rules.md),
`bzh:visual-change-needs-a-render`). A caller dispatching `frontend-verifier` tells it to capture no screenshot and to
report in words; these steps hold over the agent's own screenshot defaults. Every browser method starts, from the
workspace root, from the same provisioned env with its services up and its shell vars sourced; the board and panel
methods drive the env's daemons, and the workshop needs no daemon:

```bash
winter provision <env>
winter service up <env> --wait   # the daemons, the dev servers, and the workshop
source <(winter env <env>)
```

`tool:service-up` serves each app twice — [`./tools.md`](./tools.md#toolservice-up) owns the two copies and their ports.
Verify a change to the app's source at the `ng serve` dev-server port each Setup below names, and reach for the daemon's
own port only when what changed is how the bundle is built or served. Drive only the env's own daemons — never the
hosted hub, whose standing rule `workspace:/context/project/hub-data-modes.md` owns.

### `web:manual-board`

**Surface.** The hub board — the Angular `hub` app — driven in a real browser against a running hub: what a view renders
from the hub's state, and what a gesture on it does to that state. Auth-gated rendering is
[`blizzard:manual-standing-idp`](./manual.md#blizzardmanual-standing-idp)'s, because the hub this method stands up
serves everything unauthenticated, and whether a seed itself renders faithfully is
[`blizzard-mock:manual-seeded-board`](./manual-mock.md#blizzard-mockmanual-seeded-board)'s.

**Setup.** The shared preamble above; the board is at `http://localhost:${BZ_HUB_WEB_PORT}/`. An empty store renders an
empty board, so seed the state the changed view needs with `tool:mock-data` —
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) owns the commands and the choice against the real
ingest path.

**Steps.**

1. State the changed behavior as an observable before opening the browser: this view, over this state, renders this — or
   this gesture yields this rendered result and this change in the hub's state.
2. Seed or drive the hub into that state.
3. Open the view that carries the change and confirm it renders the stated result, with no error in the browser console
   and no failed `/api` or `/runners` request in the network log.
4. Perform each changed gesture, confirm the rendered result, then read the effect back from the hub itself —
   `GET /api/chunks/<chunk-id>` or `uv run blizzard hub status` from `<env>/blizzard` — so a control that only repaints
   the page does not pass.
5. For a visual change, check the changed surface at each width the claim names, in the render
   [`./tier-rules.md`](./tier-rules.md) (`bzh:visual-change-needs-a-render`) admits.
6. Report what you verified, in words: the view's URL, the seed command, each stated observable and what rendered, each
   gesture and its read-back output, the widths checked, and the console and network results. The report is the method's
   evidence (`bzh:visual-change-needs-a-render`).

**Passes when.** Every stated observable renders in the browser from the worktree's current source, every driven
gesture's effect is confirmed in the hub's own state, and the console and network log stay clean throughout.

### `web:manual-panel`

**Surface.** The runner panel — the Angular `runner` app — driven in a real browser against a running runner: what its
Board, Events, Host and Settings tabs render from the runner's machine-local state, and what a gesture on it does to
that state. Whether a fleet seed itself renders coherently beside the board is
[`blizzard-mock:manual-seeded-fleet`](./manual-mock.md#blizzard-mockmanual-seeded-fleet)'s.

**Setup.** The shared preamble above; the panel is one app across the host's runners at
`http://localhost:${BZ_RUNNER_WEB_PORT}/`, its pages `board`, `board/chunk/<chunk-id>`, `events`, `host`, and `settings`
at the root, narrowed to one runner by the Runner filter (`?runner=<id>`) and to one project by the Project filter. Seed
the runner store with `tool:mock-data`'s `scenario fleet`, after the daemons are up —
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding both stores together owns the command and
why the order matters.

**Steps.**

1. State the changed behavior as an observable before opening the browser: this panel, over this runner state, renders
   this — or this gesture yields this rendered result and this change in the runner's state.
2. Seed or drive the runner into that state — a seed for a dormant one, a chunk walked through the env's hub
   ([`blizzard:manual-hub`](./manual.md#blizzardmanual-hub)'s loop walk) for what only a live lease renders.
3. Open the view that carries the change and confirm it renders the stated result, with no error in the browser console
   and no failed `/api` request in the network log.
4. Wait one tick — `tick end` in the runner's log marks it — and confirm the view still renders the stated result: the
   daemon reconciles its store every tick, and a panel correct only until then does not pass.
5. Perform each changed gesture, confirm the rendered result, then read the effect back from the runner itself with
   `curl -fs "http://127.0.0.1:$BZ_RUNNER_PORT/runners/<id>/api/dashboard"`. Do not clear a seeded runner's local pause
   as a gesture unless the pause control is what changed —
   [`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding an env whose daemons are up owns what
   that one click sets off.
6. For a visual change, check the changed surface at each width the claim names, in the render
   [`./tier-rules.md`](./tier-rules.md) (`bzh:visual-change-needs-a-render`) admits.
7. Report what you verified, in words: the view's URL, the seed command, each stated observable and what rendered before
   and after the tick, each gesture and its read-back output, the widths checked, and the console and network results.
   The report is the method's evidence (`bzh:visual-change-needs-a-render`).

**Passes when.** Every stated observable renders in the browser from the worktree's current source and still renders
after the next tick, every driven gesture's effect is confirmed in the runner's own state, and the console and network
log stay clean throughout.

### `web:manual-workshop`

**Surface.** A storied part, from the kit or a shared piece, rendered alone in the workshop: what it shows in each state
its stories carry, and how it answers when a reader changes its inputs through the controls. How a page composes the
part is `web:manual-board`'s or `web:manual-panel`'s. Whether every story still renders is `web:story-render`'s.

**Setup.** The shared preamble. The workshop is at `http://localhost:${BZ_STORYBOOK_PORT}/`, served by `service up`
([`./tools.md`](./tools.md#toolservice-up)) — never start a second one by hand in a feature env, since it moves to the
next free port without a word. No seed is needed, since a story carries its own data. Outside a feature environment,
`npm run storybook` in `web/` serves the checkout's workshop at `http://localhost:6006/`.

**Steps.**

1. Name every part the change touches, and every part that composes one of them and has stories of its own.
2. For each, open its stories and work through every state, confirming the change shows as intended and nothing else
   moved.
3. Push on each changed input through the controls, including values the stories do not hold: an empty string, a long
   one, a list of one, a list of many.
4. Switch the viewport to `phone` and `phone-sm` for any part whose layout answers to width, and to `desktop`.
5. Keep the browser console open throughout; a part that logs an error does not pass.
6. Report what you verified, in words: the commit, each story id and state, what rendered at each width the claim names,
   the inputs pushed through the controls, and the console result. The report is the method's evidence
   ([`./tier-rules.md`](./tier-rules.md), `bzh:visual-change-needs-a-render`).

**Passes when.** Every changed state renders as intended at every width it is claimed at, every control drives the part
without breaking it, and the console stays clean.

A frontend build also works here as it goes: `bzh:frontend-workshop-first` in
[`../../architecture/frontend-structure/kit.md`](../../architecture/frontend-structure/kit.md) owns when a build opens
the workshop and performs this method before the work is called done.

### `web:manual-form-adoption-census`

**Surface.** Whether every kit input control in the `hub`, `runner` and `fleet` app templates is on the shared forms
path (`[formField]` over a `*.form.ts` schema and a domain draft, inside a `KitField`), or is one of the declared kinds
that are not forms. It also covers whether the keyboard models those surfaces lean on hold under real Chromium input:
the members grid, the cadence and routine select lists, and the zone picker. It reads the tree and runs gates; it drives
no page.

**Setup.** The `blizzard` worktree of the feature env under census, provisioned, with `web/`'s dependencies installed.
No service needs to be up. Run every command from the worktree root.

**Not-a-form kinds.** A kit input control without `[formField]` is classified into exactly one of these, or it fails the
census:

1. **Filter** — a list's filter, whose pick narrows a read and saves nothing: the events, findings and proposals
   filters.
2. **Acts on pick** — a control whose pick is itself the whole operation, with no draft to hold: the urgencies default,
   the routine panel's default urgency, and the members grid's role select.
3. **Composite internals** — the inner control of a composite `FormValueControl` that is itself bound by its own caller:
   `config-mark-input` and `project-color-picker`.
4. **Lifecycle argument** — the urgency retire confirmation's destination, the argument of a lifecycle verb that is kept
   apart from the urgency's edit form.

**Steps.**

1. Record `git rev-parse HEAD`.
2. List every unbound kit input control, and every `fleet-kit-option` outside a bound `fleet-kit-option-group`, in a
   non-kit, non-story app template:

   ```bash
   python3 - <<'PY'
   import pathlib, re, subprocess
   root = 'web/projects'
   listed = subprocess.run(['git', 'ls-files', root], capture_output=True, text=True, check=True).stdout
   files = [f for f in listed.split() if '/src/' in f and f.endswith(('.html', '.ts'))]
   skip = re.compile(r'(^web/projects/fleet/src/lib/kit/|\.form-story\.html$|\.stories\.ts$|\.spec\.ts$)')
   tag = lambda name: re.compile(rf'<fleet-kit-{name}(?![-\w])(?:[^>"\']|"[^"]*"|\'[^\']*\')*>')
   control = tag('(?:text-input|select|checkbox|option-group|number-input|color-input|combobox)')
   group, option = tag('option-group'), tag('option')
   for path in sorted(f for f in files if not skip.search(f)):
       text = pathlib.Path(path).read_text()
       line = lambda m: text.count('\n', 0, m.start()) + 1
       for m in control.finditer(text):
           if '[formField]' not in m.group(0):
               print(f'{path}:{line(m)}: {m.group(0).split()[0][1:]}')
       for m in option.finditer(text):
           opened = list(group.finditer(text, 0, m.start()))
           g = opened[-1] if opened else None
           if g is None or '</fleet-kit-option-group>' in text[g.end():m.start()] or '[formField]' not in g.group(0):
               print(f'{path}:{line(m)}: fleet-kit-option (no bound group)')
   PY
   ```

   Read each hit in its template and classify it under the kinds above. The census reads the tree and changes nothing: a
   hit that fits no kind is a failure to report, not something the pass migrates on its way through.
3. List every app template that binds a control, then confirm each one wraps its bound controls in `fleet-kit-field`,
   and that its container's form comes from a `*.form.ts` schema whose draft type is imported from a `*.domain.ts`:

   ```bash
   git grep -l -E '\[formField\]' -- 'web/projects/*/src/**.html' ':!web/projects/fleet/src/lib/kit/**' ':!*.form-story.html'
   ```

4. Run [`web:structural-gate`](../blizzard.md) and confirm `DOMAIN_BOUNDARY_EXEMPT` is empty:
   `grep -n 'const DOMAIN_BOUNDARY_EXEMPT' web/scripts/structural-gate.js` reads `= [];`.
5. Confirm the superseded hand-built form inventory is gone:
   `git grep -n -E 'AcceptSubmission|AcceptMode|missingRequired|invalidNumbers' -- web/` has no hits.
6. Run the four keyboard sweeps, each from `web/` with
   `npx ng test <project> --browsers=ChromiumHeadless --watch=false --include=<spec>`: the members grid (`hub`,
   `projects/hub/src/app/admin/members/members-table.shell-sweep.spec.ts`, and `fleet`,
   `projects/fleet/src/lib/kit/kit-grid.shell-sweep.spec.ts`), the cadence and routine select lists (`fleet`,
   `projects/fleet/src/lib/kit/kit-select-list.shell-sweep.spec.ts`), and the zone picker (`fleet`,
   `projects/fleet/src/lib/kit/kit-combobox.shell-sweep.spec.ts`).

**Evidence.** Record the revision, the commands as run, one line per step-2 hit giving its path, line, control, kind,
and the reason that kind was reached, and each other step's result. Keep the record with the change under review — the
pull request or commit that claims this method — rather than in this file, which holds no per-run readings
([`../../standards/prose-budget.md`](../../standards/prose-budget.md)).

**Passes when.** Every step-2 hit classifies under one of the four kinds, every bound template composes `KitField` over
a schema and a domain draft, the structural gate passes with no exemption, the superseded inventory has no hits, and the
four sweeps pass.
