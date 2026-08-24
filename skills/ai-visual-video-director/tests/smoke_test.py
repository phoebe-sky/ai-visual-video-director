#!/usr/bin/env python3
"""End-to-end smoke test: synthetic source -> cut/reorder -> visuals -> subtitles -> MP4 -> QA."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"


def main():
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg:
        print("SKIP: ffmpeg not available")
        return 0
    with tempfile.TemporaryDirectory(prefix="ai-visual-smoke-") as td:
        d=Path(td)
        source=d/"source.mp4"
        transcript=d/"transcript.json"
        plan=d/"plan.json"
        output=d/"final.mp4"
        qa=d/"qa.json"

        subprocess.run([
          ffmpeg,"-v","error","-y",
          "-f","lavfi","-i","testsrc2=size=540x960:rate=24",
          "-f","lavfi","-i","sine=frequency=440:sample_rate=44100",
          "-t","6","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",str(source)
        ],check=True)

        transcript.write_text(json.dumps({
          "segments":[
            {"start":0.0,"end":2.0,"text":"以前剪一支影片需要三個小時"},
            {"start":2.0,"end":4.0,"text":"現在可以縮短到三十分鐘"},
            {"start":4.0,"end":6.0,"text":"先理解內容再決定畫面"}
          ],
          "words":[]
        ],ensure_ascii=False),encoding="utf-8")

        plan.write_text(json.dumps({
          "source_cuts":[
            {"source_start":0.0,"source_end":3.0,"speed":1.0},
            {"source_start":3.0,"source_end":6.0,"speed":1.08}
          ],
          "subtitle_style":{"font_size":32,"max_chars":12,"margin_v":120},
          "visual_cues":[
            {
              "start_time":0.5,"end_time":2.2,
              "visual_strategy":"comparison",
              "data":{"items":[{"label":"Before","value":"3 HR"},{"label":"After","value":"30 MIN"}]},
              "motion":["slide_up"],"layout":"center"
            },
            {
              "start_time":2.5,"end_time":4.7,
              "visual_strategy":"diagram",
              "visual_concept":"Content → Visual → Edit",
              "data":{"nodes":["Content","Visual","Edit"]},
              "motion":["slide_left"],"layout":"top"
            }
          ]
        },ensure_ascii=False),encoding="utf-8")

        subprocess.run([
          sys.executable,str(SCRIPTS/"validate_edit_plan.py"),str(plan)
        ],check=True)
        subprocess.run([
          sys.executable,str(SCRIPTS/"render_video.py"),str(source),
          "--plan",str(plan),"--transcript",str(transcript),"--output",str(output),
          "--width","540","--height","960","--fps","24","--preset","ultrafast","--crf","28"
        ],check=True)
        subprocess.run([
          sys.executable,str(SCRIPTS/"qa_video.py"),str(output),"--output",str(qa)
        ],check=True)
        result=json.loads(qa.read_text(encoding="utf-8"))
        if not result.get("valid") or output.stat().st_size<10000:
            raise RuntimeError("smoke test output failed QA")
        print(json.dumps({"ok":True,"bytes":output.stat().st_size},indent=2))
        return 0


if __name__=="__main__":
    raise SystemExit(main())
