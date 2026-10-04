# Asks

A worker needing input mid-step asks a durable question; the chunk parks `waiting_on_human` until someone answers. Spoke
of the human-entry hub, [../humans.md](../humans.md).

A question is free-form or carries options, which a board or bot renders as buttons. The reap clock stops while a
question is open and restarts when the answer's resume runs.

A worker may ask on any lease still open, an attempt parked or backing off included. An ask that has not yet reached the
hub is superseded by a newer ask on the same lease: only the newest reads as open.

## Answering

Exactly one answer ever exists — the first write wins — and later answerers are shown who won and what they said.
Answering resumes the dormant agent session with the answer delivered into it. The answer stays readable to every later
session on the chunk, and binds them: none asks again what a person already decided, or contradicts it. An answer is
refused once the chunk has ended (`stopped` or `done`).

Answered and delivered are distinct derived states: a person decided, versus the resume ran and the agent heard. A
question row surfaces both, so the answerer sees the return trip rather than inferring it from the chunk moving. A
delivery is refused unless the question is answered, belongs to the chunk it is reported for, and was not superseded by
a restart; a repeated delivery is a no-op.

## What an operator's restart does

An operator's restart ([../work/restart.md](../work/restart.md)) consumes an open question: the asking step is gone, so
a fixed system answer marks it superseded — an ordinary answer write, so an earlier human answer still wins. No return
trip follows — the restart preempted the session that would have heard it — so the question stays answered but never
delivered.
