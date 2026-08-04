from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import native_audio_prompt as native  # noqa: E402


def config(item: dict) -> dict:
    return {
        "runtime": {
            "duration_seconds": 8,
            "aspect_ratio": "4:5",
            "quality": "preview",
            "fps": 24,
        },
        "style_lock": "Watercolor animation preserves the same performer from <Picture 1>.",
        "speakers": {"S1": {"description": "The lead singer", "voice": "the supplied exact voice"}},
        "segments": [item],
    }


def segment(**updates) -> dict:
    value = {
        "number": 1,
        "performance": "vocal",
        "speaker_id": "S1",
        "music_role": "soundtrack",
        "prompt": "The singer raises one hand while preserving the established profile.",
        "audio_prompt": "No separate environmental or physical-action sounds are audible above the supplied track.",
        "music_prompt": "Low strings sustain a slow pulse while sparse percussion gradually increases in volume.",
    }
    value.update(updates)
    return value


class NativeAudioPromptTests(unittest.TestCase):
    def test_vocal_without_lyrics_never_invents_words(self) -> None:
        spec = segment()
        prompt = native.H3.compile_native_audio_prompt(config(spec), spec)
        self.assertIn("sings the exact supplied vocal audio from <Audio 1>", prompt)
        self.assertNotIn("<d>", prompt)

    def test_verified_lyrics_are_preserved_exactly(self) -> None:
        exact = "Wait—don't change this; sing it exactly!"
        spec = segment(lyrics={"language": "English", "text": exact})
        prompt = native.H3.compile_native_audio_prompt(config(spec), spec)
        self.assertIn(f"<d>[English] {exact}</d>", prompt)

    def test_instrumental_requires_closed_lips(self) -> None:
        spec = segment(performance="instrumental")
        prompt = native.H3.compile_native_audio_prompt(config(spec), spec)
        self.assertIn("lips remain fully closed for every frame", prompt)
        self.assertNotIn("sings:", prompt)

    def test_diegetic_music_cannot_be_duplicated_as_score(self) -> None:
        spec = segment(music_role="diegetic-performance")
        errors, _warnings = native.lint_segment(config(spec), spec)
        self.assertTrue(any("non_diegetic_music" in value for value in errors))

    def test_locked_audio_header_and_three_fields(self) -> None:
        spec = segment(performance="instrumental")
        prompt = native.H3.compile_native_audio_prompt(config(spec), spec)
        self.assertTrue(prompt.startswith(
            "Use <Picture 1> as the exact identity, wardrobe, style, and scene reference. "
            "Use <Audio 1> as the exact performance timeline.\n\n"
        ))
        self.assertEqual(prompt.count("integrated_multimodal_description:"), 1)
        self.assertEqual(prompt.count("overall_soundscape:"), 1)
        self.assertEqual(prompt.count("non_diegetic_music:"), 1)


if __name__ == "__main__":
    unittest.main()
