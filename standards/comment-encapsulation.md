# State a seam's contract in the seam's own vocabulary (`bzh:comment-encapsulation`)

Whose vocabulary a fact on or near a boundary is stated in, in the Rule/Why/Detect/Do/Don't slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Rule

A docstring or comment on a boundary — one of the seams §Scope lists for its tree — states that boundary's obligation in
the boundary's own vocabulary: parameters, return, error contract, invariants. It never names a party on the other side:
no concrete caller, no loop step, no CLI or UI surface, no consuming container, page, or spec, no sibling or concrete
implementation. The discipline is symmetric — an implementation never re-explains the seam contract it implements, and a
caller never explains its callee.

## Why

Naming a cross-boundary party couples the boundary's text to that party's implementation — the dependency the code's
layering forbids — and every far-side change stales it silently. A seam whose docstrings enumerate their consumers stops
reading as a contract, and the next implementer or caller inherits one consumer's specifics as if they were obligations.

## Exception

- A bare pointer at the party that owns the fact: a name or path on one line, carrying none of the owner's content.
- A client verb's `--help` text: it states the observable effect of invoking it — what changes, what the operator will
  then see, what fails and when — and never the mechanism producing it.

## Scope

Binds the same trees as `bzh:comment-locality`, and the seams it holds are each language's own:

| Tree                                                  | Seams                                                                                                                                   |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `blizzard/src`, `blizzard/tests`, `blizzard-mock/src` | A Protocol, an interface dataclass, a wire model, a store schema                                                                        |
| `blizzard/web/projects`                               | An exported `interface` or type alias, an `InjectionToken`, a component's `input()` and `output()` members, a library's `public-api.ts` |

`blizzard-context`'s `exemplars/` files are expository teaching artifacts and are not bound.

## Detect

- In a Protocol, wire-model, or schema docstring, a cross-boundary party's name followed by what that party does with
  this code.
- Prose naming a symbol its module does not import — a `{@link}` target included — or naming a module that imports this
  one: the mechanical filter for narrating across a boundary.
- On an `InjectionToken`, an exported `interface`, or an `input()`/`output()` member, the name of the container, page,
  or spec that provides, binds, or overrides it, followed by what it does there — a test-override note is the commonest
  form.
- A contract restated on both sides of a seam, which is `bzh:one-prose-home`'s signature: a reviewer cites that id, and
  [./one-prose-home.md](./one-prose-home.md) owns what a pointer may carry.
- A client verb's `--help` naming the mechanism behind an effect — a loop step, a bumped counter, an internal
  reconciler, a daemon-side process — where the effect alone tells the operator what they need.

## Do

```python
def resolve(self, key: str) -> Value | None:
    """Return the first match in declaration order, skipping disabled entries; None when none match."""
```

```ts
/** Builds the event source for a stream URL; a source that never opens is the caller's timeout to raise. */
export const STREAM_SOURCE = new InjectionToken<StreamSourceFactory>('fleet.STREAM_SOURCE');
```

## Don't

```python
def resolve(self, key: str) -> Value | None:
    """Called by the CLI loader; the TOML adapter walks its file list and returns the first hit."""
```

```ts
/** Overridden by `live-feed.spec.ts` with a fake so reconnects run without a browser; `BoardShell`
 * provides the real one at bootstrap. */
export const STREAM_SOURCE = new InjectionToken<StreamSourceFactory>('fleet.STREAM_SOURCE');
```

## See also

- `bzh:comment-locality` in [./comments.md](./comments.md) — which facts code prose may state at all; this rule bounds
  whose vocabulary an owned fact is stated in.
- `bzh:dependency-inversion` in [../architecture/clean-architecture.md](../architecture/clean-architecture.md) — the
  code-layering arrows this rule makes prose obey.
