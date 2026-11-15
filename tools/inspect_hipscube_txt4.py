with open('spherex_hipscube_raw.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(420, min(550, len(lines))):
    print(f"{i+1}: {lines[i].rstrip()[:120]}")
