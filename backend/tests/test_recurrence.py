from datetime import date

from app.recurrence import next_occurrence


def test_daily_done_on_the_day():
    assert next_occurrence(date(2026, 10, 29), "daily", date(2026, 10, 29)) == date(2026, 10, 30)


def test_daily_done_late_skips_missed_days():
    # завдання було на понеділок, зроблено в середу: наступне вже після середи
    assert next_occurrence(date(2026, 10, 26), "daily", date(2026, 10, 28)) == date(2026, 10, 29)


def test_weekly_done_early_keeps_schedule():
    # на понеділок 2 листопада, зроблено завчасно в середу 28 жовтня
    assert next_occurrence(date(2026, 11, 2), "weekly", date(2026, 10, 28)) == date(2026, 11, 9)


def test_weekdays_skip_weekend():
    friday = date(2026, 10, 30)
    assert next_occurrence(friday, "weekdays", friday) == date(2026, 11, 2)  # понеділок


def test_monthly_clamps_short_months():
    assert next_occurrence(date(2026, 1, 31), "monthly", date(2026, 1, 31)) == date(2026, 2, 28)


def test_monthly_crosses_year():
    assert next_occurrence(date(2026, 12, 15), "monthly", date(2026, 12, 15)) == date(2027, 1, 15)


def test_unknown_or_missing_rule():
    assert next_occurrence(date(2026, 10, 29), None, date(2026, 10, 29)) is None
    assert next_occurrence(date(2026, 10, 29), "yearly", date(2026, 10, 29)) is None
