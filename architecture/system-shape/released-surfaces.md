# Released surfaces

This spoke owns what a change may do to a surface a supported release already ships; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A change to a released surface is additive, or a break the window admits (`bzh:released-surface-additive`)

**Rule.** A change to any surface the `blizzard` repo's `docs/versioning.md` names — the HTTP API, the hub↔runner wire,
configuration, the store schema, the trace contract, and the egress contract — is additive to every supported release,
or it is a break the compatibility window admits, or a break a recorded allowance admits: one exact finding against one
release line whose consumers survive it, in the `blizzard` repo's `contracts/compat/allowances.toml`, whose README owns
the entry format and when an entry applies. `docs/versioning.md` owns the window and what counts as breaking;
`blizzard:compat` ([../../verification/blizzard.md](../../verification/blizzard.md)) decides which a change is. Whether
a release tolerates a response enum's gained value is read from that release's own document, from the open mark
`bzh:open-response-vocabulary` puts there. A removed or reshaped surface keeps its old form beside the replacement,
marked deprecated, until a later change may remove it.

**Why.** A deployment moves its hub, its runner hosts, and its clients onto a release at their own pace, so a break
reaches a live consumer with nothing to catch it. Holding the change to supported releases makes the check mean the same
thing on every trigger, and attributes a break to the change that makes it.

**Scope.** An allowance records a reviewed fact about one shipped line, so it admits that break against that line's
releases and nowhere else; keyed on the line, it survives a patch cut there with no edit.

**Detect.** `blizzard:compat` fails the pull request, the push, and the tag whose committed contract documents break a
supported release in a way neither the window nor a recorded allowance admits; a stale allowance fails it too. A surface
that no committed document describes is invisible to it.

**Do.** Add the field, route, key, column, or span beside the old one and deprecate the old with the surface's own mark.
When the break is unavoidable, follow `workflows/judging-a-break.md`
([../../workflows/judging-a-break.md](../../workflows/judging-a-break.md)): it decides between keeping both forms, a
break the window admits, a break an allowance admits, and a break that waits for a later change, and owns what an
allowance's `because` must show.

**Don't.** Remove or rename a released surface in the change that deprecates it, or regenerate a contract document to
make a finding disappear. Record an allowance without reading the line's own consumers, or to exempt a whole surface for
every release.

**See also.** `bzh:fleet-wire-additive` ([./fleet-wire.md](./fleet-wire.md)): the wire's own form of this rule.
`bzh:store-expand-contract` ([../../standards/persistence.md](../../standards/persistence.md)): the store schema's.

## A response vocabulary field is open, or declared closed (`bzh:open-response-vocabulary`)

**Rule.** Every vocabulary field on a model that only leaves a server — a field typed by a `StrEnum`, or by a `Literal`
of more than one value — is open or declared closed. An open field, `Annotated[E | Unrecognized, OPEN]` from
`src/blizzard/wire/vocabulary.py`, parses a value outside `E` as `Unrecognized` (`src/blizzard/foundation/`), keeps
`E`'s own schema in the OpenAPI document, and marks the position open there. A field is declared closed,
`Annotated[E, DeclaredClosed("…")]`, only when no safe fallback exists: acting without knowing the value would do wrong
work, as for the envelope's dispatch fields. A request field, and any class a server validates as input — a request body
or parameter, an ingested document, a class used as both request and response — stays closed. A single-value `Literal`,
a code or discriminator, counts as declared closed.

**Why.** A deployment's clients — the runner, its CLI, and its panel — read a newer server's responses across the skew
window, so a closed parse turns every value a vocabulary gains into a failed read. Open, each typed consumer meets
`Unrecognized` in the type checker and decides what an unknown value means to it: show it, skip it, or defer to the
server's own state.

**Scope.** A request stays closed so a server still refuses a value it does not know, and the mark records, per release,
which positions that release's clients tolerate.

**Detect.** The gate test `tests/test_open_response_vocabulary.py` fails a response-only vocabulary field that is
neither open nor declared closed, and an open field on any class outside the response-only set. The response-only set is
the response-role components of both committed OpenAPI documents, plus every model class the runner's client-side
modules parse, with every model those reach, less every request-role component of either document; the second source
reaches refusal bodies no document describes. A base no request names joins the set when its every subclass is in it,
since its fields leave a server only through them. The test's planted cases prove both failures. `blizzard:typecheck`
then reports every typed consumer that receives `E | Unrecognized` where it expected `E`.

**Do.** Open the field, and give the consumer its unknown branch where a decision rests on the value — in the domain
rule that decides, its orchestrating caller logging the raw value. The runner accepts an `ApplyOutcome` it cannot read
and defers to the chunk's hub status, and an unreadable `ChunkStatus` satisfies no status test, so it neither abandons,
resumes, spawns into, nor releases a lease on one (`src/blizzard/runner/lifecycle/model.py`). A proxy route passes the
value through raw, and a display prints it raw. `NodeConfig.executor`, `.session` and `.judged_by`, and the envelope's
artifact kinds, are declared closed: a runner cannot run a node-step whose dispatch it does not know.

**Don't.** Type a response vocabulary as plain `str` to make it tolerant, which hides the decision from the type
checker, or add a sentinel member to the vocabulary, which reaches the OpenAPI document and loses the raw value. Open a
field a server validates as input.

**See also.** `bzh:fleet-wire-additive` ([./fleet-wire.md](./fleet-wire.md)): a gained value on an open field reaches a
runner that tolerates it. `bzh:shared-kernel` ([../clean-architecture.md](../clean-architecture.md)): why `Unrecognized`
sits in `foundation/`. `bzh:domain-orchestration-split` ([../clean-architecture.md](../clean-architecture.md)): where
the unknown branch lives.
