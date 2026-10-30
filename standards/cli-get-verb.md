# A client verb that reads one thing is named `get` (`bzh:cli-get-verb`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

A `blizzard` client verb that reads one thing is named `get`. A group that has a `get` also accepts `show` and `read` as
hidden aliases of it: they resolve to the same command, and neither appears in `--help` or completion.

## Why

One name for one-thing reads means an operator or an agent guesses the verb correctly in every group. The aliases keep
the other spellings people reach for working, so a wrong guess still lands; hiding them keeps the listed surface to one
name per effect.

## Scope

Binds every verb in the `blizzard hub` and `blizzard runner` trees that reads a single record, sample, or artifact.
Verbs that read a collection or a facet (`list`, `history`, `work-items`, `status`) keep their own names.

## Detect

`tests/test_cli_get_verb.py`, run under `blizzard:unit-test`, walks both roots. It fails on a command registered as
`show`, `read`, `view`, `describe`, or `inspect`; on a group with a `get` that does not resolve `show` and `read` to
that same command; and on an alias listed in a group's commands or `--help`. Detection is by name, so a read-one verb
under any other name (`info`, say) is judged by reading.

## Do

```python
@click.group("routine", cls=GetGroup)
def routine_group() -> None: ...


@routine_group.command("get", cls=FleetCommand)
def routine_get(cli: CliContext, routine_id: str) -> None:
    """Print ROUTINE_ID's definition and linked scopes."""
```

## Don't

```python
@routine_group.command("show", cls=FleetCommand)
def routine_show(cli: CliContext, routine_id: str) -> None: ...
```

## See also

- `bzh:help-states-effect` in [./help-text.md](./help-text.md) — the wording of the `--help` the `get` verb renders.
