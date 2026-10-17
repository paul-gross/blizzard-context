# Configuration

This spoke owns how the hub's configured surfaces are changed and read — the one verb set and patch meaning every
configured record shares, how a declarative document is decoded, what may carry a secret, and when configuration is
read; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned
by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

A **configured record** is a row the hub holds as operator-set configuration and that an operator changes while the hub
runs: a work source, a repository, a secret, a project, a scope, a routine. The rules below name the seams and tables
that keep them — `IConfigCodec`, `SecretValue`, `ISecretReader`, `config_changes` — by the names their implementations
take, so code adding one of them takes the name stated here. [Known debt](#known-debt) lists the code these rules do not
yet hold.

## Every configured record takes one verb set and one patch meaning (`bzh:configured-record`)

**Rule.** Give every configured record the same verb set — create, list, show, edit, retire, enable — an edit that is a
sparse merge, a `revision` that every committed write increments, one `config_changes` row appended in the same
transaction as each write, and retirement in place of deletion. A sparse merge leaves an absent field unchanged, sets a
present field, and takes an explicit `null` as clearing a nullable field, refusing it on any other. A retire of a
retired record, or an enable of an enabled one, writes nothing; an edit of a retired record is legal and leaves it
retired.

| Verb   | Route                           |
| ------ | ------------------------------- |
| create | `POST /api/<kind>`              |
| list   | `GET /api/<kind>`               |
| show   | `GET /api/<kind>/{key}`         |
| edit   | `PATCH /api/<kind>/{key}`       |
| retire | `POST /api/<kind>/{key}/retire` |
| enable | `POST /api/<kind>/{key}/enable` |

Enable reverses a retirement. Every CLI noun carries the same six verbs, a secret's replace standing in for its edit.

A record that other records reference and an operator renames — a project, a repository — carries three names, each with
one job: a hub-minted, immutable `<prefix>_<ulid>` id that every stored reference holds, a **slug** unique within its
tenant that is the handle people type, and a free display **name** that nothing resolves. A route's `{key}` for such a
record is its id or its slug, resolved once at the edge to the record by the shared id-or-slug resolution
(`blizzard/src/blizzard/hub/domain/kernel/id_or_slug.py`) — an id never as a slug, a current slug before a former one —
and nothing past the edge holds a slug. A slug the record leaves keeps resolving to it until another record claims it,
by one former-slug claim and release shared across kinds (`blizzard/src/blizzard/hub/store/internal/former_slugs.py`).
The record's change rows are keyed by its id and report its current slug as a label. The slug grammar is one for every
such kind: 1 to 64 lowercase letters, digits and single inner hyphens. A kind's own reserved slugs stay that kind's
refusal.

**Why.** Sparse merge is the only patch meaning under which two writers editing different fields do not overwrite each
other, and the only one a declarative apply's per-field difference maps onto without restating the record. One verb set
and one change log across kinds mean every door — API, CLI, board, document — changes a record the same way and leaves
the same trace.

**Scope.** Binds the six kinds named above and any kind added beside them. A project, a repository, and a work source
take the three names above; a secret is keyed by its name. A project takes create, list, show, and edit but no retire or
enable: a project, once created, stays ([../../domain/projects.md](../../domain/projects.md)). Its links to sources and
repositories carry the lifecycle in its place, each its own revisioned record whose change rows reuse the verbs —
`create` for a link, `retire` for an unlink, `enable` for a relink — each beside its link fact. A link is named into
being by `PUT /api/projects/{project}/source-links/{source}` (or `repository-links/{repository}`), which links or
relinks and leaves a standing link as it is, and unlinked by that path's `POST …/retire`; on the CLI,
`blizzard hub project link` and `unlink`. A record a project owns is created in a project the call names — `--project`
on the CLI, by id or slug — or, when it names none, in the tenant's project if it holds exactly one, and is refused
`422 project_required`, listing the tenant's projects, otherwise; its list, and the change log, take `?project=` to
narrow to one project and read the whole tenant without it ([../../domain/projects.md](../../domain/projects.md) §A call
that needs a project). A change row of a project, a project's link, or a record of any kind a project owns — a scope, a
routine, or a kind added beside them — names that record's project, since its key means something only inside its
project; one of a tenant-wide record — a work source, a repository, a secret — names none. A graph is an immutable mint,
so its definition takes no patch — an edit is a new mint — and only its mutable flags take the sparse `PATCH`, beside
its retire and enable, each of which appends a fact even when it repeats the standing value
([../../domain/graphs/identity.md](../../domain/graphs/identity.md)). A work item is work, not configuration: its patch
carries the sparse-merge meaning, and it takes no revision, no change row, and keeps its `DELETE`. A secret takes
replace in place of edit: its value is replaced whole by `PUT /api/secrets/{name}/value` — on the CLI,
`blizzard hub secret set NAME`, reading the value from stdin — and the replace still increments the revision and appends
its change row.

**Detect.**

- A `PATCH` request model with a required field — a full replace under a patch verb.
- A `PATCH` request model that does not forbid extra fields, so an unknown field is silently dropped.
- A `PUT` that replaces a whole record, other than a secret's value replace; a project link's `PUT` replaces no fields.
- A `DELETE` route on a configured record.
- A write to a configured record with no `config_changes` row in its transaction, or one that leaves `revision` where it
  was.
- A change row of a project, a project's link, or a record of any kind a project owns written without that record's
  project.
- A create of a kind a project owns that does not take the call's project by id or slug (`--project` on the CLI), does
  not fall back to the tenant's only project when the call names none, or refuses otherwise with anything but
  `422 project_required`, or whose refusal does not list the tenant's projects.
- A list of a kind a project owns, or the change log, that does not take `?project=` to narrow to one project or does
  not read the whole tenant without it.
- A patch handler that cannot tell an omitted field from an explicit `null`.
- A record that others reference and that is renamed, keyed in a reference, a change row or a route by its slug or its
  display name instead of its id; or a route's `{key}` that resolves an id and a slug by separate code instead of the
  shared id-or-slug resolution.
- A slug a record leaves that stops resolving while no other record holds it, or one that keeps resolving after another
  record claims it.

**Do.** `WorkItemPatchRequest` (`blizzard/src/blizzard/wire/work_source.py`) is the reference for telling an omitted
field from an explicit `null`: every field optional, `extra="forbid"`, and its nullable `stated_priority` told apart
through `model_fields_set` and `UNSET` (`blizzard/src/blizzard/hub/domain/kernel/unset.py`). A non-nullable field
refuses an explicit `null` with a 422 rather than reading it as unchanged. Retirement is an appended lifecycle fact, the
newest row deciding, as `scope_lifecycle_facts` holds it (`bzh:facts-not-status`, [./store-facts.md](./store-facts.md)).

**Don't.** An edit request that requires every field and a restated `name` under `PATCH` — two operators changing
different fields of one record silently revert each other.

**See also.** `bzh:fleet-wire-additive` ([./fleet-wire.md](./fleet-wire.md)) governs a configured route a runner
reaches; `bzh:controller-read-only` ([../repository-access.md](../repository-access.md)) keeps the write behind a domain
service.

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
CLI (`bzh:pluggable-seams`, [../system-shape.md](../system-shape.md)); the YAML binding loads strictly — booleans are
`true` and `false` only, a duplicate key is an error.

**Don't.** A CLI verb that reads its file with `yaml.safe_load` and posts the result — the document it accepts is no
longer the document the API accepts.

## A declarative apply is a door, one transaction, and never a retire (`bzh:config-apply`)

**Rule.** Treat a declarative apply as a door into the configured records and not an owner of them: it reconciles each
record the document names through the verbs the record's model already decides — create when absent, a sparse edit of
only the fields the entry states when present, enable when retired — and writes nothing for a record that already stands
as declared. Commit every write of one apply in a single transaction, each beside its `config_changes` row, with the
door set to `apply` by the server and every row sharing one `apply_id`. Never retire a record because the document omits
it. A dry run is the same transaction rolled back, so it reaches every refusal a real apply reaches and returns the
outcome the real apply would.

**Why.** An apply that owned the records would read an omitted record as a wish to remove it, and a document that left
out one entry could retire it. An apply that committed per record would leave a half-applied document behind its first
refusal. A dry run assembled from reads cannot know what a write's own checks — secret availability, uniqueness, the
compare-and-set — will refuse, so only the real transaction rolled back reports truthfully.

**Scope.** Binds every kind a document carries. A kind added to the document adds its writes to the one transaction and
its entries to the outcome rows; it takes no transaction of its own. An apply reconciles the records of the tenant its
request resolved, in that tenant's one transaction; a document never reaches a second tenant. An apply composed with
another write — seeding a tenant at its creation — either joins `TenantAdministration.create`'s unit of work through
`ScopedConnections.founding` (`blizzard/src/blizzard/hub/store/scoped.py`), as
[../crash-correctness/hub.md](../crash-correctness/hub.md) §Tenant creation, one identity unit of work describes, or
names the window between its commits in that file, owing what [../crash-correctness.md](../crash-correctness.md)
§Recorded exemptions — durable state the sweep does not arm sets for an entry on that ground.

A document's `projects` section reconciles first, so an entry of any kind a project owns — a scope, a routine, or a kind
added beside them — may name a project the same document declares. The apply itself resolves no project: the package
that owns projects plans the section and the project each entry acts in, and hands both to it planned
(`blizzard/src/blizzard/hub/domain/projects/declarations.py`). A project entry's stated `sources` or `repositories` list
is that project's whole set, so a name the list leaves out is unlinked — the one write an omission drives, retiring a
link and never a record; a list the entry omits leaves the stored links. A project entry naming a slug some project has
moved away from is refused, naming the project that left it, rather than taking the slug back. An entry of any kind a
project owns acts in the project its `project` names, by id or slug, or the tenant's only project when it names none,
and is refused when the tenant holds several. Export writes each project by its slug, the `projects` section first, so
applying an export back writes nothing. A legacy import links the sources and repositories it writes to the tenant's
only project, and is refused when the tenant holds several.

**Detect.**

- An apply path that commits per record or opens a second transaction.
- A retire, or any lifecycle write other than enable, driven by a record's absence from the document.
- A dry run that reads the store and predicts instead of running the writes and rolling them back.
- A change row from an apply with a door other than `apply`, or without the shared `apply_id`.
- An `apply` door value read from a request header or body.
- An apply that plans the `projects` section or resolves an entry's project itself, rather than taking both planned from
  the package that owns projects.
- A document entry of a kind a project owns that does not take `project` by id or slug, does not act in the tenant's
  only project when it names none, or is not refused when the tenant holds several.

**Do.** `ConfigAuthoring.apply` (`blizzard/src/blizzard/hub/domain/config/apply.py` decides the plan,
`blizzard/src/blizzard/hub/store/internal/config_apply_store.py` runs it) is the reference: the plan is pure, the writer
runs each planned write through the same per-operation bodies the per-record adapters run, and a dry run raises a
private sentinel after the last write so the store rolls back.

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

**Exception.** The forge token placed in a `run:` step's environment, which `bzh:hub-node-env-contract`
([../../standards/hub-nodes/env-contract.md](../../standards/hub-nodes/env-contract.md)) owns — the one place a value
leaves the hub process, and no licence to log or return it there.

**Scope.** A secret belongs to one tenant, like every configured record, and its name is unique within that tenant
(`bzh:tenant-scoped-uniqueness`). The hub's one secret key seals every tenant's values, each against its own
`(name, revision)` (`blizzard/src/blizzard/hub/secrets/internal/aes_gcm.py`); the tenant boundary on a value is the
store's, never the cipher's.

**Detect.** A `SecretValue` reaching a controller, a serializer, or a logger; an `ISecretReader` injected anywhere but
an object the composition root builds to call an external system — which reveals a value per use
(`bzh:config-read-on-use`), never once at start; a secret's view, change-row diff, or apply outcome with a value or
ciphertext field; a value taken from a command-line argument.

**Do.** A secret's view carries its name, revision, who replaced it and when, and the records that reference it. A
replace appends a change row with no diff. The CLI reads a value from stdin.

**Don't.** A `show` response with the value masked to its last four characters — a partial value is still a value, and
the route that serves it has read the plaintext.

## Configuration is read at its use (`bzh:config-read-on-use`)

**Rule.** Read a configured record from the store at the use that needs it — a request when it runs, a sweep at the
start of each pass, a hub step when it starts — and cache anything built from a record under that record's revision. The
store is the only answer to what is configured; no process holds configuration in memory as truth.

**Why.** A record read on use makes a change take effect on the next use with no restart and nothing to announce it, in
one hub process or several. A cache keyed by revision holds nothing true only in memory: a cold cache is correct, and a
second process reading the same revisions builds equivalent objects.

**Scope.** Binds configured records. Each tenant's records build into that tenant's own cache, opened with its services
(`build_live_config`, `blizzard/src/blizzard/hub/composition.py`), so an object built from one tenant's record never
serves another's request or pass. Process settings in the hub's file — its root, store URL, bind address, auth and
tracing settings, and the hub secret key — are read at start and changed by a restart.

**Detect.**

- A configured record captured at composition time into a long-lived object.
- A cache of a configured record, or of an object built from one, keyed without its revision — or without its secret's
  revision when the object holds a credential.
- A configured value read from `os.environ` outside the hub's file and key bootstrap.
- A decrypted secret value cached on its own rather than inside a built object.

**Do.** A built object — an authenticated client, a work-source adapter, a resolver — is kept under
`(kind, key, revision, secret_name, secret_revision)`, `key` being the record's own key; before handing one out, the
cache reads the current revisions in one indexed read, reuses the entry on a match, and otherwise builds a new object
and closes the one it replaces. Each read is an indexed single-row read or a read of the active set
(`bzh:live-set-read`, [../read-cost.md](../read-cost.md)).

**Don't.** A work-source registry built as a dict in the composition root — an edit to a source reaches nothing until
the hub restarts, and a second hub process answers from a different dict.

**See also.** `bzh:dependency-injection` ([../clean-architecture.md](../clean-architecture.md)): the composition root
wires the store-backed reader, not the records it reads.

## Known debt

Stated so a reviewer need not re-derive them — each is a site the rules above name as a violation and that stands until
the change that brings it under the rule:

- **Only work sources, repositories, secrets, scopes, and routines are configured records so far.** `config_changes`
  carries all five, and `ConfigAuthoring` the first three; the hub reads work sources and repositories on use. Graphs
  are not records under the rule: a graph's mutable flag is a sparse `PATCH` that appends a policy fact, with no
  `revision` or change row.
- **A secret's retire and enable move no revision.** Each appends a change row at the secret's unchanged revision,
  because its value is sealed against `(name, revision)` and a revision moved without resealing would leave the value
  undecryptable. A work source's or a repository's retire and enable do move its revision.
- **The work-item patch reads `null` as unchanged.** `WorkItemPatchRequest` declares `title` and `body` nullable, and
  its handler (`blizzard/src/blizzard/hub/api/work_sources.py`) maps an explicit `null` on either to unchanged rather
  than refusing it.
