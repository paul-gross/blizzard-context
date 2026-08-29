# Worker command nodes

The authoring contract a graph author is held to for a worker node — `executor: runner`, the default
([../domain/graphs/nodes.md](../domain/graphs/nodes.md)). [../domain/graphs/nodes.md](../domain/graphs/nodes.md) and
[../domain/artifacts.md](../domain/artifacts.md) own the concepts this tree's rules bind;
[./hub-nodes.md](./hub-nodes.md) is the parallel contract for `executor: hub`. Each rule follows the slot skeleton owned
by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

Parent: [./index.md](./index.md).

| Spoke                                                                   | When to read                                                               |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [declarations.md](./worker-nodes/declarations.md)                       | The node declares a `produces:` entry, or a completion arrived without one |
| [checks-gate.md](./worker-nodes/checks-gate.md)                         | A choice must not be selectable while the node's `checks:` are red         |
| [graph-artifact-pointers.md](./worker-nodes/graph-artifact-pointers.md) | The prompt points the worker at a graph-scoped or system-scoped read       |
