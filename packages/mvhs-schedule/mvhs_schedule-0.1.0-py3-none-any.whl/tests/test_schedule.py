import pytest
from datetime import date, datetime


from unittest.mock import AsyncMock, patch
from mvhs_schedule import (
    get_schedule_from_day,
    get_periods_from_schedule,
    get_periods_on_day,
    get_periods_from_day_count,
    time_of_period,
)
from mvhs_schedule.models import Period

pytest_plugins = ["pytest_asyncio"]


@pytest.mark.asyncio
@patch("mvhs_schedule.schedule.FirebaseFetcher")
async def test_get_schedule_from_day(mock_fetcher):
    mock_fetcher_instance = mock_fetcher.return_value

    def side_effect(arg):
        if arg == "days":
            return {"01012025-01012025": "special-schedule"}
        elif arg == "weekday-map":
            return ["none", "regular", "none", "none", "none", "none", "none"]
        return None

    mock_fetcher_instance.get_from_db = AsyncMock(
        side_effect=side_effect)

    # Test special day
    result = await get_schedule_from_day(date(2025, 1, 1))
    assert result == "special-schedule"

    # Test weekday map
    result = await get_schedule_from_day(date(2025, 1, 6))  # Monday
    assert result == "regular"


@pytest.mark.asyncio
@patch("mvhs_schedule.schedule.FirebaseFetcher")
async def test_get_periods_from_schedule(mock_fetcher):
    mock_fetcher_instance = mock_fetcher.return_value
    mock_fetcher_instance.get_from_db = AsyncMock(return_value={
        "0800-0900": "Period 1",
        "0910-1010": "Period 2"
    })

    result = await get_periods_from_schedule("regular")
    assert len(result) == 2
    assert result[0] == Period(
        start=datetime.strptime("0800", "%H%M").time(),
        end=datetime.strptime("0900", "%H%M").time(),
        period="Period 1"
    )


@pytest.mark.asyncio
@patch("mvhs_schedule.schedule.get_schedule_from_day", AsyncMock(return_value="regular"))
@patch("mvhs_schedule.schedule.get_periods_from_schedule", AsyncMock(return_value=[
    Period(
        start=datetime.strptime("0800", "%H%M").time(),
        end=datetime.strptime("0900", "%H%M").time(),
        period="Period 1"
    )
]))
async def test_get_periods_on_day():
    result = await get_periods_on_day(date(2025, 1, 6))
    assert len(result) == 1
    assert result[0].period == "Period 1"


@pytest.mark.asyncio
@patch("mvhs_schedule.schedule.get_periods_on_day", AsyncMock(return_value=[
    Period(
        start=datetime.strptime("0800", "%H%M").time(),
        end=datetime.strptime("0900", "%H%M").time(),
        period="Period 1"
    ),
    Period(
        start=datetime.strptime("0910", "%H%M").time(),
        end=datetime.strptime("1010", "%H%M").time(),
        period="Period 2"
    )
]))
async def test_get_periods_from_day_count():
    result = await get_periods_from_day_count(date(2025, 1, 6), 2)
    assert len(result) == 2


@pytest.mark.asyncio
@patch("mvhs_schedule.schedule.get_periods_on_day", AsyncMock(return_value=[
    Period(
        start=datetime.strptime("0800", "%H%M").time(),
        end=datetime.strptime("0900", "%H%M").time(),
        period="Period 1"
    )
]))
async def test_time_of_period():
    start, end = await time_of_period(date(2025, 1, 6), "Period 1")
    assert start == datetime(2025, 1, 6, 8, 0)
    assert end == datetime(2025, 1, 6, 9, 0)
