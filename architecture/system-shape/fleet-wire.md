# Fleet wire

This spoke owns what a hub change may do to the wire a runner reaches across a version-skewed deploy; the macro-shape
hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A hub change to the runner-reached wire is additive, or acknowledged (`bzh:fleet-wire-additive`)

**Rule.** A hub change to a route, request or response schema, or enum the runner reaches is additive to every supported
release's runner parse path (`bzh:released-surface-additive`, [./released-surfaces.md](./released-surfaces.md), owns
when a break is admitted). A removed route or field keeps its old form beside the replacement, the way
`GET /api/fleet/queue/peek` (`src/blizzard/hub/api/fleet.py`) stays beside its matched `POST` counterpart.

**Why.** A deployment moves its hub onto a release before its runners, which follow at their own pace
(`docs/versioning.md`'s skew window), so an unacknowledged break reaches a live runner with nothing to catch it before
the fleet wedges.

**Detect.** `blizzard:compat` ([../../verification/blizzard.md](../../verification/blizzard.md)) is the mechanical check
— it holds the wire selection of `openapi/hub.openapi.json` to each supported release. A runner call reaching the hub
outside that surface selection is invisible to it.

**Do.** A new optional response field; a new route kept beside its replacement; and, when a new runner→hub call reaches
outside the declared surface, extending the wire selection in the same change. Naming the runner's tenant took the first
form: `RunnerRegistrationResponse` and `RunnerIdentityView` (`src/blizzard/wire/runner.py`) gained `tenant_id` and
`tenant_name`, each optional and `None` by default, so a previous-minor runner parses the reply it always did, and the
route, the request, and the refusal shapes stayed as they were. Naming the projects a runner serves took it too:
`RunnerRegistrationRequest.projects` is optional, and its absence (`None`) keeps the declaration the hub holds where
`[]` serves none, so a previous-minor runner that sends no `projects` key never erases its declaration;
`RunnerRegistrationResponse.projects` is `None` from a hub that predates projects. A refusal that needs a new cause
extends the body it already has rather than adding one: a claim refused because the runner does not serve the chunk's
project keeps the incompatible-claim `409` (`RouteClaimIncompatibleDenial`, `src/blizzard/wire/route.py`), which gained
a `reason` (`ClaimDenialReason`, `capability` by default) and a `detail` naming the project, so a previous-minor runner
reads it as the refusal it already handles.

Whether a response enum gaining a value is additive is decided per supported release by `bzh:open-response-vocabulary`
([./released-surfaces.md](./released-surfaces.md)), which owns how an open field and a declared-closed one behave.

**Don't.** A response enum gaining a value that `bzh:open-response-vocabulary` does not make additive and no admitted
break covers.

**See also.** `bzh:shared-kernel` ([../clean-architecture.md](../clean-architecture.md)): where a vocabulary type the
wire carries is defined.

## Protect runner-reached refusals (`bzh:fleet-wire-protected-refusals`)

**Rule.** Preserve the supported runner's interpretation of deliberate hub refusals, including released fields, their
types and meanings, and meaningful absence, when changing any runner-reached HTTP operation or its dependencies. Declare
refusal variants in OpenAPI and extend the wire selection when a runner reaches outside it. The developer contract in
`blizzard/docs/versioning.md` owns the problem representation and migration exceptions.

**Why.** A refusal drives runner lifecycle decisions just as a success drives work; a parseable but differently
classified refusal can strand or misroute a live runner during version skew.

**Scope.** Include non-fleet bootstrap, authentication, federation, proxy and archive calls, and refusals from shared
dependencies and delegated handlers. Framework validation and unrelated operations are not deliberate runner refusals.

**Detect.** Compare runner call sites and their refusal producers with declared operation/status/media/model variants;
check `blizzard:compat` and the runner-reach guards in `blizzard/tests/guards/`. A missing field, a changed type, or a
field emitted as null where the release omits it can break an older client even when a new client parses the body.

**Do.** A dependency claim refusal adds a problem type while still omitting `status`.

**Don't.** A host bootstrap refusal loses its released discriminator because its operation is outside `/api/fleet`.

**See also.** `bzh:fleet-wire-additive` above owns supported-release compatibility; `bzh:matrix-gaps`
([../../verification/blizzard/gaps.md](../../verification/blizzard/gaps.md)) records the baseline evidence limit.
