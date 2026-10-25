# Judging whether a change breaks a supported release (`bzh:judging-a-break`)

**Rule.** Told to judge whether a change breaks a supported release, run `uv run blizzard-compat --json` in the
`blizzard` worktree on the change and decide each finding in this order. The rules applied are
`bzh:released-surface-additive`
([../architecture/system-shape/released-surfaces.md](../architecture/system-shape/released-surfaces.md)) and
`bzh:store-expand-contract` ([../standards/persistence.md](../standards/persistence.md)); this procedure restates
neither.

**Why.** A finding is a claim about a committed document, and a document can be wrong; the choice that matters is
whether the surface can stay, which no tool decides.

## Steps

1. **Is the finding real?** Regenerate the contract documents (`mise run export-openapi`, `mise run export-contracts`)
   and run again. A finding that disappears was a document the change forgot to regenerate.
2. **Can the old surface stay beside its replacement?** That is always preferred, and it makes the finding additive.
3. **If not, does the window allow the break now?** It does when the surface is deprecated in every supported release
   and `floor` can be raised to a line that deprecates it; or, on a `master` whose window carries `opening`, when the
   change declares it with a `!` commit and a breaking change note. `docs/versioning.md` and `blizzard:compat`
   ([../verification/blizzard.md](../verification/blizzard.md)) own the window and the admission.
4. **If not, do that release's consumers already survive it?** Read the release's own tree, not `master`'s: every
   consumer of the surface it ships — the runner, its CLI, the panel, the board — and what each does with the change. A
   consumer survives when it handles the change without failing. One that fails until reloaded, and whose reload loads
   the new release's client, survives after a reload. One that fails and that a reload does not fix does not survive.
   When every one survives, the finding takes an allowance in `contracts/compat/allowances.toml`, whose README owns the
   entry and when it applies.
5. **Otherwise** the change deprecates the surface and leaves the removal to a later change.

## Verdicts

Report one per finding:

- **Additive.** The change keeps both forms; nothing more is owed.
- **An allowed break.** Name the `floor` the change raises or the note it declares, and the `!` its commit needs.
- **An allowance.** Name the release's line, the exact finding, and the `because`: each of that release's consumers, the
  file and line where it reads the surface, and why it survives. A consumer left unread is named as such, and so is one
  that survives only after a reload, which may be admitted. A consumer that fails and that a reload does not fix is no
  allowance.
- **A break that waits.** Name the deprecation that starts its clock.

## Don't

- Treat a finding as real without regenerating the contract documents and rerunning the check.
- Raise `floor` or record an allowance while the old surface can stay beside its replacement.
- Judge a release's consumers from `master` instead of from that release's own tree.
- Admit an allowance for a consumer that fails even after reloading its client.
