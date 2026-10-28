import calendar
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

import flet as ft
import requests

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
            title="Обери фото дня",
            filetypes=[("Зображення", "*.jpg *.jpeg *.png *.webp *.bmp"), ("Усі файли", "*.*")],
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

    apply_theme_colors(load_settings().get("theme", "blue"))
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
                if not x.get("is_done") and x.get("due_date") and x["due_date"] < t]

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
            return ("Сьогодні · " + name) if a == datetime.date.today() else name
        if p == "week":
            s, e = rng
            return f"{s.day} {MONTHS_GEN[s.month - 1]} – {e.day} {MONTHS_GEN[e.month - 1]}"
        if p == "month":
            return f"{MONTHS[a.month - 1]} {a.year}"
        if p == "year":
            return str(a.year)
        return "Усі завдання"

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
    def open_task_dialog(column_id, task=None, default_due=None, on_done=None):
        topics = requests.get(f"{API}/topics").json()
        st = {
            "priority": (task or {}).get("priority", "green"),
            "topic_id": (task or {}).get("topic_id"),
        }

        title = ft.TextField(label="Назва", value=task["title"] if task else "", autofocus=True)
        desc = ft.TextField(label="Опис (необовʼязково)",
                            value=(task or {}).get("description") or "",
                            multiline=True, min_lines=2, max_lines=5)
        start_due = (task or {}).get("due_date") or (
            "" if task else (default_due or datetime.date.today().isoformat()))
        due = ft.TextField(label="Дата РРРР-ММ-ДД (необовʼязково)", value=start_due)
        new_topic = ft.TextField(label="Або нова тема", dense=True)

        prio_row = ft.Row(spacing=8, wrap=True)
        topic_row = ft.Row(spacing=6, wrap=True)

        def pick_priority(key):
            st["priority"] = key
            refresh()

        def pick_topic(topic_id):
            st["topic_id"] = topic_id
            refresh()

        def refresh():
            prio_row.controls = [
                ft.Container(
                    content=ft.Row([ft.Text("●", color=color), ft.Text(label, size=12)],
                                   spacing=5, tight=True),
                    bgcolor=color if st["priority"] == key else T["surface_alt"],
                    padding=8,
                    border_radius=16,
                    on_click=lambda e, k=key: pick_priority(k),
                )
                for key, (color, label) in PRIORITIES.items()
            ]
            options = [(None, "Без теми")] + [(t["id"], t["name"]) for t in topics]
            topic_row.controls = [
                ft.Container(
                    content=ft.Text(name, size=12),
                    bgcolor=T["accent_soft"] if st["topic_id"] == tid else T["surface_alt"],
                    padding=8,
                    border_radius=16,
                    on_click=lambda e, t=tid: pick_topic(t),
                )
                for tid, name in options
            ]
            page.update()

        def finish():
            close_dialog(dlg)
            load()
            if on_done:
                on_done()

        def save(e):
            t = title.value.strip()
            if not t:
                title.error_text = "Введи назву"
                page.update()
                return
            d = due.value.strip()
            if d:
                try:
                    datetime.date.fromisoformat(d)
                except ValueError:
                    due.error_text = "Формат: 2026-10-31"
                    page.update()
                    return

            topic_id = st["topic_id"]
            if new_topic.value.strip():
                r = requests.post(f"{API}/topics", json={"name": new_topic.value.strip()})
                topic_id = r.json()["id"]

            payload = {
                "title": t,
                "description": desc.value.strip() or None,
                "due_date": d or None,
                "topic_id": topic_id,
                "priority": st["priority"],
            }
            if task:
                requests.patch(f"{API}/tasks/{task['id']}", json=payload)
            else:
                payload["column_id"] = column_id
                requests.post(f"{API}/tasks", json=payload)
            finish()

        def remove(e):
            close_dialog(dlg)
            delete(task["id"])
            if on_done:
                on_done()

        def cancel(e):
            close_dialog(dlg)
            if on_done:
                on_done()

        actions = [ft.TextButton("Скасувати", on_click=cancel)]
        if task:
            actions.insert(0, ft.TextButton("Видалити", on_click=remove))
        actions.append(ft.TextButton("Зберегти", on_click=save))

        dlg = ft.AlertDialog(
            bgcolor=T["surface"],
            title=ft.Text("Редагувати завдання" if task else "Нове завдання"),
            content=ft.Column(
                [title, desc, due,
                 ft.Text("Пріоритет", size=12), prio_row,
                 ft.Text("Тема", size=12), topic_row, new_topic],
                tight=True, width=400, scroll="auto",
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
                         ft.Text(task["title"], size=15, weight="bold",
                                 color=title_color, expand=True)], spacing=6)]
        if task.get("topic"):
            lines.append(ft.Text(f"#{task['topic']['name']}", size=11, color=T["accent"]))
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

    def build_column(col, idx, columns):
        visible = [t for t in col["tasks"] if matches(t)]
        cards = [build_card(t, idx, columns) for t in visible]
        add_btn = ft.TextButton(
            "+ Додати завдання",
            on_click=lambda e, c=col["id"]: open_task_dialog(c, default_due=default_due_for_period()),
        )
        box = ft.Container(
            width=280,
            padding=12,
            bgcolor=T["column"],
            border_radius=16,
            content=ft.Column([ft.Text(col["title"], size=18, weight="bold"), *cards, add_btn]),
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

        header = ft.Text("Плани", size=26, weight="bold")

        nav_controls = []
        if state["period"] != "all":
            nav_controls.append(ft.TextButton("‹", on_click=lambda e: shift_period(-1)))
        nav_controls.append(ft.Text(period_title(), size=20, weight="bold"))
        if state["period"] != "all":
            nav_controls.append(ft.TextButton("›", on_click=lambda e: shift_period(1)))
            nav_controls.append(ft.TextButton("Сьогодні", on_click=go_today_board))
        nav = ft.Row(nav_controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        period_row = ft.Row(
            [chip(label, state["period"] == key, lambda e, k=key: set_period(k))
             for key, label in PERIODS],
            spacing=8, wrap=True,
        )

        used = {t.get("topic_id") for t in all_tasks()}
        topic_chips = [chip("Усі теми", state["topic_filter"] is None,
                            lambda e: set_topic_filter(None))]
        for t in state["topics"]:
            if t["id"] in used:
                topic_chips.append(chip(f"#{t['name']}", state["topic_filter"] == t["id"],
                                        lambda e, tid=t["id"]: set_topic_filter(tid)))
        topic_row = ft.Row(topic_chips, spacing=8, wrap=True)

        total = sum(1 for t in all_tasks() if matches(t))
        board = ft.Row([build_column(c, i, columns) for i, c in enumerate(columns)],
                       spacing=15, vertical_alignment=ft.CrossAxisAlignment.START, scroll="auto")

        parts = [header, nav, period_row, topic_row]

        overdue = overdue_tasks()
        if overdue:
            parts.append(ft.Container(
                content=ft.Row(
                    [ft.Text(f"🌿 Невиконаних справ з минулих днів: {len(overdue)}. "
                             "Нічого страшного, їх можна перенести.",
                             size=13, color=T["text_soft"], expand=True),
                     ft.TextButton("Перенести на сьогодні", on_click=carry_over)],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=T["warn_bg"],
                padding=ft.Padding(left=14, top=6, right=8, bottom=6),
                border_radius=12,
            ))

        if total == 0:
            parts.append(ft.Text("Тут поки нічого не заплановано. Спокійний час 🌿", color=T["text_soft"]))
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
                info.append(ft.Text(f"#{t['topic']['name']}", size=11, color=T["accent"]))
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
            rows = [ft.Text("Поки нічого не заплановано. Спокійний день 🌿", color=T["text_soft"])]

        title = f"{WEEKDAYS_FULL[d.weekday()]}, {d.day} {MONTHS_GEN[d.month - 1]}"
        dlg = ft.AlertDialog(
            bgcolor=T["surface"],
            title=ft.Text(title),
            content=ft.Column(rows, tight=True, width=380, scroll="auto", spacing=8),
            actions=[
                ft.TextButton("Закрити", on_click=lambda e: close_dialog(dlg)),
                ft.TextButton("+ Додати завдання", on_click=add_task),
            ],
        )
        open_dialog(dlg)

    # ---------- «Мій день»: підсумок дня ----------
    def open_summary_dialog(d):
        iso = d.isoformat()
        info = requests.get(f"{API}/days/{iso}").json()
        data = {"mood": info.get("mood_emoji"), "photo": info.get("photo_path")}

        note = ft.TextField(label="Записка дня (до 280 символів)",
                            value=info.get("note") or "",
                            multiline=True, min_lines=2, max_lines=4, max_length=280)
        photo_holder = ft.Container()
        mood_row = ft.Row(spacing=6, wrap=True)
        msg = ft.Text("", size=12, color="#B45309")

        def refresh_photo(update=True):
            if data["photo"]:
                photo_holder.content = ft.Column([
                    ft.Image(src=photo_url(data["photo"]), width=380, height=220,
                             fit=FIT_COVER, border_radius=12),
                    ft.Row([ft.TextButton("Змінити фото", on_click=pick),
                            ft.TextButton("Прибрати фото", on_click=remove_photo)], spacing=0),
                ], spacing=2)
            else:
                photo_holder.content = ft.Container(
                    content=ft.Column(
                        [ft.Text("📷  Додати фото дня", size=14, color=T["accent"])],
                        height=120, width=380,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=T["surface_alt"],
                    border_radius=12,
                    on_click=pick,
                )
            if update:
                page.update()

        def refresh_mood(update=True):
            mood_row.controls = [
                ft.Container(
                    content=ft.Text(m, size=22),
                    bgcolor=T["accent_soft"] if data["mood"] == m else T["surface_alt"],
                    padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                    border_radius=14,
                    on_click=lambda e, m=m: pick_mood(m),
                )
                for m in MOODS
            ]
            if update:
                page.update()

        def pick_mood(m):
            data["mood"] = None if data["mood"] == m else m
            refresh_mood()

        def pick(e):
            path, err = pick_photo_path()
            if err:
                msg.value = "Не вдалося відкрити вибір файлу."
                page.update()
                return
            if not path:
                return
            try:
                with open(path, "rb") as f:
                    r = requests.post(f"{API}/days/{iso}/photo",
                                      files={"file": (os.path.basename(path), f)})
                if r.ok:
                    data["photo"] = r.json().get("photo_path")
                    msg.value = ""
                else:
                    msg.value = "Не вдалося завантажити фото. Спробуй інший файл (jpg або png)."
            except Exception:
                msg.value = "Не вдалося завантажити фото."
            refresh_photo(update=False)
            page.update()

        def remove_photo(e):
            requests.delete(f"{API}/days/{iso}/photo")
            data["photo"] = None
            refresh_photo()

        def persist():
            requests.put(f"{API}/days/{iso}", json={
                "note": note.value.strip() or None,
                "mood_emoji": data["mood"],
            })

        def finish(e=None):
            close_dialog(dlg)
            render()

        def save(e):
            persist()
            finish()

        def to_plans(e):
            persist()
            close_dialog(dlg)
            render()
            open_day_dialog(d)

        day_tasks = [t for t in all_tasks() if t.get("due_date") == iso]
        done = [t for t in day_tasks if t.get("is_done")]
        todo = [t for t in day_tasks if not t.get("is_done")]
        if not day_tasks:
            task_block = [ft.Text("На цей день нічого не було заплановано 🌿",
                                  size=13, color=T["text_soft"])]
        else:
            if len(done) == len(day_tasks):
                hint = "Усе зроблено, чудовий день 💙"
            elif not done:
                hint = "Іноді день це просто відпочинок 🌿"
            else:
                hint = "Решту можна спокійно перенести 🌿"
            task_block = [
                ft.Text(f"Зроблено {len(done)} з {len(day_tasks)}", size=14, weight="bold"),
                ft.Text(hint, size=12, color=T["text_soft"]),
            ]
            task_block += [ft.Text("✓ " + t["title"], size=13, color=T["done"]) for t in done]
            task_block += [ft.Text("○ " + t["title"], size=13, color=T["text_muted"]) for t in todo]

        refresh_photo(update=False)
        refresh_mood(update=False)

        title = f"{d.day} {MONTHS_GEN[d.month - 1]} · {WEEKDAYS_FULL[d.weekday()]}"
        dlg = ft.AlertDialog(
            bgcolor=T["surface"],
            title=ft.Text(title),
            content=ft.Column(
                [photo_holder,
                 ft.Text("Настрій", size=12), mood_row,
                 note, msg,
                 ft.Divider(),
                 *task_block],
                tight=True, width=400, scroll="auto", spacing=8,
            ),
            actions=[
                ft.TextButton("Плани дня", on_click=to_plans),
                ft.TextButton("Закрити", on_click=finish),
                ft.TextButton("Зберегти", on_click=save),
            ],
        )
        open_dialog(dlg)

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
            return {"year": y, "month": m, "preview": preview, **st}

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
                label("Формат файлу"),
                chips_row("format", [("pdf", "PDF"), ("png", "PNG")]),
                label("Орієнтація аркуша A4"),
                chips_row("orientation", [("landscape", "Альбомна"), ("portrait", "Книжкова")]),
                label("Рамка"),
                chips_row("frame_style", [("none", "Без рамки"), ("line", "Лінія"),
                                          ("double", "Подвійна"), ("rounded", "Заокруглена"),
                                          ("dashed", "Пунктир")]),
                label("Колір рамки"),
                swatches,
                label("Товщина рамки"),
                chips_row("frame_width", [("thin", "Тонка"), ("medium", "Середня"),
                                          ("thick", "Товста")]),
                label("Клітинки днів"),
                chips_row("corners", [("round", "Круглі кути"), ("square", "Прямі кути")]),
                chips_row("show_logo", [(True, "З логотипом"), (False, "Без логотипа")]),
                ft.Text("Смайлики настрою не друкуються, лише фото й числа.",
                        size=11, color=T["text_muted"]),
            ]

        def refresh_preview():
            preview_holder.content = ft.Text("Оновлюю перегляд…", size=12, color=T["text_soft"])
            page.update()
            try:
                r = requests.post(f"{API}/print/month", json=payload(True), timeout=60)
                if r.ok:
                    name = r.json()["file"]
                    preview_holder.content = ft.Image(
                        src=f"{API}/exports/{name}?v={time.time()}", width=300)
                else:
                    preview_holder.content = ft.Text("Не вдалося створити перегляд", size=12)
            except Exception:
                preview_holder.content = ft.Text("Не вдалося створити перегляд", size=12)
            page.update()

        def set_opt(key, value):
            st[key] = value
            status.value = ""
            rebuild()
            page.update()
            refresh_preview()

        def create(e):
            status.value = "Створюю файл…"
            page.update()
            try:
                r = requests.post(f"{API}/print/month", json=payload(False), timeout=180)
                if r.ok:
                    info = r.json()
                    status.value = f"Готово: {info['file']} (папка exports)"
                    open_path(info["path"])
                else:
                    status.value = "Не вдалося створити файл."
            except Exception:
                status.value = "Не вдалося створити файл."
            page.update()

        def open_folder(e):
            EXPORTS_DIR.mkdir(exist_ok=True)
            open_path(EXPORTS_DIR)

        rebuild()
        dlg = ft.AlertDialog(
            bgcolor=T["surface"],
            title=ft.Text(f"Друк · {MONTHS[m - 1]} {y}"),
            content=ft.Column(
                [ft.Row([ft.Container(rows_col, width=330), preview_holder],
                        vertical_alignment=ft.CrossAxisAlignment.START, spacing=20),
                 status],
                tight=True, width=700, scroll="auto", spacing=10,
            ),
            actions=[
                ft.TextButton("Відкрити папку", on_click=open_folder),
                ft.TextButton("Закрити", on_click=lambda e: close_dialog(dlg)),
                ft.TextButton("Створити файл", on_click=create),
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
        if mode == "summary" and d <= datetime.date.today():
            open_summary_dialog(d)
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
            items.append(ft.Text(f"+{len(day_tasks) - 3} ще", size=11, color=T["text_soft"]))

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

        title = ft.Text("Календар" if mode == "plan" else "Мій день", size=26, weight="bold")

        style_row = ft.Row([
            chip("Планування", mode == "plan", lambda e: go("calendar")),
            chip("Підсумки", mode == "summary", lambda e: go("myday")),
            ft.TextButton("🖨 Друк місяця", on_click=lambda e: open_print_dialog()),
        ], spacing=8, wrap=True)

        header = ft.Row(
            [
                ft.TextButton("‹", on_click=lambda e: shift_month(-1)),
                ft.Text(f"{MONTHS[m - 1]} {y}", size=22, weight="bold"),
                ft.TextButton("›", on_click=lambda e: shift_month(1)),
                ft.TextButton("Сьогодні", on_click=go_today_calendar),
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
            parts.append(ft.Text("Натисни на день, щоб додати фото, настрій і записку 🌸",
                                 size=12, color=T["text_soft"]))
        parts += [weekdays, grid]
        return parts

    # ---------- бокове меню (висувається й зсуває вміст) ----------
    def go(view):
        state["view"] = view
        render()

    def set_theme(key):
        state["theme"] = key
        apply_theme_colors(key)
        apply_page_theme()
        settings = load_settings()
        settings["theme"] = key
        save_settings(settings)
        render()

    def toggle_sidebar(e):
        state["sidebar_open"] = not state["sidebar_open"]
        refresh_sidebar(rebuild=False)

    def build_sidebar():
        items = [("board", "🗂  Плани"), ("calendar", "📅  Календар"), ("myday", "🌸  Мій день")]
        nav = []
        for key, label in items:
            active = state["view"] == key
            nav.append(ft.Container(
                content=ft.Text(label, size=15, weight="bold" if active else "normal",
                                color=T["text"]),
                bgcolor=T["column"] if active else None,
                padding=12,
                border_radius=12,
                on_click=lambda e, k=key: go(k),
            ))

        swatches = []
        for key, th in THEMES.items():
            selected = state["theme"] == key
            swatches.append(ft.Container(
                content=ft.Column(
                    [ft.Text("✓" if selected else "", size=12, color=th["on_accent"]
                             if not th["dark"] else "#FFFFFF")],
                    width=26, height=26,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=26, height=26,
                bgcolor=th["dot"],
                border_radius=13,
                on_click=lambda e, k=key: set_theme(k),
            ))

        menu = ft.Container(
            content=ft.Column(
                [ft.Text("Меню", size=12, color=T["text_muted"]),
                 *nav,
                 ft.Container(height=14),
                 ft.Text("Тема", size=12, color=T["text_muted"]),
                 ft.Row(swatches, spacing=8)],
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
        logo_img = ft.Image(src="logo.png", height=44)
        if T["logo_plate"]:
            logo = ft.Row([ft.Container(
                content=logo_img, bgcolor=T["logo_plate"], border_radius=12,
                padding=ft.Padding(left=10, top=4, right=10, bottom=4))])
        else:
            logo = ft.Row([logo_img])
        if state["view"] == "calendar":
            parts = build_calendar_view("plan")
        elif state["view"] == "myday":
            parts = build_calendar_view("summary")
        else:
            parts = build_board_view()
        content_area.controls = [logo] + parts
        page.update()

    page.add(ft.Stack([content_wrap, sidebar], expand=True))
    load()
