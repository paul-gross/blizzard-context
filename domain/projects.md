# Projects

A **project** is a body of work inside one tenant — `blizzard`, `winter`, `celestial-frontier` — that the hub carries
from the moment its items are ingested, through the runner that claims them and the repositories they land in, to the
garden that tends it. A tenant holds many projects. A project is a lens over the tenant's state, not a wall around it:
the tenant is the only boundary ([tenancy.md](./tenancy.md)). Part of the [domain model](./index.md).

## A project's id, slug, and name

A project carries three things people and machines tell it apart by, and each has one job:

- **The id** is the project's identity. It never changes, and everything that refers to a project — a link, a chunk, a
  runner's declaration — holds the id.
- **The slug** is the handle people type and read: lowercase letters and digits, words joined by single hyphens. It is
  unique within the tenant, so two tenants may each hold the same slug, and it may change at will.
- **The name** is for people to read: free text, unique nowhere, and it may change at will. Nothing looks a project up
  by its name.

Wherever a project is accepted it may be named by its id or its slug; a slug is resolved to the id on arrival, and
nothing past that point holds a slug.

### Former slugs

Changing a project's slug leaves the old slug resolving to that project, so a link or a runner's configuration written
against it keeps working. The old slug keeps resolving until some project of the tenant takes it — another project, or
the one that left it — and from then on it names its new holder. A slug is never both current and former.

A configuration document is the exception. A document that declares a project by a slug some project has moved away from
is refused, naming the project that left it: applying it to that project would rename it back or leave the document and
the hub disagreeing, and the fix is to edit the document.

### A project's color

Every project carries a color, so people can tell its work apart at a glance. The color is a name from a fixed palette,
whose look is the board's to decide, or a custom shade, a `#rrggbb` the hub keeps lowercase and the board may adjust so
it stays legible. Anything else is refused, and the refusal names both forms.

A project created without a color gets the palette color fewest of its tenant's projects hold, with a tie broken at
random; a custom shade counts toward no palette color, and a color is never auto-assigned as a custom shade. The color
is stored once and never recomputed, so it changes only when someone sets it. Every door that creates or edits a project
can set it.

A color never stands for a project on its own: wherever one shows, the project's name is shown with it or carried as its
label.

### Every tenant starts with one

A tenant holds a project with the slug `default` from the moment it exists, so it can ingest, hold a routine, and give a
runner something to serve before anyone configures anything. A hub that was running before projects existed carries its
whole state into that project — its chunks, scopes, routines, findings, and proposals — linked to every work source and
repository it already held, with every runner serving it. Nothing else sets `default` apart: its slug and name change
like any other project's.

A project, once created, stays: there is no retiring one.

## What a project owns, and what it links

A project owns its scopes, routines, findings, and garden proposals, so a scope's slug and a routine's name are unique
within its project, and two projects never collide on the name of a sweep
([routines-and-scopes.md](./routines-and-scopes.md)). A routine's scopes are its own project's, whatever slug it names
([routines-and-scopes.md](./routines-and-scopes.md#what-refuses)), and a run's work is ingested into the routine's
project.

Work sources and repositories are the tenant's, not any project's. A project reaches one only through a link, any number
of projects may link the same record, and a link never makes the record the project's own:

- **A source link** says the project draws from that source. Closing and annotating an item still go through its source,
  whichever project carried the work.
- **A repository link** says the project's chunks may land in that repository, and grants nothing else. A repository no
  project links receives nothing.
- **The built-in hub source** is one list for the whole tenant, linked to every project without being configured, and
  cannot be unlinked. Each item in it belongs to the project it was created in.
- **A project holds no secrets.** A credential belongs to the source or repository that uses it, and a project reaches
  it only by linking that record.

## A chunk belongs to exactly one project

A chunk's project is set once, when its items are ingested, and never changes.

- **Grouping never crosses projects.** The refusal is [work/chunk.md](./work/chunk.md) §Grouping's.
- **An item sits in one project at a time.** An item is held by at most one live chunk, so it belongs to at most one
  project at a time; once that chunk is finished, the item may be ingested again into any project.
- **Dependencies cross projects.** A chunk may wait on a chunk of another project, as it waits on any blocker.
- **Findings follow their chunk.** Which project a finding and a proposal take, and what a proposal may cite, is
  [findings-and-proposals.md](./findings-and-proposals.md)'s.

### Which project an ingest goes into

An ingest that names its project goes into it. One that names none takes the project its sources agree on:

- every configured source among the ingested items is linked to exactly one project, and it is the same one — that
  project is used;
- the built-in hub source sits out of this agreement, because it is linked to every project and says nothing about which
  is meant;
- an ingest of hub items alone goes into the project those items were created in, when they all agree;
- anything else is refused, naming the candidate projects.

Every source the ingest draws on must be linked to the project it goes into; ingest never links a source by itself.

### Where a chunk may land

A chunk lands only in repositories its project links, as the links stand when the landing step begins. A landing into a
repository the project was not given is refused before anything is pushed, naming the repository and the project — a
refusal distinct from landing into a repository the tenant has not configured at all. Landing itself behaves as it does
for any chunk.

## A call that needs a project

Creating something a project owns — a scope, a routine, an operator's garden proposal, a link, a hub item — and finding
a scope or routine by its name each need a project. A call that names none uses the tenant's project when the tenant
holds exactly one; otherwise it is refused, and the refusal lists the tenant's projects. A listing that names no project
reads the whole tenant.

## Runners serve the projects they declare

A runner declares the projects it serves, and the hub offers it only chunks of those projects; a chunk of any other
project is skipped for that runner, never waited on. A runner that serves nothing is unassigned, not starved, and the
board says so.

- **The declaration begins when the runner is added.** Adding a runner may name its projects. Naming none in a tenant
  that holds exactly one project serves that project, so a runner that has never heard of projects is offered work the
  moment it is added; in a tenant of several, it serves nothing until it declares.
- **A runner that says nothing keeps what it had.** A runner that registers without a declaration keeps the one it
  holds; declaring an empty set serves nothing.
- **An entry that names nothing waits.** A declared slug that resolves to no project of the tenant serves nothing, is
  shown on the board as unresolved, and starts serving once a project answers to it.
- **A project counts as served only by a runner that can claim it.** A paused, retired, or version-refused runner, and
  one whose bindings to the project are withheld, serve it in name only: the project reads as unserved until a runner
  that can claim it is live.
- **A runner's agents are shared across its projects.** A runner binds each project it serves to a workspace and has one
  count of agents for all of them ([execution/hosts.md](./execution/hosts.md) §Bindings).

## The lens

Which project a person is looking through belongs to the whole board, not to any one view: it sits beside the tenant,
travels in the link so a shared link opens through the same lens, and every view reads it. The lens is on one project or
on All.

- **Each view decides what the lens means for it.** The board and its events narrow to the project's chunks and the
  counts follow; the runner list narrows to the runners serving the project and the unassigned ones, each still showing
  its claims across the whole tenant; administration narrows sources and repositories to the ones the project links, and
  the change log to the project's changes and the tenant-wide ones.
- **A view the lens does not touch says so.** The tenant's graph library, its members, and its secrets are the tenant's,
  and their views state that the lens does not apply rather than quietly ignoring it.
- **Gardening is per project.** Through a project's lens, gardening is that project's scopes, routines, runs, findings,
  and proposals; through All, it is a doorway into each project's garden, which a tenant with exactly one project skips.
  A link to a gardening record that carries no lens opens the record through its own project's lens.
- **An unknown project opens All.** A link naming a project the tenant does not hold opens the same view through All,
  with a notice.
