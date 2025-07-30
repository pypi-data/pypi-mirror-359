# hanifx/test.py

from hanifx.utils.parser import parse_color, get_color_codes_in_languages

def color(code: str, lang: str = "auto") -> None:
    color_data = parse_color(code, lang)
    if not color_data:
        print(f"[✘] Unsupported or invalid color: {code}")
        return

    hex_code = color_data["hex"]
    rgb = color_data["rgb"]
    name = color_data.get("name", "unknown")
    ctype = color_data.get("type", "N/A")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  HANIFX COLOR TESTER")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Input        : {code}")
    print(f"  Language     : {lang}")
    print(f"  HEX          : {hex_code}")
    print(f"  RGB          : {rgb}")
    print(f"  Name         : {name}")
    print(f"  Type         : {ctype}")
    print(f"  Preview      : \033[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m        \033[0m")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print(f"  Color Codes in Programming Languages:")
    codes = get_color_codes_in_languages(rgb)
    for lang_name, snippet in codes.items():
        print(f"    [{lang_name}]: {snippet}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
