# Standards

The code-quality conventions a finished blizzard change is held to — consulted both while writing the affected code and when reviewing whether it is up to standard before it lands. Follow the row that matches what you are writing.
Where [architecture/](../architecture/index.md) governs how code is *structured and designed*, this domain governs the *code-quality details* of the result.

The commands these standards name are proven by the verifiability matrix at [../verification/blizzard.md](../verification/blizzard.md).

Parent: [../index.md](../index.md).

| Standard | When to read |
|----------|--------------|
| [./python.md](./python.md) | Writing or reviewing Python, or authoring a docstring's prose — the uv / ruff / pyright toolchain, the commands a change must pass, and the conventions that prose is held to |
| [./frontend.md](./frontend.md) | Writing or reviewing the Angular apps — the eslint-no-prettier / vitest toolchain and the committed, drift-checked generated API client |
| [./logging.md](./logging.md) | Adding a log call or picking a level — the structlog call-site and level conventions |
| [./persistence.md](./persistence.md) | Touching a store schema or a migration — the portable-SQL rule and the manual-Alembic migration policy |
| [./wire.md](./wire.md) | Adding a route (or a frontend consumer) that serializes or reads an instant — the UTC-aware-end-to-end rule spanning store, domain, wire, and TS |
| [./hub-nodes.md](./hub-nodes.md) | Authoring or reviewing an `executor: hub` node — the `run:` step shape, the injected env-var contract, the outcome protocol, and the per-step idempotence a `run:` command must honor |
| [./worker-nodes.md](./worker-nodes.md) | Authoring or reviewing a worker node that declares a `produces:` entry or gates a choice on its `checks:` — the prompt's declaration instruction, the judgement-assessment fallback, the `produces_mode` enforcement backstop, the `requires_checks` gate, and the worker's injected identity env |
