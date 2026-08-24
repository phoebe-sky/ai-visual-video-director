# Quick Start

## 1. Install the Skill

Repository:

`https://github.com/phoebe-sky/ai-visual-video-director`

Install the `ai-visual-video-director` Skill through Codex.

## 2. Upload a source video

Then say:

```
Use $ai-visual-video-director to edit this video.
Please analyze the content, restructure it when useful, add semantic visuals,
subtitles, motion graphics and PIP/B-roll where appropriate, and export the final MP4.
```

## 3. First-run dependencies

The Skill checks its local runtime.

When Codex asks for one-time confirmation to download local dependencies and the Whisper model, approve it.

## 4. What should happen automatically

1. ffprobe inspection
2. local transcription
3. semantic / narrative analysis
4. source cuts and story order
5. executable edit plan
6. generated graphics + supplied media overlays
7. subtitles
8. FFmpeg render
9. QA decode
10. final MP4

You should not need to manually create a Visual Cue Sheet unless you want to override the AI director.

## 5. Planning-only mode

Only use this when you intentionally do not want a render:

```
Use $ai-visual-video-director to create the edit plan only. Do not render yet.
```
