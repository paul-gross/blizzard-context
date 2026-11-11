# Artifact contents

What an artifact may and may not carry. A spoke of the [artifacts hub](../artifacts.md).

## Never code (`bzh:never-code`)

Agents attach references to work, never the work: the hub validates two kinds of artifact — a commit pointer and a
finding — and stores every other asset as agent-authored content, which its consumer reads as such. Never-code is
guidance that prompts and authored prose carry, not a content check the hub runs.

The forge already durably owns code, so a pointer keeps the hub small and safe to centralize and expose to the board.
The hub validates only what has a required structure; policing free-form content would need a scanner that cannot tell a
quoted snippet from a diff.

What never-code asks in practice: the branch is pushed to the forge first, then the repository, branch, and commit hash
are submitted as the pointer artifact; assets are written as prose, quoting a snippet only where it makes a point; and
conversation travels in the transcript lane, on its own caps. It asks that neither a prompt nor a graph's authored text
direct an agent to attach a diff or the worker's transcript as an asset, and that a graph's `artifacts:` declaration
name no diff as its baked-in content.

The one exception is transcripts, and only through the transcript lane: the hub retains an agent session's turns — tool
calls and their output included, verbatim, so code the agent wrote or read can appear in them — each message and each
tool call's output capped on its own, a tool call's input under no cap of its own but yielding to the per-record cap,
marked truncated when it does, and the whole bounded by the lane's per-record, per-chunk, and per-runner-day caps. They
are readable by a person holding the transcript-read permission, and by the owning runner for its own lease's segments.
Transcript content has no designed path outside the lane — none uncapped, unpermissioned, or attached to anything other
than a segment — and every other artifact kind stays under never-code. Transcripts earn their exception because what the
agent actually did exists nowhere else once a runner rotates its session files; the lane's caps bound how much of it the
hub holds, and its read gates bound who reads it.

The validated kinds, and what each check covers:

- A commit pointer (`git_commit`) is refused unless it names a repository, a branch free of `:`, and a full lowercase
  40- or 64-hex commit hash; the forge is optional.
- A finding — the garden finding delta and the review finding delta — is refused when malformed, duplicated, or carrying
  an empty `class`, `locus`, or `summary`; the garden delta is also refused when foreign-scoped — naming a finding
  outside the run's own scope — where the review delta mints whatever scopes it names
  ([findings-and-proposals](../findings-and-proposals.md) §A finding can also be raised by a delivery lane's review).
  `class` is indexed and never interpreted.

A validated kind is never accepted without its validation, and no hub schema or lane is designed to hold code or diffs.
Every other asset, a worker node's included, is stored as submitted. A graph's `artifacts:` declaration is authored
definition text, the same class as an inlined `prompt:`, and always the asset kind. Hub-command output is recorded as
produced. A hub-owned work item's title and body are held at the hub because the hub is that item's source
([chunk](../work/chunk.md) §Work refs); what never-code bars is a foreign source's item contents copied to the hub
instead of read through it.
