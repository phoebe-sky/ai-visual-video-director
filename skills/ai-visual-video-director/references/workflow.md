# End-to-End Workflow

## 1. Inspect
Use ffprobe and preserve the source.

## 2. Transcribe
Run local-first timed transcription and reuse the hash cache.

## 3. Direct
Read the transcript and create edit/edit-plan.json.
The plan is a machine-executable directing document, not the final deliverable.

## 4. Validate
Run validate_edit_plan.py.

## 5. Render
Run render_video.py. The renderer:
- normalizes the base frame,
- creates semantic transparent graphics,
- overlays supplied screenshots/images/video assets,
- burns subtitles,
- retains source audio,
- exports H.264/AAC MP4.

## 6. QA
Run qa_video.py for probe + complete decode validation.

## 7. Fix
Inspect the preview visually. Repair timing, density, layout or caption issues and rerender.

## 8. Final
Deliver a verified final MP4, not merely JSON.
