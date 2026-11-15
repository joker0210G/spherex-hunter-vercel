with open('flash3.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(410, 445):
    print(f"L{i+1}: {lines[i].rstrip()}")
