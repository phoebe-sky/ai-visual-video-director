#!/usr/bin/env python3
"""Probe and fully decode a rendered video; emit machine-readable QA evidence."""

import argparse, json, subprocess, sys
from pathlib import Path
from runtime_paths import resolve_media_binary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--output")
    args=p.parse_args()
    video=Path(args.video).expanduser().resolve()
    if not video.is_file():
        print(json.dumps({"valid":False,"error":"file not found","path":str(video)},ensure_ascii=False))
        return 2
    ffprobe=resolve_media_binary("ffprobe")
    ffmpeg=resolve_media_binary("ffmpeg")
    probe=subprocess.run([
      ffprobe,"-v","error","-print_format","json","-show_streams","-show_format",str(video)
    ],capture_output=True,text=True)
    decode=subprocess.run([ffmpeg,"-v","error","-i",str(video),"-f","null","-"],capture_output=True,text=True)
    payload={"valid":probe.returncode==0 and decode.returncode==0,"path":str(video),"decode_errors":decode.stderr.strip()}
    if probe.returncode==0:
        data=json.loads(probe.stdout or "{}")
        payload["format"]=data.get("format",{})
        payload["streams"]=data.get("streams",[])
    else:
        payload["probe_errors"]=probe.stderr.strip()
    text=json.dumps(payload,ensure_ascii=False,indent=2)
    if args.output:
        out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8")
    print(text)
    return 0 if payload["valid"] else 3

if __name__=="__main__":
    raise SystemExit(main())
