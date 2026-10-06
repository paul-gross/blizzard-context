# Seam positions

This spoke owns the recorded positions under `bzh:pluggable-seams` — which external-system reaches are exempt from a
configured seam, structural rather than opt-in, or absent as a single Protocol, and why; the macro-shape hub is
[../system-shape.md](../system-shape.md), which owns the rule itself. Each position is stated so a reviewer need not
re-derive it.

## The hub work source is always seated

The built-in hub work source, `HubWorkSource`, implements the `IWorkSource` seam, but its binding is in-process and
always seated — never a work source record with a credential — because the hub's own store is the item's system of
record: there is no external system for a record to point at. Its concrete wiring stays at the composition root,
`hub/app.py::build_hosted_app`, per `bzh:dependency-injection`; only the walk that seats it differs — outside the
record-built loop, in `WorkSourceEntry.registry` — not the seam itself.

## The hub work editor is structural

The hub work source's editor capability, `IWorkEditor`, is seated the same always-on in-process way, and it is
structural rather than a configurable opt-in because every `IWorkEditor` method returns the hub repository's own record
types — `HubWorkItem` for `list`, `get`, `edit`, and `withdraw`, and `CreatedWorkItem` for `create`, which alone also
mints a chunk — types no binding without a hub-owned store behind it could render, unlike `IWorkSource.fetch`'s
seam-local `WorkItem` dataclass. The editor gate also covers the read verbs `list` and `get`, because `IWorkSource`
declares no enumeration method, so no non-hub binding could serve them anyway; the read half is what splits out of
`IWorkEditor` the day a binding gains a real enumeration capability, and not before. Consequently `editor(name) is None`
means structurally never edited for every source but the hub, not merely not opted in.

## The forge has no single seam

No single forge seam Protocol exists; the forge is reached through several seams `bzh:pluggable-seams` already names,
plus one path outside the Rule entirely:

| Path                   | Reaches the forge for                                                                                                                                                              | Seam status                                                                                                                                                                                                                          |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `IWorkSource`          | Work items and branch links; a chunk whose first pointer is a `hub:` item gets no branch links — `HubWorkSource.branch_url` is always `None`                                       | Protocol seam of the work-source capability family                                                                                                                                                                                   |
| `IWorkCloser`          | Closing work items                                                                                                                                                                 | Protocol seam of the work-source capability family                                                                                                                                                                                   |
| `IWorkAnnotator`       | The periodic forge-status annotation sweep                                                                                                                                         | Protocol seam of the work-source capability family                                                                                                                                                                                   |
| `IWorkEditor`          | Never — only the built-in hub source seats one, and that source has no external forge behind it                                                                                    | Protocol seam of the work-source capability family                                                                                                                                                                                   |
| `IOAuthProvider`       | Login                                                                                                                                                                              | Protocol seam                                                                                                                                                                                                                        |
| `GitHubCommitResolver` | Resolving a garden delivery's commits; it sees only bare repo names, so it resolves a name or `owner/repo` against the enabled records and answers nothing for one no record names | Behind the `CommitResolver` callable (`hub/domain/garden/delivery/validation.py`): injected and composition-root-selected, a one-call type alias rather than a Protocol, satisfying the Rule's swappability intent without being one |
| Graph land scripts     | Landing, directly through the `run:` env contract's `BZ_FORGE_*` variables                                                                                                         | Outside the Rule's sites (a loop step, domain, or store), because the script is the landing policy                                                                                                                                   |

The hub holds no shared forge endpoint and no owner fallback: each repository is a record naming its forge, owner, base
branch and secret, and a `deliver` step and the garden commit resolver each resolve the repository they act on to its
record on every use; the work-source family and the OAuth provider each declare their own endpoint through their own
record or config entry likewise. How a `deliver` step resolves the chunk's commit pointers to that record, and when it
refuses the visit, is owned by `bzh:hub-node-env-contract` in
[../../standards/hub-nodes/env-contract.md](../../standards/hub-nodes/env-contract.md);
[../../verification/blizzard/tier-rules.md](../../verification/blizzard/tier-rules.md) owns how tests bind the mock
forge for the land-script path.
