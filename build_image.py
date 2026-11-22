#!/usr/bin/env python3
"""Paint a newspaper front page summing up Sunday 22 November 2026.

The story list was researched from public reporting on the morning of
22 Nov 2026 (about 01:00 UTC): Reuters, BBC, NYT, USGS, IANS and The
Hindu. Every headline below is a paraphrase of a story that happened or
was first reported on 22 November 2026 in some time zone. The drawing
code is original to this session. Output is deterministic: fixed palette,
fixed fonts, no clock and no randomness, so re-running the script writes
identical PNG bytes.
"""

from __future__ import annotations

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 20
CONTENT = W - 2 * MARGIN  # 984

CREAM = (247, 243, 234)
PAPER_CARD = (255, 253, 247)
BLACK = (22, 22, 22)
GREY = (74, 74, 74)
PALE = (148, 140, 126)
RED = (172, 32, 28)
BLUE = (28, 62, 112)
TAN = (232, 224, 205)
GOLD = (176, 128, 28)
GREEN = (46, 110, 58)
PURPLE = (110, 46, 96)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ------------------------------------------------------------------ news ---
# (tag, city, headline, one-line deck). All checked against reporting on
# the morning of 22 Nov 2026; see README.md for the source list.
TOP_STORY = (
    "CLIMATE",
    "Antalya, Turkey",
    "COP31 nears a deal at last",
    "After two weeks deadlocked over fossil fuels, negotiators in Antalya "
    "were handed a new package late on Saturday and told to gather again "
    "on Sunday morning to approve it. The summit president, Murat Kurum, "
    "said the text was one every party could agree on.",
)
SECOND_STORIES = [
    (
        "DISASTER",
        "Junin, Peru",
        "A 6.7 quake shakes Peru's Andes",
        "The tremor struck near Carhuamayo and was felt in Lima; no damage "
        "or casualties were reported at once.",
    ),
    (
        "CRIME",
        "Mexico",
        "Mexico captures a cartel kingpin",
        "'El Chapo Isidro', one of the FBI's ten most wanted, was arrested "
        "in a shoot-out; 11 people were killed as violence flared in Sinaloa.",
    ),
]

# 24 further stories, three columns by eight rows.
MORE_STORIES = [
    ("CYBER", "Washington", "FBI probes a hack of its crime database",
     "The bureau is investigating an apparent breach of its criminal records system."),
    ("BALTIC", "Gulf of Finland", "Drones hit a Russian cargo ship",
     "Finland tightened security after the attack; Ukrainian forces are suspected."),
    ("UKRAINE", "Kyiv", "Zelensky calls bridge strikes 'fair response'",
     "The president spoke as he met Britain's Wes Streeting in Kyiv."),
    ("ESTONIA", "Tallinn", "Estonia to shut its Russia border on 1 December",
     "Five crossings close after a sabotage attempt at a defence site near the capital."),
    ("DENMARK", "Copenhagen", "Denmark accuses Russia of a murder plot",
     "Copenhagen says Moscow plotted to assassinate a US-Ukrainian rapper."),
    ("MYANMAR", "The Hague", "Myanmar rejects the UN court's genocide ruling",
     "France asked the Security Council to act after Myanmar spurned the ruling."),
    ("GULF", "Washington", "Trump seeks a lasting deal with Iran",
     "The president said an accord could last 20 years; Tehran's terms were 'unacceptable'."),
    ("INDIA", "Patna", "Modi opens the Nitish Setu bridge in Bihar",
     "The new crossing links Patna with Vaishali district across the Ganges."),
    ("WEATHER", "Ranchi", "Cyclone Akvan cancels 14 flights",
     "Flights were grounded at Ranchi airport as the storm moved inland."),
    ("ASIA", "New Delhi", "Japan to train live-fire in India, a first",
     "Japanese forces will use Indian facilities for live-fire training."),
    ("BRAZIL", "Brasilia", "Bolsonaro admitted to intensive care",
     "The imprisoned ex-president was taken to hospital with a bowel obstruction."),
    ("ISRAEL", "Jerusalem", "Eisenkot invites Likud to coalition talks",
     "Government formation talks opened after the election stalemate."),
    ("FRANCE", "Paris", "Depardieu probed over gang-rape claim",
     "France is investigating the actor and an author over the allegation."),
    ("UNITED STATES", "Los Angeles", "Palisades fire arsonist convicted",
     "A man was convicted of starting the Los Angeles wildfire."),
    ("COURTS", "Missouri", "Judge approves a $7.25bn Roundup deal",
     "The settlement covers cancer claims over the weedkiller."),
    ("MARKETS", "New York", "Tech sell-off drags markets down",
     "Shares slid as Anthropic stock fell in a broad tech retreat."),
    ("RUGBY", "Dublin", "Ireland stun South Africa 20-17",
     "Two Baloucoune tries beat the world champions; the Springboks still reach the final."),
    ("FOOTBALL", "Newcastle", "Arsenal six clear after Newcastle draw",
     "A thrilling 2-2 draw kept Arsenal top of the Premier League."),
    ("FOOTBALL", "London", "Leeds thrash Chelsea 4-1",
     "Noah Okafor scored twice at Stamford Bridge as Leeds won away."),
    ("FORMULA 1", "Las Vegas", "Antonelli fastest, Verstappen on pole",
     "A five-place penalty drops the champion to sixth; the race runs tonight."),
    ("BOXING", "Las Vegas", "Lauren Price undisputed at welterweight",
     "Price unified the division to become undisputed champion."),
    ("CRICKET", "Melbourne", "Cummins keeps the Test captaincy",
     "Cricket Australia gave Pat Cummins unanimous backing to stay captain."),
    ("SOUTH AFRICA", "Johannesburg", "ANC fights to hold its key cities",
     "The party battles to keep control after an election setback."),
    ("CULTURE", "London", "Spitting Image co-creator dies at 85",
     "Peter Fluck, who co-created the satirical puppet show, has died."),
]

# (time WIB, what happened) — times approximate.
DAY_CLOCK = [
    ("02:45", "Ireland beat South Africa 20-17 in Dublin"),
    ("06:31", "Mexico arrests 'El Chapo Isidro'"),
    ("06:39", "COP31 unveils its final-deal package"),
    ("06:45", "Peru quake reported, magnitude 6.7"),
    ("07:10", "FBI opens its crime-database hack probe"),
    ("11:30", "Modi opens the Nitish Setu bridge"),
]

DAY_NUMBERS = [
    ("27", "verified stories"),
    ("6.7", "Peru quake magnitude"),
    ("20-17", "Ireland stun South Africa"),
    ("$7.25bn", "Roundup settlement"),
    ("14", "flights cancelled at Ranchi"),
]

# Numbered dots on the sketch map: (x, y, number, label, label side).
# Label side "r" puts the name right of the dot, "l" left, "b" below.
MAP_DOTS = [
    (85, 56, "1", "Lima", "r"),
    (150, 28, "2", "Mexico City", "r"),
    (340, 18, "3", "Dublin", "b"),
    (398, 32, "4", "Tallinn", "r"),
    (432, 50, "5", "Antalya", "r"),
    (505, 46, "6", "Delhi", "b"),
    (582, 68, "7", "Wellington", "l"),
]

NOT_TODAY = [
    "Russian missiles in Poland (21 Nov), BepiColombo reaches Mercury (21 Nov), Dragon splashdown (21 Nov) - filed yesterday.",
    "ICJ genocide ruling (19 Nov), Crimean Bridge strikes (19 Nov), Anthropic IPO (19-20 Nov) - older than today.",
    "F1 Las Vegas race result - the race starts at 8pm local on Saturday, after this page was drawn.",
]


# -------------------------------------------------------------- utilities ---
class Pen:
    """Font cache and text measuring for one drawing context."""

    def __init__(self, draw: ImageDraw.ImageDraw):
        self.draw = draw
        self._fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

    def font(self, path: str, size: int) -> ImageFont.FreeTypeFont:
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(path, size)
        return self._fonts[key]

    def measure(self, text: str, path: str, size: int) -> float:
        return self.draw.textlength(text, font=self.font(path, size))

    def lines(self, text: str, path: str, size: int, width: int) -> list[str]:
        out: list[str] = []
        current = ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if self.measure(trial, path, size) <= width or not current:
                current = trial
            else:
                out.append(current)
                current = word
        if current:
            out.append(current)
        return out

    def one_line(self, text: str, path: str, size: int, width: int) -> str:
        if self.measure(text, path, size) <= width:
            return text
        cut = text
        while cut and self.measure(cut + "...", path, size) > width:
            cut = cut[:-1].rstrip()
        return cut + "..."


def rule(draw: ImageDraw.ImageDraw, x0: int, y: int, x1: int,
         thick: int = 2, colour=BLACK) -> None:
    draw.line([(x0, y), (x1, y)], fill=colour, width=thick)


class Page:
    """Lays out the front page band by band, top to bottom."""

    def __init__(self) -> None:
        self.img = Image.new("RGB", (W, H), CREAM)
        self.d = ImageDraw.Draw(self.img)
        self.p = Pen(self.d)

    # -- masthead ---------------------------------------------------
    def masthead(self) -> int:
        d, p = self.d, self.p
        d.text((MARGIN, 14), "THE WORLD IN ONE IMAGE  |  ONE DAY, EVERYWHERE  |  No. 326",
               font=p.font(SANS_B, 12), fill=RED)
        right = "PRICE: ONE READ"
        d.text((W - MARGIN - p.measure(right, SANS_B, 12), 14), right,
               font=p.font(SANS_B, 12), fill=GREY)
        rule(d, MARGIN, 36, W - MARGIN, 3)
        rule(d, MARGIN, 41, W - MARGIN, 1)
        d.text((MARGIN, 50), "Sunday 22 November 2026",
               font=p.font(SERIF_B, 48), fill=BLACK)
        deck = ("Twenty-seven verified stories from Sunday - a climate deal nearly done, "
                "a quake in the Andes, a cartel boss in cuffs, and a rugby upset in Dublin.")
        for i, line in enumerate(p.lines(deck, SANS, 13, CONTENT)):
            d.text((MARGIN, 112 + i * 17), line, font=p.font(SANS, 13), fill=GREY)
        rule(d, MARGIN, 148, W - MARGIN, 3)
        return 158

    # -- numbers strip ----------------------------------------------
    def numbers(self, y: int) -> int:
        d, p = self.d, self.p
        cell = CONTENT // len(DAY_NUMBERS)
        for i, (big, small) in enumerate(DAY_NUMBERS):
            x = MARGIN + i * cell
            d.rectangle([x + 2, y, x + cell - 2, y + 40], fill=PAPER_CARD,
                        outline=PALE)
            d.text((x + 10, y + 5), big, font=p.font(SERIF_B, 17),
                   fill=RED if i % 2 == 0 else BLUE)
            d.text((x + 10, y + 24), small, font=p.font(SANS, 10), fill=GREY)
        return y + 48

    # -- top stories -------------------------------------------------
    def top_stories(self, y: int) -> int:
        d, p = self.d, self.p
        left_w = 640
        right_w = CONTENT - left_w - 12
        rx = MARGIN + left_w + 12

        tag, city, head, deck = TOP_STORY
        d.rectangle([MARGIN, y, MARGIN + left_w, y + 116], fill=PAPER_CARD,
                    outline=BLACK)
        d.rectangle([MARGIN, y, MARGIN + 8, y + 116], fill=RED)
        d.text((MARGIN + 18, y + 8), f"{tag}  -  {city.upper()}",
               font=p.font(SANS_B, 11), fill=RED)
        d.text((MARGIN + 18, y + 26), head, font=p.font(SERIF_B, 24),
               fill=BLACK)
        for i, line in enumerate(p.lines(deck, SANS, 12, left_w - 36)):
            d.text((MARGIN + 18, y + 60 + i * 16), line,
                   font=p.font(SANS, 12), fill=GREY)

        for slot, (tag, city, head, deck) in enumerate(SECOND_STORIES):
            sy = y + slot * 59
            d.rectangle([rx, sy, rx + right_w, sy + 57], fill=PAPER_CARD,
                        outline=PALE)
            d.rectangle([rx, sy, rx + 6, sy + 57],
                        fill=BLUE if slot == 0 else RED)
            d.text((rx + 14, sy + 4), f"{tag}  -  {city.upper()}",
                   font=p.font(SANS_B, 9), fill=BLUE)
            head_fit = p.one_line(head, SERIF_B, 13, right_w - 28)
            d.text((rx + 14, sy + 16), head_fit, font=p.font(SERIF_B, 13),
                   fill=BLACK)
            for j, line in enumerate(p.lines(deck, SANS, 9, right_w - 28)[:2]):
                d.text((rx + 14, sy + 35 + j * 11), line,
                       font=p.font(SANS, 9), fill=GREY)
        return y + 116

    # -- timeline ----------------------------------------------------
    def clock(self, y: int) -> int:
        d, p = self.d, self.p
        d.text((MARGIN, y), "THE DAY, AS IT UNFOLDED  (WIB, approximate)",
               font=p.font(SANS_B, 11), fill=BLACK)
        axis = y + 38
        rule(d, MARGIN, axis, W - MARGIN, 2, PALE)
        slot = CONTENT // len(DAY_CLOCK)
        for i, (when, what) in enumerate(DAY_CLOCK):
            cx = MARGIN + i * slot + slot // 2
            d.ellipse([cx - 5, axis - 5, cx + 5, axis + 5], fill=RED,
                      outline=CREAM)
            d.text((cx - p.measure(when, SANS_B, 11) / 2, axis - 20), when,
                   font=p.font(SANS_B, 11), fill=BLACK)
            for j, line in enumerate(p.lines(what, SANS, 9, slot - 12)[:2]):
                d.text((cx - slot // 2 + 6, axis + 10 + j * 12), line,
                       font=p.font(SANS, 9), fill=GREY)
        return y + 76

    # -- story grid --------------------------------------------------
    def grid(self, y: int) -> int:
        d, p = self.d, self.p
        cols = 3
        gap = 10
        card_w = (CONTENT - gap * (cols - 1)) // cols
        row_h = 44
        palette = [RED, BLUE, GOLD, GREEN, PURPLE, (150, 90, 20)]
        for i, (tag, city, head, deck) in enumerate(MORE_STORIES):
            row, col = divmod(i, cols)
            x = MARGIN + col * (card_w + gap)
            cy = y + row * (row_h + 3)
            d.rectangle([x, cy, x + card_w, cy + row_h], fill=PAPER_CARD,
                        outline=PALE)
            d.rectangle([x, cy, x + 4, cy + row_h],
                        fill=palette[i % len(palette)])
            title = p.one_line(head, SANS_B, 11, card_w - 16)
            d.text((x + 12, cy + 4), title, font=p.font(SANS_B, 11), fill=BLACK)
            body = f"{tag} - {city} - {deck}"
            for j, line in enumerate(p.lines(body, SANS, 9, card_w - 16)[:2]):
                d.text((x + 12, cy + 19 + j * 11), line,
                       font=p.font(SANS, 9), fill=GREY)
        rows = (len(MORE_STORIES) + cols - 1) // cols
        return y + rows * (row_h + 3) - 3

    # -- sketch map + one-line verdict -------------------------------
    def map_verdict(self, y: int) -> int:
        d, p = self.d, self.p
        map_w = 620
        map_h = 88
        d.rectangle([MARGIN, y, MARGIN + map_w, y + map_h], fill=PAPER_CARD,
                    outline=BLACK)
        d.text((MARGIN + 10, y + 6), "WHERE IT HAPPENED - SCHEMATIC, NOT TO SCALE",
               font=p.font(SANS_B, 10), fill=BLUE)
        for (bx, by, bw, bh) in [(28, 18, 120, 42), (150, 48, 90, 24),
                                 (300, 10, 130, 30), (330, 46, 80, 26),
                                 (440, 14, 130, 40), (560, 54, 44, 20)]:
            d.ellipse([MARGIN + bx, y + by, MARGIN + bx + bw, y + by + bh],
                      fill=TAN, outline=PALE)
        for (px, py, num, label, side) in MAP_DOTS:
            d.ellipse([MARGIN + px - 8, y + py - 8, MARGIN + px + 8, y + py + 8],
                      fill=RED, outline=CREAM)
            d.text((MARGIN + px - 3, y + py - 6), num,
                   font=p.font(SANS_B, 10), fill=(255, 255, 255))
            if not label:
                continue
            lw = p.measure(label, SANS_B, 9)
            if side == "r":
                lx, ly = MARGIN + px + 11, y + py - 5
            elif side == "l":
                lx, ly = MARGIN + px - 11 - lw, y + py - 5
            else:
                lx, ly = MARGIN + px - lw / 2, y + py + 10
            d.text((lx, ly), label, font=p.font(SANS_B, 9), fill=BLACK)
        key = ("1 Lima  2 Mexico City  3 Dublin  4 Tallinn  5 Antalya  "
               "6 Delhi  7 Wellington")
        d.text((MARGIN + 10, y + map_h - 14), key,
               font=p.font(SANS, 9), fill=GREY)

        vx = MARGIN + map_w + 12
        vw = CONTENT - map_w - 12
        d.rectangle([vx, y, vx + vw, y + map_h], fill=BLACK)
        d.text((vx + 12, y + 8), "THE DAY IN ONE LINE",
               font=p.font(SANS_B, 10), fill=(232, 200, 120))
        verdict = ("A climate deal nearly done, a quake in the Andes, a "
                   "cartel boss in cuffs - one Sunday, every continent.")
        for i, line in enumerate(p.lines(verdict, SERIF, 12, vw - 24)):
            d.text((vx + 12, y + 26 + i * 16), line,
                   font=p.font(SERIF, 12), fill=CREAM)
        d.text((vx + 12, y + map_h - 18),
               "Watch tomorrow: COP31 vote, Las Vegas race, Wall St open.",
               font=p.font(SANS, 9), fill=(200, 200, 200))
        return y + map_h + 10

    # -- date check + footer -----------------------------------------
    def date_check(self, y: int) -> int:
        d, p = self.d, self.p
        d.rectangle([MARGIN, y, W - MARGIN, y + 50], fill=TAN, outline=PALE)
        d.text((MARGIN + 10, y + 6), "DATE CHECK - LEFT OFF ON PURPOSE",
               font=p.font(SANS_B, 10), fill=RED)
        for i, item in enumerate(NOT_TODAY):
            d.text((MARGIN + 10, y + 20 + i * 10), "- " + item,
                   font=p.font(SANS, 9), fill=GREY)
        return y + 58

    def footer(self, y: int) -> None:
        d, p = self.d, self.p
        rule(d, MARGIN, y, W - MARGIN, 2)
        foot = ("Sources, 22 Nov 2026 ~01:00 UTC: Reuters, BBC, NYT, USGS, "
                "IANS, The Hindu. 27 stories. One image, one day.")
        d.text((MARGIN, y + 6), foot, font=p.font(SANS, 9), fill=GREY)

    def render(self) -> Image.Image:
        y = self.masthead()
        y = self.numbers(y)
        y = self.top_stories(y + 8)
        y = self.clock(y + 8)
        y = self.grid(y + 8)
        y = self.map_verdict(y + 8)
        y = self.date_check(y)
        self.footer(y)
        return self.img


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    sheet = Page().render()
    sheet.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
