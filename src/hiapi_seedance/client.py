"""Seedance-focused client for HiAPI's unified task API."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Union

from ._version import __version__
from .errors import APIConnectionError, APIError, PollTimeout, TaskFailed
from .models import CreatedTask, Task

DEFAULT_BASE_URL = "https://api.hiapi.ai/v1"
DEFAULT_MODEL = "seedance-2-5"
DEFAULT_TIMEOUT = 60.0
DEFAULT_POLL_INTERVAL = 3.0
DEFAULT_WAIT_TIMEOUT = 900.0

UrlList = Union[str, Iterable[str]]


class Seedance:
    """Python SDK for Seedance video generation through HiAPI.

    Args:
        api_key: HiAPI API key. Falls back to ``HIAPI_API_KEY``.
        base_url: HiAPI base URL. Both ``https://api.hiapi.ai`` and
            ``https://api.hiapi.ai/v1`` are accepted.
        model: Default model slug. Defaults to ``seedance-2-5``.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        key = api_key or os.environ.get("HIAPI_API_KEY")
        if not key:
            raise ValueError("missing API key: pass api_key=... or set HIAPI_API_KEY")
        self.api_key = key
        self.base_url = _normalize_base_url(base_url)
        self.model = model
        self.timeout = timeout

    def text_to_video(
        self,
        *,
        prompt: str,
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        generate_audio: Optional[bool] = None,
        model: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        **extra: Any,
    ) -> Union[Task, CreatedTask]:
        """Create a Seedance text-to-video task.

        Set ``wait=False`` to return immediately with ``CreatedTask``.
        """
        input_data = _clean(
            {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "generate_audio": generate_audio,
                **extra,
            }
        )
        return self.create(
            input=input_data,
            model=model,
            callback_url=callback_url,
            wait=wait,
            poll_interval=poll_interval,
            timeout=timeout,
        )

    def image_to_video(
        self,
        *,
        prompt: str,
        image_urls: UrlList,
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        model: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        **extra: Any,
    ) -> Union[Task, CreatedTask]:
        """Create a Seedance image-to-video task with reference images."""
        input_data = _clean(
            {
                "prompt": prompt,
                "reference_image_urls": _as_list(image_urls),
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                **extra,
            }
        )
        return self.create(
            input=input_data,
            model=model,
            callback_url=callback_url,
            wait=wait,
            poll_interval=poll_interval,
            timeout=timeout,
        )

    def video_edit(
        self,
        *,
        prompt: str,
        video_urls: UrlList,
        image_urls: Optional[UrlList] = None,
        model: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        **extra: Any,
    ) -> Union[Task, CreatedTask]:
        """Create a Seedance video-edit task with source video references."""
        input_data = _clean(
            {
                "prompt": prompt,
                "reference_video_urls": _as_list(video_urls),
                "reference_image_urls": _as_list(image_urls) if image_urls else None,
                **extra,
            }
        )
        return self.create(
            input=input_data,
            model=model,
            callback_url=callback_url,
            wait=wait,
            poll_interval=poll_interval,
            timeout=timeout,
        )

    def create(
        self,
        *,
        input: Dict[str, Any],
        model: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = False,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
    ) -> Union[Task, CreatedTask]:
        """Submit a raw HiAPI task for Seedance-compatible inputs."""
        body: Dict[str, Any] = {"model": model or self.model, "input": input}
        if callback_url:
            body["callback"] = {"url": callback_url, "when": "final"}
        env = self._request("POST", "/tasks", body=body)
        created = CreatedTask.from_dict(_data(env))
        if wait:
            return self.wait(created.task_id, poll_interval=poll_interval, timeout=timeout)
        return created

    def retrieve(self, task_id: str) -> Task:
        """Fetch a task by id."""
        env = self._request("GET", "/tasks/" + urllib.parse.quote(task_id, safe=""))
        return Task.from_dict(_data(env))

    def wait(
        self,
        task_id: str,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
    ) -> Task:
        """Poll a task until it succeeds, fails, or times out."""
        if poll_interval <= 0:
            raise ValueError("poll_interval must be > 0")
        if timeout < 0:
            raise ValueError("timeout must be >= 0")

        deadline = time.monotonic() + timeout
        while True:
            task = self.retrieve(task_id)
            if task.status == "success":
                return task
            if task.status == "fail":
                raise TaskFailed(task)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise PollTimeout(task_id, timeout)
            time.sleep(min(poll_interval, remaining))

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self.base_url + path
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": f"hiapi-seedance/{__version__}",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return _decode(response.read(), response.status)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            raise _api_error(exc.code, raw) from None
        except OSError as exc:
            raise APIConnectionError(str(getattr(exc, "reason", exc))) from exc


def _normalize_base_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    return base


def _decode(raw: bytes, status: int) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw.decode("utf-8")) if raw else {}
    except (UnicodeDecodeError, ValueError) as exc:
        raise APIError(str(exc), status=status, body=raw.decode("utf-8", "replace")) from exc
    if not isinstance(parsed, dict):
        raise APIError("expected JSON object response", status=status, body=str(parsed))
    return parsed


def _api_error(status: int, raw: bytes) -> APIError:
    message = f"HTTP {status}"
    error_code = None
    body = raw.decode("utf-8", "replace") if raw else None
    try:
        parsed = json.loads(raw.decode("utf-8")) if raw else {}
        if isinstance(parsed, dict):
            message = str(parsed.get("message") or message)
            error_code = parsed.get("error_code")
    except (UnicodeDecodeError, ValueError):
        pass
    return APIError(message, status=status, error_code=error_code, body=body)


def _data(env: Dict[str, Any]) -> Dict[str, Any]:
    data = env.get("data")
    return data if isinstance(data, dict) else {}


def _clean(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def _as_list(value: UrlList) -> List[str]:
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]
