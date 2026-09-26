# The `performance` axis

The gardening axis that holds blizzard's hot paths to the cost their shape implies. A spoke of the
[garden registry](./index.md); the four fields below are the shape `canon:gardening-axes` requires.

## Evaluates

Cost drift — work the code pays for that its own result never needed, while every gate stays green. Concretely, on this
target:

- A singular read resolved per item inside a loop, where the seam offers a plural counterpart or could declare one.
- A read seam whose only shapes are one id and every id, leaving a caller holding a subset with no expressible middle.
- A sweep that rescans its whole corpus each interval with no watermark, cursor, or early exit — and one whose cadence
  is a fixed interval where a change signal would do.
- A value re-read or recomputed per iteration that the loop never varies.
- A list endpoint or store read with no bound, whose cost is set by fleet size rather than by the page asked for.
- Decoding, parsing, or validating a payload to answer a question its raw bytes already answer.

## Scope

| Slug                | Ground                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| `data-access-layer` | Both stores' read seams and the adapters behind them — reconstitution shape and its plural counterparts |
| `hub-sweeps`        | The hub's periodic background sweeps — their corpus, their gating, and their cadence                    |
| `runner-tick`       | The runner's tick loop and its outbound fact and transcript drains                                      |
| `api-surface`       | The hub's HTTP read endpoints — their per-request fan-out and their bounds                              |

## Criteria

A rule binds a shape, not a scope: each weed above is judged by one rule wherever the code showing it lives, so the same
rule serves every scope whose ground carries that shape.

| Weed                                                                                                    | Rule                                                                                                     | Scopes                                                                                           |
| ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| A singular read per item in a loop; a seam offering only one id and every id                            | [`../architecture/repository-access.md`](../architecture/repository-access.md) `bzh:bulk-reconstitution` | All four — the loop may be an adapter's, a sweep pass's, a tick step's, or an endpoint's fan-out |
| A sweep rescanning its corpus each interval, and a fixed cadence where a change signal would do         | [`../architecture/repository-access.md`](../architecture/repository-access.md) `bzh:probe-gated-pass`    | `hub-sweeps`, `runner-tick`                                                                      |
| A list endpoint or store read with no bound                                                             | [`../architecture/repository-access.md`](../architecture/repository-access.md) `bzh:page-bounded-read`   | `api-surface`, `data-access-layer`                                                               |
| A loop-invariant value re-read per iteration; a payload decoded to answer what its bytes already answer | No rule — judged by reading; a finding cites the weed's own bullet above and carries no `bzh:` id        | All four                                                                                         |

Index coverage is out of range: it belongs to its gate, [`blizzard:component-test`](../verification/blizzard.md)
(`blizzard/tests/test_store_read_index_gate.py`), which judges every change rather than every run of this axis
(`winter-canon:/enforcement-channels.md`). What that gate cannot see stays in range — a perfectly indexed read is still
a finding here when a call site issues it once per item.

## Measurement

Every run records, findings or none:

- Findings opened, per scope swept.
- Statements issued per representative operation, for each hot path the run measured — `blizzard/tests/support.py`'s
  `count_queries` over the real adapters is the instrument. A scope's trend is then a number rather than an impression,
  and a path already measured by an earlier run is re-measured rather than re-judged.
