# The eager shell

What the hub's always-loaded shell may import, and how chrome it needs only on interaction is loaded. A spoke of the
[frontend structure hub](../frontend-structure.md); the rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Eager shell code imports `fleet/shell` (`bzh:frontend-eager-shell-entry`)

**Rule.** A module statically reachable from the hub's `main.ts` — the app root, its config and route table, and the nav
chrome the root mounts outside a `@defer` block — imports the `fleet` library only through the `fleet/shell` entry point
(`projects/fleet/src/shell-api.ts`, a file-by-file list of named re-exports); a `fleet` module on that eager path
imports a sibling by file (`../kit/kit-button`), never through a sub-barrel (`../kit`); and chrome the shell needs only
on interaction — the profile menu and the mobile titlebar, with the CDK menu stack behind them — is `@defer`-loaded.

**Why.** esbuild keeps every decorated module a barrel on the eager path names, whether or not the shell reads its
export, so one `from 'fleet'` in the app root ships every feature area before the board renders. A lazy route page keeps
importing `fleet`: a barrel behind a `loadComponent` boundary costs the initial chunk nothing.

**Scope.** Binds the hub app's eager shell and the `fleet` modules `shell-api.ts` reaches; a lazy route page, the
contents of a `@defer` block, and the runner app's own shell are outside it. `bzh:generated-client`'s `'../api/hub'`
import stays as it is.

**Detect.** `from 'fleet'` in `hub/src/main.ts`, `app.ts`, `app.config.ts`, `app.routes.ts`, or a nav component the app
root mounts outside a `@defer` block; a `from '../<feature>'` sub-barrel import in a module `shell-api.ts` reaches; an
export added to `shell-api.ts` that only a lazy page uses. Each surfaces as a forbidden module in the initial chunk
under `web:bundle-composition` (`npm run bundle-check`,
[`../../verification/blizzard.md`](../../verification/blizzard.md)), which names the module and the file that imports
it; the `initial` budget in `angular.json` is the size backstop for growth the forbidden list does not name.

**Do.** `app.ts` imports `AppShell` and `injectMeQuery` from `'fleet/shell'`; `app.html` mounts `<app-nav-menu>` inside
`@defer (on immediate)` wrapped in `<ng-container ngProjectAs="[header-trailing]">`, because a `@defer` block does not
carry its root node's slot attribute through content projection; `auth/pending-lobby.ts` imports `KitButton` from
`'../kit/kit-button'`.

**Don't.** `import { AppShell } from 'fleet'` in `app.ts` — one line that puts chunk-detail, garden, graphs, transcripts
and dagre back into the initial chunk; a re-export shim that still names the menu components eagerly, which keeps the
CDK menu stack eager even though nothing renders it until a click.

**See also.** `bzh:frontend-disjoint-diffs` — the sub-barrels this rule routes the eager path around still own each
feature's public surface for every lazy consumer.
