import os
import sys
import stat
import time
import shutil
import random
import platform
import subprocess
import configparser
from glob import glob
from pathlib import Path
from collections import Counter
try:
    import requests
except Exception:
    subprocess.run(['pip', 'install', 'requests'], shell=True)

if platform.system() == "Windows":
    import ctypes.wintypes


def createlistbetweentextheaders(source, start, end=""):  # This function partially brought to you by Github Copilot (been trying to figure out how to do this for a while)
    """Returns a list of lines between two text headers."""
    if not isinstance(source, list):
        raise TypeError("Source must be a list.")

    if not isinstance(start, str):
        raise TypeError("Start must be a string.")

    if not isinstance(end, str):
        raise TypeError("End must be a string.")

    if len(end) < 1:
        end = None

    for elem in source:
        if not isinstance(elem, str):
            raise TypeError("Source list must contain only strings.")

        source[source.index(elem)] = elem.strip()

    output = []
    if len(source) > 1:
        start_index = source.index(start)
        end_index = 0

        if end:
            end_index = source.index(end)
            output = source[start_index + 1: end_index]
        else:
            output = source[start_index + 1:]

    while "" in output:
        output.remove("")

    return output


if not os.path.exists("Scan Crashlogs.ini"):  # INI FILE FOR AUTO-SCANNER
    INI_Settings = ["[MAIN]\n",
                    "# This file contains configuration settings for both Scan_Crashlogs.py and Crash Log Auto Scanner.exe \n",
                    "# Set to true if you want Auto-Scanner to check Python modules and if the latest vesion is installed. \n",
                    "Update Check = true\n\n",
                    "# FCX - File Check eXtended | If Auto-Scanner fails to scan your logs, revert this setting back to false. \n",
                    "# Set to true if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly. \n",
                    "FCX Mode = true\n\n",
                    "# IMI - Ignore Manual Installaton | Set to true if you want Auto-Scanner to hide all manual installation warnings. \n",
                    "# I still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager. \n",
                    "IMI Mode = false\n\n",
                    "# Set to true if you want Auto-Scanner to show extra stats about scanned logs in the command line window. \n",
                    "Stat Logging = false\n\n",
                    "# Set to true if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder. \n",
                    "# Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages. \n",
                    "Move Unsolved = false\n\n",
                    "# Set or copy-paste your INI directory path below. Example: INI Path = C:/Users/Zen/Documents/My Games/Fallout4 \n",
                    "# Only required if Profile Specific INIs are enabled in MO2 or you moved your Documents folder somewhere else. \n",
                    "# I highly recommend that you disable Profile Specific Game INI Files in MO2, located in Tools > Profiles... \n",
                    "INI Path = \n\n",
                    "# Set or copy-paste your custom scan folder path below, from which your crash logs will be scanned. \n",
                    "# If no path is set, Auto-Scanner will search for logs in the same folder you're running it from. \n",
                    "Scan Path = "]
    with open("Scan Crashlogs.ini", "w+", encoding="utf-8", errors="ignore") as INI_Autoscan:
        INI_Autoscan.writelines(INI_Settings)

# Use optionxform = str to preserve INI formatting. | Set comment_prefixes to unused char to keep INI comments.
CLAS_config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="$")
CLAS_config.optionxform = str  # type: ignore
CLAS_config.read("Scan Crashlogs.ini")
CLAS_Date = "250123"  # DDMMYY
CLAS_Current = "CLAS v6.06"
CLAS_Updated = False


def write_ini_value_to_file(section: str, value: str):  # Convenience function for a code snippet that's repeated many times throughout both scripts.
    if isinstance(section, str) and isinstance(value, str):
        CLAS_config.set("MAIN", section, value)
    else:
        CLAS_config.set("MAIN", str(section), str(value))

    with open("Scan Crashlogs.ini", "w+", encoding="utf-8", errors="ignore") as INI_Autoscan:
        CLAS_config.write(INI_Autoscan)


def run_update():
    global CLAS_Current
    global CLAS_Updated
    global Py_Updated
    print("CHECKING YOUR PYTHON VERSION & CRASH LOG AUTO SCANNER UPDATES...")
    print("(You can disable this check in the EXE or Scan Crashlogs.ini) \n")
    print(f"Installed Python Version: {sys.version[:6]} \n")
    if sys.version[:4] not in ["3.11", "3.10", "3.9.", "3.8."]:
        print("WARNING: YOUR PYTHON VERSION IS OUT OF DATE! PLEASE UPDATE PYTHON.")
        print("FOR LINUX / WIN 10 / WIN 11: https://www.python.org/downloads")
        print("FOR WINDOWS 7: https://github.com/adang1345/PythonWin7")
    else:
        response = requests.get("https://api.github.com/repos/GuidanceOfGrace/Buffout4-CLAS/releases/latest")  # type: ignore
        CLAS_Received = response.json()["name"]
        if CLAS_Received == CLAS_Current:
            CLAS_Updated = True
            print("You have the latest version of the Auto-Scanner!")
        else:
            print("\n [!] YOUR AUTO-SCANNER VERSION IS OUT OF DATE \n Please download the latest version from here: \n https://www.nexusmods.com/fallout4/mods/56255 \n")
            print("===============================================================================")
    return CLAS_Updated


if CLAS_config.getboolean("MAIN", "Update Check") is True:
    try:
        import requests
        CLAS_CheckUpdates = run_update()
    except (ImportError, ModuleNotFoundError) as exc:
        subprocess.run(['pip', 'install', 'requests'], shell=True)
        import requests
        CLAS_CheckUpdates = run_update()
    except Exception:
        print("AN ERROR OCCURRED! THE SCRIPT WAS UNABLE TO CHECK FOR UPDATES, BUT WILL CONTINUE SCANNING.")
        print("CHECK FOR ANY AUTO-SCANNER UPDATES HERE: https://www.nexusmods.com/fallout4/mods/56255")
        print("MAKE SURE YOU HAVE THE LATEST VERSION OF PYTHON 3: https://www.python.org/downloads")
        print("===============================================================================")
elif CLAS_config.getboolean("MAIN", "Update Check") is False:
    print("\n NOTICE: UPDATE CHECK IS DISABLED IN CLAS INI SETTINGS \n")

Sneaky_Tips = ["\nRandom Hint: [Ctrl] + [F] is a handy-dandy key combination. You should use it more often. Please.\n",
               "\nRandom Hint: Patrolling the Buffout 4 Nexus Page almost makes you wish this joke was more overused.\n",
               "\nRandom Hint: You have a crash log where Autoscanner couldn't find anything? Feel free to send it to me.\n",
               "\nRandom Hint: 20% of all crashes are caused by Classic Holstered Weapons mod. 80% of all statistics are made up.\n",
               "\nRandom Hint: No, I don't know why your game froze instead of crashed. But I know someone who might know; Google.\n",
               "\nRandom Hint: Spending 5 morbillion hours asking for help can save you from 5 minutes of reading the documentation.\n",
               "\nRandom Hint: When necessary, make sure that crashes are consistent or repeatable, since in rare cases they aren't.\n",
               "\nRandom Hint: When posting crash logs, it's helpful to mention the last thing you were doing before the crash happened.\n",
               "\nRandom Hint: Be sure to revisit both Buffout 4 Crash Crticle and Auto-Scanner Nexus Page from time to time for updates.\n"]

print("Hello World! | Crash Log Auto-Scanner | Version", CLAS_Current[-4:], "| Fallout 4")
print("CRASH LOGS MUST BE .log AND IN THE SAME FOLDER WITH THIS SCRIPT!")
print("===============================================================================")
print("You should place this script into your Documents/My Games/Fallout4/F4SE folder.")
print("(This is where Buffout 4 crash log files are generated after the game crashes.)")
print("===============================================================================")
print("WARNING: Crash Log Auto-Scanner will not work correctly on Windows 7 systems.")
print("For Win 7, install this Py version: https://github.com/adang1345/PythonWin7")
print("Click on the green Code button and Download Zip, then extract and install.")
print("===============================================================================")
Start_Time = time.perf_counter()


def scan_logs():
    print("\n PERFORMING SCAN... \n")
    global Sneaky_Tips
    global Start_Time

    # =================== STATISTICS LOGGING ===================
    # MAIN STATS
    statL_scanned = statL_incomplete = statL_failed = statL_veryold = 0
    # KNOWN CRASH MESSAGES
    statC_ActiveEffect = statC_AnimationPhysics = statC_Audio = statC_BA2Limit = statC_BGSM = statC_BitDefender = statC_BodyPhysics = statC_ConsoleCommands = statC_CorruptedTex = 0
    statC_DLL = statC_Equip = statC_Generic = statC_GridScrap = statC_Invalidation = statC_LoadOrder = statC_MCM = statC_BadMath = statC_NIF = statC_NPCPathing = statC_NVDebris = 0
    statC_NVDriver = statC_Null = statC_Overflow = statC_Papyrus = statC_Particles = statC_PluginLimit = statC_Rendering = statC_Texture = statC_CorruptedAudio = statC_LOD = 0
    statC_MapMarker = statC_Redist = statC_Decal = statC_MO2Unpack = statC_VulkanMem = statC_VulkanSet = statC_Water = statC_Precomb = statC_Player = statC_GameCorruption = 0
    statC_LeveledList = 0
    # UNSOLVED CRASH MESSAGES
    statU_Save = statU_HUDAmmo = statU_Patrol = statU_Projectile = statU_Item = statU_Input = statU_CClub = statU_LooksMenu = 0
    # KNOWN CRASH CONDITIONS
    statM_CHW = 0

    class Info:
        def __init__(self):
            self.VR_EXE: Path | None = None
            self.VR_Buffout: Path | None = None
            self.F4CK_EXE: Path | None = None
            self.F4CK_Fixes: Path | None = None
            self.Steam_INI: Path | None = None
            self.Preloader_DLL: Path | None = None
            self.Preloader_XML: Path | None = None
            self.F4SE_DLL: Path | None = None
            self.F4SE_SDLL: Path | None = None
            self.F4SE_Loader: Path | None = None
            self.F4SE_VRDLL: Path | None = None
            self.F4SE_VRLoader: Path | None = None
            self.Buffout_DLL: Path | None = None
            self.Buffout_INI: Path | None = None
            self.Buffout_TOML: Path | None = None
            self.Address_Library: Path | None = None
            self.Game_Path: str | None = None

            FO4_STEAM_ID = 377160
            Loc_Found = False
            if platform.system() == "Windows":
                # Using shell32.dll to look up Documents directory path. Thanks, StackOverflow!
                # Unsure os.path.expanduser('~/Documents') works if default path was changed.
                CSIDL_PERSONAL = 5       # (My) Documents
                SHGFP_TYPE_CURRENT = 0   # Get current, not default value.
                User_Documents = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)  # type: ignore
                ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, User_Documents)  # type: ignore
                Doc_Path = Path(User_Documents.value)
                self.FO4_Custom_Path = Doc_Path.joinpath("My Games", "Fallout4", "Fallout4Custom.ini")
                self.FO4_F4SEVR_Path = Doc_Path.joinpath("My Games", "Fallout4", "F4SE", "f4sevr.log")
                self.FO4_F4SE_Path = Doc_Path.joinpath("My Games", "Fallout4", "F4SE", "f4se.log")
                self.FO4_F4SE_Logs = str(Doc_Path.joinpath("My Games", "Fallout4", "F4SE"))
                Loc_Found = True
            else:  # Find where FO4 is installed via Steam if Linux
                libraryfolders_path = Path.home().joinpath(".local", "share", "Steam", "steamapps", "common", "libraryfolders.vdf")
                if libraryfolders_path.is_file():
                    library_path = None
                    with libraryfolders_path.open(encoding="utf-8", errors="ignore") as steam_library_raw:
                        steam_library = steam_library_raw.readlines()
                    for line in steam_library:
                        if "path" in line:
                            library_path = Path(line.split('"')[3])
                        if str(FO4_STEAM_ID) in line:
                            library_path = library_path.joinpath("steamapps") # type: ignore
                            settings_path = library_path.joinpath("compatdata", str(FO4_STEAM_ID), "pfx", "drive_c", "users", "steamuser", "My Documents", "My Games", "Fallout4")
                            if library_path.joinpath("common", "Fallout 4").exists() and settings_path.exists():
                                self.FO4_Custom_Path = settings_path.joinpath("Fallout4Custom.ini")
                                self.FO4_F4SEVR_Path = settings_path.joinpath("F4SE", "f4sevr.log")
                                self.FO4_F4SE_Path = settings_path.joinpath("F4SE", "f4se.log")
                                self.FO4_F4SE_Logs = str(settings_path.joinpath("F4SE"))
                                Loc_Found = True
                                break
            # Prompt manual input if ~\Documents\My Games\Fallout4 cannot be found.
            if not Loc_Found:
                if "fallout4" in CLAS_config.get("MAIN", "INI Path").lower():
                    INI_Line = CLAS_config.get("MAIN", "INI Path").strip()
                    self.FO4_F4SE_Logs = rf"{INI_Line}/F4SE"
                    self.FO4_F4SE_Path = Path(rf"{INI_Line}/F4SE/f4se.log")
                    self.FO4_F4SEVR_Path = Path(rf"{INI_Line}/F4SE/f4sevr.log")
                    self.FO4_Custom_Path = Path(rf"{INI_Line}/Fallout4Custom.ini")
                else:
                    print("> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR Fallout4.ini IS LOCATED < <")
                    Path_Input = input("(EXAMPLE: C:/Users/Zen/Documents/My Games/Fallout4 | Press ENTER to confirm.)\n> ")
                    print("You entered :", Path_Input, "| This path will be automatically added to Scan Crashlogs.ini")
                    self.FO4_F4SE_Logs = rf"{Path_Input.strip()}/F4SE"
                    self.FO4_F4SE_Path = Path(rf"{Path_Input.strip()}/F4SE/f4se.log")
                    self.FO4_F4SEVR_Path = Path(rf"{Path_Input.strip()}/F4SE/f4sevr.log")
                    self.FO4_Custom_Path = Path(rf"{Path_Input.strip()}/Fallout4Custom.ini")
                    write_ini_value_to_file("INI Path", Path_Input)

    info = Info()
    # Create/Open Fallout4Custom.ini and check Archive Invalidaton & other settings.
    if CLAS_config.getboolean("MAIN", "FCX Mode"):
        if info.FO4_Custom_Path.is_file():
            try:
                os.chmod(info.FO4_Custom_Path, stat.S_IWRITE)
                F4C_config = configparser.ConfigParser()
                F4C_config.optionxform = str  # type: ignore
                F4C_config.read(info.FO4_Custom_Path)
                if "Archive" not in F4C_config.sections():
                    F4C_config.add_section("Archive")
                F4C_config.set("Archive", "bInvalidateOlderFiles", "1")
                F4C_config.set("Archive", "sResourceDataDirsFinal", "")
                with open(info.FO4_Custom_Path, "w+", encoding="utf-8", errors="ignore") as FO4_Custom:
                    F4C_config.write(FO4_Custom, space_around_delimiters=False)
            except configparser.MissingSectionHeaderError:
                print("# WARNING: YOUR Fallout4Custom.ini FILE MIGHT BE BROKEN #\n")
                print("Disable FCX Mode or delete this INI file and create a new one.\n")
                print("I also strongly advise using BethINI to readjust your INI settings.\n-----\n")
        else:
            with open(info.FO4_Custom_Path, "w+", encoding="utf-8", errors="ignore") as FO4_Custom:
                F4C_config = "[Archive]\nbInvalidateOlderFiles=1\nsResourceDataDirsFinal="
                FO4_Custom.write(F4C_config)

    # Check if f4se.log exists and find game path inside.
    if info.FO4_F4SE_Path.is_file():
        with open(info.FO4_F4SE_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for line in Path_Check:
                if "plugin directory" in line:
                    line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                    info.Game_Path = line.replace("\n", "")
    elif info.FO4_F4SEVR_Path.is_file():
        with open(info.FO4_F4SEVR_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for line in Path_Check:
                if "plugin directory" in line:
                    line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                    info.Game_Path = line.replace("\n", "")
    else:
        print("\n WARNING: AUTO-SCANNER CANNOT FIND THE REQUIRED F4SE LOG FILE!")
        print("MAKE SURE THAT FALLOUT 4 SCRIPT EXTENDER IS CORRECTLY INSTALLED!")
        print("F4SE Link (Regular & VR Version): https://f4se.silverlock.org")
        os.system("pause")

    # FILES TO LOOK FOR IN GAME FOLDER ONLY (NEEDS r BECAUSE UNICODE ERROR)
    Game_Path = Path(rf"{info.Game_Path}")
    info.VR_EXE = Game_Path.joinpath("Fallout4VR.exe")
    info.VR_Buffout = Game_Path.joinpath("Data", "F4SE", "Plugins", "msdia140.dll")
    info.F4CK_EXE = Game_Path.joinpath("CreationKit.exe")
    info.F4CK_Fixes = Game_Path.joinpath("Data", "F4CKFixes")
    info.Steam_INI = Game_Path.joinpath("steam_api.ini")
    info.Preloader_DLL = Game_Path.joinpath("IpHlpAPI.dll")
    info.Preloader_XML = Game_Path.joinpath("xSE PluginPreloader.xml")

    info.F4SE_DLL = Game_Path.joinpath("f4se_1_10_163.dll")
    info.F4SE_SDLL = Game_Path.joinpath("f4se_steam_loader.dll")
    info.F4SE_Loader = Game_Path.joinpath("f4se_loader.exe")
    info.F4SE_VRDLL = Game_Path.joinpath("f4sevr_1_2_72.dll")
    info.F4SE_VRLoader = Game_Path.joinpath("f4sevr_loader.exe")

    info.Buffout_DLL = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.dll")
    info.Buffout_INI = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.ini")
    info.Buffout_TOML = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.toml")
    info.Address_Library = Game_Path.joinpath("Data", "F4SE", "Plugins", "version-1-10-163-0.bin")

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

    SCAN_folder = os.getcwd()
    if len(CLAS_config.get("MAIN", "Scan Path")) > 1:
        SCAN_folder = CLAS_config.get("MAIN", "Scan Path")

    for file in glob(f"{SCAN_folder}/crash-*.log"):  # + glob(f"{SCAN_folder}/crash-*.txt")
        logpath = Path(file).resolve()
        scanpath = Path(str(logpath.absolute()).replace(".log", "-AUTOSCAN.md")).resolve().absolute()
        logname = logpath.name
        logtext = logpath.read_text(encoding="utf-8", errors="ignore")
        with logpath.open("r+", encoding="utf-8", errors="ignore") as lines:
            loglines = lines.readlines()
            while "" in loglines:
                loglines.remove("")
        with scanpath.open("w", encoding="utf-8", errors="ignore") as output:
            output.writelines([f"{logname} | Scanned with Crash Log Auto-Scanner (CLAS) version {CLAS_Current[-4:]} \n",
                               "# FOR BEST VIEWING EXPERIENCE OPEN THIS FILE IN NOTEPAD++ | BEWARE OF FALSE POSITIVES # \n",
                               "====================================================\n"])

            # DEFINE LINE INDEXES FOR EVERYTHING REQUIRED HERE
            buff_ver = loglines[1].strip()
            buff_error = loglines[3].strip()
            plugins_index = 1
            plugins_loaded = False
            for line in loglines:
                if "F4SE" not in line and "PLUGINS:" in line:
                    plugins_index = loglines.index(line)
                if "[00]" in line:
                    plugins_loaded = True

            plugins_list = loglines[plugins_index:]
            if os.path.exists("loadorder.txt"):
                plugins_list = []
                with open("loadorder.txt", "r", encoding="utf-8", errors="ignore") as loadorder_check:
                    plugin_format = loadorder_check.readlines()
                    if len(plugin_format) >= 1 and "[00]" not in plugins_list:
                        plugins_list.append("[00]")
                    for line in plugin_format:
                        line = "[LO] " + line.strip()
                        plugins_list.append(line)

            # BUFFOUT VERSION CHECK
            buff_latest = "Buffout 4 v1.26.2"
            buffVR_latest = "Buffout 4 v1.29.0 Nov  5 2022 02:22:25"
            output.writelines([f"Main Error: {buff_error}\n",
                               "====================================================\n",
                               f"Detected Buffout Version: {buff_ver.strip()}\n",
                               f"Latest Buffout Version: {buff_latest[10:17]} (VR: v1.29.0)\n"])

            if buff_ver.casefold() == buff_latest.casefold() or buff_ver.casefold() == buffVR_latest.casefold():
                output.write("You have the lastest version of Buffout 4!\n")
            else:
                output.writelines(["# REPORTED BUFFOUT 4 VERSION DOES NOT MATCH THE VERSION USED BY AUTOSCAN # \n",
                                   "UPDATE BO4 IF NECESSARY: https://www.nexusmods.com/fallout4/mods/47359 \n",
                                   "BO4 FOR VIRTUAL REALITY: https://www.nexusmods.com/fallout4/mods/64880 \n"])
            if "v1." not in buff_ver:
                statL_veryold += 1
                statL_scanned -= 1

            output.writelines(["====================================================\n",
                               "CHECKING IF BUFFOUT 4 FILES/SETTINGS ARE CORRECT...\n",
                               "====================================================\n"])

            ALIB_Load = BUFF_Load = False

            # CHECK IF F4SE.LOG EXISTS AND REPORTS ANY ERRORS
            if CLAS_config.getboolean("MAIN", "FCX Mode"):
                output.writelines(["* NOTICE: FCX MODE IS ENABLED. AUTO-SCANNER MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *\n",
                                   "[ To disable game folder / mod files detection, set FCX Mode = false in Scan Crashlogs.ini ]\n-----\n"])
                Error_List = []
                F4SE_Error = F4SE_Version = F4SE_Buffout = 0
                if info.FO4_F4SE_Path.is_file():
                    with open(info.FO4_F4SE_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
                        Error_Check = LOG_Check.readlines()
                        for line in Error_Check:
                            if "0.6.23" in line:
                                F4SE_Version = 1
                            if "error" in line.lower() or "failed" in line.lower():
                                F4SE_Error = 1
                                Error_List.append(line)
                            if "buffout4.dll" in line.lower() and "loaded correctly" in line.lower():
                                F4SE_Buffout = 1
                if info.FO4_F4SEVR_Path.is_file():
                    with open(info.FO4_F4SEVR_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
                        Error_Check = LOG_Check.readlines()
                        for line in Error_Check:
                            if "0.6.20" in line:
                                F4SE_Version = 1
                            if "error" in line.lower() or "failed" in line.lower():
                                Error_List.append(line)
                            if "buffout4.dll" in line.lower() and "loaded correctly" in line.lower():
                                F4SE_Buffout = 1

                if F4SE_Version == 1:
                    output.write("You have the latest version of Fallout 4 Script Extender (F4SE). \n-----\n")
                else:
                    output.writelines(["# REPORTED F4SE VERSION DOES NOT MATCH THE F4SE VERSION USED BY AUTOSCAN #\n",
                                       "UPDATE FALLOUT 4 SCRIPT EXTENDER IF NECESSARY: https://f4se.silverlock.org\n",
                                       "-----\n"])

                if F4SE_Error == 1:
                    output.write("# SCRIPT EXTENDER REPORTS THAT THE FOLLOWING PLUGINS FAILED TO LOAD! #\n")
                    for elem in Error_List:
                        output.write(f"{elem}\n-----\n")
                else:
                    output.write("Script Extender reports that all DLL mod plugins have loaded correctly. \n-----\n")

                if F4SE_Buffout == 1:
                    output.write("Script Extender reports that Buffout 4.dll was found and loaded correctly. \n-----\n")
                    ALIB_Load = BUFF_Load = True
                else:
                    output.writelines(["# SCRIPT EXTENDER REPORTS THAT BUFFOUT 4.DLL FAILED TO LOAD OR IS MISSING! #\n",
                                       "Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115\n",
                                       "Buffout 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359\n",
                                       "-----\n"])

                list_ERRORLOG = []
                for file in glob(f"{info.FO4_F4SE_Logs}/*.log"):
                    if "crash-" not in file:
                        filepath = Path(file).resolve()
                        if filepath.is_file():
                            try:
                                with filepath.open("r+", encoding="utf-8", errors="ignore") as LOG_Check:
                                    Log_Errors = LOG_Check.read()
                                    if "error" in Log_Errors.lower():
                                        logname = str(filepath)
                                        if "f4se.log" not in logname:
                                            list_ERRORLOG.append(logname)
                            except OSError:
                                list_ERRORLOG.append(str(filepath))
                                continue

                if len(list_ERRORLOG) >= 1:
                    output.writelines(["# WARNING: THE FOLLOWING DLL LOGS ALSO REPORT ONE OR MORE ERRORS : #\n",
                                       "[You should open these files and check what errors are shown.]\n"])
                    errorlist = []
                    for elem in list_ERRORLOG:
                        errorlist.append(f"{elem}\n-----\n")
                    output.writelines(errorlist)
                else:
                    output.write("Available DLL logs do not report any additional errors, all is well. \n-----\n")

            # CHECK BUFFOUT 4 REQUIREMENTS AND TOML SETTINGS
                if CLAS_config.getboolean("MAIN", "IMI Mode") is False:
                    if info.Preloader_XML.is_file() and info.Preloader_DLL.is_file():
                        output.writelines(["OPTIONAL: Plugin Preloader is (manually) installed.\n\n",
                                           "NOTICE: If the game fails to start after installing this mod, open xSE PluginPreloader.xml with a text editor and CHANGE\n",
                                           "<LoadMethod Name=\"ImportAddressHook\"> TO <LoadMethod Name=\"OnThreadAttach\"> OR <LoadMethod Name=\"OnProcessAttach\">\n",
                                           "IF THE GAME STILL REFUSES TO START, COMPLETELY REMOVE xSE PluginPreloader.xml AND IpHlpAPI.dll FROM YOUR FO4 GAME FOLDER\n",
                                           "-----\n"])
                    else:
                        output.write('OPTIONAL: Plugin Preloader is not (manually) installed.\n-----\n')

                    if (info.F4SE_VRDLL.is_file() and info.F4SE_VRLoader.is_file()) or (info.F4SE_DLL.is_file() and info.F4SE_Loader.is_file() and info.F4SE_SDLL.is_file()):
                        output.write("REQUIRED: Fallout 4 Script Extender is (manually) installed. \n-----\n")
                    else:
                        output.writelines(["# WARNING: Auto-Scanner cannot find Script Extender files or they aren't (manually) installed! #\n",
                                           "FIX: Extract all files inside *f4se_0_06_XX* folder into your Fallout 4 game folder.\n",
                                           "FALLOUT 4 SCRIPT EXTENDER: (Download Latest Build) https://f4se.silverlock.org\n",
                                           "-----\n"])

                    if info.Address_Library.is_file() or ALIB_Load is True:
                        output.write("REQUIRED: Address Library is (manually) installed. \n-----\n")
                    else:
                        output.writelines(["# WARNING: Auto-Scanner cannot find the Adress Library file or it isn't (manually) installed! #\n",
                                           "FIX: Place the *version-1-10-163-0.bin* file manually into Fallout 4/Data/F4SE/Plugins folder.\n",
                                           "ADDRESS LIBRARY: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47327?tab=files\n",
                                           "-----\n"])

                    if info.Buffout_INI.is_file() and info.Buffout_DLL.is_file():
                        output.write("REQUIRED: Buffout 4 is (manually) installed. Checking configuration...\n-----\n")
                        with open(info.Buffout_INI, "r+", encoding="utf-8", errors="ignore") as BUFF_Custom:
                            BUFF_config = BUFF_Custom.read()
                            BUFF_lines = BUFF_config.splitlines()
                            for line in BUFF_lines:
                                if "=" in line:
                                    if "true" in line or "false" in line or "-1" in line:
                                        pass
                                    else:
                                        output.writelines(["# WARNING: THE FOLLOWING *Buffout4.toml* VALUE OR PARAMETER IS INVALID #\n",
                                                           f"{line} \n[ Correct all typos / formatting / capitalized letters from this line in Buffout4.toml.] \n",
                                                           "-----\n"])

                            if ("achievements.dll" in logtext or "UnlimitedSurvivalMode.dll" in logtext) and "Achievements = true" in BUFF_config:
                                output.writelines(["# WARNING: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #\n",
                                                   "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.\n",
                                                   "-----\n"])

                                BUFF_config = BUFF_config.replace("Achievements = true", "Achievements = false")
                            else:
                                output.write("Achievements parameter in *Buffout4.toml* is correctly configured. \n-----\n")

                            if "BakaScrapHeap.dll" in logtext and "MemoryManager = true" in BUFF_config:
                                output.writelines(["# WARNING: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #\n",
                                                   "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.\n",
                                                   "-----\n"])
                                BUFF_config = BUFF_config.replace("MemoryManager = true", "MemoryManager = false")
                            else:
                                output.write("Memory Manager parameter in *Buffout4.toml* is correctly configured. \n-----\n")

                            if "f4ee.dll" in logtext and "F4EE = false" in BUFF_config:
                                output.writelines(["# WARNING: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #\n",
                                                   "Auto-Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu.\n",
                                                   "-----\n"])
                                BUFF_config = BUFF_config.replace("F4EE = false", "F4EE = true")
                            else:
                                output.write("Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured. \n-----\n")
                        with open(info.Buffout_INI, "w+", encoding="utf-8", errors="ignore") as BUFF_Custom:
                            BUFF_Custom.write(BUFF_config)
                    else:
                        output.writelines(["# WARNING: Auto-Scanner cannot find Buffout 4 files or they aren't (manually) installed! #\n",
                                           "FIX: Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115\n",
                                           "BUFFOUT 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359?tab=files\n",
                                           "-----\n"])

            else:  # INSTRUCTIONS FOR MANUAL FIXING WHEN FCX MODE IS FALSE
                if ("Achievements: true" in logtext and "achievements.dll" in logtext) or ("Achievements: true" in logtext and "UnlimitedSurvivalMode.dll" in logtext):
                    output.writelines(["# WARNING: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #\n",
                                       "FIX: Open *Buffout4.toml* and change Achievements parameter to FALSE, this prevents conflicts with Buffout 4.\n",
                                       "-----\n"])
                else:
                    output.write("Achievements parameter in *Buffout4.toml* is correctly configured. \n-----\n")

                if "MemoryManager: true" in logtext and "BakaScrapHeap.dll" in logtext:
                    output.writelines(["# WARNING: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #\n",
                                       "FIX: Open *Buffout4.toml* and change MemoryManager parameter to FALSE, this prevents conflicts with Buffout 4.\n",
                                       "-----\n"])
                else:
                    output.write("Memory Manager parameter in *Buffout4.toml* is correctly configured. \n-----\n")

                if "F4EE: false" in logtext and "f4ee.dll" in logtext:
                    output.writelines(["# WARNING: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #\n",
                                       "FIX: Open *Buffout4.toml* and change F4EE parameter to TRUE, this prevents bugs and crashes from Looks Menu.\n",
                                       "-----\n"])
                else:
                    output.write("Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured. \n-----\n")

            output.writelines(["====================================================\n",
                               "CHECKING IF LOG MATCHES ANY KNOWN CRASH MESSAGES...\n",
                               "====================================================\n"])
            Buffout_Trap = False  # RETURN TRUE IF KNOWN CRASH MESSAGE WAS FOUND

            # ====================== HEADER ERRORS ======================

            if ".dll" in buff_error and "tbbmalloc" not in buff_error:
                output.write("# MAIN ERROR REPORTS A DLL WAS INVLOVED IN THIS CRASH! # \n-----\n")

            if "EXCEPTION_STACK_OVERFLOW" in buff_error:
                output.writelines(["# Checking for Stack Overflow Crash.........CULPRIT FOUND! #\n",
                                   "> Priority : [5]\n"])
                Buffout_Trap = True
                statC_Overflow += 1

            if "0x000100000000" in buff_error:
                output.writelines(["# Checking for Bad Pointer Crash............CULPRIT FOUND! #\n",
                                   "> Priority : [5]\n"])
                Buffout_Trap = True
                statC_ActiveEffect += 1

            if "EXCEPTION_INT_DIVIDE_BY_ZERO" in buff_error:
                output.writelines(["# Checking for Divide By Zero Crash.........CULPRIT FOUND! #\n",
                                   "> Priority : [5]\n"])
                Buffout_Trap = True
                statC_BadMath += 1

            if "0x000000000000" in buff_error:
                output.writelines(["# Checking for Null Crash...................CULPRIT FOUND! #\n",
                                   "> Priority : [5]\n"])
                Buffout_Trap = True
                statC_Null += 1

            # ======================= MAIN ERRORS =======================

            # OTHER | RESERVED
            # *[Creation Club Crash] | +01B59A4
            # Uneducated Shooter (56789) | "std::invalid_argument"
            # "BSResourceNiBinaryStream"
            # "ObjectBindPolicy"

            # ===========================================================
            if "DLCBannerDLC01.dds" in logtext:
                output.writelines(["# Checking for DLL Crash....................CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | DLCBannerDLC01.dds : {logtext.count("DLCBannerDLC01.dds")}\n'])
                Buffout_Trap = True
                statC_DLL += 1
            # ===========================================================
            if "BGSLocation" in logtext and "BGSQueuedTerrainInitialLoad" in logtext:
                output.writelines(["# Checking for LOD Crash....................CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | BGSLocation : {logtext.count("BGSLocation")} | BGSQueuedTerrainInitialLoad : {logtext.count("BGSQueuedTerrainInitialLoad")}\n'])
                Buffout_Trap = True
                statC_LOD += 1
            # ===========================================================
            if "FaderData" in logtext or "FaderMenu" in logtext or "UIMessage" in logtext:
                output.writelines(["# Checking for MCM Crash....................CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | FaderData : {logtext.count("FaderData")} | FaderMenu : {logtext.count("FaderMenu")} | UIMessage : {logtext.count("UIMessage")}\n'])
                Buffout_Trap = True
                statC_MCM += 1
            # ===========================================================
            if "BGSDecalManager" in logtext or "BSTempEffectGeometryDecal" in logtext:
                output.writelines(["# Checking for Decal Crash..................CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | BGSDecalManager : {logtext.count("BGSDecalManager")} | BSTempEffectGeometryDecal : {logtext.count("BSTempEffectGeometryDecal")}\n'])
                Buffout_Trap = True
                statC_Decal += 1
            # ===========================================================
            if logtext.count("PipboyMapData") >= 2:
                output.writelines(["# Checking for Equip Crash..................CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | PipboyMapData : {logtext.count("PipboyMapData")}\n'])
                Buffout_Trap = True
                statC_Equip += 1
            # ===========================================================
            if "Papyrus" in logtext or "VirtualMachine" in logtext or "Assertion failed" in logtext:
                output.writelines(["# Checking for Script Crash.................CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | Papyrus : {logtext.count("Papyrus")} | VirtualMachine : {logtext.count("VirtualMachine")}\n'])
                Buffout_Trap = True
                statC_Papyrus += 1
            # ===========================================================
            if logtext.count("tbbmalloc.dll") >= 3 or "tbbmalloc" in buff_error:
                output.writelines(["# Checking for Generic Crash................CULPRIT FOUND! #\n",
                                   f'> Priority : [2] | tbbmalloc.dll : {logtext.count("tbbmalloc.dll")}\n'])
                Buffout_Trap = True
                statC_Generic += 1
            # ===========================================================
            if "LooseFileAsyncStream" in logtext:
                output.writelines(["# Checking for BA2 Limit Crash..............CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | LooseFileAsyncStream : {logtext.count("LooseFileAsyncStream")}\n'])
                Buffout_Trap = True
                statC_BA2Limit += 1
            # ===========================================================
            if logtext.count("d3d11.dll") >= 3 or "d3d11" in buff_error:
                output.writelines(["# Checking for Rendering Crash..............CULPRIT FOUND! #\n",
                                   f'> Priority : [4] | d3d11.dll : {logtext.count("d3d11.dll")}\n'])
                Buffout_Trap = True
                statC_Rendering += 1
            # ===========================================================
            if logtext.count("MSVCR110") >= 4 or "MSVCR" in buff_error or "MSVCP" in buff_error:
                output.writelines(["# Checking for C++ Redist Crash.............CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | MSVCR110.dll : {logtext.count("MSVCR110.dll")}\n'])
                Buffout_Trap = True
                statC_Redist += 1
            # ===========================================================
            if "GridAdjacencyMapNode" in logtext or "PowerUtils" in logtext:
                output.writelines(["# Checking for Grid Scrap Crash.............CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | GridAdjacencyMapNode : {logtext.count("GridAdjacencyMapNode")} | PowerUtils : {logtext.count("PowerUtils")}\n'])
                Buffout_Trap = True
                statC_GridScrap += 1
            # ===========================================================
            if "HUDCompass" in logtext or "HUDCompassMarker" in logtext or "attachMovie()" in logtext:
                output.writelines(["# Checking for Map Marker Crash.............CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | HUDCompass : {logtext.count("HUDCompass")} | HUDCompassMarker : {logtext.count("HUDCompassMarker")}\n'])
                Buffout_Trap = True
                statC_MapMarker += 1
            # ===========================================================
            if ("LooseFileStream" in logtext or "BSFadeNode" in logtext or "BSMultiBoundNode" in logtext) and logtext.count("LooseFileAsyncStream") == 0:
                output.writelines(["# Checking for Mesh (NIF) Crash.............CULPRIT FOUND! #\n",
                                   f'> Priority : [4] | LooseFileStream : {logtext.count("LooseFileStream")} | BSFadeNode : {logtext.count("BSFadeNode")}\n',
                                   f'                   BSMultiBoundNode : {logtext.count("BSMultiBoundNode")}\n'])
                Buffout_Trap = True
                statC_NIF += 1
            # ===========================================================
            if "Create2DTexture" in logtext or "DefaultTexture" in logtext:
                output.writelines(["# Checking for Texture (DDS) Crash..........CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | Create2DTexture : {logtext.count("Create2DTexture")} | DefaultTexture : {logtext.count("DefaultTexture")}\n'])
                Buffout_Trap = True
                statC_Texture += 1
            # ===========================================================
            if "DefaultTexture_Black" in logtext or "NiAlphaProperty" in logtext:
                output.writelines(["# Checking for Material (BGSM) Crash........CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | DefaultTexture_Black : {logtext.count("DefaultTexture_Black")} | NiAlphaProperty : {logtext.count("NiAlphaProperty")}\n'])
                Buffout_Trap = True
                statC_BGSM += 1
            # ===========================================================
            if (logtext.count("bdhkm64.dll") or logtext.count("usvfs::hook_DeleteFileW")) >= 2:
                output.writelines(["# Checking for BitDefender Crash............CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | bdhkm64.dll : {logtext.count("bdhkm64.dll")} | usvfs::hook_DeleteFileW : {logtext.count("usvfs::hook_DeleteFileW")}\n'])
                Buffout_Trap = True
                statC_BitDefender += 1
            # ===========================================================
            if (logtext.count("PathingCell") or logtext.count("BSPathBuilder") or logtext.count("PathManagerServer")) >= 2:
                output.writelines(["# Checking for NPC Pathing Crash (S)........CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | PathingCell : {logtext.count("PathingCell")} | BSPathBuilder : {logtext.count("BSPathBuilder")}\n',
                                   f'                   PathManagerServer : {logtext.count("PathManagerServer")}\n'])
                Buffout_Trap = True
                statC_NPCPathing += 1
            elif (logtext.count("NavMesh") or logtext.count("BSNavmeshObstacleData") or logtext.count("DynamicNavmesh") or logtext.count("PathingRequest")) >= 2:
                output.writelines(["# Checking for NPC Pathing Crash (D)........CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | NavMesh : {logtext.count("NavMesh")} | BSNavmeshObstacleData : {logtext.count("BSNavmeshObstacleData")}\n',
                                   f'                   DynamicNavmesh : {logtext.count("DynamicNavmesh")} PathingRequest : {logtext.count("PathingRequest")}\n'])
                Buffout_Trap = True
                statC_NPCPathing += 1
            # ===========================================================
            if logtext.count("X3DAudio1_7.dll") >= 3 or logtext.count("XAudio2_7.dll") >= 3 or ("X3DAudio1_7" or "XAudio2_7") in buff_error:
                output.writelines(["# Checking for Audio Driver Crash...........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | X3DAudio1_7.dll : {logtext.count("X3DAudio1_7.dll")} | XAudio2_7.dll : {logtext.count("XAudio2_7.dll")}\n'])
                Buffout_Trap = True
                statC_Audio += 1
            # ===========================================================
            if logtext.count("cbp.dll") >= 3 or "skeleton.nif" in logtext or "cbp.dll" in buff_error:
                output.writelines(["# Checking for Body Physics Crash...........CULPRIT FOUND! #\n",
                                   f'> Priority : [4] | cbp.dll : {logtext.count("cbp.dll")} | skeleton.nif : {logtext.count("skeleton.nif")}\n'])
                Buffout_Trap = True
                statC_BodyPhysics += 1
            # ===========================================================
            if "+0D09AB7" in buff_error or "TESLevItem" in logtext:
                output.writelines(["# Checking for Leveled List Crash...........CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | +0D09AB7 : {logtext.count("+0D09AB7")} | TESLevItem : {logtext.count("TESLevItem")}\n'])
                Buffout_Trap = True
                statC_LeveledList += 1
            # ===========================================================
            if "BSMemStorage" in logtext or "DataFileHandleReaderWriter" in logtext or "[FF]" in plugins_list:
                output.writelines(["# Checking for Plugin Limit Crash...........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | BSMemStorage : {logtext.count("BSMemStorage")} | DataFileHandleReaderWriter : {logtext.count("DataFileHandleReaderWriter")}\n'])
                Buffout_Trap = True
                statC_PluginLimit += 1
            # ===========================================================
            if "+0DB9300" in buff_error or "GamebryoSequenceGenerator" in logtext:
                output.writelines(["# Checking for Plugin Order Crash...........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | +0DB9300 | GamebryoSequenceGenerator : {logtext.count("GamebryoSequenceGenerator")}\n'])
                Buffout_Trap = True
                statC_LoadOrder += 1
            # ===========================================================
            if logtext.count("BSD3DResourceCreator") >= 3:
                output.writelines(["# Checking for MO2 Extractor Crash..........CULPRIT FOUND! #\n",
                                   f'> Priority : [3] | BSD3DResourceCreator : {logtext.count("BSD3DResourceCreator")}\n'])
                Buffout_Trap = True
                statC_MO2Unpack += 1
            # ===========================================================
            if "+03EE452" in buff_error or "flexRelease_x64" in buff_error or (logtext.count("flexRelease_x64.dll") or logtext.count("CheckRefAgainstConditionsFunc")) >= 2:
                output.writelines(["# Checking for Nvidia Debris Crash..........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | +03EE452 | flexRelease_x64.dll : {logtext.count("flexRelease_x64.dll")} | CheckRefAgainstConditionsFunc : {logtext.count("CheckRefAgainstConditionsFunc")}\n'])
                Buffout_Trap = True
                statC_NVDebris += 1
            # ===========================================================
            if logtext.count("nvwgf2umx.dll") >= 10 or "nvwgf2umx" in buff_error or "USER32.dll" in buff_error:
                output.writelines(["# Checking for Nvidia Driver Crash..........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | nvwgf2umx.dll : {logtext.count("nvwgf2umx.dll")} | USER32.dll : {logtext.count("USER32.dll")}\n'])
                Buffout_Trap = True
                statC_NVDriver += 1
            # ===========================================================
            if (logtext.count("KERNELBASE.dll") or logtext.count("MSVCP140.dll")) >= 3 and "DxvkSubmissionQueue" in logtext:
                output.writelines(["# Checking for Vulkan Memory Crash..........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | KERNELBASE.dll : {logtext.count("KERNELBASE.dll")} | MSVCP140.dll : {logtext.count("MSVCP140.dll")}\n',
                                   f'                   DxvkSubmissionQueue : {logtext.count("DxvkSubmissionQueue")}\n'])
                Buffout_Trap = True
                statC_VulkanMem += 1
            # ===========================================================
            if "dxvk::DXGIAdapter" in logtext or "dxvk::DXGIFactory" in logtext:
                output.writelines(["# Checking for Vulkan Settings Crash........CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | dxvk::DXGIAdapter : {logtext.count("dxvk::DXGIAdapter")} | dxvk::DXGIFactory : {logtext.count("dxvk::DXGIFactory")}\n'])
                Buffout_Trap = True
                statC_VulkanSet += 1
            # ===========================================================
            if "BSXAudio2DataSrc" in logtext or "BSXAudio2GameSound" in logtext:
                output.writelines(["# Checking for Corrupted Audio Crash........CULPRIT FOUND! #\n",
                                   f'> Priority : [4] | BSXAudio2DataSrc : {logtext.count("BSXAudio2DataSrc")} | BSXAudio2GameSound : {logtext.count("BSXAudio2GameSound")}\n'])
                Buffout_Trap = True
                statC_CorruptedAudio += 1
            # ===========================================================
            if "SysWindowCompileAndRun" in logtext or "ConsoleLogPrinter" in logtext:
                output.writelines(["# Checking for Console Command Crash........CULPRIT FOUND! #\n",
                                   f'> Priority : [1] | SysWindowCompileAndRun : {logtext.count("SysWindowCompileAndRun")} | ConsoleLogPrinter : {logtext.count("ConsoleLogPrinter")}\n'])
                Buffout_Trap = True
                statC_ConsoleCommands += 1
            # ===========================================================
            if "+1B938F0" in buff_error or "AnimTextData\\AnimationFileData" in logtext or "AnimationFileLookupSingletonHelper" in logtext:
                output.writelines(["# Checking for Game Corruption Crash........CULPRIT FOUND! #\n",
                                   f' Priority : [5] | +1B938F0 | AnimationFileData : {logtext.count("AnimationFileData")} | AnimationFileLookup : {logtext.count("AnimationFileLookupSingletonHelper")}\n'])
                Buffout_Trap = True
                statC_GameCorruption += 1
            # ===========================================================
            if "BGSWaterCollisionManager" in logtext:
                output.writelines(["# Checking for Water Collision Crash........CULPRIT FOUND! #\n",
                                   "PLEASE CONTACT ME AS SOON AS POSSIBLE! (CONTACT INFO BELOW)\n",
                                   f'> Priority : [6] | BGSWaterCollisionManager : {logtext.count("BGSWaterCollisionManager")}\n'])
                Buffout_Trap = True
                statC_Water += 1
            # ===========================================================
            if "ParticleSystem" in logtext:
                output.writelines(["# Checking for Particle Effects Crash.......CULPRIT FOUND! #\n",
                                   f'> Priority : [4] | ParticleSystem : {logtext.count("ParticleSystem")}\n'])
                Buffout_Trap = True
                statC_Particles += 1
            # ===========================================================
            if "+1FCC07E" in buff_error or "BSAnimationGraphManager" in logtext or "hkbVariableBindingSet" in logtext or "hkbHandIkControlsModifier" in logtext or "hkbBehaviorGraph" in logtext or "hkbModifierList" in logtext:
                output.writelines(["# Checking for Animation / Physics Crash....CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | +1FCC07E | hkbVariableBindingSet : {logtext.count("hkbVariableBindingSet")} | hkbHandIkControlsModifier : {logtext.count("hkbHandIkControlsModifier")}\n',
                                   f'                   hkbBehaviorGraph : {logtext.count("hkbBehaviorGraph")} | hkbModifierList : {logtext.count("hkbModifierList")} | BSAnimationGraphManager : {logtext.count("BSAnimationGraphManager")}\n'])
                Buffout_Trap = True
                statC_AnimationPhysics += 1
            # ===========================================================
            if "DLCBanner05.dds" in logtext:
                output.writelines(["# Checking for Archive Invalidation Crash...CULPRIT FOUND! #\n",
                                   f'> Priority : [5] | DLCBanner05.dds : {logtext.count("DLCBanner05.dds")}\n'])
                Buffout_Trap = True
                statC_Invalidation += 1

            # ===========================================================
            output.write("---------- Unsolved Crash Messages Below ----------\n")

            if "+01B59A4" in buff_error:
                output.writelines(["# Checking for *[Creation Club Crash].......DETECTED! #\n",
                                   f'> Priority : [3] | +01B59A4\n'])
                Buffout_Trap = True
                statU_CClub += 1
            # ===========================================================
            if "BGSMod::Attachment" in logtext or "BGSMod::Template" in logtext or "BGSMod::Template::Item" in logtext:
                output.writelines(["# Checking for *[Item Crash]................DETECTED! #\n",
                                   f'> Priority : [5] | BGSMod::Attachment : {logtext.count("BGSMod::Attachment")} | BGSMod::Template : {logtext.count("BGSMod::Template")}\n',
                                   f'                   BGSMod::Template::Item : {logtext.count("BGSMod::Template::Item")}\n'])
                Buffout_Trap = True
                statU_Item += 1
            # ===========================================================
            if "+0CDAD30" in buff_error or "BGSSaveLoadManager" in logtext or "BGSSaveLoadThread" in logtext or "BGSSaveFormBuffer" in logtext:
                output.writelines(["# Checking for *[Save Crash]................DETECTED! #\n",
                                   f'> Priority : [4] | +0CDAD30 | BGSSaveLoadManager : {logtext.count("BGSSaveLoadManager")}\n',
                                   f'                   BGSSaveFormBuffer : {logtext.count("BGSSaveFormBuffer")} | BGSSaveLoadThread : {logtext.count("BGSSaveLoadThread")}\n'])
                Buffout_Trap = True
                statU_Save += 1
            # ===========================================================
            if "ButtonEvent" in logtext or "MenuControls" in logtext or "MenuOpenCloseHandler" in logtext or "PlayerControls" in logtext or "DXGISwapChain" in logtext:
                output.writelines(["# Checking for *[Input Crash]...............DETECTED! #\n",
                                   f'> Priority : [4] | ButtonEvent : {logtext.count("ButtonEvent")} | MenuControls : {logtext.count("MenuControls")}\n',
                                   f'                   MenuOpenCloseHandler : {logtext.count("MenuOpenCloseHandler")} | PlayerControls : {logtext.count("PlayerControls")}\n',
                                   f'                   DXGISwapChain : {logtext.count("DXGISwapChain")}\n'])
                Buffout_Trap = True
                statU_Input += 1
            # ===========================================================
            if "+1D13DA7" in buff_error and ("BSShader" in logtext or "BSBatchRenderer" in logtext or "ShadowSceneNode" in logtext):
                output.writelines(["# Checking for *[Looks Menu Crash]..........DETECTED! #\n",
                                   f'> Priority : [5] | +1D13DA7 \n'])
                Buffout_Trap = True
                statU_LooksMenu += 1
            # ===========================================================
            if "BGSProcedurePatrol" in logtext or "BGSProcedurePatrolExecState" in logtext or "PatrolActorPackageData" in logtext:
                output.writelines(["# Checking for *[NPC Patrol Crash]..........DETECTED! #\n",
                                   f'> Priority : [5] | BGSProcedurePatrol : {logtext.count("BGSProcedurePatrol")} | BGSProcedurePatrolExecStatel : {logtext.count("BGSProcedurePatrolExecState")}\n',
                                   f'                   PatrolActorPackageData : {logtext.count("PatrolActorPackageData")}\n'])
                Buffout_Trap = True
                statU_Patrol += 1
            # ===========================================================
            if "BSPackedCombinedSharedGeomDataExtra" in logtext or "BSPackedCombinedGeomDataExtra" in logtext or "BGSCombinedCellGeometryDB" in logtext or "BGSStaticCollection" in logtext or "TESObjectCELL" in logtext:
                output.writelines(["# Checking for *[Precombines Crash].........DETECTED! #\n",
                                   f'> Priority : [5] | BGSStaticCollection : {logtext.count("BGSStaticCollection")} | BGSCombinedCellGeometryDB : {logtext.count("BGSCombinedCellGeometryDB")}\n',
                                   f'                   BSPackedCombinedGeomDataExtra : {logtext.count("BSPackedCombinedGeomDataExtra")} | TESObjectCELL : {logtext.count("TESObjectCELL")}\n',
                                   f'                   BSPackedCombinedSharedGeomDataExtra : {logtext.count("BSPackedCombinedSharedGeomDataExtra")}\n'])
                Buffout_Trap = True
                statC_Precomb += 1
            # ===========================================================
            if "HUDAmmoCounter" in logtext:
                output.writelines(["# Checking for *[Ammo Counter Crash]........DETECTED! #\n",
                                   f'> Priority : [5] | HUDAmmoCounter : {logtext.count("HUDAmmoCounter")}\n'])
                Buffout_Trap = True
                statU_HUDAmmo += 1
            # ===========================================================
            if "BGSProjectile" in logtext or "CombatProjectileAimController" in logtext:
                output.writelines(["# Checking for *[NPC Projectile Crash].....DETECTED! #\n",
                                   f'> Priority : [5] | BGSProjectile : {logtext.count("BGSProjectile")} | CombatProjectileAimController : {logtext.count("CombatProjectileAimController")}\n'])
                Buffout_Trap = True
            # ===========================================================
            if logtext.count("PlayerCharacter") >= 1 and (logtext.count("0x00000007") or logtext.count("0x00000014") or logtext.count("0x00000008")) >= 3:
                output.writelines(["# Checking for *[Player Character Crash]....DETECTED! #\n",
                                   f'> Priority : [5] | PlayerCharacter : {logtext.count("PlayerCharacter")} | 0x00000007 : {logtext.count("0x00000007")}\n',
                                   f'                   0x00000008 : {logtext.count("0x00000008")} | 0x000000014 : {logtext.count("0x00000014")}\n'])
                Buffout_Trap = True
                statC_Player += 1

            # ===========================================================

            if not Buffout_Trap:  # DEFINE CHECK IF NOTHING TRIGGERED BUFFOUT TRAP
                output.writelines(["-----\n",
                                   "# AUTOSCAN FOUND NO CRASH ERRORS / CULPRITS THAT MATCH THE CURRENT DATABASE #\n",
                                   "Check below for mods that can cause frequent crashes and other problems.\n",
                                   "-----\n"])
            else:
                output.writelines(["-----\n",
                                   "* FOR DETAILED DESCRIPTIONS AND POSSIBLE SOLUTIONS TO ANY ABOVE DETECTED CRASH CULPRITS *\n",
                                   "* SEE: https://docs.google.com/document/d/17FzeIMJ256xE85XdjoPvv_Zi3C5uHeSTQh6wOZugs4c *\n",
                                   "-----\n"])

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS THAT CAN CAUSE FREQUENT CRASHES...\n",
                               "====================================================\n"])
            Mod_Trap1 = 1

            """Dictionary method that preserves numerical and alphabetical order of mods"""
            mods1 = {}
            mods1[0]["mod"] = " DamageThresholdFramework.esm"
            mods1[1]["mod"] = " Endless Warfare.esm"
            mods1[2]["mod"] = " ExtendedWeaponSystem.esm"
            mods1[3]["mod"] = " EPO.esp"
            mods1[4]["mod"] = " SakhalinWasteland"
            mods1[5]["mod"] = " 76HUD"
            mods1[6]["mod"] = " Knockout Framework.esm"
            mods1[7]["mod"] = " NCRenegade"
            mods1[8]["mod"] = " Respawnable Legendary Bosses"
            mods1[9]["mod"] = " Scrap Everything - Core"
            mods1[10]["mod"] = " Scrap Everything - Ultimate"
            mods1[11]["mod"] = " Shade Girl Leather Outfits"
            mods1[12]["mod"] = " SpringCleaning.esm"
            mods1[13]["mod"] = " (STO) NO"
            mods1[14]["mod"] = " TacticalTablet.esp"
            mods1[15]["mod"] = " True Nights v03.esp"
            mods1[16]["mod"] = " WeaponsFramework"
            mods1[17]["mod"] = " WOTC.esp"

            mods1[0]["warn"] = ["DAMAGE THRESHOLD FRAMEWORK \n",
                                "- Can cause crashes in combat on some occasions due to how damage calculations are done."]
            mods1[1]["warn"] = ["ENDLESS WARFARE \n",
                                "- Some enemy spawn points could be bugged or crash the game due to scripts or pathfinding."]
            mods1[2]["warn"] = ["EXTENDED WEAPON SYSTEMS \n",
                                "- Alternative to Tactical Reload that suffers from similar weapon related problems and crashes."]
            mods1[3]["warn"] = ["EXTREME PARTICLES OVERHAUL \n",
                                "- Can cause particle effects related crashes, its INI file raises particle count to 500000. \n",
                                "  Consider switching to Burst Impact Blast FX: https://www.nexusmods.com/fallout4/mods/57789"]
            mods1[4]["warn"] = ["FALLOUT SAKHALIN \n",
                                "- Breaks the precombine system all across Far Harbor which will randomly crash your game."]
            mods1[5]["warn"] = ["HUD76 HUD REPLACER \n",
                                "- Can sometimes cause interface and pip-boy related bugs, glitches and crashes."]
            mods1[6]["warn"] = ["KNOCKOUT FRAMEWORK \n",
                                "- Confirm that you have installed the latest version (1.4.0+) of this mod. \n",
                                "  Older versions cause weird behavior and crashes during prolonged game sessions. \n",
                                "  Knockout Framework Link: https://www.nexusmods.com/fallout4/mods/27086?tab=files"]
            mods1[7]["warn"] = ["NCR RENEGADE ARMOR \n",
                                "- Broken outfit mesh that crashes the game in 3rd person or when NPCs wearing it are hit."]
            mods1[8]["warn"] = ["RESPAWNABLE LEGENDARY BOSSES \n",
                                "- Can sometimes cause Deathclaw / Behmoth boulder projectile crashes for unknown reasons."]
            mods1[9]["warn"] = ["SCRAP EVERYTHING (CORE) \n",
                                "- Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order."]
            mods1[10]["warn"] = ["SCRAP EVERYTHING (ULTIMATE) \n",
                                 "- Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order."]
            mods1[11]["warn"] = ["SHADE GIRL LEATHER OUTFITS \n",
                                 "- Outfits can crash the game while browsing the armor workbench or upon starting a new game due to bad meshes."]
            mods1[12]["warn"] = ["SPRING CLEANING \n",
                                 "- Abandoned and severely outdated mod that breaks precombines and could potentially even break your save file."]
            mods1[13]["warn"] = ["STALKER TEXTURE OVERHAUL \n",
                                 "- Doesn't work due to incorrect folder structure and has a corrupted dds file that causes Create2DTexture crashes."]
            mods1[14]["warn"] = ["TACTICAL TABLET \n",
                                 "- Can cause flickering with certain scopes or crashes while browsing workbenches, most commonly with ECO."]
            mods1[15]["warn"] = ["TRUE NIGHTS \n",
                                 "- Has an invalid Image Space Adapter (IMAD) Record that will corrupt your save memory and has to be manually fixed."]
            mods1[16]["warn"] = ["WEAPONS FRAMEWORK BETA \n",
                                 "- Will randomly cause crashes when used with Tactical Reload and possibly other weapon or combat related mods. \n"
                                 "  Visit Important Patches List article for possible solutions: https://www.nexusmods.com/fallout4/articles/3769"]
            mods1[17]["warn"] = ["WAR OF THE COMMONWEALTH \n",
                                 "- Seems responsible for consistent crashes with specific spawn points or randomly during settlement attacks."]

            if plugins_loaded:
                for line in plugins_list:
                    for elem in mods1.keys():
                        if "File:" not in line and "[FE" not in line and mods1[elem]["mod"] in line:
                            warn = mods1[elem]["warn"]
                            output.writelines([f"[!] Found: {line[0:5].strip()} {''.join(warn)}\n",
                                               "-----\n"])
                            Mod_Trap1 = 0
                        elif "File:" not in line and "[FE" in line and mods1[elem]["mod"] in line:
                            warn = mods1[elem]["warn"]
                            output.writelines([f"[!] Found: {line[0:9].strip()} {''.join(warn)}\n",
                                               "-----\n"])
                            Mod_Trap1 = 0

                if logtext.count("ClassicHolsteredWeapons") >= 3 or "ClassicHolsteredWeapons" in buff_error:
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS\n",
                                       "AUTOSCAN IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!\n",
                                       "You should disable CHW to further confirm this.\n",
                                       "Visit the main crash logs article for additional solutions.\n",
                                       "-----\n"])
                    statM_CHW += 1
                    Mod_Trap1 = 0
                    Buffout_Trap = True
                elif logtext.count("ClassicHolsteredWeapons") >= 2 and ("UniquePlayer.esp" in logtext or "HHS.dll" in logtext or "cbp.dll" in logtext or "Body.nif" in logtext):
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS\n",
                                       "AUTOSCAN IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!\n",
                                       "You should disable CHW to further confirm this.\n",
                                       "Visit the main crash logs article for additional solutions.\n",
                                       "-----\n"])
                    statM_CHW += 1
                    Mod_Trap1 = 0
                    Buffout_Trap = True
                elif "ClassicHolsteredWeapons" in logtext and "d3d11" in buff_error:
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS, BUT...\n",
                                       "AUTOSCAN CANNOT ACCURATELY DETERMINE IF CHW CAUSED THIS CRASH OR NOT.\n",
                                       "You should open CHW's ini file and change IsHolsterVisibleOnNPCs to 0.\n",
                                       "This usually prevents most common crashes with Classic Holstered Weapons.\n",
                                       "-----\n"])
                    output.write("[!] Found: CLASSIC HOLSTERED WEAPONS, BUT...\n")
                    output.write("AUTOSCAN CANNOT ACCURATELY DETERMINE IF CHW CAUSED THIS CRASH OR NOT.\n")
                    output.write("You should open CHW's ini file and change IsHolsterVisibleOnNPCs to 0.\n")
                    output.write("This usually prevents most common crashes with Classic Holstered Weapons.\n")
                    output.write("-----\n")
                    Mod_Trap1 = 0
            if plugins_loaded and Mod_Trap1 == 0:
                output.writelines(["# WARNING: ANY ABOVE DETECTED MODS HAVE A MUCH HIGHER CHANCE TO CRASH YOUR GAME! #\n",
                                   "You can disable any/all of them temporarily to confirm they caused this crash.\n",
                                   "-----\n"])
                statL_scanned += 1
            elif plugins_loaded and Mod_Trap1 == 1:
                output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT MATCH THE CURRENT DATABASE FOR THIS LOG #\n",
                                   "THAT DOESN'T MEAN THERE AREN'T ANY! YOU SHOULD RUN PLUGIN CHECKER IN WRYE BASH.\n",
                                   "Wrye Bash Link: https://www.nexusmods.com/fallout4/mods/20032?tab=files\n",
                                   "-----\n"])
                statL_scanned += 1
            else:
                output.writelines(["# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #\n",
                                   "Autoscan cannot continue. Try scanning a different crash log.\n",
                                   "-----\n"])
                statL_incomplete += 1

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS WITH SOLUTIONS & COMMUNITY PATCHES\n",
                               "====================================================\n"])
            Mod_Trap2 = no_repeat1 = no_repeat2 = 1  # MOD TRAP 2 | NEED 8 SPACES FOR ESL [FE:XXX]

            # Needs 1 empty space as prefix to prevent duplicates.
            mods2 = {}
            mods2[0]["mod"] = " DLCUltraHighResolution.esm"
            mods2[1]["mod"] = " AAF.esm"
            mods2[2]["mod"] = " ArmorKeywords.esm"
            mods2[3]["mod"] = " BTInteriors_Project.esp"
            mods2[4]["mod"] = " CombatZoneRestored.esp"
            mods2[5]["mod"] = " D.E.C.A.Y.esp"
            mods2[6]["mod"] = " EveryonesBestFriend"
            mods2[7]["mod"] = " M8r_Item_Tags"
            mods2[8]["mod"] = " Fo4FI_FPS_fix"
            mods2[9]["mod"] = " BostonFPSFixAIO.esp"
            mods2[10]["mod"] = " FunctionalDisplays.esp"
            mods2[11]["mod"] = " skeletonmaleplayer"
            mods2[12]["mod"] = " skeletonfemaleplayer"
            mods2[13]["mod"] = " Give Me That Bottle.esp"
            mods2[14]["mod"] = " CapsWidget"
            mods2[15]["mod"] = " Homemaker.esm"
            mods2[16]["mod"] = " Horizon.esm"
            mods2[17]["mod"] = " ESPExplorerFO4.esp"
            mods2[18]["mod"] = " LegendaryModification.esp"
            mods2[19]["mod"] = " LooksMenu Customization Compendium.esp"
            mods2[20]["mod"] = " MilitarizedMinutemen.esp"
            mods2[21]["mod"] = " MoreUniques"
            mods2[22]["mod"] = " NAC.es"
            mods2[23]["mod"] = " Northland Diggers New.esp"
            mods2[24]["mod"] = " Project Zeta.esp"
            mods2[25]["mod"] = " Rusty Face Fix"
            mods2[26]["mod"] = " SKKCraftableWeaponsAmmo"
            mods2[27]["mod"] = " SOTS.esp"
            mods2[28]["mod"] = " StartMeUp.esp"
            mods2[29]["mod"] = " SuperMutantRedux.esp"
            mods2[30]["mod"] = " TacticalReload.esm"
            mods2[31]["mod"] = " Creatures and Monsters.esp"
            mods2[32]["mod"] = " ZombieWalkers"

            mods2[0]["warn"] = ["HIGH RESOLUTION DLC. I STRONGLY ADVISE NOT USING IT! \n",
                                "- Right click on Fallout 4 in your Steam Library folder, then select Properties \n",
                                "  Switch to the DLC tab and uncheck / disable the High Resolution Texture Pack",]
            mods2[1]["warn"] = ["ADVANCED ANIMATION FRAMEWORK \n",
                                "- Latest AAF version only available on Moddingham | AAF Tech Support: https://discord.gg/gWZuhMC \n",
                                "  Latest AAF Link (register / login to download): https://www.moddingham.com/viewtopic.php?t=2 \n",
                                "-----\n",
                                "- Looks Menu versions 1.6.20 & 1.6.19 can frequently break adult mod related (erection) morphs \n",
                                "  If you notice AAF realted problems, remove latest version of Looks Menu and switch to 1.6.18"]
            mods2[2]["warn"] = ["ARMOR AND WEAPONS KEYWORDS\n",
                                "- If you don't rely on AWKCR, consider switching to Equipment and Crafting Overhaul \n",
                                "  Better Alternative: https://www.nexusmods.com/fallout4/mods/55503?tab=files \n",
                                "  Patches to remove AWKCR: https://www.nexusmods.com/fallout4/mods/40752"]
            mods2[3]["warn"] = ["BEANTOWN INTERIORS \n",
                                "- Usually causes fps drops, stuttering, crashing and culling issues in multiple locations. \n",
                                "  Patch Link: https://www.nexusmods.com/fallout4/mods/53894?tab=files"]
            mods2[4]["warn"] = ["COMBAT ZONE RESTORED \n",
                                "- Contains few small issues and NPCs usually have trouble navigating the interior space. \n",
                                "  Patch Link: https://www.nexusmods.com/fallout4/mods/59329?tab=files"]
            mods2[5]["warn"] = ["DECAY BETTER GHOULS \n",
                                "- You have to install DECAY Redux patch to prevent its audio files from crashing the game. \n",
                                "  Patch Link: https://www.nexusmods.com/fallout4/mods/59025?tab=files"]
            mods2[6]["warn"] = ["EVERYONE'S BEST FRIEND \n",
                                "- This mod needs a compatibility patch to properly work with the Unofficial Patch (UFO4P). \n",
                                "  Patch Link: https://www.nexusmods.com/fallout4/mods/43409?tab=files"]
            mods2[7]["warn"] = ["FALLUI ITEM SORTER (OLD) \n",
                                "- This is an outdated item tagging / sorting patch that can cause crashes or conflicts in all kinds of situations. \n",
                                "  I strongly recommend to instead generate your own sorting patch and place it last in your load order. \n",
                                "  That way, you won't experience any conflicts / crashes and even modded items will be sorted. \n",
                                "  Generate Sorting Patch With This: https://www.nexusmods.com/fallout4/mods/48826?tab=files"]
            mods2[8]["warn"] = ["FO4FI FPS FIX \n",
                                "- This mod is severely outdated and will cause crashes even with compatibility patches. \n",
                                "  Better Alternative: https://www.nexusmods.com/fallout4/mods/46403?tab=files"]
            mods2[9]["warn"] = ["BOSTON FPS FIX \n",
                                "- This mod is severely outdated and will cause crashes even with compatibility patches. \n",
                                "  Better Alternative: https://www.nexusmods.com/fallout4/mods/46403?tab=files"]
            mods2[10]["warn"] = ["FUNCTIONAL DISPLAYS \n",
                                 "- Frequently causes object model (nif) related crashes and this needs to be manually corrected. \n",
                                 "  Advised Fix: Open its Meshes folder and delete everything inside EXCEPT for the Functional Displays folder."]
            mods2[11]["warn"] = ["GENDER SPECIFIC SKELETONS (MALE) \n",
                                 "- High chance to cause a crash when starting a new game or during the game intro sequence. \n",
                                 "  Advised Fix: Enable the mod only after leaving Vault 111. Existing saves shouldn't be affected."]
            mods2[12]["warn"] = ["GENDER SPECIFIC SKELETONS (FEMALE) \n",
                                 "- High chance to cause a crash when starting a new game or during the game intro sequence. \n",
                                 "  Advised Fix: Enable the mod only after leaving Vault 111. Existing saves shouldn't be affected."]
            mods2[13]["warn"] = ["GIVE ME THAT BOTTLE \n",
                                 "- Can rarely cause crashes in the Pip-Boy inventory menu. Switch to Fill'em Up Again instead. \n",
                                 "  Better Alternative: https://www.nexusmods.com/fallout4/mods/12674?tab=files"]
            mods2[14]["warn"] = ["HUD CAPS \n",
                                 "- Often breaks the Save / Quicksave function due to poor script implementation. \n",
                                 "  Advised Fix: Download fixed pex file and place it into HUDCaps/Scripts folder. \n",
                                 "  Fix Link: https://drive.google.com/file/d/1egmtKVR7mSbjRgo106UbXv_ySKBg5az2"]
            mods2[15]["warn"] = ["HOMEMAKER \n",
                                 "- Causes a crash while scrolling over Military / BoS fences in the Settlement Menu. \n",
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/41434?tab=files"]
            mods2[16]["warn"] = ["HORIZON \n",
                                 "- I highly recommend installing these patches for 1.8.7 until newer version is released. \n",
                                 "  Patch Link 1: https://www.nexusmods.com/fallout4/mods/65911?tab=files \n",
                                 "  Patch Link 2: https://www.nexusmods.com/fallout4/mods/61998?tab=files"]
            mods2[17]["warn"] = ["IN GAME ESP EXPLORER \n",
                                 "- Can cause a crash when pressing F10 due to a typo in the INI settings. \n",
                                 "  Fix Link: https://www.nexusmods.com/fallout4/mods/64752?tab=files \n",
                                 "  OR Switch To: https://www.nexusmods.com/fallout4/mods/56922?tab=files"]
            mods2[18]["warn"] = ["LEGENDARY MODIFICATION \n",
                                 "- Old mod plagued with all kinds of bugs and crashes, can conflict with some modded weapons. \n",
                                 "  Better Alternative: https://www.nexusmods.com/fallout4/mods/55503?tab=files"]
            mods2[19]["warn"] = ["LOOKS MENU CUSTOMIZATION COMPENDIUM \n",
                                 "- Apparently breaks the original Looks Menu mod by turning off some important values. \n",
                                 "  Fix Link: https://www.nexusmods.com/fallout4/mods/56465?tab=files"]
            mods2[20]["warn"] = ["MILITARIZED MINUTEMEN \n"
                                 "- Can occasionally crash the game due to a broken mesh on some minutemen outfits. \n"
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/55301?tab=files"]
            mods2[21]["warn"] = ["MORE UNIQUE WEAPONS EXPANSION \n",
                                 "- Causes crashes due to broken precombines and compatibility issues with other weapon mods. \n",
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/54848?tab=files"]
            mods2[22]["warn"] = ["NATURAL AND ATMOSPHERIC COMMONWEALTH \n",
                                 "- If you notice weird looking skin tones with either NAC or NACX, install this patch. \n",
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/57052?tab=files"]
            mods2[23]["warn"] = ["NORTHLAND DIGGERS RESOURCES \n",
                                 "- Contains various bugs and issues that can cause crashes or negatively affect other mods. \n",
                                 "  Fix Link: https://www.nexusmods.com/fallout4/mods/53395?tab=files"]
            mods2[24]["warn"] = ["PROJECT ZETA \n",
                                 "- Invasion quests seem overly buggy or trigger too frequently, minor sound issues. \n",
                                 "  Fix Link: https://www.nexusmods.com/fallout4/mods/65166?tab=files"]
            mods2[25]["warn"] = ["RAIDER OVERHAUL \n",
                                 "- Old mod that requires several patches to function as intended. Use ONE Version instead. \n",
                                 "  Upated ONE Version: https://www.nexusmods.com/fallout4/mods/51658?tab=files"]
            mods2[26]["warn"] = ["RUSTY FACE FIX \n",
                                 "- Can cause script lag or even crash the game in very rare cases. Switch to REDUX Version instead. \n",
                                 "  Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/64270?tab=files"]
            mods2[27]["warn"] = ["SKK CRAFT WEAPONS AND SCRAP AMMO \n",
                                 "- Version 008 is incompatible with AWKCR and will cause crashes while saving the game. \n",
                                 "  Advised Fix: Use Version 007 or remove AWKCR and switch to Equipment and Crafting Overhaul instead."]
            mods2[28]["warn"] = ["SOUTH OF THE SEA \n",
                                 "- Very unstable mod that consistently and frequently causes strange problems and crashes. \n",
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/59792?tab=files"]
            mods2[29]["warn"] = ["START ME UP \n",
                                 "- Abandoned mod that can cause infinite loading and other problems. Switch to REDUX Version instead. \n",
                                 "  Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/56984?tab=files",]
            mods2[29]["warn"] = ["SUPER MUTANT REDUX \n",
                                 "- Causes crashes at specific locations or with certain Super Muntant enemies and items. \n",
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/51353?tab=files"]
            mods2[30]["warn"] = ["TACTICAL RELOAD \n",
                                 "- Can cause weapon and combat related crashes. TR Expansion For ECO is highly recommended. \n",
                                 "  TR Expansion For ECO Link: https://www.nexusmods.com/fallout4/mods/62737"]
            mods2[31]["warn"] = ["UNIQUE NPCs CREATURES AND MONSTERS \n",
                                 "- Causes crashes and breaks precombines at specific locations, some creature spawns are too frequent. \n",
                                 "  Patch Link: https://www.nexusmods.com/fallout4/mods/48637?tab=files"]
            mods2[32]["warn"] = ["ZOMBIE WALKERS \n",
                                 "- Version 2.6.3 contains a resurrection script that will regularly crash the game. \n",
                                 "  Advised Fix: Make sure you're using the 3.0 Beta version of this mod or newer."]

            if plugins_loaded:
                for line in plugins_list:
                    for elem in mods2.keys():
                        if "File:" not in line and "[FE" not in line and mods2[elem]["mod"] in line:
                            warn = mods2[elem]["warn"]
                            output.writelines([f"[!] Found: {line[0:5].strip()} {warn}\n",
                                               "-----\n"])
                            Mod_Trap2 = 0
                        elif "File:" not in line and "[FE" in line and mods2[elem]["mod"] in line:
                            warn = mods2[elem]["warn"]
                            output.writelines([f"[!] Found: {line[0:9].strip()} {warn}\n",
                                               "-----\n"])
                            Mod_Trap2 = 0
                    if no_repeat1 == 1 and "File:" not in line and ("Depravity" or "FusionCityRising" or "HotC" or "OutcastsAndRemnants" or "ProjectValkyrie") in line:
                        output.writelines([f"[!] Found: {line[0:9].strip()} THUGGYSMURF QUEST MOD\n",
                                           "If you have Depravity, Fusion City Rising, HOTC, Outcasts and Remnants and/or Project Valkyrie\n",
                                           "install this patch with facegen data, fully generated precomb/previs data and several tweaks.\n",
                                           "Patch Link: https://www.nexusmods.com/fallout4/mods/56876?tab=files\n",
                                           "-----\n"])
                        no_repeat1 = Mod_Trap2 = 0
                    if no_repeat1 == 1 and "File:" not in line and ("CaN.esm" or "AnimeRace_Nanako.esp") in line:
                        output.writelines([f"[!] Found: {line[0:9].strip()} CUSTOM RACE SKELETON MOD\n",
                                           "If you have AnimeRace NanakoChan or Crimes Against Nature, install the Race Skeleton Fixes.\n",
                                           "Skeleton Fixes Link (READ THE DESCRIPTION): https://www.nexusmods.com/fallout4/mods/56101\n"])
                        no_repeat2 = Mod_Trap2 = 0

                if "FallSouls.dll" in logtext:
                    output.writelines([f"[!] Found: FALLSOULS UNPAUSED GAME MENUS\n",
                                       "Occasionally breaks the Quests menu, can cause crashes while changing MCM settings.\n",
                                       "Advised Fix: Toggle PipboyMenu in FallSouls MCM settings or completely reinstall the mod.\n",
                                       "-----\n"])
                    Mod_Trap2 = 0

            nopluginlist = "# BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #\nAutoscan cannot continue. Try scanning a different crash log.\n-----\n"
            if plugins_loaded and Mod_Trap2 == 0:
                output.writelines([f"# AUTOSCAN FOUND PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                   "[Due to inherent limitations, Auto-Scan will continue detecting certain mods\n",
                                   "even if fixes or patches for them are already installed. You can ignore these.]\n",
                                   "-----\n"])

            elif plugins_loaded and Mod_Trap2 == 1:
                output.writelines([f"# AUTOSCAN FOUND NO PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                   "-----\n"])
            elif plugins_loaded is False:
                output.write(nopluginlist)

            output.writelines(["FOR FULL LIST OF IMPORTANT PATCHES AND FIXES FOR THE BASE GAME AND MODS,\n",
                               "VISIT THIS ARTICLE: https://www.nexusmods.com/fallout4/articles/3769\n",
                               "-----\n"])

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS PATCHED THROUGH OPC INSTALLER...\n",
                               "====================================================\n"])
            Mod_Trap3 = 1  # MOD TRAP 3 | NEED 8 SPACES FOR ESL [FE:XXX]

            # Needs 1 empty space as prefix to prevent duplicates.
            mods3 = {}
            mods3[0]["mod"] = " Beyond the Borders"
            mods3[1]["mod"] = " Deadly Commonwealth Expansion"
            mods3[2]["mod"] = " Dogmeat and Strong Armor"
            mods3[3]["mod"] = " DoYourDamnJobCodsworth"
            mods3[4]["mod"] = " ConcordEXPANDED"
            mods3[5]["mod"] = " HagenEXPANDED"
            mods3[6]["mod"] = " GlowingSeaEXPANDED"
            mods3[7]["mod"] = " SalemEXPANDED"
            mods3[8]["mod"] = " SwampsEXPANDED"
            mods3[9]["mod"] = " _hod"
            mods3[10]["mod"] = " ImmersiveBeantown"
            mods3[11]["mod"] = " CovenantComplex"
            mods3[12]["mod"] = " GunnersPlazaInterior"
            mods3[13]["mod"] = " ImmersiveHubCity"
            mods3[14]["mod"] = " Immersive_Lexington"
            mods3[15]["mod"] = " Immersive Nahant"
            mods3[16]["mod"] = " Immersive S Boston"
            mods3[17]["mod"] = " MutilatedDeadBodies"
            mods3[18]["mod"] = " Vault4.esp"
            mods3[19]["mod"] = " atlanticofficesf23"
            mods3[20]["mod"] = " Minutemen Supply Caches"
            mods3[21]["mod"] = " moreXplore"
            mods3[22]["mod"] = " NEST_BUNKER_PROJECT"
            mods3[23]["mod"] = " Raider Children.esp"
            mods3[24]["mod"] = " sectorv"
            mods3[25]["mod"] = " SettlementShelters"
            mods3[25]["mod"] = " subwayrunnerdynamiclighting"
            mods3[26]["mod"] = " 3DNPC_FO4Settler.esp"
            mods3[27]["mod"] = " 3DNPC_FO4.esp"
            mods3[28]["mod"] = " The Hollow"
            mods3[29]["mod"] = " nvvault1080"
            mods3[30]["mod"] = " Vertibird Faction Paint Schemes"
            mods3[31]["mod"] = " MojaveImports.esp"
            mods3[32]["mod"] = " Firelance2.5"
            mods3[33]["mod"] = " zxcMicroAdditions"

            mods3[0]["name"] = "Beyond the Borders"
            mods3[1]["name"] = "Deadly Commonwealth Expansion"
            mods3[2]["name"] = "Dogmeat and Strong Armor"
            mods3[3]["name"] = "Do Your Damn Job Codsworth"
            mods3[4]["name"] = "Concord Expanded"
            mods3[5]["name"] = "Fort Hagen Expanded"
            mods3[6]["name"] = "Glowing Sea Expanded"
            mods3[7]["name"] = "Salem Expanded"
            mods3[8]["name"] = "Swamps Expanded"
            mods3[9]["name"] = "Hearts Of Darkness"
            mods3[10]["name"] = "Immersive Beantown Brewery"
            mods3[11]["name"] = "Immersive Covenant Compound"
            mods3[12]["name"] = "Immersive Gunners Plaza"
            mods3[13]["name"] = "Immersive Hub City"
            mods3[14]["name"] = "Immersive & Extended Lexington"
            mods3[15]["name"] = "Immersive & Extended Nahant"
            mods3[16]["name"] = "Immersive Military Checkpoint"
            mods3[17]["name"] = "Mutilated Dead Bodies"
            mods3[18]["name"] = "Fourville (Vault 4)"
            mods3[19]["name"] = "Lost Building of Atlantic"
            mods3[20]["name"] = "Minutemen Supply Caches"
            mods3[21]["name"] = "MoreXplore"
            mods3[22]["name"] = "NEST BUNKER PROJECT"
            mods3[23]["name"] = "Raider Children"
            mods3[24]["name"] = "Sector Five - Rise and Fall"
            mods3[25]["name"] = "Settlement Shelters"
            mods3[26]["name"] = "Subway Runner (Dynamic Lights)"
            mods3[26]["name"] = "Settlers of the Commonwealth"
            mods3[27]["name"] = "Tales from the Commonwealth"
            mods3[28]["name"] = "The Hollow"
            mods3[29]["name"] = "Vault 1080 (Vault 80)"
            mods3[30]["name"] = "Vertibird Faction Paint Schemes"
            mods3[31]["name"] = "Wasteland Imports (Mojave Imports)"
            mods3[32]["name"] = "Xander's Aid"
            mods3[33]["name"] = "ZXC Micro Additions"

            """List_Mods3 = [" Beyond the Borders",
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
                          " zxcMicroAdditions"]"""

            """List_Warn3 = ["Beyond the Borders",
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
                          "ZXC Micro Additions"]"""

            if plugins_loaded:
                for line in plugins_list:
                    for elem in mods3.keys():
                        if "File:" not in line and "[FE" not in line and mods3[elem]["mod"] in line:
                            # order_elem = List_Mods3.index(elem)
                            name = mods3[elem]["name"]
                            output.write(f"- Found: {line[0:5].strip()} {name}\n")
                            Mod_Trap3 = 0
                        elif "File:" not in line and "[FE" in line and mods3[elem]["mod"] in line:
                            name = mods3[elem]["name"]
                            output.write(f"- Found: {line[0:9].strip()} {name}\n")
                            Mod_Trap3 = 0
            if plugins_loaded and Mod_Trap3 == 0:
                output.writelines(["-----\n",
                                  "FOR PATCH REPOSITORY THAT PREVENTS CRASHES AND FIXES PROBLEMS IN THESE AND OTHER MODS,\n",
                                   "VISIT OPTIMIZATION PATCHES COLLECTION: https://www.nexusmods.com/fallout4/mods/54872\n",
                                   "-----\n"])
            elif plugins_loaded and Mod_Trap3 == 1:
                output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT ARE ALREADY PATCHED THROUGH OPC INSTALLER #\n",
                                  "-----\n"])
            elif plugins_loaded is False:
                output.write(nopluginlist)

            # ===========================================================

            output.writelines(["====================================================\n",
                               "CHECKING IF IMPORTANT PATCHES & FIXES ARE INSTALLED\n",
                               "====================================================\n"])

            gpu_amd = False
            gpu_nvidia = False
            for line in loglines:
                if "GPU" in line and "Nvidia" in line:
                    gpu_nvidia = True
                    break
                if "GPU" in line and "AMD" in line:
                    gpu_amd = True
                    break

            output.writelines(["IF YOU'RE USING DYNAMIC PERFORMANCE TUNER AND/OR LOAD ACCELERATOR,\n",
                               "remove these mods completely and switch to High FPS Physics Fix!\n",
                               "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files\n",
                               "-----\n"])

            if CLAS_config.getboolean("MAIN", "FCX Mode"):
                output.writelines(["* NOTICE: FCX MODE IS ENABLED. AUTO-SCANNER MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *\n",
                                  "[ To disable game folder / mod files detection, set FCX Mode = false in Scan Crashlogs.ini ]\n",
                                   "-----\n"])

                if info.VR_EXE.is_file() and info.VR_Buffout.is_file():
                    output.write("*Buffout 4 VR Version* is (manually) installed. \n-----\n")
                elif info.VR_EXE.is_file() and not info.VR_Buffout.is_file():
                    output.writelines(["# BUFFOUT 4 FOR VR VERSION ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                      "# This is a mandatory Buffout 4 port for the VR Version of Fallout 4.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/64880?tab=files\n"])

                if (info.F4CK_EXE.is_file() and os.path.exists(info.F4CK_Fixes)) or (isinstance(info.Game_Path, str) and Path(info.Game_Path).joinpath("winhttp.dll").is_file()):
                    output.write("*Creation Kit Fixes* is (manually) installed. \n-----\n")
                elif info.F4CK_EXE.is_file() and not os.path.exists(info.F4CK_Fixes):
                    output.writelines(["# CREATION KIT FIXES ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                      "This is a highly recommended patch for the Fallout 4 Creation Kit.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/51165?tab=files\n",
                                       "-----\n"])

            if plugins_loaded:
                if any("CanarySaveFileMonitor" in elem for elem in plugins_list):
                    output.write("*Canary Save File Monitor* is installed. \n-----\n")
                else:
                    output.writelines(["# CANARY SAVE FILE MONITOR ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                      "This is a highly recommended mod that can detect save file corrpution.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/44949?tab=files\n",
                                       "-----\n"])

                if "HighFPSPhysicsFix.dll" in logtext or "HighFPSPhysicsFixVR.dll" in logtext:
                    output.write("*High FPS Physics Fix* is installed. \n-----\n")
                else:
                    output.writelines(["# HIGH FPS PHYSICS FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                      "This is a mandatory patch / fix that prevents game engine problems.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files\n",
                                       "-----\n"])

                if any("PPF.esm" in elem for elem in plugins_list):
                    output.write("*Previs Repair Pack* is installed. \n-----\n")
                else:
                    output.writelines(["# PREVIS REPAIR PACK ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "This is a highly recommended mod that can improve performance.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/46403?tab=files\n",
                                       "-----\n"])

                if any("Unofficial Fallout 4 Patch.esp" in elem for elem in plugins_list):
                    output.write("*Unofficial Fallout 4 Patch* is installed. \n-----\n")
                else:
                    output.writelines(["# UNOFFICIAL FALLOUT 4 PATCH ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "If you own all DLCs, make sure that the Unofficial Patch is installed.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/4598?tab=files\n",
                                       "-----\n"])

                if "vulkan-1.dll" in logtext and gpu_amd:
                    output.write("Vulkan Renderer is installed. \n-----\n")
                elif logtext.count("vulkan-1.dll") == 0 and gpu_amd and not gpu_nvidia:
                    output.writelines(["# VULKAN RENDERER ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "This is a highly recommended mod that can improve performance on AMD GPUs.\n",
                                       "Installation steps can be found in 'How To Read Crash Logs' PDF / Document.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/48053?tab=files\n",
                                       "-----\n"
                                       "Installation steps can be found in 'How To Read Crash Logs' PDF / Document.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/48053?tab=files\n",
                                       "-----\n"])

                if "WeaponDebrisCrashFix.dll" in logtext and gpu_nvidia:
                    output.write("*Weapon Debris Crash Fix* is installed. \n-----\n")
                elif "WeaponDebrisCrashFix.dll" in logtext and not gpu_nvidia and gpu_amd:
                    output.writelines(["*Weapon Debris Crash Fix* is installed, but...\n",
                                       "# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #\n",
                                       "Weapon Debris Crash Fix is only required for Nvidia GPUs (NOT AMD / OTHER)\n",
                                       "-----\n"])
                if "WeaponDebrisCrashFix.dll" not in logtext and gpu_nvidia:
                    output.writelines(["# WEAPON DEBRIS CRASH FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "This is a mandatory patch / fix for players with Nvidia graphics cards.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/48078?tab=files\n",
                                       "-----\n"])

                if "NVIDIA_Reflex.dll" in logtext and gpu_nvidia:
                    output.write("*Nvidia Reflex Support* is installed. \n-----\n")
                elif "NVIDIA_Reflex.dll" in logtext and not gpu_nvidia and gpu_amd:
                    output.writelines(["*Nvidia Reflex Support* is installed, but...\n",
                                       "# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #\n",
                                       "Nvidia Reflex Support is only required for Nvidia GPUs (NOT AMD / OTHER)\n",
                                       "-----\n"])
                if "NVIDIA_Reflex.dll" not in logtext and gpu_nvidia:
                    output.writelines(["# NVIDIA REFLEX SUPPORT ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "This is a highly recommended mod that can reduce render latency.\n",
                                       "Link: https://www.nexusmods.com/fallout4/mods/64459?tab=files\n",
                                       "-----\n"])
            else:
                output.write(nopluginlist)

            output.writelines(["====================================================\n",
                               "SCANNING THE LOG FOR SPECIFIC (POSSIBLE) CUPLRITS...\n",
                               "====================================================\n"])

            list_DETPLUGINS = []
            list_DETFORMIDS = []
            list_DETFILES = []
            list_ALLPLUGINS = []

            if ("f4se_1_10_163.dll" in logtext or "f4sevr_1_2_72.dll" in logtext) and "steam_api64.dll" in logtext:
                pass
            else:
                output.writelines(["# CRASH LOG FAILED TO LIST MODULES OR F4SE IS NOT INSTALLED! #\n",
                                   "CHECK IF SCRIPT EXTENDER (F4SE) IS CORRECTLY INSTALLED! \n",
                                   "Script Extender Link: https://f4se.silverlock.org \n",
                                   "-----\n"])

            for line in loglines:
                if len(line) >= 6 and "]" in line[4]:
                    list_ALLPLUGINS.append(line.strip())
                if len(line) >= 7 and "]" in line[5]:
                    list_ALLPLUGINS.append(line.strip())
                if len(line) >= 10 and "]" in line[8]:
                    list_ALLPLUGINS.append(line.strip())
                if len(line) >= 11 and "]" in line[9]:
                    list_ALLPLUGINS.append(line.strip())

            output.write("LIST OF (POSSIBLE) PLUGIN CULRIPTS:\n")
            for line in loglines:
                if "File:" in line and "Fallout4.esm" not in line:
                    line = line.replace("File: ", "")
                    line = line.replace('"', '')
                    list_DETPLUGINS.append(line.strip())

            list_DETPLUGINS = list(filter(None, list_DETPLUGINS))  # Remove empty elements in list.
            list_remove = ["Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm"]
            for elem in list_remove:
                if elem in list_DETPLUGINS:
                    list_DETPLUGINS.remove(elem)

            list_DETPLUGINS = Counter(list_DETPLUGINS)  # list(dict.fromkeys(list_DETPLUGINS))
            PL_result = []

            for elem in list_ALLPLUGINS:
                PL_matches = []
                for item in list_DETPLUGINS:
                    if item in elem:
                        PL_matches.append(item)
                if PL_matches:
                    PL_result.append(PL_matches)
                    output.write(f"- {' '.join(PL_matches)} : {list_DETPLUGINS[item]}\n")  # type: ignore

            if not PL_result:
                output.writelines(["* AUTOSCAN COULDN'T FIND ANY PLUGIN CULRIPTS *\n",
                                   "-----\n"])
            else:
                output.writelines(["-----\n",
                                   "[Last number counts how many times each plugin culprit shows up in the crash log.]\n",
                                   "These Plugins were caught by Buffout 4 and some of them might be responsible for this crash.\n",
                                   "You can try disabling these plugins and recheck your game, though this method can be unreliable.\n",
                                   "-----\n"])

            # ===========================================================

            output.write("LIST OF (POSSIBLE) FORM ID CULRIPTS:\n")
            for line in loglines:
                if "Form ID:" in line or "FormID:" in line and "0xFF" not in line:
                    line = line.replace("0x", "")
                    if plugins_loaded:
                        line = line.replace("Form ID: ", "")
                        line = line.replace("FormID: ", "")
                        line = line.strip()
                        ID_Only = line
                        for elem in plugins_list:
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

            list_DETFORMIDS = sorted(list_DETFORMIDS)
            list_DETFORMIDS = list(dict.fromkeys(list_DETFORMIDS))
            for elem in list_DETFORMIDS:
                output.write(f"{elem}\n")

            if not list_DETFORMIDS:
                output.writelines(["* AUTOSCAN COULDN'T FIND ANY FORM ID CULRIPTS *\n",
                                   "-----\n"])
            else:
                output.writelines(["-----\n",
                                   "These Form IDs were caught by Buffout 4 and some of them might be related to this crash.\n",
                                   "You can try searching any listed Form IDs in FO4Edit and see if they lead to relevant records.\n",
                                   "-----\n"])

            # ===========================================================

            List_Files = [".bgsm", ".bto", ".btr", ".dds", ".fuz", ".hkb", ".hkx", ".ini", ".nif", ".pex", ".swf", ".strings", ".txt", ".uvd", ".wav", ".xwm", "data\\", "data/"]
            List_Exclude = ['""', "...", "[FE:"]

            output.write("LIST OF DETECTED (NAMED) RECORDS:\n")
            List_Records = []
            for line in loglines:
                if "Name" in line or "EditorID:" in line or any(elem in line.lower() for elem in List_Files):
                    if not any(elem in line for elem in List_Exclude):
                        line = line.replace('"', '')
                        List_Records.append(f"{line.strip()}\n")

            List_Records = sorted(List_Records)
            List_Records = Counter(List_Records)  # list(dict.fromkeys(List_Records))
            for item in List_Records:
                output.write("{} : {} \n".format(item.replace("\n", ""), List_Records[item]))

            if not List_Records:
                output.writelines(["* AUTOSCAN COULDN'T FIND ANY NAMED RECORDS *\n",
                                   "-----\n"])
            else:
                output.writelines(["-----\n",
                                   "[Last number counts how many times each named record shows up in the crash log.]\n",
                                   "These records were caught by Buffout 4 and some of them might be related to this crash.\n",
                                   "Named records should give extra information on involved game objects and record types.\n",
                                   "-----\n"])

            output.writelines(["FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,\n",
                               "VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115\n",
                               "===============================================================================\n",
                               f"END OF AUTOSCAN | Author / Made By: Poet#9800 (DISCORD) | {CLAS_Date}\n",
                               "CONTRIBUTORS | evildarkarchon | kittivelae | AtomicFallout757\n",
                               "CLAS | https://www.nexusmods.com/fallout4/mods/56255"])

        # MOVE UNSOLVED LOGS TO SPECIAL FOLDER
        if CLAS_config.getboolean("MAIN", "Move Unsolved"):
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
            os.chmod(info.Buffout_INI, stat.S_IWRITE)
            os.rename(info.Buffout_INI, info.Buffout_TOML)
        except FileExistsError:
            os.remove(info.Buffout_TOML)
            os.rename(info.Buffout_INI, info.Buffout_TOML)

    # ========================== LOG END ==========================
    time.sleep(0.5)
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

    # ============ CHECK FOR EMPTY (FAULTY) AUTO-SCANS ============
    list_SCANFAIL = []
    for file in glob(f"{SCAN_folder}/crash-*-AUTOSCAN.md"):
        line_count = 0
        scanname = str(file)
        with open(file, encoding="utf-8", errors="ignore") as autoscan_log:
            for line in autoscan_log:
                if line != "\n":
                    line_count += 1
        if int(line_count) <= 20:  # Adjust if necessary. Failed scans are usually 16 lines.
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
    print("\nScanned all available logs in", (str(time.perf_counter() - 0.5 - Start_Time)[:7]), "seconds.")
    print("Number of Scanned Logs (No Autoscan Errors): ", statL_scanned)
    print("Number of Incomplete Logs (No Plugins List): ", statL_incomplete)
    print("Number of Failed Logs (Autoscan Can't Scan): ", statL_failed)
    print("Number of Very Old / Wrong Formatting Logs : ", statL_veryold)
    print("(Set Stat Logging to true in Scan Crashlogs.ini for additional stats.)")
    print("-----")
    if CLAS_config.getboolean("MAIN", "Stat Logging") is True:
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
        print("Logs with C++ Redist Crash...............", statC_Redist)
        print("Logs with Grid Scrap Crash...............", statC_GridScrap)
        print("Logs with Map Marker Crash...............", statC_MapMarker)
        print("Logs with Mesh (NIF) Crash...............", statC_NIF)
        print("Logs with Precombines Crash..............", statC_Precomb)
        print("Logs with Texture (DDS) Crash............", statC_Texture)
        print("Logs with Material (BGSM) Crash..........", statC_BGSM)
        print("Logs with BitDefender Crash..............", statC_BitDefender)
        print("Logs with NPC Pathing Crash..............", statC_NPCPathing)
        print("Logs with Audio Driver Crash.............", statC_Audio)
        print("Logs with Body Physics Crash.............", statC_BodyPhysics)
        print("Logs with Leveled List Crash.............", statC_LeveledList)
        print("Logs with Plugin Limit Crash.............", statC_PluginLimit)
        print("Logs with Plugin Order Crash.............", statC_LoadOrder)
        print("Logs with MO2 Extractor Crash............", statC_MO2Unpack)
        print("Logs with Nvidia Debris Crash............", statC_NVDebris)
        print("Logs with Nvidia Driver Crash............", statC_NVDriver)
        print("Logs with Vulkan Memory Crash............", statC_VulkanMem)
        print("Logs with Vulkan Settings Crash..........", statC_VulkanSet)
        print("Logs with Console Command Crash..........", statC_ConsoleCommands)
        print("Logs with Game Corruption Crash..........", statC_GameCorruption)
        print("Logs with Water Collision Crash..........", statC_Water)
        print("Logs with Particle Effects Crash.........", statC_Particles)
        print("Logs with Player Character Crash.........", statC_Player)
        print("Logs with Animation / Physics Crash......", statC_AnimationPhysics)
        print("Logs with Archive Invalidation Crash.....", statC_Invalidation)
        print("-----")
        print("Crashes caused by Clas. Hols. Weapons....", statM_CHW)
        print("-----")
        print("Logs with *[Creation Club Crash].........", statU_CClub)
        print("Logs with *[Item Crash]..................", statU_Item)
        print("Logs with *[Save Crash]..................", statU_Save)
        print("Logs with *[Input Crash].................", statU_Input)
        print("Logs with *[Looks Menu Crash]............", statU_LooksMenu)
        print("Logs with *[NPC Patrol Crash]............", statU_Patrol)
        print("Logs with *[Ammo Counter Crash]..........", statU_HUDAmmo)
        print("Logs with *[NPC Projectile Crash]........", statU_Projectile)
        print("*Unsolved, see How To Read Crash Logs PDF")
        print("===========================================")
    return


if __name__ == "__main__":  # AKA only autorun when NOT imported.
    import argparse
    parser = argparse.ArgumentParser(prog="Buffout 4 Crash Log Auto-Scanner", description="All command-line options are saved to the INI file.")
    # Argument values will simply change INI values since that requires the least refactoring
    # I will figure out a better way in a future iteration, this iteration simply mimics the GUI. - evildarkarchon
    parser.add_argument("--fcx-mode", action=argparse.BooleanOptionalAction, help="Enable (or disable) FCX mode")
    parser.add_argument("--imi-mode", action=argparse.BooleanOptionalAction, help="Enable (or disable) IMI mode")
    parser.add_argument("--stat-logging", action=argparse.BooleanOptionalAction, help="Enable (or disable) Stat Logging")
    parser.add_argument("--move-unsolved", action=argparse.BooleanOptionalAction, help="Enable (or disable) moving unsolved logs to a aeparate directory")
    parser.add_argument("--ini-path", type=Path, help="Set the directory that stores the game's INI files.")
    parser.add_argument("--scan-path", type=Path, help="Set which directory to scan")
    args = parser.parse_args()

    scan_path: Path = args.scan_path  # VSCode gives me type errors because args.* is set at runtime (doesn't know what types it's dealing with).
    ini_path: Path = args.ini_path  # Using intermediate variables with type annotations to satisfy it.

    # Default output value for an argparse.BooleanOptionalAction is None, and so fails the isinstance check.
    # So it will respect current INI values if not specified on the command line.
    if isinstance(args.fcx_mode, bool) and not args.fcx_mode == CLAS_config.getboolean("MAIN", "FCX Mode"):
        write_ini_value_to_file("FCX Mode", str(args.fcx_mode).lower())

    if isinstance(args.imi_mode, bool) and not args.imi_mode == CLAS_config.getboolean("MAIN", "IMI Mode"):
        write_ini_value_to_file("IMI Mode", str(args.imi_mode).lower())

    if isinstance(args.stat_logging, bool) and not args.stat_logging == CLAS_config.getboolean("MAIN", "Stat Logging"):
        write_ini_value_to_file("Stat Logging", str(args.stat_logging).lower())

    if isinstance(args.move_unsolved, bool) and not args.move_unsolved == CLAS_config.getboolean("MAIN", "Move Unsolved"):
        write_ini_value_to_file("Move Unsolved", str(args.move_unsolved).lower())

    if isinstance(ini_path, Path) and ini_path.resolve().is_dir() and not str(ini_path) == CLAS_config.get("MAIN", "INI Path"):
        write_ini_value_to_file("INI Path", str(Path(ini_path).resolve()))

    if isinstance(scan_path, Path) and scan_path.resolve().is_dir() and not str(scan_path) == CLAS_config.get("MAIN", "Scan Path"):
        write_ini_value_to_file("Scan Path", str(Path(scan_path).resolve()))

    CLAS_Scan = scan_logs()
    sys.stdout.close()  # Do we still need this line since we're no longer using stdout to write to the scan file? - evildarkarchon
    os.system("pause")
