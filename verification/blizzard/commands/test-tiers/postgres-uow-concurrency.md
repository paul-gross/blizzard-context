# `blizzard:postgres-uow-concurrency` detail

<!-- rumdl-disable MD001 -->

The focused Postgres concurrency proof spoke of [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the command inventory.

### blizzard:postgres-uow-concurrency

`uv run --extra postgres python scripts/check_hub_uow_postgres.py` includes the optional Postgres driver and requires
`BLIZZARD_UOW_POSTGRES_URL` naming a Postgres server whose user may create and drop databases. The command creates and
force-drops a uniquely named scratch database through `tests/rehearsal/stores.py`; do not point it at a server on which
that privilege is inappropriate. Missing prerequisites fail, never skip.

Two independent database connections request the same chunk rows in opposite order, then the same keyed locks in
opposite order. A test-only tenant-open guard allows concurrent writers; the proof observes the second backend blocked
by the first at the decision lock and checks both complete in canonical order. A separate run checks contention with the
production tenant guard. Scratch tables on this first database contain only the guard and locking columns.

The decision-lock cases include disjoint dependency declarations and declare, group, delete, and release pairings in
both relevant orders. They prove the shared dependency key contends even when chunk rows are disjoint; a production
tenant-guard run also covers group against release. These lock-set proofs do not execute the domain operations.

A second scratch database is migrated to the head revision, so foreign keys are enforced and the production teardown and
guard are the code under test. Cases run on it, each reporting `PASS` or `FAIL` and failing the run if any fails:

- **Egress cursor authority**: a pass followed by a reset, and two queued resets, use independent connections. The
  waiting reset captures the committed predecessor; a stale pass append is refused without moving the cursor.
- **The closed-tenant check**, in both orders: a write holds its tenant's row while a close waits (the write commits,
  then the close closes), and a close holds it while a write waits (the write refuses `TenantClosed` and leaves no row).
- **Two closes of the last two open tenants**: exactly one commits and the other refuses `LastTenant`.
- **The drain under foreign keys**: a tenant seeded, from the schema, with a row in every table of `DRAIN_ORDER` drains
  and completes with no foreign-key failure, and every table it owned is empty. A table added later seeds itself; one
  that cannot is named and fails the case.
- **Keyed locks of different keys**: with a guard that takes no tenant-row lock, two units of one tenant declaring
  different keys do not wait on each other.

Database lock and statement timeouts and a process deadline make stalled writers fail. This is not a migration-history
test; the migration only builds the schema.

Run by hand as above, and nightly and on demand by `.github/workflows/postgres-uow-concurrency.yml`, which supplies a
`postgres:16` service as `BLIZZARD_UOW_POSTGRES_URL`; it never runs on a pull request or a `master` push.
