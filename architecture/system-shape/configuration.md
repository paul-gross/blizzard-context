# Configuration

This spoke owns how the hub's configured surfaces are changed and read — the one verb set and patch meaning every
configured record shares, how a declarative document is decoded, what may carry a secret, and when configuration is
read; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned
by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

A **configured record** is a record the hub or a runner host holds as operator-set configuration and that an operator
changes while it runs: a forge, a credential, a work source, a repository, a secret, a project, a project source link, a
project repository link, a scope, a routine, a cadence, an urgency, the tenant's settings, the hub-wide settings, or a
runner host's workspace or subscription. The rules below name the seams and tables that keep them — `IConfigCodec`,
`SecretValue`, `ISecretReader`, `config_changes` — by the names their implementations take, so code adding one of them
takes the name stated here. [Known debt](#known-debt) lists the code these rules do not yet hold.

## Every configured record takes one verb set and one patch meaning (`bzh:configured-record`)

**Rule.** Give a standalone retirable configured record the verb set create, list, show, edit, retire, enable — show's
CLI verb being `get` (`bzh:cli-get-verb`); a kind listed below departs from it only as its entry states. Give editable
records a sparse-merge edit, and each record a `revision` that every changed write increments and one change row
appended in the same transaction as each write; tenant records use `config_changes`, while hub-wide settings and the
host's records use their own audit below. A sparse merge leaves an absent field unchanged, sets a present field, and
takes an explicit `null` as clearing a nullable field, refusing it on any other. A retire of a retired record, or an
enable of an enabled one, writes nothing; an edit of a retired record is legal and leaves it retired. Enable reverses a
retirement.

| Verb   | Route                           |
| ------ | ------------------------------- |
| create | `POST /api/<kind>`              |
| list   | `GET /api/<kind>`               |
| show   | `GET /api/<kind>/{key}`         |
| edit   | `PATCH /api/<kind>/{key}`       |
| retire | `POST /api/<kind>/{key}/retire` |
| enable | `POST /api/<kind>/{key}/enable` |

Standalone retirable CLI nouns carry the six verbs, a secret's replace standing in for its edit. Each entry below states
a kind's own surface beside the six; only the entries for a project, a project's link, a graph, a work item, a secret,
an urgency, the tenant's settings, the hub-wide settings, and the host's workspaces and subscriptions depart from the
verb set itself:

- **A project** takes create, list, show, and edit but no retire or enable: a project, once created, stays
  ([../../domain/projects.md](../../domain/projects.md)). Its links to sources and repositories carry the lifecycle in
  its place, each its own revisioned record whose change rows reuse the verbs — `create` for a link, `retire` for an
  unlink, `enable` for a relink — each beside its link fact.
- **A project's link** is named into being by `PUT /api/projects/{project}/source-links/{source}` (or
  `repository-links/{repository}`), which links or relinks and leaves a standing link as it is, and unlinked by that
  path's `POST …/retire`; on the CLI, `blizzard hub project link` and `unlink`. A repository link's own base branch is
  edited by a sparse `PATCH /api/projects/{project}/repository-links/{repository}` under the link's revision, where an
  explicit `null` clears it so the link inherits the repository's again; on the CLI, `blizzard hub project base`.
- **A project's landing order** is written on its repository links, never on the repository:
  `PUT /api/projects/{project}/landing-order` sets the whole order and
  `POST /api/projects/{project}/landing-order/position` moves one repository — on the CLI, `blizzard hub project order`
  and `position` — each appending a position fact only for a link whose position changes, and refusing a repository the
  project does not link with `422 repository_not_linked`.
- **A repository** carries `landing_policy`, required and never null, which a request takes from the closed policy set
  and a response reports as an open string, and `park_timeout_hours`, the one repository field an explicit `null`
  clears. Its required, non-null boolean `allow_no_ci` defaults to `false` and is included in configuration documents
  and repository reads and writes; its landing meaning belongs to [delivery](../../domain/artifacts/delivery.md). A
  repository write whose policy needs a capability its forge or its credential does not offer is refused
  `forge_capability_missing` on `landing_policy`, naming each missing capability, the policy, and the forge — on create,
  on a policy or forge edit, and on every repository write a document apply plans.
- **A credential** names its `forge` and its `binding` at create and neither ever changes: an edit naming either at all,
  or a declared document entry naming another, is refused `credential_binding_immutable`. A binding is looked up by name
  in `CREDENTIAL_BINDINGS` (`blizzard/src/blizzard/hub/domain/config/credential_bindings.py`); it says whether its
  secret is supplied by the operator or its access renewed by the hub, validates and canonicalizes the record's
  `settings`, and derives its `authority`, which no write states and which a second credential on the forge is refused
  `credential_authority_taken` for claiming, a retired holder keeping its claim. An edit whose settings would stop
  offering a capability an enabled repository acting with it needs is refused `forge_capability_missing` on `settings`,
  naming the repositories that fall short and the capabilities they would lose. Its retire is refused
  `credential_in_use`, listing each enabled repository and work source naming it. Beside the verb set it takes a
  read-only check — `POST /api/credentials/{credential}/checks`, on the CLI `blizzard hub credential check` — which
  writes no record and no change row. What a credential is, and who maintains its access, is
  [../../domain/projects.md](../../domain/projects.md#the-credential-a-source-or-repository-acts-with)'s; how a binding
  becomes what a forge client authenticates with, and what adding one takes, is `bzh:forge-authorization-boundary`'s
  ([./forge-access.md](./forge-access.md)).
- **A repository and a work source** each name the credential they act with in `credential`, by id or slug. One of
  another forge is refused `credential_forge_mismatch`; one unknown, or retired while the record is enabled,
  `credential_unavailable`. The deprecated `secret_name` or `secret` field, given alone, resolves to the `github.token`
  credential reading that secret on the record's forge, created — slugged by the secret's name — when none acts as that
  authority; the write answers with a `Deprecation` header and a `warnings` entry and records a `config-old-field-used`
  event. Given beside a `credential` it disagrees with, the write is refused `credential_conflict`. A work source names
  only a binding its provider lists in `PROVIDER_BINDINGS` (`blizzard/src/blizzard/hub/domain/config/work_sources.py`),
  any other refused `credential_binding_unsupported`.
- **A record a project owns** — a scope, a routine, or a kind added beside them — is created in the project the call
  names — `--project` on the CLI, by id or slug — and a call naming none falls back or is refused as
  [../../domain/projects.md](../../domain/projects.md) §A call that needs a project states, the refusal
  `422 project_required` listing the tenant's projects; its list, and the change log, take `?project=` to narrow to one
  project and read the whole tenant without it. A change row of a project, a project's link, or a record a project owns
  names that record's project, since its key means something only inside its project; one of a tenant-wide record — a
  forge, a credential, a work source, a repository, a secret — names none.
- **A graph** is an immutable mint, so its definition takes no patch — an edit is a new mint — and only its mutable
  flags take the sparse `PATCH`, beside its retire and enable, each of which appends a fact even when it repeats the
  standing value ([../../domain/graphs/identity.md](../../domain/graphs/identity.md)).
- **A work item** is work, not configuration: its patch carries the sparse-merge meaning, and it takes no revision, no
  change row, and keeps its `DELETE`.
- **A secret** takes replace in place of edit: its value is replaced whole by `PUT /api/secrets/{name}/value` — on the
  CLI, `blizzard hub secret set NAME`, reading the value from stdin — and the replace still increments the revision and
  appends its change row.
- **An urgency** ([../../domain/work/urgency.md](../../domain/work/urgency.md)) is tenant-wide, so its change rows name
  no project, and its slug is fixed at create, so it keeps no former slugs and an edit naming `slug` is refused. Its set
  has an order, written as position facts: `PUT /api/urgencies/order` sets the whole live order and is refused
  `422 urgency_order_incomplete` when it leaves a live urgency out, names a retired one, or names one twice;
  `POST /api/urgencies/order/position` moves one urgency to just after another, or first under `after: null`. A reorder
  that moves anything appends one change row of kind `urgency_order`, keyed by the tenant id, whose revision is the
  order's sequence; one that moves nothing appends neither a fact nor a row. Its retire takes a body naming `move_to`,
  and is refused in order `409 urgency-is-default`, `409 urgency-in-use` (its `open_chunks` member counting them) when
  open chunks carry it and no `move_to` is named, then `422 urgency_unknown`, `422 urgency_retired`, or
  `422 urgency_move_to_self` on `move_to`; a retire that moves open work needs `chunk:control` beside `config:edit`. The
  model, the order, and the refusal ladder live in `blizzard/src/blizzard/hub/domain/urgency/`.
- **The tenant's settings** are a keyless singleton, one per tenant, taking show and edit only: `GET /api/settings` and
  `PATCH /api/settings`, with no `{key}`, since the tenant the request resolved is the key, and no create, retire, or
  enable, since a tenant always holds its settings. Its change rows, of kind `tenant_settings`, are keyed by the tenant
  id and name no project. Its `default_urgency` refuses an explicit `null`, and an urgency the tenant does not hold or
  has retired with `422 urgency_unknown` or `422 urgency_retired`.
- **The hub-wide settings** are one singleton shared by all tenants, not a tenant's settings. They take show and edit at
  `GET` and `PATCH /api/admin/settings`, document apply at `POST /api/admin/settings/apply`, and history at
  `GET /api/admin/settings/changes`, and export at `GET /api/admin/settings/export`; they have no create, retire, or
  enable. Every read and write on these routes requires the hub-only `SETTINGS_ADMIN` permission; a tenant role grants
  no access. Their own revision and audit live in `hub_settings`, `hub_setting_entries`, and `hub_setting_changes`, not
  tenant-scoped `config_changes`. The write decision is shared and pure, in
  `blizzard/src/blizzard/foundation/settings_record/`; the revision-conditioned transaction is the hub settings
  adapter's own. A matching revision is required, validation of the whole candidate precedes the write, and a no-op
  moves neither revision nor audit. A changed write moves the revision and appends its audit in the same transaction.
  Set and unset are distinct: unset restores the default and leaves an entry that prevents a later file seed from
  restoring the old value.
- **The host's workspaces and subscriptions** are the runner host's records, not a tenant's: their routes sit under
  `/api/host/workspaces` and `/api/host/subscriptions` on the runner, keyed by `workspace_id` and `slug`, and their CLI
  nouns are `blizzard runner workspace` and `blizzard runner subscription`. `workspace_id`, `slug` and a subscription's
  `provider` are immutable: an edit naming one is refused `422`. Each write needs superuser authority, except the
  workspace prompt routes, which write the workspace record's prompt at its current revision with no `If-Match`. Each
  changed write appends one row to the host store's `host_setting_changes`, its `record_kind` `workspace` or
  `subscription` and its `record_key` the record's key, never `config_changes`. The host file's `[[workspace]]` and
  `[[subscription]]` seed a record once, when the store holds none of that key; the file is not read for them after. The
  models own the lifecycle rules and the service the validation, in `blizzard/src/blizzard/runner/host_records/`; the
  store adapter writes the record, its lifecycle fact and its change row in one transaction; the decision and the
  refusals are `blizzard/src/blizzard/foundation/settings_record/`'s, shared with the hub-wide settings.

Implement tenant configured kinds against `blizzard/src/blizzard/hub/domain/config/records.py`: `ConfiguredRecord`
requires only revision and its check; retirement, name and slug are separate capabilities, and `ConfiguredLink` names
the link-specific capabilities. Reuse the applicable revision, transition, ordered field comparison, change-row,
slug-left and label-merge mechanics in `blizzard/src/blizzard/hub/domain/config/lifecycle.py`, which uses
`ConfigChange.of` in `blizzard/src/blizzard/hub/domain/config/changes.py`. Kinds own validation, projection, identity
and construction. Projects use the base capability without retirement; links use linked polarity and project
attribution, and position facts are not link revisions. Secrets' encryption and revision exception is outside these
helpers.

**Why.** Sparse merge is the only patch meaning under which two writers editing different fields do not overwrite each
other, and the only one a declarative apply's per-field difference maps onto without restating the record. One verb set
and one change log across kinds mean every door — API, CLI, board, document — changes a record the same way and leaves
the same trace.

**Scope.** Binds the kinds named above and any kind added beside them. How a record that other records reference is
identified and resolved is `bzh:configured-record-names` below.

**Detect.**

- A `PATCH` request model with a required field — a full replace under a patch verb.
- A `PATCH` request model that does not forbid extra fields, so an unknown field is silently dropped.
- A `PUT` that replaces a whole record, other than a secret's value replace; a project link's `PUT` replaces no fields.
- A `DELETE` route on a configured record.
- A changed write to a configured record with no change row in its transaction, or one that leaves `revision` where it
  was, except the secret lifecycle debt below; hub-wide settings and the host's records use their own audit rather than
  `config_changes`.
- A change row of a project, a project's link, or a record of any kind a project owns written without that record's
  project.
- A create of a kind a project owns that does not take the call's project by id or slug (`--project` on the CLI), does
  not fall back to the tenant's only project when the call names none, or refuses otherwise with anything but
  `422 project_required`, or whose refusal does not list the tenant's projects.
- A list of a kind a project owns, or the change log, that does not take `?project=` to narrow to one project or does
  not read the whole tenant without it.
- A patch handler that cannot tell an omitted field from an explicit `null`.

**Do.** `WorkItemPatchRequest` (`blizzard/src/blizzard/wire/work_source.py`) is the reference for telling an omitted
field from an explicit `null`: every field optional, `extra="forbid"`, and its nullable `stated_priority` told apart
through `model_fields_set` and `UNSET` (`blizzard/src/blizzard/hub/domain/kernel/unset.py`). A non-nullable field
refuses an explicit `null` with a 422 rather than reading it as unchanged. Retirement is an appended lifecycle fact, the
newest row deciding, as `scope_lifecycle_facts` holds it (`bzh:facts-not-status`, [./store-facts.md](./store-facts.md)).

Consumer semantics are proven in `blizzard/tests/unit/hub/domain/config/test_configured_record_lifecycle_rules.py`,
`blizzard/tests/unit/hub/domain/projects/test_model.py`, `blizzard/tests/unit/hub/domain/projects/test_links.py`,
`blizzard/tests/unit/hub/domain/garden/test_scopes.py` and `blizzard/tests/unit/hub/domain/garden/test_routines.py`.

For project editing or link authoring, follow `blizzard/src/blizzard/hub/domain/projects/model.py` and
`blizzard/src/blizzard/hub/domain/projects/links.py` into the shared records and lifecycle modules above. Reuse their
applicable mechanics: a project has no retirement capability, while a link's own linked state, composite identity and
project-attributed history are distinct from repository position facts.

**Don't.** An edit request that requires every field and a restated `name` under `PATCH` — two operators changing
different fields of one record silently revert each other.

**See also.** `bzh:configured-record-names` below owns the id, slug and display name of a record other records
reference; `bzh:fleet-wire-additive` ([./fleet-wire.md](./fleet-wire.md)) governs a configured route a runner reaches;
`bzh:controller-read-only` ([../repository-access.md](../repository-access.md)) keeps the write behind a domain service.

## A record other records reference carries three names (`bzh:configured-record-names`)

**Rule.** A record that other records reference and an operator renames carries three names, each with one job: a
hub-minted, immutable `<prefix>_<ulid>` id that every stored reference holds, a **slug** unique within its tenant that
is the handle people type, and a free display **name** that nothing resolves. A route's `{key}` for such a record is its
id or its slug, resolved once at the edge to the record by the shared id-or-slug resolution
(`blizzard/src/blizzard/hub/domain/kernel/id_or_slug.py`) — an id never as a slug, a current slug before a former one —
and nothing past the edge holds a slug. A slug the record leaves keeps resolving to it until another record claims it,
by one former-slug claim and release shared across kinds (`blizzard/src/blizzard/hub/store/internal/former_slugs.py`).
The record's change rows are keyed by its id and report its current slug as a label. The slug grammar is one for every
such kind: 1 to 64 lowercase letters, digits and single inner hyphens.

**Why.** A reference that held a slug would break on the next rename, and a slug resolved past the edge would resolve
differently at each door; one immutable id for references and one resolution for handles keep a rename a label change.

**Scope.** A project, a repository, a work source, a forge, a credential, and an urgency take the three names; a secret
is keyed by its name. An urgency's slug never changes, so it holds no former slug and takes no part in the former-slug
claim and release. A kind's own reserved slugs stay that kind's refusal.

**Detect.**

- A record that others reference and that is renamed, keyed in a reference, a change row or a route by its slug or its
  display name instead of its id; or a route's `{key}` that resolves an id and a slug by separate code instead of the
  shared id-or-slug resolution.
- A slug a record leaves that stops resolving while no other record holds it, or one that keeps resolving after another
  record claims it.

**Do.** The `config_changes` row a project rename appends: `record_kind="project"`, `record_key="proj_01M5…"`, the
project's id, the same before and after the rename.

**Don't.** A `config_changes` row keyed by a project's slug — the row loses its subject on the next rename.

**See also.** [../../domain/projects.md](../../domain/projects.md) §Former slugs — what a person sees when a slug is
reused or refused.

## Every ingested document decodes through the codec seam (`bzh:config-codec`)

**Rule.** Decode every document the hub ingests or the CLI reads for it — a declarative configuration document, a graph
definition — through `IConfigCodec`, and validate the decoded mapping against its kind's one wire model. The codec turns
bytes into a plain mapping and back and names the media types and file extensions it serves; validation happens after
decoding, never inside a binding.

**Why.** With one validator behind every format, a record means the same thing and fails with the same message whether
it arrived as YAML, JSON, or a later format. A parser called directly brings its own reading of the bytes — YAML 1.1
turning `no` into a boolean, a duplicate key silently winning — that the other doors do not share.

**Detect.** `yaml.safe_load`, `json.loads`, or any other parser called on an ingested document outside a codec binding;
a second model validating a kind that already has a wire model; a binding that validates or defaults fields itself. The
`bzh:config-codec` ast-grep rule fails a PyYAML import anywhere under `blizzard/src/blizzard/` outside the YAML binding.

**Do.** A new format is a new `IConfigCodec` binding selected by `Content-Type` on the API and by file extension in the
CLI (`bzh:pluggable-seams`, [./pluggable-seams.md](./pluggable-seams.md)); the YAML binding loads strictly — booleans
are `true` and `false` only, a duplicate key is an error.

**Don't.** A CLI verb that reads its file with `yaml.safe_load` and posts the result — the document it accepts is no
longer the document the API accepts.

## A declarative apply is a door, one transaction, and never a retire (`bzh:config-apply`)

**Rule.** Treat a tenant declarative apply as a door into the tenant's configured records and not an owner of them: it
reconciles each record the document names through the verbs the record's model already decides — create when absent, a
sparse edit of only the fields the entry states when present, enable when retired — and writes nothing for a record that
already stands as declared. Commit every write of one apply in a single transaction, each beside its `config_changes`
row, with the door set to `apply` by the server and every row sharing one `apply_id`. Never retire a record because the
document omits it. A dry run is the same transaction rolled back, so it reaches every refusal a real apply reaches and
returns the outcome the real apply would.

**Why.** An apply that owned the records would read an omitted record as a wish to remove it, and a document that left
out one entry could retire it. An apply that committed per record would leave a half-applied document behind its first
refusal. A dry run assembled from reads cannot know what a write's own checks — secret availability, uniqueness, the
compare-and-set — will refuse, so only the real transaction rolled back reports truthfully.

**Scope.** Binds every kind the tenant configuration document carries, not the separate hub settings document and its
apply above. A kind added to the tenant document adds its writes to the one transaction and its entries to the outcome
rows; it takes no transaction of its own. An apply reconciles the records of the tenant its request resolved, in that
tenant's one transaction; a document never reaches a second tenant. An apply composed with another write — seeding a
tenant at its creation — either joins `TenantAdministration.create`'s unit of work through `ScopedConnections.founding`
(`blizzard/src/blizzard/hub/store/scoped.py`), as [../crash-correctness/hub.md](../crash-correctness/hub.md) §Tenant
creation, one identity unit of work describes, or names the window between its commits in that file, owing what
`bzh:recorded-crash-exemption` ([../crash-correctness.md](../crash-correctness.md)) sets for an entry on that ground. A
document's `projects` section reconciles first, so an entry of any kind a project owns — a scope, a routine, or a kind
added beside them — may name a project the same document declares. The apply itself resolves no project: the package
that owns projects plans the section and the project each entry acts in, and hands both to it planned
(`blizzard/src/blizzard/hub/domain/projects/declarations.py`). A project entry's stated `sources` or `repositories` list
is that project's whole set, so a name the list leaves out is unlinked — the one write an omission drives, retiring a
link and never a record; a list the entry omits leaves the stored links. A project entry's `landing_order` lists the
repositories it ranks, first to land first, leaves every other linked repository unranked, and is planned after the
entry's links; an entry that omits it leaves the order as it stands, and export writes it only for a project that ranks
a repository. The `urgencies`, `urgency_order`, and `settings` sections reconcile after `projects` and before the
routines and cadences that may name an urgency, in that order, planned by the package that owns urgencies
(`blizzard/src/blizzard/hub/domain/urgency/`). An `urgencies` entry naming a retired urgency is refused
`urgency_retired` rather than enabled — the one kind an apply never revives, since reviving an urgency is an act an
operator takes on purpose — and so is any reference to a retired urgency anywhere in the document. A project entry
naming a former slug is refused rather than taking the slug back ([../../domain/projects.md](../../domain/projects.md)
§Former slugs), and an entry of any kind a project owns acts in the project its `project` names, by id or slug, resolved
as [../../domain/projects.md](../../domain/projects.md) §A call that needs a project states. Export writes each project
by its slug, the `projects` section first, so applying an export back writes nothing. A legacy import links the sources
and repositories it writes to the tenant's only project, and is refused when the tenant holds several. The runner host's
settings document binds too: `POST /api/host/settings/apply` on the runner host
(`blizzard/src/blizzard/runner/api/host_settings.py`) reconciles it through
`blizzard/src/blizzard/runner/settings/apply.py`, refuses the whole document on any entry's refusal, commits in one
transaction with door `apply` and one `apply_id`, and rolls a dry run back.

**Detect.**

- An apply path that commits per record or opens a second transaction.
- A retire, or any lifecycle write other than enable, driven by a record's absence from the document.
- A dry run that reads the store and predicts instead of running the writes and rolling them back.
- A change row from an apply with a door other than `apply`, or without the shared `apply_id`.
- An `apply` door value read from a request header or body.
- A runner host settings apply that commits part of a refused document, or commits outside its one transaction.
- An apply that plans the `projects` section or resolves an entry's project itself, rather than taking both planned from
  the package that owns projects.
- An apply that enables a retired urgency, or reconciles a routine or cadence before the urgency sections it may name.
- A document entry of a kind a project owns that does not take `project` by id or slug, does not act in the tenant's
  only project when it names none, or is not refused when the tenant holds several.

**Do.** `ConfigAuthoring.apply` in `blizzard/src/blizzard/hub/domain/config/authoring.py` is the reference:
`blizzard/src/blizzard/hub/domain/config/apply.py` decides the plan and
`blizzard/src/blizzard/hub/store/internal/config_apply_store.py` runs it. The plan is pure, the writer runs each planned
write through the same per-operation bodies the per-record adapters run, and a dry run raises a private sentinel after
the last write so the store rolls back. The runner host's apply mirrors it:
`blizzard/src/blizzard/runner/settings/apply.py` plans and
`blizzard/src/blizzard/runner/store/internal/host_settings_apply_store.py` runs the plan.

**Don't.** A dry run that checks "would this name collide" with a select of its own — it passes while the real apply
fails on a check the select did not know to make.

**See also.** `bzh:configured-record` above owns the sparse merge and the change row; `bzh:config-codec` owns how the
document decodes.

## A secret value is write-only (`bzh:secret-write-only`)

**Rule.** Never return or record a secret value: no route reads one back, and no response, log line, span attribute,
event, or change row carries one. A value enters in the body of a create or replace, is decrypted only at the moment it
is used, and lives only inside the object built from it. A value is never blank: every door refuses a blank one.

**Why.** Every surface that can return or record a value is a place it leaks from and a copy that survives its
replacement. A value that nothing can read back needs no read permission to guard and leaves nothing behind to scrub.

**Scope.** A secret belongs to one tenant, like every tenant configured record, and its name is unique within that
tenant (`bzh:tenant-scoped-uniqueness`). The hub's one secret key seals every tenant's values, each against its own
`(name, revision)` (`blizzard/src/blizzard/foundation/secrets/internal/aes_gcm.py`); the tenant boundary on a value is
the store's, never the cipher's. A runner host's hub tokens are secret values too: the host's own key —
`BZ_HOST_SECRET_KEY`, or the host directory's `data/secret-keys/` — seals each under the name
`runner-hub-token/<runner_id>` at its row's revision (`blizzard/src/blizzard/runner/hub/sealed_tokens.py`), so a token
copied to another runner's row or restored at an older revision does not open, and the prefix keeps its binding apart
from any hub secret's.

**Detect.** A `SecretValue` reaching a controller, a serializer, or a logger; an `ISecretReader` injected anywhere but
an object the composition root builds to call an external system — for a forge, only the forge authorization boundary
under `hub/forge/internal/` — which reveals a value per use (`bzh:config-read-on-use`), never once at start; a secret's
view, change-row diff, or apply outcome with a value or ciphertext field; a value taken from a command-line argument.

**Do.** A secret's view carries its name, revision, who replaced it and when, and the records that reference it. A
replace appends a change row with no diff. The CLI reads a value from stdin.

**Don't.** A `show` response with the value masked to its last four characters — a partial value is still a value, and
the route that serves it has read the plaintext.

## Configuration is read at its use (`bzh:config-read-on-use`)

**Rule.** Read a configured record from the store at the use that needs it — a request when it runs, a sweep at the
start of each pass, a hub step when it starts — and cache anything built from a record under that record's revision. The
store is the authority over configured records; only values whose declared lifetime is boot are fixed for the process.

**Why.** A record read on use makes a change take effect on the next use with no restart and nothing to announce it, in
one hub process or several. A cache keyed by revision holds nothing true only in memory: a cold cache is correct, and a
second process reading the same revisions builds equivalent objects.

**Scope.** Binds configured records, including hub-wide settings. Each tenant's records build into that tenant's own
cache, the tenant's registered `ConfigObjectCache` (`blizzard/src/blizzard/hub/live_config/wiring.py`), so an object
built from one tenant's record never serves another's request or pass. Hub-wide settings are shared across tenants, not
placed in a tenant cache. A hub setting's declared lifetime decides when a change takes effect: a `boot` value is fixed
for the running process and needs a restart; a later-lifetime value is read at its use. The hub's file seeds a stated
key only when no stored entry exists, including an unset entry; it is not the authority over an existing entry. Boot
inputs such as the root and secret key — `BZ_HUB_SECRET_KEY` on the hub, `BZ_HOST_SECRET_KEY` on a runner host — and
environment overrides declared for boot keys, remain process inputs.

**Detect.**

- A later-lifetime configured value captured at composition time into a long-lived object.
- A cache of a configured record, or of an object built from one, keyed without its revision — or without its secret's
  revision when the object holds a credential.
- A configured value read from `os.environ` outside the declared boot overrides and key bootstrap.
- A decrypted secret value cached on its own rather than inside a built object.

**Do.** A built object — an authenticated client, a work-source adapter, a resolver — is kept under
`(kind, key, revision, credential_id, credential_revision, secret_name, secret_revision)`, `key` being the record's own
key, and the secret being the credential's for a record naming one; before handing one out, the cache reads the current
revisions in one indexed read, reuses the entry on a match, and otherwise builds a new object and closes the one it
replaces. Each read is an indexed single-row read or a read of the active set (`bzh:live-set-read`,
[../read-cost.md](../read-cost.md)).

**Don't.** A work-source registry built as a dict in the composition root — an edit to a source reaches nothing until
the hub restarts, and a second hub process answers from a different dict.

**See also.** `bzh:dependency-injection` ([../clean-architecture.md](../clean-architecture.md)): the composition root
wires the store-backed reader, not the records it reads.

## One hub settings snapshot per entry (`bzh:hub-settings-snapshot-per-entry`)

**Rule.** Resolve hub-wide settings once at the start of each request, sweep pass, or hub step that needs them, and use
that immutable effective configuration throughout that entry. The next entry reads again. A revision-keyed reader may
reuse a snapshot after checking the store's current revision; do not capture a pass-lifetime value in a long-lived
service at boot. Read a sweep's scheduling interval afresh when scheduling the next pass.

**Why.** A single entry must not combine values from both sides of an edit, while a later entry must see the edit
without a restart.

**Scope.** Hub-wide settings only; this rule makes no claim about runner settings. Boot-lifetime values remain fixed for
the process. The store snapshot rule for a pass's deciding data reads remains `bzh:pass-reads-one-snapshot`
([../repository-access.md](../repository-access.md)); a settings snapshot does not replace that transaction.

**Detect.** A request, pass, or hub step resolving settings more than once, or a long-lived hub service using a
boot-captured pass-lifetime setting.

**Do.** `blizzard/src/blizzard/hub/api/request_config.py` memoizes the effective configuration on the request;
`blizzard/src/blizzard/hub/settings/pass_config.py` binds it for a pass.

**Don't.** Read a setting again halfway through a sweep after an operator edit: the pass would act on two revisions.

**See also.** `bzh:config-read-on-use` above owns revision-keyed reads and the lifetime boundary.

## A process setting is read only through its daemon's registry (`bzh:config-key-declared`)

**Rule.** Seed or validate a key of `blizzard-hub.toml` or `blizzard-host.toml` through the strict accessor over its
daemon's registry (`blizzard/src/blizzard/hub/config_keys.py`, `blizzard/src/blizzard/runner/config_keys.py`), and
declare in that registry every key read and every durable path under the daemon's runtime root. Adding, retiring or
retyping a key changes `contracts/config/`. A retired key stays declared `deprecated`, with `replaced_by` naming its
home.

Every value key declares its lifetime, and a grouping key declares none. A deprecated key takes its replacement's
lifetime. `env`, legal only on a `boot` key, names the environment variable that supplies the key and overrides the
file. Moving a key's lifetime later is a break that `blizzard:compat` reports; moving it earlier is additive.

On the hub, the file accessor is for seeding and configuration validation, not a runtime source for settings already
held in the store. Runtime consumers take the effective settings snapshot at their entry; they do not bypass it by
reading the file or its accessor. The runner host holds the same line: a `pass` or `session` key of `blizzard-host.toml`
read through `ConfigView` outside the seed is a finding, since the host and runner settings records own those values
once seeded. Shared settings-record write and seed decisions remain owned by
`blizzard/src/blizzard/foundation/settings_record/`, not a daemon-specific copy.

**Why.** A key the code reads and no document lists is a setting an operator cannot discover and a release cannot diff.
Refusing a retired key is itself a read of it, so the registry stays complete only while those keys stay declared.

**Scope.** Binds the daemons' process settings in their toml files. A key the loader reads and ignores at runtime stays
ignored: an undeclared key in a file loads, and an undeclared read in the test suite raises.

**Detect.**

- A `tomllib` read of the daemon's file outside its loader, or a section parser given a bare `dict` rather than a view.
- A key read through the view and absent from the registry, or declared and never read.
- A registry edit with no regenerated `contracts/config/` document.
- A value key with no lifetime, a grouping key with one, or `env` on a key that is not `boot`: the registry refuses it
  at construction, so the daemon fails at import.
- A key whose lifetime moved later than the latest supported release declares: `blizzard:compat` fails on the `config`
  surface.

The `bzh:config-key-declared` ast-grep rule fails a `tomllib` import anywhere under `blizzard/src/blizzard/runner/` or
`blizzard/src/blizzard/hub/` outside `runner/host_config.py`, `hub/config.py`, `hub/domain/runners/version_window.py`,
and the document codec `hub/documents/internal/toml_codec.py`.

**Do.** Pass the registry to the loader's root view, and hand each section parser the view at its table; declare a
section's keys beside its parser.

**Don't.** Import a daemon's registry from a section parser: the registry composes the sections, so the import closes a
cycle.

## Runner settings hold one snapshot per pass (`bzh:settings-snapshot-per-pass`)

**Rule.** Resolve the host's and each runner's pass and session entries from the runner store at use, over boot-held
configuration, not from a cached file value. A tick, a host pass and a trace sweep each acquire one coherent revision —
for a runner tick, the pair of host and runner revisions — and entries, the host's revision covering its active
workspace and subscription records with its settings, and hold their own immutable snapshot for the whole pass. Cache
built objects under their actual inputs or revisions. Publish a rebuilt context only after a successful build, together
with its harness set, whose replacement and retention `bzh:pluggable-seams` owns; keep the last good context on failure,
report a failed rebuild's acquired revision and retry on a later pass. Startup without a good build fails. A launch
takes session settings from its pass and records both of the pass's revisions and its transcript root; a resume
preserves the original session's locating values and, when recorded, its transcript root. Already-running invocations
retain their launch settings.

**Why.** Reading individual keys mid-pass could combine revisions that never existed, while replacing a harness under a
running invocation could change how its result is read. A failed build must not discard the last usable context.

**Scope.** Host and runner pass and session keys, including the host tick, trace sweeps, host tool children and all
launch paths. Boot settings remain boot-owned. Explicit file values seed only missing entries after identity and store
checks; defaults are not materialized, and a stored unset remains authoritative on later starts. A timed driver's
interval is the one read outside a pass's snapshot: it is evaluated at the host record's current revision, so a write
that wakes the driver is not waited out at the old value. A snapshot acquisition that fails before returning a revision
is distinct from a rebuild failing after one was acquired: the tick retains its last context and retries, but does not
record that failure in `in_force.failed`, since that view requires a revision and may retain an earlier failure. The
settings API also reads the store, so an ongoing store error can prevent the view itself from being returned.

**Detect.** A pass re-reading live entries midway through its work, an object cached without its settings inputs, a
failed rebuild replacing only part of the context, or a running invocation switched to a new harness set or transcript
root.

**Do.** `RunnerSettingsReader` (`blizzard/src/blizzard/runner/settings_reader.py`) and `RunnerStepper`
(`blizzard/src/blizzard/runner/loop_wiring.py`) resolve the snapshot at the pass boundary; `HostSettingsReader`'s
snapshot carries the host's active workspace and subscription records and their revisions, read once per pass, and the
host tick rebuilds the workspace registry and each moved subscription's sampler and renewer from it, with no restart;
`SessionSettings` (`blizzard/src/blizzard/runner/harness/session_settings.py`) and `HarnessSets`
(`blizzard/src/blizzard/runner/harness/harness_set.py`) retain invocation ownership.

**Don't.** Resolve the budget separately at every step of one tick, allowing an edit halfway through to change its
remaining decisions.

**See also.** `bzh:config-read-on-use` above owns hub configured-record reads; `bzh:pluggable-seams`
([./pluggable-seams.md](./pluggable-seams.md)) owns harness set replacement and retained harness bindings.

## Known debt

Stated so a reviewer need not re-derive them — each is a site the rules above name as a violation and that stands until
the change that brings it under the rule:

- Graphs are not records under the rule: a graph's mutable flag is a sparse `PATCH` that appends a policy fact, with no
  `revision` or change row.
- **A secret's retire and enable move no revision.** Each appends a change row at the secret's unchanged revision,
  because its value is sealed against `(name, revision)` and a revision moved without resealing would leave the value
  undecryptable. A forge's, a credential's, a work source's, or a repository's retire and enable do move its revision.
- **The work-item patch reads `null` as unchanged.** `WorkItemPatchRequest` declares `title` and `body` nullable, and
  its handler (`blizzard/src/blizzard/hub/api/work_sources.py`) maps an explicit `null` on either to unchanged rather
  than refusing it.
- **The runner settings route does not refuse a write from a retired runner.** `PATCH /api/settings`
  (`blizzard/src/blizzard/runner/api/settings.py`) accepts a write for a retired runner, where it owes
  `409 runner_retired`: the route holds no authoritative local hosted-runner fact to resolve retirement from. A refused
  token, a missing or halted registry entry, and a hub outage are not evidence of retirement, and settings writes remain
  hub-independent. Identity, settings, and history stay together until explicit archive cleanup, which does not itself
  make the route retirement-aware.
