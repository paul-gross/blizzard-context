# Configuration

This spoke owns how the hub's configured surfaces are changed and read — the one verb set and patch meaning every
configured record shares, how a declarative document is decoded, what may carry a secret, and when configuration is
read; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned
by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

A **configured record** is a row the hub holds as operator-set configuration and that an operator changes while the hub
runs: a work source, a repository, a secret, a scope, a routine. The rules below name the seams and tables that keep
them — `IConfigCodec`, `SecretValue`, `ISecretReader`, `config_changes` — by the names their implementations take, so
code adding one of them takes the name stated here. [Known debt](#known-debt) lists the code these rules do not yet
hold.

## Every configured record takes one verb set and one patch meaning (`bzh:configured-record`)

**Rule.** Give every configured record the same verb set — create, list, show, edit, retire, enable — an edit that is a
sparse merge, a `revision` that every committed write increments, one `config_changes` row appended in the same
transaction as each write, and retirement in place of deletion. A sparse merge leaves an absent field unchanged, sets a
present field, and takes an explicit `null` as clearing a nullable field, refusing it on any other.

| Verb   | Route                           |
| ------ | ------------------------------- |
| create | `POST /api/<kind>`              |
| list   | `GET /api/<kind>`               |
| show   | `GET /api/<kind>/{key}`         |
| edit   | `PATCH /api/<kind>/{key}`       |
| retire | `POST /api/<kind>/{key}/retire` |
| enable | `POST /api/<kind>/{key}/enable` |

Enable reverses a retirement. Every CLI noun carries the same six verbs, a secret's replace standing in for its edit.

**Why.** Sparse merge is the only patch meaning under which two writers editing different fields do not overwrite each
other, and the only one a declarative apply's per-field difference maps onto without restating the record. One verb set
and one change log across kinds mean every door — API, CLI, board, document — changes a record the same way and leaves
the same trace.

**Scope.** Binds the five kinds named above and any kind added beside them. A graph is an immutable mint, so its
definition takes no patch — an edit is a new mint — and only its mutable flags take the sparse `PATCH`, beside its
retire and enable. A work item is work, not configuration: its patch carries the sparse-merge meaning, and it takes no
revision, no change row, and keeps its `DELETE`. A secret takes replace in place of edit: its value is replaced whole by
`PUT /api/secrets/{name}/value` — on the CLI, `blizzard hub secret set NAME`, reading the value from stdin — and the
replace still increments the revision and appends its change row.

**Detect.**

- A `PATCH` request model with a required field — a full replace under a patch verb.
- A `PATCH` request model that does not forbid extra fields, so an unknown field is silently dropped.
- A `PUT` that replaces a whole record, other than a secret's value replace.
- A `DELETE` route on a configured record.
- A write to a configured record with no `config_changes` row in its transaction, or one that leaves `revision` where it
  was.
- A patch handler that cannot tell an omitted field from an explicit `null`.

**Do.** `WorkItemPatchRequest` (`blizzard/src/blizzard/wire/work_source.py`) is the reference for telling an omitted
field from an explicit `null`: every field optional, `extra="forbid"`, and its nullable `stated_priority` told apart
through `model_fields_set` and `UNSET` (`blizzard/src/blizzard/hub/domain/edit.py`). A non-nullable field refuses an
explicit `null` with a 422 rather than reading it as unchanged. Retirement is an appended lifecycle fact, the newest row
deciding, as `scope_lifecycle_facts` holds it (`bzh:facts-not-status`, [./store-facts.md](./store-facts.md)).

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
a second model validating a kind that already has a wire model; a binding that validates or defaults fields itself.

**Do.** A new format is a new `IConfigCodec` binding selected by `Content-Type` on the API and by file extension in the
CLI (`bzh:pluggable-seams`, [../system-shape.md](../system-shape.md)); the YAML binding loads strictly — booleans are
`true` and `false` only, a duplicate key is an error.

**Don't.** A CLI verb that reads its file with `yaml.safe_load` and posts the result — the document it accepts is no
longer the document the API accepts.

## A secret value is write-only (`bzh:secret-write-only`)

**Rule.** Never return or record a secret value: no route reads one back, and no response, log line, span attribute,
event, or change row carries one. A value enters in the body of a create or replace, is decrypted only at the moment it
is used, and lives only inside the object built from it.

**Why.** Every surface that can return or record a value is a place it leaks from and a copy that survives its
replacement. A value that nothing can read back needs no read permission to guard and leaves nothing behind to scrub.

**Exception.** The forge token placed in a `run:` step's environment, which `bzh:hub-node-env-contract`
([../../standards/hub-nodes/env-contract.md](../../standards/hub-nodes/env-contract.md)) owns — the one place a value
leaves the hub process, and no licence to log or return it there.

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

**Scope.** Binds configured records. Process settings in the hub's file — its root, store URL, bind address, auth and
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
(`bzh:live-set-read`, [../repository-access.md](../repository-access.md)).

**Don't.** A work-source registry built as a dict in the composition root — an edit to a source reaches nothing until
the hub restarts, and a second hub process answers from a different dict.

**See also.** `bzh:dependency-injection` ([../clean-architecture.md](../clean-architecture.md)): the composition root
wires the store-backed reader, not the records it reads.

## Known debt

Stated so a reviewer need not re-derive them — each is a site the rules above name as a violation and that stands until
the change that brings it under the rule:

- **The seams and the change log are not yet in the tree.** `IConfigCodec`, `SecretValue`, `ISecretReader`, and
  `config_changes` have no implementation; of the five kinds, only scopes and routines exist as records, and neither
  carries a `revision`.
- **Routine and scope edits are full replaces.** `RoutineEditRequest` (`blizzard/src/blizzard/wire/routine.py`) requires
  every field and a restated `name`, and the scope edit replaces its one field.
- **The work-item patch reads `null` as unchanged.** `WorkItemPatchRequest` declares `title` and `body` nullable, and
  its handler (`blizzard/src/blizzard/hub/api/work_sources.py`) maps an explicit `null` on either to unchanged rather
  than refusing it.
- **Graph definitions are parsed directly.** `yaml.safe_load` is called in `blizzard/src/blizzard/hub/graph_sync.py`,
  `blizzard/src/blizzard/hub/graphs/__init__.py`, and `blizzard/src/blizzard/hub/api/graphs.py`.
- **Work sources and forge settings are read once at start.** `blizzard/src/blizzard/hub/app.py` builds the work-source
  registry from the hub's file and reads the forge endpoint and token from `BZ_FORGE_*` in the process environment — the
  configured forge endpoint `bzh:pluggable-seams`'s recorded positions describe.
