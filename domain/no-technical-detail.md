# A domain file carries no technical detail (`bzh:domain-no-technical-detail`)

What a file in this tree may state, and where a claim it refuses goes instead. Slot skeleton: `canon:rule-shape`
(`winter-canon:/rule-shape.md`), at file-per-rule granularity. Part of the [domain model](./index.md).

## Rule

A domain file states what the model permits, requires, or refuses, and carries no technical detail. Technical detail is
either of:

- **Implementation vocabulary** — store columns and tables, wire models, service classes, HTTP routes. It belongs to
  [`architecture/`](../architecture/index.md) and [`standards/`](../standards/index.md), and a domain file points there
  instead of carrying it.
- **A claim quantified over what currently ships** — what every shipped lane does, what the shipped `deliver` nodes are,
  which authored routing is the ordinary one — whatever vocabulary it is worded in. An orientation to the shipped set
  belongs outside `domain/`, with whichever surface tracks the code for that material — architecture guidance, or the
  shipped thing's own docs.

Vocabulary an operator or graph author writes — a status name, an authored node's own keys — is domain vocabulary and
stays: what the bar refuses is the claim, never the words it is made of, so graph-author phrasing never licenses a
shipped-set census.

## Why

`domain/` is the reference a planner or verifier asserts correctness against, so a structural fact in it taxes a reader
who came for intent. What ships today is a property of the release, not of the model, and the next graph that lands
falsifies it.

## Exception

A key inside a contract the domain file has delegated to a standard leaves the domain file, while the delegating facet's
own entry stays. The key is stated in the first of these that exists:

- the spoke of that standard already stating the key's siblings;
- for a first of its kind, the spoke of that standard whose reader question the key answers.

A key no spoke takes on either count is outside the delegation, and stays.

## Detect

- A store, wire, service, or route name in a domain file carrying what that thing does, not a pointer at its owner.
- A quantifier over the release — "every shipped", "each shipped graph", "the shipped lanes" — governing a behavioral
  claim. The question to ask: would a newly landed graph, breaking no rule of the model, make the sentence false?
- A delegated contract's key stated in the domain file beside the delegating facet's entry while the standard's spoke
  states its siblings.

## Do

*"A delivery conflict is one of the script's own outcome choices, routed to whatever edge the graph authors."* — what
the model permits of any graph.

## Don't

*"The shipped `deliver` nodes route a conflict to a resolve node."* — graph-author vocabulary, yet a census of the
release: a graph landing with another routing falsifies it and breaks no rule of the model.

## See also

- `bzh:one-prose-home` in [`../standards/one-prose-home.md`](../standards/one-prose-home.md) — assigns a domain concept
  its home in this tree; this rule bounds what that home may say.
- `bzh:owed-claims-landed` in [`../verification/blizzard/evidence.md`](../verification/blizzard/evidence.md) — the
  planning rule that lands an author-facing surface's statement here, placing a delegated key by §Exception.
