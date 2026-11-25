import datetime as dt
import math
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

URL = 'https://www.openstreetmap.org/user/Kaya%20Shiranui/heatmap'

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.maximum = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-max-per-day' in a:
            self.maximum = int(a['data-max-per-day'])
        if 'data-date' in a:
            day = dt.date.fromisoformat(a['data-date'])
            if day in self.days:
                raise ValueError('Duplicate date in OSM response')
            self.days[day] = int(a.get('data-count', 0))

def main():
    request = urllib.request.Request(URL, headers={'User-Agent': 'pwu2775-dev-profile-calendar/1.0 (GitHub profile)'})
    with urllib.request.urlopen(request, timeout=30) as response:
        source = response.read().decode('utf-8')
    cal = Calendar()
    cal.feed(source)
    today = dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=364)
    dates = [start + dt.timedelta(days=n) for n in range(365)]
    if cal.maximum is None or not all(day in cal.days for day in dates):
        raise ValueError('OSM calendar is missing or incomplete; keeping previous image')
    total = sum(cal.days[day] for day in dates)
    first = start - dt.timedelta(days=(start.weekday() + 1) % 7)
    colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" viewBox="0 0 900 180" role="img" aria-label="OpenStreetMap contribution calendar">', '<rect width="900" height="180" rx="10" fill="#ffffff"/>', f'<text x="20" y="29" fill="#1f2328" font-family="Arial,sans-serif" font-size="17">{total:,} OpenStreetMap contributions in the last year</text>']
    last_month = None
    for day in dates:
        count = cal.days[day]
        col = (day - first).days // 7
        row = (day.weekday() + 1) % 7
        x, y = 42 + col * 16, 64 + row * 15
        if day.month != last_month:
            parts.append(f'<text x="{x}" y="54" fill="#59636e" font-family="Arial,sans-serif" font-size="10">{day:%b}</text>')
            last_month = day.month
        level = min(4, max(1, math.ceil(math.sqrt(count / cal.maximum) * 4))) if count and cal.maximum else 0
        parts.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{colors[level]}"><title>{day}: {count} contributions</title></rect>')
    for row, label in ((1, 'Mon'), (3, 'Wed'), (5, 'Fri')):
        parts.append(f'<text x="10" y="{73 + row * 15}" fill="#59636e" font-family="Arial,sans-serif" font-size="10">{label}</text>')
    parts.append('<text x="20" y="165" fill="#59636e" font-family="Arial,sans-serif" font-size="10">Source: openstreetmap.org • Updated daily</text></svg>')
    Path('osm-contributions.svg').write_text('\n'.join(parts) + '\n', encoding='utf-8')
    print(f'Generated {len(dates)} days; {total} contributions; maximum {cal.maximum}')

if __name__ == '__main__':
    main()
