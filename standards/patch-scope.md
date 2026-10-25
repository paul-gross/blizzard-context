# A patch carries the fix and nothing else (`bzh:patch-scope`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

A change carried onto `release/X.Y` after its cut holds the fix, the tests that prove it, and its change note, and
nothing else: no route, field, configuration key, span, event, or egress column; no flag turned on; no store revision.
This binds a patch, a further candidate's fixes, and a `Line-only:` fix alike. The cut commit is exempt; the cut owns
it.

## Why

A revision on a branch sits at a different place in the store's chain than the same revision on `master`, so a store the
patch migrated would skip whatever `master` added between them on its next upgrade. New surface and a turned-on flag
change what an operator who pinned the line relies on, and a pin on a patch is a promise that nothing but the fix moved.

## Detect

On a pull request into `release/**`: a diff touching `openapi/`, `contracts/`, a store's `versions/` directory, or a
flag's default in `src/blizzard/foundation/flags/registry.toml`; and a commit that is not a fix, its test, or its note.
`blizzard:compat --line` catches only a break, and `line-provenance` only a commit that is no cherry-pick, `Line-only:`
commit, or cut commit; no gate refuses additive surface on a line, so a review asserts it.

## Do

Carry the fix alone. When it needs stored data corrected, carry that as an idempotent repair the daemon applies at
start, or as a CLI verb the operator runs. Neither is a revision, so neither conflicts with `bzh:manual-migrations`.
When the fix needs new surface or a revision, it rides the next train from `master` instead.

## Don't

```text
fix(hub): stop losing the claim on retry     # the fix
feat(hub): add GET /api/chunks/{id}/claims   # new route on a line
chore(store): add claims.attempt column      # a store revision on a line
```

Only the first belongs on the branch.

## See also

- `bzh:manual-migrations` in [./persistence.md](./persistence.md) — why a repair is not a revision.
- `bzh:released-surface-additive` in
  [../architecture/system-shape/released-surfaces.md](../architecture/system-shape/released-surfaces.md) — the surface a
  release holds.
- `bzh:flag-hides-behavior` in [./flag-hides-behavior.md](./flag-hides-behavior.md) — flags a patch leaves as they are.
- `bzh:change-note` in [./change-notes/change-note.md](./change-notes/change-note.md) — the note a patch carries.
