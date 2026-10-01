# Artifact contents

What an artifact may and may not carry. A spoke of the [artifacts hub](../artifacts.md); the rule follows the slot
skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Never code (`bzh:never-code`)

**Rule.** Agents attach references to work, never the work: the hub validates two kinds of artifact — a commit pointer
and a finding — and stores every other asset as agent-authored content, which its consumer reads as such. Never-code is
guidance that prompts and authored prose carry, not a content check the hub runs.

**Why.** The forge already durably owns code, so a pointer keeps the hub small and safe to centralize and expose to the
board. The hub validates only what has a required structure; policing free-form content would need a scanner that cannot
tell a quoted snippet from a diff. Transcripts earn their exception because what the agent actually did exists nowhere
else once a runner rotates its session files, and the caps and permission gate keep that exception from reintroducing
the size and exposure the rule prevents.

**Exception.** Transcripts, only through the transcript lane: the hub retains normalized turn slices of an agent session
— never files, diffs, or patches — bounded by the lane's per-record, per-chunk, and per-runner-day caps and readable
only under the transcript-read permission.

**Scope.** The validated kinds, and what each check covers:

- A commit pointer (`git_commit`) is refused unless it names a repository, a branch free of `:`, and a full lowercase
  40- or 64-hex commit hash; the forge is optional.
- A finding — the garden finding delta and the review finding delta — is refused when malformed, foreign-scoped,
  duplicated, or carrying an empty `class`, `locus`, or `summary`; `class` is indexed and never interpreted.

Every other asset, a worker node's included, is stored as submitted. A graph's `artifacts:` declaration is authored
definition text, the same class as an inlined `prompt:`, and always the asset kind. Hub-command output is recorded as
produced. A hub-owned work item's title and body are held at the hub because the hub is that item's source
([chunk](../work/chunk.md) §Work refs); what the rule bars is a foreign source's item contents copied to the hub instead
of read through it.

**Detect.**

- A validated kind accepted without its validation.
- A hub schema or lane designed to hold code or diffs; a foreign work source's item contents copied to the hub rather
  than read through.
- Transcript content given a designed path outside the lane — uncapped, unpermissioned, or attached to something other
  than a segment.
- A prompt or graph's authored text that directs an agent to attach a diff or transcript.

**Do.** Push the branch to the forge, then submit the repository, branch, and commit hash as the pointer artifact; write
assets as prose, and quote a snippet only where it makes a point; let the transcript lane carry conversation, on its own
caps.

**Don't.**

- Directing an agent, in a prompt or graph, to attach a diff or the worker's transcript as an asset "for review
  convenience".
- Declaring `artifacts: {fix: ./fix.diff}` naming a diff as a graph's baked-in content.
