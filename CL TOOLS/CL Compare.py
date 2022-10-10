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
                Plugin_IDX = All_Lines.index(line)
        Plugin_Check.close()
        
        #WHEN 1st FILE IS CHECKED, CREATE MASTER LIST
        if File_Index == 1:
            Plugins_Unstripped = All_Lines[Plugin_IDX:]
            Master_List = []
            for elem in Plugins_Unstripped:
                if "[FE" in elem:
                    Master_List.append(elem[9:].strip())
                else:
                    Master_List.append(elem[5:].strip())
        #WHEN NOT 1st file, CREATE SEPARATE LIST
        if File_Index > 1:
            Plugins_Unstripped = All_Lines[Plugin_IDX:]
            Plugin_List = []
            for elem in Plugins_Unstripped:
                if "[FE" in elem:
                    Plugin_List.append(elem[9:].strip())
                else:
                    Plugin_List.append(elem[5:].strip())
            #INTERSECT ELEMS IN BOTH LISTS, SET RESULT AS MASTER LIST
            Master_List = set(Master_List).intersection(Plugin_List)

list_remove = ["NS:","PLUGINS:","Fallout4.esm","DLCCoast.esm","DLCNukaWorld.esm","DLCRobot.esm","DLCworkshop01.esm","DLCworkshop02.esm","DLCworkshop03.esm",""]
for elem in list_remove:
    if elem in Master_List:
        Master_List.remove(elem)

with open(folder_name+"-RESULT.md", "w") as Master_Output:
    Master_Output.write("LIST OF PLUGINS SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : "+folder_name+"\n")
    for item in sorted(Master_List):
        Master_Output.write("%s\n" % item)

print("COMPARISON COMPLETE! Check the -RESULTS.md output!")
os.system("pause")