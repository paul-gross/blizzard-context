# Placement

Where a unit of web code lives — in `fleet` or in an app, and in which folder of its project — what that folder may
import, and how a view both daemons serve is written once. A spoke of the
[frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Code lives with the daemons that serve it (`bzh:frontend-placement`)

**Rule.** `fleet` holds only what both apps reach: each direct child of `fleet/src/lib/` — a feature folder or a
top-level module — or, under the grouping folders `core/`, `chunk/`, and `shell/`, each child of that folder, is reached
by the non-spec code of both `hub` and `runner`, and no `fleet` file imports from `hub` or `runner`. App-local code
lives in its app, pages, queries, and components together. A view both daemons serve is written once in `fleet` and
takes the daemon as an injected seam — the generated client, the cache-key plane, and an optional actions port — rather
than being copied per app.

**Why.** A feature folder in `fleet` that one app reaches is that app's code in the wrong place: it widens the shared
surface, hides the app's real boundary from the eager-shell and bundle checks, and invites a per-app mirror when the
other daemon later needs a near copy. A per-app copy of a shared view drifts — the two pages disagree on tabs,
selection, and copy until one is fixed and the other is not.

**Scope.** Binds those units of `fleet/src/lib/` and every `fleet` import. A mixed folder reached by both apps passes at
the folder level, so shared infrastructure (`kit/`, `core/viewport/`, `sse/`) may hold a file only one app uses.
Spec-support (`testing/`, which has its own `fleet/testing` entry) and declaration-free re-export barrels
(`core/format/`) are exempt, each with its reason named in the sweep.

**Detect.** The placement sweep inside `web:structural-gate`
([`../../verification/blizzard.md`](../../verification/blizzard.md)): it resolves reach to the symbol through the
`fleet` barrels, fails naming a unit and the single app that reaches it (or no app when it is dead), and fails any
`fleet` file importing an app project. Its self-test must-catches a single-app unit and a `fleet`→app import and
must-passes a both-app unit.

**Do.** `ChunkTranscriptsContainer` and the chunk page in `fleet/src/lib/chunk/chunk-page/` take their client and plane
from the daemon the route provides; the hub supplies an actions port and the runner supplies none, so one page renders
read-only on the runner. The hub's gardening, graphs, admin, and board reads live under `hub/src/app/`.

**Don't.** A second chunk page in `runner/` that mirrors the hub's, or a gardening folder left in `fleet` because it was
written there first.

**See also.**

- `bzh:frontend-eager-shell-entry` — the hub modules that moved out of `fleet` still reach `fleet` on the eager path
  only through `fleet/shell`.
- `bzh:frontend-package-layers` below — which folder of its project a unit lands in, and what that folder may import.

## Folders import only what their project's layer table allows (`bzh:frontend-package-layers`)

**Rule.** Import another folder of the same project only along an edge its project's layer table below declares, and
move anything two features both need down into the project's kernel (`core/`) rather than adding a feature-to-feature
edge. A unit is a folder below the project's source root — `fleet/src/lib/`, `hub/src/app/`, or `runner/src/app/` — and
a file belongs to the longest unit that prefixes its path, so `garden` owns only the files directly in `garden/`. Every
folder directly under a source root, or under `garden/`, is a unit, and no file sits loose at a source root. Every unit
may also import its project's kernel, and the kernel imports no other unit. An app reaches `fleet` only through the
`fleet`, `fleet/shell`, and `fleet/testing` entry points, never by a relative path.

`fleet`, rooted at `fleet/src/lib/`, has no kernel, so every edge is listed; a `*.spec.ts` in any unit may also import
`testing`:

| Unit          | Layer        | May import                          |
| ------------- | ------------ | ----------------------------------- |
| `api`         | L0           | —                                   |
| `kit`         | L0           | —                                   |
| `core`        | L1           | `api`, `kit`                        |
| `sse`         | L2           | `api`, `core`                       |
| `transcripts` | L2           | `api`, `core`, `kit`                |
| `chunk`       | L2           | `api`, `core`, `kit`, `transcripts` |
| `shell`       | L3           | `api`, `core`, `kit`                |
| `testing`     | spec support | `api`                               |

`hub`, rooted at `hub/src/app/`, with kernel `core`:

| Unit               | Layer | May import                                                                                                                                                           |
| ------------------ | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `core`             | L0    | —                                                                                                                                                                    |
| `admin`            | L1    | —                                                                                                                                                                    |
| `board`            | L1    | `runners`                                                                                                                                                            |
| `demo`             | L1    | —                                                                                                                                                                    |
| `events`           | L1    | —                                                                                                                                                                    |
| `graphs`           | L1    | —                                                                                                                                                                    |
| `login`            | L1    | —                                                                                                                                                                    |
| `runners`          | L1    | —                                                                                                                                                                    |
| `garden/core`      | L1    | —                                                                                                                                                                    |
| `garden/proposals` | L1    | `garden/core`                                                                                                                                                        |
| `garden/runs`      | L1    | `garden/core`                                                                                                                                                        |
| `garden/scopes`    | L1    | `garden/core`                                                                                                                                                        |
| `garden/findings`  | L1    | `garden/core`, `garden/proposals`                                                                                                                                    |
| `garden/routines`  | L1    | `garden/core`, `garden/runs`, `graphs`                                                                                                                               |
| `garden`           | L1    | `garden/findings`, `garden/proposals`, `garden/routines`, `garden/runs`, `garden/scopes`                                                                             |
| `shell`            | L2    | `admin`, `board`, `demo`, `events`, `garden`, `garden/findings`, `garden/proposals`, `garden/routines`, `garden/runs`, `garden/scopes`, `graphs`, `login`, `runners` |

`runner`, rooted at `runner/src/app/`, with kernel `core`:

| Unit           | Layer | May import                                  |
| -------------- | ----- | ------------------------------------------- |
| `core`         | L0    | —                                           |
| `asks`         | L1    | —                                           |
| `environments` | L1    | —                                           |
| `events`       | L1    | —                                           |
| `machine`      | L1    | —                                           |
| `status`       | L1    | —                                           |
| `board`        | L1    | `asks`, `environments`, `machine`, `status` |
| `shell`        | L2    | `board`, `events`, `machine`                |

**Why.** A declared one-way folder graph lets a feature be read, moved, or lazy-loaded without dragging its importers
along. Without it the app root drifts back into being both shell and kernel — importing every feature while every
feature imports it — and folder cycles form unseen.

**Scope.** Binds every git-tracked `.ts` and `.css` file below the three source roots and its relative imports: static,
type-only, dynamic `import()`, and CSS `@import`. The `fleet` barrels (`fleet/src/public-api.ts`, `shell-api.ts`) and
each app's `src/main.ts` sit outside the source roots and are not bound. Which project a unit belongs to is
`bzh:frontend-placement`'s call; this rule governs the edges inside one project. A new edge or unit changes the gate's
table and this one in the same change.

**Detect.** The package-layers sweep inside `web:structural-gate` (`web/scripts/structural-gate.js`,
[`../../verification/blizzard.md`](../../verification/blizzard.md)) carries the three tables as data, with no exemption
list, and fails on:

- an import from one unit into another that its row does not list and that is not the kernel or a spec's `testing`;
- a file in no unit — loose at a source root, or in a folder the table does not declare;
- a table unit with no folder, or an edge naming an undeclared unit;
- a cycle in the table, counting every unit's implicit edge to the kernel;
- a relative import that leaves its project.

Its self-test, `assertPackageLayersDetectorWorks`, must-catches an undeclared feature-to-feature import, a stray
app-root file, and a planted table cycle, and must-passes a declared edge, a kernel import, and a spec importing
`testing`.

**Do.** `hub/src/app/board/board-page.ts` and `runners/runner-rows.ts` both read `core/chunks.query.ts`: the chunks read
two features need sits in the kernel, so `board` → `runners` stays the only edge between them. The routine detail in
`garden/routines/` opens the run dialog from `garden/runs/` along the declared `garden/routines` → `garden/runs` edge.

**Don't.** `runners/runner-rows.ts` importing `board/chunks/chunks.query.ts`, the back edge that makes `board` and
`runners` a cycle; a helper file dropped directly into `hub/src/app/` beside `shell/` and `core/`; a `runner` feature's
query keys kept in that feature's folder while the kernel's live-updates module imports them.

**See also.**

- `bzh:frontend-placement` above — whether a unit belongs in `fleet` or in an app at all.
- `bzh:frontend-eager-shell-entry` ([`./eager-shell.md`](./eager-shell.md)) — what the hub's `shell/` may import from
  `fleet` on the eager path.
- `bzh:shared-kernel` ([`../clean-architecture.md`](../clean-architecture.md)) — the daemons' kernel, which imports no
  daemon package, as this rule's `core/` imports no feature.
