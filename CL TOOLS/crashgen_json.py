import json

with open("../crashgen.json", "w", encoding="utf-8", errors="ignore") as f:
    crashgen = {
        "OLD": "Buffout 4 v1.28.1",
        "NEW": "Buffout 4 v1.31.1 Feb 28 2023 00:32:02"
    }
    json.dump(crashgen, f, indent=4)