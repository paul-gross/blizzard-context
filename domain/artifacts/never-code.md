# Artifact contents

What an artifact may and may not carry. A spoke of the [artifacts hub](../artifacts.md); the rule follows the slot
skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Never code (`bzh:never-code`)

**Rule.** The hub stores references to work, never the work — a commit pointer is the closest any hub-side model gets to
code.

**Why.** The forge already durably owns code, so a reference-only hub stays small, safe to centralize, and safe to
expose to the board. Transcripts earn their exception because what the agent actually did exists nowhere else once a
runner rotates its session files, and the caps and permission gate keep that exception from reintroducing the size and
exposure the rule prevents.

**Exception.** Transcripts, only through the transcript lane: the hub retains normalized turn slices of an agent session
— never files, diffs, or patches — bounded by the lane's per-record, per-chunk, and per-runner-day caps and readable
only under the transcript-read permission. No artifact carries code or a transcript.

**Scope.** A graph's `artifacts:` declaration is authored definition text, the same class as an inlined `prompt:` —
baking it in does not engage the rule; declaring a diff or generated patch there is exactly the work-product the rule
bars.

**Detect.**

- A design or schema persisting file contents, diffs, or patches at the hub; an artifact carrying code or a transcript
  instead of a pointer to it; a work item's contents stored rather than read through.
- Transcript content reaching the hub outside the lane — uncapped, unpermissioned, or attached to something other than a
  segment; a graph's `artifacts:` entry holding a diff, a patch, or other generated output rather than authored prose.

**Do.** Push the branch to the forge, then submit the repository, branch, and commit hash as the pointer artifact; let
the transcript lane carry conversation, on its own caps.

**Don't.**

- Attaching a diff or the worker's transcript as an asset "for review convenience".
- Declaring `artifacts: {fix: ./fix.diff}` naming a diff as a graph's baked-in content.
