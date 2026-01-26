---
name: launchpad-remotion
description: Reusable components, brand assets, and patterns for the trycua/launchpad Remotion monorepo. Use when creating videos in launchpad projects.
---

# Launchpad Remotion Components

## Animations (`@launchpad/shared`)

```tsx
import { FadeIn, SlideUp, TextReveal } from "@launchpad/shared/components/animations";

// Fade with direction
<FadeIn durationInFrames={30} delay={0} direction="up" distance={30}>
  <h1>Title</h1>
</FadeIn>

// Slide up
<SlideUp durationInFrames={20} delay={15} distance={50}>
  <p>Subtitle</p>
</SlideUp>

// Text reveal with clip-path
<TextReveal durationInFrames={30} direction="left">
  <h1>Revealed!</h1>
</TextReveal>
```

## Hooks

```tsx
import { useAnimatedValue, useFadeIn } from "@launchpad/shared/hooks";

// Interpolate any value
const scale = useAnimatedValue({ from: 0, to: 1, durationInFrames: 30, delay: 10 });

// Fade opacity
const { opacity } = useFadeIn({ durationInFrames: 20, delay: 5 });
```

## Brand Assets (`@launchpad/assets`)

```tsx
import { COLORS } from "@launchpad/assets/brand";
import { loadFonts, FONTS } from "@launchpad/assets/brand";

// Colors
COLORS.primary              // "#0070f3"
COLORS.background.cream     // "#FDF8F3"
COLORS.background.dark      // "#000000"
COLORS.text.primary         // "#1a1a1a"
COLORS.accent.success       // "#10b981"

// Fonts
const { fontFamily } = loadFonts();
<h1 style={{ fontFamily: fontFamily.heading }}>Urbanist</h1>
<p style={{ fontFamily: fontFamily.body }}>Inter</p>
<code style={{ fontFamily: fontFamily.mono }}>JetBrains Mono</code>
```

## Easings

```tsx
import { easings } from "@launchpad/shared/utils";

interpolate(frame, [0, 30], [0, 1], { easing: easings.smooth });

// Available: smooth, bounce, linear, inOut, sharp, elastic
```

## Video Presets

```tsx
import { VIDEO_PRESETS, FPS } from "@launchpad/shared/types";

VIDEO_PRESETS["1080p"]   // 1920x1080
VIDEO_PRESETS["720p"]    // 1280x720
VIDEO_PRESETS["4k"]      // 3840x2160
VIDEO_PRESETS["square"]  // 1080x1080
VIDEO_PRESETS["vertical"] // 1080x1920

FPS.STANDARD   // 30
FPS.CINEMATIC  // 24
FPS.SMOOTH     // 60
```

## Scene Structure

```tsx
// Always export duration constant
export const MY_SCENE_DURATION = 90; // 3 seconds at 30fps

export const MyScene: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background.cream }}>
      <FadeIn direction="up">
        <h1>Title</h1>
      </FadeIn>
    </AbsoluteFill>
  );
};
```

## Combining Scenes

```tsx
import { Series, Audio, staticFile } from "remotion";

export const FULL_VIDEO_DURATION = INTRO_DURATION + DEMO_DURATION + OUTRO_DURATION;

<AbsoluteFill>
  <Audio src={staticFile("music.wav")} volume={0.3} />
  <Series>
    <Series.Sequence durationInFrames={INTRO_DURATION}><IntroScene /></Series.Sequence>
    <Series.Sequence durationInFrames={DEMO_DURATION}><DemoScene /></Series.Sequence>
    <Series.Sequence durationInFrames={OUTRO_DURATION}><OutroScene /></Series.Sequence>
  </Series>
</AbsoluteFill>
```

## Staggered Animation Pattern

```tsx
const items = ["First", "Second", "Third"];

{items.map((item, i) => (
  <FadeIn key={item} delay={i * 15} direction="up">
    <div>{item}</div>
  </FadeIn>
))}
```

## Commands

```bash
pnpm create-video          # Create new video project
pnpm remotion              # Open Remotion Studio
pnpm render                # Render video
pnpm dev                   # Next.js preview
```

## Tips

- Use frames for timing: 30 frames = 1 second at 30fps
- Always `extrapolateRight: "clamp"` to prevent runaway values
- Export `DURATION` constants from every scene
- Place assets in `public/` folder, reference with `staticFile()`
- Use `Series` to sequence scenes, `Sequence` for overlays
