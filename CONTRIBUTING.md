# Contributing

`blizzard-context` is a conventions repo — it contains the rules, exemplars, and routing the rest of the blizzard ecosystem reads.
Changes target a convention file directly.

## Commit messages

Conventional Commits with a scope:

    <type>(<scope>): <description>

    [optional body]

    Co-Authored-By: Claude <noreply@anthropic.com>

- Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`, `ai`. `docs` is the common case here.
- Scope: the subsystem the change touches (`architecture`, `standards`, `verification`, …). Use the bare repo name `blizzard-context` only for a change that genuinely spans the whole harness and fits no subsystem.
- Use `Closes #N` for a GitHub issue this commit finishes; the workspace-level rules are `workspace:/context/project/contributing.md`.
- The `/wf-commit` skill (from the `winter-workflow` extension) generates commits in this exact format — prefer it over hand-writing messages.

## Authoring conventions

Every rule here follows the canon slot skeleton and stable-id scheme:

- Write rules in the `Rule` / `Why` / `Detect` / `Do` / `Don't` / `See also` skeleton owned by `winter-canon:/rule-shape.md`; keep hubs pure routers and let spokes own content (`winter-canon:/progressive-disclosure.md`).
- Give every rule a stable `bzh:<slug>` id in its heading — the id's single home (`blizzard-context:/index.md` §"Rule ids"); a non-rule leaf (a procedure or taxonomy file, `canon:rule-shape` §File kinds) carries a file-level `bzh:<slug>` id in its title. Treat a rename or removal as a breaking change for anything citing it.
- Follow the cross-cutting authoring principles in `winter-canon:/principles.md` — one canonical owner per fact, point don't duplicate, no retrospective framing, no manual line-wrapping, minimal examples.
- A new rule or routing change is a harness change: run the cold-spawn eval it is owed before pushing (`winter-canon:/evaluating-harness-changes.md`).

## Pre-push expectations

- **References resolve.** Every `blizzard-context:` / `winter-canon:` / `workspace:` path notation and every relative link points at a file that exists with the claimed shape; every `bzh:` id cited is defined.
- **Routing is complete.** A new leaf has a row in its nearest hub; a moved or removed leaf's row is repointed or deleted in the same change (`winter-canon:/progressive-disclosure.md`, `canon:index-scrutiny`).
- **Gap.** No automated markdown lint (path-notation, routing-reference, anchor checks) ships in this repo yet — verify the above by hand until the lints land. When they do, register them with `winter lint` via `winter-ext.toml` and run them before pushing.

## Delivery

- Default branch: `master`.
- Push directly to `master` — no PR, no review. Rebase onto the latest `origin/master` first so history stays linear and each landed unit of work is a single commit.
- See `workspace:/context/worktree-ops.md` for the exact git commands per worktree.
