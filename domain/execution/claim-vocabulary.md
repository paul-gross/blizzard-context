# Claim vocabulary (`bzh:claim-vocabulary`)

The one operator-facing vocabulary for what a chunk action does to a runner's claim — what UI copy, CLI help, and
operator docs use in place of blizzard's internal terms. Spoke of the [execution hub](../execution.md).

## Why

Route, tenure, lease, epoch, attempt, and holding runner name the same handful of concepts inconsistently across
surfaces, and none of them mean anything to an operator deciding whether an action is safe to click. This set is the
whole of what an operator needs to read a chunk action's consequence, no more and no less;
[`../../standards/operator-vocabulary.md`](../../standards/operator-vocabulary.md) (`bzh:operator-vocabulary`) binds
operator-facing copy to it.

## Terms

| Term                  | Meaning                                                                                                                                                                                                                                                                                                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claim**             | A runner's exclusive ownership of a chunk, sticky across nodes ([`./acquisition.md`](./acquisition.md)).                                                                                                                                                                                                                                                                    |
| **Keep the claim**    | The runner still owns the chunk: pause ([`./pause.md`](./pause.md)), reap-retry or the runner's own requeue ([`./recovery.md`](./recovery.md)), a restart — across graphs included — or a migration landing on a hub-executed node ([`./acquisition.md`](./acquisition.md) — Giving tenure back), or waiting on a question or gate.                                         |
| **Release the claim** | The runner gives the chunk up: detach, the hub's requeue of an escalated chunk, a migration that re-queues the chunk onto another graph ([`./acquisition.md`](./acquisition.md) — Giving tenure back), or stop or complete.                                                                                                                                                 |
| **Environment**       | The worktrees a claim brings, acquired by the runner ([`./responsibilities.md`](./responsibilities.md)); kept and released with the claim, and work not yet pushed as a commit does not survive a release ([`./recovery.md`](./recovery.md) — Reassignment). One claim holds an environment at a time: the runner refuses to bind an environment another claim still holds. |
| **Worker**            | The agent process running the current node ([`./envelope.md`](./envelope.md)).                                                                                                                                                                                                                                                                                              |
| **Session**           | The worker's conversation, which can outlive the process ([`./envelope.md`](./envelope.md)).                                                                                                                                                                                                                                                                                |
| **Park**              | Keep the session for a later resume. A per-chunk pause parks by interrupting the worker and killing only a survivor ([`./pause.md`](./pause.md)); waiting on an answer, like a usage-limit pause, parks a worker that has already exited — nothing is interrupted or killed.                                                                                                |
| **End**               | Kill the worker and discard the session. Not resumable — detach, complete, or stop ([`./recovery.md`](./recovery.md)).                                                                                                                                                                                                                                                      |

Which statuses admit a pause is owned by [`../work/statuses.md`](../work/statuses.md) (`paused`).

## Internal terms

Route, lease, epoch, attempt, tenure, and reap are internal terms and do not appear in operator-facing copy —
[`../../standards/operator-vocabulary.md`](../../standards/operator-vocabulary.md)'s `Detect` slot greps for them.
