import time

TIMESINCE_CHUNKS: tuple[tuple[str, int, int | None], ...] = (
    ("second", 1, 60),
    ("minute", 60, 60),
    ("hour", 60 * 60, 24),
    ("day", 60 * 60 * 24, 6),
    ("week", 60 * 60 * 24 * 7, 6),
    ("month", 60 * 60 * 24 * 30, 11),
    ("year", 60 * 60 * 24 * 365, None),
)


def format_timesince(timestamp: float) -> str:
    delta: float = time.time() - timestamp
    if delta < 20:
        return "a few seconds ago"
    for label, divider, max_value in TIMESINCE_CHUNKS:
        value: float = round(number=delta / divider)
        if max_value is not None and value <= max_value:
            break
    return f"{value} {label}{'s' if value > 1 else ''} ago"


def format_size(size: int) -> str:
    size_float = float(size)
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(size_float) < 1000.0:
            return f"{size_float:3.1f}{unit}"
        size_float /= 1000.0
    return f"{size_float:.1f}Y"
