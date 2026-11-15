import re

with open('frontend/index.html', encoding='utf-8') as f:
    text = f.read()

all_ids = re.findall(r'id=["\']([a-zA-Z0-9_-]+)["\']', text)
counts = {}
for i in all_ids:
    counts[i] = counts.get(i, 0) + 1

dups = {k: v for k, v in counts.items() if v > 1}
print(f"Total duplicates: {len(dups)}")
for k, v in dups.items():
    print(f"Duplicate {k}: {v} occurrences")
