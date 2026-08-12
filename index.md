# blizzard-context

Blizzard's conventions harness — the rules every piece of blizzard code and every blizzard agent context is held to.
blizzard-context derives from **winter-canon**: the canon defines what any harness must be, and this repo is blizzard's instance of one.
It follows `winter-harness` in **style** — domain-organized convention directories, routing hubs, a verifiability matrix, and architecture guidance — while carrying **blizzard's own rules**, not winter's.
The repo is named for what it holds rather than for the concept: blizzard also drives *coding harnesses* (Claude Code, Codex, OpenCode — the adapter seam), and that seam keeps the word.

## Path notation

Files here are addressed with the `blizzard-context:` prefix — for example, `blizzard-context:/architecture/repository-access.md`.
Resolve to the on-disk path via the `# Winter Extensions` block in workspace `CLAUDE.md`; the local directory name varies (`./.winter/ext/context/`, `./blizzard-context/`, …).
The universal substrate this harness derives from is addressed with the `winter-canon:` prefix — e.g. `winter-canon:/harness-structure.md`.

## Rule ids

Every blizzard-context rule carries a stable `bzh:<slug>` id in its heading — the citation handle a plan, a review finding, or a cross-reference uses.
The `bzh:` scheme is this harness's own, parallel to the canon's `canon:<slug>` (`winter-canon:/rule-shape.md` owns the slot skeleton and the stable-id scheme both follow).
A non-rule leaf — a procedure or taxonomy file (`winter-canon:/rule-shape.md` §File kinds) — carries a file-level `bzh:<slug>` id in its title instead.
Ids are stable: citations depend on them, so renaming or removing a rule's id is a breaking change. A rule's heading is the id's single home — there is no separate id registry to keep in sync.
That stability is why `bzh:` outlived the repo's old name: the prefix is historical, not an abbreviation of `blizzard-context`, and it stays as-is because blizzard's and blizzard-mock's code cite it. New rules take `bzh:` too — a second prefix would buy nothing and break the one-home rule.

## Domains

| Domain                                                                 | When to read                                                                                                                                                                                                                |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [domain/](./domain/index.md)                                           | Establishing or asserting correctness of behavior — planning against what blizzard's concepts are and how they behave, or reviewing and verifying work against that model, with no technical detail                         |
| [architecture/](./architecture/index.md)                               | Planning a change to blizzard's structure, or reviewing a plan — the CLEAN layering, repository access, the deterministic-shell/pluggable-seam shape, and the crash-correctness requirements the daemons are built to honor |
| [standards/](./standards/index.md)                                     | Writing or reviewing finished code — the code-quality rules a change is held to, from the Python and Angular toolchains to what a value looks like on the wire                                                              |
| [verification/](./verification/index.md)                               | Planning how a change to **blizzard** will be proven, or verifying one — blizzard's verifiability matrix                                                                                                                    |
| [workflows/](./workflows/index.md)                                     | Reasoning about how work reaches `master` — feature delivery is blizzard-orchestrated, not agent-driven — or carrying out the release cut, the one deterministic sequence an agent still drives                             |
| [exemplars/python/repo_pattern.py](./exemplars/python/repo_pattern.py) | Building a repository — the reference shape for the Protocol-seam + internal-adapter + injected-error pattern the architecture rules require                                                                                |
| [tooling/](./tooling/index.md)                                         | Driving an external tool beyond the winter CLI — the repo task runner, `gh` for CI runs and issues, or the verification-scenario setup tools                                                                                |
| [CONTRIBUTING.md](./CONTRIBUTING.md)                                   | Committing to this repo — commit format, delivery, and the pre-push expectation                                                                                                                                             |
| [verifiability.md](./verifiability.md)                                 | Verifying a change to **this repo** itself — the declared verification methods and their ids                                                                                                                                |
