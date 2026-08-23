# The injected env-var contract

Parent: [../hub-nodes.md](../hub-nodes.md).

## The injected env-var contract (`bzh:hub-node-env-contract`)

**Rule.** Every `run:` step's command is invoked with exactly this env — the only channel a step's command has into the
chunk's identity, prior work, and forge credential:

| Var                                                  | Carries                                                                                                                                                                                                                                     |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BZ_HUB_CHUNK_ID`                                    | The chunk's id.                                                                                                                                                                                                                             |
| `BZ_HUB_WORKDIR`                                     | The per-chunk hub workdir — persists across a node's steps and across a re-run of the same node.                                                                                                                                            |
| `BZ_HUB_NODE_ID`                                     | The exact node's id.                                                                                                                                                                                                                        |
| `BZ_HUB_NODE_NAME`                                   | The node's name.                                                                                                                                                                                                                            |
| `BZ_HUB_EPOCH`                                       | The current attempt's epoch, as a string.                                                                                                                                                                                                   |
| `BZ_HUB_BASE_BRANCH`                                 | The branch the chunk's work lands against.                                                                                                                                                                                                  |
| `BZ_HUB_GIT_COMMITS`                                 | A JSON list of `{repo, branch, commit}` — the chunk's latest commit-pointer artifacts.                                                                                                                                                      |
| `BZ_HUB_ARTIFACT_NAMES`                              | A JSON list of artifact names already recorded for this node — a script's own re-run-skip input, alongside the executor's step-level skip.                                                                                                  |
| `BZ_HUB_MARKER_CALLBACK_URL`                         | `POST {name, content}` records a marker mid-run, authorized by `BZ_HUB_MARKER_TOKEN` below; wrapped by `blizzard hub record-marker NAME [CONTENT]`. A non-2xx response is fatal — the script must raise rather than swallow it and proceed. |
| `BZ_HUB_MARKER_TOKEN`                                | The capability token authorizing that POST: minted per `(chunk, node, epoch)` before this node visit's steps run, sent back as the `X-Blizzard-Marker-Token` header, and revoked once the visit ends.                                       |
| `BZ_FORGE_URL` / `BZ_FORGE_TOKEN` / `BZ_FORGE_OWNER` | The hub's own configured forge credential — present only when the hub is configured with one.                                                                                                                                               |

Beyond these keys a step inherits the hub daemon's own environment, with one strengthened guarantee: the executor
prepends the hub interpreter's own bin directory to `PATH`, so a bare `python3` in a `run:` command always resolves to
the interpreter the hub itself runs under — the one that can import `blizzard` — regardless of how the daemon was
launched (a systemd unit invoking the venv binary by absolute path carries no venv on its inherited `PATH`).

**Why.** A `run:` step is an ordinary subprocess with no access to the hub's domain objects; naming the whole env here
means a graph author never guesses at an undocumented field, and a reviewer can tell a script reading anything else is
reading nothing.

**Detect.** A `run:` script referencing an env var not in this table; a script hardcoding a forge URL or token instead
of reading the injected credential; a marker-write POST sent with no `BZ_HUB_MARKER_TOKEN` header at all; a
`record_marker`-style closure whose POST result is never checked — the discarded-response shape a marker write used to
take, where a dropped or unauthorized write was swallowed and the script proceeded to report success anyway.

**Do.** `land_default.py` reads `BZ_HUB_GIT_COMMITS`/`BZ_HUB_ARTIFACT_NAMES` to compute which repos still need landing
and `BZ_FORGE_URL`/`BZ_FORGE_TOKEN`/`BZ_FORGE_OWNER` to talk to the forge directly — no forge seam, by design
(`bzh:deterministic-shell` in [../../architecture/system-shape.md](../../architecture/system-shape.md)): this script
*is* the policy. `land_common.MarkerWriter` (the one marker channel every land script holds, as `LandRun.markers`)
treats any non-2xx as fatal, raising rather than returning, so a merge can never land with no durable record of it.

**Don't.** A script assuming a field this table doesn't list — there is nothing else in its environment to read. A
script that posts the marker write and moves on without inspecting the response — a non-2xx there means the write never
happened, and proceeding to print a success choice anyway is exactly the shape issue #230 closed.
