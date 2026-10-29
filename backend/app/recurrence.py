"""Логіка повторюваних завдань (без залежностей, тому легко тестується)."""
import calendar
from datetime import date, timedelta

RULES = ("daily", "weekdays", "weekly", "monthly")


def advance(d: date, rule: str) -> date:
    """Наступна дата за правилом, починаючи з d."""
    if rule == "daily":
        return d + timedelta(days=1)
    if rule == "weekly":
        return d + timedelta(days=7)
    if rule == "weekdays":
        nxt = d + timedelta(days=1)
        while nxt.weekday() >= 5:  # субота, неділя
            nxt += timedelta(days=1)
        return nxt
    if rule == "monthly":
        year = d.year + d.month // 12
        month = d.month % 12 + 1
        return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))
    raise ValueError(f"unknown rule: {rule}")


def next_occurrence(base: date, rule: str | None, today: date) -> date | None:
    """
    Дата наступного повтору після виконання завдання.
    Завжди строго після сьогодні, тож пропущені дні не накопичуються.
    """
    if rule not in RULES:
        return None
    nxt = advance(base, rule)
    while nxt <= today:
        nxt = advance(nxt, rule)
    return nxt
