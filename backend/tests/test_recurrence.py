from datetime import date

from app.recurrence import MAX_OCCURRENCES, occurrences


def test_weekly_until_end_of_year():
    dates = occurrences(date(2026, 10, 29), "weekly", date(2026, 12, 31))
    assert dates[0] == date(2026, 10, 29)
    assert dates[1] == date(2026, 11, 5)
    assert dates[-1] == date(2026, 12, 31)
    assert len(dates) == 10


def test_daily_range_is_inclusive():
    dates = occurrences(date(2026, 10, 29), "daily", date(2026, 11, 1))
    assert dates == [date(2026, 10, 29), date(2026, 10, 30), date(2026, 10, 31), date(2026, 11, 1)]


def test_weekdays_skip_weekends():
    dates = occurrences(date(2026, 10, 30), "weekdays", date(2026, 11, 4))  # п'ятниця
    assert dates == [date(2026, 10, 30), date(2026, 11, 2), date(2026, 11, 3), date(2026, 11, 4)]


def test_monthly_keeps_original_day_after_short_month():
    dates = occurrences(date(2026, 1, 31), "monthly", date(2026, 4, 30))
    assert dates == [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31), date(2026, 4, 30)]


def test_monthly_crosses_year_boundary():
    dates = occurrences(date(2026, 11, 15), "monthly", date(2027, 2, 15))
    assert dates == [date(2026, 11, 15), date(2026, 12, 15), date(2027, 1, 15), date(2027, 2, 15)]


def test_until_before_start_gives_single_date():
    assert occurrences(date(2026, 10, 29), "weekly", date(2026, 10, 1)) == [date(2026, 10, 29)]


def test_unknown_rule_gives_single_date():
    assert occurrences(date(2026, 10, 29), "yearly", date(2030, 1, 1)) == [date(2026, 10, 29)]


def test_series_is_capped():
    assert len(occurrences(date(2026, 1, 1), "daily", date(2040, 1, 1))) == MAX_OCCURRENCES
