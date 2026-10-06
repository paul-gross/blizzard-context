<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Fact-egress e2e scenarios (`bzh:e2e-egress`)

The scenarios proving the hub's fact export from its files, against the hub's own record.

## test_egress_night_e2e

One forge, one hub and one runner carry a night of six chunk shapes — a plain build, a review bounce, a human gate, an
ask answered by a person, a delivery conflict and an escalation — across two graphs that both name a `build` and a
`deliver` node. The hub exports it live as NDJSON, is re-hosted over the same record and exports it live again as
Parquet after the real `blizzard hub egress reset`, and `blizzard hub egress backfill` writes a third copy over the
night's window, given as `Z` instants. A module fixture runs the night once and keeps the re-hosted hub up; each test
below is one proof, reading the directories back the way a warehouse would.

- `test_both_live_exports_hold_the_same_newest_rows` — proves the NDJSON and Parquet live newest-copy row sets are equal
  excluding `exported_at`, and that neither dataset is empty.
- `test_both_exports_hold_the_hubs_record` — proves every step in the chunks' history and every usage fact on the
  `spend-chunks` surface, tokens and billed cost, is in both exports.
- `test_manifests_name_every_file` — proves every data file, live and backfilled, is named by exactly one manifest with
  its row count and SHA-256, and every file a manifest names exists.
- `test_nothing_planted_leaves` — proves a scan of the decoded rows, manifests and schemas finds none of the planted
  "what never leaves" values.
- `test_late_usage_converged_in_both` — proves a usage fact forwarded on the wire after its step was exported converges
  the step's row to the sum of its `invocations` rows in both formats.
- `test_a_backfill_of_the_window_equals_the_live_export` — proves the backfill of the night's zoned `--since`/`--until`
  window writes rows equal to the live newest copies, excluding `exported_at`.
- `test_recipes_agree_with_the_hubs_analytics` — proves the docs' DuckDB cost recipe matches
  `blizzard hub analytics summary spend-nodes` over the same zoned window per station, in both formats, and the
  slowest-station recipe names the station built to be slowest on its own graph.
- `test_cost_by_node_splits_a_shared_node_name_by_graph` — proves the cost recipe keeps `build` and `deliver` as a
  distinct station on each graph that names them, never one row per node name.
- `test_published_newest_views_return_the_newest_copies` — proves the dictionary's published newest-copy views return
  the identities the rows' own newest copies name, in both formats.

## test_egress_events_e2e

One forge, one hub and one runner carry two chunks: a Claude Code build and an OpenCode review, whose workers read
files, invoke a skill and spawn an agent whose child session reads a file, and an ask answered by a person, which
extends its transcript through the resumed session. The hub derives the events and exports them as NDJSON; the module
reads them back with the dictionary's `events_current` view over the files alone.

- `test_the_exported_events_agree_with_the_hubs_own_counts` — proves `events_current` grouped by file, skill, agent type
  and node equals `blizzard hub analytics summary counts-{files,skills,agent-types,nodes}`, with paths made relative to
  the runner's recorded working directory; the docs' files-a-station-read-last-week recipe names the review node's
  reads, the child session's included; no row, manifest or schema carries the planted prompt, tool input or output, key,
  question or working directory, or an event's payload; and after a forced `blizzard hub analytics re-derive` and a real
  `blizzard runner transcript reship` the export holds a `dropped` row for the superseded segment and the counts still
  equal the hub's.
