"""Pure unit tests for the streak calculation algorithm, independent of the
database/HTTP layer, using dates relative to 'today' so they never go stale."""
from datetime import date, timedelta

from app.routers.habits import _calculate_streaks

TODAY = date.today()


def d(days_ago: int) -> date:
    return TODAY - timedelta(days=days_ago)


def test_empty_list():
    assert _calculate_streaks([]) == (0, 0)


def test_single_completion_today():
    assert _calculate_streaks([d(0)]) == (1, 1)


def test_broken_streak_if_last_completion_not_today_or_yesterday():
    # last completion 3 days ago -> current streak is 0, but longest is preserved
    dates = [d(5), d(4), d(3)]
    current, longest = _calculate_streaks(dates)
    assert current == 0
    assert longest == 3


def test_current_streak_continues_from_yesterday():
    dates = [d(2), d(1)]
    current, longest = _calculate_streaks(dates)
    assert current == 2
    assert longest == 2


def test_longest_streak_preserved_even_if_current_is_shorter():
    # 4-day streak in the past, then a gap, then today only
    dates = [d(10), d(9), d(8), d(7), d(0)]
    current, longest = _calculate_streaks(dates)
    assert current == 1
    assert longest == 4


def test_duplicate_dates_do_not_inflate_streak():
    dates = [d(1), d(1), d(0), d(0)]
    current, longest = _calculate_streaks(dates)
    assert current == 2
    assert longest == 2
