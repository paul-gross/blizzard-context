# A flag hides behavior, never contract (`bzh:flag-hides-behavior`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

A feature flag changes what the software does with a surface, never whether the surface exists: surface a release
carries is held to `docs/versioning.md` whether or not its flag is on, and each surface kind answers an off flag the one
way the table below gives.

## Why

Every compatibility check compares the surface a release carries and reads no flag. Surface skipped while its flag is
off could be reshaped after it had shipped, and an operator holding a client written against the off route would find it
broken the morning the flag turned on.

## Detect

A flag-guarded surface that is missing while its flag is off: a route that is unregistered or absent from the OpenAPI
document, a field or key that is undeclared, a CLI verb or option that is absent from `--help`. Also a migration
conditional on a flag, and a flag read hand-rolled inside a controller instead of through a seam below.
`tests/test_flag_registry.py` ties every guard in source to the registry file.

## Do

Each surface while its flag is off. The design record is
`blizzard-product:/plans/release-engineering/dark-launch/spec/contract.md`.

| Surface                       | While the flag is off                                                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| HTTP route, hub or runner     | Registered and in the OpenAPI document; answers `404` with a typed `FlagOff` body naming the flag, listed in the route's `responses`              |
| Request or response field     | Declared with a default; a request carrying it is accepted and the field ignored, and a response carries its default                              |
| Hub↔runner wire               | As a route or field, held additive by `bzh:fleet-wire-additive`; a runner never sends a field or calls a route its `fleet` flag has off           |
| CLI verb or option            | Present in `--help`, marked not yet on; running it, or giving the option, exits 1 with the `FlagOff` message                                      |
| Configuration key             | Accepted and validated like any key; read as absent, with a warning naming the key and the flag; held additive by `bzh:released-surface-additive` |
| Store schema                  | Migrated by every release that carries the revision; a migration is never conditional on a flag                                                   |
| Trace and egress dictionaries | Declared when the change that emits them lands; emitted, or non-null, only while on; held additive by `bzh:released-surface-additive`             |
| Fact kind, event type         | Declared when it lands; written only while on, and read by any reader whatever its own flag                                                       |
| Board screen or control       | Absent; the board is behavior, not surface                                                                                                        |

The seams that do it, so a change declares a guard and never writes one:

- **Route** — `flag_guard("name")` in `blizzard/src/blizzard/hub/api/flag_guard.py` or
  `blizzard/src/blizzard/runner/api/flag_guard.py`, spread into the route's keyword arguments; it adds the dependency
  and the `404` entry, and the app's one handler serves the `FlagOff` body from `wire/flags.py`.
- **Field** — `Annotated[T, FlagGuarded("name")]` on a wire-model field with a default, and `without_off_fields` applied
  to a request at entry and a response before it returns (`blizzard/src/blizzard/foundation/flags/guard.py`).
- **CLI** — `hub_flag_command` / `hub_flag_option` in `blizzard/src/blizzard/hub/cli/flag_gate.py`, or
  `runner_flag_command` / `runner_flag_option` in `blizzard/src/blizzard/runner/cli/flag_gate.py`.
- **Configuration key** — `flag="name"` on the key's `ConfigKey` declaration; a hub key takes a `hub` or `fleet` flag, a
  host key a `runner` flag.

## Don't

```python
@router.get("/chunks/{chunk}/forecast")
def forecast(request: Request) -> Forecast:
    if not request.app.state.flags.on("forecast"):
        raise HTTPException(status_code=404)  # an untyped 404 the client cannot tell from "not found"
```

Nor leave the route unregistered while the flag is off, or write a migration that runs only when a flag is on.

## See also

- `bzh:released-surface-additive` in
  [../architecture/system-shape/released-surfaces.md](../architecture/system-shape/released-surfaces.md) — what a
  configuration key, store schema, trace, or egress change stays on once released.
- `bzh:fleet-wire-additive` in [../architecture/system-shape/fleet-wire.md](../architecture/system-shape/fleet-wire.md)
  — the hub↔runner wire a flagged route or field stays additive on.
- `bzh:help-states-effect` in [./help-text.md](./help-text.md) — the wording of a marker in `--help`.
