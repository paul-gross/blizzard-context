# blizzard-context

**Blizzard's conventions harness** — the rules every piece of [blizzard](https://github.com/paul-gross/blizzard) code,
and every blizzard agent context, is held to.

A *harness* is the agent-facing half of a codebase, kept in a repo of its own: the domain model an agent plans against,
the structural invariants a change must honor, the standards finished code is held to, and the methods a change is
proven by. Keeping it separate is the point — the application repo stays free of instruction sprawl, and the conventions
can be read, reviewed, and evolved on their own terms.

This repo is blizzard's instance of one. It derives from [winter-canon](https://github.com/paul-gross/winter-canon), the
universal substrate defining what any harness must be, and follows
[winter-harness](https://github.com/paul-gross/winter-harness) in *style* — domain-organized convention directories,
routing hubs, a verifiability matrix — while carrying **blizzard's own rules**, not winter's.

The name is for what it holds rather than for the concept: blizzard also drives *coding harnesses* (Claude Code, Codex,
OpenCode — the adapter seam), and that seam keeps the word.

## Start here

**[`index.md`](./index.md)** is the front door — the topology and the routing table that reaches every convention. It is
also the file installed into every blizzard agent context, so an agent working on blizzard arrives already holding it.

## How it reaches an agent

- **Installed as a winter extension.** Dropped into a workspace, its `index.md` is surfaced into the workspace's
  `AGENTS.md`/`CLAUDE.md`, so the routing loads into every agent context without anyone remembering to mention it.
- **Addressed by path notation.** Files here are cited as `blizzard-context:/architecture/repository-access.md`,
  resolved against wherever the extension happens to be installed — the local directory name varies, the notation does
  not.
- **Cited by stable id.** Every rule carries a `bzh:<slug>` id in its heading, and non-rule leaves carry one in their
  title. That id is the handle a plan, a review finding, a cross-reference, or a source comment uses, which keeps a
  convention and the code obeying it linked in both directions. Ids are stable: renaming or removing one is a breaking
  change.

## Layout

| Directory                                          | What it holds                                                                                  |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`domain/`](./domain/index.md)                     | The domain model — what blizzard's concepts are and how they behave, with no technical detail. |
| [`architecture/`](./architecture/index.md)         | Structural invariants and design positions a change must honor.                                |
| [`standards/`](./standards/index.md)               | The toolchains and code-quality conventions finished code is held to.                          |
| [`verification/`](./verification/index.md)         | Blizzard's verifiability matrix — how a change to the application is proven.                   |
| [`workflows/`](./workflows/index.md)               | How work reaches `master`, and the release cut an agent still drives by hand.                  |
| [`tooling/`](./tooling/index.md)                   | Driving an external tool beyond the winter CLI.                                                |
| [`exemplars/`](./exemplars/python/repo_pattern.py) | Reference implementations to pattern new work off.                                             |

Alongside them sit this repo's own: [`CONTRIBUTING.md`](./CONTRIBUTING.md) for commit format, authoring conventions, and
delivery, and [`verifiability.md`](./verifiability.md) for how a change *here* is verified.

## A harness held to its own standard

Convention repos rot quietly — a rule drifts from the code it governs and nothing fails. So this one ships gates of its
own, declared as methods in [`verifiability.md`](./verifiability.md) and run before every push:

```shell
dprint check                        # markdown format
rumdl check .                       # structural markdown lint
python3 scripts/check-registry-drift.py --blizzard ../blizzard --blizzard-mock ../blizzard-mock --gate
python3 tests/test_check_registry_drift.py
```

The drift check is the interesting one: it reads a committed census and fails when a registry's stated shape and its
actual enumeration disagree — including at sites in the sibling `blizzard` and `blizzard-mock` checkouts, which is why
it wants them present. The markdown gates also run through `winter lint`, since this extension contributes the check.

Beyond the mechanical passes, a rule addition or a routing change owes a **cold-spawn eval** — put the change in front
of a fresh agent context and see whether it actually routes there. `winter-canon:/evaluating-harness-changes.md` owns
that procedure.

## Building your own

Blizzard's rules will not be your rules, so this repo is more useful as a worked example than as a dependency: a real,
enforced harness for a real system, with the canon it derives from published separately. Fork it and replace the
contents domain by domain, or start from `winter-canon` and use this as the reference for what a filled-in instance
looks like.

## Contributing

Issues and ideas are welcome. Changes target a convention file directly — read [`CONTRIBUTING.md`](./CONTRIBUTING.md)
first for the commit format, the canon slot skeleton every rule is written in, and the pre-push expectations above.
