# AI Visual Video Director

**Understand the content. Direct the visuals. Edit the story.**

AI Visual Video Director is a semantic-first video editing Skill for short-form talking-head, educational, storytelling, product, tutorial, and mixed-content videos.

It does **not** begin with a fixed template. It first understands what the speaker is saying, identifies the narrative function of each segment, chooses an appropriate visual language, then produces an edit plan that can drive motion graphics, diagrams, charts, icons, typography, screenshots, B-roll, and other visual treatments.

## Core idea

Traditional auto-editing:

```
transcript → captions → cuts → export
```

AI Visual Video Director:

```
transcript
→ narrative analysis
→ semantic object extraction
→ visual strategy
→ motion strategy
→ visual cue sheet
→ edit plan
→ render / execution
```

## What this Skill is designed to do

- Detect narrative intent: hook, problem, insight, story, example, comparison, process, result, CTA, etc.
- Detect visual opportunities without requiring the video to be data-heavy or tutorial-heavy.
- Turn numbers into the right visual form instead of forcing every number into a chart.
- Turn abstract concepts into diagrams, typography, symbolic motion, or visual metaphors.
- Use logos, icons, screenshots, UI cards, and generated visuals only when semantically useful.
- Control visual density so the video does not become over-edited.
- Preserve the presenter as the primary subject when appropriate.
- Support creator-specific visual preferences through a reusable Creator Profile.

## Public preview status

This repository is the public development edition. The architecture is intentionally modular so it can later be separated into a private premium distribution without changing the core editing language.

## Main files

- `SKILL.md` — Skill entry point and execution contract
- `QUICKSTART.md` — installation and first-run workflow
- `config/` — creator, brand, visual and editing defaults
- `agents/` — semantic, narrative, visual, motion and QC roles
- `schemas/` — structured interchange formats
- `rules/` — decision rules for visual selection, motion, pacing and density
- `workflows/` — content-specific execution patterns
- `examples/` — sample inputs and plans

## Design principle

> Do not decorate every sentence. Visualize the sentences that improve comprehension, emphasis, rhythm, or emotional impact.

