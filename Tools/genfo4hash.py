import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate a hash of the Fallout 4 executable")
parser.add_argument("--print", "-p", action="store_true", help="Print the hash to the console.")
parser.add_argument("path", type=str, help="Path to the Fallout 4 executable")
args = parser.parse_args()

FO4EXE = Path(args.path).joinpath("Fallout4.exe")
FO4Hash = hashlib.sha512(FO4EXE.read_bytes()).hexdigest()
if args.print:
    print(FO4Hash)
else:
    Path.cwd().joinpath("fo4hash.txt").write_text(FO4Hash)