# from datetime import datetime, timedelta
# from dateutil import parser


# def parse_relative_date(date_text: str) -> datetime:
#     date_text = date_text.strip().lower()

#     now = datetime.now()

#     if 'hour ago' in date_text or 'hours ago' in date_text:
#         hours = int(date_text.split()[0])
#         return now - timedelta(hours=hours)

#     elif 'minute ago' in date_text or 'minutes ago' in date_text:
#         minutes = int(date_text.split()[0])
#         return now - timedelta(minutes=minutes)

#     elif 'yesterday' in date_text:
#         return now - timedelta(days=1)

#     else:

#         return parser.parse(date_text)
    

from datetime import datetime, timedelta
from dateutil import parser
import re

def parse_relative_date(date_text: str) -> datetime:
    date_text = date_text.strip().lower()
    now = datetime.now()

    # "just now"
    if "just now" in date_text:
        return now

    # "an hour ago" or "a minute ago"
    if re.match(r"an? hour ago", date_text):
        return now - timedelta(hours=1)
    if re.match(r"an? minute ago", date_text):
        return now - timedelta(minutes=1)

    # Hours ago
    match = re.match(r"(\d+)\s*hours? ago", date_text)
    if match:
        return now - timedelta(hours=int(match.group(1)))

    # Minutes ago
    match = re.match(r"(\d+)\s*minutes? ago", date_text)
    if match:
        return now - timedelta(minutes=int(match.group(1)))

    # Days ago
    match = re.match(r"(\d+)\s*days? ago", date_text)
    if match:
        return now - timedelta(days=int(match.group(1)))

    # Weeks ago
    match = re.match(r"(\d+)\s*weeks? ago", date_text)
    if match:
        return now - timedelta(weeks=int(match.group(1)))

    # Yesterday
    if "yesterday" in date_text:
        return now - timedelta(days=1)

    # Today
    if date_text == "today":
        return now

    try:
        return parser.parse(date_text, fuzzy=True)
    except:
        return None

