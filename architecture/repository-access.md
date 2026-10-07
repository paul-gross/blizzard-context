# Repository access

These rules refine the dependency-inversion seam [`./clean-architecture.md`](./clean-architecture.md) owns
(`bzh:dependency-inversion`): they govern who may hold which repository, what crosses the domain boundary, and what a
read may cost. Each rule below uses the slot skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`), with its
`bzh:` id carried in its heading.

## Split every repository seam (`bzh:repository-split`)

**Rule.** Every repository seam splits into a read-only Protocol and a write Protocol, and a collaborator depends on the
narrowest one its job needs.

**Why.** The Protocol a service depends on makes its intent enforceable at type-check time, and is what the layer gate
`bzh:controller-read-only` keys on.

**Detect.** One repository Protocol exposing both queries and mutations, or a read-path service holding a write-capable
one.

**Scope.** A seam whose reads only project other concepts' own fact tables, with no mutation of its own, stays read-only
rather than pairing with an empty write half: `blizzard/src/blizzard/hub/domain/chunk/ports/facts.py`'s
`IReadChunkFactsRepository` has no write counterpart because `load_facts`/`load_all_facts` project the union of the
other seams' own writes, and splitting that projection per concept would turn one bounded read into one per seam.

**Do.** `blizzard/src/blizzard/hub/domain/chunk/ports/record.py` pairs `IReadChunkRecordRepository` with
`IWriteChunkRecordRepository`, the write variant extending the read one; the composition root binds the write variant
only where mutation is required.

**Don't.** One combined repository injected everywhere, handing a controller that only lists chunks the power to delete
them.

**See also.** [`../exemplars/python/repo_pattern.py`](../exemplars/python/repo_pattern.py) — the read/write Protocol
pair and its binding in runnable form. [`./system-shape/exclusive-writes.md`](./system-shape/exclusive-writes.md)
`bzh:store-exclusive-write` — the one seam where a write Protocol splits further than read and write; read it before
adding or calling a `*_locked` method.

## Controllers hold read repositories only (`bzh:controller-read-only`)

**Rule.** Access is layer-gated — controllers at the API and CLI edges hold read-only repositories only, and write
repositories belong to the domain layer alone.

**Why.** A controller able to write around the domain can violate an invariant the domain exists to protect.

**Scope.** A controller answering a query straight from a read model is fine: reads bypass no invariant.

**Detect.** A router or CLI handler injecting a write repository, or a mutation performed in an edge handler instead of
delegated. `tests/test_layering.py` fails the unit tier on `IWriteSessionStore` named anywhere other than
`foundation/operator_sessions/` (the Protocol's own package) and the composition roots — `login`/`logout` take the
`SessionService` application service instead, never the raw seam.

**Do.** `blizzard/src/blizzard/hub/api/queue.py` stays read-only over the store and delegates its writes to the queue
domain services, which hold the write chunk repository.

**Don't.** An API route that constructs a chunk and saves it through a write repository.

## Domain operations take objects (`bzh:domain-takes-objects`)

**Rule.** Domain operations receive already-loaded, typed domain objects, never raw identifiers; resolving an identifier
to its object is an edge concern, done before the domain is invoked.

**Why.** A domain that takes objects cannot fail on a missing or malformed id mid-rule, and its signatures state exactly
which entities a rule operates on.

**Exception.** A parameter that resolves not to the entity the operation is about, but to a guard the domain must itself
evaluate as part of its own business rule. `ClaimService.claim`'s `runner_id: str` resolves a paused-runner denial check
inline — a claim-denial rule that belongs in the domain, not at the edge — so it stays a raw id, reasoned and registered
at its own site with `# ast-grep-ignore: bzh:domain-takes-objects`.

**Scope.** A layer that holds no entity type for the identifier at all — the runner's chunk-keyed operations, where no
`Chunk` type exists locally (`bzh:facts-not-status` keeps each per-concept table independent) — still resolves at the
edge: it mints a typed scope naming exactly the facts the rule reads, rather than loading an aggregate that does not
exist. The scope is data, not behavior, and never grows into one.

**Detect.** A domain signature typed `chunk_id: str` rather than `chunk: Chunk`, or a domain method loading an entity
from an id it was passed.

**Do.** `blizzard/src/blizzard/hub/domain/operations/complete.py` declares `complete(self, chunk: Chunk, *, by: str)`;
the controller resolves that chunk through a read repository first. Where no aggregate exists,
`blizzard/src/blizzard/runner/api/chunk_scope.py` mints the typed scope instead — `TakeoverService.open` takes a
`TakeoverOpenScope` resolved there, never a bare `chunk_id`.

**Don't.** `advance(chunk_id: str)`, loading the chunk inside the domain.

`bzh:domain-takes-objects` is tooled by `blizzard:structural-gate`'s ast-grep scan
([`../verification/blizzard.md`](../verification/blizzard.md)), scoped to `hub/domain/` and the runner's domain core
(`bzh:domain-core`): one glob per top-level `bzh:domain-package-layers` runner node, with `**/internal/**` ignored.
`blizzard/tests/test_layering.py` holds those globs equal to the runner layer table, so a new node is in scope with no
edit to the rule.

## Reconstitute in bulk (`bzh:bulk-reconstitution`)

**Rule.** A read seam that reconstitutes domain objects declares a plural counterpart keyed by a caller-supplied id set
beside its singular getter, and a caller holding a set of ids calls that counterpart once instead of the singular form
per id. Every plural answers in a bounded number of queries per id batch and drops an id that does not resolve rather
than raising. A *wide* plural returns exactly what calling the singular form for each id would; a *narrowed* one returns
that restricted to the families it reads, and names that set at the seam so a caller can check its own reaches against
it.

**Why.** `bzh:facts-not-status` makes reconstituting one object cost a fact load and `bzh:domain-takes-objects` puts
that load at the edge before any domain call, so a seam offering only one id and every id leaves a caller holding a
subset with nothing but a fan-out: the bulk strategy has to exist at the seam before a call site can choose it.

**Scope.** This binds seams that reconstitute — a read returning an entity, an aggregate, or a fact projection keyed by
id. A read already set-shaped (a list or page over a filter) and a scalar probe (a count, an existence check) are
outside it, because neither is something a caller iterates ids over. A narrowed plural is the better form wherever the
wide projection's remaining families are dead weight to the caller, but it is never a drop-in for the wide one:
substituting it is safe only where the consumer's reaches sit inside the set it names.

**Detect.** A singular getter called inside a loop, a comprehension, or a per-item resolver; a read Protocol whose only
reads are one id and every id, with nothing keyed by a set between them; a plural form building one unbatched `IN (...)`
over a caller-supplied list, which trades the fan-out for the driver's bind-parameter ceiling; a narrowed plural
substituted for the wide one at a call site whose consumer reaches outside the set the narrowed form names; a plural
form made from a singular newest-fact read by dropping its `LIMIT 1`, which `bzh:newest-per-key-read` judges.

**Do.** `blizzard/src/blizzard/hub/domain/chunk/ports/facts.py`'s `IReadChunkFactsRepository` pairs `load_facts` with
the *wide* plural `load_facts_for`, which returns exactly what calling `load_facts` per id would; `status_facts_for` is
the *narrowed* sibling, reading only the fact families a `ChunkStatusView` reaches and naming that set in its own
docstring rather than every family `load_facts_for` loads. `blizzard/src/blizzard/hub/store/internal/finding_store.py`'s
`FindingStore.get_many` batches both its row read and its `_facts_for_many` facts read through
`blizzard/src/blizzard/foundation/store/batching.py`'s shared `id_batches`.

**Don't.** `{chunk_id: self._facts.load_facts(chunk_id) for chunk_id in chunk_ids}` — and its seam-level cause, a
Protocol declaring no `load_facts_for` for that comprehension to collapse into.

**See also.** [`./system-shape/store-facts.md`](./system-shape/store-facts.md) `bzh:facts-not-status` and
`bzh:domain-takes-objects` above — together the reason reconstitution is expensive enough to need a plural form.
[`../standards/persistence.md`](../standards/persistence.md) `bzh:sql-portable` — the surface a plural form's batched
`IN` stays inside. [`./system-shape/seam-size.md`](./system-shape/seam-size.md) `bzh:seam-size-ceiling` — a narrowed
plural is preferred partly because it lets a seam split along consumer lines rather than widening one seam toward the
cap. `blizzard/tests/support.py`'s `count_queries` is how a call site's statement count is held flat as the fleet grows.
`bzh:page-bounded-read` below — the reads this rule leaves alone, and the bound they owe instead.
`bzh:newest-per-key-read` below — the row bound a plural form owes when the singular it batches reads a newest fact.
`bzh:probe-gated-pass` below — whether a periodic pass runs at all, which this rule takes as given.

## Bound a read by its page (`bzh:page-bounded-read`)

**Rule.** A set-shaped read's cost is set by the page its caller asks for — an endpoint's `limit`, a drain's batch — not
by fleet size: its statement count is flat as the fleet grows, and its row volume is bounded by the page. A fleet-sized
read behind a paged caller is allowed only where the call site states, beside the call or in the handler's docstring,
why the page's own ids cannot bound it.

**Why.** A set-shaped read sits on a path that repeats forever — the board polls its endpoints, the runner drains every
tick — so a read whose cost tracks the fleet turns every chunk ever minted into a per-call tax, and a small page hides
that tax behind a small response. A stated reason is what lets a reviewer tell a fleet read the render needs from one
nobody has questioned.

**Scope.** This binds set-shaped reads — a list or page over a filter, and whatever answers from one: an HTTP read
endpoint, or a runner tick step draining an outbound buffer — which is exactly what `bzh:bulk-reconstitution` leaves
alone. A singular read is outside it: its statement count is judged against its own need by reading, not by this rule. A
periodic pass's corpus read is outside it too: the pass has no page to bound it by, and whether that read runs at all is
`bzh:probe-gated-pass`'s concern. This rule bounds how many keys a read reaches, not how many rows it reads per key: a
read inside the page that fetches each key's whole fact history to answer with the newest fact is
`bzh:newest-per-key-read`'s.

**Detect.** Statement count is measured, not read: `blizzard/tests/support.py`'s `count_queries` at two fixture sizes,
as `blizzard/tests/test_list_chunks_bulk_reads.py` and `blizzard/tests/test_matched_queue_peek.py` do, and a count that
grows between the sizes is the finding. Row volume is judged by reading: a `list_all()` or `load_all_*` call in a
handler, a page sliced in Python from an every-id read, or a per-request fan-out whose row count no `limit` bounds, with
no reason beside it or in the handler's docstring stating why the page's ids would not do; a drain that calls a
`limit`-accepting store read with no `limit`. The fix is the page's own ids through `bzh:bulk-reconstitution`'s plural
form, a `limit` on the drain, or the reason written at the site.

**Do.** `blizzard/src/blizzard/hub/api/chunks.py`'s `list_chunks` is keyset-paged and its statement count is flat across
fixture sizes; its `load_all_facts()` and `record.list_all()` fleet reads carry their reason — in the handler's
docstring and in the comment beside `list_all()` — that a pointer this page renders can be held live by a chunk outside
it.

**Don't.** A handler that takes `limit` and `cursor`, calls `record.list_all()`, slices the page out of the result, and
loads each page row's facts through the singular getter — bounded in rows returned, fleet-sized in rows read, and
growing in statements per page row.

**See also.** `bzh:bulk-reconstitution` above — the plural form that lets a read stop at the page's ids, and the seam
rule for the per-item reads this rule's measurement exposes. `bzh:newest-per-key-read` below — the row bound per key,
which a page-sized key set does not supply. [`../verification/blizzard.md`](../verification/blizzard.md)
`blizzard:component-test` — the tier the two-fixture-size count lives in.

## Read the live set on a hot path (`bzh:live-set-read`)

**Rule.** A read on a path that repeats forever — a runner tick, a board or runner poll — whose consumer needs only
non-terminal chunks excludes terminal chunks in the store query, by a prefilter over terminal facts, before loading or
deriving anything per chunk. The prefilter is sound, not exact: it may keep a terminal chunk for the derivation to drop,
and never drops a chunk the derivation would call non-terminal. Its cost floor is one indexed probe per `chunks` row;
removing that floor needs a persisted terminal marker, which `bzh:facts-not-status` forbids.

**Why.** Terminal is absorbing and retention keeps a finished chunk's facts forever, so a read that derives every chunk
and then discards the terminal ones charges each finished chunk to every future call. The cost of a hot read should
track the live fleet, not the deployment's age.

**Scope.** A read that renders terminal chunks stays `bzh:page-bounded-read`'s. A terminal status a live chunk needs,
such as a done prerequisite, is resolved by id through `bzh:bulk-reconstitution`'s plural form, not by widening the live
read. A periodic pass's corpus read stays `bzh:probe-gated-pass`'s.

**Detect.** Measured: `blizzard/tests/test_live_set_read.py` builds two fixtures that differ only in terminal-chunk
count and asserts `count_queries` and `count_rows_read` from `blizzard/tests/support.py` are flat and the response
identical. By reading: a `TERMINAL_STATUSES` filter applied in Python to an every-chunk status read on such a path.

**Do.** `ChunkFactsStore.load_live_statuses` excludes stopped, completed, PR-closed, and newest-movement-is-done chunks
in its query; the queue reads bound their position and record lookups by the live candidates it names.

**Don't.** Read every chunk's statuses and drop the terminal ones in Python.

**See also.** `domain/work/statuses.md` — terminal chunks never un-stop or un-complete, and restart refuses a terminal
chunk, which is what makes the exclusion sound.

## Read the newest fact per key (`bzh:newest-per-key-read`)

**Rule.** Select only the newest fact per key in the store query when a read answers with the newest fact for each of a
set of keys: the rows it reads are bounded by the key count and stay flat as each key's fact history deepens. A plural
form batching a singular newest read keeps that bound — the singular's `ORDER BY id DESC LIMIT 1` becomes a group-by-max
join, never the same select with the `LIMIT` dropped and the newest row picked in Python.

**Why.** Fact tables are append-only and keep every superseded fact (`bzh:facts-not-status`), so a newest read that
fetches the history charges every past write on a key to every future call, behind a statement count that stays flat. A
`LIMIT 1` cannot span keys, so batching loses the singular form's bound unless the query restates it per key.

**Scope.** This binds a read whose consumer uses only the newest fact per key, whether the keys are a caller-supplied
set or every key a filter leaves, the whole table included. A read whose consumer derives from more than the newest fact
— a fact projection reconstituted for the domain to derive from — is outside it: the history is that read's answer.

**Detect.** Measured: `blizzard/tests/support.py`'s `count_rows_read` over the same keys at two history depths, as
`blizzard/tests/test_newest_fact_reads.py` does — a row count above the key count, or one that grows with the depth, is
the finding, and a statement count cannot show it. By reading: a select ordered ascending by `id` with no `limit`, whose
rows a loop folds into a dict keyed by the key column so that later rows overwrite earlier ones; a comment excusing that
fold as newest-fact-wins; a `[-1]` or `[0]` taken from a whole-history select fetched for nothing else. The fix is the
group-by-max join, batched through `id_batches` when the keys are caller-supplied.

**Do.** `blizzard/src/blizzard/hub/store/internal/newest_fact.py`'s `newest_fact_select` joins a fact table to a
`max(id) ... GROUP BY key` subquery over the keys asked for, and the stores' plural newest reads share it.
`blizzard/src/blizzard/hub/store/internal/finding_store.py`'s `FindingStore.newest_by_scope_for_routine` is the same
join over every scope one routine has run against — the keys a `where` on the routine name leaves, not a supplied set.

**Don't.**

```python
rows = conn.execute(select(facts.c.key, facts.c.retired).order_by(facts.c.id)).all()
newest: dict[str, bool] = {}
for row in rows:
    newest[row.key] = row.retired  # ascending id order overwrites
```

**See also.** `bzh:bulk-reconstitution` above — the plural form this bound has to survive. `bzh:page-bounded-read` and
`bzh:live-set-read` above — they bound which keys a read reaches; this rule bounds the rows read per key.
[`../standards/persistence.md`](../standards/persistence.md) `bzh:sql-portable` — the group-by-max join stays inside the
portable surface, and its ordering clause governs a read that does index into a history.
[`../verification/blizzard.md`](../verification/blizzard.md) `blizzard:component-test` — the tier the two-depth row
count lives in.

## A probe-gated pass (`bzh:probe-gated-pass`)

**Rule.** A periodic pass converging a corpus toward a derived state checks a cheap change probe — a watermark, a
cursor, a signature — before it rescans its corpus, skips the rescan when the probe matches the previous pass's value,
and forces a full pass once a bounded floor has elapsed since the last one, so a missed signal can never become a
permanent skip. A periodic pass that prunes or expires what has aged past a window far longer than the floor instead
runs on the floor alone, with no probe.

**Why.** A reconciler runs forever at a fixed interval while the corpus it converges changes rarely, so an unprobed pass
pays the full rescan on every tick for a result the previous tick already produced. The floor is what makes the skip
safe: a probe that misses a change costs one floor's latency rather than correctness, and a pruning pass run on the
floor alone keeps aged rows at most one floor past its window.

**Scope.** This binds the pass itself — a periodic `sweep()` or tick step `run()` body, hub or runner alike — not the
`Sweep` driver in `blizzard/src/blizzard/hub/app.py`, which owns cadence and jitter and steps the pass as a black box. A
fixed cadence where a change signal would do is judged here, at the pass: the probe is what makes a fixed interval
cheap, so the answer to it is a gated pass, not a re-timed driver. A per-item resolution inside the pass is
`bzh:bulk-reconstitution`'s, not this rule's. Each pass shape owes:

| Shape                                                                                                                                                                | Example                                                                                                                                      | Owes                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rescans a corpus to converge a derived state from it                                                                                                                 | The hub's annotation and event-derivation reconcilers                                                                                        | A probe and a floor                                                                                                                                                                                           |
| Prunes or expires what has aged past a window far longer than its floor                                                                                              | The runner's `Retention` step in `blizzard/src/blizzard/runner/loop/steps.py`, pruning its day-scale lanes on a one-hour floor               | A floor, not a probe                                                                                                                                                                                          |
| Enforces a window without pruning it                                                                                                                                 | The runner's `SpendCeiling` step, which engages the pause brake once rolling-window spend reaches its cap                                    | Nothing here — it is outside this rule: it owes its reaction on the tick the cap is crossed, and a floor would let spend overshoot the cap for up to one floor                                                |
| Acts on work as it comes due — reaping a lease, advancing or filling, draining a queue or buffer, retrying an intent whose backoff has elapsed, sampling live leases | `CloseIntentDrainer.sweep` in `blizzard/src/blizzard/hub/domain/work_items/closure.py`; the runner's `Reap` and `Advance` steps              | Nothing here — it is outside this rule: its due-set is the live work the pass exists to answer, often made due by time passing alone, so no change probe sees it and a floor would delay the reaction it owes |
| Opens on a read returning only its not-yet-acted-on rows and returns when that read is empty                                                                         | `WorkItemMaterializationReconciler.sweep`'s `unmaterialized_proposals()` in `blizzard/src/blizzard/hub/domain/work_items/materialization.py` | Nothing more — that read is its probe, and it owes no floor, since it reads the pending rows themselves rather than a signal about them                                                                       |

**Detect.** A converging pass whose first statement is its full-corpus read, with no value compared against the previous
pass's; a pass whose skip has no floor behind it, so a probe that lies once skips forever; a tick step that prunes a
day-scale window unconditionally every tick. The fix is a probe seam on the store — a max-watermark or a signature query
answering in one statement — compared against the value the pass last converged on, plus a recorded last-full-pass
instant checked against the floor; for a pruning pass, the recorded instant and the floor alone.

**Do.** `blizzard/src/blizzard/hub/domain/observability/analytics/derivation.py`'s `EventDerivationReconciler.sweep`
reads `derivation_signature()` first, returns when it matches the last converged signature and the ten-minute floor is
not due, and otherwise runs the full pass and records both the signature and the instant. An unchanged pass costs the
probe's one statement.

**Don't.** A converging `sweep()` that reads its whole corpus and every remote's state unconditionally on each pass, so
an idle fleet pays the whole diff every interval, changed or not.

**See also.** [`./crash-correctness.md`](./crash-correctness.md) `bzh:steppable-loop` — the pass this rule gates is one
of its step functions — and `bzh:injected-clock` there, whose clock the floor reads. `bzh:bulk-reconstitution` above —
what the pass owes per item once it does run. [`./crash-correctness/lanes.md`](./crash-correctness/lanes.md)
`bzh:lane-contract` — what a periodic pass owes around its body: its bound, failure shape, and isolation.
