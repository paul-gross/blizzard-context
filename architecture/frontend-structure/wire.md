# Wire conformance

How the Angular suite relates to the hub and runner wire — what it may define for itself, where a gap in the wire is
closed, and which files call the generated client. A spoke of the [frontend structure hub](../frontend-structure.md);
each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## The frontend conforms to the wire and never restates it (`bzh:frontend-wire-conformist`)

**Rule.** Take every backend vocabulary, classification, and wire shape from the generated client
(`fleet/src/lib/api/{hub,runner}/`), and never restate one by hand in TypeScript. A gap in what the wire carries is
closed on the wire — the backend adds the enum, field, or schema component and the client is regenerated — never filled
in by a frontend copy. Generated client functions are called only from data-access files (`*.query.ts`,
`*.mutations.ts`); generated types may be imported anywhere.

**Why.** A hand-written copy compiles against the wire as it was when the copy was written: when the backend adds a
value or moves a judgment, the regenerated types change under every conforming consumer while the copy keeps rendering
the old answer with nothing to flag it. Data-access files own each resource's query keys and invalidations, so a client
call made anywhere else bypasses the cache plane the views read from.

**Exception.** A pending override's predicted outcome (`bzh:frontend-pending-override`) states what an in-flight
mutation will change before the wire reports it; it is a prediction over a request, not a copy of a classification, and
falls back to disabled-and-pending wherever it is not total.

**Scope.** What counts as a restatement:

- **Vocabulary** — a closed value set the backend defines (a status, kind, role, severity, event type) written out as a
  string-literal union, array, or `Set`.
- **Classification** — a backend judgment over a vocabulary (which statuses are terminal, whether a chunk can pause,
  whether a cost is partial) re-derived from raw values instead of read from a view field.
- **Wire shape** — a hand-written interface or type mirroring a model the backend serializes, including one reaching the
  client off a non-route channel such as an SSE frame or an artifact body.
- **Backend citation** — a comment or string naming a backend Python module as the authority, by `.py` path or by dotted
  `blizzard.…` module path; cite the generated type, the wire field, or a `bzh:` id instead.

**Detect.** Tooled by `web:structural-gate`, neither sweep with an exemption list: its backend-citation sweep
(`assertBackendCitationDetectorWorks`) fails a backend module citation in hand-written TypeScript, and its client-call
placement sweep (`assertClientCallPlacementDetectorWorks`) fails a generated client function named outside `*.query.ts`
/ `*.mutations.ts`.
[`../../verification/blizzard/commands/web/static-checks.md`](../../verification/blizzard/commands/web/static-checks.md)
owns each sweep's scope, report, and self-test.

`web:client-drift` fails a generated client that no longer matches the exported specs, so a wire fix lands with its
regenerated types. A hand-written vocabulary, classification, or shape is a review question, not tooled: does this
literal set, interface, or status predicate duplicate what a generated type carries, or what a view field should carry?
The fix is the generated enum or model when the wire has it, and a backend change when it does not — a vocabulary or
off-route shape registers in `src/blizzard/wire/components.py` so the spec carries it, and a classification becomes a
field on the view that already carries the raw value.

**Do.**

- `if (detail.pausable)` — the view field `ChunkDetail.pausable` carries the judgment.
- `Object.values(FindingSeverity)` populates a severity filter from the generated `const`.
- A container injects a query hook from `garden/core/finding.query.ts`, which alone imports
  `listFindingsApiFindingsGet`.

**Don't.**

- `const PAUSABLE = new Set(['ready', 'running']); if (PAUSABLE.has(detail.status))` — a classification re-derived from
  a hand-written status list.
- `type Severity = 'blocking' | 'should-fix';` beside the generated `FindingSeverity`.
- A component importing `listFindingsApiFindingsGet` and awaiting it in `ngOnInit`.

**See also.** `bzh:generated-client` ([`../../standards/frontend.md`](../../standards/frontend.md)) forbids hand-written
request code; `bzh:fleet-wire-additive` ([`../system-shape/fleet-wire.md`](../system-shape/fleet-wire.md)) governs what
a backend change to the wire may do to a running runner.

## A field the server always sends is required in the schema (`bzh:wire-sent-is-required`)

**Rule.** A response-only wire model subclasses `blizzard.wire.base.WireModel`, so its exported schema lists every field
as required — a defaulted one included. "Response-only" means all three hold: no request body reaches the model, it is
not an `SseFramePayload` (whose `to_payload` omits unset fields), and no route serves it with a
`response_model_exclude_*` flag. A model that fails one of them stays on `BaseModel`: marking a field required where the
server can omit it misleads the client, and marking one required where a request parses it splits the schema into
`-Input` and `-Output` components, which the released surface may not do (`bzh:released-surface-additive`).

**Why.** A field the server always sends but the schema types as optional invites the frontend to guard it with a
fallback, and the fallback re-derives a judgment the wire already made (`bzh:frontend-wire-conformist`).

**Detect.** The `blizzard:unit-test` guard `tests/test_wire_sent_is_required.py` derives the response-only schemas from
both built apps and fails when one lists an optional property, or when an exclude-flagged model shows up split.
`blizzard:compat` reports a split that slips past it as a deleted component schema.

**Do.**

- `class FleetSpendView(WireModel):` with `estimated_cost_usd: float | None = None` — the client reads
  `estimated_cost_usd: number | null`, always present.

**Don't.**

- A defaulted field on a bare `BaseModel` response: the client types it `x?: T | null`, and a consumer writes
  `x ?? fallback`.
- `WireModel` on a request body, an SSE payload, or a model under `response_model_exclude_none=True`.

**See also.** `bzh:frontend-wire-conformist` (above); `bzh:fleet-wire-additive`
([`../system-shape/fleet-wire.md`](../system-shape/fleet-wire.md)) governs what a backend change to the wire may do to a
running runner.
