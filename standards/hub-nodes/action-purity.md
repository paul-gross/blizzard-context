# A hub action is pure of the hub's data

What a hub action may touch while it takes a pass.

Parent: [../hub-nodes.md](../hub-nodes.md).

## An action reads only what it is handed and writes only through its sink (`bzh:hub-action-purity`)

**Rule.** An action under `blizzard/src/blizzard/hub/delivery/actions/` reads only its three inputs — the frozen
`Visit`, the forge handles it is handed, and its effect sink — and writes only by handing an effect to the sink and
waiting for it to be durable. An action that needs more declares it as an input the executor reads into the `Visit`
before the pass begins; it never reaches for it inside the pass. Every module under `hub/delivery/actions/` imports only
the allowlist: from the standard library, the pure modules that reach neither the environment, a process, nor a socket
(`asyncio` without its subprocess and connection functions, `dataclasses`, `json`, `re`, `typing`, `urllib.parse`, and
their kind); from `blizzard.foundation`, only `roles`, `escalation_causes`, `findings`, `garden_proposals`, and
`repo_ref`; and of blizzard's own, only `hub/domain/actions/`, `hub/domain/graph/actions.py`,
`hub/domain/config/repositories.py`, `hub/delivery/forge_handle.py`, and its own package. Every blizzard module an
action reaches, directly or through another, imports nothing that reaches a process or the network, and touches no part
of `os` but `os.urandom`. Each `Visit` is immutable all the way down, and each action is constructed with no arguments.

A delivery marker a pass records takes the one `content` shape its name fixes: a PR reference,
`delivery-pr/<repo>/<number>` or the bare `delivery-pr/<repo>`, carries the JSON object
`{ "repo": "<repo>", "number": <integer>, "url": "<forge web PR URL>" }` whose `repo`, and `number` where the name
carries one, match the name; `merged/<repo>` carries the landed revision, and blank content records no landing;
`awaiting-external-merge`'s content is never read. The chunk-artifacts store's delivery read, which feeds the hub's
projection of these markers, skips a PR reference of any other shape without error. What each marker means is
[delivery](../../domain/artifacts/delivery.md)'s.

**Why.** A pass runs on a thread shared by every tenant's passes, beside the process environment that holds the key
sealing every tenant's secrets. An action that could read the environment, open a process or a socket, write the store,
or take a collaborator through its constructor could leak a secret or decide an effect the executor never sees made
durable. Holding it to its inputs and its sink keeps every external effect it makes recorded before the next one
happens, and keeps the action testable from a fixture visit alone.

**Detect.** An import under `hub/delivery/actions/` outside the allowlist — the store, `os`, `sys`, `time`, `threading`,
an HTTP client, or a `blizzard.foundation` module not named above; an attribute of `asyncio` that starts a process or
opens a connection; an allowlisted module that reaches a process or the network, or any of `os` but `os.urandom`, behind
it; a `Visit` holding a `list`, `dict`, `set`, `bytearray`, a mapping that is not a `MappingProxyType`, or a dataclass
that is not frozen; an action whose constructor takes an argument; a delivery marker whose content departs from the
shapes above. `blizzard/tests/test_layering.py` fails the unit tier on each import and the transitive reach, and
`blizzard/tests/test_hub_actions.py` on the visit's runtime values and the constructions; planted cases in both prove
each check fires. The allowlist is the test's own literal: a later change that widens it names the module in its own
spec.

**Do.** `garden-deliver` (`hub/delivery/actions/garden_deliver.py`) reads its `delta` and `proposals` from the visit's
node arguments, hands a `RecordGardenDelivery` to the sink, and answers from the `EffectResult` it gets back; the
executor runs the garden delivery recorder when it writes the effect, with the run context the action cannot hold. A
forge's client stays outside the package, behind the handle Protocol in `hub/delivery/forge_handle.py`.

**Don't.** An action reading `os.environ` for a token, building its own HTTP client, or importing a store adapter to
check a marker; an action taking a recorder in its constructor; a visit carrying the domain's `Chunk` or `Node`, whose
lists make it mutable through them.

**See also.** `bzh:domain-package-layers` in
[../../architecture/clean-architecture.md](../../architecture/clean-architecture.md) orders `hub/domain/actions/`;
`bzh:data-roles` governs the visit's types as domain models; the hub node's `action:` contract is
[action-shape.md](./action-shape.md).
