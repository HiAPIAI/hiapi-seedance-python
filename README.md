# HiAPI Seedance Python SDK

Python SDK for **Seedance 2.5 API**, **Seedance text-to-video**, **Seedance image-to-video**, and Seedance video editing through the HiAPI unified task API.

[![PyPI](https://img.shields.io/badge/pip-hiapi--seedance-f97316)](https://pypi.org/project/hiapi-seedance/) [![HiAPI](https://img.shields.io/badge/HiAPI-One%20API%2C%20All%20AI%20Models-111827)](https://www.hiapi.ai/en?utm_source=github&utm_medium=readme&utm_campaign=hiapi-seedance-python) [![Docs](https://img.shields.io/badge/API%20Docs-docs.hiapi.ai-111827)](https://docs.hiapi.ai/?utm_source=github&utm_medium=readme&utm_campaign=hiapi-seedance-python)

Use this SDK when you want a small Python client focused on AI video generation:

- **Seedance 2.5 API access** through HiAPI's `/v1/tasks` endpoint.
- **Text-to-video** with `client.text_to_video(...)`.
- **Image-to-video** with `client.image_to_video(...)`.
- **Video editing** with `client.video_edit(...)`.
- **Async task polling** built in: submit, poll, and read the output URL.
- **Zero runtime dependencies**: standard library only.

## Install

```bash
pip install hiapi-seedance
```

Requires Python 3.8+.

## Quick Start

```python
from hiapi_seedance import Seedance

client = Seedance()  # uses HIAPI_API_KEY

task = client.text_to_video(
    prompt="A 30-second cinematic one-take product film, golden hour, slow dolly in",
    duration=30,
    aspect_ratio="16:9",
    resolution="1080p",
)

print(task.output[0].url)
```

Set your API key:

```bash
export HIAPI_API_KEY="sk-your-hiapi-key"
```

Get a key at [HiAPI](https://www.hiapi.ai/en/register?utm_source=github&utm_medium=readme&utm_campaign=hiapi-seedance-python).

## Text-to-Video

```python
from hiapi_seedance import Seedance

client = Seedance(api_key="sk-...")

task = client.text_to_video(
    prompt=(
        "A one-take AI video prompt: a glass perfume bottle rotates on wet black "
        "stone while sunrise light moves across the surface, macro texture, no text."
    ),
    duration=15,
    aspect_ratio="16:9",
    resolution="1080p",
)

print(task.status, task.output[0].url)
```

## Image-to-Video

```python
task = client.image_to_video(
    prompt="Animate the reference image with a slow push-in, drifting fabric, and warm rim light.",
    image_urls=["https://example.com/first-frame.png"],
    duration=8,
    aspect_ratio="9:16",
)
```

## Video Editing

```python
task = client.video_edit(
    prompt="Keep the original camera movement and timing. Add a blue-white energy bow in the actor's hands.",
    video_urls=["https://example.com/source.mp4"],
    image_urls=["https://example.com/prop-reference.png"],
)
```

## Return Immediately Instead of Waiting

```python
created = client.text_to_video(
    prompt="A fashion film in a desert gallery",
    duration=30,
    wait=False,
)

task = client.wait(created.task_id, poll_interval=3, timeout=900)
print(task.output[0].url)
```

## Raw HiAPI Task Shape

The SDK sends requests to:

```http
POST https://api.hiapi.ai/v1/tasks
Authorization: Bearer $HIAPI_API_KEY
Content-Type: application/json
```

```json
{
  "model": "seedance-2-5",
  "input": {
    "prompt": "A cinematic Seedance 2.5 prompt",
    "duration": 30,
    "aspect_ratio": "16:9",
    "resolution": "1080p"
  }
}
```

You can pass additional model fields as keyword arguments:

```python
task = client.text_to_video(
    prompt="A multilingual typography loop",
    duration=15,
    web_search=False,
    generate_audio=True,
)
```

## Prompt Library

Need production prompts and preview examples? Use the companion prompt library:

- [Seedance 2.5 prompt library](https://github.com/HiAPIAI/awesome-seedance-2-5-prompts)
- [Seedance 2.0 prompt library](https://github.com/HiAPIAI/awesome-seedance-2-0-prompts)

## Model Slug

The default model is `seedance-2-5`. You can override it per client or per call:

```python
client = Seedance(model="seedance-2-5")
task = client.text_to_video(prompt="...", model="seedance-2-0")
```

Use the fallback model while waiting for Seedance 2.5 availability on your account.

## SEO Keywords

Seedance 2.5 API, Seedance Python SDK, Seedance API Python, Seedance text to video API, Seedance image to video API, AI video generation API, text-to-video Python, image-to-video Python, HiAPI Seedance API.

## License

MIT
