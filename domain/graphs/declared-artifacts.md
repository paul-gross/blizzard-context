# Declared artifacts

The authoring side of a graph's `artifacts:` map. Part of the graph definition ([../graphs.md](../graphs.md)).

A graph may declare a top-level `artifacts:` map — name → file reference — another sibling of the node set, not a node
facet; a graph declaring none carries an empty map. This section owns the **authoring** side: what an author writes, and
what the load and the mint-time validator reject. What a worker then reads back — the graph scope itself and the
immutability every chunk pinned to that mint reads through — is [artifacts.md](../artifacts.md) §Artifact's.

Each reference resolves to its file's text as the definition is loaded, so what reaches the mint is content and never a
path — a definition submitted with no directory to resolve against carries the text inline already, and one whose value
still reads as a bare path is rejected rather than baked. A name is alphanumerics joined by single `-`, `_`, or `.`
separators, with none leading or trailing and no `/`, and a name colliding with any node's `produces:` name is rejected:
both scopes answer the same artifact reads, so a shared name would be ambiguous rather than a legal shadow.

An entry's position is taken from where it sits in the map as authored, and that position is the order a worker reads
the declarations back in — struck afresh at each mint from the map as that mint parsed it. A re-ordered map is not a
changed definition, though: reconciliation compares parsed definitions, and a map is equal to itself however its entries
are ordered. So re-ordering `artifacts:` and nothing else mints nothing, and the order in force stays the one the
current mint struck.
