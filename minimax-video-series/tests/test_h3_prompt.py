from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import h3_prompt as h3  # noqa: E402


def config(item: dict, speakers: dict | None = None) -> dict:
    return {
        "runtime": {
            "duration_seconds": 8,
            "aspect_ratio": "4:5",
            "quality": "preview",
            "fps": 24,
        },
        "style_lock": "Watercolor animation preserves the same protagonist and pale palette.",
        "speakers": speakers or {},
        "chapters": [item],
    }


def item(**updates) -> dict:
    value = {
        "number": 7,
        "title": "Manifest-only title",
        "movement": "Manifest-only movement",
        "prompt": "The protagonist opens one folded letter and looks toward the window.",
        "audio_prompt": "Rain taps against the window while the train wheels produce a steady rhythm.",
        "music_prompt": "N/A",
        "seed": 12345,
    }
    value.update(updates)
    return value


class PromptCompilerTests(unittest.TestCase):
    def test_temporal_grid(self) -> None:
        self.assertEqual(h3.snap_frames(10), 243)
        self.assertEqual(h3.snap_frames(15), 362)
        self.assertTrue(h3.is_temporal_grid(362))

    def test_i2va_header_is_exact(self) -> None:
        prompt = h3.compile_standard_prompt(config(item(mode="i2va")), item(mode="i2va"))
        self.assertTrue(prompt.startswith(
            "For the target video, at 0.00 seconds into the target video, "
            "<Picture 1> (from [Shot 1]) is fully referenced.\n\n"
        ))

    def test_fl2va_header_uses_final_shot_and_effective_duration(self) -> None:
        chapter = item(
            mode="fl2va",
            last_frame="ending.png",
            shots=[
                {"action": "She unfolds the letter."},
                {"cut_at": 3.5, "action": "Her reflection crosses the window."},
            ],
        )
        prompt = h3.compile_standard_prompt(config(chapter), chapter)
        expected = (
            "How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with "
            "the 0.00-second mark of the target video; Picture 2 (from Shot 2) aligns with the 8.00-second "
            "mark of the target video."
        )
        self.assertTrue(prompt.startswith(expected + "\n\n"))
        self.assertNotIn("Manifest-only title", prompt)
        self.assertNotIn("Manifest-only movement", prompt)

    def test_l2va_and_t2va_headers(self) -> None:
        last = item(mode="l2va", last_frame="ending.png")
        l2va = h3.compile_standard_prompt(config(last), last)
        self.assertTrue(l2va.startswith(
            "How the reference pictures align with the target video — <Picture 1> (from [Shot 1]) "
            "aligns with the 8.00-second mark of the target video."
        ))
        text_only = item(mode="t2va")
        t2va = h3.compile_standard_prompt(config(text_only), text_only)
        self.assertTrue(t2va.startswith("integrated_multimodal_description:"))

    def test_structured_camera_speech_and_visible_text(self) -> None:
        chapter = item(
            mode="i2va",
            shots=[{
                "action": "She raises the folded letter.",
                "camera": {
                    "type": "Push In", "amplitude": "small", "speed": "slow",
                    "target_phrase": "toward the letter",
                },
                "speech": [{
                    "speaker_id": "S1", "kind": "dialogue", "language": "English",
                    "text": "Wait—don't open it!",
                }],
                "on_screen_text": ["营业中"],
            }],
        )
        speakers = {"S1": {"description": "The young woman", "voice": "a quiet breathy voice"}}
        prompt = h3.compile_standard_prompt(config(chapter, speakers), chapter)
        self.assertIn("The camera pushes in with small amplitude at slow speed toward the letter.", prompt)
        self.assertIn("<d>[English] Wait—don't open it!</d>", prompt)
        self.assertIn('Visible on-screen text reads "营业中".', prompt)

    def test_voiceover_requires_closed_lips_in_output(self) -> None:
        chapter = item(
            mode="i2va",
            speech=[{
                "speaker_id": "S1", "kind": "voiceover", "language": "English",
                "text": "I remember that road.",
            }],
        )
        prompt = h3.compile_standard_prompt(
            config(chapter, {"S1": "The traveler"}), chapter
        )
        self.assertIn("says in an off-screen voiceover", prompt)
        self.assertIn("lips remain completely closed", prompt)

    def test_lint_rejects_bad_cut_and_soundscape(self) -> None:
        chapter = item(
            mode="i2va",
            shots=[
                {"action": "She waits."},
                {"cut_at": 9, "action": "The train arrives."},
            ],
            audio_prompt="N/A",
        )
        errors, _warnings = h3.lint_prompt_item(chapter, 8.0)
        self.assertTrue(any("cut_at" in value for value in errors))
        self.assertTrue(any("complete_silence" in value for value in errors))

    def test_scene_transition_must_pair_across_adjacent_shots(self) -> None:
        chapter = item(
            mode="i2va",
            shots=[{
                "action": "She begins speaking.",
                "speech": [{
                    "speaker_id": "S1", "text": "I was", "scene_transition": "out",
                }],
            }],
        )
        errors, _warnings = h3.lint_prompt_item(chapter, 8.0, {"S1": "The traveler"})
        self.assertTrue(any("transition-out" in value for value in errors))

    def test_stylized_cut_requires_explicit_user_request(self) -> None:
        chapter = item(
            mode="i2va",
            shots=[
                {"action": "She waits."},
                {"cut_at": 3, "transition": "the shot fades to", "action": "The platform is empty."},
            ],
        )
        errors, _warnings = h3.lint_prompt_item(chapter, 8.0)
        self.assertTrue(any("user_requested_transition" in value for value in errors))

    def test_later_shot_transition_compiles_as_natural_sentence(self) -> None:
        chapter = item(
            mode="i2va",
            shots=[
                {"action": "She waits."},
                {
                    "cut_at": 3,
                    "transition": "the shot fades to",
                    "user_requested_transition": True,
                    "action": "The empty platform beyond her.",
                },
            ],
        )
        prompt = h3.compile_standard_prompt(config(chapter), chapter)
        self.assertIn("At 00:03.000, the shot fades to the empty platform", prompt)
        self.assertNotIn("fades to,", prompt)


if __name__ == "__main__":
    unittest.main()
