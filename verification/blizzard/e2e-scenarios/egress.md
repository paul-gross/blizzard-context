<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Fact-egress e2e scenarios (`bzh:e2e-egress`)

The scenarios proving the hub's fact export from its files, against the hub's own record.

## test_egress_night_e2e

One forge, one hub and one runner carry a night of six chunk shapes — a plain build, a review bounce, a human gate, an
ask answered by a person, a delivery conflict and an escalation. The hub exports it live as NDJSON, is re-hosted over
the same record and exports it live again as Parquet after the real `blizzard hub egress reset`, and
`blizzard hub egress backfill` writes a third copy. The module reads the directories back the way a warehouse would.

- `test_a_night_of_chunks_is_exported_end_to_end` — proves both live newest-copy row sets and the backfilled rows are
  equal excluding `exported_at`; every step in the chunks' history and every usage fact on the spend surface is
  exported; every data file is named by a manifest with its row count and SHA-256; a usage fact forwarded on the wire
  after its step was exported converges the step's row to the sum of its `invocations` rows in both formats; the docs'
  DuckDB recipes match `blizzard hub analytics summary spend-nodes` and name the station built to be slowest; and a scan
  of the decoded rows, manifests and schemas finds none of the planted "what never leaves" values.
