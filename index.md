# blizzard-context

Blizzard's conventions harness — the rules every piece of blizzard code and every blizzard agent context is held to.

## Domains

| Domain                                                                 | When to read                                                                                                                                                                          |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [domain/](./domain/index.md)                                           | Establishing or asserting correctness of behavior — planning against what blizzard's concepts are and how they behave, or verifying work against that model, with no technical detail |
| [architecture/](./architecture/index.md)                               | Planning a change to blizzard's structure, or reviewing a plan against the structural invariants it must honor                                                                        |
| [standards/](./standards/index.md)                                     | Writing or reviewing finished code, in any language or on any surface, against the quality rules a change is held to                                                                  |
| [verification/](./verification/index.md)                               | Planning how a change to **blizzard** will be proven, or verifying one — blizzard's verifiability matrix                                                                              |
| [workflows/](./workflows/index.md)                                     | Reasoning about how work reaches `master` — feature delivery is blizzard-orchestrated, not agent-driven — or carrying out the release cut                                             |
| [tooling/](./tooling/index.md)                                         | Driving an external tool beyond the winter CLI                                                                                                                                        |
| [garden/](./garden/index.md)                                           | Declaring or resolving a gardening axis — the named axes blizzard is recurringly evaluated along, and what each judges by                                                             |
| [exemplars/python/repo_pattern.py](./exemplars/python/repo_pattern.py) | Building a repository — the reference shape for the Protocol-seam + internal-adapter + injected-error pattern the architecture rules require                                          |
| [CONTRIBUTING.md](./CONTRIBUTING.md)                                   | Committing to this repo, or authoring or reshaping a rule here                                                                                                                        |
| [verifiability.md](./verifiability.md)                                 | Verifying a change to **this repo** itself — the declared verification methods and their ids                                                                                          |
