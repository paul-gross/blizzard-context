# Deterministic shell

This spoke owns the rule keeping coordination free of model calls; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Deterministic shell (`bzh:deterministic-shell`)

**Rule.** Coordination — the runner tick, the hub coordinator, workflow transitions, and store reads and writes — is
deterministic code with no model calls; intelligent work is confined to the leaf where a worker runs, behind the harness
seam.

**Why.** Crash correctness depends on the loop being a pure function of store, clock, and seams — a deterministic shell
is replayable, unit-testable without tokens, and crash-recoverable, while model judgement in the coordinator would break
replay and spend tokens on control flow.

**Detect.** A model call, prompt, or LLM client inside a runner loop step, the hub coordinator, a transition, or a store
method; or orchestration logic branching on freshly generated model output rather than on a parsed verdict fact.

**Do.** The worker produces a verdict; the coordinator reads the parsed verdict fact from the store and picks the
workflow edge deterministically.

**Don't.** A coordinator that prompts a model to choose the next node — it cannot be replayed under the crash sweep.

## See also

- [../crash-correctness.md](../crash-correctness.md) owns the daemon-loop requirements built on
  `bzh:deterministic-shell` and `bzh:facts-not-status`.
