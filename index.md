# blizzard-context

Blizzard's conventions harness — the rules every piece of blizzard code and every blizzard agent context is held to.

## Domains

| Domain                                                                 | When to read                                                                                                                                                                          |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [domain/](./domain/index.md)                                           | Establishing or asserting correctness of behavior — planning against what blizzard's concepts are and how they behave, or verifying work against that model, with no technical detail |
| [architecture/](./architecture/index.md)                               | Planning a change to blizzard's structure, or reviewing a plan — the layering, the deterministic-shell/pluggable-seam shape, and the crash-correctness the daemons are built to honor |
| [standards/](./standards/index.md)                                     | Writing or reviewing finished code — the quality rules a change is held to, from the Python and Angular toolchains to what a value looks like on the wire                             |
| [verification/](./verification/index.md)                               | Planning how a change to **blizzard** will be proven, or verifying one — blizzard's verifiability matrix                                                                              |
| [workflows/](./workflows/index.md)                                     | Reasoning about how work reaches `master` — feature delivery is blizzard-orchestrated, not agent-driven — or carrying out the release cut                                             |
| [tooling/](./tooling/index.md)                                         | Driving an external tool beyond the winter CLI                                                                                                                                        |
| [exemplars/python/repo_pattern.py](./exemplars/python/repo_pattern.py) | Building a repository — the reference shape for the Protocol-seam + internal-adapter + injected-error pattern the architecture rules require                                          |
| [CONTRIBUTING.md](./CONTRIBUTING.md)                                   | Committing to this repo — commit format, delivery, and the pre-push expectation                                                                                                       |
| [verifiability.md](./verifiability.md)                                 | Verifying a change to **this repo** itself — the declared verification methods and their ids                                                                                          |

## Rule ids

Every rule here carries a stable `bzh:<slug>` id in its heading, per `winter-canon:/rule-shape.md`'s scheme. This repo
keeps no id registry: an id resolves by grepping the tree for its slug — a deliberate trade while the rule count stays
greppable, revisited if resolution ever misses. Adding or renaming an id updates every citation in the same change.
