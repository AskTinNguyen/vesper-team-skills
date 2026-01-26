---
name: elevenlabs
description: Generate AI voiceovers, sound effects, and music using ElevenLabs APIs. Use when creating audio content for videos, podcasts, or games. Triggers include generating voiceovers, narration, dialogue, sound effects from descriptions, background music, soundtrack generation, voice cloning, or any audio synthesis task.
---

# ElevenLabs Audio Generation

Requires `ELEVENLABS_API_KEY` in `.env`.

## Text-to-Speech

```python
from elevenlabs.client import ElevenLabs
from elevenlabs import save, VoiceSettings
import os

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

audio = client.text_to_speech.convert(
    text="Welcome to my video!",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.5,
        speed=1.0
    )
)
save(audio, "voiceover.mp3")
```

### Models

| Model | Quality | SSML Support | Notes |
|-------|---------|--------------|-------|
| `eleven_multilingual_v2` | Highest consistency | None | Stable, production-ready, 29 languages |
| `eleven_flash_v2_5` | Good | `<break>`, `<phoneme>` | Fast, supports pause/pronunciation tags |
| `eleven_turbo_v2_5` | Good | `<break>`, `<phoneme>` | Fastest latency |
| `eleven_v3` | Most expressive | None | Alpha — unreliable, needs prompt engineering |

**Choose:** multilingual_v2 for reliability, flash/turbo for SSML control, v3 for maximum expressiveness (expect retakes).

### Voice Settings by Style

| Style | stability | similarity | style | speed |
|-------|-----------|------------|-------|-------|
| Natural/professional | 0.75-0.85 | 0.9 | 0.0-0.1 | 1.0 |
| Conversational | 0.5-0.6 | 0.85 | 0.3-0.4 | 0.9-1.0 |
| Energetic/YouTuber | 0.3-0.5 | 0.75 | 0.5-0.7 | 1.0-1.1 |

### Pauses Between Sections

**With flash/turbo models:** Use SSML break tags inline:
```
...end of section. <break time="1.5s" /> Start of next...
```
Max 3 seconds per break. Excessive breaks can cause speed artifacts.

**With multilingual_v2 / v3:** No SSML support. Options:
- Paragraph breaks (blank lines) — creates ~0.3-0.5s natural pause
- Post-process with ffmpeg: split audio and insert silence

**WARNING:** `...` (ellipsis) is NOT a reliable pause — it can be vocalized as a word/sound. Do not use ellipsis as a pause mechanism.

### Pronunciation Control

**Phonetic spelling (any model):** Write words as you want them pronounced:
- `Janus` → `Jan-us`
- `nginx` → `engine-x`
- Use dashes, capitals, apostrophes to guide pronunciation

**SSML phoneme tags (flash/turbo only):**
```
<phoneme alphabet="ipa" ph="ˈdʒeɪnəs">Janus</phoneme>
```

### Iterative Workflow

1. Generate → listen → identify pronunciation/pacing issues
2. Adjust: phonetic spellings, break tags, voice settings
3. Regenerate. If pauses aren't precise enough, add silence in post with ffmpeg rather than fighting the TTS engine.

## Voice Cloning

### Instant Voice Clone

```python
with open("sample.mp3", "rb") as f:
    voice = client.voices.ivc.create(
        name="My Voice",
        files=[f],
        remove_background_noise=True
    )
print(f"Voice ID: {voice.voice_id}")
```

- Use `client.voices.ivc.create()` (not `client.voices.clone()`)
- Pass file handles in binary mode (`"rb"`), not paths
- Convert m4a first: `ffmpeg -i input.m4a -codec:a libmp3lame -qscale:a 2 output.mp3`
- Multiple samples (2-3 clips) improve accuracy
- Save voice ID for reuse

**Professional Voice Clone:** Requires Creator plan+, 30+ min audio. See [reference.md](reference.md).

## Sound Effects

Max 22 seconds per generation.

```python
result = client.text_to_sound_effects.convert(
    text="Thunder rumbling followed by heavy rain",
    duration_seconds=10,
    prompt_influence=0.3
)
with open("thunder.mp3", "wb") as f:
    for chunk in result:
        f.write(chunk)
```

**Prompt tips:** Be specific — "Heavy footsteps on wooden floorboards, slow and deliberate, with creaking"

## Music Generation

10 seconds to 5 minutes. Use `client.music.compose()` (not `.generate()`).

```python
result = client.music.compose(
    prompt="Upbeat indie rock, catchy guitar riff, energetic drums, travel vlog",
    music_length_ms=60000,
    force_instrumental=True
)
with open("music.mp3", "wb") as f:
    for chunk in result:
        f.write(chunk)
```

**Prompt structure:** Genre, mood, instruments, tempo, use case. Add "no vocals" or use `force_instrumental=True` for background music.

## Remotion Integration

Save to `public/` folder, then:
```tsx
<Audio src={staticFile('audio/voiceover.mp3')} />
```

## Popular Voices

- George: `JBFqnCBsd6RMkjVDRZzb` (warm narrator)
- Rachel: `21m00Tcm4TlvDq8ikWAM` (clear female)
- Adam: `pNInz6obpgDQGcFmaJgB` (professional male)

List all: `client.voices.get_all()`

For full API docs, see [reference.md](reference.md).
