import os, sys, stat, time, random, shutil, logging, fnmatch, pathlib, platform, subprocess, configparser, ctypes.wintypes

if not os.path.exists("Scan Crashlogs.ini"): # INI FILE FOR AUTO-SCANNER
    INI_Settings = ["[MAIN]\n",
    "# This file contains available configuration settings for both Scan Crashlogs.py and Scan Crashlogs.exe \n",
    "# Set to true if you want Auto-Scanner to check Python version and if all required packages are installed. \n",
    "Update Check = true\n\n",
    "# Set to true if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly. \n",
    "# FCX - File Check eXtended | If Auto-Scanner fails to scan your logs, revert this setting back to false. \n",
    "FCX Mode = true\n\n",
    "# Set to true if you want Auto-Scanner to show extra stats about scanned logs in the command line window. \n",
    "Stat Logging = false\n\n",
    "# Set to true if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder. \n",
    "# Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages. \n",
    "Move Unsolved = false\n\n",
    "# Set or copy/paste your INI directory path below. Example: INI Path = C:/Users/Zen/Documents/My Games/Fallout4 \n",
    "# Only required if Profile Specific INIs are enabled in MO2 or you moved your Documents folder somewhere else. \n",
    "# I highly recommend that you disable Profile Specific Game INI Files in MO2, located in Tools > Profiles... \n",
    "INI Path = "]
    with open("Scan Crashlogs.ini", "w+") as INI_Autoscan:
        INI_Autoscan.write("".join(INI_Settings))

# Use optionxform = str to preserve INI formatting. | Set comment_prefixes to unused char to keep INI comments. 
CLAS_config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="$")
CLAS_config.optionxform = str
CLAS_config.read("Scan Crashlogs.ini")
Python_Current = sys.version[:6]
CLAS_Date = 271022 #DDMMYY
CLAS_Current = "CLAS v5.66"
CLAS_Update = False

if CLAS_config.get("MAIN","Update Check").lower() == "true":
    print("CHECKING FOR PACKAGE & CRASH LOG AUTO-SCANNER UPDATES...")
    print("(You can disable this check in Scan Crashlogs.ini) \n")
    print(f"Installed Python Version: {Python_Current} \n")
    if not Python_Current[:4] in ["3.11","3.10","3.9","3.8"]:
        print("CAUTION: YOUR PYTHON VERSION IS OUT OF DATE! PLEASE UPDATE PYTHON.")
        print("FOR LINUX / WIN 10 / WIN 11: https://www.python.org/downloads")
        print("FOR WINDOWS 7: https://github.com/adang1345/PythonWin7")

    try: # > AUTO UPDATE PIP, INSTALL & LIST PACKAGES
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'requests'])
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        # installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        # print("List of all installed packages:", installed_packages) | RESERVED
        # print("===============================================================================")
        import requests
        response = requests.get("https://api.github.com/repos/GuidanceOfGrace/Buffout4-CLAS/releases/latest")
        CLAS_Received = response.json()["name"]
        if CLAS_Received == CLAS_Current:
            print("You have the latest version of the Auto-Scanner!")
            print("===============================================================================")
        else:
            print("\n [!] YOUR AUTO-SCANNER VERSION IS OUT OF DATE \n Please download the latest version from here: \n https://www.nexusmods.com/fallout4/mods/56255 \n")
            print("===============================================================================")
            CLAS_Update = True
    except Exception:
        pass
        print("AN ERROR OCCURRED! THE SCRIPT WAS UNABLE TO CHECK FOR UPDATES, BUT WILL CONTINUE SCANNING.")
        print("CHECK FOR ANY AUTO-SCANNER UPDATES HERE: https://www.nexusmods.com/fallout4/mods/56255")
        print("MAKE SURE YOU HAVE THE LATEST VERSION OF PYTHON 3: https://www.python.org/downloads")
        print("===============================================================================")

Sneaky_Tips = ["\nRandom Hint: [Ctrl] + [F] is a handy-dandy key combination. You should use it more often. Please.\n",
               "\nRandom Hint: Patrolling the Buffout 4 Nexus Page almost makes you wish this joke was more overused.\n",
               "\nRandom Hint: You have a crash log where Autoscanner couldn't find anything? Feel free to send it to me.\n",
               "\nRandom Hint: 20% of all crashes are caused by Classic Holstered Weapons mod. 80% of all statistics are made up.\n",
               "\nRandom Hint: No, I don't know why your game froze instead of crashed. But I know someone who might know; Google.\n",
               "\nRandom Hint: When necessary, make sure that crashes are consistent or repeatable, since in rare cases they aren't.\n",
               "\nRandom Hint: When posting crash logs, it's helpful to mention the last thing you were doing before the crash happened.\n",
               "\nRandom Hint: Be sure to revisit both Buffout 4 Crash Crticle and Auto-Scanner Nexus Page from time to time for updates.\n"]

# =================== STATISTICS LOGGING ===================
# MAIN STATS
statL_scanned = statL_incomplete = statL_failed = statL_veryold = 0
# KNOWN CRASH MESSAGES
statC_ActiveEffect = statC_AnimationPhysics = statC_Audio = statC_BA2Limit = statC_BGSM = statC_BitDefender = statC_BodyPhysics = statC_ConsoleCommands = statC_CorruptedTex = 0
statC_DLL = statC_Equip = statC_Generic = statC_GridScrap = statC_Invalidation = statC_LoadOrder = statC_MCM = statC_BadMath = statC_NIF = statC_NPCPathing = statC_NVDebris = 0
statC_NVDriver = statC_Null = statC_Overflow = statC_Papyrus = statC_Particles = statC_PluginLimit = statC_Rendering = statC_Texture = statC_CorruptedAudio = statC_LOD = 0
statC_Decal = statC_MO2Unp = statC_VulkanMem = statC_VulkanSet = statC_Water = 0
# UNSOLVED CRASH MESSAGES
statU_Precomb = statU_Player = statU_Save = statU_HUDAmmo = statU_Patrol = statU_Projectile = statU_Item = statU_Input = statU_INI = statU_CClub = 0
# KNOWN CRASH CONDITIONS
statM_CHW = 0

print("Hello World! | Crash Log Auto-Scanner | Version",CLAS_Current[-4:],"| Fallout 4")
print("CRASH LOGS MUST BE .log AND IN THE SAME FOLDER WITH THIS SCRIPT!")
print("===============================================================================")
print("You should place this script into your Documents\My Games\Fallout4\F4SE folder.")
print("(This is where Buffout 4 crash log files are generated after the game crashes.)")
print("===============================================================================")
print("CAUTION: Crash Log Auto-Scanner will not work correctly on Windows 7 systems.")
print("For Win 7, install this Py version: https://github.com/adang1345/PythonWin7")
print("Click on the green Code button and Download Zip, then extract and install.")
print("===============================================================================")
from pathlib import Path
FO4_STEAM_ID = 377160

Loc_Found = False
if platform.system() == "Windows":
    # Using shell32.dll to look up Documents directory path. Thanks, StackOverflow!
    # Unsure os.path.expanduser('~/Documents') works if default path was changed.
    CSIDL_PERSONAL = 5       # (My) Documents 
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value.
    User_Documents = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, User_Documents)
    Doc_Path = User_Documents.value
    FO4_Custom_Path = Path(Doc_Path + r"\My Games\Fallout4\Fallout4Custom.ini")
    FO4_F4SE_Path = Path(Doc_Path + r"\My Games\Fallout4\F4SE\f4se.log")
    FO4_F4SE_Logs = Doc_Path + r"\My Games\Fallout4\F4SE"
    Loc_Found = True
else: # Find where FO4 is installed via Steam if Linux
    home_directory = str(Path.home())
    if os.path.isfile(home_directory + r"/.local/share/Steam/steamapps/libraryfolders.vdf"):
        steam_library = None
        library_path=None
        with open(home_directory + r"/.local/share/Steam/steamapps/libraryfolders.vdf") as steam_library_raw:
            steam_library=steam_library_raw.readlines()
        for line in steam_library:
            if "path" in line:
                library_path=line.split('"')[3]
            if str(FO4_STEAM_ID) in line:
                library_path = rf"{library_path}/steamapps"
                settings_path = rf"{library_path}/compatdata/{FO4_STEAM_ID}/pfx/drive_c/users/steamuser/My Documents/My Games/Fallout4"
                if os.path.exists(rf"{library_path}/common/Fallout 4") and os.path.exists(settings_path):
                    FO4_Custom_Path = Path(rf"{settings_path}/Fallout4Custom.ini")
                    FO4_F4SE_Path = Path(rf"{settings_path}/F4SE/f4se.log")
                    FO4_F4SE_Logs = rf"{settings_path}/F4SE"
                    Loc_Found = True
                    break

# Prompt manual input if ~\Documents\My Games\Fallout4 cannot be found.
if not Loc_Found:
    if "fallout4" in CLAS_config.get("MAIN","INI Path").lower():
        INI_Line = CLAS_config.get("MAIN","INI Path").strip()
        FO4_F4SE_Logs = INI_Line + r"\F4SE"
        FO4_F4SE_Path = Path(INI_Line + r"\F4SE\f4se.log")
        FO4_Custom_Path = Path(INI_Line + r"\Fallout4Custom.ini")
    else:
        print("> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR Fallout4.ini IS LOCATED < <" )
        Path_Input = input("(EXAMPLE: C:/Users/Zen/Documents/My Games/Fallout4 | Press ENTER to confirm.)\n> ")
        print("You entered :",Path_Input,"| This path will be automatically added to Scan Crashlogs.ini")
        FO4_F4SE_Logs = Path_Input.strip() + r"\F4SE"
        FO4_F4SE_Path = Path(Path_Input.strip() + r"\F4SE\f4se.log")
        FO4_Custom_Path = Path(Path_Input.strip() + r"\Fallout4Custom.ini")
        CLAS_config.set("MAIN","INI Path",Path_Input)
        with open("Scan Crashlogs.ini", "w+") as INI_Autoscan:
            CLAS_config.write(INI_Autoscan)

# Create/Open Fallout4Custom.ini and check Archive Invalidaton & other settings.
if CLAS_config.get("MAIN","FCX Mode").lower() == "true":
    if FO4_Custom_Path.is_file():
        os.chmod(FO4_Custom_Path, stat.S_IWRITE)
        F4C_config = configparser.ConfigParser()
        F4C_config.optionxform = str
        F4C_config.read(FO4_Custom_Path)
        if "Archive" not in F4C_config.sections():
            F4C_config.add_section("Archive")

        if F4C_config.get("Archive","bInvalidateOlderFiles") == 0:
            F4C_config.set("Archive","bInvalidateOlderFiles","1")

        if F4C_config.get("Archive","sResourceDataDirsFinal"):
            F4C_config.set("Archive","sResourceDataDirsFinal","")

        with open(FO4_Custom_Path, "w+") as FO4_Custom:
           F4C_config.write(FO4_Custom,space_around_delimiters=False)
    else:
        with open(FO4_Custom_Path, "w+") as FO4_Custom:
            F4C_config = "[Archive]\nbInvalidateOlderFiles=1\nsResourceDataDirsFinal="
        with open(FO4_Custom_Path, "w+") as FO4_Custom:
            FO4_Custom.write(F4C_config)

# Check if f4se.log exists and find game path inside.
if FO4_F4SE_Path.is_file():
    with open(FO4_F4SE_Path, "r") as LOG_Check:
        Path_Check = LOG_Check.readlines()
        for line in Path_Check:
            if "plugin directory" in line:
                line = line[19:].replace("\Data\F4SE\Plugins","")
                Game_Path = line.replace("\n","")
else:
    print("\n CAUTION: AUTO-SCANNER CANNOT FIND THE REQUIRED F4SE.LOG FILE!")
    print("MAKE SURE THAT FALLOUT 4 SCRIPT EXTENDER IS CORRECTLY INSTALLED!")
    print("Link: https://f4se.silverlock.org")
    os.system("pause")

# FILES TO LOOK FOR IN GAME FOLDER ONLY (NEEDS r BECAUSE UNICODE ERROR)
Steam_INI = Path(Game_Path + r"\steam_api.ini")
Preloader_DLL = Path(Game_Path + r"\IpHlpAPI.dll")
Preloader_XML = Path(Game_Path + r"\xSE PluginPreloader.xml")
F4SE_Loader = Path(Game_Path + r"\f4se_loader.exe")
F4SE_DLL = Path(Game_Path + r"\f4se_1_10_163.dll")
F4SE_SDLL = Path(Game_Path + r"\f4se_steam_loader.dll")
Buffout_DLL = Path(Game_Path + r"\Data\F4SE\Plugins\Buffout4.dll")
Buffout_INI = Path(Game_Path + r"\Data\F4SE\Plugins\Buffout4.ini")
Buffout_TOML = Path(Game_Path + r"\Data\F4SE\Plugins\Buffout4.toml")
Address_Library = Path(Game_Path + r"\Data\F4SE\Plugins\version-1-10-163-0.bin")

if Buffout_TOML.is_file(): # RENAME BECAUSE PYTHON CAN'T WRITE TO TOML
    try:
        os.chmod(Buffout_TOML, stat.S_IWRITE)
        os.rename(Buffout_TOML, Buffout_INI)
    except FileExistsError:
        os.remove(Buffout_INI)
        os.chmod(Buffout_TOML, stat.S_IWRITE)
        os.rename(Buffout_TOML, Buffout_INI)

# CAN'T USE CONFIGPARSER BECAUSE DUPLICATE COMMENT IN Buffout_INI
# To preserve original toml formatting, just stick to replace.
# ===========================================================

print("\n PERFORMING SCAN... \n")
start_time = time.time()
orig_stdout = sys.stdout

for file in os.listdir("."):
    if fnmatch.fnmatch(file, "crash-*.log"): # or fnmatch.fnmatch(file, "crash-*.txt") | RESERVED
        logname = str(file)[:len(str(file))-4]
        sys.stdout = open(logname + "-AUTOSCAN.md", "w", encoding='utf-8-sig', errors="ignore")
        crashlog = str(logname + str(".log"))
        if Steam_INI.is_file():
            print(logname + ".log \U0001F480")
        else:
            print(logname + ".log")
        print("This crash log was automatically scanned.")
        print("VER",CLAS_Current[-4:],"| MIGHT CONTAIN FALSE POSITIVES.")
        if CLAS_Update == True:
            print("# NOTICE: YOU NEED TO UPDATE THE AUTO-SCANNER! #")
        print("====================================================")

        # OPEN FILE TO CHECK LINE INDEXES AND EVERYTHING ELSE
        crash_version = open(crashlog, "r", errors="ignore")
        # DEFINE LINE INDEXES FOR EVERYTHING REQUIRED HERE
        all_lines = crash_version.readlines()
        buff_ver = str(all_lines[1].strip())
        buff_error = str(all_lines[3].strip())
        for line in all_lines:
            if not "F4SE" in line and "PLUGINS" in line:
                plugin_idx = all_lines.index(line)
        plugin_list = all_lines[plugin_idx:]
        if os.path.exists("loadorder.txt"):
            plugin_list = []
            with open("loadorder.txt", "r", errors="ignore") as loadorder_check:
                plugin_format = loadorder_check.readlines()
                for line in plugin_format:
                    line = "[LO] " + line.strip()
                    plugin_list.append(line)

        # BUFFOUT VERSION CHECK
        buff_latest = str("Buffout 4 v1.26.2")
        print("Main Error:", buff_error)
        print("====================================================")
        print("Detected Buffout Version:", buff_ver.strip())
        print("Latest Buffout Version:", buff_latest.strip())

        if buff_ver.casefold() == buff_latest.casefold():
            print("You have the lastest version of Buffout 4!")
        else:
            print("REPORTED BUFFOUT VERSION DOES NOT MATCH THE BUFFOUT VERSION USED BY AUTOSCAN")
            print("UPDATE BUFFOUT 4 IF NECESSARY: https://www.nexusmods.com/fallout4/mods/47359")

        if str("v1.") not in buff_ver:
            statL_veryold +=1
            statL_scanned -=1

        # CLOSE CURRENT FILE & OPEN FILE AGAIN FOR ANOTHER CHECK
        crash_version.close()
        crash_log = open(crashlog, "r", errors="ignore")
        crash_message = crash_log.read()

        # ===========================================================

        print("====================================================")
        print("CHECKING IF BUFFOUT 4 FILES/SETTINGS ARE CORRECT...")
        print("====================================================")

        count_Survival_Mod = crash_message.count("UnlimitedSurvivalMode.dll")
        count_buff_Achieve = crash_message.count("Achievements: true")
        count_Achieve_Mod = crash_message.count("achievements.dll")
        count_buff_Memory = crash_message.count("MemoryManager: true")
        count_Memory_Mod = crash_message.count("BakaScrapHeap.dll")
        count_buff_F4EE = crash_message.count("F4EE: false")
        count_F4EE_Mod = crash_message.count("f4ee.dll")

        # CHECK IF F4SE.LOG EXISTS AND REPORTS ANY ERRORS

        if CLAS_config.get("MAIN","FCX Mode").lower() == "true":
            print("* NOTICE: FCX MODE IS ENABLED. AUTO-SCANNER MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *")
            print("[ To disable game folder / mod files detection, set FCX Mode = false in Scan Crashlogs.ini ]")
            print("-----")
            Error_List = []
            F4SE_Error = F4SE_Version = F4SE_Buffout = 0
            with open(FO4_F4SE_Path, "r") as LOG_Check:
                Error_Check = LOG_Check.readlines()
                for line in Error_Check:
                    if "0.6.23" in line:
                        F4SE_Version = 1
                    if "Error" in line:
                        F4SE_Error = 1
                        Error_List.append(line)
                    if "Buffout4.dll" in line and "loaded correctly" in line:
                        F4SE_Buffout = 1

            if F4SE_Version == 1:
                print("You have the latest version of Fallout 4 Script Extender (F4SE). \n-----")
            else:
                print("# REPORTED F4SE VERSION DOES NOT MATCH THE F4SE VERSION USED BY AUTOSCAN #")
                print("UPDATE FALLOUT 4 SCRIPT EXTENDER IF NECESSARY: https://f4se.silverlock.org")
                print("-----")

            if F4SE_Error == 1:
                print("# SCRIPT EXTENDER REPORTS THAT THE FOLLOWING PLUGINS FAILED TO LOAD! #")
                for elem in Error_List:
                    print(elem + "\n-----")
            else:
                print("Script Extender reports that all DLL mod plugins have loaded correctly. \n-----")

            if F4SE_Buffout == 1:
                print("Script Extender reports that Buffout 4.dll was found and loaded correctly. \n-----")
            else:
                print("# SCRIPT EXTENDER REPORTS THAT BUFFOUT 4.DLL FAILED TO LOAD OR IS MISSING! #")
                print("Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115")
                print("Buffout 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359")
                print("-----")

            list_ERRORLOG = []
            for file in FO4_F4SE_Logs:
                if fnmatch.fnmatch(file, ".log"):
                    with open(file, "r+") as LOG_Check:
                        Log_Errors = LOG_Check.read()
                        if "error" in Log_Errors.lower():
                            logname = str(file)
                            if not logname == "f4se.log":
                                list_ERRORLOG.append(logname)

            if len(list_ERRORLOG) >= 1:
                print("# CAUTION: THE FOLLOWING DLL LOGS ALSO REPORT ONE OR MORE ERRORS : #")
                print("[These are located in your Documents\My Games\Fallout4\F4SE folder.]")
                for elem in list_ERRORLOG:
                    print(elem + "\n-----")
            else:
                print("Available DLL logs do not report any additional errors, all is well. \n-----")

        # CHECK BUFFOUT 4 REQUIREMENTS AND TOML SETTINGS

            if Preloader_XML.is_file() and Preloader_DLL.is_file():
                print('OPTIONAL: Plugin Preloader is (manually) installed.')
                print('NOTICE: If the game fails to start after installing this mod, open xSE PluginPreloader.xml with a text editor and CHANGE')
                print('<LoadMethod Name="ImportAddressHook"> TO <LoadMethod Name="OnThreadAttach"> OR <LoadMethod Name="OnProcessAttach">')
                print('IF THE GAME STILL REFUSES TO START, COMPLETELY REMOVE xSE PluginPreloader.xml AND IpHlpAPI.dll FROM YOUR FO4 GAME FOLDER')
                print("-----")
            else:
                print('OPTIONAL: Plugin Preloader is not (manually) installed.\n-----')
                
            if F4SE_Loader.is_file() and F4SE_DLL.is_file() and F4SE_SDLL.is_file():
                print("REQUIRED: Fallout 4 Script Extender is (manually) installed. \n-----")
            else:
                print("# CAUTION: Auto-Scanner cannot find Script Extender files or they aren't (manually) installed! #")
                print("FIX: Extract all files inside *f4se_0_06_21* folder into your Fallout 4 game folder.")
                print("FALLOUT 4 SCRIPT EXTENDER: (Download Build 0.6.23) https://f4se.silverlock.org")
                print("-----")

            if Address_Library.is_file():
                print("REQUIRED: Address Library is (manually) installed. \n-----")
            else:
                print("# CAUTION: Auto-Scanner cannot find the Adress Library file or it isn't (manually) installed! #")
                print("FIX: Place the *version-1-10-163-0.bin* file manually into Fallout 4/Data/F4SE/Plugins folder.")
                print("ADDRESS LIBRARY: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47327?tab=files")
                print("-----")

            if Buffout_INI.is_file() and Buffout_DLL.is_file():
                with open(Buffout_INI, "r+") as BUFF_Custom:
                    BUFF_config = BUFF_Custom.read()
                    print("REQUIRED: Buffout 4 is (manually) installed. Checking configuration...\n-----")
                    if count_buff_Achieve >= 1 and (count_Achieve_Mod or count_Survival_Mod) >= 1 and "Achievements = true" in BUFF_config:
                        print("# CAUTION: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #")
                        print("Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.")
                        print("-----")
                        BUFF_config = BUFF_config.replace("Achievements = true","Achievements = false")
                    else:
                        print("Achievements parameter in *Buffout4.toml* is correctly configured. \n-----")

                    if (count_buff_Memory and count_Memory_Mod) >= 1 and "MemoryManager = true" in BUFF_config:
                        print("# CAUTION: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #")
                        print("Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.")
                        print("-----")
                        BUFF_config = BUFF_config.replace("MemoryManager = true","MemoryManager = false")
                    else:
                        print("Memory Manager parameter in *Buffout4.toml* is correctly configured. \n-----")

                    if (count_buff_F4EE and count_F4EE_Mod) >= 1 and "F4EE = false" in BUFF_config:
                        print("# CAUTION: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #")
                        print("Auto-Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu.")
                        print("-----")
                        BUFF_config = BUFF_config.replace("F4EE = false","F4EE = true")
                    else:
                        print("Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured. \n-----")
                with open(Buffout_INI, "w+") as BUFF_Custom:
                    BUFF_Custom.write(BUFF_config)
            else:
                print("# CAUTION: Auto-Scanner cannot find Buffout 4 files or they aren't (manually) installed! #")
                print("FIX: Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115")
                print("BUFFOUT 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359?tab=files")
                print("-----")

        else: # INSTRUCTIONS FOR MANUAL FIXING WHEN FCX MODE IS FALSE
            if (count_buff_Achieve and count_Achieve_Mod) >= 1 or (count_buff_Achieve and count_Survival_Mod) >= 1:
                print("# CAUTION: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #")
                print("FIX: Open *Buffout4.toml* and change Achievements parameter to FALSE, this prevents conflicts with Buffout 4.")
                print("-----")
            else:
                print("Achievements parameter in *Buffout4.toml* is correctly configured. \n-----")

            if (count_buff_Memory and count_Memory_Mod) >= 1:
                print("# CAUTION: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #")
                print("FIX: Open *Buffout4.toml* and change MemoryManager parameter to FALSE, this prevents conflicts with Buffout 4.")
                print("-----")
            else:
                print("Memory Manager parameter in *Buffout4.toml* is correctly configured. \n-----")

            if (count_buff_F4EE and count_F4EE_Mod) >= 1:
                print("# CAUTION: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #")
                print("FIX: Open *Buffout4.toml* and change F4EE parameter to TRUE, this prevents bugs and crashes from Looks Menu.")
                print("-----")
            else:
                print("Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured. \n-----")

        print("====================================================")
        print("CHECKING IF LOG MATCHES ANY KNOWN CRASH MESSAGES...")
        print("====================================================")
        Buffout_Trap = False # CHECK FOR KNOWN CRASH MESSAGES - BUFFOUT TRAP

        # ====================== HEADER ERRORS ======================
        if ".dll" in buff_error and "tbbmalloc" not in buff_error:
            print("# MAIN ERROR REPORTS A DLL WAS INVLOVED IN THIS CRASH! # \n-----")

        # Stack Overflow Crash
        if "EXCEPTION_STACK_OVERFLOW" in buff_error:
            print("# Checking for Stack Overflow Crash.........CULPRIT FOUND! #")
            print("> Priority Level: [5]")
            Buffout_Trap = True
            statC_Overflow +=1

        # Active Effect Crash
        if "0x000100000000" in buff_error:
            print("# Checking for Active Effects Crash.........CULPRIT FOUND! #")
            print("> Priority Level: [5]")
            Buffout_Trap = True
            statC_ActiveEffect +=1

        # Bad Math Crash
        if "EXCEPTION_INT_DIVIDE_BY_ZERO" in buff_error:
            print("# Checking for Bad Math Crash...............CULPRIT FOUND! #")
            print("> Priority Level: [5]")
            Buffout_Trap = True
            statC_BadMath +=1

        # Null Crash
        if "0x000000000000" in buff_error:
            print("# Checking for Null Crash...................CULPRIT FOUND! #")
            print("> Priority Level: [5]")
            Buffout_Trap = True
            statC_Null +=1

        # ======================= MAIN ERRORS =======================
        # SPECIAL - Uneducated Shooter (56789)
        count_InvalidArg = crash_message.count("std::invalid_argument")
        # GENERIC - DLL
        count_KERNELBASE = crash_message.count("KERNELBASE.dll")
        count_MSVCP140 = crash_message.count("MSVCP140.dll")
        count_MSVCR110 = crash_message.count("MSVCR110.dll")
        # CBP Crash
        count_CBP = crash_message.count("cbp.dll")
        count_skeleton = crash_message.count("skeleton.nif")
        # DLL Crash
        count_DLCBanner01 = crash_message.count("DLCBannerDLC01.dds")
        # LOD Crash
        count_BGSLocation = crash_message.count("BGSLocation")
        count_BGSQueued = crash_message.count("BGSQueuedTerrainInitialLoad")
        # MCM Crash
        count_FaderData = crash_message.count("FaderData")
        count_FaderMenu = crash_message.count("FaderMenu")
        count_UIMessage = crash_message.count("UIMessage")
        # Decal Crash
        count_BGSDecal = crash_message.count("BGSDecalManager")
        count_BSTempEffect = crash_message.count("BSTempEffectGeometryDecal")
        # Equip Crash
        count_PipboyMapData = crash_message.count("PipboyMapData")
        # Script Crash
        count_Papyrus = crash_message.count("Papyrus")
        count_VirtualMachine = crash_message.count("VirtualMachine")
        # Console Crash
        count_CompileAndRun = crash_message.count("SysWindowCompileAndRun")
        count_ConsoleLogPrinter = crash_message.count("ConsoleLogPrinter")
        # Generic Crash
        count_tbbmalloc = crash_message.count("tbbmalloc.dll")
        # Particle Crash
        count_ParticleSystem = crash_message.count("ParticleSystem")
        # BA2 Limit Crash
        count_LooseFileAsync = crash_message.count("LooseFileAsyncStream")
        # Rendering Crash
        count_d3d11 = crash_message.count("d3d11.dll")
        # Grid Scrap Crash
        count_GridAdjacency = crash_message.count("GridAdjacencyMapNode")
        count_PowerUtils = crash_message.count("PowerUtils")
        # Mesh (NIF) Crash
        count_LooseFileStream = crash_message.count("LooseFileStream")
        count_BSMulti = crash_message.count("BSMultiBoundNode")
        count_BSFade = crash_message.count("BSFadeNode")
        # Texture (DDS) Crash
        count_Create2DTexture = crash_message.count("Create2DTexture")
        count_DefaultTexture = crash_message.count("DefaultTexture")
        # Material (BGSM) Crash
        count_TextureBlack = crash_message.count("DefaultTexture_Black")
        count_NiAlphaProperty = crash_message.count("NiAlphaProperty")
        # NPC Pathing Crash - Static
        count_PathingCell = crash_message.count("PathingCell")
        count_BSPathBuilder = crash_message.count("BSPathBuilder")
        count_PathManagerServer = crash_message.count("PathManagerServer")
        # NPC Pathing Crash - Dynamic
        count_NavMesh = crash_message.count("NavMesh")
        count_NavMeshObstacle = crash_message.count("BSNavmeshObstacleData")
        count_NavMeshDynamic = crash_message.count("DynamicNavmesh")
        # BitDefender Crash
        count_bdhkm64 = crash_message.count("bdhkm64.dll")
        count_DeleteFileW = crash_message.count("usvfs::hook_DeleteFileW")
        # Audio Driver Crash
        count_X3DAudio1_7 = crash_message.count("X3DAudio1_7.dll")
        count_XAudio2_7 = crash_message.count("XAudio2_7.dll")
        # Plugin Limit Crash
        count_BSMemStorage = crash_message.count("BSMemStorage")
        count_ReaderWriter = crash_message.count("DataFileHandleReaderWriter")
        # Plugin Order Crash
        count_Gamebryo = crash_message.count("GamebryoSequenceGenerator")
        # MO2 Extractor Crash
        count_BSD3D = crash_message.count("BSD3DResourceCreator")
        # Nvidia Debris Crash
        count_flexRelease_x64 = crash_message.count("flexRelease_x64.dll")
        # Nvidia Driver Crash
        count_nvwgf2umx = crash_message.count("nvwgf2umx.dll")
        # Vulkan Memory Crash
        count_SubmissionQueue = crash_message.count("DxvkSubmissionQueue")
        # Vulkan Settings Crash
        count_DXGIAdapter = crash_message.count("dxvk::DXGIAdapter")
        count_DXGIFactory = crash_message.count("dxvk::DXGIFactory")
        # Corrupted Audio Crash
        count_BSXAudio2Data = crash_message.count("BSXAudio2DataSrc")
        count_BSXAudio2Game = crash_message.count("BSXAudio2GameSound")
        # Water Collision Crash
        count_BGSWater = crash_message.count("BGSWaterCollisionManager")
        # count_TESWaterForm = crash_message.count("TESWaterForm") | RESERVED
        # Animation / Physics Crash
        count_Anim1 = crash_message.count("hkbVariableBindingSet")
        count_Anim2 = crash_message.count("hkbHandIkControlsModifier")
        count_Anim3 = crash_message.count("hkbBehaviorGraph")
        count_Anim4 = crash_message.count("hkbModifierList")
        # Archive Invalidation Crash
        count_DLCBanner05 = crash_message.count("DLCBanner05.dds")
        # *[Item Crash]
        count_BGSAttachment = crash_message.count("BGSMod::Attachment")
        count_BGSTemplate = crash_message.count("BGSMod::Template")
        count_BGSTemplateItem = crash_message.count("BGSMod::Template::Item")
        # *[Save Crash] <?> *[Bad INI Crash]
        count_BGSSaveBuffer = crash_message.count("BGSSaveFormBuffer")
        # *[Input Crash]
        count_ButtonEvent = crash_message.count("ButtonEvent")
        count_MenuControls = crash_message.count("MenuControls")
        count_MenuOpenClose = crash_message.count("MenuOpenCloseHandler")
        count_PlayerControls = crash_message.count("PlayerControls")
        count_DXGISwapChain = crash_message.count("DXGISwapChain")
        # *[Bad INI Crash] <?> *[Save Crash]
        count_BGSSaveManager = crash_message.count("BGSSaveLoadManager")
        count_BGSSaveThread = crash_message.count("BGSSaveLoadThread")
        count_INIMem1 = crash_message.count("+0CDAD30")
        count_INIMem2 = crash_message.count("+0D09AB7")
        # *[NPC Patrol Crash]
        count_Patrol = crash_message.count("BGSProcedurePatrol")
        count_PatrolExec = crash_message.count("BGSProcedurePatrolExecState")
        count_PatrolActor = crash_message.count("PatrolActorPackageData")
        # *[Precombines Crash]
        count_TESObjectCELL = crash_message.count("TESObjectCELL")
        count_BGSStatic = crash_message.count("BGSStaticCollection")
        count_BGSCombined = crash_message.count("BGSCombinedCellGeometryDB")
        count_BSPacked = crash_message.count("BSPackedCombinedGeomDataExtra")
        # *[Ammo Counter Crash]
        count_HUDAmmo = crash_message.count("HUDAmmoCounter")
        # *[NPC Projectile Crash]
        count_BGSProjectile = crash_message.count("BGSProjectile")
        count_CombatProjectile = crash_message.count("CombatProjectileAimController")
        # *[Player Character Crash]
        count_Player = crash_message.count("PlayerCharacter")
        count_0x7 = crash_message.count("0x00000007")
        count_0x8 = crash_message.count("0x00000008")
        count_0x14 = crash_message.count("0x00000014")
        # *[Creation Club Crash]
        #  Call Stack(s): +01B59A4

        # OTHER | RESERVED
        # count_NiBinaryStream = crash_message.count("BSResourceNiBinaryStream")
        # count_ObjectBindPolicy = crash_message.count("ObjectBindPolicy")

        # ===========================================================
        if count_DLCBanner01 >= 1:
            print("# Checking for DLL Crash....................CULPRIT FOUND! #")
            print("> Priority Level: [5] | DLCBannerDLC01.dds : ",count_DLCBanner01)
            Buffout_Trap = True
            statC_DLL +=1
        # ===========================================================
        if (count_BGSLocation and count_BGSQueued) >= 1:
            print("# Checking for LOD Crash....................CULPRIT FOUND! #")
            print("> Priority Level: [5] | BGSLocation : ",count_BGSLocation," | BGSQueuedTerrainInitialLoad : ",count_BGSQueued)
            Buffout_Trap = True
            statC_LOD +=1
        # ===========================================================
        if (count_FaderData or count_FaderMenu or count_UIMessage) >= 1:
            print("# Checking for MCM Crash....................CULPRIT FOUND! #")
            print("> Priority Level: [3] | FaderData : ",count_FaderData," | FaderMenu : ",count_FaderMenu," | UIMessage : ",count_UIMessage)
            Buffout_Trap = True
            statC_MCM +=1
        # ===========================================================
        if (count_BGSDecal or count_BSTempEffect) >= 1:
            print("# Checking for Decal Crash..................CULPRIT FOUND! #")
            print("> Priority Level: [5] | BGSDecalManager : ",count_BGSDecal," | BSTempEffectGeometryDecal : ",count_BSTempEffect)
            Buffout_Trap = True
            statC_Decal +=1
        # ===========================================================
        if count_PipboyMapData >= 2:
            print("# Checking for Equip Crash..................CULPRIT FOUND! #")
            print("> Priority Level: [2] | PipboyMapData : ",count_PipboyMapData)
            Buffout_Trap = True
            statC_Equip +=1
        # ===========================================================            
        if (count_Papyrus or count_VirtualMachine) >= 2:
            print("# Checking for Script Crash.................CULPRIT FOUND! #")
            print("> Priority Level: [3] | Papyrus : ",count_Papyrus," | VirtualMachine : ",count_VirtualMachine)
            Buffout_Trap = True
            statC_Papyrus +=1
        # ===========================================================
        if count_tbbmalloc >= 3 or str("tbbmalloc") in buff_error:
            print("# Checking for Generic Crash................CULPRIT FOUND! #")
            print("> Priority Level: [2] | tbbmalloc.dll : ",count_tbbmalloc)
            Buffout_Trap = True
            statC_Generic +=1
        # ===========================================================
        if count_LooseFileAsync >= 1:
            print("# Checking for BA2 Limit Crash..............CULPRIT FOUND! #")
            print("> Priority Level: [5] | LooseFileAsyncStream : ",count_LooseFileAsync)
            Buffout_Trap = True
            statC_BA2Limit +=1
        # ===========================================================
        if count_d3d11 >= 3 or str("d3d11") in buff_error:
            print("# Checking for Rendering Crash..............CULPRIT FOUND! #")
            print("> Priority Level: [4] | d3d11.dll : ",count_d3d11)
            Buffout_Trap = True
            statC_Rendering +=1
        # ===========================================================
        if (count_GridAdjacency or count_PowerUtils) >= 1:
            print("# Checking for Grid Scrap Crash.............CULPRIT FOUND! #")
            print("> Priority Level: [5] | GridAdjacencyMapNode : ",count_GridAdjacency," | PowerUtils : ",count_PowerUtils)
            Buffout_Trap = True
            statC_GridScrap +=1
        # ===========================================================
        if (count_LooseFileStream or count_BSFade or count_BSMulti) >= 1 and count_LooseFileAsync == 0:
            print("# Checking for Mesh (NIF) Crash.............CULPRIT FOUND! #")
            print("> Priority Level: [4] | LooseFileStream : ",count_LooseFileStream," | BSFadeNode : ",count_BSFade," | BSMultiBoundNode : ",count_BSMulti)
            Buffout_Trap = True
            statC_NIF +=1
        # ===========================================================
        if (count_Create2DTexture or count_DefaultTexture) >= 1:
            print("# Checking for Texture (DDS) Crash..........CULPRIT FOUND! #")
            print("> Priority Level: [3] | Create2DTexture : ",count_Create2DTexture," | DefaultTexture : ",count_DefaultTexture)
            Buffout_Trap = True
            statC_Texture +=1
        # ===========================================================
        if (count_TextureBlack or count_NiAlphaProperty) >= 1:
            print("# Checking for Material (BGSM) Crash........CULPRIT FOUND! #")
            print("> Priority Level: [3] | DefaultTexture_Black : ",count_TextureBlack," | NiAlphaProperty : ",count_NiAlphaProperty)
            Buffout_Trap = True
            statC_BGSM +=1
        # ===========================================================
        if (count_bdhkm64 or count_DeleteFileW) >= 2:
            print("# Checking for BitDefender Crash............CULPRIT FOUND! #")
            print("> Priority Level: [5] | bdhkm64.dll : ",count_bdhkm64," | usvfs::hook_DeleteFileW : ",count_DeleteFileW)
            Buffout_Trap = True
            statC_BitDefender +=1
        # ===========================================================
        if (count_PathingCell or count_BSPathBuilder or count_PathManagerServer) >= 1:
            print("# Checking for NPC Pathing Crash............CULPRIT FOUND! #")
            print("> Priority Level: [3] | PathingCell : ",count_PathingCell," | BSPathBuilder : ",count_BSPathBuilder," | PathManagerServer : ",count_PathManagerServer)
            Buffout_Trap = True
            statC_NPCPathing +=1
        elif (count_NavMesh or count_NavMeshObstacle or count_NavMeshDynamic) >= 1:
            print("# Checking for NPC Pathing Crash............CULPRIT FOUND! #")
            print("> Priority Level: [3] | NavMesh : ",count_NavMesh," | BSNavmeshObstacleData : ",count_NavMeshObstacle," | DynamicNavmesh : ",count_NavMeshDynamic)
            Buffout_Trap = True
            statC_NPCPathing +=1
        # ===========================================================
        if count_X3DAudio1_7 >= 3 or count_XAudio2_7 >= 2 or str("X3DAudio1_7") in buff_error or str("XAudio2_7") in buff_error:
            print("# Checking for Audio Driver Crash...........CULPRIT FOUND! #")
            print("> Priority Level: [5] | X3DAudio1_7.dll : ",count_X3DAudio1_7," | XAudio2_7.dll : ",count_XAudio2_7)
            Buffout_Trap = True
            statC_Audio +=1
        # ===========================================================
        if count_CBP >= 3 or count_skeleton >= 1 or str("cbp") in buff_error:
            print("# Checking for Body Physics Crash...........CULPRIT FOUND! #")
            print("> Priority Level: [4] | cbp.dll : ",count_CBP," | skeleton.nif : ",count_skeleton)
            Buffout_Trap = True
            statC_BodyPhysics +=1
        # =========================================================== 
        if (count_BSMemStorage or count_ReaderWriter) >= 1:
            print("# Checking for Plugin Limit Crash...........CULPRIT FOUND! #")
            print("> Priority Level: [5] | BSMemStorage : ",count_BSMemStorage," | DataFileHandleReaderWriter : ",count_ReaderWriter)
            Buffout_Trap = True
            statC_PluginLimit +=1
        # =========================================================== 
        if count_Gamebryo >= 1:
            print("# Checking for Plugin Order Crash...........CULPRIT FOUND! #")
            print("> Priority Level: [5] | GamebryoSequenceGenerator : ",count_Gamebryo)
            Buffout_Trap = True
            statC_LoadOrder +=1
        # ===========================================================
        if count_BSD3D == 3 or count_BSD3D == 6:
            print("# Checking for MO2 Extractor Crash..........CULPRIT FOUND! #")
            print("> Priority Level: [5] | BSD3DResourceCreator : ",count_BSD3D)
            Buffout_Trap = True
            statC_MO2Unp +=1
        # ===========================================================
        if count_flexRelease_x64 >= 2 or str("flexRelease_x64") in buff_error:
            print("# Checking for Nvidia Debris Crash..........CULPRIT FOUND! #")
            print("> Priority Level: [5] | flexRelease_x64.dll : ",count_flexRelease_x64)
            Buffout_Trap = True
            statC_NVDebris +=1
        # =========================================================== 
        if count_nvwgf2umx >= 10 or str("nvwgf2umx") in buff_error:
            print("# Checking for Nvidia Driver Crash..........CULPRIT FOUND! #")
            print("> Priority Level: [5] | nvwgf2umx.dll : ",count_nvwgf2umx)
            Buffout_Trap = True
            statC_NVDriver +=1
        # ===========================================================
        if (count_KERNELBASE or count_MSVCP140) >= 3 and count_SubmissionQueue >= 1:
            print("# Checking for Vulkan Memory Crash..........CULPRIT FOUND! #")
            print("> Priority Level: [5] | KERNELBASE.dll : ",count_KERNELBASE," | MSVCP140.dll : ",count_MSVCP140," | DxvkSubmissionQueue : ",count_SubmissionQueue)
            Buffout_Trap = True
            statC_VulkanMem +=1
        # ===========================================================     
        if (count_DXGIAdapter or count_DXGIFactory) >= 1:
            print("# Checking for Vulkan Settings Crash........CULPRIT FOUND! #")
            print("> Priority Level: [5] | dxvk::DXGIAdapter : ",count_DXGIAdapter," | dxvk::DXGIFactory : ",count_DXGIFactory)
            Buffout_Trap = True
            statC_VulkanSet +=1
        # ===========================================================        
        if (count_BSXAudio2Data or count_BSXAudio2Game) >= 1:
            print("# Checking for Corrupted Audio Crash........CULPRIT FOUND! #")
            print("> Priority Level: [4] | BSXAudio2DataSrc : ",count_BSXAudio2Data," | BSXAudio2GameSound : ",count_BSXAudio2Game)
            Buffout_Trap = True
            statC_CorruptedAudio +=1
        # ===========================================================
        if (count_CompileAndRun or count_ConsoleLogPrinter) >= 1:
            print("# Checking for Console Command Crash........CULPRIT FOUND! #")
            print("> Priority Level: [1] | SysWindowCompileAndRun : ",count_CompileAndRun," | ConsoleLogPrinter : ",count_ConsoleLogPrinter)
            Buffout_Trap = True
            statC_ConsoleCommands +=1
        # =========================================================== 
        if count_BGSWater >= 1:
            print("# Checking for Water Collision Crash........CULPRIT FOUND! #")
            print("PLEASE CONTACT ME AS SOON AS POSSIBLE! (CONTACT INFO BELOW)")
            print("> Priority Level: [6] | BGSWaterCollisionManager : ",count_BGSWater)
            Buffout_Trap = True
            statC_Water +=1
        # ===========================================================
        if count_ParticleSystem >= 1:
            print("# Checking for Particle Effects Crash.......CULPRIT FOUND! #")
            print("> Priority Level: [4] | ParticleSystem : ",count_ParticleSystem)
            Buffout_Trap = True
            statC_Particles +=1
        # ===========================================================            
        if int(count_Anim1) or int(count_Anim2) or int(count_Anim3) or int(count_Anim4) >= 1:
            print("# Checking for Animation / Physics Crash....CULPRIT FOUND! #")
            print("> Priority Level: [5] | hkbVariableBindingSet : ",count_Anim1," | hkbHandIkControlsModifier : ",count_Anim2)
            print("                        hkbBehaviorGraph : ",count_Anim3," | hkbModifierList : ",count_Anim4)
            Buffout_Trap = True
            statC_AnimationPhysics +=1
        # ===========================================================            
        if int(count_DLCBanner05) >= 1:
            print("# Checking for Archive Invalidation Crash...CULPRIT FOUND! #")
            print("> Priority Level: [5] | DLCBanner05.dds : ",count_DLCBanner05)
            Buffout_Trap = True
            statC_Invalidation +=1

        # ===========================================================
        print("---------- Unsolved Crash Messages Below ----------")
        
        if "+01B59A4" in buff_error:
            print("Checking for *[Creation Club Crash].......DETECTED!")
            print("> Priority Level: [5]")
            Buffout_Trap = True
            statU_CClub +=1
        
        if (count_BGSAttachment or count_BGSTemplate or count_BGSTemplateItem) >= 1:
            print("Checking for *[Item Crash]................DETECTED!")
            print("> Priority Level: [5] | BGSMod::Attachment : ",count_BGSAttachment," | BGSMod::Template : ",count_BGSTemplate," | BGSMod::Template::Item : ",count_BGSTemplateItem)
            Buffout_Trap = True
            statU_Item +=1
        # ===========================================================           
        if count_BGSSaveBuffer >= 2:
            print("Checking for *[Save Crash]................DETECTED!")
            print("> Priority Level: [5] | BGSSaveFormBuffer : ",count_BGSSaveBuffer)
            Buffout_Trap = True
            statU_Save +=1
        # ===========================================================
        if (count_ButtonEvent or count_MenuControls or count_MenuOpenClose or count_PlayerControls or count_DXGISwapChain) >= 1:
            print("Checking for *[Input Crash]...............DETECTED!")
            print("> Priority Level: [5] | ButtonEvent : ",count_ButtonEvent," | MenuControls : ",count_MenuControls)
            print("                        MenuOpenCloseHandler : ",count_MenuOpenClose," | PlayerControls : ",count_PlayerControls," | DXGISwapChain : ",count_DXGISwapChain)
            Buffout_Trap = True
            statU_Input +=1
        # ===========================================================
        if (count_BGSSaveManager or count_BGSSaveThread or count_BGSSaveBuffer or count_INIMem1 or count_INIMem2) >= 1:
            print("Checking for *[Bad INI Crash].............DETECTED!")
            print("> Priority Level: [5] | BGSSaveLoadManager : ",count_BGSSaveManager," | BGSSaveLoadThread : ",count_BGSSaveThread," | BGSSaveFormBuffer : ",count_BGSSaveBuffer)
            Buffout_Trap = True
            statU_INI +=1
        # ===========================================================
        if (count_Patrol or count_PatrolExec or count_PatrolActor) >= 1: 
            print("Checking for *[NPC Patrol Crash]..........DETECTED!")
            print("> Priority Level: [5] | BGSProcedurePatrol : ",count_Patrol," | BGSProcedurePatrolExecStatel : ",count_PatrolExec," | PatrolActorPackageData : ",count_PatrolActor)
            Buffout_Trap = True
            statU_Patrol +=1
        # ===========================================================            
        if (count_BSPacked or count_BGSCombined or count_BGSStatic or count_TESObjectCELL) >= 1:
            print("Checking for *[Precombines Crash].........DETECTED!")
            print("> Priority Level: [5] | BGSStaticCollection : ",count_BGSStatic," | BGSCombinedCellGeometryDB : ",count_BGSCombined)
            print("                        BSPackedCombinedGeomDataExtra : ",count_BSPacked," | TESObjectCELL : ",count_TESObjectCELL)
            Buffout_Trap = True
            statU_Precomb +=1
        # =========================================================== 
        if count_HUDAmmo >= 1:
            print("Checking for *[Ammo Counter Crash]........DETECTED!")
            print("> Priority Level: [5] | HUDAmmoCounter : ",count_HUDAmmo)
            Buffout_Trap = True
            statU_HUDAmmo +=1
        # ===========================================================
        if (count_BGSProjectile or count_CombatProjectile) >= 1:
             print("Checking for *[NPC Projectile Crash].....DETECTED!")
             print("> Priority Level: [5] | BGSProjectile : ",count_BGSProjectile," | CombatProjectileAimController : ",count_CombatProjectile)
             Buffout_Trap = True
        # ===========================================================
        if (count_Player and count_0x7) >= 2 and (count_0x14 or count_0x8) >= 2:
            print("Checking for *[Player Character Crash]....DETECTED!")
            print("> Priority Level: [5] | PlayerCharacter : ",count_Player," | 0x00000007 : ",count_0x7)
            print("                        0x00000008 : ",count_0x8," | 0x000000014 : ",count_0x14)
            Buffout_Trap = True
            statU_Player +=1
       
        # ===========================================================
        
        if Buffout_Trap == False: # DEFINE CHECK IF NOTHING TRIGGERED BUFFOUT TRAP
            print("-----")
            print("# AUTOSCAN FOUND NO CRASH MESSAGES THAT MATCH THE CURRENT DATABASE #")
            print("Check below for mods that can cause frequent crashes and other problems.")
            print("-----")
        else:
            print("-----")
            print("FOR DETAILED DESCRIPTIONS AND POSSIBLE SOLUTIONS TO ANY ABOVE DETECTED CRASH MESSAGES,")
            print("SEE: https://docs.google.com/document/d/17FzeIMJ256xE85XdjoPvv_Zi3C5uHeSTQh6wOZugs4c")
            print("-----")

        print("====================================================")
        print("CHECKING FOR MODS THAT CAN CAUSE FREQUENT CRASHES...")
        print("====================================================")
        Mod_Trap1 = 1

        count_LoadOrder = crash_message.count("[00]")
        count_CHW = crash_message.count("ClassicHolsteredWeapons")
        count_BSShadow = crash_message.count("BSShadowParabolicLight")
        count_BSShader = crash_message.count("BSShaderAccumulator")
        count_BSDFLight = crash_message.count("BSDFLightShader")
        count_UniquePlayer = crash_message.count("UniquePlayer.esp")
        count_BodyNIF = crash_message.count("Body.nif")
        count_HighHeels = crash_message.count("HHS.dll")

        # Why lists and not dictionaries? So I can preserve alphabetical order in code and
        # numerical order in output without having to rename a bunch of variables.
        # Needs 1 empty space as prefix to prevent duplicates.
        List_Mods1 = [" DamageThresholdFramework.esm",
                      " Endless Warfare.esm",
                      " ExtendedWeaponSystem.esm",
                      " EPO",
                      " SakhalinWasteland",
                      " 76HUD",
                      " NCRenegade",
                      " Respawnable Legendary Bosses",
                      " Scrap Everything - Core",
                      " Scrap Everything - Ultimate",
                      " Shade Girl Leather Outfits",
                      " SpringCleaning.esm",
                      " (STO) NO",
                      " TacticalTablet.esp",
                      " True Nights",
                      " WeaponsFramework",
                      " WOTC.esp"]

        List_Warn1 = ["DAMAGE THRESHOLD FRAMEWORK \n"
                      "- Can cause crashes in combat on some occasions due to how damage calculations are done.",
                      
                      "ENDLESS WARFARE \n"
                      "- Some enemy spawn points could be bugged or crash the game due to scripts or pathfinding.",
                      
                      "EXTENDED WEAPON SYSTEMS \n"
                      "- Alternative to Tactical Reload that suffers from similar weapon related problems and crashes.",
                      
                      "EXTREME PARTICLES OVERHAUL \n"
                      "- Can cause particle effects related crashes, its INI file raises particle count to 500000. \n"
                      "  Consider switching to Burst Impact Blast FX: https://www.nexusmods.com/fallout4/mods/57789",
                      
                      "FALLOUT SAKHALIN \n"
                      "- Breaks the precombine system all across Far Harbor which will randomly crash your game.",
                      
                      "HUD76 HUD REPLACER \n"
                      "- Can sometimes cause interface and pip-boy related bugs, glitches and crashes.",
                      
                      "NCR RENEGADE ARMOR \n"
                      "- Broken outfit mesh that crashes the game in 3rd person or when NPCs wearing it are hit.",
                      
                      "RESPAWNABLE LEGENDARY BOSSES \n"
                      "- Can sometimes cause Deathclaw \ Behmoth boulder projectile crashes for unknown reasons.",
                      
                      "SCRAP EVERYTHING (CORE) \n"
                      "- Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order.",
                      
                      "SCRAP EVERYTHING (ULTIMATE) \n"
                      "- Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order.",
                      
                      "SHADE GIRL LEATHER OUTFITS \n"
                      "- Outfits can crash the game while browsing the armor workbench or upon starting a new game due to bad meshes.",
                      
                      "SPRING CLEANING \n"
                      "- Abandoned and severely outdated mod that breaks precombines and could potentially even break your save file.",
                      
                      "STALKER TEXTURE OVERHAUL \n"
                      "- Doesn't work due to incorrect folder structure and has a corrupted dds file that causes Create2DTexture crashes.",  
                      
                      "TACTICAL TABLET \n"
                      "- Can cause flickering with certain scopes or crashes while browsing workbenches, most commonly with ECO.",
                      
                      "TRUE NIGHTS \n"
                      "- Has an invalid Image Space Adapter (IMAD) Record that will corrupt your save memory and has to be manually fixed.",
                      
                      "WEAPONS FRAMEWORK BETA \n"
                      "- Will randomly cause crashes when used with Tactical Reload and possibly other weapon or combat related mods. \n"
                      "  Visit Important Patches List article for possible solutions: https://www.nexusmods.com/fallout4/articles/3769",
                      
                      "WAR OF THE COMMONWEALTH \n"
                      "- Seems responsible for consistent crashes with specific spawn points or randomly during settlement attacks."]

        if count_LoadOrder >= 1:
            for line in plugin_list:
                for elem in List_Mods1:
                    if str("File:") not in line and str("[FE") not in line and elem in line:
                        order_elem = List_Mods1.index(elem)
                        print("[!] Found:", line[0:5].strip(), List_Warn1[order_elem])
                        print("-----")
                        Mod_Trap1 = 0
                    elif str("File:") not in line and str("[FE") in line and elem in line:
                        order_elem = List_Mods1.index(elem)
                        print("[!] Found:", line[0:9].strip(), List_Warn1[order_elem])
                        print("-----")
                        Mod_Trap1 = 0

            if count_CHW >= 2 and (count_BSShadow or count_BSShader or count_BSDFLight) >= 1 or str("ClassicHolsteredWeapons") in buff_error:
                print("[!] Found: CLASSIC HOLSTERED WEAPONS")
                print("AUTOSCAN IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!")
                print("You should disable CHW to further confirm this.")
                print("Visit the main crash logs article for additional solutions.")
                print("-----")
                statM_CHW +=1
                Mod_Trap1 = 0
                Buffout_Trap = True
            elif count_CHW >= 2 and (count_UniquePlayer or count_HighHeels or count_CBP or count_BodyNIF) >= 1:
                print("[!] Found: CLASSIC HOLSTERED WEAPONS")
                print("AUTOSCAN ALSO DETECTED ONE OR SEVERAL MODS THAT WILL CRASH WITH CHW.")
                print("You should disable CHW to further confirm it caused this crash.")
                print("Visit the main crash logs article for additional solutions.")
                print("-----")
                statM_CHW +=1
                Mod_Trap1 = 0
                Buffout_Trap = True
            elif count_CHW == 1 and str("d3d11") in buff_error:
                print("[!] Found: CLASSIC HOLSTERED WEAPONS, BUT...")
                print("AUTOSCAN CANNOT ACCURATELY DETERMINE IF CHW CAUSED THIS CRASH OR NOT.")
                print("You should open CHW's ini file and change IsHolsterVisibleOnNPCs to 0.")
                print("This usually prevents most common crashes with Classic Holstered Weapons.")
                print("-----")
                Mod_Trap1 = 0
        if count_LoadOrder >= 1 and Mod_Trap1 == 0:
            print("# CAUTION: ANY ABOVE DETECTED MODS HAVE A MUCH HIGHER CHANCE TO CRASH YOUR GAME! #")
            print("You can disable any/all of them temporarily to confirm they caused this crash.")
            print("-----")
            statL_scanned +=1
        elif count_LoadOrder >= 1 and Mod_Trap1 == 1:
            print("# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT MATCH THE CURRENT DATABASE FOR THIS LOG #")
            print("THAT DOESN'T MEAN THERE AREN'T ANY! YOU SHOULD RUN PLUGIN CHECKER IN WRYE BASH.")
            print("Wrye Bash Link: https://www.nexusmods.com/fallout4/mods/20032?tab=files")
            print("-----")
            statL_scanned +=1
        elif count_LoadOrder == 0:
            print("# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #")
            print("Autoscan cannot continue. Try scanning a different crash log.")
            print("-----")
            statL_incomplete +=1

        print("====================================================")
        print("CHECKING FOR MODS WITH SOLUTIONS & COMMUNITY PATCHES")
        print("====================================================")
        Mod_Trap2 = no_repeat1 = no_repeat2 = 1 # MOD TRAP 2 | NEED 8 SPACES FOR ESL [FE:XXX]
        
        count_FallSouls = crash_message.count("FallSouls.dll")

        # Needs 1 empty space as prefix to prevent duplicates.
        List_Mods2 = [" DLCUltraHighResolution.esm",
                      " AAF.esm",
                      " ArmorKeywords.esm",
                      " BTInteriors_Project.esp",
                      " CombatZoneRestored",
                      " D.E.C.A.Y.esp",
                      " EveryonesBestFriend",
                      " M8r_Item_Tags",
                      " Fo4FI_FPS_fix",
                      " BostonFPSFixAIO.esp",
                      " FunctionalDisplays.esp",
                      " skeletonmaleplayer",
                      " skeletonfemaleplayer",
                      " CapsWidget",
                      " Homemaker.esm",
                      " Horizon.esm",
                      " ESPExplorerFO4.esp",
                      " LegendaryModification.esp",
                      " MilitarizedMinutemen.esp",
                      " MoreUniques",
                      " NAC.es",
                      " Northland Diggers New.esp",
                      " RaiderOverhaul.esp",
                      " Rusty Face Fix",
                      " SKKCraftableWeaponsAmmo",
                      " SOTS.esp",
                      " StartMeUp.esp",
                      " SuperMutantRedux.esp",
                      " TacticalReload.esm",
                      " Creatures and Monsters.esp",
                      " ZombieWalkers"]

        List_Warn2 = ["HIGH RESOLUTION DLC. I STRONGLY ADVISE NOT USING IT! \n"
                      "Right click on Fallout 4 in your Steam Library folder, then select Properties \n"
                      "Switch to the DLC tab and uncheck / disable the High Resolution Texture Pack",
                      #
                      "ADVANCED ANIMATION FRAMEWORK \n"
                      "Newest AAF version only available on Moddingham | AAF Tech Support: https://discord.gg/gWZuhMC \n"
                      "Newest AAF Link (register / login to download): https://www.moddingham.com/viewtopic.php?t=2 \n"
                      "-----\n"
                      "Looks Menu versions 1.6.20 & 1.6.19 can frequently break adult mod related (erection) morphs \n"
                      "If you notice AAF realted problems, remove latest version of Looks Menu and switch to 1.6.18",
                      #
                      "ARMOR AND WEAPON KEYWORDS \n"
                      "If you don't rely on AWKCR, consider switching to Equipment and Crafting Overhaul \n"
                      "Better Alternative: https://www.nexusmods.com/fallout4/mods/55503?tab=files",
                      #
                      "BEANTOWN INTERIORS PROJECT \n"
                      "Usually causes fps drops, stuttering, crashing and culling issues in multiple locations. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/53894?tab=files",
                      #
                      "COMBAT ZONE RESTORED \n"
                      "Contains few small issues and NPCs usually have trouble navigating the interior space. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/59329?tab=files",
                      #
                      "DECAY BETTER GHOULS \n"
                      "You have to install DECAY Redux patch to prevent its audio files from crashing the game. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/59025?tab=files",
                      #
                      "EVERYONE'S BEST FRIEND \n"
                      "This mod needs a compatibility patch to properly work with the Unofficial Patch (UFO4P). \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/43409?tab=files",
                      #
                      "FALLUI ITEM SORTER (OLD) \n"
                      "This is an outdated item tagging / sorting patch that can cause crashes or conflicts in all kinds of situations. \n"
                      "I strongly recommend to instead generate your own sorting patch and place it last in your load order. \n"
                      "That way, you won't experience any conflicts / crashes and even modded items will be sorted. \n"
                      "Generate Sorting Patch With This: https://www.nexusmods.com/fallout4/mods/48826?tab=files",
                      #
                      "FO4FI FPS FIX \n"
                      "This mod is severely outdated and will cause crashes even with compatibility patches. \n"
                      "Better Alternative: https://www.nexusmods.com/fallout4/mods/46403?tab=files",
                      #
                      "BOSTON FPS FIX \n"
                      "This mod is severely outdated and will cause crashes even with compatibility patches. \n"
                      "Better Alternative: https://www.nexusmods.com/fallout4/mods/46403?tab=files",
                      #
                      "FUNCTIONAL DISPLAYS \n"
                      "Frequently causes object model (nif) related crashes and this needs to be manually corrected. \n"
                      "Advised Fix: Open its Meshes folder and delete everything inside EXCEPT for the Functional Displays folder.",
                      #
                      "GENDER SPECIFIC SKELETONS (MALE) \n"
                      "High chance to cause a crash when starting a new game or during the game intro sequence. \n"
                      "Advised Fix: Enable the mod only after leaving Vault 111. Existing saves shouldn't be affected.",
                      #
                      "GENDER SPECIFIC SKELETONS (FEMALE) \n"
                      "High chance to cause a crash when starting a new game or during the game intro sequence. \n"
                      "Advised Fix: Enable the mod only after leaving Vault 111. Existing saves shouldn't be affected.",
                      #
                      "HUD CAPS \n"
                      "Often breaks the Save / Quicksave function due to poor script implementation. \n"
                      "Advised Fix: Download fixed pex file and place it into HUDCaps/Scripts folder. \n"
                      "Fix Link: https://drive.google.com/file/d/1egmtKVR7mSbjRgo106UbXv_ySKBg5az2",
                      #
                      "HOMEMAKER \n"
                      "Causes a crash while scrolling over Military / BoS fences in the Settlement Menu. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/41434?tab=files",
                      #
                      "HORIZON \n"
                      "Use the mod specific unofficial patch for 1.8.7 until a newer version gets released. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/61998?tab=files",
                      #
                      "IN GAME ESP EXPLORER \n"
                      "Can cause a crash when pressing F10 due to a typo in the INI settings. \n"
                      "Fix Link: https://www.nexusmods.com/fallout4/mods/64752?tab=files \n"
                      "OR Switch To: https://www.nexusmods.com/fallout4/mods/56922?tab=files",
                      #
                      "LEGENDARY MODIFICATION \n"
                      "Old mod plagued with all kinds of bugs and crashes, can conflict with some modded weapons. \n"
                      "Better Alternative: https://www.nexusmods.com/fallout4/mods/55503?tab=files",
                      #
                      "MILITARIZED MINUTEMEN \n"
                      "Can occasionally crash the game due to a broken mesh on some minutemen outfits. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/55301?tab=files",
                      #
                      "MORE UNIQUE WEAPONS EXPANSION \n"
                      "Causes crashes due to broken precombines and compatibility issues with other weapon mods. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/54848?tab=files",
                      #
                      "NATURAL AND ATMOSPHERIC COMMONWEALTH \n"
                      "If you notice weird looking skin tones with either NAC or NACX, install this patch. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/57052?tab=files",
                      #
                      "NORTHLAND DIGGERS RESOURCES \n"
                      "Contains various bugs and issues that can cause crashes or negatively affect other mods. \n"
                      "Fix Link: https://www.nexusmods.com/fallout4/mods/53395?tab=files",
                      #
                      "RAIDER OVERHAUL \n"
                      "Old mod that requires several patches to function as intended. Use ONE Version instead. \n"
                      "Upated ONE Version: https://www.nexusmods.com/fallout4/mods/51658?tab=files",
                      #
                      "RUSTY FACE FIX \n"
                      "Can cause script lag or even crash the game in very rare cases. Switch to REDUX Version instead. \n"
                      "Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/64270?tab=files",
                      #
                      "SKK CRAFT WEAPONS AND SCRAP AMMO \n"
                      "Version 008 is incompatible with AWKCR and will cause crashes while saving the game. \n"
                      "Advised Fix: Use Version 007 or remove AWKCR and switch to Equipment and Crafting Overhaul.",
                      #
                      "SOUTH OF THE SEA \n"
                      "Very unstable mod that consistently and frequently causes strange problems and crashes. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/59792?tab=files",
                      #
                      "START ME UP \n"
                      "Abandoned mod that can cause infinite loading and other problems. Switch to REDUX Version instead. \n"
                      "Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/56984?tab=files",
                      #
                      "SUPER MUTANT REDUX \n"
                      "Causes crashes at specific locations or with certain Super Muntant enemies and items. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/51353?tab=files",
                      #
                      "TACTICAL RELOAD \n"
                      "Can cause weapon and combat related crashes. TR Expansion For ECO is highly recommended. \n"
                      "TR Expansion For ECO Link: https://www.nexusmods.com/fallout4/mods/62737",
                      #
                      "UNIQUE NPCs CREATURES AND MONSTERS \n"
                      "Causes crashes and breaks precombines at specific locations, some creature spawns are too frequent. \n"
                      "Patch Link: https://www.nexusmods.com/fallout4/mods/48637?tab=files",
                      #
                      "ZOMBIE WALKERS \n"
                      "Version 2.6.3 contains a resurrection script that will regularly crash the game. \n"
                      "Advised Fix: Make sure you're using the 3.0 Beta version of this mod or newer."]

        if count_LoadOrder >= 1:
            for line in plugin_list:
                for elem in List_Mods2:
                    if str("File:") not in line and str("[FE") not in line and elem in line:
                        order_elem = List_Mods2.index(elem)
                        print("[!] Found:", line[0:5].strip(), List_Warn2[order_elem])
                        print("-----")
                        Mod_Trap2 = 0
                    elif str("File:") not in line and str("[FE") in line and elem in line:
                        order_elem = List_Mods2.index(elem)
                        print("[!] Found:", line[0:9].strip(), List_Warn2[order_elem])
                        print("-----")
                        Mod_Trap2 = 0
                if no_repeat1 == 1 and "File:" not in line and ("Depravity" or "FusionCityRising" or "HotC" or "OutcastsAndRemnants" or "ProjectValkyrie") in line:
                    print("[!] Found:", line[0:9].strip(), "THUGGYSMURF QUEST MOD")
                    print("If you have Depravity, Fusion City Rising, HOTC, Outcasts and Remnants and/or Project Valkyrie,")
                    print("install this patch with facegen data, fully generated precomb/previs data and several tweaks.")
                    print("Patch Link: https://www.nexusmods.com/fallout4/mods/56876?tab=files")
                    print("-----")
                    no_repeat1 = Mod_Trap2 = 0
                if no_repeat1 == 1 and "File:" not in line and ("CaN.esm" or "AnimeRace_Nanako.esp") in line:
                    print("[!] Found:", line[0:9].strip(), "CUSTOM RACE SKELETON MOD")
                    print("If you have AnimeRace NanakoChan or Crimes Against Nature, install the Race Skeleton Fixes.")
                    print("Skeleton Fixes Link (READ THE DESCRIPTION): https://www.nexusmods.com/fallout4/mods/56101")
                    no_repeat2 = Mod_Trap2 = 0

            if count_FallSouls >= 1:
                print("[!] Found: FALLSOULS UNPAUSED GAME MENUS")
                print("Occasionally breaks the Quests menu, can cause crashes while changing MCM settings.")
                print("Advised Fix: Toggle PipboyMenu in FallSouls MCM settings or completely reinstall the mod.")
                print("-----")
                Mod_Trap2 = 0
        if count_LoadOrder >= 1 and Mod_Trap2 == 0:
            print("[Due to inherent limitations, Auto-Scan will continue detecting certain mods,")
            print(" even if fixes or patches for them are already installed. You can ignore these.]")
            print("-----")
        elif count_LoadOrder >= 1 and Mod_Trap2 == 1:
            print("# AUTOSCAN FOUND NO PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #")
            print("-----")
        elif count_LoadOrder == 0:
            print("# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #")
            print("Autoscan cannot continue. Try scanning a different crash log.")
            print("-----")

        print("FOR FULL LIST OF IMPORTANT PATCHES AND FIXES FOR THE BASE GAME AND MODS,")
        print("VISIT THIS ARTICLE: https://www.nexusmods.com/fallout4/articles/3769")
        print("-----")

        print("====================================================")
        print("CHECKING FOR MODS PATCHED THROUGH OPC INSTALLER...")
        print("====================================================")
        Mod_Trap3 = 1 # MOD TRAP 3 | NEED 8 SPACES FOR ESL [FE:XXX]

        # Needs 1 empty space as prefix to prevent duplicates.
        List_Mods3 = [" Beyond the Borders",
                      " Deadly Commonwealth Expansion",
                      " Dogmeat and Strong Armor",
                      " DoYourDamnJobCodsworth",
                      " ConcordEXPANDED",
                      " HagenEXPANDED",
                      " GlowingSeaEXPANDED",
                      " SalemEXPANDED",
                      " SwampsEXPANDED",
                      " _hod",
                      " ImmersiveBeantown",
                      " CovenantComplex",
                      " GunnersPlazaInterior",
                      " ImmersiveHubCity",
                      " Immersive_Lexington",
                      " Immersive Nahant",
                      " Immersive S Boston",
                      " MutilatedDeadBodies",
                      " Vault4.esp",
                      " atlanticofficesf23",
                      " Minutemen Supply Caches",
                      " moreXplore",
                      " NEST_BUNKER_PROJECT",
                      " Raider Children.esp",
                      " sectorv",
                      " SettlementShelters",
                      " subwayrunnnerdynamiclighting",
                      " 3DNPC_FO4Settler.esp",
                      " 3DNPC_FO4.esp",
                      " The Hollow",
                      " nvvault1080",
                      " Vertibird Faction Paint Schemes",
                      " MojaveImports.esp",
                      " Firelance2.5",
                      " zxcMicroAdditions"]

        List_Warn3 = ["Beyond the Borders",
                      "Deadly Commonwealth Expansion",
                      "Dogmeat and Strong Armor",
                      "Do Your Damn Job Codsworth",
                      "Concord Expanded",
                      "Fort Hagen Expanded",
                      "Glowing Sea Expanded",
                      "Salem Expanded",
                      "Swamps Expanded",
                      "Hearts Of Darkness",
                      "Immersive Beantown Brewery",
                      "Immersive Covenant Compound",
                      "Immersive Gunners Plaza",
                      "Immersive Hub City",
                      "Immersive & Extended Lexington",
                      "Immersive & Extended Nahant",
                      "Immersive Military Checkpoint",
                      "Mutilated Dead Bodies",
                      "Fourville (Vault 4)",
                      "Lost Building of Atlantic",
                      "Minutemen Supply Caches",
                      "MoreXplore",
                      "NEST Survival Bunkers",
                      "Raider Children & Other Horrors",
                      "Sector Five - Rise and Fall",
                      "Settlement Shelters",
                      "Subway Runner (Dynamic Lights)",
                      "Settlers of the Commonwealth",
                      "Tales from the Commonwealth",
                      "The Hollow",
                      "Vault 1080 (Vault 80)",
                      "Vertibird Faction Paint Schemes",
                      "Wasteland Imports (Mojave Imports)",
                      "Xander's Aid",
                      "ZXC Micro Additions"]

        if count_LoadOrder >= 1:
            for line in plugin_list:
                for elem in List_Mods3:
                    if str("File:") not in line and str("[FE") not in line and elem in line:
                        order_elem = List_Mods3.index(elem)
                        print("- Found:", line[0:5].strip(), List_Warn3[order_elem])
                        Mod_Trap3 = 0
                    elif str("File:") not in line and str("[FE") in line and elem in line:
                        order_elem = List_Mods3.index(elem)
                        print("- Found:", line[0:9].strip(), List_Warn3[order_elem])
                        Mod_Trap3 = 0
        if count_LoadOrder >= 1 and Mod_Trap3 == 0:  
            print("-----")
            print("FOR PATCH REPOSITORY THAT PREVENTS CRASHES AND FIXES PROBLEMS IN THESE AND OTHER MODS,")
            print("VISIT OPTIMIZATION PATCHES COLLECTION: https://www.nexusmods.com/fallout4/mods/54872")
            print("-----")
        elif count_LoadOrder >= 1 and Mod_Trap3 == 1:
            print("# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT ARE ALREADY PATCHED THROUGH OPC INSTALLER #")
            print("-----")           
        elif count_LoadOrder == 0:
            print("# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #")
            print("Autoscan cannot continue. Try scanning a different crash log.")
            print("-----")

        # ===========================================================

        print("====================================================")
        print("CHECKING IF IMPORTANT PATCHES & FIXES ARE INSTALLED")
        print("====================================================")

        gpu_amd = False
        gpu_nvidia = False
        for line in all_lines:
            if "GPU" in line and "Nvidia" in line:
                gpu_nvidia = True
            if "GPU" in line and "AMD" in line:
                gpu_amd = True

        count_PhysicsFIX = crash_message.count("HighFPSPhysicsFix.dll")
        count_DebrisFIX = crash_message.count("WeaponDebrisCrashFix.dll")
        count_ReflexFix = crash_message.count("NVIDIA_Reflex.dll")
        count_VulkanDLL = crash_message.count("vulkan-1.dll")

        print("IF YOU'RE USING DYNAMIC PERFORMANCE TUNER AND/OR LOAD ACCELERATOR,")
        print("remove these mods completely and switch to High FPS Physics Fix!")
        print("Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files")
        print("-----")

        if count_LoadOrder >= 1:
            if any("CanarySaveFileMonitor" in elem for elem in plugin_list):
                print("*Canary Save File Monitor* is installed. \n-----")
            else:
                print("# CANARY SAVE FILE MONITOR ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("This is a highly recommended mod that can detect save file corrpution.")
                print("Link: https://www.nexusmods.com/fallout4/mods/44949?tab=files")
                print("-----")

            if count_PhysicsFIX > 0:
                print("*High FPS Physics Fix* is installed. \n-----")
            else:
                print("# HIGH FPS PHYSICS FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("This is a mandatory patch / fix that prevents game engine problems.")
                print("Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files")
                print("-----")

            if any("PPF.esm" in elem for elem in plugin_list):
                print("*Previs Repair Pack* is installed. \n-----")
            else:
                print("# PREVIS REPAIR PACK ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("This is a highly recommended mod that can improve performance.")
                print("Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files")
                print("-----")

            if any("Unofficial Fallout 4 Patch.esp" in elem for elem in plugin_list):
                print("*Unofficial Fallout 4 Patch* is installed. \n-----")
            else:
                print("# UNOFFICIAL FALLOUT 4 PATCH ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("If you own all DLCs, make sure that the Unofficial Patch is installed.")
                print("Link: https://www.nexusmods.com/fallout4/mods/4598?tab=files")
                print("-----")

            if count_VulkanDLL > 0 and gpu_amd:
                print("Vulkan Renderer is installed. \n-----")
            elif count_VulkanDLL == 0 and gpu_amd and not gpu_nvidia:
                print("VULKAN RENDERER ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("This is a highly recommended mod that can improve performance on AMD GPUs.")
                print("-----") 
                print("Installation steps can be found in 'How To Read Crash Logs' PDF / Document.")
                print("Link: https://www.nexusmods.com/fallout4/mods/48053?tab=files")
                print("-----")

            if count_DebrisFIX > 0 and gpu_nvidia:
                print("*Weapon Debris Crash Fix* is installed. \n-----")
            elif count_DebrisFIX > 0 and not gpu_nvidia or gpu_amd:
                print("*Weapon Debris Crash Fix* is installed, but...")
                print("# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #")
                print("Weapon Debris Crash Fix is only required for Nvidia GPUs (NOT AMD / OTHER)")
                print("-----")
            elif count_DebrisFIX == 0 and gpu_nvidia:
                print("# WEAPON DEBRIS CRASH FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("This is a mandatory patch / fix for players with Nvidia graphics cards.")
                print("Link: https://www.nexusmods.com/fallout4/mods/48078?tab=files")
                print("-----")

            if count_ReflexFix > 0 and gpu_nvidia:
                print("*Nvidia Reflex Support* is installed. \n-----")
            elif count_ReflexFix > 0 and not gpu_nvidia or gpu_amd:
                print("*Nvidia Reflex Support* is installed, but...")
                print("# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #")
                print("Nvidia Reflex Support is only required for Nvidia GPUs (NOT AMD / OTHER)")
                print("-----")
            elif count_ReflexFix == 0 and gpu_nvidia:
                print("# NVIDIA REFLEX SUPPORT ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #")
                print("This is a highly recommended mod that can reduce render latency.")
                print("Link: https://www.nexusmods.com/fallout4/mods/64459?tab=files")
                print("-----")
        else:
            print("# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #")
            print("Autoscan cannot continue. Try scanning a different crash log.")
            print("-----")

        print("====================================================")
        print("SCANNING THE LOG FOR SPECIFIC (POSSIBLE) CUPLRITS...")
        print("====================================================")

        list_DETPLUGINS = []
        list_DETFORMIDS = []
        list_DETFILES = []
        list_ALLPLUGINS = []

        count_F4SE = crash_message.count("f4se_1_10_163.dll")
        count_Module = crash_message.count("steam_api64.dll")

        if count_F4SE == 0 and count_Module >= 1:
            print("AUTOSCAN CANNOT FIND FALLOUT 4 SCRIPT EXTENDER DLL!")
            print("MAKE SURE THAT F4SE IS CORRECTLY INSTALLED!")
            print("Link: https://f4se.silverlock.org")
            print("-----")

        for line in all_lines:
            if len(line) >= 6 and "]" in line[4]:
                list_ALLPLUGINS.append(line.strip())
            if len(line) >= 7 and "]" in line[5]:
                list_ALLPLUGINS.append(line.strip())
            if len(line) >= 10 and "]" in line[8]:
                list_ALLPLUGINS.append(line.strip())
            if len(line) >= 11 and "]" in line[9]:
                list_ALLPLUGINS.append(line.strip())

        print("LIST OF (POSSIBLE) PLUGIN CULRIPTS:")
        for line in all_lines:
          if "File:" in line:
            line = line.replace("File: ", "") 
            line = line.replace('"', '') 
            list_DETPLUGINS.append(line.strip())

        list_DETPLUGINS = list(dict.fromkeys(list_DETPLUGINS))
        list_remove = ["Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm", ""]
        for elem in list_remove:
            if elem in list_DETPLUGINS:
                list_DETPLUGINS.remove(elem)

        PL_strings = list_ALLPLUGINS
        PL_substrings = list_DETPLUGINS
        PL_result = []

        for string in PL_strings:
            PL_matches = []
            for substring in PL_substrings:
                if substring in string:
                    PL_matches.append(string)
            if PL_matches:
                PL_result.append(PL_matches)
                print("- " + ' '.join(PL_matches))

        if not PL_result:
            print("* AUTOSCAN COULDN'T FIND ANY PLUGIN CULRIPTS *")
            print("-----")
        else:
            print("-----")
            print("These Plugins were caught by Buffout 4 and some of them might be responsible for this crash.")
            print("You can try disabling these plugins and recheck your game, though this method can be unreliable.")
            print("-----")

        # ===========================================================

        print("LIST OF (POSSIBLE) FORM ID CULRIPTS:")
        for line in all_lines:
          if "Form ID:" in line and not "0xFF" in line:
            line = line.replace("0x", "")
            list_DETFORMIDS.append(line.strip())
            line = line.replace("Form ID: ", "")
            line = line[:5].strip()

        list_DETFORMIDS = list(dict.fromkeys(list_DETFORMIDS))
        for elem in list_DETFORMIDS:
            print(elem)

        if not list_DETFORMIDS:
            print("* AUTOSCAN COULDN'T FIND ANY FORM ID CULRIPTS *")
            print("-----")
        else:
            print("-----")
            print("These Form IDs were caught by Buffout 4 and some of them might be related to this crash.")
            print("You can try searching any listed Form IDs in FO4Edit and see if they lead to relevant records.")
            print("-----")

        # ===========================================================

        print("LIST OF (POSSIBLE) FILE CULPRITS:")
        List_Files = [".bgsm",".bto",".btr",".dds",".fuz",".hkb",".hkx",".ini",".nif",".pex",".swf",".txt",".uvd",".wav",".xwm","data\*"]

        for line in all_lines:
            for elem in List_Files:
                if elem in line.lower():
                    line = line.replace("File Name: ", "")
                    line = line.replace("Name: ", "")
                    line = line.replace('"', '')
                    list_DETFILES.append(line.strip())
                # if "[rsp+" in line.lower() and ".dll" in line.lower():
                #     list_DETFILES.append(line.strip()) | RESERVED

        list_DETFILES = list(dict.fromkeys(list_DETFILES))
        for elem in list_DETFILES:
            print(elem)

        if not list_DETFILES:
            print("* AUTOSCAN COULDN'T FIND ANY FILE CULRIPTS *")
            print("-----")
        else:
            print("-----")
            print("These files were caught by Buffout 4 and some of them might be related to this crash.")
            print("Detected files in most cases appear as false positives, so no recommendation is given.")
            print("-----")

        # ===========================================================

        print("LIST OF DETECTED (NAMED) RECORDS:")
        List_Named = []
        for line in all_lines:
            for elem in list_DETFILES:
                if not elem in line.lower() and not '""' in line and not "..." in line and "Name:" in line:
                    line = line.replace('"', '')
                    List_Named.append(line.strip())

        List_Named = list(dict.fromkeys(List_Named))
        for elem in List_Named:
            print(elem)

        if not List_Named:
            print("* AUTOSCAN COULDN'T FIND ANY NAMED RECORDS *")
            print("-----")
        else:
            print("-----")
            print("These records were caught by Buffout 4 and some of them might be related to this crash.")
            print("Named records should give extra information on involved game objects and record types.")
            print("-----")

        print("FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,")
        print("VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115")
        print("===============================================================================")
        print("END OF AUTOSCAN | Author/Made By: Poet#9800 (DISCORD) |",CLAS_Date,)
        crash_log.close()
        sys.stdout.close()

        # MOVE UNSOLVED LOGS TO SPECIAL FOLDER
        if CLAS_config.get("MAIN","Move Unsolved").lower() == "true":
            if not os.path.exists("CLAS-UNSOLVED"):
               os.mkdir("CLAS-UNSOLVED")
            if int(Buffout_Trap) == 1:
                uCRASH_path = "CLAS-UNSOLVED/" + crashlog
                shutil.move(crashlog, uCRASH_path)
                uSCAN_path = "CLAS-UNSOLVED/" + logname + "-AUTOSCAN.md"
                shutil.move(logname + "-AUTOSCAN.md", uSCAN_path)

# dict.fromkeys -> Create dictionary, removes duplicates as dicts cannot have them.
# BUFFOUT.INI BACK TO BUFFOUT.TOML BECAUSE PYTHON CAN'T WRITE
if Buffout_INI.is_file():
    try:
      os.rename(Buffout_INI, Buffout_TOML)
    except FileExistsError:
      os.remove(Buffout_TOML)
      os.rename(Buffout_INI, Buffout_TOML)

# ========================== LOG END ==========================
sys.stdout=orig_stdout
print("SCAN COMPLETE! (IT MIGHT TAKE SEVERAL SECONDS FOR SCAN RESULTS TO APPEAR)")
print("SCAN RESULTS ARE AVAILABE IN FILES NAMED crash-date-and-time-AUTOSCAN.md")
print("===============================================================================")
print("FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,")
print("VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115")
print(random.choice(Sneaky_Tips))

# ============ CHECK FOR EMPTY (FAUTLY) AUTO-SCANS ============

list_SCANFAIL = []
for file in os.listdir("."):
    if fnmatch.fnmatch(file, "*-AUTOSCAN.md"):
        line_count = 0
        scanname = str(file)
        autoscan_log = open(file, errors="ignore")
        for line in autoscan_log:
            if line != "\n":
                line_count += 1
        if int(line_count) <= 10:
            list_SCANFAIL.append(scanname.removesuffix("-AUTOSCAN.md") + ".log")
            statL_failed +=1

if len(list_SCANFAIL) >= 1:
    print("NOTICE: AUTOSCANNER WAS UNABLE TO PROPERLY SCAN THE FOLLOWING LOG(S): ")
    for elem in list_SCANFAIL:
        print(elem)
    print("===============================================================================")
    print("To troubleshoot this, right click on Scan Crashlogs.py and select option 'Edit With IDLE'")
    print("Once it opens the code, press [F5] to run the script. Any error messages will appear in red.")
    print("-----")
    print('If any given error contains "codec cant decode byte", you can fix this in two ways:')
    print('1.) Move all crash logs and the scan script into a folder with short and simple path name, example: "C:\Crash Logs"')
    print("-----")
    print('2.) Open the original crash log with Notepad, select File > Save As... and make sure that Encoding is set to UTF-8,')
    print('then press Save and overwrite the original crash log file. Run the Scan Crashlogs script again after that.')
    print("-----")
    print('FOR ALL OTHER ERRORS PLEASE CONTACT ME DIRECTLY, CONTACT INFO BELOW!')

print("======================================================================")
print("END OF AUTOSCAN | Author/Made By: Poet |",CLAS_Date,"| All Rights Reserved.")
print("============================ CONTACT INFO ============================")
print("DISCORD | Poet#9800 (https://discord.gg/DfFYJtt8p4)")
print("NEXUS MODS | https://www.nexusmods.com/users/64682231")
print("SCAN SCRIPT PAGE | https://www.nexusmods.com/fallout4/mods/56255")
print("======================================================================")
print("\nScanned all available logs in", (str(time.time() - start_time)[:7]), "seconds.")
print("Number of Scanned Logs (No Autoscan Errors): ", statL_scanned)
print("Number of Incomplete Logs (No Plugins List): ", statL_incomplete)
print("Number of Failed Logs (Autoscan Can't Scan): ", statL_failed)
print("Number of Very Old / Wrong Formatting Logs): ", statL_veryold)
print("(Set Stat Logging to true in Scan Crashlogs.ini for additional stats.)")
print("-----")
if CLAS_config.get("MAIN","Stat Logging").lower() == "true":
    print("Logs with Stack Overflow Crash...........", statC_Overflow)
    print("Logs with Active Effects Crash...........", statC_ActiveEffect)
    print("Logs with Bad Math Crash.................", statC_BadMath)
    print("Logs with Null Crash.....................", statC_Null)
    print("Logs with DLL Crash......................", statC_DLL)
    print("Logs with LOD Crash......................", statC_LOD)
    print("Logs with MCM Crash......................", statC_MCM)
    print("Logs with Decal Crash....................", statC_Decal)
    print("Logs with Equip Crash....................", statC_Equip)
    print("Logs with Script Crash...................", statC_Papyrus)
    print("Logs with Generic Crash..................", statC_Generic)
    print("Logs with BA2 Limit Crash................", statC_BA2Limit)
    print("Logs with Rendering Crash................", statC_Rendering)
    print("Logs with Grid Scrap Crash...............", statC_GridScrap)
    print("Logs with Mesh (NIF) Crash...............", statC_NIF)
    print("Logs with Texture (DDS) Crash............", statC_Texture)
    print("Logs with Material (BGSM) Crash..........", statC_BGSM)
    print("Logs with BitDefender Crash..............", statC_BitDefender)
    print("Logs with NPC Pathing Crash..............", statC_NPCPathing)
    print("Logs with Audio Driver Crash.............", statC_Audio)
    print("Logs with Body Physics Crash.............", statC_BodyPhysics)
    print("Logs with Plugin Limit Crash.............", statC_PluginLimit)
    print("Logs with Plugin Order Crash.............", statC_LoadOrder)
    print("Logs with MO2 Extractor Crash............", statC_MO2Unp)
    print("Logs with Nvidia Debris Crash............", statC_NVDebris)
    print("Logs with Nvidia Driver Crash............", statC_NVDriver)
    print("Logs with Vulkan Memory Crash............", statC_VulkanMem)
    print("Logs with Vulkan Settings Crash..........", statC_VulkanSet)
    print("Logs with Console Command Crash..........", statC_ConsoleCommands)
    print("Logs with Water Collision Crash..........", statC_Water)
    print("Logs with Particle Effects Crash.........", statC_Particles)
    print("Logs with Animation / Physics Crash......", statC_AnimationPhysics)
    print("Logs with Archive Invalidation Crash.....", statC_Invalidation)
    print("-----")
    print("Crashes caused by Clas. Hols. Weapons....", statM_CHW)
    print("-----")
    print("Logs with *[Creation Club Crash].........", statU_CClub)
    print("Logs with *[Item Crash]..................", statU_Item)
    print("Logs with *[Save Crash]..................", statU_Save)
    print("Logs with *[Input Crash].................", statU_Input)
    print("Logs with *[Bad INI Crash]...............", statU_INI)
    print("Logs with *[NPC Patrol Crash]............", statU_Patrol)
    print("Logs with *[Precombines Crash]...........", statU_Precomb)
    print("Logs with *[Ammo Counter Crash]..........", statU_HUDAmmo)
    print("Logs with *[NPC Projectile Crash]........", statU_Projectile)
    print("Logs with *[Player Character Crash]......", statU_Player)
    print("*Unsolved, see How To Read Crash Logs PDF")
    print("===========================================")
sys.stdout.close()
os.system("pause")