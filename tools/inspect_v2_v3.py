
with open('flash3.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("File length:", len(text))

keywords = ['compat', 'legacy', 'simbad', 'vizier', 'panstarrs', 'ps1', 'legacysurvey', 'zooniverse', 'v1', 'v2', 'v3', 'version', 'external', 'link']
matches = []
for i, line in enumerate(text.splitlines()):
    if any(k in line.lower() for k in keywords):
        matches.append((i+1, line.strip()))

print(f"Total matching lines: {len(matches)}")
for lineno, line in matches[:40]:
    print(f"L{lineno}: {line[:140]}")
