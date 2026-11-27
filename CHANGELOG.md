# Changelog

## 0.1.1 — 2026-11-27

- Fix: the default model `seedance-2-5` does not exist, so calls without `model=` failed. Each method now defaults to an official Seedance 2.5 ID: `text_to_video` / `create` → `seedance-2.5/text-to-video`, `image_to_video` → `seedance-2.5/image-to-video`, `video_edit` → `seedance-2.5/reference-to-video`. A `model=` passed to the call or the constructor still wins.
- With `seedance-2.5/image-to-video`, `aspect_ratio` only accepts `adaptive`.
- Default base URL is now `https://api.hiapi.sh/v1`; set `HIAPI_BASE_URL` or pass `base_url=` to override. `https://api.hiapi.ai` keeps working during the transition.

## 0.1.0 — 2026-07-05

- Initial release.
