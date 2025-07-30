from datetime import datetime, timedelta

def parse_period(period):
    """Parse a period string and return the corresponding datetime."""
    now = datetime.now()
    
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "this week":
        # Start of current week (Monday)
        days_since_monday = now.weekday()
        start_of_week = now - timedelta(days=days_since_monday)
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "15 days":
        return now - timedelta(days=15)
    elif period == "a month":
        return now - timedelta(days=30)
    elif period == "all":
        return "all"
    else:
        raise ValueError(f"Unknown period: {period}") 