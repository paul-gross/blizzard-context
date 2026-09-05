"""Canonical repository-pattern example.

Read this when adding a new repository class or extending an existing one.
The prose here is expository teaching commentary and is not a model of in-tree
comment density or altitude — `bzh:prose-budget` and `bzh:comment-encapsulation`
do not bind exemplar files; write in-tree prose to those rules, not to this file's.
The shape codifies the three seams the blizzard architecture rules require
(architecture/clean-architecture.md, architecture/repository-access.md):

  1. **Protocol seams, I-prefix names, read/write split.** The public callable
     surface is a `Protocol` named `IRead<Foo>Repository` / `IWrite<Foo>Repository`
     (bzh:repository-split). Services depend on the narrowest variant they need
     (bzh:controller-read-only): a controller holds the read Protocol, the domain
     holds the write Protocol. The domain owns these Protocols, the adapter
     implements them (bzh:dependency-inversion) — the arrow points inward.

  2. **`internal/` adapter placement.** Concrete implementations live under an
     `internal/` subpackage (e.g. `<feature>/internal/foo_repository.py`). The
     Protocol file lives at the feature-package root, alongside the service that
     uses it. Anything under `internal/` is package-private and must not be
     imported from outside the feature.

  3. **Factory-injected error wrapping, behind a generic connections seam.**
     Library exceptions are turned into the domain `RepoError` by an injected
     `RepoErrorFactory.from_*` method, not by inline `raise X from Y` at every
     call site. The factory logs once at the wrap site (structlog,
     standards/logging.md) with structured fields, so the reporter and
     dashboard render them without re-parsing. Adapters never hold the
     library client directly: they take an injected `RepoConnections`
     (bzh:dependency-injection) — mirroring `RunnerStoreConnections` /
     `HubStoreConnections` in production, the pattern
     architecture/clean-architecture.md's structural gate holds every
     `hub/store/internal/` and `runner/` adapter to. `RepoConnections` stays
     generic — `connect()`/`begin()`/`all(query)`, never a per-entity method —
     so entity-specific reads and writes live on the one adapter that owns
     that entity, not on the shared seam every adapter takes.

The DI container binds the Write variant where mutations are required and the
Read variant where they aren't (bzh:dependency-injection) — the Protocol type
is the contract, and tests substitute a fake by type.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import structlog

import some_io_library  # the client itself is confined to RepoConnections


# --- Domain types ----------------------------------------------------------

@dataclass
class Thing:
    """Domain object for whatever this repository deals with."""
    id: str
    payload: bytes


class RepoError(Exception):
    """Raised by repository methods to signal a failed operation.

    Carries structured fields populated by RepoErrorFactory at the wrap site.
    Callers depend on this type — never on `some_io_library`'s exceptions.
    """
    def __init__(self, message: str, *, operation: str = "", cwd: Path | None = None,
                 exit_code: int | None = None, detail: str = ""):
        super().__init__(message)
        self.operation = operation
        self.cwd = cwd
        self.exit_code = exit_code
        self.detail = detail


# --- Error factory (injected) ---------------------------------------------

class RepoErrorFactory:
    """The injected error-wrapping seam.

    One `from_<transport>(...)` method per underlying exception type it knows
    how to translate, each called at the boundary where the library exception
    is caught. The factory logs once (structlog, at ERROR) so we never get
    catch-log-rethrow cascades, and constructs a `RepoError` with the
    structured fields populated. Inject the concrete class directly; extract an
    `IRepoErrorFactory` Protocol only when a second factory shape appears.
    """

    def __init__(self, log: structlog.stdlib.BoundLogger) -> None:
        self._log = log

    def from_io(self, exc: Exception, message: str, *,
                cwd: Path | None = None) -> RepoError:
        """Wrap `exc` into a structured `RepoError` and log it once at ERROR.

        This is the single log site for the failure — callers must not log it
        again. Fields go on the event as key-values, not into the message.
        """
        operation = getattr(exc, "operation", "")
        exit_code: int | None = getattr(exc, "exit_code", None)
        detail: str = str(getattr(exc, "detail", "") or "").strip()
        err = RepoError(message, operation=operation, cwd=cwd,
                        exit_code=exit_code, detail=detail)
        self._log.error(message, operation=operation, cwd=str(cwd) if cwd else "",
                        exit_code=exit_code, detail=detail)
        return err


# --- Connections (injected, the only place the library client is held) ----

class RepoConnections:
    """The connection-acquiring collaborator every adapter takes in place of
    the raw `some_io_library` client (bzh:dependency-injection) —
    `connect()`/`begin()`/`all(query)`, generic across every concept the
    feature package adapts. Statement construction and entity-specific
    operations stay on the adapter that owns that entity, never here
    (bzh:screaming-architecture); this seam only acquires and translates.
    Mirrors `RunnerStoreConnections` / `HubStoreConnections` in production,
    including their one real gap: `begin()` wraps only the context manager's
    own creation, not a caller's `with` block, so a write that can collide on
    a business rule — a replay, a uniqueness constraint — still needs its own
    catch inside that block, the same as a `check_and_record`-style method
    catches `IntegrityError` locally rather than relying on this seam.
    """

    def __init__(self, client: "some_io_library.Client", errors: RepoErrorFactory) -> None:
        self._client = client
        self._errors = errors

    def connect(self):
        try:
            return self._client.connect()
        except some_io_library.IOError as exc:
            raise self._errors.from_io(exc, "connect failed") from exc

    def begin(self):
        try:
            return self._client.begin()
        except some_io_library.IOError as exc:
            raise self._errors.from_io(exc, "begin failed") from exc

    def all(self, query) -> list:
        try:
            with self._client.connect() as conn:
                return list(conn.execute(query))
        except some_io_library.IOError as exc:
            raise self._errors.from_io(exc, f"query failed for {query!r}") from exc


# --- Public Protocols (the seam services depend on) -----------------------

class IReadFooRepository(Protocol):
    """Read-only operations. Controllers at the edges depend on this variant."""

    def get_thing(self, thing_id: str) -> Thing: ...
    def list_things(self, prefix: str) -> list[Thing]: ...


class IWriteFooRepository(IReadFooRepository, Protocol):
    """Read-write variant. Only the domain layer depends on this."""

    def save_thing(self, thing: Thing) -> None: ...
    def delete_thing(self, thing_id: str) -> None: ...


# --- Concrete adapter (lives at <feature>/internal/foo_repository.py in
# production; shown here in one file for the exemplar) ----------------------

class ReadFooRepository:
    """Read-only `some_io_library` adapter. Builds its own queries; the client
    itself is reached only through the injected `RepoConnections`."""

    def __init__(self, connections: RepoConnections) -> None:
        self._connections = connections

    def get_thing(self, thing_id: str) -> Thing:
        rows = self._connections.all(("get", thing_id))
        if not rows:
            raise RepoError(f"no such thing {thing_id}", operation="get")
        return self._parse(rows[0])

    def list_things(self, prefix: str) -> list[Thing]:
        rows = self._connections.all(("list", prefix))
        return [self._parse(row) for row in rows]

    @staticmethod
    def _parse(row) -> Thing:
        # Parsing is a private detail of this class — callers see only Thing.
        return Thing(id=row.id, payload=row.payload)


class WriteFooRepository(ReadFooRepository):
    """Read-write adapter. Mutating operations live here; reads inherited."""

    def save_thing(self, thing: Thing) -> None:
        with self._connections.begin() as conn:
            conn.execute(("save", thing.id, thing.payload))

    def delete_thing(self, thing_id: str) -> None:
        with self._connections.begin() as conn:
            conn.execute(("delete", thing_id))


# Typecheck-time Protocol/adapter conformance sentinel. Pyright rejects the
# return if WriteFooRepository drifts from IWriteFooRepository. Lives next to
# the concrete so the Protocol module doesn't import its own adapter. Because
# IWriteFooRepository extends IReadFooRepository, this single sentinel pins
# both seams (bzh:dependency-inversion).
def _conforms_write_foo_repository(x: WriteFooRepository) -> IWriteFooRepository:
    return x


# --- DI container binding (lives in container.py in production) -----------
#
# from dependency_injector import containers, providers
#
# class Container(containers.DeclarativeContainer):
#     error_factory = providers.Singleton(RepoErrorFactory)
#     connections = providers.Singleton(RepoConnections, client=client, errors=error_factory)
#     foo_repo: providers.Provider[IWriteFooRepository] = providers.Singleton(
#         WriteFooRepository, connections=connections,
#     )
#
# Controllers declare their dependency as `IReadFooRepository` — the Singleton
# above satisfies the supertype too, and the type system makes the read-only
# intent visible at the consumer (bzh:controller-read-only).
