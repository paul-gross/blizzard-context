# Declared artifacts

A graph may declare a top-level `artifacts:` map (name → file reference) — a sibling of the node set, not a node facet
(graph definition: [../graphs.md](../graphs.md)); declaring none means an empty map. Definitional — a taxonomy of the
map's authoring surface: what an author writes and what load and mint-time validation reject (`canon:rule-shape` §File
kinds); worker read-back is owned by [../artifacts.md](../artifacts.md) §Artifact. Part of the
[domain model](../index.md).

## Names

A name is alphanumerics joined by single `-`, `_`, or `.` separators, none leading or trailing, no `/`. A name colliding
with any node's `produces:` name is rejected — both scopes answer the same artifact reads, so sharing would be
ambiguous, not a legal shadow.

## Resolution

Each reference resolves to its file's text at definition load, so what reaches the mint is content, never a path. A
definition submitted with no directory to resolve against must already carry the text inline; a value still reading as a
bare path is rejected rather than baked.

## Order

An entry's authored map position is the order a worker reads the declarations back in, struck afresh at each mint.
Re-ordering the map alone mints nothing — reconciliation compares parsed definitions, and a map equals itself however
ordered — so the order in force stays the current mint's.
