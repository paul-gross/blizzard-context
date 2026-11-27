# The eager shell

What an app's always-loaded shell may import, the entry points every consumer reads `fleet` through, how chrome the
shell needs only on interaction is loaded, and how the project lens the shell derives reaches a view. A spoke of the
[frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Eager shell code imports `fleet/shell` (`bzh:frontend-eager-shell-entry`)

**Rule.** A module statically reachable from an app's `main.ts` imports the `fleet` library's values only through
`fleet/shell` and, for the runner, `fleet/runner-shell` (an `import type` may name any entry, since it is erased before
bundling); a `fleet` module on that eager path imports a sibling by file (`../../kit/kit-button`), as every `fleet`
module does (`bzh:frontend-weight-class-entries` below); and chrome the shell needs only on interaction — the profile
menu and the mobile titlebar, with the CDK menu stack behind them — is `@defer`-loaded.

- **The hub.** Its `shell/` folder (the app root, its config and route table, and the nav chrome the root mounts outside
  a `@defer` block) and the hub modules they reach (`core/auth/` — among them the no-access screen and the tenant picker
  the root renders in place of the shell, and the tenant context and interceptor every hub call and the live stream read
  — the board, spend, health, and questions reads, and `runners/runner-host-names.ts` with the `runners/hosts.query.ts`
  read it provides from `shell/app.config.ts`, so every runner reference names its host) import through `fleet/shell`
  (`projects/fleet/src/shell-api.ts`, a file-by-file list of named re-exports).
- **The runner.** Its `shell/` folder (the same parts) and the `core/` modules they reach (the host, lease, and status
  reads, the session and its recovery, the live stream, and the panel reads) import through `fleet/shell` for what both
  apps read and through `fleet/runner-shell` (`projects/fleet/src/runner-shell-api.ts`) for what only the runner does —
  the runner API and client and its live-stream vocabulary. The shared live mechanics — the SSE transport, the
  invalidation spine, the coalesce window, and the plane-root chunk key helpers — sit on `fleet/shell`, which both apps'
  live services read; the query keys are each app's own. The runner's exports sit in a second file because esbuild keeps
  every module a re-export names, so the same exports in `shell-api.ts` would grow the hub's initial chunk.

**Why.** esbuild keeps every decorated module a barrel on the eager path names, whether or not the shell reads its
export, so one weight-class entry in the app root ships all of that entry's members before the board renders.

**Scope.** Binds each app's eager shell and the `fleet` modules `shell-api.ts` and `runner-shell-api.ts` reach; a lazy
route page and the contents of a `@defer` block are outside it. `bzh:generated-client` illustrates a shell import.

**Detect.**

- A value import of any other entry from `main.ts`, `shell/app.ts`, `shell/app.config.ts`, `shell/app.routes.ts`, a nav
  component the app root mounts outside a `@defer` block, or a `core/` module they reach: `web:bundle-composition`
  (`npm run bundle-check`, [`../../verification/blizzard.md`](../../verification/blizzard.md)) fails on an `entries/`
  file or the `fleet` root in the initial chunk, naming the file that imports it.
- An export added to `shell-api.ts` or `runner-shell-api.ts` that only a lazy page uses, or one only the runner reads
  added to `shell-api.ts`: a review question. The gate catches it only where the module it brings is on the forbidden
  list, and the `initial` budget in `angular.json` is the size backstop.

**Do.** The runner's `shell/app.ts` imports `AppShell` from `'fleet/shell'`, its `core/host.query.ts` takes `runnerApi`
from `'fleet/runner-shell'`, its `app.html` mounts `<app-mobile-titlebar>` inside `@defer (on immediate)` with a
fixed-height placeholder, and `nav/app-header.html` mounts `<app-profile-menu>` the same way. The hub's `shell/app.ts`
imports `AppShell` from `'fleet/shell'` and `injectMeQuery` from `'../core/auth/me.query'`; `app.html` mounts
`<app-nav-menu>` inside `@defer (on immediate)` wrapped in `<ng-container ngProjectAs="[header-trailing]">`, because a
`@defer` block does not carry its root node's slot attribute through content projection; `core/auth/no-access.ts` and
`core/auth/tenant-picker.ts` import `KitButton` from `'fleet/shell'`, and `core/auth/tenant.interceptor.ts` takes
`hubClient`, `FetchEventSource`, and `EVENT_SOURCE_FACTORY` from it, so the one tenant context names the tenant on the
generated client's requests and on the live stream's own `fetch`.

**Don't.** `import { errorMessage } from 'fleet/core'` in `shell/app.ts` — one line that puts every decorated part that
entry names into the initial chunk; an eager import of the hub's `garden/` or `graphs/` folder, which brings the whole
feature and dagre with it; a re-export shim that still names the menu components eagerly, which keeps the CDK menu stack
eager even though nothing renders it until a click.

**See also.** `bzh:frontend-weight-class-entries` below — the entries every consumer off the eager path imports.
`bzh:frontend-project-lens-seam` below — the app scope reaches `fleet` through the same entry point's seams.

## `fleet` is imported through weight-class entry points (`bzh:frontend-weight-class-entries`)

**Rule.** Consume `fleet` only through a `fleet/<entry>` path, never a root and never a relative path into the library,
and group an entry's members by the heavy dependencies they reach, so importing an entry costs about what using it
costs.

- **An entry is a file** under `fleet/src/entries/`, named for its specifier, holding a file-by-file list of named
  re-exports, with its specifier a `paths` entry in `web/tsconfig.json`. A new entry also takes a line in
  `public-api.ts` and in each path map that overrides `tsconfig.json`'s wholesale: `web/tsconfig.exemplars.json` and
  both heredocs of `web/scripts/exemplar-tree.sh`.
- **An exported symbol belongs to one entry.** `fleet/shell` and `fleet/runner-shell`, files beside `entries/`,
  re-export eager subsets of the entries' symbols.
- **An entry's members cost about the same to import.** The packages `@angular/cdk`, `@angular/aria`, and
  `@angular/forms` are the first cut, and `fleet/kit` reaches none of them. Within one package set, a member that would
  make the others' consumers download much more takes its own entry: each heavy widget family (`fleet/kit/<family>`),
  `fleet/viewport/menu` with the CDK menu stack beside `fleet/viewport`'s service, and `fleet/chunk-page/view`, the
  composed page beside `fleet/chunk-page`'s data seams. The weight, not the folder, decides the boundary.
- **Inside `fleet/src/lib`, a module imports a sibling area by file**, never through an entry. `fleet/testing`, the
  test-helper path outside this model, is the one `fleet/*` import allowed there, and only from a spec or a story.
- **`public-api.ts` is the library build's aggregate** (`ng-package.json`'s entry file), one `export *` line per entry.
  Nothing imports it, and no `fleet` path names it.
- **`lib/api/` keeps its generated barrels**, whose weight is the generated files alone.

**Why.** esbuild splits code per file and keeps every decorated module a barrel names, so a lazy page importing one
symbol from a barrel downloads the barrel's whole surface. A single entry per symbol would cost less still but leaves no
surface to name; a weight class keeps a short specifier and bounds what a page pays for it.

**Detect.**

- `'fleet'` named by an import, a re-export, a dynamic `import()`, or an `import('fleet')` type: the
  `fleet-root/no-root-import` lint rule, under `web:lint` in every project and under `blizzard:exemplar-check` in the
  exemplars.
- `fleet/kit`'s closure reaching `@angular/cdk`, `@angular/aria`, or `@angular/forms`, or the hub build holding no
  `fleet/kit` entry: `web:bundle-composition`.
- A lazy entry's closure reaching `fleet/src/public-api.ts`: `web:bundle-composition`, which also prints each lazy
  entry's closure and that of each entry file in the build, the evidence for whether an entry's members still cost alike
  ([`../../verification/blizzard/commands/web/static-checks.md`](../../verification/blizzard/commands/web/static-checks.md)).
- A `fleet/*` import from `fleet/src/lib/` other than a spec's or story's `fleet/testing`: `web:structural-gate`'s
  package-layers sweep.
- A member much heavier than its entry's others, in an entry other than `fleet/kit`, a symbol exported by two entries,
  or a new entry missing a path map or its `public-api.ts` line: review questions.

**Do.** A new menu-backed control in `fleet/src/lib/kit/` is exported from `entries/kit/menu.ts`; a lazy page imports
`KitButton` from `'fleet/kit'` and `KitMenu` from `'fleet/kit/menu'`.

**Don't.** A menu-backed part added to `entries/kit.ts` so that one import line serves it — every page that renders a
button then downloads the CDK menu stack.

**See also.** `bzh:frontend-disjoint-diffs` ([`./disjoint-diffs.md`](./disjoint-diffs.md)) — an entry is a feature's one
shared line. `bzh:frontend-eager-shell-entry` above — the eager path's own two entries.

## A view follows the project lens through its `fleet/shell` seams (`bzh:frontend-project-lens-seam`)

**Rule.** Make a hub view, a read, or a link follow its app's scope through its scope seams — `HUB_PROJECT_FILTER`
(`injectProjectFilter()`, the hub kernel's seam in `hub/src/app/core/project-filter.ts`) for the project a read narrows
to, `APP_SCOPE` (on `fleet/shell`) for a link that keeps the scope: `appLink` for a cross-page link or navigation,
`appPath` only where an anchor deliberately keeps the current query through `queryParamsHandling` — and never by reading
the URL's `/p/{project}/` segment yourself. An app supplies policy only: the hub a path rewrite (its project prefix),
the runner a scope query (`?runner=`, `?project=`). Only `core/project-lens.ts` derives the lens from the URL, and
`shell/app.config.ts`'s `provideProjectLens()` provides the hub's seams from it; no `fleet` module imports
`core/project-lens.ts` or names a policy's query keys.

**Why.** One module parsing the lens segment keeps every view agreeing on which project the page is under, and a `fleet`
module that takes the scope from a seam rather than an app's own stays servable by both apps. The runner keeps its
display context on a shared link only because composition lives once in `fleet`; an app with no policy keeps every link
as written.

**Detect.**

- A `fleet` or hub module other than `core/project-lens.ts` reading `/p/`, `paramMap`, or the router URL to find the
  project.
- An import of `core/project-lens` from under `projects/fleet/`.
- A lensed read whose query key omits the project — not built through `lensedKey` — so two lenses share a cache entry.
- An absolute in-app `routerLink` in a view the scope covers that does not pass through `appLink` or `appPath`.

**Do.** `admin/changes/changes.query.ts` takes the project from `injectProjectFilter()`, keys its read
`lensedKey(hubConfigChangesKey, project)` (both from the hub's `core/query-keys.ts`), and sends the project as
`?project=`; a template links `[routerLink]="'/board' | appLink: { chunk: id }"`.

**Don't.** A query that splits `router.url` on `/` to find the project — a second parser that drifts from the lens the
moment the URL shape changes, and that writes the hub's URL into a `fleet` view the runner app also serves.

**See also.** `bzh:frontend-eager-shell-entry` above — what the shell may import from `fleet`, the seams' entry point
among it.
