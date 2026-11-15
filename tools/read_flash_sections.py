with open('flash3.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== External links (lines 440-475) ===")
for i in range(439, min(475, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")

print("\n=== v1UrlCompat (lines 535-595) ===")
for i in range(535, min(595, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")

print("\n=== Navigation/v3 open (lines 885-915) ===")
for i in range(885, min(915, len(lines))):
    print(f"L{i+1}: {lines[i].rstrip()}")
