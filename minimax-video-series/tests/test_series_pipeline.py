from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import h3_prompt as h3  # noqa: E402
import series_pipeline as pipeline  # noqa: E402


def cfg() -> dict:
    return {
        "series": {"slug": "test", "output_subdir": "video/test"},
        "runtime": h3.normalize_runtime({
            "duration_seconds": 8, "aspect_ratio": "4:5", "quality": "preview", "fps": 24, "steps": 4,
        }),
        "models": {
            "unet": "unet.safetensors", "text_encoder": "clip.safetensors",
            "video_vae": "video.safetensors", "audio_vae": "audio.safetensors",
        },
        "style_lock": "Watercolor animation remains stable.",
        "speakers": {},
    }


def chapter(mode: str, last_frame: str | None = None) -> dict:
    value = {
        "number": 1, "title": "Test", "mode": mode,
        "prompt": "One seed opens and settles into a stable tableau.",
        "audio_prompt": "A faint shell crack is audible in a quiet room.",
        "music_prompt": "N/A", "seed": 7,
    }
    if last_frame:
        value["last_frame"] = last_frame
    return value


class GraphModeTests(unittest.TestCase):
    def test_t2va_uses_no_keyframes(self) -> None:
        graph = pipeline.graph(cfg(), chapter("t2va"), None, None)
        self.assertNotIn("1", graph)
        self.assertNotIn("2", graph)
        self.assertNotIn("first_frame", graph["104"]["inputs"])
        self.assertNotIn("last_frame", graph["104"]["inputs"])

    def test_i2va_uses_first_keyframe(self) -> None:
        graph = pipeline.graph(cfg(), chapter("i2va"), "first.png", None)
        self.assertEqual(graph["104"]["inputs"]["first_frame"], ["1", 0])
        self.assertNotIn("last_frame", graph["104"]["inputs"])

    def test_fl2va_uses_both_keyframes(self) -> None:
        graph = pipeline.graph(cfg(), chapter("fl2va", "last.png"), "first.png", "last.png")
        self.assertEqual(graph["104"]["inputs"]["first_frame"], ["1", 0])
        self.assertEqual(graph["104"]["inputs"]["last_frame"], ["2", 0])

    def test_l2va_uses_only_last_keyframe(self) -> None:
        graph = pipeline.graph(cfg(), chapter("l2va", "last.png"), None, "last.png")
        self.assertNotIn("first_frame", graph["104"]["inputs"])
        self.assertEqual(graph["104"]["inputs"]["last_frame"], ["2", 0])


if __name__ == "__main__":
    unittest.main()
