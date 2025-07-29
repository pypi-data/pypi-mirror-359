from datetime import date, datetime, timedelta

from .db import FirebaseFetcher
from .models import Period


async def get_schedule_from_day(day: date) -> str:
    """
    Fetches the schedule for a specific day.

    :param day: The date for which to fetch the schedule.
    :return: A list of Period objects for the given day.
    """
    fetcher = FirebaseFetcher()

    special_days = await fetcher.get_from_db("days")

    for key in special_days:
        start, end = key.split("-")
        start_date = datetime.strptime(start, "%m%d%Y").date()
        end_date = datetime.strptime(end, "%m%d%Y").date()

        if start_date <= day <= end_date:
            return special_days[key]

    weekday_map = await fetcher.get_from_db("weekday-map")
    schedule = weekday_map[int(day.strftime("%w"))]

    return schedule


async def get_periods_from_schedule(schedule: str) -> list[Period]:
    """
    Fetches periods from a given schedule string.

    :param schedule: The schedule string containing period information.
    :return: A list of Period objects parsed from the schedule string.
    """
    fetcher = FirebaseFetcher()
    periods = await fetcher.get_from_db(f"schedules/{schedule}")

    res = []

    for key in periods:
        start, end = key.split("-")
        start_time = datetime.strptime(start, "%H%M").time()
        end_time = datetime.strptime(end, "%H%M").time()
        period_name = periods[key]
        res.append(Period(start=start_time, end=end_time, period=period_name))

    return res


async def get_periods_on_day(day: date) -> list[Period]:
    """
    Fetches periods for a specific day.

    :param day: The date for which to fetch periods.
    :return: A list of Period objects for the given day.
    """
    schedule = await get_schedule_from_day(day)

    if schedule == "none":
        return []

    return await get_periods_from_schedule(schedule)


async def get_periods_from_day_count(day: date, day_count: int) -> list[Period]:
    """
    Fetches periods for a range of days starting from a specific day.

    :param day: The starting date for the range.
    :param day_count: The number of days to fetch periods for.
    :return: A list of Period objects for the specified range of days.
    """
    periods = []
    for i in range(day_count):
        new_day = day + timedelta(days=i)
        periods.append(await get_periods_on_day(new_day))
    return periods


async def time_of_period(day: date, period: str) -> tuple[datetime, datetime]:
    """
    Fetches the start and end times of a specific period on a given day.

    :param day: The date for which to fetch the period times.
    :param period: The name of the period to fetch.
    :return: A tuple containing the start and end times of the period.
    """
    periods = await get_periods_on_day(day)

    for p in periods:
        if p.period == period:
            return datetime.combine(day, p.start), datetime.combine(day, p.end)

    return None, None
