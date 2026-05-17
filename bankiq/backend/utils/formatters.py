"""Display-layer formatters — UTC to IST conversion for API responses."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def utc_to_ist(dt: datetime | None) -> str | None:
    """
    Convert a UTC datetime to IST ISO string for display.

    Parameters:
        dt: Timezone-aware or naive UTC datetime.

    Returns:
        ISO-formatted IST string, or None if dt is None.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST).isoformat()
