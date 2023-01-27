import argparse
import os
from glob import glob
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("error_code", type=str, help="Specify the error code you want to run log comparisons for.", nargs="?", default=str(Path.cwd()))
args = parser.parse_args()

folder_name = Path(args.error_code).resolve().name
scanpath = str(Path(args.error_code).resolve())
# READ 4TH LINE FROM EACH .log AND GRAB LAST 7 CHARS
print("Hello World! | Crash Logs Compare | Fallout 4")

File_Index = 0
# Declaring the Master Lists here to appease VSCode's type checker/linter
Master_ListP = []
Master_ListM = []
for file in glob(f"{scanpath}/crash-*.log"):
    File_Index += 1
    Plugin_IDX: int = int()
    F4SE_IDX: int = int()
    with open(file, "r+", encoding="utf-8", errors="ignore") as Plugin_Check:
        All_Lines = Plugin_Check.readlines()
    for line in All_Lines:
        if not "F4SE" in line and "PLUGINS" in line:
            Plugin_IDX = All_Lines.index(line) + 1
        if "F4SE PLUGINS" in line:
            F4SE_IDX = All_Lines.index(line) + 1

    if File_Index == 1:
        Plugins_Unstripped = All_Lines[Plugin_IDX:]
        F4SEP_Unstripped = All_Lines[F4SE_IDX:Plugin_IDX - 1]

        for elem in Plugins_Unstripped:
            if "[FE" in elem:
                Master_ListP.append(elem[9:].strip())  # type: ignore
            else:
                Master_ListP.append(elem[5:].strip())  # type: ignore
        for elem in F4SEP_Unstripped:
            if not "Buffout4.dll" in elem:
                Master_ListM.append(elem.strip())  # type: ignore
    # WHEN NOT 1st file, CREATE SEPARATE LIST
    if File_Index > 1:
        Plugins_Unstripped = All_Lines[Plugin_IDX:]
        F4SEP_Unstripped = All_Lines[F4SE_IDX:Plugin_IDX - 1]
        Plugin_List = []
        F4SEP_List = []
        for elem in Plugins_Unstripped:
            if "[FE" in elem:
                Plugin_List.append(elem[9:].strip())
            else:
                Plugin_List.append(elem[5:].strip())
        for elem in F4SEP_Unstripped:
            if not "Buffout4.dll" in elem:
                F4SEP_List.append(elem.strip())
                print(elem.strip())
        # INTERSECT ELEMS IN BOTH LISTS, SET RESULT AS MASTER LIST
        Master_ListP = set(Master_ListP).intersection(Plugin_List)
        Master_ListM = set(Master_ListM).intersection(F4SEP_List)

list_remove = ["Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm", ""]
for elem in list_remove:
    if elem in Master_ListP:
        Master_ListP.remove(elem)
    if elem in Master_ListM:
        Master_ListM.remove(elem)

with open(f"{scanpath}/{folder_name}-RESULT.md", "w") as Master_Output:
    Master_Output.write(f"LIST OF PLUGINS SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : {folder_name}\n")
    for item in sorted(Master_ListP):
        Master_Output.write(f"{item}\n")
    if not Master_ListP:
        Master_Output.write("- SCRIPT FOUND 0 MATCHING PLUGINS")
    Master_Output.write(f"\nLIST OF F4SE DLLs SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : {folder_name}\n")
    for item in sorted(Master_ListM):
        Master_Output.write(f"{item}\n")
    if not Master_ListM:
        Master_Output.write("- SCRIPT FOUND 0 MATCHING F4SE DLLs")

print("COMPARISON COMPLETE! Check the -RESULTS.md output!")
os.system("pause")
