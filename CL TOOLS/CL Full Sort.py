import os
import shutil
from glob import glob

list_SORTFAIL = []
# READ 4TH LINE FROM EACH .log AND GRAB LAST 7 CHARS
print("Hello World! | Crash Logs Sort | Fallout 4")
for file in glob("crash-*.log"):
    with open(file, "r+", encoding="utf-8", errors="ignore") as Error_Check:
        All_Lines = Error_Check.readlines()
    Error_Line = All_Lines[3]
    Error_Num = Error_Line[-8:].strip()

    # SKIP INVALID LOGS & FIND PLUGIN INDEX
    Plugin_IDX = 0
    Check_Valid = 0
    for line in All_Lines:
        if not "F4SE" in line and "PLUGINS:" in line:
            Plugin_IDX = All_Lines.index(line)
        if "[00]" in line:
            Check_Valid = 1
    if not "exception" in Error_Line.lower():
        Check_Valid = 0

    match Check_Valid:
        case 1 if Plugin_IDX and not os.path.exists(Error_Num): # Using if Plugin_IDX instead of if not Plugin_IDX == 0 because 0 evaluates to false anyway.
            os.mkdir(Error_Num)
            shutil.copy(file, Error_Num)
            os.remove(file)
        case 1 if Plugin_IDX:
            shutil.copy(file, Error_Num)
            os.remove(file)
        case 0:
            list_SORTFAIL.append(str(file))

if len(list_SORTFAIL) >= 1:
    print("NOTICE: SCRIPT WAS UNABLE TO PROPERLY SORT THE FOLLOWING LOG(S): ")
    for elem in list_SORTFAIL:
        print(elem)
    print("-----")
    print("(These logs most likely have wrong formatting or don't have a plugin list.)")
    os.system("pause")

print("SORTING COMPLETE! Check the newly created folders!")
os.system("pause")
