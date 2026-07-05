"""Exception hierarchy for hiapi-seedance."""

from __future__ import annotations

from typing import Optional


class SeedanceError(Exception):
    """Base class for all SDK errors."""


class APIError(SeedanceError):
    """The API returned a non-2xx response."""

    def __init__(
        self,
        message: str,
        *,
        status: int,
        error_code: Optional[str] = None,
        body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.error_code = error_code
        self.body = body


class APIConnectionError(SeedanceError):
    """A network error prevented the request from completing."""


class TaskFailed(SeedanceError):
    """A polled task reached terminal status=fail."""

    def __init__(self, task: object) -> None:
        err = getattr(task, "error", None)
        self.code = getattr(err, "code", None)
        self.message = getattr(err, "message", None) or "task failed"
        self.task = task
        super().__init__(f"task {getattr(task, 'task_id', '?')} failed: {self.message}")


class PollTimeout(SeedanceError):
    """The task did not finish within the client-side timeout."""

    def __init__(self, task_id: str, timeout: float) -> None:
        self.task_id = task_id
        self.timeout = timeout
        super().__init__(f"task {task_id} did not finish within {timeout:g}s")
