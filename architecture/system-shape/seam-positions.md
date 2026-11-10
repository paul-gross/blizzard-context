# Seam positions

This spoke owns the recorded positions under `bzh:pluggable-seams` — which external-system reaches are exempt from a
configured seam, structural rather than opt-in, or absent as a single Protocol, and why — and `bzh:forge-rate-budget`,
the rule for how forge calls reach their shared rate budget; the macro-shape hub is
[../system-shape.md](../system-shape.md), and [./pluggable-seams.md](./pluggable-seams.md) owns the seam rule itself.
Each position is stated so a reviewer need not re-derive it; a rule stated here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

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

## The forge is reached through the landing seam and the work-source seams

Delivery reaches a repository's forge through the landing seam, `hub/forge/landing.py`: three narrow Protocols,
`IForgeRefs`, `IForgeChanges`, and `IForgeChecks`, each under `bzh:seam-size-ceiling` and never composed into one wide
seam. The registry builds one adapter bundle per repository from its forge record's kind and API origin, its
`owner/repo`, and its revealed secret, and the `land` action and the garden's commit check call only the roles they
need. Work items reach the forge through the work-source family, and login through its own seam:

| Path             | Reaches the forge for                                                                                                                                                                                | Seam status                                                                                                                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `IWorkSource`    | Work items and their own browser links                                                                                                                                                               | Protocol seam of the work-source capability family                                                                                                                                                   |
| `IForgeWebLinks` | Repository branch links and landed commit links on the board and in the issue's delivery note, from the resolved repository record's forge; a kind without a web-link binding answers no link        | Pure forge-kind binding, independent of credentialed API calls                                                                                                                                       |
| `IWorkCloser`    | Closing work items                                                                                                                                                                                   | Protocol seam of the work-source capability family, domain-owned in `blizzard/src/blizzard/hub/domain/chunk/ports/work_sources.py`; the work-source bindings implement it                            |
| `IWorkAnnotator` | The periodic forge-status annotation sweep                                                                                                                                                           | Protocol seam of the work-source capability family, domain-owned in `blizzard/src/blizzard/hub/domain/chunk/ports/work_sources.py`; the work-source bindings implement it                            |
| `IWorkEditor`    | Never — only the built-in hub source seats one, and that source has no external forge behind it                                                                                                      | Protocol seam of the work-source capability family                                                                                                                                                   |
| `IOAuthProvider` | Login                                                                                                                                                                                                | Protocol seam                                                                                                                                                                                        |
| Landing seam     | Delivery: the `land` action's refs, changes and checks, and the garden's commit check, which resolves a name or `owner/repo` against the enabled records and answers nothing for one no record names | Protocol seams, `IForgeRefs`, `IForgeChanges` and `IForgeChecks`, built per repository by the registry; each forge kind offers a capability set, and an action's unmet requirement refuses the visit |

The hub holds no shared forge endpoint and no owner fallback: each repository is a record naming its forge record,
owner, base branch and secret, and a `deliver` step and the garden's commit check each resolve every repository they act
on to its record on every use; a work source names its forge record likewise, and the OAuth provider declares its own
endpoint through its config entry.

Each tenant holds one rate budget per forge key — a forge record and the secret its calls go out under, or that forge's
anonymous budget when none — beside the registry and outside its adapter cache, so an edit that rebuilds an adapter
keeps the budget. The landing seam's role handles and the work-source family share it, reaching it as
`bzh:forge-rate-budget` below states.
[../../verification/blizzard/tier-rules.md](../../verification/blizzard/tier-rules.md) owns how tests bind the mock
forge for the land action's path.

## The rate budget is reached by handle, in the forge kind's dialect (`bzh:forge-rate-budget`)

**Rule.** Carry a forge call's priority on the handle it goes out through, never on the adapter: `land` admits as
`landing`, the garden's commit check as `sweeping`. The work-source family reaches the budget only through its own
narrow rate-gate Protocol, fixed to `sweeping` and bound where the source is built, so it never imports the forge seam.
Each forge kind's rate dialect, chosen by kind, owns how that forge's answers become readings and refusal verdicts — the
work-source gate translates each answer by its source's forge kind — and `hub/forge/budget.py` owns only the arithmetic
over readings, free of any HTTP library.

**Why.** One adapter serves every caller of its repository, so a priority on the adapter would be every caller's. A
budget that spoke HTTP would carry one forge's dialect into arithmetic every forge kind shares.

**Detect.** A priority argument or attribute on a forge adapter rather than on its handle; an import of any module of
the forge package (`hub/forge/`) from the work-source family (`hub/work_sources/`); an HTTP library imported in
`hub/forge/budget.py`; a forge's answer turned into a reading anywhere but in its forge kind's dialect.

**Do.** The `land` action takes a `landing` handle and the garden's commit check a `sweeping` one, both over the one
adapter the registry built for the repository; a work source is built with its `sweeping` rate gate
(`hub/work_sources/rate_gate.py`) and reads the budget through nothing else.

**Don't.** A work-source binding importing `hub/forge/budget.py` to ask its forge key's budget directly; a forge's rate
headers parsed in `budget.py` rather than in that forge kind's dialect.
