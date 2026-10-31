# The branch name, declared based on the project's guidance (`bzh:branch-name`)

**Rule.** Told to name a chunk's branch, take the Conventional Commits type of the chunk's lead change as the prefix,
then `/`, then a short kebab-case slug derived from the work item: `fix/<slug>` for a bug fix, `feat/<slug>` for a
feature. The type list is the workspace's contributing conventions (`workspace:/context/project/contributing.md`); this
rule restates none of it. One name serves every repo the chunk touches. A chunk of mixed types takes the most
significant: a feature over a fix over the rest. A release-line patch branch (`patch/X.Y/<slug>`) is the operator's
workflow, never a name a fleet node chooses.

**Why.** The prefix tells a reader what the branch carries before they open it, and one name across repos lets every
later node find the work by the name alone.
