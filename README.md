# blizzard-context

Blizzard's conventions harness — the rules every piece of blizzard code and every blizzard agent context is held to.
Derived from [winter-canon](https://github.com/paul-gross/winter-canon), it carries blizzard's own domain, architecture, standards, and verification conventions in the domain-organized, routing-hub style of `winter-harness`.

**Start at [`index.md`](./index.md)** — the topology and the domain routing table.
It is the file installed into every blizzard agent context (as the `blizzard-context:` extension) and the entry point a reader traverses to reach any convention.

## Layout

- [`domain/`](./domain/index.md) — the business/domain model: what the concepts are and how they behave, technical-free.
- [`architecture/`](./architecture/index.md) — structural invariants and design decisions a change must honor.
- [`standards/`](./standards/index.md) — the code-quality toolchains and conventions finished code is held to.
- [`verification/`](./verification/index.md) — the verifiability matrix: how a change is proven.
- [`exemplars/`](./exemplars/python/repo_pattern.py) — reference implementations to pattern new work off.
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — commit format, authoring conventions, and delivery.
