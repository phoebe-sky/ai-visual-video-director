---
name: ai-visual-video-director
description: Semantic-first AI video directing and editing Skill that understands spoken content, identifies narrative intent, chooses appropriate visual treatments, creates a timed visual cue sheet, and produces a structured edit plan for dynamic short-form video.
---

# AI Visual Video Director

## Mission

Transform raw spoken-video content into a directed visual edit by understanding meaning before choosing effects.

The Skill must not assume that every video is:
- data-driven,
- screen-recording based,
- tutorial based,
- or suited to the same visual template.

The same decision framework must support educational, opinion, storytelling, product, tutorial, business, creator, and mixed-content videos.

## Required execution order

1. **Ingest**
   - Accept one or more source videos.
   - Accept optional transcript, script, B-roll, screenshots, brand assets, or creator profile.
   - Preserve source timing whenever possible.

2. **Transcribe**
   - Prefer word-level timestamps.
   - Segment into semantic sentences and larger narrative beats.
   - Remove filler only when it does not alter meaning or personality.

3. **Analyze narrative intent**
   For every segment, classify one or more intents:
   - hook
   - problem
   - pain_point
   - question
   - claim
   - explanation
   - example
   - story
   - contrast
   - myth
   - insight
   - evidence
   - process
   - instruction
   - result
   - emotion
   - call_to_action
   - conclusion

4. **Extract semantic objects**
   Detect:
   - people
   - brands
   - tools
   - products
   - places
   - objects
   - numbers
   - money
   - percentages
   - time
   - actions
   - emotions
   - concepts
   - relationships
   - steps
   - before/after states

5. **Choose a visual strategy**
   Available strategies:
   - presenter_only
   - kinetic_typography
   - icon
   - logo
   - number_card
   - chart
   - diagram
   - comparison
   - timeline
   - checklist
   - ui_card
   - screenshot
   - picture_in_picture
   - b_roll
   - generated_visual
   - visual_metaphor

6. **Choose motion**
   Available motion presets:
   - fade
   - pop
   - slide_up
   - slide_left
   - scale
   - counter
   - line_draw
   - typewriter
   - mask_reveal
   - pulse
   - zoom
   - track
   - morph
   - highlight
   - parallax

7. **Score visual priority**
   Do not create a visual simply because a keyword exists.
   Score each candidate by:
   - comprehension gain
   - emphasis value
   - novelty
   - narrative importance
   - visual clarity
   - timing opportunity

8. **Build the Visual Cue Sheet**
   Each cue must include:
   - start_time
   - end_time
   - spoken_text
   - narrative_intent
   - visual_strategy
   - visual_concept
   - visual_elements
   - motion
   - layout
   - priority
   - confidence
   - fallback

9. **Build the Edit Plan**
   Include:
   - source cut decisions
   - subtitle timing
   - visual cues
   - PIP windows
   - safe-zone constraints
   - transition decisions
   - audio emphasis
   - optional asset requests

10. **Quality control**
    Reject or simplify visuals that:
    - repeat the same pattern too often,
    - cover the presenter’s face,
    - collide with subtitles or platform UI,
    - overstate data,
    - invent unsupported facts,
    - reduce comprehension,
    - or create visual noise.

## Number visualization rules

Do not convert every number into a chart.

- One standalone value → `number_card`
- Two comparable values → `comparison`
- Three or more categorical values → `chart`
- Ordered time series → `chart:line`
- Percentage/progress → `progress` or `donut` style visual
- Increase/decrease → `counter + directional indicator`
- Monetary value → `number_card` with currency context
- Unsupported or ambiguous numbers → typography only, no fabricated chart

## Abstract-concept rules

When a segment contains no literal visual object, prefer:
1. typography,
2. symbolic icons,
3. simple diagrams,
4. visual metaphor,
5. generated visual only when the first four are insufficient.

## Visual density

Default to `medium`.

Approximate guide:
- low: 3–5 major visual events / 30 sec
- medium: 5–9 major visual events / 30 sec
- high: 9–15 major visual events / 30 sec

Never insert motion for every sentence.

## Presenter priority

When the source is talking-head:
- the presenter remains the narrative anchor;
- overlays should support, not replace, the speaker;
- reserve full-screen graphics for high-value moments;
- use PIP or side-by-side when the visual needs context but the presenter should remain visible.

## Output contract

Produce, in order:
1. content profile
2. narrative beat map
3. visual cue sheet
4. edit plan
5. asset needs
6. QC notes

If rendering tools are available, execute the plan only after the plan is internally consistent.
If rendering tools are unavailable, return the structured plan without pretending a video was rendered.

## Creator preferences

Read `config/creator-profile.yaml` and `config/visual-style.yaml` before selecting visual treatments.

User-specified instructions for the current project override defaults.
