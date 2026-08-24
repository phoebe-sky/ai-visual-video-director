#!/usr/bin/env python3
"""Render semantic visual cues to transparent PNG overlays."""

import argparse
import json
import math
import os
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def find_font(size, bold=False):
    candidates = []
    if sys.platform == "darwin":
        candidates += [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    elif sys.platform == "win32":
        root = os.environ.get("WINDIR", r"C:\Windows")
        candidates += [
            str(Path(root) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf")),
            str(Path(root) / "Fonts" / "msjh.ttc"),
        ]
    else:
        candidates += [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def rgba(value, default=(255,255,255,255)):
    if not value:
        return default
    value = str(value).lstrip("#")
    if len(value) == 6:
        return tuple(int(value[i:i+2],16) for i in (0,2,4)) + (255,)
    if len(value) == 8:
        return tuple(int(value[i:i+2],16) for i in (0,2,4,6))
    return default


def wrap_text(text, width=16):
    text = str(text or "").strip()
    if not text:
        return ""
    if " " in text:
        return "\n".join(textwrap.wrap(text, width=max(8,width)))
    chunks=[text[i:i+width] for i in range(0,len(text),width)]
    return "\n".join(chunks)


def center_text(draw, box, text, font, fill, spacing=10):
    x1,y1,x2,y2=box
    bbox=draw.multiline_textbbox((0,0),text,font=font,spacing=spacing,align="center")
    w,h=bbox[2]-bbox[0],bbox[3]-bbox[1]
    draw.multiline_text(((x1+x2-w)/2,(y1+y2-h)/2),text,font=font,fill=fill,spacing=spacing,align="center")


def rounded_card(draw, box, fill=(18,18,20,225), outline=(255,255,255,45), radius=36, width=2):
    draw.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)


def render_typography(draw, cue, W, H, colors):
    box=(70,170,W-70,H-170)
    rounded_card(draw,box,fill=colors["panel"])
    text=cue.get("display_text") or cue.get("visual_concept") or cue.get("spoken_text","")
    center_text(draw,box,wrap_text(text,14),find_font(68,True),colors["text"],14)


def render_number(draw, cue, W, H, colors):
    box=(100,170,W-100,H-170)
    rounded_card(draw,box,fill=colors["panel"])
    data=cue.get("data") or {}
    value=data.get("value",cue.get("display_text",""))
    unit=data.get("unit","")
    label=data.get("label",cue.get("label",""))
    center_text(draw,(120,200,W-120,470),f"{value}{unit}",find_font(112,True),colors["accent"])
    if label:
        center_text(draw,(140,470,W-140,620),wrap_text(label,20),find_font(40,True),colors["text"])


def render_comparison(draw, cue, W, H, colors):
    data=cue.get("data") or {}
    items=data.get("items") or []
    if len(items)<2:
        items=[
          {"label":"Before","value":data.get("before","—")},
          {"label":"After","value":data.get("after","—")}
        ]
    gap=24
    margin=50
    card_w=(W-margin*2-gap)//2
    y1,y2=170,H-170
    for idx,item in enumerate(items[:2]):
        x1=margin+idx*(card_w+gap); x2=x1+card_w
        rounded_card(draw,(x1,y1,x2,y2),fill=colors["panel"])
        label=str(item.get("label",""))
        value=str(item.get("value",""))
        center_text(draw,(x1+20,y1+40,x2-20,y1+180),wrap_text(label,12),find_font(34,True),colors["muted"])
        center_text(draw,(x1+20,y1+180,x2-20,y2-40),wrap_text(value,10),find_font(72,True),colors["accent"])


def render_chart(draw, cue, W, H, colors):
    data=cue.get("data") or {}
    labels=list(data.get("labels") or [])
    values=list(data.get("values") or [])
    ctype=data.get("chart_type","bar")
    title=data.get("title") or cue.get("display_text") or ""
    box=(55,115,W-55,H-100)
    rounded_card(draw,box,fill=colors["panel"])
    if title:
        draw.text((85,145),wrap_text(title,24),font=find_font(34,True),fill=colors["text"])
    if not labels or not values or len(labels)!=len(values):
        center_text(draw,(90,220,W-90,H-130),"Data required",find_font(42,True),colors["muted"])
        return
    plot=(120,275,W-90,H-160)
    px1,py1,px2,py2=plot
    vals=[float(v) for v in values]
    maxv=max(max(vals),1e-9)
    if ctype=="line":
        pts=[]
        for i,v in enumerate(vals):
            x=px1+(px2-px1)*(i/max(1,len(vals)-1))
            y=py2-(py2-py1)*(v/maxv)
            pts.append((x,y))
        if len(pts)>1: draw.line(pts,fill=colors["accent"],width=8,joint="curve")
        for (x,y),lab in zip(pts,labels):
            draw.ellipse((x-8,y-8,x+8,y+8),fill=colors["accent"])
            draw.text((x-30,py2+18),str(lab)[:8],font=find_font(22),fill=colors["muted"])
    else:
        n=len(vals); gap=18; bw=max(24,(px2-px1-gap*(n-1))/n)
        for i,(lab,v) in enumerate(zip(labels,vals)):
            x1=px1+i*(bw+gap); x2=x1+bw
            y1=py2-(py2-py1)*(v/maxv)
            draw.rounded_rectangle((x1,y1,x2,py2),radius=12,fill=colors["accent"])
            draw.text((x1,py2+18),str(lab)[:8],font=find_font(22),fill=colors["muted"])


def render_diagram(draw, cue, W, H, colors):
    data=cue.get("data") or {}
    nodes=data.get("nodes") or []
    if not nodes:
        concept=cue.get("visual_concept") or cue.get("spoken_text","")
        nodes=[x.strip() for x in str(concept).replace("→","|").split("|") if x.strip()][:4]
    if not nodes:
        nodes=["Idea","Workflow","Result"]
    nodes=[n.get("label",n) if isinstance(n,dict) else n for n in nodes]
    y=H//2
    margin=45
    gap=26
    bw=max(150,(W-margin*2-gap*(len(nodes)-1))//len(nodes))
    boxes=[]
    for i,n in enumerate(nodes):
        x1=margin+i*(bw+gap); x2=x1+bw
        b=(x1,y-100,x2,y+100); boxes.append(b)
        rounded_card(draw,b,fill=colors["panel"])
        center_text(draw,(x1+16,y-85,x2-16,y+85),wrap_text(n,9),find_font(30,True),colors["text"])
    for a,b in zip(boxes,boxes[1:]):
        x1=a[2]; x2=b[0]; yy=y
        draw.line((x1+5,yy,x2-12,yy),fill=colors["accent"],width=7)
        draw.polygon([(x2-12,yy-12),(x2,yy),(x2-12,yy+12)],fill=colors["accent"])


def render_list(draw, cue, W, H, colors, numbered=False):
    data=cue.get("data") or {}
    items=data.get("items") or cue.get("visual_elements") or []
    box=(70,110,W-70,H-100)
    rounded_card(draw,box,fill=colors["panel"])
    title=data.get("title") or cue.get("display_text") or cue.get("visual_concept") or ""
    if title: draw.text((105,145),wrap_text(title,24),font=find_font(38,True),fill=colors["text"])
    y=245
    for i,item in enumerate(items[:6]):
        label=item.get("label",item) if isinstance(item,dict) else item
        marker=f"{i+1}." if numbered else "✓"
        draw.text((115,y),marker,font=find_font(34,True),fill=colors["accent"])
        draw.multiline_text((180,y),wrap_text(label,22),font=find_font(32,True),fill=colors["text"],spacing=6)
        y+=95


def render_icon(draw, cue, W, H, colors):
    box=(160,155,W-160,H-155)
    rounded_card(draw,box,fill=colors["panel"])
    cx=W//2; cy=H//2-40
    r=86
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=colors["accent"],width=10)
    draw.line((cx-r//2,cy,cx+r//2,cy),fill=colors["accent"],width=10)
    draw.line((cx,cy-r//2,cx,cy+r//2),fill=colors["accent"],width=10)
    label=cue.get("display_text") or cue.get("label") or cue.get("visual_concept") or ""
    center_text(draw,(190,cy+110,W-190,H-180),wrap_text(label,16),find_font(42,True),colors["text"])


def render_visual_metaphor(draw, cue, W, H, colors):
    concept=cue.get("visual_concept") or cue.get("display_text") or cue.get("spoken_text","")
    render_diagram(draw,{**cue,"data":{"nodes":[x.strip() for x in str(concept).replace("→","|").split("|") if x.strip()][:4]}},W,H,colors)


def render(cue, output, width=960, height=720):
    style=cue.get("style") or {}
    colors={
      "text":rgba(style.get("text_color"),(255,255,255,255)),
      "muted":rgba(style.get("muted_color"),(195,198,205,255)),
      "accent":rgba(style.get("accent_color"),(255,76,76,255)),
      "panel":rgba(style.get("panel_color"),(18,18,20,230))
    }
    img=Image.new("RGBA",(width,height),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    strategy=cue.get("visual_strategy","kinetic_typography")
    if strategy=="number_card": render_number(draw,cue,width,height,colors)
    elif strategy=="comparison": render_comparison(draw,cue,width,height,colors)
    elif strategy=="chart": render_chart(draw,cue,width,height,colors)
    elif strategy in {"diagram","visual_metaphor"}:
        (render_diagram if strategy=="diagram" else render_visual_metaphor)(draw,cue,width,height,colors)
    elif strategy in {"checklist","timeline"}: render_list(draw,cue,width,height,colors,numbered=(strategy=="timeline"))
    elif strategy in {"icon","logo","ui_card"}: render_icon(draw,cue,width,height,colors)
    else: render_typography(draw,cue,width,height,colors)
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    img.save(output)
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("cue_json")
    p.add_argument("output")
    p.add_argument("--width",type=int,default=960)
    p.add_argument("--height",type=int,default=720)
    args=p.parse_args()
    cue_path=Path(args.cue_json)
    cue=json.loads(cue_path.read_text(encoding="utf-8")) if cue_path.is_file() else json.loads(args.cue_json)
    print(render(cue,args.output,args.width,args.height))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
