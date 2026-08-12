# Extracted Reddit post

Source: r/StableDiffusion, `crinklypaper`, “Long-Form videos (1+ min long) are
very possible with H3 locally! Here's mine.” The text below was supplied by the
user after Reddit blocked automated access.

Original credit goes to NikoDemon for `ComfyUI-H3-Motion-Context`. The author
recommends Ethan Fel's `ComfyUI-MiniMaxH3-Contex-Loop` fork. It carries 22
frames from the preceding clip and uses reference images for character and
style consistency. The example used two GPT-generated character sheets.

The workflow has a shared prompt prepended to every scene. The author put the
style and the definitions for each main character there. To prevent character
bleed, every scene also described the other visible characters in enough detail
to establish that they were different people.

The author planned every scene with Claude and required each scene to end on a
still transition beat, such as a stationary character or a close-up, because
the ending must connect to the opening of the next scene. This constraint is
unnecessary for one deliberately continuous long shot.

H3 can reproduce nearly the same prompt across different seeds. The author
worked out prompt problems at roughly 0.5–1 megapixel, then ran the final at a
higher resolution. Their 94-second result took about 70 minutes on an RTX 5090,
roughly ten minutes for each 15-second clip.

The context-loop node allows every scene to be reviewed and rerolled or edited
before continuing. Every accepted clip creates a checkpoint, so a crashed or
paused production can resume. Final assembly concatenates the accepted clips
and their audio. The same method can split a nominal eight-second generation
into two four-second generations when pursuing a higher working resolution.

The author's settings were LightX, six steps, strength 0.8, Euler with the basic
scheduler, and SageAttention. Their machine had an RTX 5090 and 96 GB of system
memory, though they expected lower-end cards to work. The linked Pastebin
contains seven scenes totaling 102 seconds and specifies `context_length=22`,
`encode_mode=video`, and `anchor_mode=head`.

In the comments, the author confirmed that the loop feeds the previous video's
last 22 frames into Ref2VA and that prompts must account for scene transitions.
They also confirmed that the prompts follow MiniMax's reference-model guide.
