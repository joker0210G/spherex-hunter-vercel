with open("flash3.js", "r", encoding="utf-8") as f:
    code = f.read()

for i, line in enumerate(code.splitlines()):
    if "synth_a" in line:
        if any(k in line for k in ["ajax", "data:", "buildUrl", "fromUrl", "prop", "val()"]):
            continue
        print(f"L{i+1}: {line.strip()[:140]}")
