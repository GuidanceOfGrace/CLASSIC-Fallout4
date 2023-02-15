import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate a hash of the Fallout 4 executable")
parser.add_argument("path", help="Path to the Fallout 4 executable")
args = parser.parse_args()

FO4EXE = Path(args.path)
FO4Hash = hashlib.sha512(FO4EXE.read_bytes()).hexdigest()
Path("fo4hash.txt").write_text(FO4Hash)
# print(FO4Hash)