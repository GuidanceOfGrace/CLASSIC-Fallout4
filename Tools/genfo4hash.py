import hashlib
from pathlib import Path


FO4EXE = Path("E:/Games/Steam/steamapps/common/Fallout 4/Fallout4.exe")
FO4Hash = hashlib.sha512(FO4EXE.read_bytes()).hexdigest()
Path("fo4hash.txt").write_text(FO4Hash)
# print(FO4Hash)