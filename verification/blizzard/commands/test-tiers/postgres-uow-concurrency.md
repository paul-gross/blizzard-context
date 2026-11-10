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
production tenant guard. Database lock and statement timeouts and a process deadline make stalled writers fail. Scratch
tables contain only the guard and locking columns; this is not a migration, teardown-race, or delete-atomicity test.
