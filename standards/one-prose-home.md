# One prose home per fact (`bzh:one-prose-home`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

Every fact stated in code prose has exactly one home site; every other mention is a one-line pointer that names the home
and carries none of its content. The home is assigned by the fact's kind, never chosen per site:

| Fact kind             | Home                                                                                                                                                        |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A boundary contract   | The seam that defines the boundary — the Protocol, wire model, or schema                                                                                    |
| A local invariant     | The module that owns the state                                                                                                                              |
| Wire-field semantics  | The wire dataclass, as the field's own meaning (`bzh:comment-locality`'s wire-row qualification) — it generates into `openapi/` and thence a client's JSDoc |
| A domain concept      | The [`blizzard-context:/domain/`](../domain/index.md) file modeling it, or the delegate spoke that tree's hub sends a delegated key to                      |
| A defended decision   | The docstring of the pinning test that fails on revert (`bzh:mutation-review-selection`)                                                                    |
| An operator procedure | The owning section of the operator docs, `blizzard/docs/`                                                                                                   |

## Pointer forms

A prose pointer uses exactly one of the forms below; the registry's machine-matched citation forms are a separate
system. The site's reader, not the target, decides the form: the in-tree forms serve a reader with the source tree in
front of them, and a published surface takes the public-URL form regardless of target.

| Target            | Form                                                                                                                   | Example                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Same repo         | Repo-root-relative path — never a short form dropping the `src/...` prefix                                             | `src/blizzard/wire/chunk.py`                                                                                                       |
| Another repo      | Repo-name-qualified path                                                                                               | `blizzard/src/blizzard/wire/chunk.py`, `blizzard-mock/src/...`                                                                     |
| Harness doc       | Harness path, section named as `§Section` from the heading text — never the `#anchor` slug                             | `blizzard-context:/domain/humans/escalation.md` §The commands an escalation carries                                                |
| Published surface | Markdown link whose text names the repo and file; URL to the owning file, section-anchored where the fact lives in one | [`blizzard-context/verification/blizzard.md`](https://github.com/paul-gross/blizzard-context/blob/master/verification/blizzard.md) |

A human-read pointer may name a code symbol with its enclosing class for clarity — `src/blizzard/hub/domain/claim.py`'s
`ClaimService.rekey`.

The harness form is in-tree only, resolving through the winter-generated path-notation block the workspace instruction
file imports. A published surface is text rendered to a reader with no source tree at all — Click/argparse `--help`
output, a FastAPI/Pydantic docstring, or a hand-authored document with that same reader — so its pointer is a public
URL, or the fact restated locally as a registered survivor under §Exception's classes; a `blizzard-context:/...`
citation or a bare in-repo path never qualifies.

The URL form is branch-pinned on `master`, never a commit permalink: the pointer must age forward with its target, where
a permalink freezes at prose that will drift. And it is only as true as the target's pushed state — minted against
unpushed prose, it is a false claim until that prose lands.

## Why

This is `canon:one-owner` (`winter-canon:/principles.md`) applied to code prose: a fact explained in two files drifts
into two versions, and a reader cannot tell which one the code obeys.

## Exception

The sanctioned restatement classes:

| Class                       | What keeps its fact inline                                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Pinning test                | The test's docstring stating what its own assertion verifies — never a second narrative copy of a fact it merely touches |
| Published rendered surface  | Docstring text a tool renders into a consumer-facing artifact — `--help`, `openapi/`, generated client JSDoc             |
| Operator-facing doc section | A section whose reader is outside the workspace and cannot resolve any source path (hand-authored, not code)             |

Every sanctioned restatement is recorded in a committed census, never implicit: the site carries `role: "allowed"` and a
`reason` naming its class. A registered site belongs to exactly one register, chosen by what it restates:

| Register                                                                            | Holds                                                                          | Read by                                                     |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| `blizzard/scripts/restated-invariants.json`                                         | Restated facts — prose stating the fact itself                                 | [`blizzard:restatement-sweep`](../verification/blizzard.md) |
| [`blizzard-context:/scripts/registry-copies.json`](../scripts/registry-copies.json) | Restated cardinalities — a site stating how many members an owned registry has | `blizzard-context:registry-drift` check F                   |

In the fact register, `owner` and `sites[].symbol` match what `prose_spans.py`'s extractor emits as a site's identity —
the bare enclosing symbol alone (`rekey`, `EscalationView`, `<module>`), never a dotted `Class.method` — because
`check`/`measure` compare that bare name. The `owner` field is machine-resolved — by `resolve_md_scope` in the
`blizzard` repo's `scripts/restated_invariants.py` — and always uses the lowercase hyphenated `#anchor` slug that
`slug()` derives from the heading, e.g.
`blizzard-context:/domain/humans/escalation.md#the-commands-an-escalation-carries`. In the cardinality register,
`scripts/registry-copies.json`'s header states each `role` value's meaning.

A count is rarely worth exempting: rewrite so no number is stated — a naming phrase like "the per-concept `create`
verbs" cannot drift, while a number adds nothing over the enumeration beneath it.

## Scope

Binds:

- `blizzard/src`
- `blizzard/tests`
- `blizzard/docs`
- `blizzard/README.md`
- `blizzard/web/projects`
- `blizzard-mock/src`

Excludes generated output:

- `blizzard/openapi/`
- `blizzard/web/projects/fleet/src/lib/api/`
- `blizzard/src/blizzard/static/`

A fact's home may live outside every bound tree — a domain concept's home, `blizzard-context:/domain/`, is none of them;
the pointer obligation binds only inside them.

This scope extends past `bzh:comment-locality`'s, adding `blizzard/docs` and `blizzard/README.md`.

For restated facts, `[tasks.restatement-check]`'s roots argument in `blizzard/mise.toml` mechanically enforces the Binds
list above. The cardinality half binds wider: the bound trees' markdown, instantiated for the sibling checkouts by
`scripts/check-registry-drift.py`'s `SWEPT_CHECKOUT_GLOBS` and `SWEPT_EXCLUDED_PREFIXES` (which instantiate the
generated-output exclusions above), plus all of blizzard-context's own markdown, swept directly rather than through
those constants; it reads markdown only.

## Detect

- A contract narrated at both the seam and an implementation, or at both a schema column and its domain reader.
- A `.ts` leading `/** */` block or a `.md` section repeating a `.py` docstring's phrasing almost verbatim — the
  non-Python signature of the same drift.
- The same issue number explained — not merely cited — in more than one file.
- A pointer that also summarizes its target: a pointer names the owner, never précises the content.
- A hand-maintained count — `canon:parallel-structure` (`winter-canon:/principles.md`) names it a Detect signal, and
  `canon:row-is-router` forbids one in a hub row outright.

Mechanically: `mise run restatement-check` ([`blizzard:restatement-sweep`](../verification/blizzard.md)) — a restated
fact at an undeclared site is a `new` finding, and a declared site no longer observed is `stale`. A restated count
carries no phrase for that sweep to match, so cardinality is checked separately by check F against the census,
[`../scripts/registry-copies.json`](../scripts/registry-copies.json). Check F's contract and limits are stated once, in
`scripts/check-registry-drift.py`'s module docstring — read its Declared limitations before treating a green run as full
coverage.

## Do

```python
# Mint-only model application: see IHarnessAdapter.spawn.
```

## Don't

```python
# Model is applied at mint only — a resume passes no model flag and leans on the
# harness restoring the session's own (the same contract IHarnessAdapter.spawn states).
```

## See also

- [`bzh:comment-locality`](./comments.md) — the pointer-at-the-owner keep-shape this rule's pointers follow.
- [`bzh:comment-encapsulation`](./comment-encapsulation.md) — a fact's home also determines whose vocabulary states it.
