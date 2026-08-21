# Contributing

`blizzard-context` is a conventions repo — it contains the rules, exemplars, and routing the rest of the blizzard
ecosystem reads. Changes target a convention file directly.

## Commit messages

Conventional Commits with a scope:

    <type>(<scope>): <description>

    [optional body]

    Co-Authored-By: Claude <noreply@anthropic.com>

- Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`, `ai`. `docs` is the common case here.
- Scope: the subsystem the change touches (`architecture`, `standards`, `verification`, …). Use the bare repo name
  `blizzard-context` only for a change that genuinely spans the whole harness and fits no subsystem.
- Use `Closes #N` for a GitHub issue this commit finishes; the workspace-level rules are
  `workspace:/context/project/contributing.md`.
- The `/wf-commit` skill (from the `winter-workflow` extension) generates commits in this exact format — prefer it over
  hand-writing messages.

## Authoring conventions

Every rule here follows the canon slot skeleton and stable-id scheme:

- Write rules in the `Rule` / `Why` / `Detect` / `Do` / `Don't` / `See also` skeleton owned by
  `winter-canon:/rule-shape.md`; keep hubs pure routers and let spokes own content
  (`winter-canon:/progressive-disclosure.md`).
- Give every rule its stable id, per the scheme `winter-canon:/rule-shape.md` owns — with two differences here: the
  prefix is `bzh:`, historical from the repo's old name and kept because blizzard's and blizzard-mock's code cite it;
  and the rule's heading is the id's only home — this harness keeps no id registry to re-sync.
- Read `winter-canon:/principles.md` before authoring or editing any file here, and follow every principle it states —
  the canon owns that list, so this is a read-trigger rather than a copy to re-sync.
- A new rule or routing change is a harness change: run the cold-spawn eval it is owed before pushing
  (`winter-canon:/evaluating-harness-changes.md`).

## Pre-push expectations

Run this repo's own declared methods before pushing. [verifiability.md](./verifiability.md) owns each one's surface and
pass criteria; what belongs here is only *which* a change owes:

- `blizzard-context:registry-drift` and `blizzard-context:registry-drift-tests` — every change.
- `blizzard-context:markdown-format` and `blizzard-context:markdown-lint` — every change: the mechanical style gates
  every markdown file here is held to. They also run through `winter lint`: this extension contributes the check
  (`winter-ext.toml`'s `lint` field), so a routine env lint catches the same drift; `blizzard-context:lint-script-tests`
  covers the contribution itself.
- `blizzard-context:manual-reference-check` — every change: the by-hand pass covering the reference checks no tool here
  runs — path notation, routing references, anchors.
- `blizzard-context:manual-cold-eval` — a rule addition, a trigger broadening, or a routing change (`canon:cold-eval`).

## Delivery

- Default branch: `master`.
- Push directly to `master` — no PR, no review. Rebase onto the latest `origin/master` first so history stays linear and
  each landed unit of work is a single commit.
- See `workspace:/context/worktree-ops.md` for the exact git commands per worktree.
