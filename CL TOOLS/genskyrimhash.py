import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate a hash of the Skyrim executable")
parser.add_argument("-v", "--version", type=str, dest="version", help="Version of Skyrim to generate a hash for. Default is 1.6.640", default="1.6.640")
parser.add_argument("-o", "--oldrim", dest="oldrim", action="store_true", help="Generate a hash for Oldrim instead of Skyrim Special Edition.")
parser.add_argument("path", type=str, help="Path to the Skyrim installation folder.")
args = parser.parse_args()

SEPATH = Path(args.path).joinpath("SkyrimSE.exe")
OLDRIMPATH = Path(args.path).joinpath("Skyrim.exe")

if args.oldrim and OLDRIMPATH.exists():
    SKYRIMEXE = OLDRIMPATH
elif not args.oldrim and SEPATH.exists():
    SKYRIMEXE = SEPATH
else:
    print("Could not find Skyrim executable. Please specify the path to the Skyrim installation folder.")
    input("Press enter to exit.")
    exit(1)

SKYRIMHash = hashlib.sha512(SKYRIMEXE.read_bytes()).hexdigest()

print("Skyrim hash: " + SKYRIMHash)
Path.cwd().joinpath(f"skyrim-{args.version}_hash.txt").write_text(SKYRIMHash)