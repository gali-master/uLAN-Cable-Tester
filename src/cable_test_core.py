#!/usr/bin/env python3
"""
Common implementation for the uLAN BCM54213PE cable tester.

The actual measurement/display flow from the original cable_test.py is combined
with the live measurement/report flow from ulan_test.py.
"""

import os
import re
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime

from generate_cable_report import generate_report_from_measurement

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = PROJECT_ROOT / "bin"
CONFIG_FILE = PROJECT_ROOT / "config" / "ulan_config.json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
REPORTS_DIR = PROJECT_ROOT / "reports"

TICKS_PER_METER = 97.4
PAIR_NAMES = ["1,2", "3,6", "4,5", "7,8"]

FAULT_NAMES = {
    0x0: "INVALID",
    0x1: "OK",
    0x2: "OPEN",
    0x3: "SAME SHORT",
    0x4: "CROSS SHORT",
    0x9: "BUSY",
}

# Windows-invalid characters are replaced although Linux itself only forbids
# '/' and NUL. This makes report names portable and predictable.
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def run(cmd, check=True, quiet=False):
    p = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and p.returncode:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n{p.stderr.strip()}"
        )
    if not quiet and p.stdout.strip():
        print(p.stdout.strip())
    return p.stdout.strip()


def mdio_write(mdio_dir, reg, value):
    run(
        ["sudo", str(Path(mdio_dir) / "mdio_write"), str(reg), value],
        quiet=True,
    )


def mdio_exp_read(mdio_dir, reg):
    out = run(
        ["sudo", str(Path(mdio_dir) / "mdio_exp_read"), reg],
        quiet=True,
    )
    m = re.search(r"=\s*(0x[0-9a-fA-F]+)", out)
    if not m:
        raise RuntimeError(
            f"Cannot parse MDIO extended register {reg}: {out}"
        )
    return int(m.group(1), 16)


def start_tdr(mdio_dir):
    # Exact sequence established during the BCM54213PE bench test.
    mdio_write(mdio_dir, 0, "0x8000")       # PHY reset
    time.sleep(0.20)

    for reg, value in [
        (0, "0x1140"),       # BMCR: AN enabled
        (4, "0x0001"),       # ADVERTISE: CSMA only
        (9, "0x0000"),       # CTRL1000: disable 1000 advertisement
        (0x1e, "0x0087"),    # RDB address
        (0x1f, "0x8000"),    # legacy access
        (0x17, "0x0fc0"),    # select ECD control
        (0x15, "0x9000"),    # RUN + BREAK_LINK
    ]:
        mdio_write(mdio_dir, reg, value)


def measure(mdio_dir, wait_s=0.25):
    start_tdr(mdio_dir)
    time.sleep(wait_s)

    ctrl = mdio_exp_read(mdio_dir, "0x0fc0")
    fault = mdio_exp_read(mdio_dir, "0x0fc1")
    raw = [
        mdio_exp_read(mdio_dir, f"0x{r:03x}")
        for r in range(0x0fc2, 0x0fc6)
    ]

    statuses = []
    lengths = []

    for i in range(4):
        code = (fault >> (i * 4)) & 0xF
        statuses.append(FAULT_NAMES.get(code, f"CODE {code:X}"))

        value = raw[i]
        if value in (0, 0xFFFF):
            lengths.append(None)
        else:
            lengths.append(value / TICKS_PER_METER)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status_reg": ctrl,
        "fault_reg": fault,
        "raw_lengths": raw,
        "lengths": lengths,
        "statuses": statuses,
    }


def sanitize_filename_component(value):
    value = INVALID_FILENAME_CHARS.sub("_", str(value))
    value = re.sub(r"\s+", " ", value).strip()
    value = value.rstrip(". ")
    return value or "Cable"


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}


def make_report_filename(cable_id):
    safe_id = sanitize_filename_component(cable_id)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"Cable_report_{stamp}_{safe_id}.pdf"


def display_result(measurement, lang):
    lengths = measurement["lengths"]
    statuses = measurement["statuses"]

    valid = [x for x in lengths if x is not None]
    avg_length = sum(valid) / len(valid) if valid else 0.0

    has_open = any(s == "OPEN" for s in statuses)
    has_short = any(s in ("SAME SHORT", "CROSS SHORT") for s in statuses)
    no_cable = not valid

    if lang == "eng":
        title = "LAN CABLE TEST"
        labels = ("Length:", "Pair", "Wiremap:", "Open:", "Short:", "Split pair:")
        none_text = "NONE"
        wiremap = "NO CABLE" if no_cable else ("PASS" if max(valid) - min(valid) < 2.0 else "FAIL / OPEN")
        open_status = "NO CABLE" if no_cable else ("OPEN" if has_open else "NONE")
        short_text = "DETECTED" if has_short else none_text
    else:
        title = "LAN KÁBEL TESZT"
        labels = ("Hossz:", "Pár", "Vezetékezés:", "Nyitott:", "Zárlat:", "Osztott pár:")
        none_text = "NINCS"
        wiremap = "NINCS KÁBEL" if no_cable else ("PASS" if max(valid) - min(valid) < 2.0 else "HIBA / NYITOTT")
        # Rövid státuszok: a mező neve már közli, hogy mit mérünk.
        open_status = "NINCS KÁBEL" if no_cable else ("NYITOTT" if has_open else "NINCS")
        short_text = "ÉSZLELVE" if has_short else none_text

    def lcd_line(label, value):
        # A keret belseje pontosan 34 karakter. A jobb oldali ║ soha nem kerülhet ki.
        text = f" {label:<16}{value}"
        return "║" + text[:33].ljust(34) + "║"

    print("╔" + "═" * 34 + "╗")
    print(f"║{title.center(34)}║")
    print("╠" + "═" * 34 + "╣")
    print(f"║{f' {labels[0]:<16}{avg_length:4.1f} m'.ljust(34)}║")
    print(f"║{'':34}║")
    for i, length in enumerate(lengths, 1):
        value = f"{length:4.1f} m" if length is not None else "---"
        print(f"║{f' {labels[1]} {i}:       {value}'.ljust(34)}║")
    print(f"║{'':34}║")
    print(lcd_line(labels[2], wiremap))
    print(lcd_line(labels[3], open_status))
    print(lcd_line(labels[4], short_text))
    print(lcd_line(labels[5], none_text))
    print("╚" + "═" * 34 + "╝")

def prompt_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes", "i", "igen"):
            return True
        if answer in ("n", "no", "nem"):
            return False


def main(lang="eng", mdio_dir=None):
    if mdio_dir is None:
        mdio_dir = BIN_DIR

    try:
        measurement = measure(mdio_dir)
    except Exception as exc:
        print(("HIBA: " if lang == "hu" else "ERROR: ") + str(exc), file=sys.stderr)
        return 1

    cfg = load_config()
    measurement["operator"] = str(cfg.get("operator", "Operator"))

    display_result(measurement, lang)

    if lang == "hu":
        wants_report = prompt_yes_no("\nJegyzőkönyv készítése? [I/N]: ")
    else:
        wants_report = prompt_yes_no("\nCreate PDF report? [Y/N]: ")

    if not wants_report:
        return 0

    if lang == "hu":
        cable_id = input("Cable ID: ").strip()
    else:
        cable_id = input("Cable ID: ").strip()

    # Per requirement: empty/invalid input is never rejected. Invalid filename
    # characters are sanitized automatically.
    if not cable_id:
        cable_id = "1"

    safe_cable_id = sanitize_filename_component(cable_id)

    # The template field is named Test ID; here it is explicitly the Cable ID.
    measurement["test_id"] = safe_cable_id
    measurement["cable_id"] = safe_cable_id

    template = TEMPLATES_DIR / ("Template_hu.png" if lang == "hu" else "Template_eng.png")
    layout = TEMPLATES_DIR / ("template_layout_hu.json" if lang == "hu" else "template_layout_eng.json")

    if not os.path.exists(template):
        print(f"Template missing: {template}", file=sys.stderr)
        return 2
    if not os.path.exists(layout):
        print(f"Layout missing: {layout}", file=sys.stderr)
        return 2

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORTS_DIR / make_report_filename(safe_cable_id)

    generate_report_from_measurement(
        measurement,
        output,
        template_path=template,
        layout_path=layout,
        language=lang,
    )

    print(
    f"{'Jegyzőkönyv: ' if lang == 'hu' else 'Report: '}{output}"
    )
    return 0
