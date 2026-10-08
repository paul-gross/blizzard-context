"""Repository pattern: read/write Protocols, an `internal/` adapter, injected error wrapping.

Instantiates bzh:repository-split, bzh:controller-read-only, bzh:dependency-inversion and
bzh:dependency-injection, each of which owns its seam's rationale.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import structlog
from dependency_injector import containers, providers

import some_io_library


# --- Domain types ----------------------------------------------------------

@dataclass
class Thing:
    """Domain object for whatever this repository deals with."""
    id: str
    payload: bytes


class RepoError(Exception):
    """A failed repository operation, with the operation, cwd, exit code and detail it failed with."""
    def __init__(self, message: str, *, operation: str = "", cwd: Path | None = None,
                 exit_code: int | None = None, detail: str = ""):
        super().__init__(message)
        self.operation = operation
        self.cwd = cwd
        self.exit_code = exit_code
        self.detail = detail


# --- Error factory (injected) ---------------------------------------------

class RepoErrorFactory:
    """Translates library exceptions into `RepoError`, one `from_<transport>` method per exception type.

    Each translation logs the failure once, at ERROR, with its fields as key-values.
    """

    def __init__(self, log: structlog.stdlib.BoundLogger) -> None:
        self._log = log

    def from_io(self, exc: Exception, message: str, *,
                cwd: Path | None = None) -> RepoError:
        """Return `exc` as a `RepoError` and log it once at ERROR; the returned error is already logged."""
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
    """Acquires `some_io_library` connections and translates their failures to `RepoError`.

    Generic across entities: it offers no entity-specific operation (bzh:screaming-architecture).
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
        """Open a transaction; only opening it is translated, not failures inside the caller's block."""
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


# --- Public Protocols ---------------------------------------------------

class IReadFooRepository(Protocol):
    """Read-only operations."""

    def get_thing(self, thing_id: str) -> Thing: ...
    def list_things(self, prefix: str) -> list[Thing]: ...


class IWriteFooRepository(IReadFooRepository, Protocol):
    """Adds the writes."""

    def save_thing(self, thing: Thing) -> None: ...
    def delete_thing(self, thing_id: str) -> None: ...


# --- Concrete adapter (lives at <feature>/internal/foo_repository.py in
# production; shown here in one file for the exemplar) ----------------------

class ReadFooRepository:
    """`IReadFooRepository` over `some_io_library`, reached through `RepoConnections`."""

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
        return Thing(id=row.id, payload=row.payload)


class WriteFooRepository(ReadFooRepository):
    """`IWriteFooRepository` over `some_io_library`."""

    def save_thing(self, thing: Thing) -> None:
        with self._connections.begin() as conn:
            conn.execute(("save", thing.id, thing.payload))

    def delete_thing(self, thing_id: str) -> None:
        with self._connections.begin() as conn:
            conn.execute(("delete", thing_id))


# Pyright rejects this return if WriteFooRepository drifts from IWriteFooRepository,
# which extends IReadFooRepository, so one sentinel pins both seams.
def _conforms_write_foo_repository(x: WriteFooRepository) -> IWriteFooRepository:
    return x


# --- DI container binding (lives in container.py in production) -----------

class Container(containers.DeclarativeContainer):
    """Binds `IWriteFooRepository`, which satisfies `IReadFooRepository` too (bzh:controller-read-only)."""

    client = providers.Dependency(instance_of=some_io_library.Client)
    log = providers.Object(structlog.get_logger())
    error_factory = providers.Singleton(RepoErrorFactory, log=log)
    connections = providers.Singleton(RepoConnections, client=client, errors=error_factory)
    foo_repo: providers.Provider[IWriteFooRepository] = providers.Singleton(
        WriteFooRepository, connections=connections,
    )
