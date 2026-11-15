with open('spherex_cutouts_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines[:60]):
    print(f"{i+1}: {line[:120]}")
