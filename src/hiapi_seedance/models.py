"""Typed response models for the HiAPI Seedance SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

TERMINAL_STATUSES = frozenset({"success", "fail"})


@dataclass
class Output:
    url: str
    type: str = ""
    expire_at: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Output:
        return cls(
            url=str(data.get("url", "")),
            type=str(data.get("type", "")),
            expire_at=data.get("expireAt"),
            raw=data,
        )


@dataclass
class TaskError:
    code: Optional[str] = None
    message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskError:
        return cls(code=data.get("code"), message=data.get("message"), raw=data)


@dataclass
class CreatedTask:
    task_id: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CreatedTask:
        return cls(task_id=str(data.get("taskId", "")), raw=data)


@dataclass
class Task:
    task_id: str
    model: str
    status: str
    output: List[Output] = field(default_factory=list)
    error: Optional[TaskError] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES

    @property
    def succeeded(self) -> bool:
        return self.status == "success"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        outputs = [
            Output.from_dict(item)
            for item in (data.get("output") or [])
            if isinstance(item, dict)
        ]
        err = data.get("error")
        return cls(
            task_id=str(data.get("taskId", "")),
            model=str(data.get("model", "")),
            status=str(data.get("status", "")),
            output=outputs,
            error=TaskError.from_dict(err) if isinstance(err, dict) else None,
            raw=data,
        )
