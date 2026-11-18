# The domain boundary

How the Angular suite relates to the hub and runner wire — where the wire is read and translated, which concept files
may import what, which files call the generated client, and how a vocabulary the client does not know is handled. A
spoke of the [frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## The frontend owns its domain and reads the wire at one boundary (`bzh:frontend-domain-boundary`)

**Rule.** The frontend models its own domain and translates to and from the wire at one boundary. Only data-access files
(`*.query.ts`, `*.mutations.ts`), translators (`*.translate.ts`), their focused specs, the generated client
(`fleet/src/lib/api/{hub,runner}/`), and the test transport (`fleet/src/lib/testing/transport/`) consume a generated
wire type; every other file — a domain file, form, service, model, component, view, story, ordinary spec, or test helper
— works in domain types. Generated client functions are called only from data-access files. Within the boundary:

- A wire vocabulary becomes a closed domain union with an explicit unknown member, and the translator is the one place
  an unforeseen wire value is handled (`bzh:frontend-open-vocabulary`).
- A judgment the wire already carries, such as a chunk's `terminal` or a member's `revocable`, is translated from its
  field, never re-derived from raw values.
- A judgment the frontend makes from what it holds is a pure function in a `*.domain.ts`, pinned by its spec.

Each concept file has a fixed dependency budget:

| Concept file                                   | Imports wire types | Imports Angular               | Pinned by                                   |
| ---------------------------------------------- | ------------------ | ----------------------------- | ------------------------------------------- |
| `<concept>.query.ts`, `<concept>.mutations.ts` | yes                | yes                           | its focused spec                            |
| `<concept>.translate.ts`                       | yes                | no                            | `<concept>.translate.spec.ts`, no `TestBed` |
| `<concept>.domain.ts`                          | no                 | no                            | `<concept>.domain.spec.ts`, no `TestBed`    |
| `<concept>.form.ts` (validation rules)         | no                 | `@angular/forms/signals` only | `<concept>.form.spec.ts`                    |
| `<concept>.service.ts`                         | no                 | yes                           | `<concept>.service.spec.ts`                 |
| `*.model.ts`, components, views                | no                 | per their own rules           | their specs                                 |

A concept's files sit in its feature folder, beside its `*.query.ts` and `*.model.ts`; which folder that is, and what it
may import, is `bzh:frontend-placement`'s and `bzh:frontend-package-layers`' call ([placement.md](./placement.md)). A
concept two features share goes down to the project's kernel, or to `fleet` where both apps reach it.

A focused boundary spec (`*.query.spec.ts`, `*.mutations.spec.ts`, `*.translate.spec.ts`) may import wire types to pin
its boundary's contract. Wire builders live in pure `*.translate.ts` fixture modules; a component or model spec and a
story build their presentation inputs from domain builders, and a component spec may hand those wire fixtures to its
stubbed HTTP transport without importing a generated type itself. No production file or story reaches
`testing/transport/`, directly or through a barrel or helper.

Hand-written TypeScript never cites a backend Python module as the authority, by `.py` path or by dotted `blizzard.…`
module path; cite the generated type, the wire field, or a `bzh:` id instead.

A unit that still reads a wire type outside the boundary is named on the gate's migration exemption list,
`DOMAIN_BOUNDARY_EXEMPT`, until the landing that moves it behind the boundary
(`decision:ui-toolkit/incremental-replacement`). Until then its query may keep the old wire projection for exempt
callers beside a domain projection in the same data-access file, sharing one cache, query keys, and invalidations; the
list only shrinks.

**Why.** When every component works in the generated types directly, a wire change lands in every component that read
the field; behind one boundary it is absorbed in one translator. A judgment re-derived from raw values is a second copy
of one the wire already makes, and keeps rendering the old answer when the backend moves it. A domain file free of
Angular and the wire is tested case by case with plain literals. Data-access files own each resource's query keys and
invalidations, so a client call made anywhere else bypasses the cache plane the views read from. A backend module
citation rots silently when the backend moves.

**Exception.** A pending override's predicted outcome (`bzh:frontend-pending-override`) states what an in-flight
mutation will change before the wire reports it. It is a prediction over a request rather than a re-derived judgment,
lives with the mutation in its data-access file, and falls back to disabled-and-pending wherever it is not total.

**Scope.** Every `.ts` below `web/projects`, `.storybook/` included: production files, specs, stories, and test helpers.
A spec is inside the boundary only by its own focused name; a component or model spec is not. A barrel that re-exports a
generated type is never itself judged — its importer is — and a domain type may share a generated type's name. The
backend-citation and client-call halves bind every hand-written `.ts` except specs, stories, and the generated client.

**Detect.** Tooled by `web:structural-gate`'s domain-boundary sweeps, proven first by
`assertDomainBoundaryDetectorWorks`: the symbol-origin sweep resolves every symbol a file references to its declaration
and fails a file outside the boundary that consumes one declared in a generated `types.gen.ts`, fails a stale
`DOMAIN_BOUNDARY_EXEMPT` entry, and fails a production file or story reaching the test transport. Beside it, with no
exemption list, the backend-citation sweep (`assertBackendCitationDetectorWorks`) fails a backend module citation, and
the client-call placement sweep (`assertClientCallPlacementDetectorWorks`) fails a generated client function named
outside `*.query.ts` / `*.mutations.ts`. `web:lint` refuses Angular and the query library in a `*.domain.ts` or
`*.translate.ts` and every Angular import but `@angular/forms/signals` in a `*.form.ts`, proven by
`web/scripts/boundary-imports-lint-probe.js`.
[`../../verification/blizzard/commands/web/static-checks.md`](../../verification/blizzard/commands/web/static-checks.md)
owns each check's scope, report, and self-test.

Whether a translator re-derives a judgment a wire field already carries, and whether a domain function judges only what
the frontend holds, are review questions.

**Do.**

- `garden/core/cadence.translate.ts` exports `fromCadenceView(wire: CadenceView): Cadence`, and the cadences query's
  `select` maps the cached wire response through it, so its consumers read `Cadence`.
- A translator maps the wire's chunk status into `ChunkStatus`, ending in `'unknown'` for a value the client does not
  list.
- `if (chunk.terminal)` — the translator carried `ChunkDetail.terminal` into the domain type.
- A container injects a query hook from `garden/core/finding.query.ts`, which alone imports
  `listFindingsApiFindingsGet`.

**Don't.**

- A component or `*.model.ts` importing `CadenceView` from `fleet`, directly or through a barrel.
- `const PAUSABLE = new Set(['ready', 'running']); if (PAUSABLE.has(detail.status))` — a judgment the wire carries,
  re-derived from a hand-written status list.
- A `*.domain.ts` importing `signal` from `@angular/core`.
- A component importing `listFindingsApiFindingsGet` and awaiting it in `ngOnInit`.

**See also.** `bzh:generated-client` ([`../../standards/frontend.md`](../../standards/frontend.md)) forbids hand-written
request code; `bzh:frontend-containers-compose` ([containers.md](./containers.md)) moves a container's derivation into a
pure file; `bzh:fleet-wire-additive` ([`../system-shape/fleet-wire.md`](../system-shape/fleet-wire.md)) governs what a
backend change to the wire may do to a running runner.

## A wire vocabulary is open to a value the client does not know (`bzh:frontend-open-vocabulary`)

**Rule.** Every branch on, and every lookup of, a vocabulary a hub or runner response carries handles a value the
generated client does not list. A translator is where a wire vocabulary is read, so it is where an unforeseen value is
handled: it maps one onto its domain union's explicit unknown (`bzh:frontend-domain-boundary`). A lookup table keyed by
a generated vocabulary is built through `fleet`'s `openLookup` (`fleet/src/lib/core/open-lookup.ts`): its table stays a
full `Record` over the vocabulary, so a value the client learns fails to compile until it is placed, and a raw value
outside it resolves through the table's fallback instead of to `undefined`. A TypeScript `switch` carries a `default`,
and a template `@switch` an `@default`. A `switch` that gives every declared value its own `case` hands its `default` to
`fleet`'s `unlisted`, whose `never` parameter keeps a value the client learns a compile error there while a raw value
still reaches it at run time. An unknown value renders raw, in the `idle` tone (`fleet/src/lib/kit/tone.ts`), or is
skipped where it names nothing the surface can show. The board seats a chunk whose status it does not know in its own
lane, declared beside `LANES` in `fleet/src/lib/core/chunk-lanes.ts` as `unknownLane`: shown only while such a chunk is
on the board, headed with the raw status, and given no titlebar stat cell, since `ChunkCountsView` carries no count for
a status the board cannot name.

**Why.** The board and the runner panel read whatever server they are pointed at, and a server newer than the build adds
values to its vocabularies (`bzh:open-response-vocabulary`,
[`../system-shape/released-surfaces.md`](../system-shape/released-surfaces.md)). The web reads wire values with no
runtime check, so a `Record` lookup returns `undefined` for a gained value and a destructure of that answer throws,
taking the whole view down over one field.

**Scope.** Every vocabulary the generated clients declare — a response field's, an SSE frame's event type, and a request
vocabulary a response also carries, such as the verbs a record names as legal — wherever it is read: in a
`*.translate.ts`, `*.query.ts`, or `*.mutations.ts`, and, while the migration lasts, in any file of a unit still on
`DOMAIN_BOUNDARY_EXEMPT`, which still reads wire vocabularies outside the boundary. Specs and stories are outside it.
The `switch` and template `@switch` halves hold every hand-written `.ts` and `.html` under `web/projects/` except specs
and stories, a domain union's included: lint is not type-aware, so the `switch` rule cannot tell a domain union from a
wire one.

**Detect.** `web:lint` (its `default-case` rule, probed by `web/scripts/default-case-lint-probe.js`) and
`web:structural-gate` (the open-vocabulary sweeps, with no exemption list of their own; the vocabulary-record sweep
binds translators, queries, mutations, and the units on `DOMAIN_BOUNDARY_EXEMPT`) fail a branch with no unknown arm;
`web/scripts/open-lookup-type-probe.js` proves the compiler still refuses a table or a `switch` missing a declared
value.
[`../../verification/blizzard/commands/web/static-checks.md`](../../verification/blizzard/commands/web/static-checks.md)
owns each check's scope and self-test. Whether an unknown value's fallback is the right reading — raw, `idle`, or
skipped — is a review question.

**Do.**

- `openLookup<EventView['severity'], Tone>({ critical: 'stale', warning: 'running', info: 'idle' }, () => 'idle')` — an
  unknown severity reads `idle`.
- `const LABEL = openLookup<HostRegistrationView['state'], readonly [string, Tone]>({ … }, (raw) => [raw, 'idle']);` —
  an unknown state reads raw rather than throwing at the destructure.
- An action menu offers only the verbs its lookup `has`; a verb the build cannot name gets no control.
- `default: return { label: unlisted(lease.state).toUpperCase(), tone: 'idle' };` after a `case` per declared state — an
  unknown state reads raw, and a state the client learns fails to compile until it has a `case`.

**Don't.**

- `const LABEL: Record<HostRegistrationView['state'], …> = { … }` read as `const [label, tone] = LABEL[view.state]` —
  throws on the first state the client does not know.
- `const tones: Partial<Record<string, Tone>> = STATE_TONE; return tones[state] ?? 'idle';` — tolerant, but a second
  hand-written spelling of what `openLookup` already owns.
- An `@switch (author.kind)` with a case per known kind and no `@default`.
- `case 'enroll': default: enroll.mutate(…)` — folding `default` into a known case acts on a value it never named, and
  silences the compile error a new value would raise.

**See also.** `bzh:frontend-domain-boundary` (above): the translator turns the wire's vocabulary into a closed domain
union, and this rule stops it assuming the generated client lists every value.
