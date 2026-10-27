import calendar
import datetime
import flet as ft
import requests

API = "http://127.0.0.1:8000"

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

COL_BG = "#CFE6F5"
COL_HOVER = "#B5D9F0"
CHIP_ON = "#9CCBEA"
CHIP_OFF = "#FFFFFF"


def main(page: ft.Page):
    page.title = "Memio"
    page.bgcolor = "#EAF4FB"
    page.padding = 20

    today = datetime.date.today()
    state = {
        "view": "board",
        "period": "day",
        "anchor": today,
        "topic_filter": None,
        "year": today.year,
        "month": today.month,
        "columns": [],
        "topics": [],
    }

    content_area = ft.Column(expand=True, scroll="auto", spacing=15)
    sidebar = ft.Container(width=210, padding=16, bgcolor="white", border_radius=16)

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
    def load():
        state["columns"] = requests.get(f"{API}/board").json()
        state["topics"] = requests.get(f"{API}/topics").json()
        render()

    def move(task_id, column_id):
        requests.patch(f"{API}/tasks/{task_id}/move",
                       json={"column_id": column_id, "position": 9999})
        load()

    def delete(task_id):
        requests.delete(f"{API}/tasks/{task_id}")
        load()

    def all_tasks():
        return [t for col in state["columns"] for t in col["tasks"]]

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
                    bgcolor=color if st["priority"] == key else "#F1F1F1",
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
                    bgcolor=CHIP_ON if st["topic_id"] == tid else "#F1F1F1",
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
        title_color = "#8A98A5" if task.get("is_done") else "#1F2D3A"

        lines = [ft.Row([ft.Text("●", color=color, size=16),
                         ft.Text(task["title"], size=15, weight="bold",
                                 color=title_color, expand=True)], spacing=6)]
        if task.get("topic"):
            lines.append(ft.Text(f"#{task['topic']['name']}", size=11, color="#4A90C2"))
        if task.get("description"):
            lines.append(ft.Text(task["description"], size=12, color="#5B6B7A"))
        if task.get("due_date"):
            lines.append(ft.Text(f"📅 {task['due_date']}", size=12, color="#5B6B7A"))

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
            bgcolor="white",
            padding=10,
            border_radius=12,
        )

    def build_card(task, idx, columns):
        body = card_body(task, idx, columns, with_buttons=True)
        body.on_click = lambda e, t=task: open_task_dialog(t["column_id"], t)

        feedback = card_body(task, idx, columns, with_buttons=False)
        feedback.width = 256
        feedback.scale = 1.06
        feedback.rotate = 0.04
        feedback.shadow = ft.BoxShadow(blur_radius=18, color="#55000000", offset=ft.Offset(0, 6))

        ghost = card_body(task, idx, columns, with_buttons=False)
        ghost.opacity = 0.35

        return ft.Draggable(
            group="task",
            content=body,
            content_feedback=feedback,
            content_when_dragging=ghost,
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
            bgcolor=COL_BG,
            border_radius=16,
            content=ft.Column([ft.Text(col["title"], size=18, weight="bold"), *cards, add_btn]),
        )

        def will_accept(e):
            box.bgcolor = COL_HOVER
            page.update()

        def leave(e):
            box.bgcolor = COL_BG
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
            bgcolor=CHIP_ON if active else CHIP_OFF,
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

        topic_chips = [chip("Усі теми", state["topic_filter"] is None,
                            lambda e: set_topic_filter(None))]
        for t in state["topics"]:
            topic_chips.append(chip(f"#{t['name']}", state["topic_filter"] == t["id"],
                                    lambda e, tid=t["id"]: set_topic_filter(tid)))
        topic_row = ft.Row(topic_chips, spacing=8, wrap=True)

        total = sum(1 for t in all_tasks() if matches(t))
        board = ft.Row([build_column(c, i, columns) for i, c in enumerate(columns)],
                       spacing=15, vertical_alignment=ft.CrossAxisAlignment.START, scroll="auto")

        parts = [header, nav, period_row, topic_row]
        if total == 0:
            parts.append(ft.Text("Тут поки нічого не заплановано. Спокійний час 🌿", color="#5B6B7A"))
        parts.append(board)
        return parts

    # ---------- календар ----------
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
                info.append(ft.Text(f"#{t['topic']['name']}", size=11, color="#4A90C2"))
            if t.get("description"):
                info.append(ft.Text(t["description"], size=12, color="#5B6B7A"))
            rows.append(ft.Container(
                content=ft.Row([ft.Text("●", color=color, size=16),
                                ft.Column(info, spacing=2, expand=True)], spacing=8),
                bgcolor="#F3F8FC",
                padding=10,
                border_radius=10,
                on_click=lambda e, t=t: edit_task(t),
            ))
        if not rows:
            rows = [ft.Text("Поки нічого не заплановано. Спокійний день 🌿", color="#5B6B7A")]

        title = f"{WEEKDAYS_FULL[d.weekday()]}, {d.day} {MONTHS_GEN[d.month - 1]}"
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(rows, tight=True, width=380, scroll="auto", spacing=8),
            actions=[
                ft.TextButton("Закрити", on_click=lambda e: close_dialog(dlg)),
                ft.TextButton("+ Додати завдання", on_click=add_task),
            ],
        )
        open_dialog(dlg)

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

    def build_day_cell(d, day_tasks):
        in_month = d.month == state["month"]
        is_today = d == datetime.date.today()

        num_color = "white" if is_today else ("#1F2D3A" if in_month else "#9AA7B2")
        num = ft.Container(
            content=ft.Text(str(d.day), size=12, weight="bold", color=num_color),
            bgcolor="#4A90C2" if is_today else None,
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
            items.append(ft.Text(f"+{len(day_tasks) - 3} ще", size=11, color="#5B6B7A"))

        return ft.Container(
            content=ft.Column(items, spacing=2),
            expand=1,
            height=125,
            padding=6,
            bgcolor="white" if in_month else "#F3F8FC",
            border_radius=10,
            on_click=lambda e, day=d: open_day_dialog(day),
        )

    def build_calendar_view():
        y, m = state["year"], state["month"]

        by_day = {}
        for t in all_tasks():
            if t.get("due_date"):
                by_day.setdefault(t["due_date"], []).append(t)

        header = ft.Row(
            [
                ft.TextButton("‹", on_click=lambda e: shift_month(-1)),
                ft.Text(f"{MONTHS[m - 1]} {y}", size=24, weight="bold"),
                ft.TextButton("›", on_click=lambda e: shift_month(1)),
                ft.TextButton("Сьогодні", on_click=go_today_calendar),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        weekdays = ft.Row(
            [ft.Container(ft.Text(w, size=12, color="#5B6B7A", text_align=ft.TextAlign.CENTER),
                          expand=1) for w in WEEKDAYS],
            spacing=6,
        )

        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(y, m)
        grid = ft.Column(
            [ft.Row([build_day_cell(d, by_day.get(d.isoformat(), [])) for d in week], spacing=6)
             for week in weeks],
            spacing=6,
        )
        return [header, weekdays, grid]

    # ---------- меню та загальний рендер ----------
    def go(view):
        state["view"] = view
        render()

    def build_sidebar():
        items = [("board", "🗂  Плани"), ("calendar", "📅  Календар")]
        nav = []
        for key, label in items:
            active = state["view"] == key
            nav.append(ft.Container(
                content=ft.Text(label, size=15, weight="bold" if active else "normal"),
                bgcolor=COL_BG if active else None,
                padding=12,
                border_radius=12,
                on_click=lambda e, k=key: go(k),
            ))
        return ft.Column([ft.Image(src="logo.png", height=36), ft.Container(height=10), *nav], spacing=6)

    def render():
        sidebar.content = build_sidebar()
        if state["view"] == "calendar":
            content_area.controls = build_calendar_view()
        else:
            content_area.controls = build_board_view()
        page.update()

    page.add(
        ft.Row([sidebar, content_area], expand=True,
               vertical_alignment=ft.CrossAxisAlignment.START, spacing=20)
    )
    load()