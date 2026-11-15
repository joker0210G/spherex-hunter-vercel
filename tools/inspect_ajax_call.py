with open("flash3.js", "r", encoding="utf-8") as f:
    code = f.read()

pos = code.find("png-animation")
if pos != -1:
    print(code[pos:pos+1500])
