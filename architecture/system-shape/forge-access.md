# Forge access

This spoke owns the two rules every forge call is held to behind its seam: how a credential becomes what a forge client
authenticates with, and how the call reaches its forge key's rate budget; the macro-shape hub is
[../system-shape.md](../system-shape.md), and [./seam-positions.md](./seam-positions.md) owns which seams reach the
forge. Every rule here follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A forge credential becomes an authorization at one boundary (`bzh:forge-authorization-boundary`)

**Rule.** Turn a credential into what a forge client authenticates with only at the forge authorization boundary,
`IForgeAuthorizations` (`blizzard/src/blizzard/hub/forge/auth.py`) — the only forge code that reveals a secret
(`bzh:secret-write-only`, [./configuration.md](./configuration.md)). A caller hands it the credential a record resolved
to and the scope it is asking for, and takes back an authorization, never a secret. The boundary is a seam of its own,
apart from the landing seam and the work-source family: both sit behind it, and neither knows how its calls are
authenticated. Word a forge's refusal of a credential in one vocabulary wherever it is raised — at the boundary's mint,
on a landing call, or on a work-source call: each forge kind's adapter classifies the answer into an `AuthRefusal` and a
sanitized `ForgeDiagnostic` (`blizzard/src/blizzard/hub/domain/kernel/forge_refusals.py`), and that module owns each
refusal's sentence and remedy and the `forge-auth-refused` event's detail.

**Why.** With one boundary between a credential and a client, a new way to authenticate changes a binding and its
builder and no seam, work-source binding, or action. With one module wording a refusal, the escalation, the event, and a
check's outcome word one refusal one way.

**Scope.** Binds every forge client the hub builds. The scopes a caller asks for:

| Scope         | Asked by                                                                                                              |
| ------------- | --------------------------------------------------------------------------------------------------------------------- |
| `landing`     | The forge registry, building a repository's adapter bundle                                                            |
| `work-source` | The work-source family, through its own `IWorkSourceAuthorizations`, seated at the composition root                   |
| `check`       | The credential check (`blizzard/src/blizzard/hub/forge/readiness.py`), whose client is held to reads by its transport |

The work-source family declares that narrow Protocol itself so it imports nothing of `hub/forge/`
(`bzh:forge-rate-budget` below); the composition root seats the one boundary behind it, fixed to its scope. The
authorization carries the `auth` its client authenticates each request with, the authority the calls go out as — which
keys the rate budget every caller acting as it shares, and the write lane its landing writes go out under — and the
capabilities it offers, narrowing its forge kind's set — so what the registry offers a repository is that narrowed set.
`ForgeAuthorizations` (`blizzard/src/blizzard/hub/forge/internal/authorizations.py`) builds one by the credential's
binding, and a binding that mints access mints it there, narrowed to the scope. `AuthRefusal` and `ForgeDiagnostic` sit
in the kernel because the landing seam, the work-source family, and the forge-status pass all name them and the
work-source family may not import the forge package. What an operator does with a refusal is
[../../domain/humans/escalation.md](../../domain/humans/escalation.md#a-refused-credential)'s.

**Detect.** A secret revealed in forge or work-source code anywhere but behind the boundary; a landing adapter, a
work-source binding, or an action that reads a credential's binding or secret to decide how its client authenticates; a
credential refusal's sentence or remedy worded outside `forge_refusals.py`.

**Do.** A new way to authenticate is a `CredentialBinding`
(`blizzard/src/blizzard/hub/domain/config/credential_bindings.py`) and its builder in `ForgeAuthorizations`, behind the
boundary — beside its entry in `PROVIDER_BINDINGS` (`blizzard/src/blizzard/hub/domain/config/work_sources.py`) for each
work-source provider that may act with it — with no change to the landing seam, a work-source binding, or any action.

**Don't.** A work-source binding that reads its credential's secret and sets its own request header; an escalation that
composes its own sentence for a token the forge refused.

**See also.** [./configuration.md](./configuration.md) `bzh:configured-record` — what a credential record names and
which writes it refuses. `bzh:forge-rate-budget` below — the budget an authorization's authority keys.

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
