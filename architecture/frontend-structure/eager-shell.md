# The eager shell

What an app's always-loaded shell may import, how chrome it needs only on interaction is loaded, and how the project
lens the shell derives reaches a view. A spoke of the [frontend structure hub](../frontend-structure.md); each rule
follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Eager shell code imports `fleet/shell` (`bzh:frontend-eager-shell-entry`)

**Rule.** A module statically reachable from an app's `main.ts` imports the `fleet` library only through an entry point;
a `fleet` module on that eager path imports a sibling by file (`../../kit/kit-button`), never through a sub-barrel
(`../../kit`); and chrome the shell needs only on interaction — the profile menu and the mobile titlebar, with the CDK
menu stack behind them — is `@defer`-loaded.

- **The hub.** Its `shell/` folder (the app root, its config and route table, and the nav chrome the root mounts outside
  a `@defer` block) and the hub modules they reach (`core/auth/` — among them the no-access screen and the tenant picker
  the root renders in place of the shell, and the tenant context and interceptor every hub call and the live stream read
  — the board, spend, health, and questions reads, and `runners/runner-host-names.ts` with the `runners/hosts.query.ts`
  read it provides from `shell/app.config.ts`, so every runner reference names its host) import through `fleet/shell`
  (`projects/fleet/src/shell-api.ts`, a file-by-file list of named re-exports).
- **The runner.** Its `shell/` folder (the same parts) and the `core/` modules they reach (the host, lease, and status
  reads, the session and its recovery, the live stream, and the panel reads) import through `fleet/shell` for what both
  apps read and through `fleet/runner-shell` (`projects/fleet/src/runner-shell-api.ts`) for what only the runner does —
  the runner API and client, its live-stream vocabulary, and its query keys. The runner's exports sit in a second file
  because esbuild keeps every module a re-export names, so the same exports in `shell-api.ts` would grow the hub's
  initial chunk.

**Why.** esbuild keeps every decorated module a barrel on the eager path names, whether or not the shell reads its
export, so one `from 'fleet'` in the app root ships every feature area before the board renders. A lazy route page keeps
importing `fleet`: a barrel behind a `loadComponent` boundary costs the initial chunk nothing.

**Scope.** Binds each app's eager shell and the `fleet` modules `shell-api.ts` and `runner-shell-api.ts` reach; a lazy
route page and the contents of a `@defer` block are outside it. `bzh:generated-client`'s `'../api/hub'` import stays as
it is.

**Detect.** `from 'fleet'` in either app's `main.ts`, `shell/app.ts`, `shell/app.config.ts`, `shell/app.routes.ts`, a
nav component the app root mounts outside a `@defer` block, or a `core/` module they reach; a `from '../<feature>'`
sub-barrel import in a module either entry file reaches; an export added to an entry file that only a lazy page uses; an
export only the runner reads added to `shell-api.ts`. Each surfaces as a forbidden module in the initial chunk under
`web:bundle-composition` (`npm run bundle-check`, [`../../verification/blizzard.md`](../../verification/blizzard.md)),
which names the module and the file that imports it; the `initial` budget in `angular.json` is the size backstop for
growth the forbidden list does not name.

**Do.** The runner's `shell/app.ts` imports `AppShell` from `'fleet/shell'`, its `core/host.query.ts` takes `runnerApi`
from `'fleet/runner-shell'`, its `app.html` mounts `<app-mobile-titlebar>` inside `@defer (on immediate)` with a
fixed-height placeholder, and `nav/app-header.html` mounts `<app-profile-menu>` the same way. The hub's `shell/app.ts`
imports `AppShell` from `'fleet/shell'` and `injectMeQuery` from `'../core/auth/me.query'`; `app.html` mounts
`<app-nav-menu>` inside `@defer (on immediate)` wrapped in `<ng-container ngProjectAs="[header-trailing]">`, because a
`@defer` block does not carry its root node's slot attribute through content projection; `core/auth/no-access.ts` and
`core/auth/tenant-picker.ts` import `KitButton` from `'fleet/shell'`, and `core/auth/tenant.interceptor.ts` takes
`hubClient`, `FetchEventSource`, and `EVENT_SOURCE_FACTORY` from it, so the one tenant context names the tenant on the
generated client's requests and on the live stream's own `fetch`.

**Don't.** `import { AppShell } from 'fleet'` in `shell/app.ts` — one line that puts the chunk-detail and transcripts
barrels back into the initial chunk; an eager import of the hub's `garden/` or `graphs/` folder, which brings the whole
feature and dagre with it; a re-export shim that still names the menu components eagerly, which keeps the CDK menu stack
eager even though nothing renders it until a click.

**See also.** `bzh:frontend-disjoint-diffs` — the sub-barrels this rule routes the eager path around still own each
feature's public surface for every lazy consumer. `bzh:frontend-project-lens-seam` below — the project lens reaches
`fleet` through the same entry point's seams.

## A view follows the project lens through its `fleet/shell` seams (`bzh:frontend-project-lens-seam`)

**Rule.** Make a hub view, a read, or a link follow the project lens by injecting the seams `fleet/shell` exports —
`HUB_PROJECT_FILTER` (`injectProjectFilter()`) for the project a read narrows to, `IN_APP_LINK` (the `lensLink` pipe)
for a link that keeps the lens — and never by reading the URL's `/p/{project}/` segment yourself. Only
`core/project-lens.ts` derives the lens from the URL, and `shell/app.config.ts`'s `provideProjectLens()` provides both
seams from it; no `fleet` module imports `core/project-lens.ts`.

**Why.** One module parsing the lens segment keeps every view agreeing on which project the page is under, and a `fleet`
module that took the lens from a seam rather than the hub's own lens stays servable by the runner app, which provides
neither seam and so keeps every read whole and every link as written.

**Detect.**

- A `fleet` or hub module other than `core/project-lens.ts` reading `/p/`, `paramMap`, or the router URL to find the
  project.
- An import of `core/project-lens` from under `projects/fleet/`.
- A lensed read whose query key omits the project — not built through `lensedKey` — so two lenses share a cache entry.
- An absolute in-app `routerLink` in a view the lens covers that does not pass through `lensLink` or `IN_APP_LINK`.

**Do.** `admin/changes/changes.query.ts` takes the project from `injectProjectFilter()`, keys its read
`lensedKey(hubConfigChangesKey, project)`, and sends the project as `?project=`; a template links
`[routerLink]="'/board' | lensLink"`.

**Don't.** A query that splits `router.url` on `/` to find the project — a second parser that drifts from the lens the
moment the URL shape changes, and that writes the hub's URL into a `fleet` view the runner app also serves.

**See also.** `bzh:frontend-eager-shell-entry` above — what the shell may import from `fleet`, the seams' entry point
among it.
