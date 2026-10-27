import datetime
import flet as ft
import requests

API = "http://127.0.0.1:8000"

PRIORITIES = {
    "red": ("#F28B82", "Високий"),
    "yellow": ("#FDD663", "Середній"),
    "green": ("#81C995", "Низький"),
}


def main(page: ft.Page):
    page.title = "Memio"
    page.bgcolor = "#EAF4FB"
    page.padding = 20
    page.scroll = "auto"

    board = ft.Row(spacing=15, vertical_alignment=ft.CrossAxisAlignment.START)

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
    def move(task_id, column_id):
        requests.patch(f"{API}/tasks/{task_id}/move",
                       json={"column_id": column_id, "position": 9999})
        load()

    def delete(task_id):
        requests.delete(f"{API}/tasks/{task_id}")
        load()

    # ---------- вікно «нове / редагувати завдання» ----------
    def open_task_dialog(column_id, task=None):
        topics = requests.get(f"{API}/topics").json()
        state = {
            "priority": (task or {}).get("priority", "green"),
            "topic_id": (task or {}).get("topic_id"),
        }

        title = ft.TextField(label="Назва", value=task["title"] if task else "", autofocus=True)
        desc = ft.TextField(label="Опис (необовʼязково)",
                            value=(task or {}).get("description") or "",
                            multiline=True, min_lines=2, max_lines=5)
        default_due = (task or {}).get("due_date") or ("" if task else datetime.date.today().isoformat())
        due = ft.TextField(label="Дата РРРР-ММ-ДД (необовʼязково)", value=default_due)
        new_topic = ft.TextField(label="Або нова тема", dense=True)

        prio_row = ft.Row(spacing=8, wrap=True)
        topic_row = ft.Row(spacing=6, wrap=True)

        def pick_priority(key):
            state["priority"] = key
            refresh()

        def pick_topic(topic_id):
            state["topic_id"] = topic_id
            refresh()

        def refresh():
            prio_row.controls = [
                ft.Container(
                    content=ft.Row([ft.Text("●", color=color), ft.Text(label, size=12)], spacing=5, tight=True),
                    bgcolor=color if state["priority"] == key else "#F1F1F1",
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
                    bgcolor="#9CCBEA" if state["topic_id"] == tid else "#F1F1F1",
                    padding=8,
                    border_radius=16,
                    on_click=lambda e, t=tid: pick_topic(t),
                )
                for tid, name in options
            ]
            page.update()

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

            topic_id = state["topic_id"]
            if new_topic.value.strip():
                r = requests.post(f"{API}/topics", json={"name": new_topic.value.strip()})
                topic_id = r.json()["id"]

            payload = {
                "title": t,
                "description": desc.value.strip() or None,
                "due_date": d or None,
                "topic_id": topic_id,
                "priority": state["priority"],
            }
            if task:
                requests.patch(f"{API}/tasks/{task['id']}", json=payload)
            else:
                payload["column_id"] = column_id
                requests.post(f"{API}/tasks", json=payload)
            close_dialog(dlg)
            load()

        def remove(e):
            close_dialog(dlg)
            delete(task["id"])

        actions = [ft.TextButton("Скасувати", on_click=lambda e: close_dialog(dlg))]
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

    # ---------- картки та колонки ----------
    def build_card(task, idx, columns):
        color = PRIORITIES.get(task.get("priority"), PRIORITIES["green"])[0]
        buttons = []
        if idx > 0:
            prev_id = columns[idx - 1]["id"]
            buttons.append(ft.TextButton("←", on_click=lambda e, t=task["id"], c=prev_id: move(t, c)))
        if idx < len(columns) - 1:
            next_id = columns[idx + 1]["id"]
            buttons.append(ft.TextButton("→", on_click=lambda e, t=task["id"], c=next_id: move(t, c)))

        lines = [ft.Row([ft.Text("●", color=color, size=16),
                         ft.Text(task["title"], size=15, weight="bold", expand=True)], spacing=6)]
        if task.get("topic"):
            lines.append(ft.Text(f"#{task['topic']['name']}", size=11, color="#4A90C2"))
        if task.get("description"):
            lines.append(ft.Text(task["description"], size=12, color="#5B6B7A"))
        if task.get("due_date"):
            lines.append(ft.Text(f"📅 {task['due_date']}", size=12, color="#5B6B7A"))
        lines.append(ft.Row(buttons, spacing=0))

        return ft.Container(
            content=ft.Column(lines, spacing=3),
            bgcolor="white",
            padding=10,
            border_radius=12,
            on_click=lambda e, t=task, c=task["column_id"]: open_task_dialog(c, t),
        )

    def build_column(col, idx, columns):
        cards = [build_card(t, idx, columns) for t in col["tasks"]]
        add_btn = ft.TextButton("+ Додати завдання",
                                on_click=lambda e, c=col["id"]: open_task_dialog(c))
        return ft.Container(
            width=280,
            padding=12,
            bgcolor="#CFE6F5",
            border_radius=16,
            content=ft.Column([ft.Text(col["title"], size=18, weight="bold"), *cards, add_btn]),
        )

    def load():
        columns = requests.get(f"{API}/board").json()
        board.controls = [build_column(c, i, columns) for i, c in enumerate(columns)]
        page.update()

    page.add(
        ft.Row([ft.Image(src="logo.png", height=56)]),
        board,
    )
    load()