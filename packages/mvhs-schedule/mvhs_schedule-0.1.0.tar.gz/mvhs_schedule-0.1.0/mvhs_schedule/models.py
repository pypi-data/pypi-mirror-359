from datetime import datetime


class Period:
    def __init__(self, start: datetime, end: datetime, period: str):
        self.start = start
        self.end = end
        self.period = period

    def __repr__(self) -> str:
        return f"Period(start={self.start}, end={self.end}, period='{self.period}')"

    def __eq__(self, other):
        if not isinstance(other, Period):
            return False
        return (
            self.start == other.start
            and self.end == other.end
            and self.period == other.period
        )
