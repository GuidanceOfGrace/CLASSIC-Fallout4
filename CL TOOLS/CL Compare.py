import os, sys, time, random, shutil, logging, fnmatch, pathlib
folder_name = os.path.basename(os.getcwd())

#READ 4TH LINE FROM EACH .log AND GRAB LAST 7 CHARS
print("Hello World! | Crash Logs Compare | Fallout 4")

File_Index = 0
for file in os.listdir("."):
    if fnmatch.fnmatch(file, "crash-*.log"):
        File_Index +=1
        Plugin_Check = open(file, "r+", encoding="utf-8", errors="ignore")
        All_Lines = Plugin_Check.readlines()
        for line in All_Lines:
            if not "F4SE" in line and "PLUGINS" in line:
                Plugin_IDX = All_Lines.index(line)+1
            if "F4SE PLUGINS" in line:
                F4SE_IDX = All_Lines.index(line)+1
        Plugin_Check.close()
        
        #WHEN 1st FILE IS CHECKED, CREATE MASTER LIST
        if File_Index == 1:
            Plugins_Unstripped = All_Lines[Plugin_IDX:]
            F4SEP_Unstripped = All_Lines[F4SE_IDX:Plugin_IDX-1]
            Master_ListP = []
            Master_ListM = []
            for elem in Plugins_Unstripped:
                if "[FE" in elem:
                    Master_ListP.append(elem[9:].strip())
                else:
                    Master_ListP.append(elem[5:].strip())
            for elem in F4SEP_Unstripped:
                if not "Buffout4.dll" in elem:
                    Master_ListM.append(elem.strip())
        #WHEN NOT 1st file, CREATE SEPARATE LIST
        if File_Index > 1:
            Plugins_Unstripped = All_Lines[Plugin_IDX:]
            F4SEP_Unstripped = All_Lines[F4SE_IDX:Plugin_IDX-1]
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
            #INTERSECT ELEMS IN BOTH LISTS, SET RESULT AS MASTER LIST
            Master_ListP = set(Master_ListP).intersection(Plugin_List)
            Master_ListM = set(Master_ListM).intersection(F4SEP_List)

list_remove = ["Fallout4.esm","DLCCoast.esm","DLCNukaWorld.esm","DLCRobot.esm","DLCworkshop01.esm","DLCworkshop02.esm","DLCworkshop03.esm",""]
for elem in list_remove:
    if elem in Master_ListP:
        Master_ListP.remove(elem)
    if elem in Master_ListM:
        Master_ListM.remove(elem)

with open(folder_name+"-RESULT.md", "w") as Master_Output:
    Master_Output.write("LIST OF PLUGINS SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : "+folder_name+"\n")
    for item in sorted(Master_ListP):
        Master_Output.write("%s\n" % item)
    if not Master_ListP:
        Master_Output.write("- SCRIPT FOUND 0 MATCHING PLUGINS")
    Master_Output.write("\nLIST OF F4SE DLLs SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : "+folder_name+"\n")
    for item in sorted(Master_ListM):
        Master_Output.write("%s\n" % item)
    if not Master_ListM:
        Master_Output.write("- SCRIPT FOUND 0 MATCHING F4SE DLLs")

print("COMPARISON COMPLETE! Check the -RESULTS.md output!")
os.system("pause")