#!/usr/bin/env python3
"""Build printable A4 reference sheets for the FAST boards in this machine.

One PDF per board plus a combined binder, written to printouts/ (git-ignored).
Board diagrams are downloaded from fastpinball.com at build time into
printouts/.cache/ and are not committed: they are FAST's images and this repo
is public. Optional photos of this machine's own boards are read from
printouts/photos/ (cabinet_io.jpg, opto_flipper.jpg) if present.

Pinouts come from docs/12-fast-boards.md (FAST's product pages and board
silkscreens). "This machine" columns are read from config/config.yaml, so
re-run this after changing switch or coil numbers.

Requires: reportlab, pypdf, pillow, pyyaml.
Usage: python3 tools/board_sheets.py
"""

import datetime
import io
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

import yaml
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "printouts")
CACHE = os.path.join(OUT, ".cache")
PHOTOS = os.path.join(OUT, "photos")
FAST = "https://fastpinball.com"

IMAGES = {
    "neuron_labels": "/products/controllers/images/FAST Neuron with labels.jpg",
    "neuron_wiring": "/wiring/neuron/images/neuron wiring.jpg",
    "spfb_headers": "/products/power/images/FAST Smart Power Filter Board Headers.jpg",
    "spfb_to_neuron": "/wiring/neuron/images/spfb to neuron.jpg",
    "spfb_switches": "/wiring/neuron/images/spfb switches.jpg",
    "spfb_to_pib": "/wiring/neuron/images/spfb to pib.jpg",
    "pib_board": "/products/power/images/FP-PWR-0030.jpg",
    "pib_outputs": "/products/power/images/pib outputs.jpg",
    "1616_connectors": "/products/images/1616 Connectors.png",
    "1616_mosfet": "/products/images/1616-mosfet-mapping.jpg",
    "3208_connectors": "/products/images/3208 Connectors.png",
    "3208_mosfet": "/products/images/3208-mosfet-mapping.jpg",
    "cab_features": "/products/images/cabinet io board features.png",
    "cab_power": "/wiring/neuron/images/cab io power wiring.png",
    "cab_left": "/wiring/neuron/images/cabinet left switches.png",
    "cab_coin": "/wiring/neuron/images/coin door wiring.jpg",
    "exp71": "/products/expansion/images/FP-EXP-0071.jpg",
    "exp81": "/products/expansion/images/FP-EXP-0081.jpg",
    "io_loop": "/wiring/neuron/images/io loop wiring.jpg",
    "numbering": "/modern/images/driver and switch numbers.jpg",
}

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 28
INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#999999")
BAR = colors.HexColor("#222222")
SHADE = colors.HexColor("#EEEEEE")

# FAST wire colour standard (fastpinball.com/wiring/standards).
WIRES = {
    "sw": ("Orange", "#F28C28"),
    "swg": ("Purple", "#7B3FA0"),
    "drv": ("Grey/white", "#BBBBBB"),
    "tg": ("Black (toxic)", "#111111"),
    "gnd": ("Black", "#111111"),
    "12": ("Yellow", "#F5D000"),
    "5": ("Red", "#D62828"),
    "48": ("Blue", "#1F5FBF"),
    "data": ("White", "#FFFFFF"),
    "key": ("", None),
    "": ("", None),
}


# ---------------------------------------------------------------- data ----

def load_assignments():
    """Map 'board-index' to device names, separately for switches and coils.

    A trailing comment on a device's number line (e.g. '## To check') is kept.
    """
    path = os.path.join(ROOT, "config", "config.yaml")
    cfg = yaml.safe_load(open(path))
    comments = {"switches": {}, "coils": {}}
    section = None
    for line in open(path):
        m = re.match(r"^([A-Za-z_]+):", line)
        if m:
            section = m.group(1)
        m = re.match(r"^\s+number:\s*(\S+)\s*#+\s*(.+)$", line)
        if m and section in comments:
            comments[section][m.group(1)] = m.group(2).strip()
    out = {"switches": {}, "coils": {}}
    for sec in out:
        for name, dev in (cfg.get(sec) or {}).items():
            if isinstance(dev, dict) and "number" in dev and dev.get("platform") != "virtual":
                num = str(dev["number"])
                note = comments[sec].get(num)
                out[sec][num] = name + (" (" + note.lower() + ")" if note else "")
    return out


def git_rev():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


def fetch(key):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + ".jpg")
    if not os.path.exists(path):
        url = FAST + urllib.parse.quote(IMAGES[key])
        print("download", url)
        data = urllib.request.urlopen(url, timeout=60).read()
        im = Image.open(io.BytesIO(data))
        if im.mode in ("P", "RGBA", "LA"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        im = im.convert("RGB")
        im.thumbnail((1800, 1800))
        im.save(path, quality=85)
    return path


def photo(name):
    path = os.path.join(PHOTOS, name)
    return path if os.path.exists(path) else None


# ------------------------------------------------------------ drawing ----

def fit(c, text, font, size, maxw, minsize=5.5):
    while size > minsize and c.stringWidth(text, font, size) > maxw:
        size -= 0.25
    while text and c.stringWidth(text, font, size) > maxw:
        text = text[:-1]
    return text, size


def para(c, text, x, y_top, w, size=8.5, leading=None):
    style = ParagraphStyle("p", fontName="Helvetica", fontSize=size,
                           leading=leading or size * 1.3, textColor=INK)
    p = Paragraph(text, style)
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, y_top - h)
    return h


class Sheet:
    """One board's PDF: header band, footer, and a simple top-down flow."""

    def __init__(self, path, title, part, where, sources, rev, date):
        self.c = canvas.Canvas(path, pagesize=(PAGE_W, PAGE_H))
        self.c.setTitle(title)
        self.title, self.part, self.where = title, part, where
        self.sources, self.rev, self.date = sources, rev, date
        self.page = 0
        self.new_page()

    def new_page(self):
        if self.page:
            self.c.showPage()
        self.page += 1
        c = self.c
        c.setFillColor(BAR)
        c.rect(0, PAGE_H - 46, PAGE_W, 46, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(MARGIN, PAGE_H - 29, self.title)
        c.setFont("Helvetica", 10)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 22, self.part)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 36, self.where)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 6.5)
        c.drawString(MARGIN, 14, "Sources: " + self.sources)
        c.drawString(MARGIN, 6, "Generated %s from matrix-pinball %s (tools/board_sheets.py). "
                     "Verify pin 1 on the board silkscreen before crimping." % (self.date, self.rev))
        c.drawRightString(PAGE_W - MARGIN, 6, "%s, sheet %d" % (self.title, self.page))
        self.y = PAGE_H - 58

    def space(self, h):
        if self.y - h < 26:
            self.new_page()

    def images(self, items, max_h=None, min_h=None):
        """items: list of (path, caption), side by side. Shrinks to the space
        left on the page, down to min_h, before starting a new page."""
        items = [i for i in items if i[0]]
        if not items:
            return
        c = self.c
        avail_w = PAGE_W - 2 * MARGIN
        gap = 12
        max_h = max_h or (self.y - 40)
        ims = [Image.open(p) for p, _ in items]
        ratios = [im.width / im.height for im in ims]
        # common height so the row fills the width, capped by max_h
        h = min(max_h - 12, (avail_w - gap * (len(items) - 1)) / sum(ratios))
        room = self.y - 26 - 16
        if h > room and min_h and room >= min_h:
            h = room
        self.space(h + 14)
        total_w = sum(r * h for r in ratios) + gap * (len(items) - 1)
        x = MARGIN + (avail_w - total_w) / 2
        for (p, cap), r in zip(items, ratios):
            w = r * h
            c.drawImage(ImageReader(p), x, self.y - h, w, h)
            c.setStrokeColor(RULE)
            c.setLineWidth(0.5)
            c.rect(x, self.y - h, w, h)
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Oblique", 7)
            c.drawString(x, self.y - h - 9, cap)
            x += w + gap
        self.y -= h + 16

    def notes(self, title, lines, size=8.5):
        c = self.c
        w = PAGE_W - 2 * MARGIN
        text = "".join("&bull; %s<br/>" % l for l in lines)
        style = ParagraphStyle("p", fontName="Helvetica", fontSize=size, leading=size * 1.3)
        h = Paragraph(text, style).wrap(w - 16, 1000)[1] + 22
        self.space(h)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.rect(MARGIN, self.y - h, w, h)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(MARGIN + 8, self.y - 13, title)
        para(c, text, MARGIN + 8, self.y - 18, w - 16, size)
        self.y -= h + 10

    def cards(self, cards, cols=2):
        gap = 12
        w = (PAGE_W - 2 * MARGIN - gap * (cols - 1)) / cols
        for i in range(0, len(cards), cols):
            row = cards[i:i + cols]
            h = max(card.height(w) for card in row)
            self.space(h)
            for j, card in enumerate(row):
                card.draw(self.c, MARGIN + j * (w + gap), self.y, w)
            self.y -= h + 10

    def save(self):
        self.c.save()


class Card:
    """A connector: title bar, optional pin strip, and a table."""

    ROW = 11.8

    def __init__(self, title, spec, rows, strip=True, pin1=True, note="",
                 heads=("Pin", "Signal", "Wire", "This machine", "Notes"),
                 widths=(0.08, 0.2, 0.15, 0.37, 0.2)):
        # rows: (pin, signal, wire_key, machine) ; wire_key may be ''
        self.title, self.spec, self.rows = title, spec, rows
        self.strip, self.pin1, self.note = strip, pin1, note
        self.heads, self.widths = heads, widths

    def height(self, w):
        h = 20 + 16 + self.ROW * len(self.rows) + 4
        if self.strip:
            h += 36
        if self.note:
            h += 11 * (1 + int(len(self.note) * 4.2 / (w - 12)))
        return h

    def draw(self, c, x, y, w):
        y0 = y - 18
        c.setFillColor(BAR)
        c.rect(x, y - 18, w, 18, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 6, y - 13, self.title)
        c.setFont("Helvetica", 8)
        c.drawRightString(x + w - 6, y - 13, self.spec)
        y -= 22
        if self.strip:
            y = self.draw_strip(c, x, y, w)
        # table header
        cols = [w * f for f in self.widths]
        c.setFillColor(SHADE)
        c.rect(x, y - 14, w, 14, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7.5)
        cx = x
        for head, cw in zip(self.heads, cols):
            c.drawString(cx + 3, y - 10, head)
            cx += cw
        y -= 14
        for n, row in enumerate(self.rows):
            pin, sig, wire, mach = (list(row) + ["", "", "", ""])[:4]
            if wire == "key":
                c.setFillColor(colors.HexColor("#F6F6F6"))
                c.rect(x, y - self.ROW, w, self.ROW, stroke=0, fill=1)
            cx = x
            vals = [str(pin), str(sig), wire, str(mach), ""]
            for k, (val, cw) in enumerate(zip(vals, cols)):
                if k == 2 and self.heads[2] == "Wire":
                    name, hexc = WIRES.get(val, (val, None))
                    if hexc:
                        c.setFillColor(colors.HexColor(hexc))
                        c.setStrokeColor(INK)
                        c.setLineWidth(0.4)
                        c.rect(cx + 3, y - 9.6, 9, 7, stroke=1, fill=1)
                    c.setFillColor(INK)
                    t, s = fit(c, name, "Helvetica", 7, cw - 16)
                    c.setFont("Helvetica", s)
                    c.drawString(cx + 15, y - 8.8, t)
                else:
                    font = "Helvetica-Bold" if k == 0 else "Helvetica"
                    t, s = fit(c, val, font, 8 if k < 2 else 7.5, cw - 5)
                    c.setFillColor(INK if val else MUTED)
                    c.setFont(font, s)
                    c.drawString(cx + 3, y - 8.8, t)
                cx += cw
            c.setStrokeColor(colors.HexColor("#CCCCCC"))
            c.setLineWidth(0.4)
            c.line(x, y - self.ROW, x + w, y - self.ROW)
            y -= self.ROW
        # column rules and frame
        top = y + self.ROW * len(self.rows) + 14
        cx = x
        for cw in cols[:-1]:
            cx += cw
            c.line(cx, top, cx, y)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.rect(x, y, w, y0 - y)
        if self.note:
            para(c, self.note, x + 3, y - 3, w - 6, 7.2, 9)

    def draw_strip(self, c, x, y, w):
        pins = self.rows
        n = len(pins)
        bw = min(26, (w - 20) / n)
        sx = x + (w - bw * n) / 2
        c.setFont("Helvetica", 6)
        for i, row in enumerate(pins):
            bx = sx + i * bw
            key = row[2] == "key"
            c.setStrokeColor(INK)
            c.setLineWidth(0.6)
            if key:
                c.setFillColor(colors.HexColor("#DDDDDD"))
                c.rect(bx + 1, y - 22, bw - 2, 16, stroke=1, fill=1)
                c.line(bx + 1, y - 22, bx + bw - 1, y - 6)
                c.line(bx + 1, y - 6, bx + bw - 1, y - 22)
            else:
                name, hexc = WIRES.get(row[2], ("", None))
                c.setFillColor(colors.HexColor(hexc) if hexc else colors.white)
                c.rect(bx + 1, y - 22, bw - 2, 16, stroke=1, fill=1)
            c.setFillColor(INK)
            label, s = fit(c, str(row[1]), "Helvetica-Bold", 6.5, bw - 2, 4.5)
            c.setFont("Helvetica-Bold", s)
            c.drawCentredString(bx + bw / 2, y - 32, label)
            c.setFont("Helvetica", 6)
            c.drawCentredString(bx + bw / 2, y - 4, str(row[0]))
        if self.pin1:
            c.setFillColor(INK)
            p = c.beginPath()
            p.moveTo(sx - 9, y - 10)
            p.lineTo(sx - 3, y - 14)
            p.lineTo(sx - 9, y - 18)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
        else:
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Oblique", 6)
            c.drawString(x + 4, y - 12, "Order as")
            c.drawString(x + 4, y - 19, "printed;")
            c.drawString(x + 4, y - 26, "pin 1 end")
            c.drawString(x + 4, y - 33, "unconfirmed")
        return y - 36


# ------------------------------------------------------------- boards ----

def sw_rows(labels, board, asg, start_pin=1):
    """Switch header rows from labels like 'S0', 'K', 'G'."""
    rows = []
    for i, lab in enumerate(labels, start_pin):
        if lab == "K":
            rows.append((i, "KEY", "key", ""))
        elif lab == "G":
            rows.append((i, "G", "swg", "switch return"))
        else:
            num = int(lab[1:])
            rows.append((i, lab, "sw", asg["switches"].get("%s-%d" % (board, num), "")))
    return rows


def drv_rows(labels, board, asg):
    rows = []
    for i, lab in enumerate(labels, 1):
        if lab == "K":
            rows.append((i, "KEY", "key", ""))
        elif lab == "GND":
            rows.append((i, "GND", "tg", "toxic gnd to PIB TG"))
        else:
            num = int(lab[1:])
            rows.append((i, lab, "drv", asg["coils"].get("%s-%d" % (board, num), "")))
    return rows


def neuron(s):
    s.images([(fetch("neuron_labels"), "FAST: Neuron ports and headers")], max_h=225)
    s.cards([
        Card("Header map", "FP-CPU-2000", [
            ("J1", "12 V in", "12", "from SPFB J1 CONTROLLER"),
            ("J3/J4", "SSR, soft power", "", "not used"),
            ("J5", "Host PC control", "", ""),
            ("J10", "Raspberry Pi", "", "not used"),
            ("J13", "USB to host", "", "NUC; /dev/ttyACM0-2"),
            ("J26", "12 V out", "12", ""),
            ("J23-J25", "Breakouts", "", "one to SPFB J7: J__"),
            ("J19-J22", "LED chains", "", "not used"),
            ("J15, J11", "I/O loop", "", "loop OUT / IN"),
            ("J6", "Display bus", "", "not used"),
            ("J7, J8", "EXP bus", "", ""),
            ("BAT1", "CR2032", "", ""),
        ], strip=False, heads=("Header", "Function", "Wire", "This machine", "Notes"),
            widths=(0.14, 0.22, 0.14, 0.32, 0.18)),
        Card("Breakout header (J23 / J24 / J25)", "5-pin 0.100\"", [
            (1, "G", "gnd", "SPFB J7 pin 1"),
            (2, "T", "", "SPFB J7 pin 2"),
            (3, "R", "", "SPFB J7 pin 3"),
            (4, "G", "gnd", "SPFB J7 pin 4"),
            (5, "V", "", "SPFB J7 pin 5"),
        ], note="Straight through, pin to pin, 22 AWG. T and R are swapped on the boards "
                 "by design. Pin order as FAST's text lists it."),
    ])
    s.notes("At the machine", [
        "BLANKING LED (D5) on = watchdog expired, all drivers disabled (MPF default watchdog 1 s).",
        "The Cabinet I/O needs Neuron firmware v2.13 or newer. Recorded version: __________",
        "I/O loop: board OUT to next board IN; last board OUT back to the Neuron IN. Close the loop.",
    ])
    s.new_page()
    s.images([(fetch("neuron_wiring"), "FAST: typical backbox wiring"),
              (fetch("spfb_to_neuron"), "FAST: SPFB J7 BREAKOUT to a Neuron breakout header")])


def spfb(s):
    s.images([(fetch("spfb_headers"), "FAST: headers and fuses (F1 F2 F3 top row, F4 F5 F6 bottom row)")],
             max_h=290)
    s.cards([
        Card("Fuse map", "6x 5x20 mm", [
            ("F1", "48V_2 (H2)", "48", "J12 H2 + J10 CABINET H2"),
            ("F2", "BKBOX 12 V", "12", "J1, J2, J3"),
            ("F3", "CPU", "", "J4 CPU POWER"),
            ("F4", "48V_1 (H1)", "48", "J12 PLAYFIELD H1"),
            ("F5", "CAB12", "12", "J10 CABINET 12 V"),
            ("F6", "PLAY12", "12", "J12 PLAYFIELD 12 V"),
        ], strip=False, heads=("Fuse", "Circuit", "Wire", "Feeds", "Fitted (A)"),
            widths=(0.1, 0.22, 0.16, 0.34, 0.18),
            note="Use the lowest value that survives play; short each circuit once to prove it "
                 "blows. 12 V branches: 6 A maximum (7 A per 0.156\" pin)."),
        Card("J6  48V INPUT", "7-pin 0.156\"", [
            (1, "TG", "tg", "48 V PSU V-"), (2, "TG", "tg", "48 V PSU V-"),
            (3, "TG", "tg", "48 V PSU V-"), (4, "K", "key", ""),
            (5, "48", "48", "48 V PSU V+"), (6, "48", "48", "48 V PSU V+"),
            (7, "48", "48", "48 V PSU V+"),
        ], note="All six wires are required (18 AWG)."),
        Card("J5  12V/CPU INPUT", "7-pin 0.156\"", [
            (1, "G", "gnd", "host PC supply -"), (2, "CPU", "12", "host PC supply +"),
            (3, "K", "key", ""), (4, "G", "gnd", "12 V PSU V-"),
            (5, "G", "gnd", "12 V PSU V-"), (6, "12", "12", "12 V PSU V+"),
            (7, "12", "12", "12 V PSU V+"),
        ], note="Pins 1-2 feed J4 CPU POWER only. Wire them even for a 12 V host PC."),
        Card("J12  PLAYFIELD", "9-pin 0.156\"", [
            (1, "12", "12", "PIB J19 (F6)"), (2, "G", "gnd", "PIB J19"),
            (3, "K", "key", ""), (4, "TG", "tg", "PIB J19"), (5, "TG", "tg", "PIB J19"),
            (6, "TG", "tg", "PIB J19"), (7, "H2", "48", "PIB J19 (F1)"),
            (8, "H1", "48", "PIB J19 (F4)"), (9, "H1", "48", "PIB J19 (F4)"),
        ], note="Straight through to the Playfield Interchange J19. All 8 wires required. "
                 "Leave slack for the backbox to fold and the playfield to lift."),
        Card("J10  CABINET", "4-pin 0.156\"", [
            (1, "12", "12", "Cab I/O J3 12 (F5)"), (2, "G", "gnd", "Cab I/O J3 G"),
            (3, "TG", "tg", "Cab I/O J3 TG"), (4, "H2", "48", "Cab I/O J3 H2 (F1)"),
        ]),
        Card("J1 CONTROLLER / J2 BACKBOX / J3 TOPPER", "3-pin 0.156\", F2", [
            ("", "K", "key", ""), ("", "+", "12", "J1 to Neuron J1"),
            ("", "-", "gnd", ""),
        ], pin1=False),
        Card("J4  CPU POWER", "3-pin 0.156\", F3", [
            ("", "+", "12", "host PC (NUC)"), ("", "K", "key", ""), ("", "-", "gnd", ""),
        ], pin1=False),
        Card("J7  BREAKOUT", "5-pin 0.100\"", [
            (1, "G", "gnd", "Neuron breakout"), (2, "T", "", ""), (3, "R", "", ""),
            (4, "G", "gnd", ""), (5, "V", "", ""),
        ], note="Straight through to one Neuron breakout header. Config: port 1 (unconfirmed)."),
        Card("J8 ENA IN / J9 ENA OUT", "3-pin 0.100\" each", [
            ("J8", "pins 1+3", "", "closed = 48 V enabled"),
            ("J8", "machine", "", "coin door switch / jumper"),
            ("J9", "+", "sw", "Cab I/O switch input"),
            ("J9", "-", "swg", "Cab I/O switch return"),
        ], strip=False,
            note="FAST's software 48 V enable is not released (2026-09-25): J8 must be closed "
                 "or there is no 48 V. The 48V ENA LED shows the state."),
    ])
    s.notes("At the machine", [
        "The capacitors hold charge for hours after power-off. Treat them as live.",
        "48 V toxic ground and 12 V logic ground join only inside this board. Never link them elsewhere.",
        "J11 GND TIE (spade) ties DC grounds to chassis/earth: a deliberate decision, see FAST's ground guide.",
        "AC line fuse: FAST suggests 5 A for 240 V countries.",
    ])
    s.new_page()
    s.images([(fetch("spfb_switches"), "FAST: J8 ENA IN from the coin door switch, J9 ENA OUT to a switch input"),
              (fetch("spfb_to_pib"), "FAST: J12 PLAYFIELD to the Playfield Interchange J19")])


def pib(s):
    s.images([(fetch("pib_board"), "FAST: FP-PWR-0030 silkscreen")], max_h=170)
    s.cards([
        Card("J19  TO POWER FILTER BOARD", "9-pin 0.156\"", [
            (1, "12", "12", "SPFB J12"), (2, "G", "gnd", ""), (3, "K", "key", ""),
            (4, "TG", "tg", ""), (5, "TG", "tg", ""), (6, "TG", "tg", ""),
            (7, "H2", "48", ""), (8, "H1", "48", ""), (9, "H1", "48", ""),
        ]),
        Card("J5 / J6 / J11  48 V H1 to coils", "4-pin 0.156\"", [
            ("", "H1", "48", "blue to coils (diode band lug)"),
            ("", "TG", "tg", "to I/O board driver GND"),
            ("", "TG", "tg", "to I/O board driver GND"),
            ("", "TG", "tg", "to I/O board driver GND"),
        ], pin1=False, note="H1 (fuse F4) is for most coils, including the flippers."),
        Card("J10  48 V H2", "4-pin 0.156\"", [
            ("", "H2", "48", "magnets / isolated loads"), ("", "K", "key", ""),
            ("", "TG", "tg", ""), ("", "TG", "tg", ""),
        ], pin1=False, note="H2 (fuse F1) is shared with the cabinet (knocker)."),
        Card("J2 / J3 / J4  12 V OUT (high current)", "3-pin 0.156\", 7 A each", [
            ("", "K", "key", ""), ("", "+", "12", "expansion board 12 V IN"),
            ("", "-", "gnd", ""),
        ], pin1=False),
        Card("J1 / J7 / J12 / J13  FUSED 12 V (low current)", "3-pin 0.100\"", [
            ("", "+", "12", "opto emitter boards"), ("", "K", "key", ""),
            ("", "-", "gnd", ""),
        ], pin1=False, note="2.5 A combined, soldered self-resetting fuse F1. 22 AWG minimum."),
        Card("RJ45 jacks", "pass-through", [
            ("J8", "NODE IN", "", ""), ("J9", "NODE OUT", "", ""),
            ("J17", "NODE OUT", "", ""), ("J18", "NODE IN", "", ""),
            ("3x", "EXP BUS", "", "all bussed together"),
        ], strip=False, heads=("Jack", "Label", "Wire", "This machine", "Notes"),
            note="Loop jacks are straight couplers in pairs; direction does not matter."),
    ])
    s.new_page()
    s.images([(fetch("pib_outputs"), "FAST: Playfield Interchange outputs (pink box = playfield disconnect)")])


def io1616(s, asg):
    s.images([(fetch("1616_connectors"), "FAST: 1616 connectors"),
              (fetch("1616_mosfet"), "FAST: driver MOSFETs (IRL540NSTRLPBF)")], max_h=210)
    s.notes("Which 1616 is this?", [
        "Two 1616s are fitted: back and middle of the playfield. Print one copy per board.",
        "This board: [ ] back   [ ] middle      Loop order: ____      Part no. and rev: ______________",
        "io_loop name: [ ] top16   [ ] (second 1616, not yet in the config)      No devices are assigned to top16 yet.",
    ])
    b = "top16"
    s.cards([
        Card("J3  Drivers 0-7", "12-pin 0.156\"",
             drv_rows(["D0", "D1", "D2", "D3", "K", "D4", "D5", "D6", "D7", "GND", "GND", "GND"], b, asg)),
        Card("J4  Drivers 8-15", "12-pin 0.156\"",
             drv_rows(["D8", "D9", "D10", "D11", "D12", "K", "D13", "D14", "D15", "GND", "GND", "GND"], b, asg)),
        Card("J7  Switches 0-7", "11-pin 0.100\"",
             sw_rows(["S0", "S1", "S2", "S3", "K", "S4", "S5", "S6", "S7", "G", "G"], b, asg)),
        Card("J8  Switches 8-15", "11-pin 0.100\"",
             sw_rows(["S8", "S9", "S10", "K", "S11", "S12", "S13", "S14", "S15", "G", "G"], b, asg)),
    ])
    s.notes("At the board", [
        "J1 = NODE OUT, J2 = NODE IN (RJ45). The 11-pin DBI header near the jacks is not used.",
        "Driver GND pins are the toxic ground return to the Playfield Interchange TG pins. 48 V goes straight to each coil.",
        "Each header's key is in a different place, so a keyed housing only fits its own header.",
        "LEDs: STATUS slow flash = OK, fast = inactive/watchdog; LINK solid = loop OK; ACTIVE flashes on switch/driver activity.",
    ])


def io3208(s, asg):
    s.images([(fetch("3208_connectors"), "FAST: 3208 connectors"),
              (fetch("3208_mosfet"), "FAST: driver MOSFETs (IRL540NSTRLPBF)")], max_h=190)
    s.notes("At the board", [
        "io_loop name bottom32. 'This machine' is the config as it stands, not a switch test result.",
        "J1 = NODE OUT, J2 = NODE IN. Driver GND pins go to the Playfield Interchange TG pins.",
        "Key positions differ from the 1616: a 1616 J3 driver housing (key 5) will not fit a 3208 J4 (key 6).",
    ])


    b = "bottom32"
    s.cards([
        Card("J4  Drivers 0-7", "12-pin 0.156\"",
             drv_rows(["D0", "D1", "D2", "D3", "D4", "K", "D5", "D6", "D7", "GND", "GND", "GND"], b, asg)),
        Card("J8  Switches 0-7", "11-pin 0.100\"",
             sw_rows(["S0", "S1", "S2", "S3", "K", "S4", "S5", "S6", "S7", "G", "G"], b, asg)),
        Card("J3  Switches 8-15", "11-pin 0.100\"",
             sw_rows(["S8", "S9", "S10", "K", "S11", "S12", "S13", "S14", "S15", "G", "G"], b, asg)),
        Card("J6  Switches 16-23", "11-pin 0.100\"",
             sw_rows(["S16", "S17", "K", "S18", "S19", "S20", "S21", "S22", "S23", "G", "G"], b, asg)),
        Card("J9  Switches 24-31", "11-pin 0.100\"",
             sw_rows(["S24", "K", "S25", "S26", "S27", "S28", "S29", "S30", "S31", "G", "G"], b, asg)),
    ])
def cabinet(s, asg):
    s.images([(photo("cabinet_io.jpg"), "This machine: FP-I/O-0024-5 as fitted (2026-09-25)"),
              (fetch("cab_features"), "FAST: Cabinet I/O connection groups (rev -4)")], max_h=250)
    s.notes("Revision -5 on this machine differs from FAST's -4 docs", [
        "J1 is printed CABINET A (FAST: left). The right header is printed CABINET B (FAST: J9, right).",
        "BILL/CARD/TICKET is J11 (FAST: J10). SHAKER PWR is J12 (FAST: J11). J8 (5-pin, in the COIN DOOR group) is undocumented.",
        "On this board, pin 1 of CABINET B and BILL/CARD/TICKET (switch 16 / 21) is at the right-hand end.",
        "No 13-pin header is keyed. Cut a different unused pin on each and fit key plugs. Neuron firmware v2.13+ required.",
        "The NET jacks were empty on 2026-09-25: plug in before booting, or MPF's order: 1 for cab is wrong.",
    ])

    def sw(n):
        return asg["switches"].get("cab-%d" % n, "")

    def side(first, lamps, plan, lamp_use=("", "")):
        labs = ["S%d" % n for n in range(first, first + 8)]
        rows = []
        for i, lab in enumerate(labs, 1):
            n = first + i - 1
            rows.append((i, lab, "sw", plan.get(n, sw(n) or "cab-%d" % n)))
        rows += [(9, "G", "swg", plan.get("G", "")), (10, "5V", "5", ""),
                 (11, lamps[0], "drv", lamp_use[0]), (12, lamps[1], "drv", lamp_use[1]),
                 (13, "V+ 12V", "12", plan.get("V", ""))]
        return rows

    s.cards([
        Card("J1  CABINET A (left)", "13-pin 0.100\"", side(8, ("L2", "L3"), {
            8: "s_left_flipper <- opto SW1", 9: "cab-9 <- opto SW2",
            10: "s_start <- start button", "G": "left opto J1 pin 3 (GND)",
            "V": "left opto J1 pin 6 (12V)"}, ("start lamp - (cab-2)", ""))),
        Card("CABINET B (right)", "13-pin 0.100\"", side(16, ("L4", "L5"), {
            16: "s_right_flipper <- opto SW1", 17: "cab-17 <- opto SW2",
            21: "cab-21 (also on J11 pin 1)", 22: "cab-22 (also J11 pin 2)",
            23: "cab-23 (also J11 pin 3)", "G": "opto GND", "V": "opto board 12V"}),
            note="-5 labels for 5V, L4, L5, V+ not legible in the photo: meter before use."),
        Card("J4  COIN DOOR", "13-pin 0.100\"", side(0, ("L0", "L1"), {}),
             note="FAST -4 pinout; -5 labels not visible. Some boards misprint the input "
                  "labels 0-7-6-5-4-2-1-0: trust the pin order."),
        Card("J11  BILL/CARD/TICKET", "13-pin 0.100\" (FAST: J10)", [
            (1, "S21", "sw", "same input as CABINET B pin 6"),
            (2, "S22", "sw", "same input as CABINET B pin 7"),
            (3, "S23", "sw", "same input as CABINET B pin 8"),
            (4, "D6", "drv", "digital out, 200 mA"), (5, "D5 TTL", "drv", "shares L5"),
            (6, "D6 inv", "drv", "TTL, inverted"), (7, "G", "gnd", ""), (8, "G", "gnd", ""),
            (9, "G", "gnd", ""), (10, "5V", "5", ""), (11, "L3", "drv", "same as J1 pin 12"),
            (12, "L5", "drv", "same as CAB B pin 12"), (13, "V+ 12V", "12", "4 A rated"),
        ], note="No bill acceptor owned. Pinout per FAST -4; -5 pins 1-3 confirmed from photo."),
        Card("J2  KNOCKER", "4-pin 0.156\"", [
            (1, "D1", "drv", "driver 7 (cab-7): knocker or shaker"),
            (2, "K", "key", ""), (3, "TG", "tg", ""),
            (4, "H2", "48", "coil lug, diode band side"),
        ], note="D1 is software driver 7. On this -5 board D1 is at the right-hand end."),
        Card("J3  TO FILTER BOARD", "4-pin 0.156\"", [
            (1, "12", "12", "SPFB J10 12"), (2, "G", "gnd", "SPFB J10 G"),
            (3, "TG", "tg", "SPFB J10 TG"), (4, "H2", "48", "SPFB J10 H2"),
        ], note="On this -5 board 12 is at the right-hand end."),
        Card("J12  SHAKER PWR", "3-pin 0.156\" (FAST: J11)", [
            (1, "K", "key", ""), (2, "+ 12V", "12", ""), (3, "-", "gnd", ""),
        ], note="FAST -4 order. On -5, K is printed at the right-hand end; + and - not "
                "legible. Meter before connecting."),
        Card("J8  (undocumented, -5 only)", "5-pin, COIN DOOR group", [
            (1, "?", "", "ask FAST"), (2, "?", "", ""), (3, "?", "", ""),
            (4, "?", "", ""), (5, "?", "", ""),
        ], pin1=False),
        Card("Driver numbers", "software vs silkscreen", [
            ("0-5", "L0-L5", "drv", "LED/lamp, current-limited"),
            ("6", "D6", "drv", "200 mA open drain; TTL 20 mA"),
            ("5", "D5 TTL", "drv", "shares L5, 20 mA"),
            ("7", "D1 (J2)", "drv", "only high-current driver"),
        ], strip=False, heads=("MPF", "Silkscreen", "Wire", "Type", "Notes")),
    ])
    s.images([(fetch("cab_left"), "FAST: cabinet left switches and a lighted start button")],
             max_h=210, min_h=120)
    s.images([(fetch("cab_power"), "FAST: power from the SPFB J10 to the Cabinet I/O J3")],
             max_h=220, min_h=120)
    s.images([(fetch("cab_coin"), "FAST: example coin door wiring (door pinouts are not standard)")],
             max_h=260, min_h=140)


def exp_board(s, key, name, ports, servos):
    s.images([(fetch(key), "FAST: %s silkscreen" % name)], max_h=230 if not servos else 190)
    cards = [
        Card("12V IN", "3-pin 0.156\"", [
            (1, "K", "key", ""), (2, "+", "12", "PIB 12 V OUT (J2-J4)"), (3, "-", "gnd", ""),
        ], note="Pin 1 triangle at K in FAST's photo."),
        Card("LED PORT (each)", "4-pin 0.100\"", [
            ("", "G", "gnd", "LED chain ground"),
            ("", "C", "", "clock: not connected for WS2812"),
            ("", "D", "data", "LED data in"),
            ("", "V", "5", "5 V (made on the board)"),
        ], pin1=False, note="Order as printed in the board legend. Max 32 LEDs per port, "
                            "WS2812 3-wire only. Follow the data arrows on each LED."),
    ]
    if servos:
        cards.append(Card("SERVO 1-4 (J2-J5)", "3-pin 0.100\"", [
            ("", "S", "", "signal"), ("", "V", "", "servo supply (6 V, made on board)"),
            ("", "G", "gnd", "ground"),
        ], pin1=False, note="Order as printed; the legend's triangle is at S."))
    ports_card = Card("Ports and MPF numbers", "", ports, strip=False,
                      heads=("Port", "Label", "Wire", "MPF number / use", "Notes"),
                      widths=(0.1, 0.28, 0.0001, 0.37, 0.2499))
    if servos:
        s.cards(cards, cols=3)
        s.cards([ports_card], cols=2)
    else:
        s.cards(cards + [ports_card], cols=3)


def exp81(s):
    exp_board(s, "exp81", "FP-EXP-0081", [
        ("1-4", "PORT1-4", "", "<board>-1-<led> .. -4-", "bank 1: 10 W"),
        ("5-8", "PORT5-8", "", "<board>-5-<led> .. -8-", "bank 2: 10 W"),
        ("EXP", "2x RJ45", "", "any port to any port", "tree, not loop"),
        ("addr", "84", "", "default; jumpers 85-87", ""),
    ], servos=False)
    s.notes("Status", [
        "Not installed and not in the config yet. Add under fast: exp: boards: with model FP-EXP-0081.",
        "20 W sustained total (10 W per bank of 4 ports). MPF 0.80 needs EXP firmware 0.12 or newer.",
        "Bank split as ports 1-4 and 5-8 is assumed from FAST's '10 W per bank of 4 ports'.",
    ])


def exp71(s):
    exp_board(s, "exp71", "FP-EXP-0071", [
        ("1-4", "PORT1-4 (J9-J12)", "", "<board>-<port>-<led>", "10 W total"),
        ("S1-4", "SERVO1-4 (J2-J5)", "", "servos:", ""),
        ("EXP", "2x RJ45", "", "any port to any port", "tree, not loop"),
        ("addr", "B4", "", "default; jumpers B5-B7", ""),
    ], servos=True)
    s.notes("Status", [
        "Not installed and not in the config yet. Add under fast: exp: boards: with model FP-EXP-0071.",
        "MPF 0.80 needs EXP firmware 0.11 or newer. FAST's servo wiring guide is still 'coming soon'.",
    ])


def opto(s):
    s.images([(photo("opto_flipper.jpg"), "This machine: FP-SWI-7083-1 (2026-09-25)")], max_h=200)
    s.cards([
        Card("J1", "7-pin, pitch to measure", [
            (1, "SW1", "sw", "Cab A pin 1 (cab-8) / Cab B pin 1 (cab-16)"),
            (2, "SW2", "sw", "Cab A pin 2 (cab-9) / Cab B pin 2 (cab-17)"),
            (3, "GND", "swg", "Cab A/B pin 9 (G)"),
            (4, "GND", "swg", "left: start button common lug"),
            (5, "KEY", "key", "check if a pin is fitted"),
            (6, "12V", "12", "Cab A/B pin 13 (V+)"),
            (7, "12V", "12", "left: start lamp +; 6-7 joined"),
        ], widths=(0.07, 0.12, 0.14, 0.5, 0.17),
            note="Pin 1 marked by a triangle on the board. Housing: 15.24 mm pin 1 to 7 = 0.100\"; "
                 "15.0 mm = 2.5 mm (e.g. JST XH)."),
    ])
    s.notes("Bench test before connecting to the Cabinet I/O (output type unverified)", [
        "Power one board from a 12 V bench supply: + to pin 6, - to pin 3. Record current draw: ______ mA",
        "With nothing else connected, measure SW1 and SW2 to GND, released and pressed.",
        "Open, then near 0 V = open collector: suits a FAST switch input. About 12 V = driven: do not connect; ask FAST.",
        "Record which output trips first: ____. An output active when released needs type: NC in MPF.",
        "Not on FAST's part index. Undocumented board: everything here is from its silkscreen.",
    ])


def wiring(s):
    rows = [(WIRES[k][0], purpose, k, gauge) for k, purpose, gauge in [
        ("48", "48 V power", "18"), ("12", "12 V power", "18 / 22"),
        ("5", "5 V power", "18 / 22"), ("gnd", "DC ground returns (incl. toxic)", "18 / 22"),
        ("drv", "Driver control: coil to I/O driver pin", "18"),
        ("sw", "Switch inputs", "22"), ("swg", "Switch returns", "22"),
        ("data", "LED data", "22"),
    ]]
    s.cards([
        Card("FAST wire colour standard", "fastpinball.com/wiring/standards",
             [(r[0], r[1], r[2], r[3] + " AWG") for r in rows], strip=False,
             heads=("Colour", "Purpose", "Swatch", "Gauge", "This machine"),
             widths=(0.16, 0.4, 0.14, 0.14, 0.16),
             note="This machine uses black for the coil-to-driver wire; FAST uses grey/white "
                  "there and keeps black for ground returns. 0.156\" = 18 AWG, 7 A. "
                  "0.100\" = 22 AWG, 3 A."),
        Card("I/O loop order (fill in)", "Neuron OUT ... back to Neuron IN", [
            ("1", "", "", "", ""), ("2", "", "", "", ""),
            ("3", "", "", "", ""), ("4", "", "", "", ""),
            ("back", "Neuron IN", "", "", ""),
        ], strip=False, heads=("Order", "Board", "Wire", "Part no. / rev", "io_loop name"),
            widths=(0.12, 0.3, 0.0001, 0.33, 0.2499)),
    ])
    s.notes("Rules", [
        "Toxic ground (48 V returns) never joins the 12 V logic ground except inside the Smart Power Filter Board.",
        "Every coil and magnet gets a flyback diode, band to the 48 V lug. This repo uses 1N4004/1N4007.",
        "Switches need no diodes (direct inputs, no matrix). Opto receivers: collector to input, emitter to return.",
        "I/O loop: OUT to IN, closed ring; 99% of loop faults are two INs or two OUTs joined. EXP bus: any port, tree.",
    ])
    s.new_page()
    s.images([(fetch("io_loop"), "FAST: I/O loop ring through the Playfield Interchange"),
              (fetch("numbering"), "FAST: loop order sets switch and driver numbering")])


def cover(path, index, rev, date):
    c = canvas.Canvas(path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("FAST boards: reference sheets")
    c.setFillColor(BAR)
    c.rect(0, PAGE_H - 90, PAGE_W, 90, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(MARGIN, PAGE_H - 50, "Matrix Pinball: FAST board reference sheets")
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, PAGE_H - 72, "Generated %s from matrix-pinball %s. Pinouts: docs/12-fast-boards.md."
                 % (date, rev))
    y = PAGE_H - 125
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, "Contents")
    y -= 20
    c.setFont("Helvetica", 11)
    for name, page in index:
        c.drawString(MARGIN + 10, y, name)
        c.drawRightString(MARGIN + 420, y, "page %d" % page)
        y -= 17
    x0 = MARGIN + 470
    y = PAGE_H - 125
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x0, y, "How to read the sheets")
    lines = [
        "Pin strip: pin 1 is at the arrow end. Hatched box = key position.",
        "No arrow: order as printed on the board, pin 1 end not confirmed.",
        "Swatch = FAST's standard wire colour for that pin.",
        "'This machine' = config/config.yaml at generation time, not a switch test.",
        "Blank lines are for recording what you find at the machine.",
        "FAST diagrams are FAST Pinball's; sources are listed on each page.",
        "Always confirm pin 1 on the silkscreen, and meter anything marked",
        "'not legible' or 'unconfirmed' before connecting power.",
    ]
    c.setFont("Helvetica", 9.5)
    y -= 20
    for l in lines:
        c.drawString(x0, y, l)
        y -= 14
    c.showPage()
    c.save()


def main():
    rev = git_rev()
    date = datetime.date.today().isoformat()
    asg = load_assignments()
    os.makedirs(OUT, exist_ok=True)
    src = "fastpinball.com/products/ and /wiring/neuron/ (fetched at build time)"
    boards = [
        ("01-neuron", "Neuron controller", "FP-CPU-2000", "Backbox", neuron, ()),
        ("02-smart-power-filter", "Smart Power Filter Board", "FP-PWR-0007", "Backbox", spfb, ()),
        ("03-playfield-interchange", "Playfield Interchange Board", "FP-PWR-0030",
         "Rear of playfield", pib, ()),
        ("04-io-1616", "I/O 1616 (x2)", "FP-I/O-1616", "Playfield back and middle", io1616, (asg,)),
        ("05-io-3208", "I/O 3208", "FP-I/O-3208", "Playfield (io_loop: bottom32)", io3208, (asg,)),
        ("06-cabinet-io", "Cabinet I/O", "FP-I/O-0024-5", "Cabinet, front left (io_loop: cab)",
         cabinet, (asg,)),
        ("07-exp-0081", "Expansion board, 256 LEDs", "FP-EXP-0081", "Not installed", exp81, ()),
        ("08-exp-0071", "Expansion board, 128 LEDs + 4 servos", "FP-EXP-0071", "Not installed",
         exp71, ()),
        ("09-opto-flipper", "Opto flipper switch board (x2)", "FP-SWI-7083-1",
         "Cabinet, one per side", opto, ()),
        ("10-wiring-reference", "Wiring reference", "FAST standard vs this machine",
         "Whole machine", wiring, ()),
    ]
    files, index, page = [], [], 2
    for fname, title, part, where, fn, args in boards:
        path = os.path.join(OUT, fname + ".pdf")
        s = Sheet(path, title, part, where, src, rev, date)
        fn(s, *args)
        s.save()
        files.append(path)
        index.append(("%s  (%s)" % (title, part), page))
        page += len(PdfReader(path).pages)
        print("wrote", path)
    cover_path = os.path.join(CACHE, "cover.pdf")
    cover(cover_path, index, rev, date)
    w = PdfWriter()
    for p in [cover_path] + files:
        for pg in PdfReader(p).pages:
            w.add_page(pg)
    binder = os.path.join(OUT, "fast-boards-binder.pdf")
    with open(binder, "wb") as f:
        w.write(f)
    print("wrote", binder)


if __name__ == "__main__":
    sys.exit(main())
