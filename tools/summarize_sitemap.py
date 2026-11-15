import json

with open('spherex_sitemap.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for url, info in data.items():
    title = info.get('title', 'Unknown')
    internal = info.get('internal', [])
    external = info.get('external', [])
    print(f"PAGE: {title} | {url}")
    print(f"  Internal Links: {len(internal)}, External: {len(external)}")
    # Print distinct child links
    sub_urls = set(x['url'] for x in internal if 'spherex' in x['url'].lower() or 'splices' in x['url'].lower())
    for s in sorted(sub_urls):
        print(f"    -> {s}")
