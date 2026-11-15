with open('spherex_cutouts_raw.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(300, len(lines)):
    print(f"{i+1}: {lines[i].rstrip()[:120]}")
