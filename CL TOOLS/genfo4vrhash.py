import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate a hash of the Fallout 4 executable")
parser.add_argument("path", type=str, help="Path to the Fallout 4 installation folder.")
args = parser.parse_args()

FO4EXE = Path(args.path).joinpath("FalloutVR.exe")
FO4Hash = hashlib.sha512(FO4EXE.read_bytes()).hexdigest()
print("Fallout 4 VR hash: " + FO4Hash)
Path.cwd().joinpath("fo4vrhash.txt").write_text(FO4Hash)