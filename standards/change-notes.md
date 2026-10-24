# Change notes

The rules for the notes a change commits beside itself, which `blizzard` assembles into a release's published body. The
format — where a note lives, its fields, its id, its headings — is `blizzard`'s `changes/README.md`; the rules here own
the judgement. Each rule in this tree follows the slot skeleton owned by `winter-canon:/rule-shape.md`
(`canon:rule-shape`) and carries a stable `bzh:<slug>` id. The procedure that applies them in order is
[../workflows/change-notes.md](../workflows/change-notes.md).

Parent: [./index.md](./index.md).

| Spoke                                                     | When to read                                                                              |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [change-note.md](./change-notes/change-note.md)           | Deciding whether a change owes a note, or writing or reviewing a note's body              |
| [upgrade-note.md](./change-notes/upgrade-note.md)         | A change asks something of the operator — a key to set, an order to upgrade in, a command |
| [deprecation-note.md](./change-notes/deprecation-note.md) | Deprecating a surface, postponing its removal, or removing one                            |
