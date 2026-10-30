"""Повторювані завдання: дати всієї серії наперед (без залежностей, легко тестується)."""
import calendar
from datetime import date, timedelta

RULES = ("daily", "weekdays", "weekly", "monthly")
MAX_OCCURRENCES = 400  # запобіжник, щоб одна серія не роздула базу


def add_months(d: date, n: int) -> date:
    """Дата через n місяців; якщо дня немає в місяці, береться останній (31 січня -> 28 лютого)."""
    year = d.year + (d.month - 1 + n) // 12
    month = (d.month - 1 + n) % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def occurrences(start: date, rule: str, until: date) -> list[date]:
    """
    Усі дати серії від start до until включно (перша дата це сам start).
    Для невідомого правила або until раніше за start повертається лише start.
    """
    dates = [start]
    if rule not in RULES:
        return dates

    k = 0
    current = start
    while len(dates) < MAX_OCCURRENCES:
        if rule == "weekdays":
            current += timedelta(days=1)
            while current.weekday() >= 5:  # субота, неділя
                current += timedelta(days=1)
            nxt = current
        else:
            k += 1
            if rule == "daily":
                nxt = start + timedelta(days=k)
            elif rule == "weekly":
                nxt = start + timedelta(days=7 * k)
            else:  # monthly
                nxt = add_months(start, k)
        if nxt > until:
            break
        dates.append(nxt)
    return dates
