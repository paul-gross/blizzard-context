# The eager shell

What the hub's always-loaded shell may import, and how chrome it needs only on interaction is loaded. A spoke of the
[frontend structure hub](../frontend-structure.md); the rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Eager shell code imports `fleet/shell` (`bzh:frontend-eager-shell-entry`)

**Rule.** A module statically reachable from the hub's `main.ts` — the hub's `shell/` folder (the app root, its config
and route table, and the nav chrome the root mounts outside a `@defer` block) and the hub modules they reach
(`core/auth/` — among them the no-access screen and the tenant picker the root renders in place of the shell, and the
tenant context and interceptor every hub call and the live stream read — and the board, spend, health, and questions
reads) — imports the `fleet` library only through the `fleet/shell` entry point (`projects/fleet/src/shell-api.ts`, a
file-by-file list of named re-exports); a `fleet` module on that eager path imports a sibling by file
(`../../kit/kit-button`), never through a sub-barrel (`../../kit`); and chrome the shell needs only on interaction — the
profile menu and the mobile titlebar, with the CDK menu stack behind them — is `@defer`-loaded.

**Why.** esbuild keeps every decorated module a barrel on the eager path names, whether or not the shell reads its
export, so one `from 'fleet'` in the app root ships every feature area before the board renders. A lazy route page keeps
importing `fleet`: a barrel behind a `loadComponent` boundary costs the initial chunk nothing.

**Scope.** Binds the hub app's eager shell and the `fleet` modules `shell-api.ts` reaches; a lazy route page, the
contents of a `@defer` block, and the runner app's own shell are outside it. `bzh:generated-client`'s `'../api/hub'`
import stays as it is.

**Detect.** `from 'fleet'` in `hub/src/main.ts`, `shell/app.ts`, `shell/app.config.ts`, `shell/app.routes.ts`, or a nav
component the app root mounts outside a `@defer` block; a `from '../<feature>'` sub-barrel import in a module
`shell-api.ts` reaches; an export added to `shell-api.ts` that only a lazy page uses. Each surfaces as a forbidden
module in the initial chunk under `web:bundle-composition` (`npm run bundle-check`,
[`../../verification/blizzard.md`](../../verification/blizzard.md)), which names the module and the file that imports
it; the `initial` budget in `angular.json` is the size backstop for growth the forbidden list does not name.

**Do.** `shell/app.ts` imports `AppShell` from `'fleet/shell'` and `injectMeQuery` from `'../core/auth/me.query'`;
`app.html` mounts `<app-nav-menu>` inside `@defer (on immediate)` wrapped in
`<ng-container ngProjectAs="[header-trailing]">`, because a `@defer` block does not carry its root node's slot attribute
through content projection; `core/auth/no-access.ts` and `core/auth/tenant-picker.ts` import `KitButton` from
`'fleet/shell'`, and `core/auth/tenant.interceptor.ts` takes `hubClient`, `FetchEventSource`, and `EVENT_SOURCE_FACTORY`
from it, so the one tenant context names the tenant on the generated client's requests and on the live stream's own
`fetch`. The project lens is the same shape: `core/project-lens.ts` derives the lensed project from the URL's
`/p/{project}/` segment alone, and `shell/app.config.ts`'s `provideProjectLens()` hands it to `fleet` through the
`fleet/shell` seams `HUB_PROJECT_FILTER`, which every read the lens narrows injects, and `IN_APP_LINK`, which keeps a
link under the lens — so no `fleet` module imports the hub's lens, and the runner app, providing neither, keeps every
read whole.

**Don't.** `import { AppShell } from 'fleet'` in `shell/app.ts` — one line that puts the chunk-detail and transcripts
barrels back into the initial chunk; an eager import of the hub's `garden/` or `graphs/` folder, which brings the whole
feature and dagre with it; a re-export shim that still names the menu components eagerly, which keeps the CDK menu stack
eager even though nothing renders it until a click.

**See also.** `bzh:frontend-disjoint-diffs` — the sub-barrels this rule routes the eager path around still own each
feature's public surface for every lazy consumer.
