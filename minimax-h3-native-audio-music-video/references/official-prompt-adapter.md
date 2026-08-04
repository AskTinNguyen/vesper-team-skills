# Official prompt contract adapter for locked audio

Use this reference for NativeAudio segment configs and compiled prompts. The [official MiniMax H3 base guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md) defines T2VA/I2VA/FL2VA/L2VA prompt grammar but does not specify R2VA or the local audio-lock node. The three fields and language below follow the official guide; the `<Picture 1>` plus `<Audio 1>` instruction is a clearly labeled local adaptation to ComfyUI's Ref2VA reference order.

## Locked-audio header and fields

Begin with:

```text
Use <Picture 1> as the exact identity, wardrobe, style, and scene reference. Use <Audio 1> as the exact performance timeline.
```

Insert one blank line, then emit `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in that order. These fields condition synchronization and visuals; `MiniMaxH3NativeAudioLock` prevents audio denoising, and final assembly still muxes the untouched full song once.

## Vocal segments

- Use one stable speaker ID across every appearance.
- With verified user-supplied lyrics, put only the language tag and exact lyrics inside `<d>`. Preserve every character and punctuation mark.
- Without verified lyrics, state that the on-screen performer sings the exact supplied vocal audio from `<Audio 1>` with precise natural lip synchronization. Never invent, paraphrase, or auto-transcribe lyrics.
- If a vocal fragment spans an intentional cut, use paired transition-out and transition-in markers for the same speaker.
- For off-screen vocals presented as voiceover, use the exact voiceover phrase and require fully closed on-screen lips.

## Instrumental segments

Require fully closed lips for every frame. Direct performance through body, hands, gaze, prop interaction, screen direction, and camera rhythm. Do not add singing or dialogue merely because a performer is visible.

## Diegetic versus audience-only music

Set `music_role` to `diegetic-performance` when characters hear or perform the music in-world. Describe that music and singing inside the multimodal timeline and set non-diegetic music to `N/A`.

Set `music_role` to `soundtrack` for audience-only backing music. Describe its actual instrumentation, tempo, rhythm, and dynamics under non-diegetic music. Do not use mood labels. Keep separate ambience and physical sounds under soundscape; when none are audible, say so in a complete sentence rather than using `N/A` while music is present.

## Shots, camera, and exact text

Prefer one continuous shot for a short performance segment. A later shot requires a strictly increasing cut time and new information. Use a structured camera type with optional amplitude and speed. Keep exact visible text inside `on_screen_text`; the compiler adds English double quotation marks without changing the supplied characters.

## Review

Compare the render with the compiled prompt and source excerpt. Reject wrong lyric timing, identity drift, open lips during instrumental or voiceover passages, invented visible text, unmotivated cuts, camera motion that contradicts the performance, or an unstable accepted continuation frame. Audio identity is verified separately from visual synchronization through the final decoded-PCM hash procedure.
