with open('spherex_mosaic_raw.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i in range(min(120, len(lines))):
    print(f"{i+1}: {lines[i].rstrip()[:120]}")
