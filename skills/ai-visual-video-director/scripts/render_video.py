#!/usr/bin/env python3
"""Render a complete edited MP4 from a semantic edit plan using FFmpeg."""

import argparse
import importlib.util
import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from runtime_paths import resolve_media_binary, runtime_python


def maybe_relaunch():
    if importlib.util.find_spec("PIL") is not None:
        return
    py=runtime_python()
    if py.is_file() and os.environ.get("AI_VISUAL_VIDEO_RENDER_RUNTIME")!="1":
        env=os.environ.copy()
        env["AI_VISUAL_VIDEO_RENDER_RUNTIME"]="1"
        os.execve(str(py),[str(py),str(Path(__file__).resolve()),*sys.argv[1:]],env)


maybe_relaunch()

from visual_renderer import render as render_visual  # noqa: E402


VIDEO_EXTS={".mp4",".mov",".m4v",".webm",".mkv",".avi"}


def run(cmd):
    subprocess.run(cmd,check=True)


def probe(ffprobe, source):
    result=subprocess.run([
        ffprobe,"-v","error","-print_format","json",
        "-show_streams","-show_format",str(source)
    ],check=True,capture_output=True,text=True)
    return json.loads(result.stdout)


def ass_time(seconds):
    cs=max(0,int(round(float(seconds)*100)))
    h=cs//360000; cs%=360000
    m=cs//6000; cs%=6000
    s=cs//100; c=cs%100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def wrap_caption(text,max_chars=16):
    text=str(text or "").strip()
    if not text:
        return ""
    if " " in text:
        words=text.split()
        lines=[]; cur=""
        for w in words:
            test=(cur+" "+w).strip()
            if len(test)>max_chars and cur:
                lines.append(cur); cur=w
            else:
                cur=test
        if cur: lines.append(cur)
    else:
        lines=[text[i:i+max_chars] for i in range(0,len(text),max_chars)]
    if len(lines)>2:
        lines=[lines[0],"".join(lines[1:])]
    return r"\N".join(lines)


def default_font():
    if sys.platform=="darwin": return "PingFang TC"
    if sys.platform=="win32": return "Microsoft JhengHei"
    return "Noto Sans CJK TC"


def build_ass(transcript, path, width, height, style):
    segments=transcript.get("segments") or []
    font=style.get("font_name") or default_font()
    size=int(style.get("font_size",58 if height>=1600 else 40))
    margin_v=int(style.get("margin_v",250 if height>=1600 else 150))
    primary=style.get("text_color","&H00FFFFFF")
    outline=style.get("outline_color","&H00151515")
    header=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,{font},{size},{primary},&H000000FF,{outline},&H64000000,-1,0,0,0,100,100,0,0,1,4,1,2,70,70,{margin_v},1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events=[]
    for seg in segments:
        text=wrap_caption(seg.get("text",""),int(style.get("max_chars",16)))
        if not text: continue
        text=text.replace("{",r"\{").replace("}",r"\}")
        events.append(f"Dialogue: 0,{ass_time(seg.get('start',0))},{ass_time(seg.get('end',0))},Default,,0,0,0,,{text}")
    path.write_text(header+"\n".join(events)+"\n",encoding="utf-8")


def ffmpeg_escape_filter_path(path):
    value=str(Path(path).resolve()).replace("\\","/")
    value=value.replace(":","\\:").replace("'","\\'")
    return value


def layout_xy(layout, base_w, base_h, ov_w, ov_h, start, motion):
    layout=(layout or "center").lower()
    if layout in {"top","upper_center"}:
        tx=f"(W-w)/2"; ty="180"
    elif layout in {"lower","bottom"}:
        tx=f"(W-w)/2"; ty=f"H-h-360"
    elif layout in {"left","side_left"}:
        tx="60"; ty=f"(H-h)/2"
    elif layout in {"right","side_right"}:
        tx=f"W-w-60"; ty=f"(H-h)/2"
    else:
        tx=f"(W-w)/2"; ty=f"(H-h)/2"

    motion_set=set(motion or [])
    if "slide_left" in motion_set:
        x=f"{tx}+180*max(0,1-(t-{start:.3f})/0.25)"
    else:
        x=tx
    if "slide_up" in motion_set:
        y=f"{ty}+140*max(0,1-(t-{start:.3f})/0.25)"
    else:
        y=ty
    return x,y


def make_overlay_asset(cue, out_dir, index):
    asset=cue.get("asset_path")
    strategy=cue.get("visual_strategy","kinetic_typography")
    if asset:
        p=Path(asset).expanduser().resolve()
        if p.is_file():
            return p
    if strategy in {"presenter_only","b_roll","picture_in_picture","screenshot","logo"} and asset:
        return None
    path=out_dir/f"cue-{index:03d}.png"
    render_visual(cue,path,900,650)
    return path


def main():
    p=argparse.ArgumentParser(description="Render semantic visual cues, subtitles and source audio to MP4")
    p.add_argument("source")
    p.add_argument("--plan",required=True)
    p.add_argument("--transcript")
    p.add_argument("--output",required=True)
    p.add_argument("--width",type=int,default=1080)
    p.add_argument("--height",type=int,default=1920)
    p.add_argument("--fps",type=float,default=30)
    p.add_argument("--crf",type=int,default=18)
    p.add_argument("--preset",default="medium")
    p.add_argument("--no-subtitles",action="store_true")
    args=p.parse_args()

    source=Path(args.source).expanduser().resolve()
    plan_path=Path(args.plan).expanduser().resolve()
    output=Path(args.output).expanduser().resolve()
    if not source.is_file(): raise SystemExit(f"source not found: {source}")
    if not plan_path.is_file(): raise SystemExit(f"plan not found: {plan_path}")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    transcript={}
    if args.transcript:
        tp=Path(args.transcript).expanduser().resolve()
        if tp.is_file(): transcript=json.loads(tp.read_text(encoding="utf-8"))

    ffmpeg=resolve_media_binary("ffmpeg")
    ffprobe=resolve_media_binary("ffprobe")
    meta=probe(ffprobe,source)
    output.parent.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ai-visual-render-") as td:
        tmp=Path(td)
        generated=output.parent/"generated-visuals"
        generated.mkdir(parents=True,exist_ok=True)

        cues=[]
        for idx,cue in enumerate(plan.get("visual_cues") or []):
            if cue.get("visual_strategy")=="presenter_only":
                continue
            start=float(cue.get("start_time",0)); end=float(cue.get("end_time",start))
            if end<=start: continue
            asset=make_overlay_asset(cue,generated,idx)
            if asset is None: continue
            cues.append((idx,cue,asset,start,end))

        cmd=[ffmpeg,"-v","error","-y","-i",str(source)]
        input_defs=[]
        for idx,cue,asset,start,end in cues:
            dur=max(0.1,end-start)
            if asset.suffix.lower() in VIDEO_EXTS:
                cmd += ["-stream_loop","-1","-i",str(asset)]
                input_defs.append(("video",asset,dur))
            else:
                cmd += ["-loop","1","-t",f"{dur:.3f}","-i",str(asset)]
                input_defs.append(("image",asset,dur))

        filters=[
          f"[0:v]scale={args.width}:{args.height}:force_original_aspect_ratio=increase,"
          f"crop={args.width}:{args.height},setsar=1,fps={args.fps}[v0]"
        ]
        current="v0"
        for n,((idx,cue,asset,start,end),(kind,_asset,dur)) in enumerate(zip(cues,input_defs),start=1):
            strategy=cue.get("visual_strategy","")
            motion=cue.get("motion") or ["fade"]
            ov=f"ov{n}"
            if kind=="video":
                if strategy=="b_roll":
                    filters.append(
                      f"[{n}:v]trim=duration={dur:.3f},setpts=PTS-STARTPTS+{start:.3f}/TB,"
                      f"scale={args.width}:{args.height}:force_original_aspect_ratio=increase,"
                      f"crop={args.width}:{args.height},setsar=1[{ov}]"
                    )
                    x,y="0","0"
                else:
                    filters.append(
                      f"[{n}:v]trim=duration={dur:.3f},setpts=PTS-STARTPTS+{start:.3f}/TB,"
                      f"scale=520:-2,setsar=1[{ov}]"
                    )
                    x,y=layout_xy(cue.get("layout","right"),args.width,args.height,520,700,start,motion)
            else:
                fadeout=max(0,dur-0.18)
                scale_filter=""
                if "pop" in motion or "zoom" in motion:
                    # Static semantic overlay with fade; position movement supplies the motion.
                    scale_filter="scale=900:650,"
                filters.append(
                  f"[{n}:v]format=rgba,{scale_filter}"
                  f"fade=t=in:st=0:d=0.16:alpha=1,"
                  f"fade=t=out:st={fadeout:.3f}:d=0.16:alpha=1,"
                  f"setpts=PTS-STARTPTS+{start:.3f}/TB[{ov}]"
                )
                x,y=layout_xy(cue.get("layout","center"),args.width,args.height,900,650,start,motion)

            nxt=f"v{n}"
            filters.append(
              f"[{current}][{ov}]overlay=x='{x}':y='{y}':"
              f"enable='between(t,{start:.3f},{end:.3f})':eof_action=pass:shortest=0[{nxt}]"
            )
            current=nxt

        if transcript and not args.no_subtitles:
            ass=tmp/"captions.ass"
            build_ass(transcript,ass,args.width,args.height,plan.get("subtitle_style") or {})
            escaped=ffmpeg_escape_filter_path(ass)
            filters.append(f"[{current}]ass='{escaped}'[vout]")
            current="vout"

        cmd += [
          "-filter_complex",";".join(filters),
          "-map",f"[{current}]",
          "-map","0:a?",
          "-c:v","libx264","-preset",args.preset,"-crf",str(args.crf),
          "-pix_fmt","yuv420p",
          "-c:a","aac","-b:a","192k",
          "-movflags","+faststart",
          "-shortest",
          str(output)
        ]
        run(cmd)

    summary={
      "output":str(output),
      "visual_cues_rendered":len(cues),
      "subtitles_burned":bool(transcript and not args.no_subtitles),
      "width":args.width,"height":args.height,"fps":args.fps
    }
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
