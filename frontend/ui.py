import calendar
import datetime
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import quote

import flet as ft
import requests

import about_config
from i18n import (LANGS, detect_language, get_language, set_language, tr)
from i18n import lists as lang_lists

API = "http://127.0.0.1:8000"

ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = ROOT / "exports"

PRIORITIES = {
    "red": ("#F28B82", "Високий"),
    "yellow": ("#FDD663", "Середній"),
    "green": ("#81C995", "Низький"),
}

MONTHS = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
          "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]
MONTHS_GEN = ["січня", "лютого", "березня", "квітня", "травня", "червня",
              "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
WEEKDAYS_FULL = ["Понеділок", "Вівторок", "Середа", "Четвер", "Пʼятниця", "Субота", "Неділя"]

REPEATS = [(None, "Не повторювати"), ("daily", "Щодня"), ("weekdays", "По буднях"),
           ("weekly", "Щотижня"), ("monthly", "Щомісяця")]
REPEAT_LABELS = {key: label for key, label in REPEATS if key}
UNTILS = [("month", "Кінця місяця"), ("year", "Кінця року"), ("next_year", "Кінця наступного року")]
SCOPES = [("this", "Лише це завдання"), ("future", "Це й наступні"), ("all", "Усі в серії")]

PERIODS = [("day", "День"), ("week", "Тиждень"), ("month", "Місяць"),
           ("year", "Рік"), ("all", "Усі")]

MOODS = ["😊", "😌", "🥰", "😴", "😐", "😔", "😤", "🤒"]

FRAME_COLORS = [
    ("#9CCBEA", "Блакитний"),
    ("#F4B6C2", "Рожевий"),
    ("#A8DCC0", "Мʼятний"),
    ("#C9B8EC", "Лавандовий"),
    ("#F7D58B", "Медовий"),
    ("#5B6B7A", "Графіт"),
]

THEMES = {
    "blue": {
        "name": "Хвиля", "dot": "#9CCBEA", "dark": False,
        "bg": "#EAF4FB", "surface": "#FFFFFF", "surface_alt": "#F3F8FC",
        "column": "#CFE6F5", "column_hover": "#B5D9F0",
        "accent": "#4A90C2", "accent_soft": "#9CCBEA", "on_accent": "#FFFFFF",
        "chip_off": "#FFFFFF", "text": "#1F2D3A", "text_soft": "#5B6B7A",
        "text_muted": "#8A98A5", "done": "#3F8F5B",
        "warn_bg": "#FFF4D6", "logo_plate": None,
    },
    "pink": {
        "name": "Сакура", "dot": "#F4B6C2", "dark": False,
        "bg": "#FDF0F3", "surface": "#FFFFFF", "surface_alt": "#FEF7F9",
        "column": "#F9DCE4", "column_hover": "#F4C8D5",
        "accent": "#D9708C", "accent_soft": "#F4B6C2", "on_accent": "#FFFFFF",
        "chip_off": "#FFFFFF", "text": "#3A2530", "text_soft": "#7A5A68",
        "text_muted": "#A68A96", "done": "#3F8F5B",
        "warn_bg": "#FFF4D6", "logo_plate": None,
    },
    "mint": {
        "name": "Мʼята", "dot": "#A8DCC0", "dark": False,
        "bg": "#EDF7F1", "surface": "#FFFFFF", "surface_alt": "#F5FBF8",
        "column": "#D3EBDD", "column_hover": "#BFE0CE",
        "accent": "#4E9E78", "accent_soft": "#A8DCC0", "on_accent": "#FFFFFF",
        "chip_off": "#FFFFFF", "text": "#1F3328", "text_soft": "#55705F",
        "text_muted": "#8AA394", "done": "#3F8F5B",
        "warn_bg": "#FFF4D6", "logo_plate": None,
    },
    "night": {
        "name": "Ніч", "dot": "#3E6A8E", "dark": True,
        "bg": "#1B2430", "surface": "#26323F", "surface_alt": "#202B37",
        "column": "#2C3A4A", "column_hover": "#36485C",
        "accent": "#8FC3EA", "accent_soft": "#3E6A8E", "on_accent": "#16202B",
        "chip_off": "#2C3A4A", "text": "#E8EEF4", "text_soft": "#A9B7C5",
        "text_muted": "#7F8E9D", "done": "#7CC59A",
        "warn_bg": "#4A4125", "logo_plate": "#FFFFFF",
    },
}
THEME = dict(THEMES["blue"])
T = THEME
OVERLAY_BG = "#CCFFFFFF"     # напівпрозорі плашки поверх фото
OVERLAY_TEXT = "#1F2D3A"

SETTINGS_FILE = ROOT / "settings.json"
FONT_REGULAR = ROOT / "assets" / "fonts" / "Nunito-Regular.ttf"
LOGO_DARK = ROOT / "assets" / "logo_dark.png"

SB_HANDLE = 34
SB_OPEN = 210
SB_GAP = 14
ANIM_MS = 260

_FitEnum = getattr(ft, "BoxFit", None) or getattr(ft, "ImageFit", None)
FIT_COVER = _FitEnum.COVER if _FitEnum else "cover"


def load_settings():
    try:
        import json
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(data):
    try:
        import json
        SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def apply_theme_colors(key):
    THEME.clear()
    THEME.update(THEMES.get(key, THEMES["blue"]))


def make_anim(ms=ANIM_MS):
    """Анімація, що працює у різних версіях Flet; None, якщо недоступна."""
    for build in (
        lambda: ft.Animation(ms, ft.AnimationCurve.EASE_OUT),
        lambda: ft.Animation(ms, "easeOut"),
        lambda: ft.Animation(ms),
    ):
        try:
            return build()
        except Exception:
            continue
    return None


def make_dialog(**kwargs):
    """Діалог із заокругленими кутами та кольорами теми."""
    kwargs.setdefault("bgcolor", T["surface"])
    try:
        return ft.AlertDialog(shape=ft.RoundedRectangleBorder(radius=24), **kwargs)
    except Exception:
        return ft.AlertDialog(**kwargs)


def make_field(**kwargs):
    """Поле вводу в сучасному стилі (залите, без рамки); запасний варіант для старих версій."""
    styled = dict(kwargs, filled=True, bgcolor=T["surface_alt"], border_radius=14,
                  border_color="transparent")
    try:
        return ft.TextField(**styled)
    except Exception:
        return ft.TextField(**kwargs)


def primary_button(text, on_click):
    return ft.Container(
        content=ft.Text(text, size=14, weight="bold", color=T["on_accent"]),
        bgcolor=T["accent"],
        padding=ft.Padding(left=20, top=10, right=20, bottom=10),
        border_radius=20,
        on_click=on_click,
    )


def small_label(text):
    return ft.Text(text, size=12, weight="bold", color=T["text_muted"])


def refresh_lists():
    """Назви місяців і днів тижня відповідно до поточної мови."""
    lists = lang_lists()
    MONTHS[:] = lists["months"]
    MONTHS_GEN[:] = lists["months_gen"]
    WEEKDAYS[:] = lists["weekdays"]
    WEEKDAYS_FULL[:] = lists["weekdays_full"]


def open_url(url):
    try:
        webbrowser.open(url)
    except Exception:
        pass


def photo_url(name):
    return f"{API}/uploads/{name}"


def open_path(path):
    """Відкриває файл або папку у системній програмі."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


def pick_photo_path():
    """Системне вікно вибору фото. Повертає (шлях, помилка)."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title=tr("Обери фото дня"),
            filetypes=[(tr("Зображення"), "*.jpg *.jpeg *.png *.webp *.bmp"), (tr("Усі файли"), "*.*")],
        )
        root.destroy()
        return (path or None), None
    except Exception as ex:
        return None, str(ex)


def main(page: ft.Page):
    page.title = "Memio"
    page.padding = 20

    def apply_page_theme():
        """Колір сторінки, світлий/темний режим, акцент і шрифт."""
        page.bgcolor = T["bg"]
        try:
            page.theme_mode = ft.ThemeMode.DARK if T["dark"] else ft.ThemeMode.LIGHT
        except Exception:
            pass
        options = {"color_scheme_seed": T["accent"]}
        if FONT_REGULAR.exists():
            try:
                page.fonts = {"Nunito": "fonts/Nunito-Regular.ttf"}
                options["font_family"] = "Nunito"
            except Exception:
                pass
        for opts in (options, {k: v for k, v in options.items() if k == "font_family"}):
            try:
                page.theme = ft.Theme(**opts)
                page.dark_theme = ft.Theme(**opts)
                break
            except Exception:
                continue

    _saved = load_settings()
    set_language(_saved.get("language") or detect_language())
    refresh_lists()
    apply_theme_colors(_saved.get("theme", "blue"))
    apply_page_theme()

    today = datetime.date.today()
    state = {
        "view": "board",          # board / calendar / myday
        "period": "day",
        "anchor": today,
        "topic_filter": None,
        "year": today.year,
        "month": today.month,
        "columns": [],
        "topics": [],
        "sidebar_open": False,
        "theme": load_settings().get("theme", "blue"),
        "language": get_language(),
        "day": today,
        "day_msg": "",
        "note_ctrl": None,
        "expanded": set(),
        "group_series": True,
    }

    content_area = ft.Column(expand=True, scroll="auto", spacing=15)
    # меню має повну ширину й висувається вліво/вправо, а вміст зсувається разом із ним
    sidebar = ft.Container(width=SB_OPEN, bgcolor=T["surface"], border_radius=16,
                           left=-(SB_OPEN - SB_HANDLE), top=0, bottom=0)
    content_wrap = ft.Container(
        content=content_area,
        left=0, top=0, right=0, bottom=0,
        padding=ft.Padding(left=SB_HANDLE + SB_GAP, top=0, right=0, bottom=0),
    )
    _anim = make_anim()
    if _anim is not None:
        sidebar.animate_position = _anim
        content_wrap.animate = _anim

    # ---------- діалоги (старі й нові версії Flet) ----------
    def open_dialog(dlg):
        if hasattr(page, "show_dialog"):
            page.show_dialog(dlg)
        else:
            page.dialog = dlg
            dlg.open = True
            page.update()

    def close_dialog(dlg):
        if hasattr(page, "pop_dialog"):
            page.pop_dialog()
        else:
            dlg.open = False
            page.update()

    # ---------- дії з API ----------
    def all_tasks():
        return [t for col in state["columns"] for t in col["tasks"]]

    def load():
        state["columns"] = requests.get(f"{API}/board").json()
        state["topics"] = requests.get(f"{API}/topics").json()
        used = {t.get("topic_id") for t in all_tasks()}
        if state["topic_filter"] is not None and state["topic_filter"] not in used:
            state["topic_filter"] = None
        render()

    def move(task_id, column_id):
        requests.patch(f"{API}/tasks/{task_id}/move",
                       json={"column_id": column_id, "position": 9999})
        load()

    def delete(task_id):
        requests.delete(f"{API}/tasks/{task_id}")
        load()

    # ---------- невиконане з минулих днів ----------
    def overdue_tasks():
        t = datetime.date.today().isoformat()
        return [x for x in all_tasks()
                if not x.get("is_done") and x.get("due_date") and x["due_date"] < t
                and not x.get("series_id")]

    def carry_over(e):
        iso = datetime.date.today().isoformat()
        for x in overdue_tasks():
            requests.patch(f"{API}/tasks/{x['id']}", json={"due_date": iso})
        load()

    # ---------- період дошки ----------
    def get_range():
        p, a = state["period"], state["anchor"]
        if p == "day":
            return a, a
        if p == "week":
            start = a - datetime.timedelta(days=a.weekday())
            return start, start + datetime.timedelta(days=6)
        if p == "month":
            last = calendar.monthrange(a.year, a.month)[1]
            return a.replace(day=1), a.replace(day=last)
        if p == "year":
            return datetime.date(a.year, 1, 1), datetime.date(a.year, 12, 31)
        return None

    def period_title():
        p, a = state["period"], state["anchor"]
        rng = get_range()
        if p == "day":
            name = f"{WEEKDAYS_FULL[a.weekday()]}, {a.day} {MONTHS_GEN[a.month - 1]}"
            return (tr("Сьогодні · ") + name) if a == datetime.date.today() else name
        if p == "week":
            s, e = rng
            return f"{s.day} {MONTHS_GEN[s.month - 1]} – {e.day} {MONTHS_GEN[e.month - 1]}"
        if p == "month":
            return f"{MONTHS[a.month - 1]} {a.year}"
        if p == "year":
            return str(a.year)
        return tr("Усі завдання")

    def shift_period(delta):
        p, a = state["period"], state["anchor"]
        if p == "day":
            a = a + datetime.timedelta(days=delta)
        elif p == "week":
            a = a + datetime.timedelta(days=7 * delta)
        elif p == "month":
            idx = a.month - 1 + delta
            y, m = a.year + idx // 12, idx % 12 + 1
            a = datetime.date(y, m, min(a.day, calendar.monthrange(y, m)[1]))
        elif p == "year":
            y = a.year + delta
            a = datetime.date(y, a.month, min(a.day, calendar.monthrange(y, a.month)[1]))
        state["anchor"] = a
        render()

    def set_period(p):
        state["period"] = p
        render()

    def go_today_board(e):
        state["anchor"] = datetime.date.today()
        render()

    def set_topic_filter(topic_id):
        state["topic_filter"] = topic_id
        render()

    def matches(task):
        if state["topic_filter"] is not None and task.get("topic_id") != state["topic_filter"]:
            return False
        rng = get_range()
        if rng is None:
            return True
        due = task.get("due_date")
        if not due:
            return False
        return rng[0].isoformat() <= due <= rng[1].isoformat()

    def default_due_for_period():
        rng = get_range()
        t = datetime.date.today()
        if rng is None:
            return t.isoformat()
        if rng[0] <= t <= rng[1]:
            return t.isoformat()
        return rng[0].isoformat()

    # ---------- вікно «нове / редагувати завдання» ----------
    def fmt_date(d):
        if d is None:
            return tr("Без дати")
        return f"{WEEKDAYS_FULL[d.weekday()]}, {d.day} {MONTHS_GEN[d.month - 1]}"

    def open_task_dialog(column_id, task=None, default_due=None, on_done=None):
        topics = requests.get(f"{API}/topics").json()
        if task:
            due_src = task.get("due_date")
        else:
            due_src = default_due or datetime.date.today().isoformat()
        st = {
            "priority": (task or {}).get("priority", "green"),
            "topic_id": (task or {}).get("topic_id"),
            "due": datetime.date.fromisoformat(due_src) if due_src else None,
            "recurrence": (task or {}).get("recurrence"),
            "is_focus": bool((task or {}).get("is_focus")),
            "until": "year",
            "scope": "this",
        }
        is_series = bool((task or {}).get("series_id"))

        title = make_field(label=tr("Назва"), value=task["title"] if task else "", autofocus=True)
        desc = make_field(label=tr("Опис (необовʼязково)"),
                          value=(task or {}).get("description") or "",
                          multiline=True, min_lines=2, max_lines=5)
        new_topic = make_field(label=tr("Або нова тема"), dense=True)

        quick_row = ft.Row(spacing=6, wrap=True)
        date_row = ft.Row(spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        prio_row = ft.Row(spacing=8, wrap=True)
        topic_row = ft.Row(spacing=6, wrap=True)
        repeat_row = ft.Row(spacing=6, wrap=True)
        until_row = ft.Row(spacing=6, wrap=True)
        until_info = ft.Text("", size=12, color=T["text_muted"])
        scope_row = ft.Row(spacing=6, wrap=True)
        focus_row = ft.Row(spacing=6)
        form_msg = ft.Text("", size=12, color="#B45309")

        repeat_block = ft.Column([small_label(tr("Повтор")), repeat_row], spacing=6)
        until_block = ft.Column([small_label(tr("Повторювати до")), until_row, until_info],
                                spacing=6)
        series_block = ft.Column([
            small_label(tr("Частина серії повторів")),
            ft.Text("↻ " + tr(REPEAT_LABELS.get((task or {}).get("recurrence"), "")),
                    size=14, color=T["text"]),
            small_label(tr("Застосувати до")), scope_row], spacing=6)

        def until_date():
            base = st["due"] or datetime.date.today()
            if st["until"] == "month":
                return base.replace(day=calendar.monthrange(base.year, base.month)[1])
            if st["until"] == "next_year":
                return datetime.date(base.year + 1, 12, 31)
            return datetime.date(base.year, 12, 31)

        def set_until(key):
            st["until"] = key
            refresh()

        def set_scope(key):
            st["scope"] = key
            refresh()

        def set_repeat(value):
            st["recurrence"] = value
            refresh()

        def toggle_focus_flag():
            st["is_focus"] = not st["is_focus"]
            refresh()

        def set_due(value):
            st["due"] = value
            refresh()

        def shift_due(delta):
            base = st["due"] or datetime.date.today()
            st["due"] = base + datetime.timedelta(days=delta)
            refresh()

        def pick_priority(key):
            st["priority"] = key
            refresh()

        def pick_topic(topic_id):
            st["topic_id"] = topic_id
            refresh()

        def refresh():
            today_ = datetime.date.today()
            quick = [(tr("Сьогодні"), today_),
                     (tr("Завтра"), today_ + datetime.timedelta(days=1)),
                     (tr("Через тиждень"), today_ + datetime.timedelta(days=7)),
                     (tr("Без дати"), None)]
            quick_row.controls = [
                chip(text, st["due"] == value, lambda e, v=value: set_due(v))
                for text, value in quick
            ]
            repeat_row.controls = [
                chip(tr(label), st["recurrence"] == value, lambda e, v=value: set_repeat(v))
                for value, label in REPEATS
            ]
            show_until = bool(st["recurrence"]) and not is_series
            repeat_block.visible = not is_series
            until_block.visible = show_until
            series_block.visible = is_series
            until_row.controls = [
                chip(tr(label), st["until"] == key, lambda e, k=key: set_until(k))
                for key, label in UNTILS
            ]
            end = until_date()
            until_info.value = tr("Повторюватиметься до {date}").format(
                date=f"{end.day} {MONTHS_GEN[end.month - 1]} {end.year}")
            scope_row.controls = [
                chip(tr(label), st["scope"] == key, lambda e, k=key: set_scope(k))
                for key, label in SCOPES
            ]
            focus_row.controls = [
                chip(tr("★ Головне на день"), st["is_focus"], lambda e: toggle_focus_flag())
            ]
            date_row.controls = [
                ft.TextButton("‹", on_click=lambda e: shift_due(-1)),
                ft.Text(fmt_date(st["due"]), size=15, weight="bold", color=T["text"]),
                ft.TextButton("›", on_click=lambda e: shift_due(1)),
            ]
            prio_row.controls = [
                ft.Container(
                    content=ft.Row([ft.Text("●", color=color, size=16),
                                    ft.Text(tr(label), size=13, color=T["text"])],
                                   spacing=6, tight=True),
                    bgcolor=color if st["priority"] == key else T["surface_alt"],
                    padding=ft.Padding(left=14, top=9, right=14, bottom=9),
                    border_radius=18,
                    on_click=lambda e, k=key: pick_priority(k),
                )
                for key, (color, label) in PRIORITIES.items()
            ]
            options = [(None, tr("Без теми"))] + [(t["id"], tr(t["name"])) for t in topics]
            topic_row.controls = [
                chip(name, st["topic_id"] == tid, lambda e, t=tid: pick_topic(t))
                for tid, name in options
            ]
            page.update()

        def finish():
            close_dialog(dlg)
            load()
            if on_done:
                on_done()

        def save(e):
            t = (title.value or "").strip()
            if not t:
                title.error_text = tr("Введи назву")
                page.update()
                return

            topic_id = st["topic_id"]
            if (new_topic.value or "").strip():
                r = requests.post(f"{API}/topics", json={"name": new_topic.value.strip()})
                topic_id = r.json()["id"]

            payload = {
                "title": t,
                "description": (desc.value or "").strip() or None,
                "due_date": st["due"].isoformat() if st["due"] else None,
                "topic_id": topic_id,
                "priority": st["priority"],
                "is_focus": st["is_focus"],
            }
            if not is_series:
                payload["recurrence"] = st["recurrence"]
                if st["recurrence"]:
                    payload["repeat_until"] = until_date().isoformat()
            if task:
                r = requests.patch(f"{API}/tasks/{task['id']}",
                                   params={"scope": st["scope"]}, json=payload)
            else:
                payload["column_id"] = column_id
                r = requests.post(f"{API}/tasks", json=payload)
            if not r.ok:
                form_msg.value = (tr("Головних справ може бути не більше трьох.")
                                  if st["is_focus"] else tr("Не вдалося зберегти завдання."))
                page.update()
                return
            finish()

        def remove(e):
            close_dialog(dlg)
            requests.delete(f"{API}/tasks/{task['id']}", params={"scope": st["scope"]})
            load()
            if on_done:
                on_done()

        def cancel(e):
            close_dialog(dlg)
            if on_done:
                on_done()

        actions = [ft.TextButton(tr("Скасувати"), on_click=cancel)]
        if task:
            actions.insert(0, ft.TextButton(tr("Видалити"), on_click=remove))
        actions.append(primary_button(tr("Зберегти"), save))

        dlg = make_dialog(
            title=ft.Text(tr("Редагувати завдання") if task else tr("Нове завдання"),
                          weight="bold"),
            content=ft.Column(
                [title, desc,
                 small_label(tr("Дата")), quick_row, date_row,
                 small_label(tr("Пріоритет")), prio_row,
                 small_label(tr("Тема")), topic_row, new_topic,
                 repeat_block, until_block, series_block,
                 focus_row, form_msg],
                tight=True, width=440, scroll="auto", spacing=10,
            ),
            actions=actions,
        )
        refresh()
        open_dialog(dlg)

    # ---------- картки (з перетягуванням) ----------
    def card_body(task, idx, columns, with_buttons):
        color = PRIORITIES.get(task.get("priority"), PRIORITIES["green"])[0]
        title_color = T["text_muted"] if task.get("is_done") else T["text"]

        lines = [ft.Row([ft.Text("●", color=color, size=16),
                         ft.Text(("★ " if task.get("is_focus") else "") + task["title"],
                                 size=15, weight="bold",
                                 color=title_color, expand=True)], spacing=6)]
        if task.get("recurrence"):
            lines.append(ft.Text("↻ " + tr(REPEAT_LABELS.get(task["recurrence"], "")),
                                 size=11, color=T["text_muted"]))
        if task.get("topic"):
            lines.append(ft.Text(f"#{tr(task['topic']['name'])}", size=11, color=T["accent"]))
        if task.get("description"):
            lines.append(ft.Text(task["description"], size=12, color=T["text_soft"]))
        if task.get("due_date"):
            lines.append(ft.Text(f"📅 {task['due_date']}", size=12, color=T["text_soft"]))

        if with_buttons:
            buttons = []
            if idx > 0:
                prev_id = columns[idx - 1]["id"]
                buttons.append(ft.TextButton("←", on_click=lambda e, t=task["id"], c=prev_id: move(t, c)))
            if idx < len(columns) - 1:
                next_id = columns[idx + 1]["id"]
                buttons.append(ft.TextButton("→", on_click=lambda e, t=task["id"], c=next_id: move(t, c)))
            lines.append(ft.Row(buttons, spacing=0))

        return ft.Container(
            content=ft.Column(lines, spacing=3),
            bgcolor=T["surface"],
            padding=10,
            border_radius=12,
        )

    def build_card(task, idx, columns):
        body = card_body(task, idx, columns, with_buttons=True)
        body.on_click = lambda e, t=task: open_task_dialog(t["column_id"], t)

        feedback = card_body(task, idx, columns, with_buttons=False)
        feedback.width = 256
        feedback.scale = 1.05
        feedback.shadow = ft.BoxShadow(blur_radius=18, color="#55000000", offset=ft.Offset(0, 6))

        placeholder = card_body(task, idx, columns, with_buttons=False)
        placeholder.opacity = 0

        return ft.Draggable(
            group="task",
            content=body,
            content_feedback=feedback,
            content_when_dragging=placeholder,
            data=task["id"],
        )

    def dragged_task_id(e):
        src = None
        try:
            src = e.src
        except Exception:
            src = None
        if src is None or getattr(src, "data", None) is None:
            try:
                src = page.get_control(e.src_id)
            except Exception:
                src = None
        return getattr(src, "data", None)

    def toggle_group(key):
        if key in state["expanded"]:
            state["expanded"].discard(key)
        else:
            state["expanded"].add(key)
        render()

    def toggle_grouping(e):
        state["group_series"] = not state["group_series"]
        render()

    def build_group(col, sid, rows, idx, columns):
        """Одна картка на всю серію повторів; клік розгортає окремі завдання."""
        key = f"{col['id']}:{sid}"
        expanded = key in state["expanded"]
        rows = sorted(rows, key=lambda t: t.get("due_date") or "")
        first = rows[0]
        color = PRIORITIES.get(first.get("priority"), PRIORITIES["green"])[0]
        pending = [t for t in rows if not t.get("is_done")]
        meta = (f"↻ {tr(REPEAT_LABELS.get(first.get('recurrence'), ''))} · ×{len(rows)}")

        lines = [
            ft.Row([ft.Text("●", color=color, size=16),
                    ft.Text(first["title"], size=15, weight="bold", color=T["text"], expand=True),
                    ft.Text("▾" if expanded else "▸", size=16, color=T["text_muted"])],
                   spacing=6),
            ft.Text(meta, size=12, color=T["text_muted"]),
        ]
        if pending and pending[0].get("due_date"):
            nearest = datetime.date.fromisoformat(pending[0]["due_date"])
            lines.append(ft.Text(tr("Найближче: {date}").format(date=fmt_date(nearest)),
                                 size=12, color=T["text_soft"]))
        header = ft.Container(
            content=ft.Column(lines, spacing=3),
            bgcolor=T["surface"], padding=10, border_radius=12,
            on_click=lambda e, k=key: toggle_group(k),
        )
        items = [header]
        if expanded:
            items += [ft.Container(content=build_card(t, idx, columns),
                                   padding=ft.Padding(left=14, top=0, right=0, bottom=0))
                      for t in rows]
        return ft.Column(items, spacing=6)

    def build_cards(visible, col, idx, columns):
        # у режимі «День» кожне завдання окремо; в ширших періодах серії згортаються
        grouping = state["group_series"] and state["period"] != "day"
        groups = {}
        if grouping:
            for t in visible:
                if t.get("series_id"):
                    groups.setdefault(t["series_id"], []).append(t)
        cards, seen = [], set()
        for t in visible:
            sid = t.get("series_id")
            if grouping and sid and len(groups.get(sid, [])) > 1:
                if sid in seen:
                    continue
                seen.add(sid)
                cards.append(build_group(col, sid, groups[sid], idx, columns))
            else:
                cards.append(build_card(t, idx, columns))
        return cards

    def build_column(col, idx, columns):
        visible = [t for t in col["tasks"] if matches(t)]
        cards = build_cards(visible, col, idx, columns)
        add_btn = ft.TextButton(
            tr("+ Додати завдання"),
            on_click=lambda e, c=col["id"]: open_task_dialog(c, default_due=default_due_for_period()),
        )
        box = ft.Container(
            width=280,
            padding=12,
            bgcolor=T["column"],
            border_radius=16,
            content=ft.Column([ft.Text(tr(col["title"]), size=18, weight="bold"), *cards, add_btn]),
        )

        def will_accept(e):
            box.bgcolor = T["column_hover"]
            page.update()

        def leave(e):
            box.bgcolor = T["column"]
            page.update()

        def accept(e):
            task_id = dragged_task_id(e)
            if task_id is not None:
                move(task_id, col["id"])

        return ft.DragTarget(
            group="task",
            content=box,
            on_will_accept=will_accept,
            on_leave=leave,
            on_accept=accept,
        )

    def chip(text, active, on_click):
        return ft.Container(
            content=ft.Text(text, size=13, weight="bold" if active else "normal"),
            bgcolor=T["accent_soft"] if active else T["chip_off"],
            padding=ft.Padding(left=14, top=8, right=14, bottom=8),
            border_radius=16,
            on_click=on_click,
        )

    def build_board_view():
        columns = state["columns"]

        header = ft.Text(tr("Плани"), size=26, weight="bold")

        nav_controls = []
        if state["period"] != "all":
            nav_controls.append(ft.TextButton("‹", on_click=lambda e: shift_period(-1)))
        nav_controls.append(ft.Text(period_title(), size=20, weight="bold"))
        if state["period"] != "all":
            nav_controls.append(ft.TextButton("›", on_click=lambda e: shift_period(1)))
            nav_controls.append(ft.TextButton(tr("Сьогодні"), on_click=go_today_board))
        nav = ft.Row(nav_controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        period_row = ft.Row(
            [chip(tr(label), state["period"] == key, lambda e, k=key: set_period(k))
             for key, label in PERIODS],
            spacing=8, wrap=True,
        )

        used = {t.get("topic_id") for t in all_tasks()}
        topic_chips = [chip(tr("Усі теми"), state["topic_filter"] is None,
                            lambda e: set_topic_filter(None))]
        for t in state["topics"]:
            if t["id"] in used:
                topic_chips.append(chip(f"#{tr(t['name'])}", state["topic_filter"] == t["id"],
                                        lambda e, tid=t["id"]: set_topic_filter(tid)))
        if state["period"] != "day":
            topic_chips.append(chip("↻ " + tr("Групувати повтори"),
                                    state["group_series"], toggle_grouping))
        topic_row = ft.Row(topic_chips, spacing=8, wrap=True)

        total = sum(1 for t in all_tasks() if matches(t))
        board = ft.Row([build_column(c, i, columns) for i, c in enumerate(columns)],
                       spacing=15, vertical_alignment=ft.CrossAxisAlignment.START, scroll="auto")

        parts = [header, nav, period_row, topic_row]

        overdue = overdue_tasks()
        if overdue:
            parts.append(ft.Container(
                content=ft.Row(
                    [ft.Text(tr("🌿 Невиконаних справ з минулих днів: {n}. Нічого страшного, їх можна перенести.").format(n=len(overdue)),
                             size=13, color=T["text_soft"], expand=True),
                     ft.TextButton(tr("Перенести на сьогодні"), on_click=carry_over)],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=T["warn_bg"],
                padding=ft.Padding(left=14, top=6, right=8, bottom=6),
                border_radius=12,
            ))

        if total == 0:
            parts.append(ft.Text(tr("Тут поки нічого не заплановано. Спокійний час 🌿"), color=T["text_soft"]))
        parts.append(board)
        return parts

    # ---------- план дня (список завдань дня) ----------
    def open_day_dialog(d):
        iso = d.isoformat()
        day_tasks = [t for t in all_tasks() if t.get("due_date") == iso]

        def reopen():
            open_day_dialog(d)

        def edit_task(t):
            close_dialog(dlg)
            open_task_dialog(t["column_id"], t, on_done=reopen)

        def add_task(e):
            close_dialog(dlg)
            first_col = state["columns"][0]["id"]
            open_task_dialog(first_col, None, default_due=iso, on_done=reopen)

        rows = []
        for t in day_tasks:
            color = PRIORITIES.get(t.get("priority"), PRIORITIES["green"])[0]
            info = [ft.Text(("✓ " if t.get("is_done") else "") + t["title"], size=14, weight="bold")]
            if t.get("topic"):
                info.append(ft.Text(f"#{tr(t['topic']['name'])}", size=11, color=T["accent"]))
            if t.get("description"):
                info.append(ft.Text(t["description"], size=12, color=T["text_soft"]))
            rows.append(ft.Container(
                content=ft.Row([ft.Text("●", color=color, size=16),
                                ft.Column(info, spacing=2, expand=True)], spacing=8),
                bgcolor=T["surface_alt"],
                padding=10,
                border_radius=10,
                on_click=lambda e, t=t: edit_task(t),
            ))
        if not rows:
            rows = [ft.Text(tr("Поки нічого не заплановано. Спокійний день 🌿"), color=T["text_soft"])]

        title = f"{WEEKDAYS_FULL[d.weekday()]}, {d.day} {MONTHS_GEN[d.month - 1]}"
        dlg = make_dialog(
            title=ft.Text(title),
            content=ft.Column(rows, tight=True, width=380, scroll="auto", spacing=8),
            actions=[
                ft.TextButton(tr("Мій день"),
                              on_click=lambda e: (close_dialog(dlg), open_day(d))),
                ft.TextButton(tr("Закрити"), on_click=lambda e: close_dialog(dlg)),
                ft.TextButton(tr("+ Додати завдання"), on_click=add_task),
            ],
        )
        open_dialog(dlg)

    # ---------- «Мій день»: сторінка одного дня ----------
    PHOTO_W, PHOTO_H = 420, 300

    def flush_note():
        """Зберігає записку, якщо її змінили, перед будь-яким переходом."""
        ctrl = state.get("note_ctrl")
        if not ctrl:
            return
        iso, field, original = ctrl
        value = (field.value or "").strip()
        if value != (original or ""):
            try:
                requests.put(f"{API}/days/{iso}", json={"note": value or None})
            except Exception:
                pass
            state["note_ctrl"] = (iso, field, value)

    def open_day(d):
        flush_note()
        state["day"] = d
        state["day_msg"] = ""
        state["view"] = "myday"
        render()

    def shift_day(delta):
        flush_note()
        state["day"] = state["day"] + datetime.timedelta(days=delta)
        state["day_msg"] = ""
        render()

    def go_today_day(e):
        flush_note()
        state["day"] = datetime.date.today()
        state["day_msg"] = ""
        render()

    def upload_day_photo(iso):
        flush_note()
        path, err = pick_photo_path()
        if err:
            state["day_msg"] = tr("Не вдалося відкрити вибір файлу.")
            render()
            return
        if not path:
            return
        ok = False
        try:
            with open(path, "rb") as f:
                r = requests.post(f"{API}/days/{iso}/photo",
                                  files={"file": (os.path.basename(path), f)})
            ok = bool(r.ok)
        except Exception:
            ok = False
        state["day_msg"] = "" if ok else tr("Не вдалося завантажити фото. Спробуй інший файл (jpg або png).")
        render()

    def remove_day_photo(iso):
        flush_note()
        requests.delete(f"{API}/days/{iso}/photo")
        render()

    def set_day_mood(iso, mood, current):
        flush_note()
        requests.put(f"{API}/days/{iso}", json={"mood_emoji": None if mood == current else mood})
        render()

    def toggle_task(task):
        flush_note()
        columns = state["columns"]
        target = columns[0]["id"] if task.get("is_done") else columns[-1]["id"]
        move(task["id"], target)

    def toggle_focus(task):
        flush_note()
        r = requests.patch(f"{API}/tasks/{task['id']}",
                           json={"is_focus": not task.get("is_focus")})
        if not r.ok:
            state["task_msg"] = tr("Головних справ може бути не більше трьох.")
        load()

    def fill_stats(rows, y, m):
        prefix = f"{y}-{m:02d}-"
        filled = sum(
            1 for r in rows
            if str(r.get("memory_date", "")).startswith(prefix)
            and (r.get("photo_path") or r.get("note") or r.get("mood_emoji")))
        return filled, calendar.monthrange(y, m)[1]

    def month_fill_card(filled, total, month_name, on_click=None):
        if filled == 0:
            note = tr("Кожен день це маленька історія. Почни з сьогоднішнього 🌱")
        elif filled >= total:
            note = tr("Місяць заповнено! Можна друкувати календар 🌸")
        else:
            note = tr("Дні можна дописувати пізніше, нічого не згорає 🌿")
        track_w = 360
        return ft.Container(
            content=ft.Column([
                ft.Text(f"{month_name} · " + tr("Заповнено {filled} з {total} днів").format(
                    filled=filled, total=total), size=14, weight="bold", color=T["text"]),
                ft.Container(
                    width=track_w, height=8, bgcolor=T["surface_alt"], border_radius=4,
                    content=ft.Container(width=max(0, int(track_w * filled / total)), height=8,
                                         bgcolor=T["accent"], border_radius=4)),
                ft.Text(note, size=12, color=T["text_muted"]),
            ], spacing=6),
            bgcolor=T["surface"], padding=16, border_radius=16, on_click=on_click)

    def build_day_view():
        d = state["day"]
        iso = d.isoformat()
        today_ = datetime.date.today()
        future = d > today_

        info = {}
        if not future:
            try:
                info = requests.get(f"{API}/days/{iso}").json()
            except Exception:
                info = {}

        label = (tr("Сьогодні · ") + fmt_date(d)) if d == today_ else fmt_date(d)
        nav = ft.Row(
            [ft.TextButton("‹", on_click=lambda e: shift_day(-1)),
             ft.Text(label, size=20, weight="bold", color=T["text"]),
             ft.TextButton("›", on_click=lambda e: shift_day(1)),
             ft.TextButton(tr("Сьогодні"), on_click=go_today_day)],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- ліва частина: фото, настрій, записка ---
        left_cards = []
        if future:
            state["note_ctrl"] = None
            left_cards.append(section_card(tr("Фото дня"), ft.Text(
                tr("Фото й запис можна додати в сам день 🌿"), size=13, color=T["text_soft"])))
        else:
            photo_name = info.get("photo_path")
            if photo_name:
                photo_block = ft.Column([
                    ft.Container(
                        content=ft.Image(src=photo_url(photo_name), width=PHOTO_W, height=PHOTO_H,
                                         fit=FIT_COVER, border_radius=18),
                        on_click=lambda e: upload_day_photo(iso)),
                    ft.Row([ft.TextButton(tr("Змінити фото"), on_click=lambda e: upload_day_photo(iso)),
                            ft.TextButton(tr("Прибрати фото"), on_click=lambda e: remove_day_photo(iso))],
                           spacing=0),
                ], spacing=4)
            else:
                photo_block = ft.Container(
                    content=ft.Column(
                        [ft.Text("+", size=44, color=T["accent"]),
                         ft.Text(tr("📷  Додати фото дня"), size=14, color=T["text_soft"])],
                        width=PHOTO_W, height=PHOTO_H,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=T["surface_alt"],
                    border_radius=18,
                    on_click=lambda e: upload_day_photo(iso),
                )
            photo_items = [photo_block]
            if state.get("day_msg"):
                photo_items.append(ft.Text(state["day_msg"], size=12, color="#B45309"))
            photo_items.append(ft.Text(tr("Фото автоматично потрапляє в календар «Щоденник»."),
                                       size=12, color=T["text_muted"]))
            left_cards.append(section_card(tr("Фото дня"), ft.Column(photo_items, spacing=8)))

            current_mood = info.get("mood_emoji")
            mood_row = ft.Row(
                [ft.Container(
                    content=ft.Text(m, size=24),
                    bgcolor=T["accent_soft"] if current_mood == m else T["surface_alt"],
                    padding=ft.Padding(left=10, top=6, right=10, bottom=6),
                    border_radius=16,
                    on_click=lambda e, m=m: set_day_mood(iso, m, current_mood))
                 for m in MOODS],
                spacing=8, wrap=True)
            left_cards.append(section_card(tr("Настрій"), mood_row))

            note_field = make_field(
                label=tr("Записка дня (до 280 символів)"),
                value=info.get("note") or "",
                multiline=True, min_lines=3, max_lines=6, max_length=280)
            note_status = ft.Text("", size=12, color=T["done"])
            state["note_ctrl"] = (iso, note_field, info.get("note"))

            def save_note(e):
                flush_note()
                note_status.value = tr("Збережено ✓")
                page.update()

            left_cards.append(section_card(tr("Записка дня (до 280 символів)"), ft.Column(
                [note_field,
                 ft.Row([primary_button(tr("Зберегти"), save_note), note_status], spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER)],
                spacing=10)))

        left = ft.Column(left_cards, spacing=16, width=PHOTO_W + 36,
                         horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        # --- права частина: справи дня ---
        day_tasks = [t for t in all_tasks() if t.get("due_date") == iso]
        done = [t for t in day_tasks if t.get("is_done")]
        focus = [t for t in day_tasks if t.get("is_focus")]
        others = [t for t in day_tasks if not t.get("is_focus")]
        task_msg = state.pop("task_msg", "")
        task_items = []
        if day_tasks:
            frac = len(done) / len(day_tasks)
            track_w = 340
            task_items.append(ft.Text(
                tr("Зроблено {done} з {total}").format(done=len(done), total=len(day_tasks)),
                size=14, weight="bold", color=T["text"]))
            task_items.append(ft.Container(
                width=track_w, height=8, bgcolor=T["surface_alt"], border_radius=4,
                content=ft.Container(width=max(0, int(track_w * frac)), height=8,
                                     bgcolor=T["accent"], border_radius=4)))
            if len(done) == len(day_tasks):
                hint = tr("Усе зроблено, чудовий день 💙")
            elif focus and all(t.get("is_done") for t in focus):
                hint = tr("Головне зроблено, решта це бонус 🌿")
            elif not done:
                hint = tr("Іноді день це просто відпочинок 🌿")
            else:
                hint = tr("Решту можна спокійно перенести 🌿")
            task_items.append(ft.Text(hint, size=12, color=T["text_muted"]))
        else:
            task_items.append(ft.Text(tr("Поки нічого не заплановано. Спокійний день 🌿"),
                                      size=13, color=T["text_soft"]))
        if task_msg:
            task_items.append(ft.Text(task_msg, size=12, color="#B45309"))

        def task_row(t, highlight=False):
            is_done = t.get("is_done")
            is_focus = t.get("is_focus")
            color = PRIORITIES.get(t.get("priority"), PRIORITIES["green"])[0]
            check = ft.Container(
                content=ft.Column([ft.Text("✓" if is_done else "", size=13, color=T["on_accent"])],
                                  width=24, height=24,
                                  alignment=ft.MainAxisAlignment.CENTER,
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=24, height=24, border_radius=12,
                bgcolor=T["accent"] if is_done else T["column"],
                on_click=lambda e, t=t: toggle_task(t),
            )
            star = ft.Container(
                content=ft.Text("★" if is_focus else "☆", size=20,
                                color=T["accent"] if is_focus else T["text_muted"]),
                padding=ft.Padding(left=6, top=0, right=2, bottom=0),
                on_click=lambda e, t=t: toggle_focus(t),
            )
            cells = [check, ft.Text("●", color=color, size=14),
                     ft.Text(t["title"], size=15, weight="bold", expand=True,
                             color=T["text_muted"] if is_done else T["text"])]
            if t.get("recurrence"):
                cells.append(ft.Text("↻", size=14, color=T["text_muted"]))
            cells.append(star)
            return ft.Container(
                content=ft.Row(cells, spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=10, top=8, right=10, bottom=8),
                border_radius=14,
                bgcolor=T["column"] if highlight else T["surface_alt"],
                on_click=lambda e, t=t: open_task_dialog(t["column_id"], t),
            )

        if focus:
            task_items.append(small_label(tr("Головне на день")))
            task_items += [task_row(t, highlight=True) for t in focus]
        if others:
            if focus:
                task_items.append(small_label(tr("Решта")))
            task_items += [task_row(t) for t in others]
        if day_tasks and not focus:
            task_items.append(ft.Text(
                tr("Познач ★ до трьох справ, які справді важливі. Решта за можливості."),
                size=12, color=T["text_muted"]))

        task_items.append(ft.TextButton(
            tr("+ Додати завдання"),
            on_click=lambda e: open_task_dialog(state["columns"][0]["id"], default_due=iso)))

        right = ft.Column([section_card(tr("Справи дня"), ft.Column(task_items, spacing=8))],
                          spacing=16, width=400,
                          horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        body = ft.Row([left, right], wrap=True, spacing=20, run_spacing=20,
                      vertical_alignment=ft.CrossAxisAlignment.START)
        try:
            last = calendar.monthrange(d.year, d.month)[1]
            rows = requests.get(f"{API}/days", params={
                "start": d.replace(day=1).isoformat(),
                "end": d.replace(day=last).isoformat()}).json()
            filled, total = fill_stats(rows, d.year, d.month)
            fill_card = month_fill_card(filled, total, MONTHS[d.month - 1],
                                        on_click=lambda e: go("diary"))
        except Exception:
            fill_card = ft.Container()
        return [ft.Text(tr("Мій день"), size=26, weight="bold"), nav, fill_card, body]

    # ---------- друк місяця ----------
    def open_print_dialog():
        y, m = state["year"], state["month"]
        st = {
            "format": "pdf",
            "orientation": "landscape",
            "frame_style": "line",
            "frame_color": FRAME_COLORS[0][0],
            "frame_width": "medium",
            "corners": "round",
            "show_logo": True,
        }

        rows_col = ft.Column(spacing=6)
        preview_holder = ft.Container(width=300)
        status = ft.Text("", size=12, color=T["done"])

        def payload(preview):
            return {"year": y, "month": m, "preview": preview,
                    "language": get_language(), **st}

        def centered(control, w, h):
            return ft.Column([control], width=w, height=h,
                             alignment=ft.MainAxisAlignment.CENTER,
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def label(text):
            return ft.Text(text, size=12, color=T["text_soft"])

        def chips_row(key, options):
            return ft.Row(
                [chip(text, st[key] == value, lambda e, k=key, v=value: set_opt(k, v))
                 for value, text in options],
                spacing=6, wrap=True,
            )

        def rebuild():
            swatches = ft.Row(
                [ft.Container(
                    content=centered(ft.Text("✓" if st["frame_color"] == c else "",
                                             size=14, color="white"), 32, 32),
                    width=32, height=32, bgcolor=c, border_radius=16,
                    on_click=lambda e, c=c: set_opt("frame_color", c))
                 for c, _ in FRAME_COLORS],
                spacing=8, wrap=True,
            )
            rows_col.controls = [
                label(tr("Формат файлу")),
                chips_row("format", [("pdf", "PDF"), ("png", "PNG")]),
                label(tr("Орієнтація аркуша A4")),
                chips_row("orientation", [("landscape", tr("Альбомна")), ("portrait", tr("Книжкова"))]),
                label(tr("Рамка")),
                chips_row("frame_style", [("none", tr("Без рамки")), ("line", tr("Лінія")),
                                          ("double", tr("Подвійна")), ("rounded", tr("Заокруглена")),
                                          ("dashed", tr("Пунктир"))]),
                label(tr("Колір рамки")),
                swatches,
                label(tr("Товщина рамки")),
                chips_row("frame_width", [("thin", tr("Тонка")), ("medium", tr("Середня")),
                                          ("thick", tr("Товста"))]),
                label(tr("Клітинки днів")),
                chips_row("corners", [("round", tr("Круглі кути")), ("square", tr("Прямі кути"))]),
                chips_row("show_logo", [(True, tr("З логотипом")), (False, tr("Без логотипа"))]),
                ft.Text(tr("Смайлики настрою не друкуються, лише фото й числа."),
                        size=11, color=T["text_muted"]),
            ]

        def refresh_preview():
            preview_holder.content = ft.Text(tr("Оновлюю перегляд…"), size=12, color=T["text_soft"])
            page.update()
            try:
                r = requests.post(f"{API}/print/month", json=payload(True), timeout=60)
                if r.ok:
                    name = r.json()["file"]
                    preview_holder.content = ft.Image(
                        src=f"{API}/exports/{name}?v={time.time()}", width=300)
                else:
                    preview_holder.content = ft.Text(tr("Не вдалося створити перегляд"), size=12)
            except Exception:
                preview_holder.content = ft.Text(tr("Не вдалося створити перегляд"), size=12)
            page.update()

        def set_opt(key, value):
            st[key] = value
            status.value = ""
            rebuild()
            page.update()
            refresh_preview()

        def create(e):
            status.value = tr("Створюю файл…")
            page.update()
            try:
                r = requests.post(f"{API}/print/month", json=payload(False), timeout=180)
                if r.ok:
                    info = r.json()
                    status.value = tr("Готово: {file} (папка exports)").format(file=info["file"])
                    open_path(info["path"])
                else:
                    status.value = tr("Не вдалося створити файл.")
            except Exception:
                status.value = tr("Не вдалося створити файл.")
            page.update()

        def open_folder(e):
            EXPORTS_DIR.mkdir(exist_ok=True)
            open_path(EXPORTS_DIR)

        rebuild()
        dlg = make_dialog(
            title=ft.Text(tr("Друк · {month} {year}").format(month=MONTHS[m - 1], year=y)),
            content=ft.Column(
                [ft.Row([ft.Container(rows_col, width=330), preview_holder],
                        vertical_alignment=ft.CrossAxisAlignment.START, spacing=20),
                 status],
                tight=True, width=700, scroll="auto", spacing=10,
            ),
            actions=[
                ft.TextButton(tr("Відкрити папку"), on_click=open_folder),
                ft.TextButton(tr("Закрити"), on_click=lambda e: close_dialog(dlg)),
                ft.TextButton(tr("Створити файл"), on_click=create),
            ],
        )
        open_dialog(dlg)
        refresh_preview()

    # ---------- календар (Планування / Підсумки) ----------
    def shift_month(delta):
        m = state["month"] + delta
        y = state["year"]
        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1
        state["month"], state["year"] = m, y
        render()

    def go_today_calendar(e):
        t = datetime.date.today()
        state["year"], state["month"] = t.year, t.month
        render()

    def on_day_click(mode, d):
        if mode == "summary":
            open_day(d)
        else:
            open_day_dialog(d)

    def build_plan_cell(d, day_tasks):
        in_month = d.month == state["month"]
        is_today = d == datetime.date.today()

        num_color = T["on_accent"] if is_today else (T["text"] if in_month else T["text_muted"])
        num = ft.Container(
            content=ft.Text(str(d.day), size=12, weight="bold", color=num_color),
            bgcolor=T["accent"] if is_today else None,
            padding=4,
            border_radius=10,
        )
        items = [num]
        for t in day_tasks[:3]:
            color = PRIORITIES.get(t.get("priority"), PRIORITIES["green"])[0]
            label = ("✓ " if t.get("is_done") else "") + t["title"]
            items.append(ft.Container(
                content=ft.Text(label, size=11, max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS, color="#33404D"),
                bgcolor=color,
                padding=3,
                border_radius=6,
            ))
        if len(day_tasks) > 3:
            items.append(ft.Text(tr("+{n} ще").format(n=len(day_tasks) - 3), size=11, color=T["text_soft"]))

        return ft.Container(
            content=ft.Column(items, spacing=2),
            expand=1,
            height=125,
            padding=6,
            bgcolor=T["surface"] if in_month else T["surface_alt"],
            border_radius=10,
            on_click=lambda e, day=d: on_day_click("plan", day),
        )

    def build_summary_cell(d, day_tasks, memory):
        in_month = d.month == state["month"]
        is_today = d == datetime.date.today()
        memory = memory or {}
        photo = memory.get("photo_path")
        mood = memory.get("mood_emoji")

        layers = []
        if photo:
            layers.append(ft.Image(src=photo_url(photo), fit=FIT_COVER, border_radius=10,
                                   left=0, top=0, right=0, bottom=0))

        num_color = T["on_accent"] if is_today else OVERLAY_TEXT
        layers.append(ft.Container(
            content=ft.Text(str(d.day), size=12, weight="bold", color=num_color),
            bgcolor=T["accent"] if is_today else OVERLAY_BG,
            padding=ft.Padding(left=6, top=2, right=6, bottom=2),
            border_radius=10,
            left=6, top=6,
        ))

        if mood:
            layers.append(ft.Container(
                content=ft.Text(mood, size=20),
                right=6, top=4,
            ))

        if day_tasks:
            done = sum(1 for t in day_tasks if t.get("is_done"))
            layers.append(ft.Container(
                content=ft.Text(f"✓ {done}/{len(day_tasks)}", size=11, color="#33404D"),
                bgcolor=OVERLAY_BG,
                padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                border_radius=8,
                left=6, bottom=6,
            ))

        bg = T["surface_alt"] if d > datetime.date.today() else T["surface"]

        return ft.Container(
            content=ft.Stack(layers, height=125),
            expand=1,
            height=125,
            bgcolor=bg,
            border_radius=10,
            opacity=1 if in_month else 0.45,
            on_click=lambda e, day=d: on_day_click("summary", day),
        )

    def build_calendar_view(mode):
        y, m = state["year"], state["month"]
        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(y, m)

        by_day = {}
        for t in all_tasks():
            if t.get("due_date"):
                by_day.setdefault(t["due_date"], []).append(t)

        memories = {}
        if mode == "summary":
            try:
                rows = requests.get(f"{API}/days", params={
                    "start": weeks[0][0].isoformat(),
                    "end": weeks[-1][-1].isoformat(),
                }).json()
                memories = {r["memory_date"]: r for r in rows}
            except Exception:
                memories = {}

        title = ft.Text(tr("Календар") if mode == "plan" else tr("Щоденник"), size=26, weight="bold")

        style_row = ft.Row([
            chip(tr("Планування"), mode == "plan", lambda e: go("calendar")),
            chip(tr("Підсумки"), mode == "summary", lambda e: go("diary")),
            ft.TextButton(tr("🖨 Друк місяця"), on_click=lambda e: open_print_dialog()),
        ], spacing=8, wrap=True)

        header = ft.Row(
            [
                ft.TextButton("‹", on_click=lambda e: shift_month(-1)),
                ft.Text(f"{MONTHS[m - 1]} {y}", size=22, weight="bold"),
                ft.TextButton("›", on_click=lambda e: shift_month(1)),
                ft.TextButton(tr("Сьогодні"), on_click=go_today_calendar),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        weekdays = ft.Row(
            [ft.Container(ft.Text(w, size=12, color=T["text_soft"], text_align=ft.TextAlign.CENTER),
                          expand=1) for w in WEEKDAYS],
            spacing=6,
        )

        rows_ui = []
        for week in weeks:
            cells = []
            for d in week:
                iso = d.isoformat()
                if mode == "plan":
                    cells.append(build_plan_cell(d, by_day.get(iso, [])))
                else:
                    cells.append(build_summary_cell(d, by_day.get(iso, []), memories.get(iso)))
            rows_ui.append(ft.Row(cells, spacing=6))
        grid = ft.Column(rows_ui, spacing=6)

        parts = [title, style_row, header]
        if mode == "summary":
            parts.append(ft.Text(tr("Натисни на день, щоб додати фото, настрій і записку 🌸"),
                                 size=12, color=T["text_soft"]))
        if mode == "summary":
            filled, total = fill_stats(list(memories.values()), y, m)
            parts.append(month_fill_card(filled, total, MONTHS[m - 1]))
        parts += [weekdays, grid]
        return parts

    # ---------- налаштування ----------
    def save_setting(key, value):
        settings = load_settings()
        settings[key] = value
        save_settings(settings)

    def set_theme(key):
        state["theme"] = key
        apply_theme_colors(key)
        apply_page_theme()
        save_setting("theme", key)
        render()

    def set_lang(code):
        set_language(code)
        refresh_lists()
        state["language"] = code
        save_setting("language", code)
        render()

    def section_card(title, body):
        return ft.Container(
            content=ft.Column([ft.Text(title, size=16, weight="bold", color=T["text"]), body],
                              spacing=12),
            bgcolor=T["surface"],
            padding=18,
            border_radius=16,
        )

    def build_settings_view():
        theme_cards = []
        for key, th in THEMES.items():
            selected = state["theme"] == key
            theme_cards.append(ft.Container(
                content=ft.Row(
                    [ft.Container(width=22, height=22, bgcolor=th["dot"], border_radius=11),
                     ft.Text(tr(th["name"]), size=14,
                             weight="bold" if selected else "normal")],
                    spacing=8, tight=True),
                bgcolor=T["accent_soft"] if selected else T["surface_alt"],
                padding=ft.Padding(left=14, top=10, right=16, bottom=10),
                border_radius=16,
                on_click=lambda e, k=key: set_theme(k),
            ))
        lang_chips = [chip(name, state["language"] == code, lambda e, c=code: set_lang(c))
                      for code, name in LANGS.items()]
        return [
            ft.Text(tr("Налаштування"), size=26, weight="bold"),
            section_card(tr("Колірна тема"), ft.Row(theme_cards, spacing=10, wrap=True)),
            section_card(tr("Мова"), ft.Row(lang_chips, spacing=8, wrap=True)),
            ft.Text(tr("Налаштування зберігаються автоматично."), size=12, color=T["text_muted"]),
        ]

    # ---------- про Memio ----------
    def build_about_view():
        email = about_config.CONTACT_EMAIL
        feedback = ft.TextField(label=tr("Що б ти хотів змінити чи додати?"),
                                multiline=True, min_lines=3, max_lines=6)
        status = ft.Text("", size=12, color=T["text_soft"])

        def mail_url(body=""):
            url = f"mailto:{email}?subject={quote('Memio')}"
            return url + (f"&body={quote(body)}" if body else "")

        def write_mail(e):
            open_url(mail_url())

        def send_feedback(e):
            text = (feedback.value or "").strip()
            if not text:
                status.value = tr("Напиши кілька слів, щоб було що надсилати.")
            else:
                open_url(mail_url(text))
                status.value = tr("Відкрив поштову програму. Якщо вона не відкрилась, напиши на {email}").format(email=email)
            page.update()

        def line(label, value):
            return ft.Row([ft.Text(label + ":", size=13, color=T["text_muted"], width=80),
                           ft.Text(value, size=14, color=T["text"], selectable=True)],
                          spacing=8)

        about_rows = [
            ft.Text(tr("Memio — затишний планувальник і щоденник: плануй день вранці, а ввечері зберігай його фото, настрій і записку."),
                    size=14, color=T["text"]),
            line(tr("Версія"), about_config.APP_VERSION),
            line(tr("Автор"), about_config.AUTHOR_NAME),
            line(tr("Пошта"), email),
        ]
        buttons = [ft.TextButton(tr("Написати листа"), on_click=write_mail)]
        if about_config.WEBSITE_URL:
            buttons.append(ft.TextButton(
                tr("Сайт"), on_click=lambda e: open_url(about_config.WEBSITE_URL)))
        about_rows.append(ft.Row(buttons, spacing=0, wrap=True))

        cards = [
            ft.Text(tr("Про Memio"), size=26, weight="bold"),
            section_card("Memio", ft.Column(about_rows, spacing=8)),
            section_card(tr("Відгук або ідея"), ft.Column(
                [feedback, ft.Row([ft.TextButton(tr("Надіслати поштою"), on_click=send_feedback)]),
                 status], spacing=6)),
        ]
        if about_config.SUPPORT_URL:
            cards.append(section_card(tr("Підтримати проєкт"), ft.Column([
                ft.Text(tr("Memio безкоштовний. Якщо він тобі подобається, можеш підтримати розробку."),
                        size=13, color=T["text_soft"]),
                ft.Row([ft.TextButton(tr("Підтримати проєкт"),
                                      on_click=lambda e: open_url(about_config.SUPPORT_URL))]),
            ], spacing=6)))
        return cards

    # ---------- бокове меню (висувається й зсуває вміст) ----------
    def go(view):
        flush_note()
        state["view"] = view
        render()

    def toggle_sidebar(e):
        state["sidebar_open"] = not state["sidebar_open"]
        refresh_sidebar(rebuild=False)

    def nav_item(key, label):
        active = state["view"] == key
        return ft.Container(
            content=ft.Text(label, size=15, weight="bold" if active else "normal",
                            color=T["text"]),
            bgcolor=T["column"] if active else None,
            padding=12,
            border_radius=12,
            on_click=lambda e, k=key: go(k),
        )

    def build_sidebar():
        main_items = [("board", tr("🗂  Плани")), ("myday", tr("🌸  Мій день")),
                      ("calendar", tr("📅  Календар")), ("diary", tr("📖  Щоденник"))]
        bottom_items = [("settings", tr("⚙  Налаштування")), ("about", tr("💙  Про Memio"))]

        menu = ft.Container(
            content=ft.Column(
                [ft.Text(tr("Меню"), size=12, color=T["text_muted"]),
                 *[nav_item(k, l) for k, l in main_items],
                 ft.Container(height=18),
                 *[nav_item(k, l) for k, l in bottom_items]],
                spacing=6,
            ),
            width=SB_OPEN - SB_HANDLE,
            padding=ft.Padding(left=12, top=16, right=4, bottom=12),
        )
        handle = ft.Container(
            content=ft.Text("☰", size=18, color=T["accent"]),
            width=SB_HANDLE,
            height=56,
            padding=ft.Padding(left=8, top=14, right=0, bottom=0),
            on_click=toggle_sidebar,
        )
        return ft.Row([menu, handle], spacing=0,
                      vertical_alignment=ft.CrossAxisAlignment.START)

    def refresh_sidebar(update=True, rebuild=True):
        is_open = state["sidebar_open"]
        sidebar.left = 0 if is_open else -(SB_OPEN - SB_HANDLE)
        sidebar.bgcolor = T["surface"]
        sidebar.shadow = (ft.BoxShadow(blur_radius=20, color="#33000000", offset=ft.Offset(2, 0))
                          if is_open else None)
        if rebuild:
            sidebar.content = build_sidebar()
        # вміст зсувається разом із краєм меню, а не ховається під ним
        content_wrap.padding = ft.Padding(
            left=(SB_OPEN if is_open else SB_HANDLE) + SB_GAP, top=0, right=0, bottom=0)
        if update:
            page.update()

    def on_sidebar_hover(e):
        inside = str(e.data).lower() == "true"
        if inside != state["sidebar_open"]:
            state["sidebar_open"] = inside
            refresh_sidebar(rebuild=False)

    sidebar.on_hover = on_sidebar_hover

    # ---------- загальний рендер ----------
    def render():
        refresh_sidebar(update=False)
        use_dark_logo = T["dark"] and LOGO_DARK.exists()
        logo_img = ft.Image(src="logo_dark.png" if use_dark_logo else "logo.png", height=44)
        if T["logo_plate"] and not use_dark_logo:
            logo = ft.Row([ft.Container(
                content=logo_img, bgcolor=T["logo_plate"], border_radius=12,
                padding=ft.Padding(left=10, top=4, right=10, bottom=4))])
        else:
            logo = ft.Row([logo_img])
        view = state["view"]
        if view == "calendar":
            parts = build_calendar_view("plan")
        elif view == "myday":
            parts = build_day_view()
        elif view == "diary":
            parts = build_calendar_view("summary")
        elif view == "settings":
            parts = build_settings_view()
        elif view == "about":
            parts = build_about_view()
        else:
            parts = build_board_view()
        content_area.controls = [logo] + parts
        page.update()

    page.add(ft.Stack([content_wrap, sidebar], expand=True))
    load()
