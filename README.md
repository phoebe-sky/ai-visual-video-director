# AI Visual Video Director

> **Understand the content. Direct the visuals. Edit the story.**

AI Visual Video Director is an **end-to-end Codex Skill for real video editing and MP4 export**.

It combines:
- local-first faster-whisper transcription
- semantic / narrative analysis
- source cutting, reordering and per-segment speed changes
- subtitle timing remap
- semantic motion graphics
- number cards and comparisons
- charts and diagrams
- screenshots / logos / icons
- PIP and B-roll overlays
- FFmpeg compositing
- final H.264/AAC MP4 export
- full decode QA

## Install

The installable Skill is:

`skills/ai-visual-video-director/`

Use the repository URL with your Codex Skill installation workflow:

`https://github.com/phoebe-sky/ai-visual-video-director`

Then invoke:

```
Use $ai-visual-video-director to edit this video and export the final MP4.
```

The default contract is **not planning-only**. Unless you explicitly ask for a plan only, the Skill should continue through transcription → edit plan → render → QA → final MP4.

## First run

The Skill checks an isolated local runtime. If dependencies are missing, it requests one combined confirmation and installs them outside the Skill directory.

Runtime:
- FFmpeg / ffprobe
- faster-whisper
- Whisper `small` model
- Pillow
- matplotlib

It does not require a separate desktop editing application.

## How visual direction works

The Skill first understands each narrative beat, then chooses a visual strategy.

Examples:

| Spoken content | Visual |
|---|---|
| 「一個月 29 美金」 | Number card |
| 「以前 3 小時，現在 30 分鐘」 | Comparison |
| Supported multi-category data | Chart |
| AI Agent → MCP → tools | Diagram |
| Personal story / emotional beat | Presenter-first |
| Software operation | Screenshot or PIP |
| Abstract insight | Typography / diagram / metaphor |

It does not force every sentence into a graphic.

## Actual editing

The executable edit plan supports:

```json
"source_cuts": [
  {"source_start": 12.4, "source_end": 18.9, "speed": 1.0},
  {"source_start": 2.1, "source_end": 7.8, "speed": 1.08}
]
```

The order of entries is the final story order, so the Skill can restructure the source instead of merely decorating the original clip.

## Renderer

The current public implementation uses **Python + FFmpeg** as the production renderer. This keeps the Skill portable and allows Codex to produce the final file directly without depending on a separate GUI editor.

## Repository structure

```
skills/ai-visual-video-director/
├── SKILL.md
├── scripts/
│   ├── setup_runtime.py
│   ├── transcribe_video.py
│   ├── validate_edit_plan.py
│   ├── visual_renderer.py
│   ├── render_video.py
│   ├── qa_video.py
│   └── ...
├── references/
└── assets/
```

## Status

**Public development build — executable.**

The next useful step is to install it and run it against real footage, then tune visual style presets from actual outputs rather than adding more theoretical rules.
