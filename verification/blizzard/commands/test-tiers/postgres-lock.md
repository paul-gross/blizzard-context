# PostgreSQL lock proof

## Command

### blizzard:postgres-lock-test

Run `mise run postgres-lock-test` in blizzard with `BLIZZARD_LOCK_TEST_PG_URL` naming an invocation-owned local
PostgreSQL server with database create and drop privileges. Each session migrates a uniquely named template to head,
clones it into an isolated database per test, and drops both clones and template afterwards. It fails on missing
configuration, a non-PostgreSQL or non-loopback URL, or setup failure. The tenant and runner statement guards remain
enabled. Default SQLite collection does not collect this opt-in suite.

The admission baseline checks that a scoped writer waits behind another scoped writer using separate connections and
PostgreSQL's blocker relationship, then completes after release. The suite also exercises decision locks; it does not
establish shared admission or general PostgreSQL backend correctness. The independent `upper-tiers` CI job runs the same
command against PostgreSQL 16.

For a disposable local server, run the following from the blizzard root. The trap removes only the container this
invocation created, including on failure. The port is allocated on loopback by Docker.

```bash
id=$(docker run -d --rm -e POSTGRES_PASSWORD=postgres -p 127.0.0.1::5432 postgres:16)
trap 'docker rm -f "$id" >/dev/null' EXIT
ready=0
for i in {1..60}; do
  if docker exec "$id" pg_isready -h 127.0.0.1 -U postgres >/dev/null 2>&1; then ready=1; break; fi
  sleep 1
done
test "$ready" = 1 || { printf 'PostgreSQL readiness deadline exceeded\n' >&2; exit 1; }
port=$(docker inspect --format '{{(index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' "$id")
BLIZZARD_LOCK_TEST_PG_URL="postgresql://postgres:postgres@127.0.0.1:$port/postgres" mise run postgres-lock-test
```
