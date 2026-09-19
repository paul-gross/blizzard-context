# A verb's `--help` states its effect, never its mechanism (`bzh:help-states-effect`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

A client verb's `--help` text states the observable effect of invoking the verb — what changes, what the operator will
then see, what fails and when — and never the mechanism producing it.

## Why

`--help` renders to an operator with no source tree in front of them, so the effect is the only part of the text they
can check against what they then see. A named mechanism couples the text to an implementation that changes without the
verb's help being reopened.

## Scope

Binds the text Click renders for a `blizzard` client verb — the command's docstring and each parameter's `help=`. The
effect may land on the far side of a boundary; `bzh:comment-encapsulation` excepts it for that reason, and this rule
bounds what the exception admits.

## Detect

A client verb's `--help` naming the mechanism behind an effect — a loop step, a bumped counter, an internal reconciler,
a daemon-side process — where the effect alone tells the operator what they need.

## Do

```python
def pause(...) -> None:
    """Pause this runner: it starts no new workers, and `runner status` reports it paused until the brake is cleared."""
```

## Don't

```python
def pause(...) -> None:
    """Append a pause fact the loop's spawn step reads at its next tick before it forks a worker."""
```

## See also

- `bzh:comment-encapsulation` in [./comment-encapsulation.md](./comment-encapsulation.md) — the seam-vocabulary rule
  whose Exception admits this text.
- `bzh:operator-vocabulary` in [./operator-vocabulary.md](./operator-vocabulary.md) — the terms the stated effect is
  worded in.
- `bzh:one-prose-home` in [./one-prose-home.md](./one-prose-home.md) — `--help` as a published surface, and the pointer
  form it takes.
