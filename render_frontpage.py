#!/usr/bin/env python3
"""
Render the dense front page for news-image-20261117 Round 2.
1024x1024 JPEG, PIL only, deterministic, no network.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ── Constants ──────────────────────────────────────────────────────────────
W, H = 1024, 1024
JPEG_QUALITY = 88
MAX_BYTES = 1_048_576

# Colours (navy/cream newspaper palette)
CREAM = (245, 240, 232)
NAVY = (27, 42, 74)
DARK_NAVY = (13, 27, 46)
RED = (192, 57, 43)
TEXT_DARK = (44, 44, 44)
TEXT_MED = (74, 74, 74)
LIGHT_GRAY = (232, 224, 208)
WHITE = (255, 255, 255)
PIN_COL = (200, 30, 30)

# Fonts
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu/")
SERIF_BOLD = FONT_DIR / "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR / "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"


# ── Story Data ─────────────────────────────────────────────────────────────
LEADS = [
    {
        "num": 1,
        "cat": "EUROPE · UKRAINE WAR",
        "icon": "bridge",
        "headline": "Ukraine cripples the Kerch Bridge",
        "deck": "Kyiv says its strike severely damaged the road-and-rail link to occupied Crimea; Zelenskyy hails an 'unprecedented operation'.",
        "source": "Just Security",
    },
    {
        "num": 2,
        "cat": "MIDDLE EAST · GULF",
        "icon": "gulf",
        "headline": "Iran drones hit a US radar base in Bahrain",
        "deck": "Iran says it struck the Sheikh Isa radar site; Bahrain and the US say every drone was downed, no casualties.",
        "source": "Just Security / PBS",
    },
    {
        "num": 3,
        "cat": "ASIA · DIPLOMACY",
        "icon": "flags",
        "headline": "Trump lands in Manila for ASEAN and the Quad",
        "deck": "First Quad leaders' meeting in two years, ahead of a China trip for talks with Xi — and Putin.",
        "source": "NPR / BusinessWorld",
    },
]

CARDS = [
    {
        "num": 4,
        "cat": "EUROPE · AIRSPACE",
        "icon": "airspace",
        "headline": "Moldova shuts its airspace as drones cross",
        "deck": "Seven drones enter; one flies over Chisinau. Shut 16:27, central sector reopened 17:03.",
        "source": "Reuters",
    },
    {
        "num": 5,
        "cat": "ASIA · DEFENCE",
        "icon": "jets",
        "headline": "Japan scrambles jets as Russian planes intrude",
        "deck": "Two suspected Russian aircraft violate Japanese airspace; Tokyo protests strongly.",
        "source": "Just Security",
    },
    {
        "num": 6,
        "cat": "MIDDLE EAST · SANCTIONS",
        "icon": "sanctions",
        "headline": "UK sanctions firms building settlements",
        "deck": "Eight Israeli construction firms plus a group blocking Gaza aid face UK sanctions.",
        "source": "Just Security",
    },
    {
        "num": 7,
        "cat": "AFRICA · HEALTH",
        "icon": "health",
        "headline": "Ebola in Congo passes 11,000 cases",
        "deck": "WHO: 11,000+ cases, 5,400+ deaths; children a quarter of cases; 400–500 new cases a week.",
        "source": "WHO / UN News",
    },
    {
        "num": 8,
        "cat": "AMERICAS · HEALTH",
        "icon": "health",
        "headline": "US loses measles-free status after 26 years",
        "deck": "PAHO: US, Mexico, Bolivia lose elimination status; US cases hit 5,412, most since 1991.",
        "source": "PAHO / AP",
    },
    {
        "num": 9,
        "cat": "MARKETS · TECH",
        "icon": "tech",
        "headline": "Nvidia posts a $115.8bn quarter",
        "deck": "Revenue doubles to $115.8bn; Kress guides Q4 to $130bn. Shares rise after hours.",
        "source": "Reuters / CNN",
    },
    {
        "num": 10,
        "cat": "MARKETS · STOCKS",
        "icon": "stocks",
        "headline": "Dow sheds 849 points in a fourth straight fall",
        "deck": "S&P −1.03%, Nasdaq −0.74%; software sinks ahead of Nvidia results; Salesforce −9.5%.",
        "source": "AP",
    },
    {
        "num": 11,
        "cat": "CLIMATE · COP31",
        "icon": "climate",
        "headline": "COP31: draft deal splits talks in Antalya",
        "deck": "EU demands a clean-energy signal; ministers back a heat-and-cooling plan, $20m+ support.",
        "source": "Reuters / UNEP",
    },
    {
        "num": 12,
        "cat": "ASIA · WEATHER",
        "icon": "cyclone",
        "headline": "Cyclone Akvan bears down on India",
        "deck": "IMD: storm 610 km east of Chennai; winds to 145 km/h; landfall ~20 Nov, Andhra Pradesh.",
        "source": "IMD",
    },
    {
        "num": 13,
        "cat": "EUROPE · DISASTER",
        "icon": "crash",
        "headline": "An-12 crashes in Siberia; 19 dead",
        "deck": "Russian military transport down near Kemerovo; ministry cites preliminary technical fault.",
        "source": "Reuters",
    },
    {
        "num": 14,
        "cat": "EUROPE · POLITICS",
        "icon": "politics",
        "headline": "Serbia's student MPs take their seats",
        "deck": "Student List, 140 of 250 seats, sworn in after ending 14 years of Vucic party rule.",
        "source": "Reuters",
    },
    {
        "num": 15,
        "cat": "SPACE",
        "icon": "space",
        "headline": "Voyager 1 nears one light-day from Earth",
        "deck": "NASA asks the world to shine a light skyward tonight; its signals will soon take a full day.",
        "source": "NASA",
    },
]

ALSO = [
    "Russia launches mass strikes on Ukraine after the Kerch attack.",
    "Estonia to shut all Russia border crossings from 1 Dec.",
    "Sudan's civilian toll passes 2,230, the UN says.",
    "Bangladesh garment workers protest over pay.",
    "France: 146,000 march in a nationwide strike.",
    "Poland's Tusk survives a no-confidence vote.",
    "Turkey seizes opposition channel Sozcu TV.",
    "JPMorgan outage hits Zelle payments.",
    "Israel's Knesset votes for a new speaker.",
    "Rwanda named as a new asylum hub.",
    "Mozambique: the Mondlane trial opens.",
    "Moldova closes six border checkpoints with Ukraine.",
    "Russia rejects Moldova's drone accusations, saying no proof was given.",
    "Outage on a classified NSA network deepens the Wall St sell-off.",
    "Salesforce sinks 9.5%, the Dow's steepest fall.",
    "Home Depot beats profit forecasts but shares fall.",
    "Disney tops revenue forecasts, then gives back gains.",
    "United Airlines outage delays departing flights.",
    "Nvidia board rules out Huang's return; Kress stays interim chief.",
    "COP31: 23 countries back a wildfire-prevention plan.",
    "COP31: 95% of coastal nations now include ocean measures.",
    "Trump to meet Xi — and Putin — in China after Manila.",
    "ASEAN–US Special Summit opens in Manila.",
    "Australia shares the COP31 presidency with Turkiye.",
    "Anthropic IPO pricing watched as the AI boom is tested.",
    "WHO: Ebola still a global emergency as attacks hit clinics.",
    "Fed minutes due Wednesday as the rate path stays in focus.",
]

# Map pin positions: (num, label, x, y) in image coordinates (approx)
# Longitude -180..180 maps to x 0..1024, Latitude -90..90 maps to y 0..1024 (inverted)
MAP_PINS = [
    (1, "Kerch", 45.3, 35.5),
    (2, "Bahrain", 26.0, 50.6),
    (3, "Manila", 14.6, 121.0),
    (4, "Moldova", 47.0, 28.9),
    (5, "Japan", 36.0, 138.0),
    (6, "West Bank", 31.9, 35.2),
    (7, "DRC", -2.9, 23.7),
    (8, "USA", 39.0, -98.0),
    (9, "Santa Clara", 37.4, -122.0),
    (10, "New York", 40.7, -74.0),
    (11, "Antalya", 36.9, 30.7),
    (12, "Bay of Bengal", 12.2, 85.7),
    (13, "Kemerovo", 55.4, 86.1),
    (14, "Belgrade", 44.8, 20.5),
]

CONTINENTS = [
    ("North America", -120, 60),
    ("South America", -65, -12),
    ("Europe", -25, 58),
    ("Africa", 10, 15),
    ("Asia", 100, 35),
    ("Oceania", 145, -25),
]


# ── Helpers ────────────────────────────────────────────────────────────────
def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Wrap text to fit within max_w pixels. Returns list of lines."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = cur + " " + w
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    color: tuple[int, int, int],
    line_spacing: float = 1.15,
    align: str = "left",
) -> int:
    """Draw wrapped lines, return actual height used. Assert no overflow."""
    line_h = int(font.size * line_spacing)
    total_h = len(lines) * line_h
    if total_h > h:
        # shrink font until it fits
        while total_h > h and font.size > 6:
            font = ImageFont.truetype(str(font.path), font.size - 1)
            line_h = int(font.size * line_spacing)
            total_h = len(lines) * line_h
    for i, line in enumerate(lines):
        lx = x
        if align == "center":
            lx = x + (w - draw.textlength(line, font=font)) // 2
        elif align == "right":
            lx = x + w - draw.textlength(line, font=font)
        draw.text((lx, y + i * line_h), line, font=font, fill=color)
    return total_h


def draw_flat_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, kind: str, color=NAVY):
    """Draw a simple flat icon at center (cx, cy) within size box."""
    s = size // 2
    x, y = cx - s, cy - s
    if kind == "bridge":
        # Two arches for bridge
        draw.arc([x + 2, y + s // 2, x + s * 2 - 2, y + s * 2 - 2], 0, 180, fill=color, width=3)
        draw.arc([x + 2, y + s // 2 + 4, x + s * 2 - 2, y + s * 2 + 2], 0, 180, fill=color, width=2)
    elif kind == "gulf":
        # Simple Gulf shape - water blob
        draw.ellipse([x + 4, y + 4, x + s * 2 - 4, y + s * 2 - 4], outline=color, width=2)
        draw.ellipse([x + 8, y + 8, x + s * 2 - 8, y + s * 2 - 8], fill=(120, 140, 180))
    elif kind == "flags":
        # Four small flag poles
        for i in range(4):
            fx = x + 6 + i * (s // 2 - 2)
            draw.line([fx, y + s, fx, y + 4], fill=color, width=2)
            draw.polygon([(fx, y + 4), (fx + 8, y + 8), (fx, y + 12)], fill=color)
    elif kind == "airspace":
        draw.line([x + 4, y + s, x + s * 2 - 4, y + s], fill=color, width=2)
        # drone shape
        draw.ellipse([cx - 6, cy - 4, cx + 6, cy + 4], outline=color, width=2)
        draw.line([cx - 10, cy, cx + 10, cy], fill=color, width=1)
    elif kind == "jets":
        draw.polygon([(cx, y + 4), (x + s * 2 - 4, cy), (cx, y + s * 2 - 4)], fill=color)
        draw.polygon([(cx, y + 4), (x + 4, cy), (cx, y + s * 2 - 4)], fill=color)
    elif kind == "sanctions":
        draw.rectangle([x + 4, y + 4, x + s * 2 - 4, y + s * 2 - 4], outline=color, width=2)
        draw.line([x + 4, y + 4, x + s * 2 - 4, y + s * 2 - 4], fill=color, width=2)
        draw.line([x + s * 2 - 4, y + 4, x + 4, y + s * 2 - 4], fill=color, width=2)
    elif kind == "health":
        draw.rectangle([cx - 8, y + 4, cx + 8, y + s * 2 - 4], outline=color, width=2)
        draw.rectangle([cx - 4, y + 4, cx + 4, y + s * 2 - 4], fill=color)
        draw.rectangle([x + 4, cy - 4, x + s * 2 - 4, cy + 4], fill=color)
    elif kind == "tech":
        # Chip: outer square, inner square, pins — all coords valid for any size.
        draw.rectangle([x + 3, y + 3, x + s * 2 - 3, y + s * 2 - 3], outline=color, width=2)
        draw.rectangle([x + s - 3, y + s - 3, x + s + 3, y + s + 3], fill=color)
        for px in (x + s - 2, x + s + 2):
            draw.line([px, y, px, y + 3], fill=color, width=1)
            draw.line([px, y + s * 2 - 3, px, y + s * 2], fill=color, width=1)
        for py in (y + s - 2, y + s + 2):
            draw.line([x, py, x + 3, py], fill=color, width=1)
            draw.line([x + s * 2 - 3, py, x + s * 2, py], fill=color, width=1)
    elif kind == "stocks":
        # Downward chart
        pts = [(x + 4, y + 4), (x + s, y + s // 2), (x + s * 2 - 4, y + s * 2 - 4)]
        draw.line(pts, fill=RED, width=2)
        draw.line([x + 4, y + s * 2 - 4, x + s * 2 - 4, y + s * 2 - 4], fill=color, width=1)
        draw.line([x + 4, y + 4, x + 4, y + s * 2 - 4], fill=color, width=1)
    elif kind == "climate":
        draw.ellipse([x + 4, y + 4, x + s * 2 - 4, y + s * 2 - 4], outline=color, width=2)
        draw.polygon([(cx, y + 4), (x + s * 2 - 4, cy), (cx, y + s * 2 - 4)], outline=color, width=2)
    elif kind == "cyclone":
        # Spiral
        for r in range(4, s, 4):
            draw.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=color, width=1)
    elif kind == "crash":
        draw.polygon([(cx, y + 4), (x + 4, y + s * 2 - 4), (x + s * 2 - 4, y + s * 2 - 4)], fill=color)
        draw.line([cx, y + 4, cx, y + s * 2 - 4], fill=WHITE, width=2)
    elif kind == "politics":
        draw.rectangle([x + 4, y + 4, x + s * 2 - 4, y + s * 2 - 4], outline=color, width=2)
        for i in range(3):
            draw.line([x + 8, y + 10 + i * 8, x + s * 2 - 8, y + 10 + i * 8], fill=color, width=2)
    elif kind == "space":
        draw.ellipse([x + 4, y + 4, x + s * 2 - 4, y + s * 2 - 4], outline=color, width=2)
        draw.line([x + 4, cy, x + s * 2 - 4, cy], fill=color, width=1)
        draw.line([cx, y + 4, cx, y + s * 2 - 4], fill=color, width=1)
        # Small dot moving away (kept inside the icon box)
        draw.ellipse([cx + 4, cy - 3, cx + 9, cy + 3], fill=color)


def latlon_to_xy(lat: float, lon: float, map_x: int, map_y: int, map_w: int, map_h: int) -> tuple[int, int]:
    """Convert lat/lon to pixel coordinates within map rect.

    Latitude range is cropped to 80..-60 (no pins live outside it) so the
    strip reads taller than a full -90..90 equirectangular map would.
    """
    # lon -180..180 -> x 0..map_w
    # lat 80..-60 -> y 0..map_h (inverted)
    px = map_x + int((lon + 180) / 360 * map_w)
    py = map_y + int((80 - lat) / 140 * map_h)
    return px, py


def draw_dotted_world(draw: ImageDraw.ImageDraw, map_x: int, map_y: int, map_w: int, map_h: int):
    """Draw a stylised flat world map: coarse continent outlines, filled."""
    # (lon, lat) outlines — rough but recognisable at strip scale.
    continents_poly = [
        # North America
        [(-168, 66), (-150, 70), (-135, 70), (-125, 72), (-110, 73), (-95, 80),
         (-85, 80), (-80, 73), (-75, 72), (-65, 60), (-55, 52), (-60, 47),
         (-70, 42), (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21),
         (-97, 26), (-105, 22), (-110, 28), (-120, 34), (-125, 40), (-125, 48),
         (-135, 58), (-150, 60), (-165, 60)],
        # Greenland
        [(-58, 64), (-45, 60), (-30, 68), (-25, 76), (-40, 80), (-58, 76)],
        # South America
        [(-80, 10), (-75, 12), (-65, 12), (-60, 5), (-50, 0), (-40, -5),
         (-35, -10), (-40, -20), (-48, -28), (-55, -35), (-62, -42), (-68, -50),
         (-70, -55), (-75, -45), (-75, -30), (-70, -18), (-80, -5), (-82, 5)],
        # Europe
        [(-10, 36), (-9, 43), (-2, 48), (2, 51), (8, 57), (12, 56), (18, 56),
         (21, 59), (24, 60), (28, 62), (30, 70), (35, 68), (40, 66), (42, 60),
         (38, 55), (35, 50), (30, 46), (28, 44), (23, 40), (19, 42), (15, 44),
         (12, 44), (8, 44), (3, 43), (-2, 37), (-6, 36)],
        # Africa
        [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (32, 27), (35, 20),
         (38, 15), (43, 12), (48, 11), (51, 10), (46, 0), (40, -10), (35, -20),
         (32, -28), (26, -34), (20, -35), (15, -30), (12, -18), (12, -8),
         (9, 0), (4, 5), (-8, 5), (-15, 10), (-17, 15), (-15, 25), (-10, 30)],
        # Asia
        [(40, 68), (50, 70), (60, 72), (70, 72), (80, 73), (90, 75), (100, 76),
         (110, 76), (120, 73), (130, 72), (140, 72), (150, 70), (160, 66),
         (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 45),
         (142, 40), (140, 35), (135, 33), (130, 31), (127, 35), (122, 38),
         (120, 32), (115, 25), (110, 20), (108, 12), (105, 8), (100, 10),
         (98, 16), (95, 20), (92, 22), (88, 22), (85, 18), (80, 15), (77, 8),
         (74, 12), (70, 20), (66, 25), (62, 25), (58, 26), (55, 26), (52, 28),
         (50, 30), (48, 30), (44, 30), (42, 35), (40, 40), (40, 50), (42, 60)],
        # Japan
        [(130, 31), (135, 34), (140, 38), (142, 44), (145, 44), (142, 40),
         (138, 36), (133, 33)],
        # SE Asia islands (Indonesia)
        [(95, 5), (105, 0), (115, -5), (125, -8), (135, -5), (140, -8),
         (130, -2), (115, 2), (105, 5)],
        # Australia
        [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
         (132, -38), (137, -38), (140, -38), (142, -35), (145, -38), (147, -40),
         (150, -37), (153, -30), (153, -25), (150, -22), (146, -19), (142, -15),
         (140, -12), (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
         (122, -17), (118, -20)],
        # New Zealand
        [(167, -45), (170, -42), (174, -38), (177, -38), (175, -42), (170, -46)],
        # UK
        [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51), (-3, 50)],
    ]
    for poly in continents_poly:
        pts = [latlon_to_xy(lat, lon, map_x, map_y, map_w, map_h) for lon, lat in poly]
        draw.polygon(pts, fill=LIGHT_GRAY, outline=NAVY)
    # Continent labels so the squashed strip still reads as a world map.
    label_font = load_font(SANS_BOLD, 8)
    for name, lon, lat in CONTINENTS:
        lx, ly = latlon_to_xy(lat, lon, map_x, map_y, map_w, map_h)
        lw = draw.textlength(name, font=label_font)
        draw.text((lx - lw / 2, ly - 5), name.upper(), font=label_font, fill=TEXT_MED)


# ── Main Render ────────────────────────────────────────────────────────────
def render() -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Fonts (sizes tuned for density)
    f_kicker = load_font(SERIF_BOLD, 18)
    f_date = load_font(SERIF_BOLD, 56)
    f_count = load_font(SANS_BOLD, 16)
    f_lead_cat = load_font(SANS_BOLD, 11)
    f_lead_num = load_font(SANS_BOLD, 28)
    f_lead_head = load_font(SERIF_BOLD, 20)
    f_lead_deck = load_font(SANS, 11)
    f_card_num = load_font(SANS_BOLD, 14)
    f_card_cat = load_font(SANS_BOLD, 9)
    f_card_head = load_font(SERIF_BOLD, 13)
    f_card_deck = load_font(SANS, 9)
    f_map_title = load_font(SANS_BOLD, 13)
    f_map_legend = load_font(SANS, 9)
    f_also = load_font(SANS, 11)
    f_also_small = load_font(SANS, 10)
    f_datecheck = load_font(SANS, 10)
    f_footer = load_font(SANS, 10)
    f_footer_bold = load_font(SANS_BOLD, 10)

    # ── Y positions ────────────────────────────────────────────────────────
    y = 16
    margin = 24
    content_w = W - 2 * margin

    # MASTHEAD
    # Kicker
    draw.text((margin, y), "THE WORLD TODAY", font=f_kicker, fill=NAVY)
    y += 24
    # Date - big serif
    date_text = "Tuesday 17 November 2026"
    date_w = draw.textlength(date_text, font=f_date)
    draw.text((margin + (content_w - date_w) // 2, y), date_text, font=f_date, fill=DARK_NAVY)
    y += 60
    # Count bar
    count_text = "42 STORIES · 6 CONTINENTS · ONE DAY"
    count_w = draw.textlength(count_text, font=f_count)
    draw.text((margin + (content_w - count_w) // 2, y), count_text, font=f_count, fill=RED)
    y += 26

    # Divider line
    draw.line([(margin, y), (W - margin, y)], fill=NAVY, width=2)
    y += 14

    # ── 3 LEAD PANELS (row) ───────────────────────────────────────────────
    lead_w = (content_w - 2 * 12) // 3
    lead_h = 164
    lead_xs = [margin + i * (lead_w + 12) for i in range(3)]

    for i, lead in enumerate(LEADS):
        lx = lead_xs[i]
        # Panel background
        draw.rectangle([lx, y, lx + lead_w, y + lead_h], fill=WHITE, outline=NAVY, width=1)
        # Number circle (top-left) + category label to its right
        cx = lx + 18
        cy = y + 18
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED)
        _nt = str(lead["num"])
        _nw = draw.textlength(_nt, font=f_lead_num)
        draw.text((cx - _nw / 2, cy - 13), _nt, font=f_lead_num, fill=WHITE)
        # Icon (top-right)
        draw_flat_icon(draw, lx + lead_w - 26, y + 22, 32, lead["icon"], NAVY)
        # Category label
        draw.text((lx + 40, y + 10), lead["cat"], font=f_lead_cat, fill=RED)
        # Headline (wrap to 2 lines max)
        head_lines = wrap_text(draw, lead["headline"], f_lead_head, lead_w - 32)
        head_lines = head_lines[:2]
        hy = y + 44
        draw_text_box(draw, lx + 16, hy, lead_w - 32, 48, head_lines, f_lead_head, DARK_NAVY, 1.2)
        # Deck (3 lines)
        deck_lines = wrap_text(draw, lead["deck"], f_lead_deck, lead_w - 32)
        deck_lines = deck_lines[:3]
        draw_text_box(draw, lx + 16, y + 96, lead_w - 32, 46, deck_lines, f_lead_deck, TEXT_MED, 1.25)
        # Source line at bottom
        src_text = f"— {lead['source']}"
        src_w = draw.textlength(src_text, font=load_font(SANS, 9))
        draw.text((lx + lead_w - src_w - 12, y + lead_h - 16), src_text, font=load_font(SANS, 9), fill=TEXT_MED)

    y += lead_h + 12

    # ── 12 SMALL CARDS (3 rows × 4 cols) ──────────────────────────────────
    card_w = (content_w - 3 * 8) // 4
    card_h = 85
    for row in range(3):
        for col in range(4):
            idx = row * 4 + col
            if idx >= len(CARDS):
                break
            card = CARDS[idx]
            cx = margin + col * (card_w + 8)
            cy = y + row * (card_h + 8)
            # Card bg
            draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=WHITE, outline=LIGHT_GRAY, width=1)
            # Number
            draw.text((cx + 6, cy + 3), str(card["num"]), font=f_card_num, fill=RED)
            # Mini icon (top-right)
            draw_flat_icon(draw, cx + card_w - 14, cy + 14, 18, card["icon"], NAVY)
            # Category
            draw.text((cx + 6, cy + 18), card["cat"], font=f_card_cat, fill=RED)
            # Headline (2 lines max)
            head_lines = wrap_text(draw, card["headline"], f_card_head, card_w - 16)
            head_lines = head_lines[:2]
            draw_text_box(draw, cx + 6, cy + 30, card_w - 16, 30, head_lines, f_card_head, DARK_NAVY, 1.15)
            # Deck (2 lines, 9px so ~90 chars fit)
            deck_lines = wrap_text(draw, card["deck"], f_card_deck, card_w - 16)
            deck_lines = deck_lines[:2]
            draw_text_box(draw, cx + 6, cy + 62, card_w - 16, 22, deck_lines, f_card_deck, TEXT_MED, 1.15)

    y += 3 * (card_h + 8) + 6

    # ── WORLD MAP STRIP ───────────────────────────────────────────────────
    # Block budget: 152px total (title 18 + map 118 + legend 16).
    map_title_y = y
    draw.text((margin, map_title_y), "WHERE IT HAPPENED", font=f_map_title, fill=NAVY)
    map_y = y + 18
    map_x = margin
    map_w = content_w
    map_h = 118
    # Draw map
    draw_dotted_world(draw, map_x, map_y, map_w, map_h)
    # Pins (European cluster staggered vertically so pins do not overlap)
    pin_dy = {1: 14, 4: -14, 6: 20, 11: 4, 14: -4}
    for num, label, lat, lon in MAP_PINS:
        px, py = latlon_to_xy(lat, lon, map_x, map_y, map_w, map_h)
        py += pin_dy.get(num, 0)
        # Pin circle
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=PIN_COL, outline=WHITE, width=1)
        _pt = str(num)
        _pw = draw.textlength(_pt, font=load_font(SANS_BOLD, 8))
        draw.text((px - _pw / 2, py - 6), _pt, font=load_font(SANS_BOLD, 8), fill=WHITE)
    # Legend line under the map
    leg_y = map_y + map_h + 3
    draw.text((map_x, leg_y), "15 SPACE — beyond the map", font=f_map_legend, fill=TEXT_MED)
    leg_x = map_x + 210
    for name, _, _ in CONTINENTS:
        draw.rectangle([leg_x, leg_y + 1, leg_x + 10, leg_y + 9], fill=LIGHT_GRAY, outline=NAVY)
        draw.text((leg_x + 14, leg_y), name, font=f_map_legend, fill=TEXT_MED)
        leg_x += 92

    y = map_y + map_h + 16

    # ── ALSO ON TUESDAY (two columns, 14 + 13 items, one line each) ───────
    also_title = "ALSO ON TUESDAY 17 NOVEMBER"
    draw.text((margin, y), also_title, font=f_map_title, fill=NAVY)
    y += 20
    col_w = (content_w - 16) // 2
    half = (len(ALSO) + 1) // 2
    left_items = ALSO[:half]
    right_items = ALSO[half:]
    also_lead = 12

    for col_idx, items in enumerate([left_items, right_items]):
        cx = margin + col_idx * (col_w + 16)
        cy = y
        for j, item in enumerate(items):
            num = 16 + col_idx * half + j
            text = f"{num}. {item}"
            font = f_also
            if draw.textlength(text, font=font) > col_w - 8:
                font = f_also_small
            assert draw.textlength(text, font=font) <= col_w - 8, \
                "ALSO line too wide: %s" % text
            draw.text((cx + 4, cy), text, font=font, fill=TEXT_DARK)
            cy += also_lead

    y += half * also_lead + 6

    # ── DATE CHECK BOX ────────────────────────────────────────────────────
    dc_text = "Left out on purpose: the Depardieu appeal — announced Monday 16 November, not Tuesday."
    draw.rectangle([margin, y, W - margin, y + 26], outline=NAVY, width=1)
    dc_font = load_font(SANS, 10)
    dc_w = draw.textlength(dc_text, font=dc_font)
    draw.text((margin + (content_w - dc_w) // 2, y + 7), dc_text, font=dc_font, fill=TEXT_MED)
    y += 32

    # ── FOOTER ────────────────────────────────────────────────────────────
    footer1 = "Every story here happened or was first reported on Tuesday 17 November 2026. Disputed claims are attributed."
    footer2 = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN."
    f1_w = draw.textlength(footer1, font=f_footer)
    f2_w = draw.textlength(footer2, font=f_footer_bold)
    draw.text((margin + (content_w - f1_w) // 2, y), footer1, font=f_footer, fill=TEXT_MED)
    y += 15
    draw.text((margin + (content_w - f2_w) // 2, y), footer2, font=f_footer_bold, fill=NAVY)
    assert y + 12 <= H, "layout overflow: footer ends at y=%d" % y

    return img


def verify_image(path: Path) -> tuple[int, str, str]:
    """Verify entry.png: size, mode, decode, bytes <= 1MiB. Returns (bytes, sha256, md5)."""
    with Image.open(path) as im:
        im.load()  # full decode
        if im.size != (W, H):
            raise ValueError(f"Wrong size: {im.size}, expected {(W, H)}")
        if im.mode != "RGB":
            raise ValueError(f"Wrong mode: {im.mode}, expected RGB")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"File too large: {size} > {MAX_BYTES}")
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    return size, sha256, md5


def main() -> int:
    print("Rendering front page...", file=sys.stderr)
    img = render()
    out_path = Path("entry.png")
    img.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    print(f"Saved {out_path}", file=sys.stderr)

    size, sha256, md5 = verify_image(out_path)
    print(f"Size: {size} bytes", file=sys.stderr)
    print(f"SHA-256: {sha256}", file=sys.stderr)
    print(f"MD5: {md5}", file=sys.stderr)
    print(f"Stories rendered: 3 leads + 12 cards + {len(ALSO)} also = {3 + 12 + len(ALSO)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
