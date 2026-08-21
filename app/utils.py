from calendar import monthrange
from datetime import datetime, timedelta, timezone


def as_utc(moment: datetime) -> datetime:
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def next_occurrence(moment: datetime, recurrence: str) -> datetime:
    if recurrence == "daily":
        return moment + timedelta(days=1)
    if recurrence == "weekly":
        return moment + timedelta(weeks=1)
    if recurrence == "monthly":
        month = 1 if moment.month == 12 else moment.month + 1
        year = moment.year + 1 if moment.month == 12 else moment.year
        return moment.replace(year=year, month=month, day=min(moment.day, monthrange(year, month)[1]))
    raise ValueError(f"Unsupported recurrence: {recurrence}")
