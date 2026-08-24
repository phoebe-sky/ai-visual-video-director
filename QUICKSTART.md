# Quick Start

## 1. Prepare source material

Minimum:
- one talking-head or narration video

Optional:
- script or transcript
- screen recording
- product images
- screenshots
- logos
- B-roll
- brand guide

## 2. Set your Creator Profile

Edit `config/creator-profile.yaml` once.

This controls:
- visual density
- preferred visual language
- pacing
- subtitle behavior
- camera treatment
- styles to avoid

## 3. Give the Skill a simple request

Example:

```
Use $ai-visual-video-director to edit this video.
Keep the speaker natural.
Analyze the content first, then create appropriate graphics, diagrams, icons,
number treatments and visual metaphors only where they improve comprehension.
Use medium visual density.
```

## 4. Expected planning output

Before rendering, the Skill should produce:
- content profile
- narrative beat map
- timed Visual Cue Sheet
- Edit Plan
- asset list

## 5. Review only what matters

The creator should not need to manually design every visual.

Review:
- whether the visual concept matches the spoken idea,
- whether the density feels right,
- whether any facts or numbers need correction,
- whether a brand asset should replace a generic visual.

## 6. Render

Use the available video rendering stack in the execution environment.
The Skill itself defines the directing logic; rendering implementation may vary.
