#!/usr/bin/env python3
import json
import math
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BLACK=(25,25,25)
GREEN=(35,125,55)
RED=(190,45,45)
WHITE=(255,255,255)
GRID=(185,185,185)

def font(size,bold=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(p):
        return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def put_in_box(draw,box,text,fnt,fill=BLACK,align="left",pad=4):
    x0,y0,x1,y1=box
    if align=="center":
        draw.text(((x0+x1)/2,(y0+y1)/2),str(text),font=fnt,fill=fill,anchor="mm")
    elif align=="right":
        draw.text((x1-pad,(y0+y1)/2),str(text),font=fnt,fill=fill,anchor="rm")
    else:
        draw.text((x0+pad,(y0+y1)/2),str(text),font=fnt,fill=fill,anchor="lm")

def white_patch(draw,box):
    draw.rectangle(box,fill=WHITE)

def localized_status(s,language):
    s=str(s).upper()
    if language=="hu":
        return {
            "OK":"OK","OPEN":"NYITOTT","SAME SHORT":"AZONOS ZÁRLAT",
            "CROSS SHORT":"KERESZT ZÁRLAT","INVALID":"ÉRVÉNYTELEN",
            "BUSY":"FOGLALT"
        }.get(s,s)
    return {
        "OK":"OK","OPEN":"OPEN","SAME SHORT":"SAME SHORT",
        "CROSS SHORT":"CROSS SHORT","INVALID":"INVALID","BUSY":"BUSY"
    }.get(s,s)

def synthetic_tdr(draw, plot, length_m, max_m=None):
    """
    Draw only the illustrative TDR waveform on the blank plot area of the
    supplied template.  The template itself owns the axes, ticks, labels,
    grid, dB scale and 'meter' text.
    """
    x0, y0, x1, y1 = plot

    if max_m is None:
        max_m = 30.0

    # The template is intentionally left untouched.  Only the waveform and
    # the measured-length marker are drawn into the already blank area.
    pts = []
    N = 700

    for i in range(N):
        m = max_m * i / (N - 1)

        # Illustrative noise floor and damped ringing.
        baseline = -20.0 - 5.5 * (m / max_m)
        ripple = (
            0.65 * math.sin(m * 17.0)
            + 0.35 * math.sin(m * 31.0)
        )

        d = m - length_m
        peak = 0.0

        if abs(d) < 0.9:
            peak += 27.0 * math.exp(-(d / 0.32) ** 2)

        if d >= 0:
            peak += 10.0 * math.exp(-d / 4.0) * math.sin(d * 7.0)

        ydb = max(-30.0, min(0.0, baseline + ripple + peak))

        xx = x0 + (m / max_m) * (x1 - x0)
        yy = y0 + (0.0 - ydb) / 30.0 * (y1 - y0)

        pts.append((xx, yy))

    draw.line(pts, fill=GREEN, width=2)

    # Measured cable-end marker.  It terminates exactly at the template X axis.
    xx = x0 + (length_m / max_m) * (x1 - x0)
    draw.line((xx, y0, xx, y1), fill=RED, width=1)

    lx = max(x0 + 28, min(x1 - 28, xx))
    draw.text(
        (lx, y0 + 2),
        f"{length_m:.2f} m",
        font=font(10, True),
        fill=RED,
        anchor="ma",
    )


def generate_report_from_measurement(measurement,output,template_path,layout_path,language="eng"):
    with open(layout_path,"r",encoding="utf-8") as f:
        layout=json.load(f)

    img=Image.open(template_path).convert("RGB")
    draw=ImageDraw.Draw(img)
    fs=font(11)
    fsb=font(11,True)

    metadata={
        "test_id":measurement.get("test_id","1"),
        "date_time": (
    datetime.strptime(
        measurement.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "%Y-%m-%d %H:%M:%S"
    ).strftime("%d/%m/%Y %H:%M:%S")
    if language == "eng"
    else datetime.strptime(
        measurement.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "%Y-%m-%d %H:%M:%S"
    ).strftime("%Y.%m.%d. %H:%M:%S")
),
        "operator":measurement.get("operator","Operator"),
        "nvp":"97.4 tick/m (calib.)",
        "shielding_required":"NO",
        "transitions_permitted":"NO",
        "far_end_id":measurement.get("far_end_id","1"),
        "device":"uConsole AIO v2",
        "phy":"Broadcom BCM54213PE",
        "software":"uLAN Test v0.1",
        "serial_number":measurement.get("serial_number","UCONSOLE-0001"),
    }

    # Metadata positions come from the language-specific layout file.
    # The boxes are the same calibrated coordinates used during the template work.
    for key, value in metadata.items():
        box = layout["metadata"][key]
        x0, y0, x1, y1 = box
        # Values are aligned to the left edge of their calibrated field box.
        # The template supplies the labels; we only add the values.
        draw.text((x0 + 2, (y0 + y1) / 2), str(value),
                  font=fs, fill=BLACK, anchor="lm")

    put_in_box(draw,layout["far_end"],metadata["far_end_id"],fs)

    lengths=measurement["lengths"]
    statuses=measurement["statuses"]
    rows=layout["length_table"]["row_boxes"]

    pairs=["1,2","3,6","4,5","7,8"]

    for i in range(4):
        put_in_box(draw,rows[i]["pair"],pairs[i],fs,BLACK,"center")
        if lengths[i] is None:
            put_in_box(draw,rows[i]["length"],"---",fsb,RED,"center")
        else:
            put_in_box(draw,rows[i]["length"],f"{lengths[i]:.2f}",fsb,GREEN,"center")
        st=localized_status(statuses[i],language)
        ok=str(statuses[i]).upper() in ("OK","OPEN")
        put_in_box(draw,rows[i]["status"],st,fsb,GREEN if ok else RED,"center")

    measured=lengths[0] if lengths[0] is not None else next((x for x in lengths if x is not None),0.0)
    if measured>0:
        synthetic_tdr(draw,layout["tdr"]["plot"],measured)

    img.save(output,"PDF",resolution=104.5)
