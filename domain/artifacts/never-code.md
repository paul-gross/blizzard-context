# Never code (`bzh:never-code`)

The one enforceable invariant over what an artifact may carry. Spoke of the [artifacts hub](../artifacts.md).

**Rule.** The hub stores **references** to work, never the work: a commit pointer is the closest any hub-side model gets
to code. Transcripts are the one deliberate exception, and only through the **transcript lane**: the hub retains
normalized turn slices of an agent session — never files, diffs, or patches — bounded by the lane's own per-record,
per-chunk, and per-runner-day caps, and readable only under the transcript-read permission. No *artifact* carries either
one.

**Why.** The forge is already the durable owner of code, so a hub holding only references stays small, safe to
centralize, and safe to expose to the board. Transcripts earn their exception because the thing an operator most needs
to see — what the agent actually did — exists nowhere else once a runner's machine rotates its session files; the caps
and the permission gate are what keep that exception from reintroducing the size and exposure the rule exists to
prevent.

**Scope.** A graph's `artifacts:` declaration is authored definition text, not work product — the same class of thing as
an inlined `prompt:`, prose the graph mint already stores. The rule is not engaged by baking it in, but the boundary
still binds: the *name* "artifact" invites treating a diff or a generated patch as declarable content, and that is
exactly the work-product this rule bars.

**Detect.** A design or schema persisting file contents, diffs, or patches at the hub; an artifact carrying code or a
transcript instead of a pointer to it; a work item's contents stored rather than read through; transcript content
reaching the hub **outside** the lane — uncapped, unpermissioned, or attached to something other than a segment; a
graph's `artifacts:` entry holding a diff, a patch, or other generated output rather than authored prose.

**Do.** Push the branch to the forge, then submit the repository, branch, and commit hash as the pointer artifact. Let
the transcript lane carry conversation, on its own caps.

**Don't.** Attach a diff or the worker's transcript as an asset artifact "for review convenience" — the review reads the
pushed branch, and the conversation is already on the lane. Declare `artifacts: {fix: ./fix.diff}` naming a diff as a
graph's baked-in content — the graph mint stores only what its author wrote, never work a chunk produced.
