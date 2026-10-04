# Splitting domain and orchestration (`bzh:domain-orchestration-split-pass`)

**Rule.** When told to split a concept's domain and orchestration — in any wording that names split, domain, and
orchestration — bring that concept into `bzh:domain-orchestration-split` shape
([../architecture/clean-architecture.md](../architecture/clean-architecture.md) §Domain-orchestration split) through the
steps below. The pass moves where each decision lives, never what it decides.

**Why.** Rules interleaved with orchestration hide the decisions the code never made; a pass that holds behavior fixed
surfaces each one as a question instead of settling it silently, and stays one reviewable lane.

**Scope.** One concept per pass: its model module, every service holding its write port, and every API route and CLI
verb reaching those services. A domain question the pass raises goes to the user, never into the code.

1. **Map the ground.** Locate the concept's model module, every service holding its write port, and every route and CLI
   verb reaching those services.
2. **Inventory the decisions.** List every `if`/`raise` on a loaded object's state wherever it sits — service,
   controller, or adapter — and classify each as rule or orchestration by the Scope slot of
   `bzh:domain-orchestration-split`.
3. **Tabulate the transitions.** If the concept carries a state, tabulate every verb against every state, marking what
   the code decides today in each cell. A cell the code decides moves to the model in step 4. A cell the code leaves
   open goes in the report: as a conformance defect where [../domain/](../domain/index.md) decides it, or as a question
   for the user where it does not.
4. **Move each rule onto the model**, returning the fact, record, or refusal, with the instant passed in. An id a rule
   needs becomes its loaded object, resolved at the edge.
5. **Thin the edges.** Each service keeps only clock → model → port → race handling. Each controller keeps only
   load-or-404 → service → domain error mapped to its status.
6. **Pin by value.** Each moved rule gets a unit test that needs no fake. The existing service and API tests pass with
   their assertions unchanged; a changed assertion is a changed behavior, which this pass forbids.
7. **Report** each rule moved, from and to, and each open cell from step 3.
