# Landing, turning on, and retiring a flag (`bzh:flags-procedure`)

**Rule.** Told to land work behind a flag, turn a flag on, or retire one, run the part of this procedure that names it.
The rules applied are `bzh:flag-hides-behavior`
([../standards/flag-hides-behavior.md](../standards/flag-hides-behavior.md)) and the lifecycle contract
(`blizzard-product:/plans/release-engineering/dark-launch/spec/lifecycle.md`); the registry's fields and scopes are
`blizzard-product:/plans/release-engineering/dark-launch/spec/registry.md`, how a process resolves a flag is
`.../spec/reading.md`. This procedure restates none of them.

**Why.** A flag's age is read from the releases, so the one thing an author must get right is the shape of each change;
the check then says when the next one is owed.

## Landing work behind a flag

1. **Is there a flag already?** Read `src/blizzard/foundation/flags/registry.toml` in `blizzard`. Work belonging to the
   same capability joins the live flag of its epic; a new capability declares a new one.
2. **Choose the scope** — `hub`, `runner`, or `fleet` — by who must agree on the behavior (`registry.md` §Scopes). Split
   behavior is one `fleet` flag, never two.
3. **Declare it** under `[flag.<name>]` with `owner`, `summary`, `scope`, and `default = "off"`. A flag is never created
   on.
4. **Guard the behavior and only the behavior**: each surface through the seam `bzh:flag-hides-behavior` names,
   answering as its table says while off; a board screen or control through the board's flag store and route guard.
   Never guard a migration, and never leave surface unregistered.
5. **Prove the on path**: tests that build their `Flags` with the flag on, living with the change, beside the off-path
   tests the default gate already runs (`lifecycle.md` §Testing both sides).
6. **Prove it** with `uv run pytest tests/test_flag_registry.py` and `mise run flag-lifecycle`
   (`blizzard:flag-lifecycle`, [../verification/blizzard.md](../verification/blizzard.md)), then `blizzard:compat`.

## Turning a flag on

1. **Is it time?** The capability is complete on the on path, and no stable release has promised the flag off.
2. **Make the one change**: the registry's `default` set to `on`, and the change note naming the flag, written under
   `bzh:change-notes` ([change-notes.md](./change-notes.md)). Neither goes alone.
3. **Keep every off-path test** until the flag retires; move the on-path tests onto the default path unchanged.
4. **Prove it** with `mise run flag-lifecycle` on the pull request, which fails a flip with no note naming the flag, and
   by running the suite: the on path is now the gate's, since the gate runs every flag at its registry default.

## Retiring a flag

1. **Is it due?** `mise run flag-lifecycle` lists the flag as due: a stable release later than the one that turned it on
   has shipped with it still live.
2. **Collapse every branch to its on side**: each `flags.on(name)` read, each `FlagOff` answer for the flag, the board's
   guard and markers, and the off-path tests. What the flag guarded stays exactly as it was released.
3. **Move the name** from `[flag.<name>]` to `[retired]`, keeping its scope. Never reuse the name. A retirement owes no
   change note.
4. **Prove it** with `uv run pytest tests/test_flag_registry.py` (no code names the flag, the file holds no unread live
   flag) and `mise run flag-lifecycle` (`cut` mode fails a due flag still live, and a tombstone removed too early).
