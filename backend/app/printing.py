import calendar
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]

MONTHS = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
          "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

REGULAR_FONTS = [
    ROOT / "assets" / "fonts" / "regular.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
BOLD_FONTS = [
    ROOT / "assets" / "fonts" / "bold.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

FRAME_WIDTHS = {"thin": 6, "medium": 14, "thick": 26}
TEXT_DARK = (47, 62, 78)
TEXT_SOFT = (107, 122, 137)


@dataclass
class PrintOptions:
    frame_style: str = "line"      # none / line / double / rounded / dashed
    frame_color: str = "#9CCBEA"
    frame_width: str = "medium"    # thin / medium / thick
    corners: str = "round"         # round / square
    orientation: str = "portrait"  # portrait / landscape
    show_logo: bool = True


@lru_cache(maxsize=64)
def load_font(size: int, bold: bool = False):
    for path in (BOLD_FONTS if bold else REGULAR_FONTS):
        try:
            if Path(path).exists():
                return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def hex_to_rgb(value: str):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def tint(color, amount):
    """Освітлює колір: amount 0 = колір, 1 = білий."""
    return tuple(int(c + (255 - c) * amount) for c in color)


def rounded_mask(size, radius, scale=3):
    w, h = size
    if radius <= 0:
        return Image.new("L", size, 255)
    big = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        [0, 0, w * scale - 1, h * scale - 1], radius=radius * scale, fill=255)
    return big.resize(size, Image.LANCZOS)


def dashed_rect(draw, box, color, width, dash, gap):
    x0, y0, x1, y1 = box
    x = x0
    while x < x1:
        end = min(x + dash, x1)
        draw.line([(x, y0), (end, y0)], fill=color, width=width)
        draw.line([(x, y1), (end, y1)], fill=color, width=width)
        x += dash + gap
    y = y0
    while y < y1:
        end = min(y + dash, y1)
        draw.line([(x0, y), (x0, end)], fill=color, width=width)
        draw.line([(x1, y), (x1, end)], fill=color, width=width)
        y += dash + gap


def draw_frame(draw, W, H, opts, S):
    style = opts.frame_style
    if style == "none":
        return
    color = hex_to_rgb(opts.frame_color)
    w = S(FRAME_WIDTHS.get(opts.frame_width, 14))
    inset = S(70)
    box = [inset, inset, W - inset, H - inset]

    if style == "line":
        draw.rectangle(box, outline=color, width=w)
    elif style == "rounded":
        draw.rounded_rectangle(box, radius=S(90), outline=color, width=w)
    elif style == "double":
        draw.rounded_rectangle(box, radius=S(30), outline=color, width=w)
        off = w + S(20)
        inner = [box[0] + off, box[1] + off, box[2] - off, box[3] - off]
        draw.rounded_rectangle(inner, radius=S(18), outline=color, width=max(1, w // 2))
    elif style == "dashed":
        half = w // 2
        dashed_rect(draw, [box[0] + half, box[1] + half, box[2] - half, box[3] - half],
                    color, w, dash=S(46) + w, gap=S(26) + w)


def draw_centered(draw, cx, y, text, font, fill):
    width = draw.textlength(text, font=font)
    draw.text((cx - width / 2, y), text, font=font, fill=fill)


def render_month(year, month, photos, opts, dpi=300, logo_path=None):
    """
    photos: {номер_дня: Path до фото}. Смайлики настрою сюди не передаються
    і ніколи не друкуються.
    """
    k = dpi / 300

    def S(v):
        return max(1, int(round(v * k)))

    if opts.orientation == "landscape":
        W, H = S(3508), S(2480)
    else:
        W, H = S(2480), S(3508)
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img, "RGBA")

    color = hex_to_rgb(opts.frame_color)
    draw_frame(d, W, H, opts, S)

    margin = S(190)

    # заголовок
    title_font = load_font(S(150), bold=True)
    draw_centered(d, W / 2, margin, f"{MONTHS[month - 1]} {year}", title_font, TEXT_DARK)
    ul_w, ul_y = S(260), margin + S(215)
    d.line([(W / 2 - ul_w / 2, ul_y), (W / 2 + ul_w / 2, ul_y)], fill=color, width=S(8))

    # сітка
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    n = len(weeks)
    gap = S(14)
    cell_w = (W - 2 * margin - 6 * gap) // 7
    grid_top = margin + S(330)
    grid_bottom = H - margin - S(120)
    cell_h = min(int(cell_w * 2.0), (grid_bottom - grid_top - (n - 1) * gap) // n)
    left0 = (W - (7 * cell_w + 6 * gap)) // 2
    radius = S(30) if opts.corners == "round" else 0

    # дні тижня
    wd_font = load_font(S(46))
    for col, name in enumerate(WEEKDAYS):
        cx = left0 + col * (cell_w + gap) + cell_w / 2
        draw_centered(d, cx, grid_top - S(80), name, wd_font, TEXT_SOFT)

    num_size = S(54)
    num_font = load_font(num_size, bold=True)
    border_w = max(1, S(4))

    for row, week in enumerate(weeks):
        for col, day in enumerate(week):
            if day == 0:
                continue
            x = left0 + col * (cell_w + gap)
            y = grid_top + row * (cell_h + gap)
            box = [x, y, x + cell_w - 1, y + cell_h - 1]

            photo_file = photos.get(day)
            photo = None
            if photo_file:
                try:
                    photo = Image.open(photo_file)
                    photo = ImageOps.exif_transpose(photo).convert("RGB")
                    photo = ImageOps.fit(photo, (cell_w, cell_h), Image.LANCZOS,
                                         centering=(0.5, 0.4))
                except Exception:
                    photo = None

            if photo is not None:
                img.paste(photo, (x, y), rounded_mask((cell_w, cell_h), radius))
                d.rounded_rectangle(box, radius=radius, outline=color, width=border_w)
                text = str(day)
                tw = d.textlength(text, font=num_font)
                px, py = S(16), S(8)
                pill = [x + S(14), y + S(14),
                        x + S(14) + tw + 2 * px, y + S(14) + num_size + 2 * py]
                d.rounded_rectangle(pill, radius=S(26), fill=(255, 255, 255, 225))
                d.text((pill[0] + px, pill[1] + py - S(2)), text, font=num_font, fill=TEXT_DARK)
            else:
                d.rounded_rectangle(box, radius=radius, fill=tint(color, 0.84),
                                    outline=color, width=border_w)
                d.text((x + S(20), y + S(14)), str(day), font=num_font, fill=TEXT_SOFT)

    # лого
    if opts.show_logo and logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            target_h = S(90)
            logo = logo.resize((int(logo.width * target_h / logo.height), target_h), Image.LANCZOS)
            img.paste(logo, ((W - logo.width) // 2, H - margin - S(100)), logo)
        except Exception:
            pass

    return img
