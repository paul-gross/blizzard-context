# A `run:` step's environment

What a step's command may read from its environment, and the one write channel that environment hands it.

Parent: [../hub-nodes.md](../hub-nodes.md).

## The injected environment is the command's whole interface (`bzh:hub-node-env-contract`)

**Rule.** The injected env vars below are the only channel a `run:` step's command has into the chunk's identity, prior
work, and the forge credential — a script referencing any field this contract does not list is reading nothing.

| Variable                                           | Carries                                                                                                                                                                                                |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `BZ_HUB_CHUNK_ID`                                  | The chunk's id                                                                                                                                                                                         |
| `BZ_HUB_NODE_ID`, `BZ_HUB_NODE_NAME`               | The node's id and the node's name                                                                                                                                                                      |
| `BZ_HUB_EPOCH`                                     | The current attempt's epoch, as a string                                                                                                                                                               |
| `BZ_HUB_BASE_BRANCH`                               | The branch the chunk's work lands against                                                                                                                                                              |
| `BZ_HUB_FEATURE_TITLE`                             | The prose PR/merge title resolved from the chunk's primary work item; absent when it cannot be resolved                                                                                                |
| `BZ_HUB_WORKDIR`                                   | The per-chunk hub workdir — also the working directory each step's command runs in — persisting across a node's steps and across a re-run of the same node                                             |
| `BZ_HUB_GIT_COMMITS`                               | A JSON list of `{repo, branch, commit}` — the chunk's latest commit-pointer artifacts                                                                                                                  |
| `BZ_HUB_ARTIFACT_NAMES`                            | A JSON list of artifact names already recorded for this node — a script's own re-run-skip input, alongside the executor's step-level skip                                                              |
| `BZ_HUB_EXPECT_GIT_COMMITS`                        | `"1"` when some node in the chunk's graph declares a `git_commit`-kind `produces:`, `"0"` when none does                                                                                               |
| `BZ_FORGE_URL`, `BZ_FORGE_TOKEN`, `BZ_FORGE_OWNER` | The hub's own configured forge credential, present only when the hub is configured with one                                                                                                            |
| `BZ_HUB_MARKER_CALLBACK_URL`                       | Records a marker mid-run via `POST {name, content}`; the CLI wrapper is `blizzard hub record-marker NAME [CONTENT]`                                                                                    |
| `BZ_HUB_MARKER_TOKEN`                              | The capability token authorizing the marker POST, sent back as the `X-Blizzard-Marker-Token` header — minted per `(chunk, node, epoch)` before the node visit's steps run, revoked once the visit ends |

A non-2xx response to the marker-write POST is fatal — the script must raise rather than swallow it and proceed. Beyond
the injected keys a step inherits the hub daemon's own environment, and the executor prepends the hub interpreter's own
bin directory to `PATH`, so a bare `python3` in a `run:` command always resolves to the interpreter the hub itself runs
under — the one that can import `blizzard` — regardless of how the daemon was launched (a systemd unit invoking the venv
binary by absolute path carries no venv on its inherited `PATH`).

**Why.** A `run:` step is an ordinary subprocess with no access to the hub's domain objects; naming the whole env here
means a graph author never guesses at an undocumented field and a reviewer can tell a script reading anything else is
reading nothing.

**Detect.** A `run:` script referencing an env var outside this contract; a script hardcoding a forge URL or token
instead of reading the injected credential; a marker-write POST sent with no `BZ_HUB_MARKER_TOKEN` header; a
marker-write closure whose POST result is never checked — the discarded-response shape in which a dropped or
unauthorized write is swallowed and the script proceeds to report success anyway.

**Do.**

- `land_default.py` reads `BZ_HUB_GIT_COMMITS`/`BZ_HUB_ARTIFACT_NAMES` to compute which repos still need landing, and
  `BZ_FORGE_URL`/`BZ_FORGE_TOKEN`/`BZ_FORGE_OWNER` to talk to the forge directly — deliberately no forge seam
  (`bzh:deterministic-shell` in [../../architecture/system-shape.md](../../architecture/system-shape.md)), because this
  script is the policy.
- `land_common.MarkerWriter` — the one marker channel every land script holds, as `LandRun.markers` — treats any non-2xx
  as fatal, raising rather than returning, so a merge can never land with no durable record of it.

**Don't.** A script that posts the marker write and moves on without inspecting the response — a non-2xx there means the
write never happened, and printing a success choice anyway reports success over an unrecorded merge.
