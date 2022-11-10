import fnmatch
import logging
import os
import pathlib
import platform
import random
import shutil
import stat
import sys
import time
from glob import glob
from pathlib import Path

try:
    import requests
    RequestsImportFailed = False
except ImportError:
    RequestsImportFailed = True
import configparser
import subprocess

if platform.system() == "Windows":
    import ctypes.wintypes

if not os.path.exists("Scan Crashlogs.ini"):  # INI FILE FOR AUTO-SCANNER
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
CLAS_config.optionxform = str  # type: ignore
CLAS_config.read("Scan Crashlogs.ini")
Python_Current = sys.version[:6]
CLAS_Date = "051122"  # DDMMYY
CLAS_Current = "CLAS v5.90"
CLAS_Update = False


def run_update():
    print("CHECKING FOR PACKAGE & CRASH LOG AUTO-SCANNER UPDATES...")
    print("(You can disable this check in Scan Crashlogs.ini) \n")
    print(f"Installed Python Version: {Python_Current} \n")
    if not Python_Current[:4] in ["3.11", "3.10", "3.9", "3.8"]:
        print("CAUTION: YOUR PYTHON VERSION IS OUT OF DATE! PLEASE UPDATE PYTHON.")
        print("FOR LINUX / WIN 10 / WIN 11: https://www.python.org/downloads")
        print("FOR WINDOWS 7: https://github.com/adang1345/PythonWin7")
    if RequestsImportFailed:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'requests'])
    # reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    # installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
    # print("List of all installed packages:", installed_packages) | RESERVED
    # print("===============================================================================")
    response = requests.get("https://api.github.com/repos/GuidanceOfGrace/Buffout4-CLAS/releases/latest")
    return response.json()["name"]


if CLAS_config.getboolean("MAIN", "Update Check") == True:
    CLAS_Received = run_update()
    try:  # AUTO UPDATE PIP, INSTALL & LIST PACKAGES
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
else:
    print("\n NOTICE: UPDATE CHECK IS DISABLED IN Scan Crashlogs.ini \n")

Sneaky_Tips = ["\nRandom Hint: [Ctrl] + [F] is a handy-dandy key combination. You should use it more often. Please.\n",
               "\nRandom Hint: Patrolling the Buffout 4 Nexus Page almost makes you wish this joke was more overused.\n",
               "\nRandom Hint: You have a crash log where Autoscanner couldn't find anything? Feel free to send it to me.\n",
               "\nRandom Hint: 20% of all crashes are caused by Classic Holstered Weapons mod. 80% of all statistics are made up.\n",
               "\nRandom Hint: No, I don't know why your game froze instead of crashed. But I know someone who might know; Google.\n",
               "\nRandom Hint: Spending 5 morbillion hours asking for help can save you from 5 minutes of reading the documentation.\n",
               "\nRandom Hint: When necessary, make sure that crashes are consistent or repeatable, since in rare cases they aren't.\n",
               "\nRandom Hint: When posting crash logs, it's helpful to mention the last thing you were doing before the crash happened.\n",
               "\nRandom Hint: Be sure to revisit both Buffout 4 Crash Crticle and Auto-Scanner Nexus Page from time to time for updates.\n"]

# =================== STATISTICS LOGGING ===================
# MAIN STATS
statL_scanned = statL_incomplete = statL_failed = statL_veryold = 0
# KNOWN CRASH MESSAGES
statC_ActiveEffect = statC_AnimationPhysics = statC_Audio = statC_BA2Limit = statC_BGSM = statC_BitDefender = statC_BodyPhysics = statC_ConsoleCommands = statC_CorruptedTex = 0
statC_DLL = statC_Equip = statC_Generic = statC_GridScrap = statC_Invalidation = statC_LoadOrder = statC_MCM = statC_BadMath = statC_NIF = statC_NPCPathing = statC_NVDebris = 0
statC_NVDriver = statC_Null = statC_Overflow = statC_Papyrus = statC_Particles = statC_PluginLimit = statC_Rendering = statlogtexture = statC_CorruptedAudio = statC_LOD = 0
statC_Decal = statC_MO2Unp = statC_VulkanMem = statC_VulkanSet = statC_Water = 0
# UNSOLVED CRASH MESSAGES
statU_Precomb = statU_Player = statU_Save = statU_HUDAmmo = statU_Patrol = statU_Projectile = statU_Item = statU_Input = statU_INI = statU_CClub = 0
# KNOWN CRASH CONDITIONS
statM_CHW = 0

print("Hello World! | Crash Log Auto-Scanner | Version", CLAS_Current[-4:], "| Fallout 4")
print("CRASH LOGS MUST BE .log AND IN THE SAME FOLDER WITH THIS SCRIPT!")
print("===============================================================================")
print("You should place this script into your Documents/My Games/Fallout4/F4SE folder.")
print("(This is where Buffout 4 crash log files are generated after the game crashes.)")
print("===============================================================================")
print("CAUTION: Crash Log Auto-Scanner will not work correctly on Windows 7 systems.")
print("For Win 7, install this Py version: https://github.com/adang1345/PythonWin7")
print("Click on the green Code button and Download Zip, then extract and install.")
print("===============================================================================")
FO4_STEAM_ID = 377160


class Info:
    def __init__(self):
        self.VR_EXE: Path | None = None
        self.VR_Buffout: Path | None = None
        self.F4CK_EXE: Path | None = None
        self.F4CK_Fixes: Path | None = None
        self.Steam_INI: Path | None = None
        self.Preloader_DLL: Path | None = None
        self.Preloader_XML: Path | None = None
        self.F4SE_Loader: Path | None = None
        self.F4SE_DLL: Path | None = None
        self.F4SE_SDLL: Path | None = None
        self.Buffout_DLL: Path | None = None
        self.Buffout_INI: Path | None = None
        self.Buffout_TOML: Path | None = None
        self.Address_Library: Path | None = None
        self.Game_Path: str | None = None

        Loc_Found = False
        if platform.system() == "Windows":
            # Using shell32.dll to look up Documents directory path. Thanks, StackOverflow!
            # Unsure os.path.expanduser('~/Documents') works if default path was changed.
            CSIDL_PERSONAL = 5       # (My) Documents
            SHGFP_TYPE_CURRENT = 0   # Get current, not default value.
            User_Documents = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)  # type: ignore
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, User_Documents)  # type: ignore
            Doc_Path = User_Documents.value
            self.FO4_Custom_Path = Path(rf"{Doc_Path}\My Games\Fallout4\Fallout4Custom.ini")
            self.FO4_F4SE_Path = Path(rf"{Doc_Path}\My Games\Fallout4\F4SE\f4se.log")
            self.FO4_F4SE_Logs = rf"{Doc_Path}\My Games\Fallout4\F4SE"
            Loc_Found = True
        else:  # Find where FO4 is installed via Steam if Linux
            home_directory = str(Path.home())
            if os.path.isfile(rf"{home_directory}/.local/share/Steam/steamapps/libraryfolders.vdf"):
                steam_library = None
                library_path = None
                with open(rf"{home_directory}/.local/share/Steam/steamapps/libraryfolders.vdf") as steam_library_raw:
                    steam_library = steam_library_raw.readlines()
                for line in steam_library:
                    if "path" in line:
                        library_path = line.split('"')[3]
                    if str(FO4_STEAM_ID) in line:
                        library_path = rf"{library_path}/steamapps"
                        settings_path = rf"{library_path}/compatdata/{FO4_STEAM_ID}/pfx/drive_c/users/steamuser/My Documents/My Games/Fallout4"
                        if os.path.exists(rf"{library_path}/common/Fallout 4") and os.path.exists(settings_path):
                            self.FO4_Custom_Path = Path(rf"{settings_path}/Fallout4Custom.ini")
                            self.FO4_F4SE_Path = Path(rf"{settings_path}/F4SE/f4se.log")
                            self.FO4_F4SE_Logs = rf"{settings_path}/F4SE"
                            Loc_Found = True
                            break
        # Prompt manual input if ~\Documents\My Games\Fallout4 cannot be found.
        if not Loc_Found:
            if "fallout4" in CLAS_config.get("MAIN", "INI Path").lower():
                INI_Line = CLAS_config.get("MAIN", "INI Path").strip()
                self.FO4_F4SE_Logs = rf"{INI_Line}\F4SE"
                self.FO4_F4SE_Path = Path(rf"{INI_Line}\F4SE\f4se.log")
                self.FO4_Custom_Path = Path(rf"{INI_Line}\Fallout4Custom.ini")
            else:
                print("> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR Fallout4.ini IS LOCATED < <")
                Path_Input = input("(EXAMPLE: C:/Users/Zen/Documents/My Games/Fallout4 | Press ENTER to confirm.)\n> ")
                print("You entered :", Path_Input, "| This path will be automatically added to Scan Crashlogs.ini")
                self.FO4_F4SE_Logs = rf"{Path_Input.strip()}\F4SE"
                self.FO4_F4SE_Path = Path(rf"{Path_Input.strip()}\F4SE\f4se.log")
                self.FO4_Custom_Path = Path(rf"{Path_Input.strip()}\Fallout4Custom.ini")
                CLAS_config.set("MAIN", "INI Path", Path_Input)
                with open("Scan Crashlogs.ini", "w+") as INI_Autoscan:
                    CLAS_config.write(INI_Autoscan)


info = Info()
# Create/Open Fallout4Custom.ini and check Archive Invalidaton & other settings.
if CLAS_config.getboolean("MAIN", "FCX Mode") == True:
    if info.FO4_Custom_Path.is_file():
        os.chmod(info.FO4_Custom_Path, stat.S_IWRITE)
        F4C_config = configparser.ConfigParser()
        F4C_config.optionxform = str  # type: ignore
        F4C_config.read(info.FO4_Custom_Path)
        if "Archive" not in F4C_config.sections():
            F4C_config.add_section("Archive")
        F4C_config.set("Archive", "bInvalidateOlderFiles", "1")
        F4C_config.set("Archive", "sResourceDataDirsFinal", "")
        with open(info.FO4_Custom_Path, "w+") as FO4_Custom:
            F4C_config.write(FO4_Custom, space_around_delimiters=False)
    else:
        with open(info.FO4_Custom_Path, "w+") as FO4_Custom:
            F4C_config = "[Archive]\nbInvalidateOlderFiles=1\nsResourceDataDirsFinal="
            FO4_Custom.write(F4C_config)

# Check if f4se.log exists and find game path inside.
if info.FO4_F4SE_Path.is_file():
    with open(info.FO4_F4SE_Path, "r") as LOG_Check:
        Path_Check = LOG_Check.readlines()
        for line in Path_Check:
            if "plugin directory" in line:
                line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                info.Game_Path = line.replace("\n", "")
else:
    print("\n CAUTION: AUTO-SCANNER CANNOT FIND THE REQUIRED F4SE.LOG FILE!")
    print("MAKE SURE THAT FALLOUT 4 SCRIPT EXTENDER IS CORRECTLY INSTALLED!")
    print("Link: https://f4se.silverlock.org")
    os.system("pause")

# FILES TO LOOK FOR IN GAME FOLDER ONLY (NEEDS r BECAUSE UNICODE ERROR)
info.VR_EXE = Path(rf"{info.Game_Path}\Fallout4VR.exe")
info.VR_Buffout = Path(rf"{info.Game_Path}\Data\F4SE\Plugins\msdia140.dll")
info.F4CK_EXE = Path(rf"{info.Game_Path}\CreationKit.exe")
info.F4CK_Fixes = Path(rf"{info.Game_Path}\Data\F4CKFixes")
info.Steam_INI = Path(rf"{info.Game_Path}\steam_api.ini")
info.Preloader_DLL = Path(rf"{info.Game_Path}\IpHlpAPI.dll")
info.Preloader_XML = Path(rf"{info.Game_Path}\xSE PluginPreloader.xml")
info.F4SE_Loader = Path(rf"{info.Game_Path}\f4se_loader.exe")
info.F4SE_DLL = Path(rf"{info.Game_Path}\f4se_1_10_163.dll")
info.F4SE_SDLL = Path(rf"{info.Game_Path}\f4se_steam_loader.dll")
info.Buffout_DLL = Path(rf"{info.Game_Path}\Data\F4SE\Plugins\Buffout4.dll")
info.Buffout_INI = Path(rf"{info.Game_Path}\Data\F4SE\Plugins\Buffout4.ini")
info.Buffout_TOML = Path(rf"{info.Game_Path}\Data\F4SE\Plugins\Buffout4.toml")
info.Address_Library = Path(rf"{info.Game_Path}\Data\F4SE\Plugins\version-1-10-163-0.bin")

if info.Buffout_TOML.is_file():  # RENAME BECAUSE PYTHON CAN'T WRITE TO TOML
    try:
        os.chmod(info.Buffout_TOML, stat.S_IWRITE)
        os.rename(info.Buffout_TOML, info.Buffout_INI)
    except FileExistsError:
        os.remove(info.Buffout_INI)
        os.chmod(info.Buffout_TOML, stat.S_IWRITE)
        os.rename(info.Buffout_TOML, info.Buffout_INI)

# CAN'T USE CONFIGPARSER BECAUSE DUPLICATE COMMENT IN Buffout_INI
# To preserve original toml formatting, just stick to replace.
# ===========================================================

print("\n PERFORMING SCAN... \n")
start_time = time.time()
# orig_stdout = sys.stdout

logs = glob("crash-*.log")  # + glob("crash-*.txt") # For people who just HAVE to post their logs on pastebin.

for file in logs:
    logpath = Path(file).resolve()
    scanpath = Path(str(logpath.name).replace(".log", "-AUTOSCAN.md")).resolve()
    logname = logpath.name
    logtext = logpath.read_text()
    loglines: list | None = None
    with logpath.open("r+", encoding="utf-8", errors="ignore") as lines:
        loglines = lines.readlines()
    with scanpath.open("w", encoding='utf-8-sig', errors="ignore") as output:
        output.write(logname)
        output.write("This crash log was automatically scanned.")
        output.write(f"VER {CLAS_Current[-4:]} | MIGHT CONTAIN FALSE POSITIVES.")
        if CLAS_Update == True:
            output.write("# NOTICE: YOU NEED TO UPDATE THE AUTO-SCANNER! #")
        output.write("====================================================")

        # DEFINE LINE INDEXES FOR EVERYTHING REQUIRED HERE
        buff_ver = loglines[1].strip()
        buff_error = loglines[3].strip()
        plugin_idx = 1
        for line in loglines:
            if not "F4SE" in line and "PLUGINS:" in line:
                plugin_idx = loglines.index(line)

        plugin_list = loglines[plugin_idx:]
        if os.path.exists("loadorder.txt"):
            plugin_list = []
            with open("loadorder.txt", "r", errors="ignore") as loadorder_check:
                plugin_format = loadorder_check.readlines()
                for line in plugin_format:
                    line = "[LO] " + line.strip()
                    plugin_list.append(line)

        # BUFFOUT VERSION CHECK
        buff_latest = "Buffout 4 v1.26.2"
        output.write(f"Main Error: {buff_error}")
        output.write("====================================================")
        output.write(f"Detected Buffout Version: {buff_ver.strip()}")
        output.write(f"Latest Buffout Version: {buff_latest.strip()}")

        if buff_ver.casefold() == buff_latest.casefold():
            output.write("You have the lastest version of Buffout 4!")
        else:
            output.write("REPORTED BUFFOUT VERSION DOES NOT MATCH THE BUFFOUT VERSION USED BY AUTOSCAN")
            output.write("UPDATE BUFFOUT 4 IF NECESSARY: https://www.nexusmods.com/fallout4/mods/47359")

        if "v1." not in buff_ver:
            statL_veryold += 1
            statL_scanned -= 1

        output.write("====================================================")
        output.write("CHECKING IF BUFFOUT 4 FILES/SETTINGS ARE CORRECT...")
        output.write("====================================================")

        ALIB_Load = BUFF_Load = False

        # CHECK IF F4SE.LOG EXISTS AND REPORTS ANY ERRORS
        if CLAS_config.getboolean("MAIN", "FCX Mode") == True:
            output.writelines(["* NOTICE: FCX MODE IS ENABLED. AUTO-SCANNER MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *",
                               "[ To disable game folder / mod files detection, set FCX Mode = false in Scan Crashlogs.ini ]",
                               "-----"
                               ])
            Error_List = []
            F4SE_Error = F4SE_Version = F4SE_Buffout = 0
            with open(info.FO4_F4SE_Path, "r") as LOG_Check:
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
                output.write("You have the latest version of Fallout 4 Script Extender (F4SE). \n-----")
            else:
                output.write("# REPORTED F4SE VERSION DOES NOT MATCH THE F4SE VERSION USED BY AUTOSCAN #")
                output.write("UPDATE FALLOUT 4 SCRIPT EXTENDER IF NECESSARY: https://f4se.silverlock.org")
                output.write("-----")

            if F4SE_Error == 1:
                output.write("# SCRIPT EXTENDER REPORTS THAT THE FOLLOWING PLUGINS FAILED TO LOAD! #")
                for elem in Error_List:
                    output.write(f"{elem}\n-----")
            else:
                output.write("Script Extender reports that all DLL mod plugins have loaded correctly. \n-----")

            if F4SE_Buffout == 1:
                output.write("Script Extender reports that Buffout 4.dll was found and loaded correctly. \n-----")
                ALIB_Load = BUFF_Load = True
            else:
                output.write("# SCRIPT EXTENDER REPORTS THAT BUFFOUT 4.DLL FAILED TO LOAD OR IS MISSING! #")
                output.write("Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115")
                output.write("Buffout 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359")
                output.write("-----")

            list_ERRORLOG = []
            for file in info.FO4_F4SE_Logs:
                if fnmatch.fnmatch(file, ".log"):
                    with open(file, "r+") as LOG_Check:
                        Log_Errors = LOG_Check.read()
                        if "error" in Log_Errors.lower():
                            logname = str(file)
                            if not logname == "f4se.log":
                                list_ERRORLOG.append(logname)

            if len(list_ERRORLOG) >= 1:
                output.write("# CAUTION: THE FOLLOWING DLL LOGS ALSO REPORT ONE OR MORE ERRORS : #")
                output.write("[These are located in your Documents/My Games/Fallout4/F4SE folder.]")
                for elem in list_ERRORLOG:
                    output.write(f"{elem}\n-----")
            else:
                output.write("Available DLL logs do not report any additional errors, all is well. \n-----")

        # CHECK BUFFOUT 4 REQUIREMENTS AND TOML SETTINGS
            if info.Preloader_XML.is_file() and info.Preloader_DLL.is_file():
                output.write('OPTIONAL: Plugin Preloader is (manually) installed.\n')
                output.write('NOTICE: If the game fails to start after installing this mod, open xSE PluginPreloader.xml with a text editor and CHANGE')
                output.write('<LoadMethod Name="ImportAddressHook"> TO <LoadMethod Name="OnThreadAttach"> OR <LoadMethod Name="OnProcessAttach">')
                output.write('IF THE GAME STILL REFUSES TO START, COMPLETELY REMOVE xSE PluginPreloader.xml AND IpHlpAPI.dll FROM YOUR FO4 GAME FOLDER')
                output.write("-----")
            else:
                output.write('OPTIONAL: Plugin Preloader is not (manually) installed.\n-----')

            if info.F4SE_Loader.is_file() and info.F4SE_DLL.is_file() and info.F4SE_SDLL.is_file():
                output.write("REQUIRED: Fallout 4 Script Extender is (manually) installed. \n-----")
            else:
                output.write("# CAUTION: Auto-Scanner cannot find Script Extender files or they aren't (manually) installed! #")
                output.write("FIX: Extract all files inside *f4se_0_06_21* folder into your Fallout 4 game folder.")
                output.write("FALLOUT 4 SCRIPT EXTENDER: (Download Build 0.6.23) https://f4se.silverlock.org")
                output.write("-----")

            if info.Address_Library.is_file() or ALIB_Load == True:
                output.write("REQUIRED: Address Library is (manually) installed. \n-----")
            else:
                output.write("# CAUTION: Auto-Scanner cannot find the Adress Library file or it isn't (manually) installed! #")
                output.write("FIX: Place the *version-1-10-163-0.bin* file manually into Fallout 4/Data/F4SE/Plugins folder.")
                output.write("ADDRESS LIBRARY: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47327?tab=files")
                output.write("-----")

            if info.Buffout_INI.is_file() and info.Buffout_DLL.is_file() or BUFF_Load == True:
                with open(info.Buffout_INI, "r+") as BUFF_Custom:
                    BUFF_config = BUFF_Custom.read()
                    output.write("REQUIRED: Buffout 4 is (manually) installed. Checking configuration...\n-----")
                    if ("achievements.dll" or "UnlimitedSurvivalMode.dll") in logtext and "Achievements = true" in BUFF_config:
                        output.write("# CAUTION: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #")
                        output.write("Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.")
                        output.write("-----")

                        BUFF_config = BUFF_config.replace("Achievements = true", "Achievements = false")
                    else:
                        output.write("Achievements parameter in *Buffout4.toml* is correctly configured. \n-----")

                    if "BakaScrapHeap.dll" in logtext and "MemoryManager = true" in BUFF_config:
                        output.write("# CAUTION: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #")
                        output.write("Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.")
                        output.write("-----")
                        BUFF_config = BUFF_config.replace("MemoryManager = true", "MemoryManager = false")
                    else:
                        output.write("Memory Manager parameter in *Buffout4.toml* is correctly configured. \n-----")

                    if "f4ee.dll" in logtext and "F4EE = false" in BUFF_config:
                        output.write("# CAUTION: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #")
                        output.write("Auto-Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu.")
                        output.write("-----")
                        BUFF_config = BUFF_config.replace("F4EE = false", "F4EE = true")
                    else:
                        output.write("Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured. \n-----")
                with open(info.Buffout_INI, "w+") as BUFF_Custom:
                    BUFF_Custom.write(BUFF_config)
            else:
                output.write("# CAUTION: Auto-Scanner cannot find Buffout 4 files or they aren't (manually) installed! #")
                output.write("FIX: Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115")
                output.write("BUFFOUT 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359?tab=files")
                output.write("-----")

        else:  # INSTRUCTIONS FOR MANUAL FIXING WHEN FCX MODE IS FALSE
            if ("Achievements: true" in logtext and "achievements.dll" in logtext) or ("Achievements: true" in logtext and "UnlimitedSurvivalMode.dll" in logtext):
                output.write("# CAUTION: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #")
                output.write("FIX: Open *Buffout4.toml* and change Achievements parameter to FALSE, this prevents conflicts with Buffout 4.")
                output.write("-----")
            else:
                output.write("Achievements parameter in *Buffout4.toml* is correctly configured. \n-----")

            if "MemoryManager: true" in logtext and "BakaScrapHeap.dll" in logtext:
                output.write("# CAUTION: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #")
                output.write("FIX: Open *Buffout4.toml* and change MemoryManager parameter to FALSE, this prevents conflicts with Buffout 4.")
                output.write("-----")
            else:
                output.write("Memory Manager parameter in *Buffout4.toml* is correctly configured. \n-----")

        if "F4EE: false" in logtext and "f4ee.dll" in logtext:
            output.write("# CAUTION: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #")
            output.write("FIX: Open *Buffout4.toml* and change F4EE parameter to TRUE, this prevents bugs and crashes from Looks Menu.")
            output.write("-----")
        else:
            output.write("Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured. \n-----")

        output.write("====================================================")
        output.write("CHECKING IF LOG MATCHES ANY KNOWN CRASH MESSAGES...")
        output.write("====================================================")
        Buffout_Trap = False  # RETURN TRUE IF KNOWN CRASH MESSAGE WAS FOUND

        # ====================== HEADER ERRORS ======================

        if ".dll" in buff_error and "tbbmalloc" not in buff_error:
            output.write("# MAIN ERROR REPORTS A DLL WAS INVLOVED IN THIS CRASH! # \n-----")

        if "EXCEPTION_STACK_OVERFLOW" in buff_error:
            output.writelines(["# Checking for Stack Overflow Crash.........CULPRIT FOUND! #",
                               "> Priority : [5]"
                               ])
            Buffout_Trap = True
            statC_Overflow += 1

        if "0x000100000000" in buff_error:
            output.writelines(["# Checking for Active Effects Crash.........CULPRIT FOUND! #",
                               "> Priority : [5]"
                               ])
        Buffout_Trap = True
        statC_ActiveEffect += 1

        if "EXCEPTION_INT_DIVIDE_BY_ZERO" in buff_error:
            output.writelines(["# Checking for Bad Math Crash...............CULPRIT FOUND! #",
                               "> Priority : [5]"
                               ])
            Buffout_Trap = True
            statC_BadMath += 1

        if "0x000000000000" in buff_error:
            output.writelines(["# Checking for Null Crash...................CULPRIT FOUND! #",
                               "> Priority : [5]"
                               ])
            Buffout_Trap = True
            statC_Null += 1

        # ======================= MAIN ERRORS =======================

        # OTHER | RESERVED
        # *[Creation Club Crash] | +01B59A4
        # Uneducated Shooter (56789) | logtext.count("std::invalid_argument")
        # logtext.count("BSResourceNiBinaryStream")
        # logtext.count("ObjectBindPolicy")

        # ===========================================================
        if "DLCBannerDLC01.dds" in logtext:
            output.writelines(["# Checking for DLL Crash....................CULPRIT FOUND! #",
                               f'> Priority : [5] | DLCBannerDLC01.dds : {logtext.count("DLCBannerDLC01.dds")}'
                               ])
            Buffout_Trap = True
            statC_DLL += 1
        # ===========================================================
        if "BGSLocation" in logtext and "BGSQueuedTerrainInitialLoad" in logtext:
            output.writelines(['# Checking for LOD Crash....................CULPRIT FOUND! #',
                               f'> Priority : [5] | BGSLocation : {logtext.count("BGSLocation")} | BGSQueuedTerrainInitialLoad : {logtext.count("BGSQueuedTerrainInitialLoad")}'
                               ])
            Buffout_Trap = True
            statC_LOD += 1
        # ===========================================================
        if ("FaderData" or "FaderMenu" or "UIMessage") in logtext:
            output.writelines(["# Checking for MCM Crash....................CULPRIT FOUND! #",
                               f'> Priority : [3] | FaderData : {logtext.count("FaderData")} | FaderMenu : {logtext.count("FaderMenu")} | UIMessage : {logtext.count("UIMessage")}'
                               ])
            Buffout_Trap = True
            statC_MCM += 1
        # ===========================================================
        if ("BGSDecalManager" or "BSTempEffectGeometryDecal") in logtext:
            output.writelines(["# Checking for Decal Crash..................CULPRIT FOUND! #",
                               f'> Priority : [5] | BGSDecalManager : {logtext.count("BGSDecalManager")} | BSTempEffectGeometryDecal : {logtext.count("BSTempEffectGeometryDecal")}'
                               ])
            Buffout_Trap = True
            statC_Decal += 1
        # ===========================================================
        if logtext.count("PipboyMapData") >= 2:
            output.writelines(["# Checking for Equip Crash..................CULPRIT FOUND! #",
                               f'> Priority : [2] | PipboyMapData : {logtext.count("PipboyMapData")}'
                               ])
            Buffout_Trap = True
            statC_Equip += 1
        # ===========================================================
        if (logtext.count("Papyrus") or logtext.count("VirtualMachine")) >= 2:
            output.writelines(["# Checking for Script Crash.................CULPRIT FOUND! #",
                               f'> Priority : [3] | Papyrus : {logtext.count("Papyrus")} | VirtualMachine : {logtext.count("VirtualMachine")}'
                               ])
            Buffout_Trap = True
            statC_Papyrus += 1
        # ===========================================================
        if logtext.count("tbbmalloc.dll") >= 3 or "tbbmalloc" in buff_error:
            output.writelines(["# Checking for Generic Crash................CULPRIT FOUND! #",
                               f'> Priority : [2] | tbbmalloc.dll : {logtext.count("tbbmalloc.dll")}'
                               ])
            Buffout_Trap = True
            statC_Generic += 1
        # ===========================================================
        if "LooseFileAsyncStream" in logtext:
            output.writelines(["# Checking for BA2 Limit Crash..............CULPRIT FOUND! #",
                               f'> Priority : [5] | LooseFileAsyncStream : {logtext.count("LooseFileAsyncStream")}'
                               ])
            Buffout_Trap = True
            statC_BA2Limit += 1
        # ===========================================================
        if logtext.count("d3d11.dll") >= 3 or "d3d11" in buff_error:
            output.writelines(["# Checking for Rendering Crash..............CULPRIT FOUND! #",
                               f'> Priority : [4] | d3d11.dll : {logtext.count("d3d11.dll")}'
                               ])
            Buffout_Trap = True
            statC_Rendering += 1
        # ===========================================================
        if ("GridAdjacencyMapNode" or "PowerUtils") in logtext:
            output.writelines(["# Checking for Grid Scrap Crash.............CULPRIT FOUND! #",
                               f'> Priority : [5] | GridAdjacencyMapNode : {logtext.count("GridAdjacencyMapNode")} | PowerUtils : {logtext.count("PowerUtils")}'
                               ])
            Buffout_Trap = True
            statC_GridScrap += 1
        # ===========================================================
        if ("LooseFileStream" or "BSFadeNode" or "BSMultiBoundNode") in logtext and logtext.count("LooseFileAsyncStream") == 0:
            output.writelines(["# Checking for Mesh (NIF) Crash.............CULPRIT FOUND! #",
                               f'> Priority : [4] | LooseFileStream : {logtext.count("LooseFileStream")} | BSFadeNode : {logtext.count("BSFadeNode")}',
                               f'                   BSMultiBoundNode : {logtext.count("BSMultiBoundNode")}'
                               ])
            Buffout_Trap = True
            statC_NIF += 1
        # ===========================================================
        if ("Create2DTexture" or "DefaultTexture") in logtext:
            output.writelines(["# Checking for Texture (DDS) Crash..........CULPRIT FOUND! #",
                               f'> Priority : [3] | Create2DTexture : {logtext.count("Create2DTexture")} | DefaultTexture : {logtext.count("DefaultTexture")}'
                               ])
            Buffout_Trap = True
            statlogtexture += 1
        # ===========================================================
        if ("DefaultTexture_Black" or "NiAlphaProperty") in logtext:
            output.writelines(["# Checking for Material (BGSM) Crash........CULPRIT FOUND! #",
                               f'> Priority : [3] | DefaultTexture_Black : {logtext.count("DefaultTexture_Black")} | NiAlphaProperty : {logtext.count("NiAlphaProperty")}'
                               ])
            Buffout_Trap = True
            statC_BGSM += 1
        # ===========================================================
        if (logtext.count("bdhkm64.dll") or logtext.count("usvfs::hook_DeleteFileW")) >= 2:
            output.writelines(["# Checking for BitDefender Crash............CULPRIT FOUND! #",
                               f'> Priority : [5] | bdhkm64.dll : {logtext.count("bdhkm64.dll")} | usvfs::hook_DeleteFileW : {logtext.count("usvfs::hook_DeleteFileW")}'
                               ])
            Buffout_Trap = True
            statC_BitDefender += 1
        # ===========================================================
        if ("PathingCell" or "BSPathBuilder" or "PathManagerServer") in logtext:
            output.writelines(["# Checking for NPC Pathing Crash............CULPRIT FOUND! #",
                               f'> Priority : [3] | PathingCell : {logtext.count("PathingCell")} | BSPathBuilder : {logtext.count("BSPathBuilder")}',
                               f'                   PathManagerServer : {logtext.count("PathManagerServer")}'
                               ])
            Buffout_Trap = True
            statC_NPCPathing += 1
        elif ("NavMesh" or "BSNavmeshObstacleData" or "DynamicNavmesh") in logtext:
            output.writelines(["# Checking for NPC Pathing Crash............CULPRIT FOUND! #",
                               f'> Priority : [3] | NavMesh : {logtext.count("NavMesh")} | BSNavmeshObstacleData : {logtext.count("BSNavmeshObstacleData")}',
                               f'                   DynamicNavmesh : {logtext.count("DynamicNavmesh")}'
                               ])
            Buffout_Trap = True
            statC_NPCPathing += 1
        # ===========================================================
        if logtext.count("X3DAudio1_7.dll") >= 3 or logtext.count("XAudio2_7.dll") >= 3 or ("X3DAudio1_7" or "XAudio2_7") in buff_error:
            output.writelines(["# Checking for Audio Driver Crash...........CULPRIT FOUND! #",
                               f'> Priority : [5] | X3DAudio1_7.dll : {logtext.count("X3DAudio1_7.dll")} | XAudio2_7.dll : {logtext.count("XAudio2_7.dll")}'
                               ])
            Buffout_Trap = True
            statC_Audio += 1
        # ===========================================================
        if logtext.count("cbp.dll") >= 3 or "skeleton.nif" in logtext or "cbp.dll" in buff_error:
            output.writelines(["# Checking for Body Physics Crash...........CULPRIT FOUND! #",
                               f'> Priority : [4] | cbp.dll : {logtext.count("cbp.dll")} | skeleton.nif : {logtext.count("skeleton.nif")}'
                               ])
            Buffout_Trap = True
            statC_BodyPhysics += 1
        # ===========================================================
        if ("BSMemStorage" or "DataFileHandleReaderWriter") in logtext:
            output.writelines(["# Checking for Plugin Limit Crash...........CULPRIT FOUND! #",
                               f'> Priority : [5] | BSMemStorage : {logtext.count("BSMemStorage")} | DataFileHandleReaderWriter : {logtext.count("DataFileHandleReaderWriter")}'])
            Buffout_Trap = True
            statC_PluginLimit += 1
        # ===========================================================
        if "GamebryoSequenceGenerator" in logtext or "+0DB9300" in buff_error:
            output.writelines(["# Checking for Plugin Order Crash...........CULPRIT FOUND! #",
                               f'> Priority : [5] | GamebryoSequenceGenerator : {logtext.count("GamebryoSequenceGenerator")}'
                               ])
            Buffout_Trap = True
            statC_LoadOrder += 1
        # ===========================================================
        if logtext.count("BSD3DResourceCreator") == 3 or logtext.count("BSD3DResourceCreator") == 6:
            output.writelines(["# Checking for MO2 Extractor Crash..........CULPRIT FOUND! #",
                               f'> Priority : [5] | BSD3DResourceCreator : {logtext.count("BSD3DResourceCreator")}'
                               ])
            Buffout_Trap = True
            statC_MO2Unp += 1
        # ===========================================================
        if logtext.count("flexRelease_x64.dll") >= 2 or "flexRelease_x64" in buff_error:
            output.writelines(["# Checking for Nvidia Debris Crash..........CULPRIT FOUND! #",
                               f'> Priority : [5] | flexRelease_x64.dll : {logtext.count("flexRelease_x64.dll")}'
                               ])
            Buffout_Trap = True
            statC_NVDebris += 1
        # ===========================================================
        if logtext.count("nvwgf2umx.dll") >= 10 or ("nvwgf2umx" or "USER32.dll") in buff_error:
            output.writelines(["# Checking for Nvidia Driver Crash..........CULPRIT FOUND! #",
                               f'> Priority : [5] | nvwgf2umx.dll : {logtext.count("nvwgf2umx.dll")} | USER32.dll : {logtext.count("USER32.dll")}'
                               ])
            Buffout_Trap = True
            statC_NVDriver += 1
        # ===========================================================
        if (logtext.count("KERNELBASE.dll") or logtext.count("MSVCP140.dll")) >= 3 and "DxvkSubmissionQueue" in logtext:
            output.writelines(["# Checking for Vulkan Memory Crash..........CULPRIT FOUND! #",
                               f'> Priority : [5] | KERNELBASE.dll : {logtext.count("KERNELBASE.dll")} | MSVCP140.dll : {logtext.count("MSVCP140.dll")}',
                               f'                   DxvkSubmissionQueue : {logtext.count("DxvkSubmissionQueue")}'
                               ])
            Buffout_Trap = True
            statC_VulkanMem += 1
        # ===========================================================
        if ("dxvk::DXGIAdapter" or "dxvk::DXGIFactory") in logtext:
            output.writelines(["# Checking for Vulkan Settings Crash........CULPRIT FOUND! #",
                               f'> Priority : [5] | dxvk::DXGIAdapter : {logtext.count("dxvk::DXGIAdapter")} | dxvk::DXGIFactory : {logtext.count("dxvk::DXGIFactory")}'
                               ])
            Buffout_Trap = True
            statC_VulkanSet += 1
        # ===========================================================
        if ("BSXAudio2DataSrc" or "BSXAudio2GameSound") in logtext:
            output.writelines(["# Checking for Corrupted Audio Crash........CULPRIT FOUND! #",
                               f'> Priority : [4] | BSXAudio2DataSrc : {logtext.count("BSXAudio2DataSrc")} | BSXAudio2GameSound : {logtext.count("BSXAudio2GameSound")}'
                               ])
            Buffout_Trap = True
            statC_CorruptedAudio += 1
        # ===========================================================
        if ("SysWindowCompileAndRun" or "ConsoleLogPrinter") in logtext:
            output.writelines(["# Checking for Console Command Crash........CULPRIT FOUND! #",
                               f'> Priority : [1] | SysWindowCompileAndRun : {logtext.count("SysWindowCompileAndRun")} | ConsoleLogPrinter : {logtext.count("ConsoleLogPrinter")}'
                               ])
            Buffout_Trap = True
            statC_ConsoleCommands += 1
        # ===========================================================
        if "BGSWaterCollisionManager" in logtext:
            output.writelines(["# Checking for Water Collision Crash........CULPRIT FOUND! #",
                               "PLEASE CONTACT ME AS SOON AS POSSIBLE! (CONTACT INFO BELOW)",
                               f'> Priority : [6] | BGSWaterCollisionManager : {logtext.count("BGSWaterCollisionManager")}'
                               ])
            Buffout_Trap = True
            statC_Water += 1
        # ===========================================================
        if "ParticleSystem" in logtext:
            output.writelines(["# Checking for Particle Effects Crash.......CULPRIT FOUND! #",
                               f'> Priority : [4] | ParticleSystem : {logtext.count("ParticleSystem")}'
                               ])
            Buffout_Trap = True
            statC_Particles += 1
        # ===========================================================
        if ("hkbVariableBindingSet" or "hkbHandIkControlsModifier" or "hkbBehaviorGraph" or "hkbModifierList") in logtext:
            output.writelines(["# Checking for Animation / Physics Crash....CULPRIT FOUND! #",
                               f'> Priority : [5] | hkbVariableBindingSet : {logtext.count("hkbVariableBindingSet")} | hkbHandIkControlsModifier : {logtext.count("hkbHandIkControlsModifier")}',
                               f'                   hkbBehaviorGraph : {logtext.count("hkbBehaviorGraph")} | hkbModifierList : {logtext.count("hkbModifierList")}'
                               ])
            Buffout_Trap = True
            statC_AnimationPhysics += 1
        # ===========================================================
        if "DLCBanner05.dds" in logtext:
            output.writelines(["# Checking for Archive Invalidation Crash...CULPRIT FOUND! #",
                               f'> Priority : [5] | DLCBanner05.dds : {logtext.count("DLCBanner05.dds")}'
                               ])
            Buffout_Trap = True
            statC_Invalidation += 1

        # ===========================================================
        output.write("---------- Unsolved Crash Messages Below ----------")

        if "+01B59A4" in buff_error:
            output.writelines(["Checking for *[Creation Club Crash].......DETECTED!",
                               "> Priority : [5]"
                               ])
            Buffout_Trap = True
            statU_CClub += 1

        if ("BGSMod::Attachment" or "BGSMod::Template" or "BGSMod::Template::Item") in logtext:
            output.writelines(["Checking for *[Item Crash]................DETECTED!",
                               f'> Priority : [5] | BGSMod::Attachment : {logtext.count("BGSMod::Attachment")} | BGSMod::Template : {logtext.count("BGSMod::Template")}',
                               f'                        BGSMod::Template::Item : {logtext.count("BGSMod::Template::Item")}'
                               ])
            Buffout_Trap = True
            statU_Item += 1
        # ===========================================================
        if logtext.count("BGSSaveFormBuffer") >= 2:
            output.writelines(["Checking for *[Save Crash]................DETECTED!",
                               f'> Priority : [5] | BGSSaveFormBuffer : {logtext.count("BGSSaveFormBuffer")}'
                               ])
            Buffout_Trap = True
            statU_Save += 1
        # ===========================================================
        if ("ButtonEvent" or "MenuControls" or "MenuOpenCloseHandler" or "PlayerControls" or "DXGISwapChain") in logtext:
            output.writelines(["Checking for *[Input Crash]...............DETECTED!",
                               f'> Priority : [5] | ButtonEvent : {logtext.count("ButtonEvent")} | MenuControls : {logtext.count("MenuControls")}',
                               f'                        MenuOpenCloseHandler : {logtext.count("MenuOpenCloseHandler")} | PlayerControls : {logtext.count("PlayerControls")}',
                               f'                        DXGISwapChain : {logtext.count("DXGISwapChain")}'
                               ])
            Buffout_Trap = True
            statU_Input += 1
        # ===========================================================
        if ("BGSSaveLoadManager" or "BGSSaveLoadThread" or "BGSSaveFormBuffer") in logtext or ("+0CDAD30" or "+0D09AB7") in buff_error:
            output.writelines(["Checking for *[Bad INI Crash].............DETECTED!",
                               f'> Priority : [5] | BGSSaveLoadManager : {logtext.count("BGSSaveLoadManager")} | BGSSaveLoadThread : {logtext.count("BGSSaveLoadThread")}',
                               f'                        BGSSaveFormBuffer : {logtext.count("BGSSaveFormBuffer")}'
                               ])
            Buffout_Trap = True
            statU_INI += 1
        # ===========================================================
        if ("BGSProcedurePatrol" or "BGSProcedurePatrolExecState" or "PatrolActorPackageData") in logtext:
            output.writelines(["Checking for *[NPC Patrol Crash]..........DETECTED!",
                               f'> Priority : [5] | BGSProcedurePatrol : {logtext.count("BGSProcedurePatrol")} | BGSProcedurePatrolExecStatel : {logtext.count("BGSProcedurePatrolExecState")}',
                               f'                        PatrolActorPackageData : {logtext.count("PatrolActorPackageData")}'
                               ])
            Buffout_Trap = True
            statU_Patrol += 1
        # ===========================================================
        if ("BSPackedCombinedGeomDataExtra" or "BGSCombinedCellGeometryDB" or "BGSStaticCollection" or "TESObjectCELL") in logtext:
            output.writelines(["Checking for *[Precombines Crash].........DETECTED!",
                               f'> Priority : [5] | BGSStaticCollection : {logtext.count("BGSStaticCollection")} | BGSCombinedCellGeometryDB : {logtext.count("BGSCombinedCellGeometryDB")}',
                               f'                        BSPackedCombinedGeomDataExtra : {logtext.count("BSPackedCombinedGeomDataExtra")} | TESObjectCELL : {logtext.count("TESObjectCELL")}'
                               ])
            Buffout_Trap = True
            statU_Precomb += 1
        # ===========================================================
        if "HUDAmmoCounter" in logtext:
            output.writelines(["Checking for *[Ammo Counter Crash]........DETECTED!",
                               f'> Priority : [5] | HUDAmmoCounter : {logtext.count("HUDAmmoCounter")}'
                               ])
            Buffout_Trap = True
            statU_HUDAmmo += 1
        # ===========================================================
        if ("BGSProjectile" or "CombatProjectileAimController") in logtext:
            output.writelines(["Checking for *[NPC Projectile Crash].....DETECTED!",
                               f'> Priority : [5] | BGSProjectile : {logtext.count("BGSProjectile")} | CombatProjectileAimController : {logtext.count("CombatProjectileAimController")}'
                               ])
            Buffout_Trap = True
        # ===========================================================
        if logtext.count("PlayerCharacter") >= 1 and (logtext.count("0x00000007") or logtext.count("0x00000014") or logtext.count("0x00000008")) >= 3:
            output.write("Checking for *[Player Character Crash]....DETECTED!")
            output.write(f'> Priority : [5] | PlayerCharacter : {logtext.count("PlayerCharacter")} | 0x00000007 : {logtext.count("0x00000007")}')
            output.write(f'                        0x00000008 : {logtext.count("0x00000008")} | 0x000000014 : {logtext.count("0x00000014")}')
            output.writelines(["Checking for *[Player Character Crash]....DETECTED!",
                               f'> Priority : [5] | PlayerCharacter : {logtext.count("PlayerCharacter")} | 0x00000007 : {logtext.count("0x00000007")}',
                               f'                        0x00000008 : {logtext.count("0x00000008")} | 0x000000014 : {logtext.count("0x00000014")}'
                               ])
            Buffout_Trap = True
            statU_Player += 1

        # ===========================================================

        if Buffout_Trap == False:  # DEFINE CHECK IF NOTHING TRIGGERED BUFFOUT TRAP
            output.writelines([
                "-----",
                "# AUTOSCAN FOUND NO CRASH ERRORS / CULPRITS THAT MATCH THE CURRENT DATABASE #",
                "Check below for mods that can cause frequent crashes and other problems.",
                "-----"
            ])
        else:
            output.writelines([
                "-----",
                "FOR DETAILED DESCRIPTIONS AND POSSIBLE SOLUTIONS TO ANY ABOVE DETECTED CRASH CULPRITS,",
                "SEE: https://docs.google.com/document/d/17FzeIMJ256xE85XdjoPvv_Zi3C5uHeSTQh6wOZugs4c",
                "-----"
            ])

        output.writelines([
            "====================================================",
            "CHECKING FOR MODS THAT CAN CAUSE FREQUENT CRASHES...",
            "===================================================="
        ])
        Mod_Trap1 = 1

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
                      " True Nights v03.esp",
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
                      "- Can sometimes cause Deathclaw / Behmoth boulder projectile crashes for unknown reasons.",

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

        if "[00]" in logtext:
            for line in plugin_list:
                for elem in List_Mods1:
                    if "File:" not in line and "[FE" not in line and elem in line:
                        order_elem = List_Mods1.index(elem)
                        output.writelines([f"[!] Found:{line[0:5].strip()} {List_Warn1[order_elem]}",
                                           "-----"])
                        Mod_Trap1 = 0
                    elif "File:" not in line and "[FE" in line and elem in line:
                        order_elem = List_Mods1.index(elem)
                        output.writelines([f"[!] Found:{line[0:9].strip()} {List_Warn1[order_elem]}",
                                           "-----"])
                        Mod_Trap1 = 0

            if logtext.count("ClassicHolsteredWeapons") >= 3 or "ClassicHolsteredWeapons" in buff_error:
                output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS",
                                   "AUTOSCAN IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!",
                                   "You should disable CHW to further confirm this.",
                                   "Visit the main crash logs article for additional solutions.",
                                   "-----"
                                   ])
                statM_CHW += 1
                Mod_Trap1 = 0
                Buffout_Trap = True
            elif logtext.count("ClassicHolsteredWeapons") >= 2 and ("UniquePlayer.esp" or "HHS.dll" or "cbp.dll" or "Body.nif") in logtext:
                output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS",
                                   "AUTOSCAN ALSO DETECTED ONE OR SEVERAL MODS THAT WILL CRASH WITH CHW.",
                                   "You should disable CHW to further confirm it caused this crash.",
                                   "Visit the main crash logs article for additional solutions.",
                                   "-----"
                                   ])
                statM_CHW += 1
                Mod_Trap1 = 0
                Buffout_Trap = True
            elif "ClassicHolsteredWeapons" in logtext and "d3d11" in buff_error:
                output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS, BUT...",
                                   "AUTOSCAN CANNOT ACCURATELY DETERMINE IF CHW CAUSED THIS CRASH OR NOT.",
                                   "You should open CHW's ini file and change IsHolsterVisibleOnNPCs to 0.",
                                   "This usually prevents most common crashes with Classic Holstered Weapons.",
                                   "-----"
                                   ])
                Mod_Trap1 = 0
        if "[00]" in logtext and Mod_Trap1 == 0:
            output.writelines(["# CAUTION: ANY ABOVE DETECTED MODS HAVE A MUCH HIGHER CHANCE TO CRASH YOUR GAME! #",
                               "You can disable any/all of them temporarily to confirm they caused this crash.",
                               "-----"
                               ])
            statL_scanned += 1
        elif "[00]" in logtext and Mod_Trap1 == 1:
            output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT MATCH THE CURRENT DATABASE FOR THIS LOG #",
                               "THAT DOESN'T MEAN THERE AREN'T ANY! YOU SHOULD RUN PLUGIN CHECKER IN WRYE BASH.",
                               "Wrye Bash Link: https://www.nexusmods.com/fallout4/mods/20032?tab=files",
                               "-----"
                               ])
            statL_scanned += 1
        elif not "[00]" in logtext:
            output.writelines(["# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #\n",
                               "Autoscan cannot continue. Try scanning a different crash log.\n",
                               "-----"
                               ])
            statL_incomplete += 1

        output.writelines(["====================================================",
                           "CHECKING FOR MODS WITH SOLUTIONS & COMMUNITY PATCHES",
                           "===================================================="
                           ])
        Mod_Trap2 = no_repeat1 = no_repeat2 = 1  # MOD TRAP 2 | NEED 8 SPACES FOR ESL [FE:XXX]

        # Needs 1 empty space as prefix to prevent duplicates.
        List_Mods2 = [" DLCUltraHighResolution.esm",
                      " AAF.esm",
                      " ArmorKeywords.esm",
                      " BTInteriors_Project.esp",
                      " CombatZoneRestored.esp",
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
                      " LooksMenu Customization Compendium.esp",
                      " MilitarizedMinutemen.esp",
                      " MoreUniques",
                      " NAC.es",
                      " Northland Diggers New.esp",
                      " ProjectZeta.esm",
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
                      "LOOKS MENU CUSTOMIZATION COMPENDIUM \n"
                      "Apparently breaks the original Looks Menu mod by turning off some important values. \n"
                      "Fix Link: https://www.nexusmods.com/fallout4/mods/56465?tab=files",
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
                      "PROJECT ZETA \n"
                      "Invasion quests seem overly buggy or trigger too frequently, minor sound issues. \n"
                      "Fix Link: https://www.nexusmods.com/fallout4/mods/65166?tab=files",
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

        if "[00]" in logtext:
            for line in plugin_list:
                for elem in List_Mods2:
                    if "File:" not in line and "[FE" not in line and elem in line:
                        order_elem = List_Mods2.index(elem)
                        output.writelines([f"[!] Found:{line[0:5].strip()} {List_Warn2[order_elem]}",
                                           "-----"
                                           ])
                        Mod_Trap2 = 0
                    elif "File:" not in line and "[FE" in line and elem in line:
                        order_elem = List_Mods2.index(elem)
                        output.writelines([f"[!] Found:{line[0:9].strip()} {List_Warn2[order_elem]}",
                                           "-----"
                                           ])
                        Mod_Trap2 = 0
                if no_repeat1 == 1 and "File:" not in line and ("Depravity" or "FusionCityRising" or "HotC" or "OutcastsAndRemnants" or "ProjectValkyrie") in line:
                    output.writelines([f"[!] Found:{line[0:9].strip()} THUGGYSMURF QUEST MOD",
                                       "If you have Depravity, Fusion City Rising, HOTC, Outcasts and Remnants and/or Project Valkyrie",
                                       "install this patch with facegen data, fully generated precomb/previs data and several tweaks.",
                                       "Patch Link: https://www.nexusmods.com/fallout4/mods/56876?tab=files",
                                       "-----"
                                       ])
                    no_repeat1 = Mod_Trap2 = 0
                if no_repeat1 == 1 and "File:" not in line and ("CaN.esm" or "AnimeRace_Nanako.esp") in line:
                    output.writelines([f"[!] Found:{line[0:9].strip()} CUSTOM RACE SKELETON MOD",
                                       "If you have AnimeRace NanakoChan or Crimes Against Nature, install the Race Skeleton Fixes.",
                                       "Skeleton Fixes Link (READ THE DESCRIPTION): https://www.nexusmods.com/fallout4/mods/56101"
                                       ])
                    no_repeat2 = Mod_Trap2 = 0

            if "FallSouls.dll" in logtext:
                output.writelines(["[!] Found: FALLSOULS UNPAUSED GAME MENUS",
                                   "Occasionally breaks the Quests menu, can cause crashes while changing MCM settings.",
                                   "Advised Fix: Toggle PipboyMenu in FallSouls MCM settings or completely reinstall the mod.",
                                   "-----"
                                   ])
                Mod_Trap2 = 0

        # inherentlimitations= "[Due to inherent limitations, Auto-Scan will continue detecting certain mods\neven if fixes or patches for them are already installed. You can ignore these.]\n-----"

        nopluginlist = "# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #\nAutoscan cannot continue. Try scanning a different crash log.\n-----"
        if "[00]" in logtext and Mod_Trap2 == 0:
            output.write("[Due to inherent limitations, Auto-Scan will continue detecting certain mods")
            output.write("even if fixes or patches for them are already installed. You can ignore these.]")
            output.write("-----")

        elif "[00]" in logtext and Mod_Trap2 == 1:
            output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #",
                               "-----"
                               ])
        elif logtext.count("[00]") == 0:
            output.write(nopluginlist)

        output.writelines(["FOR FULL LIST OF IMPORTANT PATCHES AND FIXES FOR THE BASE GAME AND MODS,",
                           "VISIT THIS ARTICLE: https://www.nexusmods.com/fallout4/articles/3769",
                           "-----"
                           ])

        output.writelines(["====================================================",
                           "CHECKING FOR MODS PATCHED THROUGH OPC INSTALLER...",
                           "===================================================="
                           ])
        Mod_Trap3 = 1  # MOD TRAP 3 | NEED 8 SPACES FOR ESL [FE:XXX]

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

        if "[00]" in logtext:
            for line in plugin_list:
                for elem in List_Mods3:
                    if "File:" not in line and "[FE" not in line and elem in line:
                        order_elem = List_Mods3.index(elem)
                        output.write(f"- Found:{line[0:5].strip()} {List_Warn3[order_elem]}")
                        Mod_Trap3 = 0
                    elif "File:" not in line and "[FE" in line and elem in line:
                        order_elem = List_Mods3.index(elem)
                        output.write(f"- Found:{line[0:9].strip()} {List_Warn3[order_elem]}")
                        Mod_Trap3 = 0
        if "[00]" in logtext and Mod_Trap3 == 0:
            output.writelines(["-----",
                               "FOR PATCH REPOSITORY THAT PREVENTS CRASHES AND FIXES PROBLEMS IN THESE AND OTHER MODS,",
                               "VISIT OPTIMIZATION PATCHES COLLECTION: https://www.nexusmods.com/fallout4/mods/54872",
                               "-----"
                               ])
        elif "[00]" in logtext and Mod_Trap3 == 1:
            output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT ARE ALREADY PATCHED THROUGH OPC INSTALLER #",
                               "-----"
                               ])
        elif logtext.count("[00]") == 0:
            output.writelines(nopluginlist)

        # ===========================================================

        output.writelines(["====================================================",
                           "CHECKING IF IMPORTANT PATCHES & FIXES ARE INSTALLED"
                           "===================================================="
                           ])

        gpu_amd = False
        gpu_nvidia = False
        for line in loglines:
            if "GPU" in line and "Nvidia" in line:
                gpu_nvidia = True
            if "GPU" in line and "AMD" in line:
                gpu_amd = True

        output.writelines(["IF YOU'RE USING DYNAMIC PERFORMANCE TUNER AND/OR LOAD ACCELERATOR,",
                           "remove these mods completely and switch to High FPS Physics Fix!",
                           "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files",
                           "-----"
                           ])

        if CLAS_config.getboolean("MAIN", "FCX Mode") == True:
            output.writelines(["* NOTICE: FCX MODE IS ENABLED. AUTO-SCANNER MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *",
                               "[ To disable game folder / mod files detection, set FCX Mode = false in Scan Crashlogs.ini ]",
                               "-----"
                               ])

            if info.VR_EXE.is_file() and info.VR_Buffout.is_file():
                output.write("*Buffout 4 VR Version* is (manually) installed. \n-----")
            elif info.VR_EXE.is_file() and not info.VR_Buffout.is_file():
                output.writelines(["# BUFFOUT 4 FOR VR VERSION ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "# This is a mandatory Buffout 4 port for the VR Version of Fallout 4.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/64880?tab=files"
                                   ])

            if info.F4CK_EXE.is_file() and os.path.exists(info.F4CK_Fixes):
                output.write("*Creation Kit Fixes* is (manually) installed. \n-----")
            elif info.F4CK_EXE.is_file() and not os.path.exists(info.F4CK_Fixes):
                output.writelines(["# CREATION KIT FIXES ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a highly recommended patch for the Fallout 4 Creation Kit.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/51165?tab=files",
                                   "-----"
                                   ])

        if "[00]" in logtext:
            if any("CanarySaveFileMonitor" in elem for elem in plugin_list):
                output.write("*Canary Save File Monitor* is installed. \n-----")
            else:
                output.writelines(["# CANARY SAVE FILE MONITOR ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a highly recommended mod that can detect save file corrpution.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/44949?tab=files",
                                   "-----"
                                   ])

            if "HighFPSPhysicsFix.dll" in logtext:
                output.write("*High FPS Physics Fix* is installed. \n-----")
            else:
                output.writelines(["# HIGH FPS PHYSICS FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a mandatory patch / fix that prevents game engine problems.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files",
                                   "-----"
                                   ])

            if any("PPF.esm" in elem for elem in plugin_list):
                output.write("*Previs Repair Pack* is installed. \n-----")
            else:
                output.writelines(["# PREVIS REPAIR PACK ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a highly recommended mod that can improve performance.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files",
                                   "-----"
                                   ])

            if any("Unofficial Fallout 4 Patch.esp" in elem for elem in plugin_list):
                output.write("*Unofficial Fallout 4 Patch* is installed. \n-----")
            else:
                output.writelines(["# UNOFFICIAL FALLOUT 4 PATCH ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "If you own all DLCs, make sure that the Unofficial Patch is installed.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/4598?tab=files",
                                   "-----"
                                   ])

            if "vulkan-1.dll" in logtext and gpu_amd:
                output.write("Vulkan Renderer is installed. \n-----")
            elif logtext.count("vulkan-1.dll") == 0 and gpu_amd and not gpu_nvidia:
                output.writelines(["# VULKAN RENDERER ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a highly recommended mod that can improve performance on AMD GPUs.",
                                   "-----",
                                   "Installation steps can be found in 'How To Read Crash Logs' PDF / Document.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/48053?tab=files",
                                   "-----"
                                   ])

            if "WeaponDebrisCrashFix.dll" in logtext and gpu_nvidia:
                output.write("*Weapon Debris Crash Fix* is installed. \n-----")
            elif "WeaponDebrisCrashFix.dll" in logtext and not gpu_nvidia and gpu_amd:
                output.writelines(["*Weapon Debris Crash Fix* is installed, but...",
                                   "# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #",
                                   "Weapon Debris Crash Fix is only required for Nvidia GPUs (NOT AMD / OTHER)",
                                   "-----"
                                   ])
            if not "WeaponDebrisCrashFix.dll" in logtext and gpu_nvidia:
                output.writelines(["# WEAPON DEBRIS CRASH FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a mandatory patch / fix for players with Nvidia graphics cards.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/48078?tab=files",
                                   "-----"
                                   ])

            if "NVIDIA_Reflex.dll" in logtext and gpu_nvidia:
                output.write("*Nvidia Reflex Support* is installed. \n-----")
            elif "NVIDIA_Reflex.dll" in logtext and not gpu_nvidia and gpu_amd:
                output.writelines(["*Nvidia Reflex Support* is installed, but...",
                                   "# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #",
                                   "Nvidia Reflex Support is only required for Nvidia GPUs (NOT AMD / OTHER)",
                                   "-----"
                                   ])
            if not "NVIDIA_Reflex.dll" in logtext and gpu_nvidia:
                output.writelines(["# NVIDIA REFLEX SUPPORT ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                   "This is a highly recommended mod that can reduce render latency.",
                                   "Link: https://www.nexusmods.com/fallout4/mods/64459?tab=files",
                                   "-----"
                                   ])
        else:
            output.writelines(nopluginlist)
        output.writelines(["====================================================",
                           "SCANNING THE LOG FOR SPECIFIC (POSSIBLE) CUPLRITS...",
                           "===================================================="
                           ])

        list_DETPLUGINS = []
        list_DETFORMIDS = []
        list_DETFILES = []
        list_ALLPLUGINS = []

        if not "f4se_1_10_163.dll" in logtext and "steam_api64.dll" in logtext:
            output.writelines(["AUTOSCAN CANNOT FIND FALLOUT 4 SCRIPT EXTENDER DLL!",
                               "MAKE SURE THAT F4SE IS CORRECTLY INSTALLED!",
                               "Link: https://f4se.silverlock.org",
                               "-----"
                               ])

        for line in loglines:
            if len(line) >= 6 and "]" in line[4]:
                list_ALLPLUGINS.append(line.strip())
            if len(line) >= 7 and "]" in line[5]:
                list_ALLPLUGINS.append(line.strip())
            if len(line) >= 10 and "]" in line[8]:
                list_ALLPLUGINS.append(line.strip())
            if len(line) >= 11 and "]" in line[9]:
                list_ALLPLUGINS.append(line.strip())

        output.write("LIST OF (POSSIBLE) PLUGIN CULRIPTS:")
        for line in loglines:
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
                output.write(f"- {' '.join(PL_matches)}")  # not 100% sure on this, will have to see how it works.

        if not PL_result:
            output.writelines(["* AUTOSCAN COULDN'T FIND ANY PLUGIN CULRIPTS *",
                               "-----"
                               ])
        else:
            output.writelines(["-----",
                               "These Plugins were caught by Buffout 4 and some of them might be responsible for this crash.",
                               "You can try disabling these plugins and recheck your game, though this method can be unreliable.",
                               "-----"
                               ])

        # ===========================================================

        output.write("LIST OF (POSSIBLE) FORM ID CULRIPTS:")
        for line in loglines:
            if "Form ID:" in line and not "0xFF" in line:
                line = line.replace("0x", "")
                if "[00]" in logtext:
                    line = line.replace("Form ID: ", "")
                    line = line.strip()
                    ID_Only = line
                    for elem in plugin_list:
                        if "]" in elem and "[FE" not in elem:
                            if elem[2:4].strip() == ID_Only[:2]:
                                Full_Line = "Form ID: " + ID_Only + " | " + elem.strip()
                                list_DETFORMIDS.append(Full_Line.replace("    ", ""))
                        if "[FE" in elem:
                            elem = elem.replace(":", "")
                            if elem[2:7] == ID_Only[:5]:
                                Full_Line = "Form ID: " + ID_Only + " | " + elem.strip()
                                list_DETFORMIDS.append(Full_Line.replace("    ", ""))
                else:
                    list_DETFORMIDS.append(line.strip())

            list_DETFORMIDS = list(dict.fromkeys(list_DETFORMIDS))
            for elem in list_DETFORMIDS:
                output.write(elem)

            if not list_DETFORMIDS:
                output.writelines(["* AUTOSCAN COULDN'T FIND ANY FORM ID CULRIPTS *",
                                   "-----"
                                   ])
        else:
            output.writelines(["-----",
                               "These Form IDs were caught by Buffout 4 and some of them might be related to this crash.",
                               "You can try searching any listed Form IDs in FO4Edit and see if they lead to relevant records.",
                               "-----"
                               ])

        # ===========================================================

        List_Files = [".bgsm", ".bto", ".btr", ".dds", ".fuz", ".hkb", ".hkx", ".ini", ".nif", ".pex", ".swf", ".txt", ".uvd", ".wav", ".xwm", "data\\*"]
        List_Exclude = ['""', "...", ".esp"]

        output.write("LIST OF DETECTED (NAMED) RECORDS:")
        List_Records = []
        for line in loglines:
            if "Name" in line or any(elem in line for elem in List_Files):
                if not any(elem in line for elem in List_Exclude):
                    line = line.replace('"', '')
                    List_Records.append(line.strip())

        List_Records = list(dict.fromkeys(List_Records))
        for elem in List_Records:
            output.write(elem)

        if not List_Records:
            output.writelines(["* AUTOSCAN COULDN'T FIND ANY NAMED RECORDS *",
                               "-----"
                               ])
        else:
            output.writelines(["-----",
                               "These records were caught by Buffout 4 and some of them might be related to this crash.",
                               "Named records should give extra information on involved game objects and record types.",
                               "-----"
                               ])

        output.writelines(["FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,",
                           "VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115",
                           "===============================================================================",
                           f"END OF AUTOSCAN | Author/Made By: Poet#9800 (DISCORD) | {CLAS_Date}"
                           ])

    # MOVE UNSOLVED LOGS TO SPECIAL FOLDER
    if CLAS_config.getboolean("MAIN", "Move Unsolved") == True:
        if not os.path.exists("CLAS-UNSOLVED"):
            os.mkdir("CLAS-UNSOLVED")
        if int(Buffout_Trap) == 1:
            uCRASH_path = "CLAS-UNSOLVED/" + logname
            shutil.move(logname, uCRASH_path)
            uSCAN_path = "CLAS-UNSOLVED/" + logname + "-AUTOSCAN.md"
            shutil.move(logname + "-AUTOSCAN.md", uSCAN_path)

# dict.fromkeys -> Create dictionary, removes duplicates as dicts cannot have them.
# BUFFOUT.INI BACK TO BUFFOUT.TOML BECAUSE PYTHON CAN'T WRITE
if info.Buffout_INI.is_file():
    try:
        os.rename(info.Buffout_INI, info.Buffout_TOML)
    except FileExistsError:
        os.remove(info.Buffout_TOML)
        os.rename(info.Buffout_INI, info.Buffout_TOML)

# ========================== LOG END ==========================
print("SCAN COMPLETE! (IT MIGHT TAKE SEVERAL SECONDS FOR SCAN RESULTS TO APPEAR)")
print("SCAN RESULTS ARE AVAILABE IN FILES NAMED crash-date-and-time-AUTOSCAN.md")
print("===============================================================================")
print("FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,")
print("VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115")
print("================================ CONTACT INFO =================================")
print("DISCORD | Poet#9800 (https://discord.gg/DfFYJtt8p4)")
print("NEXUS MODS | https://www.nexusmods.com/users/64682231")
print("SCAN SCRIPT PAGE | https://www.nexusmods.com/fallout4/mods/56255")
print(random.choice(Sneaky_Tips))

# ============ CHECK FOR EMPTY (FAUTLY) AUTO-SCANS ============
list_SCANFAIL = []
for file in glob("*-AUTOSCAN.md"):
    line_count = 0
    scanname = str(file)
    with open(file, errors="ignore") as autoscan_log:
        for line in autoscan_log:
            if line != "\n":
                line_count += 1
    if int(line_count) <= 10:
        list_SCANFAIL.append(scanname.replace("-AUTOSCAN.md", ".log"))
        statL_failed += 1

if len(list_SCANFAIL) >= 1:
    print("NOTICE: AUTOSCANNER WAS UNABLE TO PROPERLY SCAN THE FOLLOWING LOG(S): ")
    for elem in list_SCANFAIL:
        print(elem)
    print("===============================================================================")
    print("To troubleshoot this, right click on Scan Crashlogs.py and select option 'Edit With IDLE'")
    print("Once it opens the code, press [F5] to run the script. Any error messages will appear in red.")
    print("-----")
    print('If any given error contains "codec cant decode byte", you can fix this in two ways:')
    print('1.] Move all crash logs and the scan script into a folder with short and simple path name, example: "C:\\Crash Logs"')
    print("-----")
    print('2.] Open the original crash log with Notepad, select File > Save As... and make sure that Encoding is set to UTF-8,')
    print('then press Save and overwrite the original crash log file. Run the Scan Crashlogs script again after that.')
    print("-----")
    print('FOR ALL OTHER ERRORS PLEASE CONTACT ME DIRECTLY, CONTACT INFO BELOW!')

print("======================================================================")
print("\nScanned all available logs in", (str(time.time() - start_time)[:7]), "seconds.")
print("Number of Scanned Logs (No Autoscan Errors): ", statL_scanned)
print("Number of Incomplete Logs (No Plugins List): ", statL_incomplete)
print("Number of Failed Logs (Autoscan Can't Scan): ", statL_failed)
print("Number of Very Old / Wrong Formatting Logs : ", statL_veryold)
print("(Set Stat Logging to true in Scan Crashlogs.ini for additional stats.)")
print("-----")
if CLAS_config.getboolean("MAIN", "Stat Logging") == True:
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
    print("Logs with Texture (DDS) Crash............", statlogtexture)
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
