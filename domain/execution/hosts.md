# Hosts

The machine a tenant's runners live on: the host, its workspaces and their shared environments, the bindings that place
a runner's projects in them, and the subscriptions its runners spend. Spoke of the [execution hub](../execution.md); the
invariant below is written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## The host

A **host** is the one presence of blizzard on a machine. It owns the machine's workspaces and the subscriptions the
operator pays for, and runs as many runners as the operator declares. Each runner is still the unit the hub grants work
to: it claims, holds, and lands its own chunks under its own identity and its own brakes, exactly as a runner does
([./responsibilities.md](./responsibilities.md)). A runner that cannot work — a credential the hub refuses, an identity
that is not its own, a hub that no longer holds it under this host or holds it in another tenant, or a version the hub's
window does not admit — stops alone, and its neighbours carry on; it resumes once that is put right, with nothing lost.
A hub that cannot be reached changes no runner's standing.

A host is a record of its tenant at the hub, beside its runners:

- **Its identity.** The hub mints its id when an operator adds it; the id never changes and is never reused. Its name is
  for people to read, unique among the tenant's hosts that are not retired, so an add naming a taken one is refused.
- **Its own credential.** The host's credential lets it describe the machine — its workspaces, its subscriptions, where
  its panel is reached — report its subscriptions' usage, sign the operator in to its panel, and add or retire runners
  under itself. It claims no work and acts as none of its runners, and no runner's credential acts as the host. A host
  acts only on the runners it holds. It is revoked and re-issued the way a runner's is
  ([./retirement.md](./retirement.md) §Token revocation).
- **One tenant, for life.** A host serves the tenant it was added in, and every runner it adds is born there. Nothing
  moves a host between tenants: its operator retires it and adds another.
- **Its report is never refused.** The host describes itself on every contact, and the hub records what arrives; a name
  another live host holds is not recorded, and the host keeps the one it had.

A runner stands under at most one host. Adding a runner under a host — whether the host asks for it under its own
credential or an operator asks from a session — gives it its id there, in the host's tenant. An existing runner can be
**adopted** into a host, and **released** from it back to standing alone, keeping its id and its credential either way;
adoption refuses a retired runner, one already under a host, and one the tenant does not hold, which it answers as
unknown. A runner released from a host that still runs it stops there, as one the hub no longer holds.

A host the hub does not hold runs exactly one runner, which stands alone at the hub and reports its own subscriptions,
as any runner with no host does ([./responsibilities.md](./responsibilities.md)).

**Retiring a host** revokes its credential and retires every runner under it, each as a runner's own retirement does
([./retirement.md](./retirement.md)): refused while any of them holds a chunk, unless forced, which releases them.
Retiring a host is final — a retired host is never enrolled again — and repeating it finishes retiring any runner it
left unretired.

## Workspaces

A **workspace** is a place on the host where work happens: its environments and the standing prompt its workers are
primed with. It is the host's, not any runner's, and may serve any number of projects and runners at once. What its
environments hold — whether they already carry every repository a project links, or fetch one when a chunk first needs
it — is the business of whatever provides the workspace; binding a project to it checks none of it.

Each workspace has one pool of environments, shared by every binding to it, whichever runner holds the binding, and the
host arbitrates it; two workspaces are two pools, even when they share one place on the machine. An environment returns
to the pool only when the claim holding it releases it ([./acquisition.md](./acquisition.md) §Giving tenure back).

## An environment is held by one claim across the host (`bzh:environment-held-once`)

**Rule.** At most one claim holds an environment of a workspace at a time, whichever of the host's runners holds that
claim; a runner that has stopped working keeps the environments its claims hold, and none is handed to a neighbour until
its claim releases it.

**Why.** Two claims in one environment overwrite each other's work, and no runner sees another's claims; only the host,
which holds every runner's claims together, can arbitrate the pool.

**Detect.**

- An environment two claims hold at once, of one runner or of two.
- A runner's acquisition that consults only its own claims when choosing a free environment.
- A stopped runner's held environments offered to another runner while its chunks still hold them.

**Do.** Two runners bind projects to one workspace of ten environments; each claim takes a free one, and a claim that
finds none free waits for one.

**Don't.** Free a stopped runner's environments for its neighbours because nothing is working in them.

**See also.** [./claim-vocabulary.md](./claim-vocabulary.md) — the environment as an operator reads it;
[../../architecture/crash-correctness.md](../../architecture/crash-correctness.md) `bzh:invariant-checker` — the
invariant it audits after every crash.

## Bindings

A runner **binds** each project it serves to exactly one workspace of its host. A chunk belongs to one project, so the
runner claiming it already knows the one workspace its work will happen in; the route locates it
([./acquisition.md](./acquisition.md) §The route). A runner's bindings are its declaration of the projects it serves
([../projects.md](../projects.md) §Runners serve the projects they declare).

- **One count of agents, shared.** A runner has a single count of agents, shared by every one of its bindings; a binding
  fixes only the workspace its project runs in. Any free agent works whichever project the hub's ready queue ranks next
  among those the runner can take, so the queue's order alone decides which project an agent serves and a full project
  never stands in front of another's work.
- **Agents are not environments.** The count is separate from how many environments a workspace holds: an agent whose
  next project's workspace has no free environment claims only as one frees, and the runner looks to the projects whose
  workspaces have one.
- **The workspace is fixed for the chunk's tenure.** Recovery, release, and resume work in the workspace the chunk was
  claimed through; a binding changed later affects only the next claim.
- **One project, one binding.** Two of a runner's bindings that resolve to the same project leave the runner claiming
  nothing until one is removed.
- **Checked against the host, never refused.** A binding naming a workspace its host has not described, or a runner
  spending a subscription outside its host's roster, is flagged rather than refused. The hub offers no work through a
  flagged binding, and none at all to a runner whose subscription is flagged.

## Subscriptions

A **subscription** is a plan the operator pays for, declared once on the host. Any number of the host's runners may
spend one; a runner spends at most one, and a runner paid for some other way spends none and works exactly as well.
Naming a subscription is the operator's word about which plan pays for a runner's work, not a wire blizzard runs:
blizzard never hands a worker a plan's credentials, and a runner's harnesses constrain nothing about which plan it
names.

The host samples each subscription once, however many runners spend it — one that no runner spends included — and
reports it to the hub once, as the host's. The host's entry shows each subscription once, naming the runners spending
it, by the same rules a runner's entry follows ([./responsibilities.md](./responsibilities.md)); a runner's own entry
shows the usage of the subscription it spends, and nothing for a runner spending none. An exhausted subscription holds
back every runner spending it and no other — `bzh:subscription-floor-reach`, owned by
[./throttling.md](./throttling.md).
