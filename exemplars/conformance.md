# Exemplar conformance (`bzh:exemplar-conformance`)

What an exemplar is held to, in the slot skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`). Parent:
[./index.md](./index.md).

## Rule

An exemplar passes every gate its production counterpart is held to, run over the real blizzard checkout, and agrees
with every standard it touches. It reads like the best production code of its layer — the same names, layering, and
comment density — and carries no prose explaining itself beyond the `# exemplar:` device below. When an exemplar and a
standard disagree, the same change fixes whichever one is wrong.

Exemplars live in the `blizzard` repo, outside the shipped package, so a change to the code they build on changes them
in the same commit. An exemplar sits where its production counterpart would: Python under
`blizzard/exemplars/python/exemplar/` mirrors `blizzard/src/blizzard/` with `exemplar` in place of `blizzard`, its tests
sit flat in `blizzard/exemplars/python/tests/` as `blizzard/tests/` does, and Angular files under
`blizzard/exemplars/web/` mirror `blizzard/web/projects/`. It imports the real blizzard infrastructure its counterpart
would, never a placeholder library. This file and [./index.md](./index.md), the router to them, stay in the harness.

## The `# exemplar:` device

A comment opening `# exemplar:` (`// exemplar:` in TypeScript) explains the exemplar itself and is never copied into
production. Each exemplar module carries one directly under its module docstring, naming the `bzh:` ids it instantiates;
beyond that, one marks only a stand-in for something production does elsewhere, such as a cut-down composition root.

## Why

Agents imitate the pattern pool, so an exemplar is the deliberate route from a standard into write-time behavior
(`canon:enforcement-channels`) — and an exemplar no gate runs over drifts unseen, carrying its drift into every module
patterned off it.

## Detect

- blizzard's own gates failing over `blizzard/exemplars/`. The Python half rides `blizzard:lint`, `blizzard:format`,
  `blizzard:typecheck`, and the pytest tiers, where `blizzard/tests/test_layering.py` also holds it to the
  `bzh:prose-budget` caps and the `bzh:data-roles`, `bzh:domain-core`, and `bzh:internal-visibility` scans;
  `blizzard:exemplar-check` runs the strict Angular type-check, eslint, the specs, and `web:structural-gate` over the
  web half, and fails when the committed client stand-in differs from the one generated from the exemplar router.
- An exemplar whose prose density exceeds its production layer's, as `prose_density.py measure` in `blizzard/scripts/`
  reports it — judged at review.
- An exemplar diverging from the shape its layer's production code settled on — a second name for a role, a second
  placement for a seam — with no standard choosing it.

## Do

```python
"""Permit use cases — request a permit, then move it through its verbs under the permit's row lock."""

# exemplar: bzh:domain-orchestration-split, bzh:narrow-seams, bzh:store-exclusive-write.
```

## Don't

An exemplar importing a library blizzard does not depend on, or a docstring walking the reader through the pattern — the
next agent copies the walkthrough into production.
