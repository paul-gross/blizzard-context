# One prose home per fact (`bzh:one-prose-home`)

Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), at file-per-rule granularity.

## Rule

Every fact stated in code prose has exactly one home site; every other mention is a one-line pointer naming the home and carrying none of its content.
The home is assigned by the fact's kind, never chosen per site:

| Fact | Home |
|------|------|
| A boundary contract | The seam that defines the boundary — the Protocol, wire model, or schema |
| A defended decision | The pinning test that fails on revert (`bzh:mutation-review-selection`), in its docstring |
| A local invariant | The module that owns the state |
| Wire-field semantics | The wire dataclass — the field's own meaning (`bzh:comment-locality`'s wire-row qualification); it generates into `openapi/` |
| A domain concept | The `blizzard-context:/domain/` file that models it — [`../domain/index.md`](../domain/index.md) |
| An operator procedure | The section of the operator doc (`blizzard/docs/`) that owns it |

A pointer on a **published surface** — text that renders to a reader with no source tree at all: Click/argparse `--help` output, a FastAPI/Pydantic docstring (it generates into `openapi/` and thence a client's JSDoc), or any hand-authored document with the same reader — names its owner only in a form that reader can resolve: a public URL, or (per the Home table's own logic) restating the fact locally as a reasoned survivor. A `blizzard-context:/...` citation or a bare in-repo path is never such a form; see Exception below for when the local restatement is sanctioned rather than a drift finding.

## Pointer forms

A prose pointer names its target in exactly one of the forms below, never an invented one (the registry's machine-matched citation forms are separate). **Which form is available is decided by the site's reader, not by the target**: the first three serve a reader with the source tree in front of them, and a published surface — one whose reader has no source tree, per §Rule — takes the public-URL form regardless of what it points at.

- Same-repo, repo-root-relative: `` `src/blizzard/wire/chunk.py` `` — never a short form dropping the `src/...` prefix.
- Cross-repo, repo-name-qualified: `` `blizzard/src/blizzard/wire/chunk.py` ``, `` `blizzard-mock/src/...` ``.
- A harness target: `` `blizzard-context:/domain/humans.md` §Escalation `` — a prose pointer names the section with `§Section`, the human-readable form, not the `#anchor` slug. This form is in-tree only: it resolves through the `# Winter Extensions` block in workspace `CLAUDE.md`, which a published surface's reader cannot read. The registry's own `owner` field is a separate citation form: it is machine-resolved (`scripts/restated_invariants.py`'s `resolve_md_scope`), so it always uses the lowercase, hyphenated `#anchor` slug `slug()` produces from the heading text, e.g. `blizzard-context:/domain/humans.md#escalation`.
- A published-surface target: a public URL to the owning file, section-anchored where the fact lives in one — `` [`blizzard-context`'s `verification/blizzard.md`](https://github.com/paul-gross/blizzard-context/blob/master/verification/blizzard.md) ``. Branch-pinned on `master`, not a commit permalink: the pointer is meant to age forward with its target, and a permalink freezes it at prose that will drift. The cost is that the URL is only as true as the target's *pushed* state — a pointer minted against unpushed prose is a false claim until that prose lands.

A code-symbol target is anchored two ways for two different readers. A **prose pointer**, read by a human, may name a method with its enclosing class for clarity — `` `src/blizzard/hub/domain/claim.py`'s `ClaimService.rekey` ``. The **registry's** `owner`/`sites[].symbol` fields are machine-matched against what `prose_spans.py`'s extractor actually emits as a site's identity — always the bare enclosing symbol name alone (`rekey`, `EscalationView`, `<module>`), never a dotted `Class.method` form — because that bare name is what `check`/`measure` compare against.

## Why

This is `canon:one-owner` applied to code prose: a fact explained in two files drifts into two versions, and a reader cannot tell which one the code obeys.

## Exception

A site that would otherwise restate a fact may keep doing so, deliberately, in these classes:

- An operator-facing doc section whose reader is outside the workspace and cannot resolve a source path at all (a hand-authored document, not code) — the published-surface case above.
- A pinning test's own docstring stating what that test's own assertion verifies, not a second narrative copy of the fact it happens to touch.
- A published rendered surface — text a tool renders out of a docstring into a consumer-facing artifact (`--help` output, `openapi/`, generated client JSDoc) — keeping its fact inline per the published-surface clause above.

A committed census is where this is recorded, never left implicit: such a site carries `role: "allowed"` and a `reason` naming which class it is. The registers below are split by what the survivor restates, and a site belongs to exactly one:

| Register | Records | Read by |
|----------|---------|---------|
| `blizzard/scripts/restated-invariants.json` | a restated **fact** — a site whose prose states the fact itself | `blizzard:restatement-sweep` |
| `blizzard-context:/scripts/registry-copies.json` | a restated **cardinality** — a site stating how many members an owned registry has | `blizzard-context:registry-drift` check F |

The cardinality register's `role` field distinguishes a survivor from a registry's own home; `scripts/registry-copies.json`'s own header states what each value means.

A count is rarely worth exempting. Prefer rewriting the sentence so the number is not stated at all — a naming phrase ("the per-concept `create` verbs") carries what a reader needs and cannot drift, where a number carries nothing the enumeration beneath it does not already say. `canon:parallel-structure` (`winter-canon:/principles.md`) names a hand-maintained count as a Detect signal, and `canon:row-is-router` forbids one outright in a hub row, which is a contents list wearing a count. Registering is the fallback for a site that genuinely cannot be rewritten, not the first move.

## Scope

Binds:

- `blizzard/src`
- `blizzard/tests`
- `blizzard/docs`
- `blizzard/README.md`
- `blizzard/web/projects`
- `blizzard-mock/src`

excluding generated output (`blizzard/openapi/`, `blizzard/web/projects/fleet/src/lib/api/`, `blizzard/src/blizzard/static/`). `[tasks.restatement-check]`'s roots argument in `blizzard/mise.toml` is this list's mechanical enforcement for restated **facts** — a root added or dropped there without a matching edit here is scope drift. The cardinality half binds a wider set: **this list's markdown**, instantiated for the sibling checkouts by `scripts/check-registry-drift.py`'s `SWEPT_CHECKOUT_GLOBS` and `SWEPT_EXCLUDED_PREFIXES` (which carry the generated-output exclusions above), **plus all of blizzard-context's own markdown**, which that script sweeps directly rather than through those constants. It reads markdown only. The two enforcement surfaces are deliberately different, not one list stated twice.
Relative to `bzh:comment-locality`'s own Scope slot, this rule adds `blizzard/docs`, `blizzard/README.md`, and `blizzard/web/projects` to the trees that rule binds; `bzh:prose-budget` and `bzh:comment-encapsulation` keep to `bzh:comment-locality`'s scope as declared in their own Scope slots — their machinery (the docstring-kind cap table, `prose_density.py`'s roots) has no `.ts`/`.md` analogue.
A fact's home may live outside every bound tree above — a domain concept's home is `blizzard-context:/domain/`, which is none of them — the pointer obligation binds only inside them.

## Detect

- The same issue number *explained* — not merely cited — in more than one file.
- A contract narrated at both the seam and an implementation, or at both a schema column and its domain reader.
- A pointer that also summarizes what it points at: a pointer names the owner, it never précises the content.
- A `.ts` leading `/** */` block or a `.md` section repeating a `.py` docstring's phrasing almost verbatim — the non-Python signature of the same drift.
- Mechanically: `mise run restatement-check` (`blizzard:restatement-sweep`) — a fact restated at a site the committed registry does not declare is a `new` finding; a declared site no longer observed is `stale`.
- A restated **count** carries no phrase for that sweep to match, so cardinality is checked separately by `blizzard-context:registry-drift`'s check F, against [`../scripts/registry-copies.json`](../scripts/registry-copies.json). Its contract and its limits are stated once, in `scripts/check-registry-drift.py`'s module docstring — read its Declared limitations before reading a green run as full coverage. What it sweeps is §Scope above.

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

- `canon:one-owner` in `winter-canon:/principles.md` — the one-canonical-owner principle this rule instantiates for code prose.
- `bzh:comment-locality` in [`./comments.md`](./comments.md) — the pointer-at-the-owner keep-shape this rule's pointers follow.
- `bzh:comment-encapsulation` in [`./comment-encapsulation.md`](./comment-encapsulation.md) — a fact's home also determines whose vocabulary states it.
- `blizzard:restatement-sweep` in [`../verification/blizzard.md`](../verification/blizzard.md) — the mechanical check that a fact is stated at exactly one site.
