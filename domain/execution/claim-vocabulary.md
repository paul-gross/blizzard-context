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

| Term                  | Meaning                                                                                                                                                                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Claim**             | A runner's exclusive ownership of a chunk, sticky across nodes ([`./acquisition.md`](./acquisition.md)).                                                                                                                                                     |
| **Keep the claim**    | The runner still owns the chunk: pause ([`./pause.md`](./pause.md)), restart, reap-retry ([`./recovery.md`](./recovery.md)), or waiting on a question or gate.                                                                                               |
| **Release the claim** | The runner gives the chunk up: detach, requeue, or migration ([`./recovery.md`](./recovery.md)), or stop or complete.                                                                                                                                        |
| **Environment**       | The worktrees a claim brings, acquired by the runner ([`./responsibilities.md`](./responsibilities.md)); kept and released with the claim, and work not yet pushed as a commit does not survive a release ([`./recovery.md`](./recovery.md) — Reassignment). |
| **Worker**            | The agent process running the current node ([`./envelope.md`](./envelope.md)).                                                                                                                                                                               |
| **Session**           | The worker's conversation, which can outlive the process ([`./envelope.md`](./envelope.md)).                                                                                                                                                                 |
| **Park**              | Interrupt the worker, kill only a survivor, keep the session. Resumable — pause ([`./pause.md`](./pause.md)), or waiting on an answer.                                                                                                                       |
| **End**               | Kill the worker and discard the session. Not resumable — detach, complete, or stop ([`./recovery.md`](./recovery.md)).                                                                                                                                       |

Which statuses admit a pause is owned by [`../work/statuses.md`](../work/statuses.md) (`paused`).

## Internal terms

Route, lease, epoch, attempt, tenure, and reap are internal terms and do not appear in operator-facing copy —
[`../../standards/operator-vocabulary.md`](../../standards/operator-vocabulary.md)'s `Detect` slot greps for them.
