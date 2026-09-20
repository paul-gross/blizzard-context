# The `agent-facing-context` axis

The gardening axis that holds this harness's own prose to the substrate `winter-canon:/index.md` declares. A spoke of
the [garden registry](./index.md); the four fields below are the shape `canon:gardening-axes` requires.

## Evaluates

Guidance drift — prose that accretes, ages, or stops being reachable while every mechanical check on it stays green.
Concretely, on this target:

- A rule no hub routes to and no task would reach, whatever its merit (`canon:admission-test`).
- Weight in a file every session loads, where a task-time read would carry it better (`canon:auto-load-tax`).
- A hub carrying content rather than routing to it, or naming a spoke that no longer exists (`canon:pure-hubs`,
  `canon:index-scrutiny`).
- A row whose stated trigger no longer matches what its file holds, so a reader routes past what they needed
  (`canon:row-is-router`, `canon:truthful-names`).
- A fact given a second full statement in a second file, where a pointer at its owner would serve
  (`canon:point-dont-duplicate`, `canon:one-owner`).
- A rule authored outside the slot skeleton, or carrying no stable id for a citation to resolve (`canon:rule-shape`).
- A process reference left in prose that is read as current guidance — a GH- reference, a tracker URL, a bare `M`/`C`
  id, "per the review" phrasing, or delivery-plan shorthand (a step label, a phase number) — or change-history narration
  (`canon:no-process-refs`, `canon:no-retro`).

## Scope

| Slug               | Ground                                                                             |
| ------------------ | ---------------------------------------------------------------------------------- |
| `blizzard-context` | The whole conventions harness — every rule, exemplar, and routing file in the repo |

## Criteria

`winter-canon:/index.md` owns every rule this axis judges by; `winter-canon:/routing.md` resolves a cited `canon:` id to
the file that owns it. [`../CONTRIBUTING.md`](../CONTRIBUTING.md) is in range for the authoring conventions local to
this harness — the `bzh:` id scheme and the skeleton a rule here is written in.

Where a command already judges the same prose, it owns that judgement and this axis does not
(`winter-canon:/enforcement-channels.md`):

- `canon:format` and `canon:markdown-lint` are out of range entirely — `blizzard-context:markdown-format` and
  `blizzard-context:markdown-lint` judge every file against them.
- `canon:no-process-refs`'s two crisp-signature citation shapes — a tracker number (`blizzard#\d+`) and a review-finding
  id (`review:F\d+`) — are out of range: `blizzard-context:markdown-prose-lint` judges every file against them. Every
  other shape its Detect list names — a GH- reference, a tracker URL, a bare `M`/`C` id, "per the review" phrasing,
  delivery-plan shorthand, and `canon:no-retro`'s change-history narration — carries no crisp signature a mechanical
  rule can safely match, and stays in range above.
- A count, roster, or enumeration is out of range where `blizzard-context:registry-drift` reaches it. Its own declared
  limitations name what it does not, and that residue is in range.

## Measurement

Every run records, findings or none:

- Files flagged, per scope swept.
- How many distinct `canon:` ids the run found at least one violation of — the breadth of drift, which a count of
  flagged files alone hides when one rule accounts for most of them.
