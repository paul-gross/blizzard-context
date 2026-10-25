# Writing a change note (`bzh:change-notes`)

**Rule.** Told to make any change in `blizzard`, decide whether it owes a change note and, when it does, write it in
this order. The facts each step acts on stay with their owners: the judgement and the body with `bzh:change-note`
([../standards/change-notes/change-note.md](../standards/change-notes/change-note.md)), the upgrade section with
`bzh:upgrade-note` ([../standards/change-notes/upgrade-note.md](../standards/change-notes/upgrade-note.md)), the
deprecation and removal fields with `bzh:deprecation-note`
([../standards/change-notes/deprecation-note.md](../standards/change-notes/deprecation-note.md)), and the file's
location, id, fields, and headings with `blizzard`'s `changes/README.md`. This procedure restates none of them.

**Why.** A note is written only if the worker making the change knows it owes one, and the release body is assembled
from the notes alone.

## Steps

1. **Does the change owe a note?** Apply `bzh:change-note`. A change an operator would not notice writes nothing; stop.
   One that touches a watched contract document (`blizzard:change-notes`) still carries the
   `Change-Note: none — <reason>` trailer on a commit, or the gate fails it.
2. **Choose the id** — `changes/README.md` §The id — unique across the whole of `changes/`.
3. **Set the kind and fields** — `changes/README.md` §Frontmatter: the kind, the surfaces it touches, and `flag` when
   the change ships behind one.
4. **Write the body** under `bzh:change-note`, in the operator's vocabulary.
5. **A break or a removal:** write the `## Upgrade` section under `bzh:upgrade-note`, set `breaking` and `breaks`, and
   mark the commit subject with the `!`.
6. **An operator-facing step of any kind** — a key to set, an order to restart in, a command to run: write it as the
   `## Upgrade` section under `bzh:upgrade-note`, even when the work item's `## Landing and deployment` also names it.
7. **A crossing that needs more than a paragraph:** add a boundary section under `## Upgrading to the next release` in
   `docs/upgrade.md` and set `upgrade-guide` to its anchor.
8. **A deprecation or a removal:** name the removal line in `removes-in`, or the deprecation the removal `retires`,
   under `bzh:deprecation-note`; a moved date is a `postpones` note.
9. **Prove it** with `blizzard:change-notes` ([../verification/blizzard.md](../verification/blizzard.md)).
