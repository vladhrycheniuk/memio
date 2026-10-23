import flet as ft
import requests

API = "http://127.0.0.1:8000"


def main(page: ft.Page):
    page.title = "Memio"
    page.bgcolor = "#EAF4FB"
    page.padding = 20

    board = ft.Row(spacing=15, vertical_alignment=ft.CrossAxisAlignment.START)

    def move(task_id, column_id):
        requests.patch(f"{API}/tasks/{task_id}/move",
                       json={"column_id": column_id, "position": 9999})
        load()

    def delete(task_id):
        requests.delete(f"{API}/tasks/{task_id}")
        load()

    def add(column_id, field):
        title = field.value.strip()
        if title:
            requests.post(f"{API}/tasks", json={"title": title, "column_id": column_id})
        load()

    def build_card(task, idx, columns):
        buttons = []
        if idx > 0:
            prev_id = columns[idx - 1]["id"]
            buttons.append(ft.TextButton("←", on_click=lambda e, t=task["id"], c=prev_id: move(t, c)))
        if idx < len(columns) - 1:
            next_id = columns[idx + 1]["id"]
            buttons.append(ft.TextButton("→", on_click=lambda e, t=task["id"], c=next_id: move(t, c)))
        buttons.append(ft.TextButton("✕", on_click=lambda e, t=task["id"]: delete(t)))

        return ft.Container(
            content=ft.Column([ft.Text(task["title"], size=15), ft.Row(buttons, spacing=0)], spacing=2),
            bgcolor="white",
            padding=10,
            border_radius=12,
        )

    def build_column(col, idx, columns):
        field = ft.TextField(hint_text="Нова картка", dense=True,
                             on_submit=lambda e, c=col["id"]: add(c, e.control))
        cards = [build_card(t, idx, columns) for t in col["tasks"]]
        return ft.Container(
            width=280,
            padding=12,
            bgcolor="#CFE6F5",
            border_radius=16,
            content=ft.Column([ft.Text(col["title"], size=18, weight="bold"), *cards, field]),
        )

    def load():
        columns = requests.get(f"{API}/board").json()
        board.controls = [build_column(c, i, columns) for i, c in enumerate(columns)]
        page.update()

        page.add(
        ft.Row([ft.Image(src="logo.png", height=48), ft.Text("Memio", size=28, weight="bold")]),
        board,
    )
    load()