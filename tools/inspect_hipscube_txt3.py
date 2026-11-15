with open('spherex_hipscube_raw.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(260, min(420, len(lines))):
    print(f"{i+1}: {lines[i].rstrip()[:120]}")
