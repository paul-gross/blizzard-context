# Ask and answer

A worker that needs input mid-step asks a durable question — free-form, or with options a board or bot renders as
buttons — and the chunk parks `waiting_on_human` until someone answers. Spoke of the [human-entry hub](../humans.md).

- **The reap clock stops** while the question is open: a chunk waiting on a person is not stalled.
- **Exactly one answer ever exists.** The first answer wins; later would-be answerers are told who won and what they
  said.
- **The session resumes around the answer** — the dormant agent session continues with the answer delivered into it, and
  the resume restarts the reap clock.
- **An operator's restart consumes an open one.** Forcing the chunk onto a node ([work/restart.md](../work/restart.md))
  answers the question with a fixed system answer saying the step was superseded, since the step that asked it is gone.
  The *write* is an ordinary answer, so the first-write rule above is unchanged: a person who already answered still
  wins. The *return trip* is deliberately never made — the session that would have heard it was preempted in the same
  move, so the question stays answered-and-never-delivered, and that pair is the honest record of what happened to it.
- **The delivery is itself a fact, and the question carries it.** Answered and delivered are distinct derived states:
  answered says a person decided, delivered says the resume actually ran and the agent heard. A question row surfaces
  both, so the return trip is visible to whoever answered rather than inferred from the chunk moving.
