---
name: ai-visual-video-director
description: End-to-end semantic video editing Skill. Use when Codex must take user-supplied talking-head, educational, storytelling, product, tutorial, or mixed-content footage, transcribe it, understand each narrative beat, generate timed visual cues such as typography, number cards, charts, diagrams, icons, screenshots or PIP, render those visuals, composite subtitles and motion with FFmpeg, and export a verified MP4.
---

# AI Visual Video Director

This Skill is not a planning-only assistant. Its default job is to produce a real edited video file.

## Read before editing

Read:
- `references/workflow.md`
- `references/visual-language.md`
- `references/edit-plan-format.md`
- `references/runtime-setup.md`

Use the root repository material only as background. The installable Skill lives in this directory.

## End-to-end contract

For a normal request such as “幫我剪這支影片” or “use $ai-visual-video-director”:

1. Inspect the supplied media with `ffprobe`.
2. Run `scripts/setup_runtime.py --check`.
3. If the isolated runtime is missing, request one combined confirmation for local dependency/model downloads, then run:
   `scripts/setup_runtime.py --install --confirm-local-downloads --model small`.
4. Transcribe with `scripts/transcribe_video.py`, reusing the SHA-256 cache and preferring local faster-whisper.
5. Read the timed transcript yourself and create `edit/edit-plan.json` using the required schema and semantic rules.
6. Do not stop at the plan unless the user explicitly asks for planning only.
7. Run `scripts/validate_edit_plan.py edit/edit-plan.json`.
8. Run `scripts/render_video.py SOURCE --plan edit/edit-plan.json --transcript edit/transcripts/source.json --output edit/preview.mp4`.
9. Inspect the preview. Run `scripts/qa_video.py edit/preview.mp4`.
10. Fix evidence-based issues and rerender. Maximum three self-fix passes unless the user requests more.
11. Export the final MP4. For vertical social video, default to 1080×1920 H.264 + AAC.
12. Report the actual output path and QA result. Never say a video is complete when only a plan exists.

## Semantic direction

For each transcript beat determine:
- narrative intent
- semantic objects
- visual opportunity
- visual strategy
- motion
- priority

Narrative intents:
`hook`, `problem`, `pain_point`, `question`, `claim`, `explanation`, `example`, `story`, `contrast`, `myth`, `insight`, `evidence`, `process`, `instruction`, `result`, `emotion`, `call_to_action`, `conclusion`.

Visual strategies supported by the renderer:
- `presenter_only`
- `kinetic_typography`
- `number_card`
- `comparison`
- `chart`
- `diagram`
- `timeline`
- `checklist`
- `ui_card`
- `icon`
- `logo`
- `screenshot`
- `picture_in_picture`
- `b_roll`
- `visual_metaphor`

## Visual selection rules

Do not turn every sentence into a graphic.

- one value → number card
- two comparable values → comparison
- 3+ supported categories → chart
- time series → line chart
- steps → checklist/timeline/diagram
- system relationships → diagram
- tool/platform → logo or screenshot
- software operation → screenshot/PIP
- abstract claim → typography/diagram/metaphor
- emotional story → presenter first, restrained overlays
- no semantic benefit → presenter only

Never fabricate data for charts.

## Motion

The executable renderer supports timed entry/exit motion. Use:
- `fade`
- `pop`
- `slide_up`
- `slide_left`
- `zoom`
- `highlight`

Treat `counter`, `line_draw`, `morph`, and `pulse` as semantic motion requests. When the runtime cannot faithfully execute one, degrade gracefully to the closest supported motion rather than failing the full render.

## Visual density

Default `medium`:
- low: 3–5 major visual events / 30 sec
- medium: 5–9
- high: 9–15

Preserve quiet presenter-led sections.

## Asset behavior

If a cue uses `asset_path`:
- image → overlay as screenshot/logo/icon/card
- video → use as PIP or B-roll
- do not invent a local path
- if an expected asset is missing, use the cue's fallback or generated semantic card

## Subtitles

Default Traditional Chinese subtitles:
- 2 lines maximum
- semantic phrase breaks
- lower safe region
- do not cover face, PIP or platform UI
- burn subtitles into the final MP4 unless the user asks otherwise

## Output files

Use a project-local `edit/` directory:
- `edit/transcripts/`
- `edit/edit-plan.json`
- `edit/generated-visuals/`
- `edit/preview.mp4`
- `edit/final.mp4`
- `edit/qa.json`

Do not overwrite the user's source media.

## Honesty rule

A Visual Cue Sheet is not a finished edit.
A rendered but unchecked MP4 is not a finished edit.
Only report completion after full render and QA.
