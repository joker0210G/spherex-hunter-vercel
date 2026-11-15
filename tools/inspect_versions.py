with open('flash3.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re

matches = re.findall(r'.{0,50}(?:coadd_mode|v1UrlCompat|wiseview-v2|wiseview-v3).{0,50}', text)
for m in set(matches):
    print(m.strip())
