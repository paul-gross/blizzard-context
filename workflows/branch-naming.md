# The branch name, declared based on the project's guidance (`bzh:branch-name`)

**Rule.** Told to name a chunk's branch, take the Conventional Commits type of the chunk's lead change as the prefix,
then `/`, then a short kebab-case slug derived from the work item. The type list is the workspace's contributing
conventions (`workspace:/context/project/contributing.md`); this rule restates none of it. One name serves every repo
the chunk touches. A chunk of mixed types takes the most significant: a feature over a fix over the rest. A release-line
patch branch (`patch/X.Y/<slug>`) and a `hotfix/<slug>` branch, the lint-only lane into `master`, are the operator's
workflow, never a name a fleet node chooses.

**Why.** The prefix tells a reader what the branch carries before they open it, and one name across repos lets every
later node find the work by the name alone.

**Detect.** A declared branch not of the form `<type>/<slug>` with `<type>` a Conventional Commits type, or a chunk
whose repos carry different branch names.

**Do.** `fix/<slug>` for a bug fix and `feat/<slug>` for a feature: `feat/cadence-anchor` for a feature that also fixes
a bug, declared under that one name in every repo the chunk touches.

**Don't.** `paul/cadence-anchor`, `feature/cadence-anchor`, `fix-cadence-anchor`, or `patch/0.4/cadence-anchor` from a
node; nor `feat/cadence-anchor` in one repo and `fix/cadence-anchor` in another repo of the same chunk.
