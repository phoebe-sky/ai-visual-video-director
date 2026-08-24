# Executable Edit Plan Format

Minimal example:

```json
{
  "content_profile": {
    "primary_style": "educational",
    "visual_density": "medium"
  },
  "subtitle_style": {
    "font_size": 58,
    "max_chars": 16
  },
  "visual_cues": [
    {
      "start_time": 2.0,
      "end_time": 4.5,
      "spoken_text": "原本要三個小時，現在只要三十分鐘",
      "narrative_intent": "contrast",
      "visual_strategy": "comparison",
      "visual_concept": "Editing time before and after AI",
      "data": {
        "items": [
          {"label": "Before", "value": "3 HR"},
          {"label": "After", "value": "30 MIN"}
        ]
      },
      "motion": ["slide_up"],
      "layout": "center",
      "priority": "high"
    }
  ]
}
```

## Chart data
```json
"data": {
  "chart_type": "bar",
  "title": "完成時間",
  "labels": ["傳統", "AI"],
  "values": [180, 30]
}
```

## Diagram data
```json
"data": {
  "nodes": ["Human Judgment", "Workflow", "AI"]
}
```

## External media
```json
{
  "visual_strategy": "picture_in_picture",
  "asset_path": "/absolute/path/to/screen-recording.mp4",
  "layout": "right"
}
```
