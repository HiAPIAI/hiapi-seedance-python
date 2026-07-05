import json

import pytest
from _server import sequence

from hiapi_seedance import PollTimeout, Seedance, TaskFailed

OK_CREATE = (200, {"code": 200, "message": "success", "data": {"taskId": "tk-seedance"}})


def detail(status, **extra):
    data = {"taskId": "tk-seedance", "model": "seedance-2-5", "status": status}
    data.update(extra)
    return (200, {"code": 200, "message": "success", "data": data})


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("HIAPI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="HIAPI_API_KEY"):
        Seedance()


def test_text_to_video_posts_seedance_task(client, server):
    server.set_responder(lambda *a: OK_CREATE)

    created = client.text_to_video(
        prompt="A one-take product film",
        duration=30,
        aspect_ratio="16:9",
        resolution="1080p",
        generate_audio=True,
        wait=False,
    )

    assert created.task_id == "tk-seedance"
    req = server.requests[-1]
    assert req["method"] == "POST"
    assert req["path"] == "/v1/tasks"
    assert req["headers"]["Authorization"] == "Bearer sk-test"
    assert json.loads(req["body"]) == {
        "model": "seedance-2-5",
        "input": {
            "prompt": "A one-take product film",
            "duration": 30,
            "aspect_ratio": "16:9",
            "resolution": "1080p",
            "generate_audio": True,
        },
    }


def test_image_to_video_sends_reference_images(client, server):
    server.set_responder(lambda *a: OK_CREATE)

    client.image_to_video(
        prompt="Animate the hero frame",
        image_urls=["https://example.com/hero.png", "asset://uploaded-frame"],
        duration=12,
        wait=False,
    )

    body = json.loads(server.requests[-1]["body"])
    assert body["model"] == "seedance-2-5"
    assert body["input"]["prompt"] == "Animate the hero frame"
    assert body["input"]["reference_image_urls"] == [
        "https://example.com/hero.png",
        "asset://uploaded-frame",
    ]
    assert body["input"]["duration"] == 12


def test_video_edit_sends_video_and_image_references(client, server):
    server.set_responder(lambda *a: OK_CREATE)

    client.video_edit(
        prompt="Keep motion, add a blue energy bow",
        video_urls=["https://example.com/source.mp4"],
        image_urls=["https://example.com/bow.png"],
        wait=False,
    )

    body = json.loads(server.requests[-1]["body"])
    assert body["input"]["reference_video_urls"] == ["https://example.com/source.mp4"]
    assert body["input"]["reference_image_urls"] == ["https://example.com/bow.png"]


def test_wait_true_polls_until_success(client, server):
    server.set_responder(
        sequence(
            [
                OK_CREATE,
                detail("queued"),
                detail(
                    "success",
                    output=[{"url": "https://cdn.example.com/out.mp4", "type": "video"}],
                ),
            ]
        )
    )

    task = client.text_to_video(
        prompt="A scene",
        wait=True,
        poll_interval=0.01,
        timeout=1.0,
    )

    assert task.status == "success"
    assert task.output[0].url == "https://cdn.example.com/out.mp4"
    assert [r["method"] for r in server.requests] == ["POST", "GET", "GET"]


def test_wait_raises_task_failed(client, server):
    server.set_responder(lambda *a: detail("fail", error={"code": "TASK_FAILED", "message": "bad"}))

    with pytest.raises(TaskFailed) as exc:
        client.wait("tk-seedance", poll_interval=0.01, timeout=1.0)

    assert exc.value.task.status == "fail"
    assert exc.value.code == "TASK_FAILED"


def test_wait_times_out(client, server):
    server.set_responder(lambda *a: detail("handling"))

    with pytest.raises(PollTimeout):
        client.wait("tk-seedance", poll_interval=0.01, timeout=0.03)
