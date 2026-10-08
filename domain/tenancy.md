# Tenancy

A **tenant** is a wall around one fleet's world on a hub: its graphs, projects, work sources, repositories, secrets,
chunks, findings, proposals, runners, and the record of everything that happened to them. Everything a hub holds for a
fleet belongs to exactly one tenant, and nothing crosses from one tenant into another. People enter a tenant through a
**membership**, and arrive only by **invitation**; **hub administrators** stand above every tenant. Part of the
[domain model](./index.md).

## The wall

Every read, write, queue operation, and live stream acts within one tenant. A record of another tenant cannot be reached
by any means, its id included: asking for it answers as if it did not exist, never that it is forbidden. What a tenant
chooses a name for — a graph, a project, a source, a repository, a secret, a scope, a routine — is unique within that
tenant only, so two tenants never collide on a name neither knows the other holds.

A project is not a second wall inside the tenant: it is a lens over the tenant's state ([projects.md](./projects.md)).
The tenant is the only boundary.

## A tenant's id and name

A tenant has an id and a name, each with one job:

- **The id** is the tenant's identity. It never changes and is never reused, even after the tenant is deleted, and it is
  the only way anything names a tenant — every request, command, credential, and link.
- **The name** is for people to read. It is unique nowhere, so two tenants may share one, and nothing looks a tenant up
  by it; renaming a tenant breaks nothing and leaves nothing to redirect.

## Memberships and roles

A person signs in to the hub once, as one identity, however many tenants they belong to. A membership grants that person
one role in one tenant — `guest`, `contributor`, or `admin` — and the role means what it means only in that tenant, so
the same person can administer one tenant and only watch another.

- **The sign-in remembers no tenant.** Each act names the tenant it acts within and is checked against the person's
  memberships, so two windows can hold two tenants without disturbing each other.
- **One membership settles it.** A person who holds exactly one membership is never asked to choose and never sees a
  tenant named. A person who holds several and names none is refused, and told which tenants they may name.
- **No membership, no access.** A person whose last membership is revoked is still recognized at sign-in, sees nothing
  of any tenant, and is told to reach out to their administrator.
- **Machines never choose.** A runner belongs to exactly one tenant, the one it was added in, for its whole life; its
  credential settles the tenant of everything it does.

A tenant's `admin` members manage who belongs to it: they invite people, change members' roles, revoke memberships, and
may make other members admins. They reach nothing beyond their tenant.

- **Nobody changes their own role.**
- **A tenant keeps an admin.** Once a tenant has an `admin` member, revoking or demoting its last one is refused.

## Hub administrators

Hub administrators stand above every tenant. They alone create, rename, and delete tenants, and they may grant a
membership in any tenant, which is how a tenant gets its first admin. Standing above every tenant is not seeing inside
one: a hub administrator reads a tenant's state only through a membership of their own, like anyone else. The hub's own
occurrences — its startup, its migrations, a tenant's teardown, its exports' failures — belong to no tenant, and only
hub administrators read them.

- **Only a hub administrator makes another.** No tenant role reaches the hub administrator role, and no tenant admin can
  grant it.
- **There is always one.** Revoking the last hub administrator is refused, so a hub is never left with nobody able to
  create a tenant or grant the role again.
- **The first comes from configuration.** The person whose address the hub's configuration names becomes a hub
  administrator when they sign in, invited or not. Naming a further address later makes that person an additional hub
  administrator on their sign-in; configuration never revokes anyone, and removing the address from it does nothing.
- **The first one is let into the first tenant.** When that first claim happens on a hub whose only tenant has no admin
  yet, the person also becomes that tenant's admin, so whoever sets up a fresh hub is not locked out of the only world
  it holds.

## Invitations

The hub is invite-only: signing in proves who a person is and never lets them in. An invitation admits one email address
into one tenant with one role.

- **Who issues one.** A tenant's admins, for their tenant, and a hub administrator, for any tenant. The issuer hands the
  person a link by whatever channel they already use; the hub sends nothing itself.
- **The address must match.** Whatever account the person signs in with must carry the invited address as a verified
  one, so a forwarded link admits nobody else. An account without it is turned away and the invitation stays usable.
- **Used once, and not forever.** An invitation admits at most once, expires, and may be revoked before it is used. An
  expired, revoked, or used invitation admits nobody, and the person is told to ask for a new one.
- **An uninvited stranger leaves no trace.** A first sign-in with no invitation creates nothing, and the person is told
  the hub is invite-only.

Accepting an invitation into a tenant the person already belongs to records it as accepted and leaves their role as it
was. An invitation is the tenant's own record, so it lives and dies with the tenant.

## The default tenant

A hub that was running before tenants existed becomes one tenant named `default`, holding all of its state: every person
a member of it in the role they held, every runner inside it, nothing re-ingested and nothing reconfigured. A fresh hub
starts with an empty `default` tenant. Nothing else sets it apart — its name changes like any other tenant's — and an
operator who never creates a second tenant never needs to notice the concept.

## Deleting a tenant

Deleting a tenant removes everything it owns. The tenant is closed first: from that moment its people and its runners
cannot reach it, nothing more is written into it — by a person, a runner, or the hub's own passes — and its contents are
then removed. Once begun, deletion carries on to the end, a restart included, and the tenant's id is never given to
another. The hub's only tenant cannot be deleted.
