import os
import sys
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
except (ImportError, ModuleNotFoundError):
    subprocess.run(['pip', 'install', 'requests'], shell=True)

''' AUTHOR NOTES (POET):
- In cases where output.write is used instead of output.writelines, this is so I can more easily copy-paste specific content.
- (..., encoding="utf-8", errors="ignore") needs to go with every opened file because unicode errors are a bitch.
- Comments marked as RESERVED in all scripts are intended for future updates, do not edit / move / remove.
'''

# =================== CLAS INI FILE ===================
def clas_ini_create():
    if not os.path.exists("Scan Crashlogs.ini"):  # INI FILE FOR AUTO-SCANNER
        INI_Settings = ["[MAIN]\n",
                        "# This file contains configuration settings for both Scan_Crashlogs.py and Crash Log Auto Scanner.exe \n",
                        "# Set to true if you want Auto-Scanner to check Python modules and if the latest version is installed. \n",
                        "Update Check = true\n\n",
                        "# FCX - File Check eXtended | If Auto-Scanner fails to scan your logs, revert this setting back to false. \n",
                        "# Set to true if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly. \n",
                        "FCX Mode = true\n\n",
                        "# IMI - Ignore Manual Installation | Set to true if you want Auto-Scanner to hide all manual installation warnings. \n",
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


clas_ini_create()
# Use optionxform = str to preserve INI formatting. | Set comment_prefixes to unused char to keep INI comments.
CLAS_config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="$")
CLAS_config.optionxform = str  # type: ignore
CLAS_config.read("Scan Crashlogs.ini")
CLAS_Date = "170223"  # DDMMYY
CLAS_Current = "CLAS v6.35"
CLAS_Updated = False


def clas_ini_update(section: str, value: str):  # Convenience function for a code snippet that's repeated many times throughout both scripts.
    if isinstance(section, str) and isinstance(value, str):
        CLAS_config.set("MAIN", section, value)
    else:
        CLAS_config.set("MAIN", str(section), str(value))

    with open("Scan Crashlogs.ini", "w+", encoding="utf-8", errors="ignore") as INI_AUTOSCAN:
        CLAS_config.write(INI_AUTOSCAN)


# =================== WARNING MESSAGES ==================
# Can change first line to """\ to remove spacing.
Warn_CLAS_Outdated_Scanner = """
[!] WARNING : YOUR AUTO SCANNER VERSION IS OUT OF DATE!
    Please download the latest version from here:
    https://www.nexusmods.com/fallout4/mods/56255
"""
Warn_CLAS_Python_Platform = """
[!] WARNING : NEWEST PYTHON VERSIONS ARE NOT OFFICIALLY SUPPORTED ON WINDOWS 7/8/8.1
    Install the newest Py version from here: https://github.com/adang1345/PythonWin7
    Click on green Code button and Download Zip, then extract and install Python 3.11
"""
Warn_CLAS_Python_Version = """
[!] WARNING : YOUR PYTHON VERSION IS OUT OF DATE! PLEASE UPDATE PYTHON.
    FOR LINUX / WIN 10 / WIN 11: https://www.python.org/downloads
    FOR WIN 7 / 8 / 8.1 : https://github.com/adang1345/PythonWin7
"""
Warn_CLAS_Update_Failed = """
[!] WARNING : AN ERROR OCCURRED! THE SCRIPT WAS UNABLE TO CHECK FOR UPDATES, BUT WILL CONTINUE SCANNING.
    CHECK FOR ANY AUTO-SCANNER UPDATES HERE: https://www.nexusmods.com/fallout4/mods/56255
    MAKE SURE YOU HAVE THE LATEST VERSION OF PYTHON 3: https://www.python.org/downloads
"""

Warn_TOML_Achievements = """\
# [!] CAUTION : Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #
  FIX: Open *Buffout4.toml* and change Achievements parameter to FALSE, this prevents conflicts with Buffout 4.
  -----
"""
Warn_TOML_Memory = """\
# [!] CAUTION : Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #
  FIX: Open *Buffout4.toml* and change MemoryManager parameter to FALSE, this prevents conflicts with Buffout 4.
  -----
"""
Warn_TOML_F4EE = """\
# [!] CAUTION : Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #
  FIX: Open *Buffout4.toml* and change F4EE parameter to TRUE, this prevents bugs and crashes from Looks Menu.
  -----
"""

Warn_SCAN_Outdated_Buffout4 = """
# [!] CAUTION : REPORTED BUFFOUT 4 VERSION DOES NOT MATCH THE VERSION USED BY AUTOSCAN #
      UPDATE BUFFOUT 4 IF NECESSARY: https://www.nexusmods.com/fallout4/mods/47359
      BUFFOUT 4 FOR VIRTUAL REALITY: https://www.nexusmods.com/fallout4/mods/64880
"""
Warn_SCAN_NOTE_DLL = """\
# [!] NOTICE : MAIN ERROR REPORTS THAT A DLL FILE WAS INVOLVED IN THIS CRASH! #
  If the dll from main error belongs to a mod, that mod is likely the culprit.

"""
Warn_SCAN_NOTE_FCX = """\
[!] * NOTICE: FCX MODE IS ENABLED. AUTO-SCANNER MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *
      [ To disable game folder / mod files detection, set FCX Mode = false in Scan Crashlogs.ini ]
-----
"""
Warn_BLOG_NOTE_Plugins = """\
# [!] NOTICE : BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #
  Autoscan cannot continue. Try scanning a different crash log
  OR copy-paste your *loadorder.txt* into the scanner folder.
"""
Warn_BLOG_NOTE_Modules = """\
# [!] NOTICE : BUFFOUT 4 COULDN'T LIST ALL MODULES OR F4SE IS NOT INSTALLED! #
      CHECK IF SCRIPT EXTENDER (F4SE) IS CORRECTLY INSTALLED! \n")
      Script Extender Link: https://f4se.silverlock.org \n")
"""


# =================== UPDATE FUNCTION ===================


def clas_update_check():
    global CLAS_Current
    global CLAS_Updated
    print("CHECKING YOUR PYTHON VERSION & CRASH LOG AUTO SCANNER UPDATES...")
    print("(You can disable this check in the EXE or Scan Crashlogs.ini) \n")
    print(f"Installed Python Version: {sys.version[:6]} \n")
    if sys.version_info[:2] < (3, 9):
        print(Warn_CLAS_Python_Version)
        if platform.system() == "Windows":
            os_version = int(platform.win32_ver()[0])
            if os_version < 10:
                print(Warn_CLAS_Python_Platform)
        os.system("pause")
    else:
        response = requests.get("https://api.github.com/repos/GuidanceOfGrace/Buffout4-CLAS/releases/latest")  # type: ignore
        CLAS_Received = response.json()["name"]
        if CLAS_Received == CLAS_Current:
            CLAS_Updated = True
            print("✔️ You have the latest version of the Auto Scanner! \n")
        else:
            print(Warn_CLAS_Outdated_Scanner)
            print("===============================================================================")
    return CLAS_Updated


def clas_update_run():
    if CLAS_config.getboolean("MAIN", "Update Check") is True:
        try:
            import requests
            CLAS_CheckUpdates = clas_update_check()
            return CLAS_CheckUpdates
        except (ImportError, ModuleNotFoundError):
            subprocess.run(['pip', 'install', 'requests'], shell=True)
            print(Warn_CLAS_Update_Failed)
            print("===============================================================================")
    elif CLAS_config.getboolean("MAIN", "Update Check") is False:
        print("\n ❌ NOTICE: UPDATE CHECK IS DISABLED IN CLAS INI SETTINGS \n")


# ======================== FLAVOUR TEXT ========================
Sneaky_Tips = ["\nRandom Hint: [Ctrl] + [F] is a handy-dandy key combination. You should use it more often. Please.\n",
               "\nRandom Hint: Patrolling the Buffout 4 Nexus Page almost makes you wish this joke was more overused.\n",
               "\nRandom Hint: You have a crash log where Auto-Scanner couldn't find anything? Feel free to send it to me.\n",
               "\nRandom Hint: 20% of all crashes are caused by Classic Holstered Weapons mod. 80% of all statistics are made up.\n",
               "\nRandom Hint: No, I don't know why your game froze instead of crashed. But I know someone who might know; Google.\n",
               "\nRandom Hint: Spending 5 morbillion hours asking for help can save you from 5 minutes of reading the documentation.\n",
               "\nRandom Hint: When necessary, make sure that crashes are consistent or repeatable, since in rare cases they aren't.\n",
               "\nRandom Hint: When posting crash logs, it's helpful to mention the last thing you were doing before the crash happened.\n",
               "\nRandom Hint: Be sure to revisit both Buffout 4 Crash Article and Auto-Scanner Nexus Page from time to time for updates.\n"]

# =================== TERMINAL OUTPUT START ====================

print("Hello World! | Crash Log Auto-Scanner (CLAS) | Version", CLAS_Current[-4:], "| Fallout 4")
print("ELIGIBLE CRASH LOGS MUST START WITH 'crash-' AND HAVE .log FILE EXTENSION")
print("===============================================================================")


def scan_logs():
    print("PERFORMING SCAN... \n")
    statL_scanned = statL_incomplete = statL_failed = 0
    start_time = time.perf_counter()
    crash_template_stats = {}
    global Sneaky_Tips

    # =================== AUTOSCAN REPORT ===================

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
                    break

            plugins_list = loglines[plugins_index:]
            if os.path.exists("loadorder.txt"):
                plugins_list = []
                with open("loadorder.txt", "r", encoding="utf-8", errors="ignore") as loadorder_check:
                    plugin_format = loadorder_check.readlines()
                    if len(plugin_format) >= 1 and not any("[00]" in elem for elem in plugins_list):
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
                output.write("✔️ You have the latest version of Buffout 4!")
            else:
                output.write(Warn_SCAN_Outdated_Buffout4)

            output.writelines(["\n====================================================\n",
                               "CHECKING IF NECESSARY FILES/SETTINGS ARE CORRECT...\n",
                               "====================================================\n"])
            if CLAS_config.get("MAIN", "FCX Mode").lower() == "true":
                output.write(Warn_SCAN_NOTE_FCX)
                from Scan_Gamefiles import scan_mainfiles
                mainfiles_result = scan_mainfiles()
                for line in mainfiles_result:
                    try:
                        output.writelines(str(line))
                        output.write("\n")
                    except TypeError:
                        output.write(line)
                        output.write("\n")
            else:
                # CHECK BUFFOUT 4 TOML SETTINGS IN CRASH LOG ONLY
                if ("Achievements: true" in logtext and "achievements.dll" in logtext) or ("Achievements: true" in logtext and "UnlimitedSurvivalMode.dll" in logtext):
                    output.write(Warn_TOML_Achievements)
                else:
                    output.write("✔️ Achievements parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

                if "MemoryManager: true" in logtext and "BakaScrapHeap.dll" in logtext:
                    output.write(Warn_TOML_Memory)
                else:
                    output.write("✔️ Memory Manager parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

                if "F4EE: false" in logtext and "f4ee.dll" in logtext:
                    output.write(Warn_TOML_F4EE)
                else:
                    output.write("✔️ Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

            output.writelines(["====================================================\n",
                               "CHECKING IF LOG MATCHES ANY KNOWN CRASH CULPRITS...\n",
                               "====================================================\n"])
            global Culprit_Trap
            Culprit_Trap = False  # RETURN TRUE IF ANY POSSIBLE CRASH CULPRIT IS FOUND OR DETECTED

            # =============== CRASH / STAT CHECK TEMPLATE ===============
            def crash_template(crash_prefix, crash_main, crash_suffix, crash_stat):
                global Culprit_Trap
                if "CULPRIT FOUND" in crash_suffix or "DETECTED" in crash_suffix:
                    Culprit_Trap = True

                if "Logs with" in crash_prefix:  # FOR STAT LOGGING
                    print(f"{crash_prefix}{crash_main}{crash_suffix}", end='')
                else:  # MODIFY OUTPUT WHEN NOT CALLED FOR LOGGING
                    output.write(f"{crash_prefix}{crash_main}{crash_suffix}")

                if crash_stat in crash_template_stats:
                    crash_template_stats[crash_stat] += 1
                else:
                    crash_template_stats[crash_stat] = 0

                return crash_template_stats[crash_stat]

            # ===================== HEADER CULPRITS =====================
            if ".dll" in buff_error.lower() and "tbbmalloc" not in buff_error.lower():
                output.write(Warn_SCAN_NOTE_DLL)

            if "EXCEPTION_STACK_OVERFLOW" in buff_error:
                crash_template("# Checking for ", "Stack Overflow Crash.........", "CULPRIT FOUND! #\n", "statC_Overflow")
                output.write("> Priority : [5]\n")

            if "0x000100000000" in buff_error:
                crash_template("# Checking for ", "Active Effects Crash..........", "CULPRIT FOUND! #\n", "statC_ActiveEffects")
                output.write("> Priority : [5]\n")

            if "EXCEPTION_INT_DIVIDE_BY_ZERO" in buff_error:
                crash_template("# Checking for ", "Bad Math Crash................", "CULPRIT FOUND! #\n", "statC_BadMath")
                output.write("> Priority : [5]\n")

            if "0x000000000000" in buff_error:
                crash_template("# Checking for ", "Null Crash................", "CULPRIT FOUND! #\n", "statC_Null")
                output.write("> Priority : [5]\n")

            # ====================== MAIN CULPRITS ======================
            # OTHER | RESERVED
            # "BSResourceNiBinaryStream" | "ObjectBindPolicy"
            # Uneducated Shooter (56789) | "std::invalid_argument"
            # ===========================================================
            if "DLCBannerDLC01.dds" in logtext:
                crash_template("# Checking for ", "DLL Crash....................", "CULPRIT FOUND! #\n", "statC_DLL")
                output.write(f'> Priority : [5] | DLCBannerDLC01.dds : {logtext.count("DLCBannerDLC01.dds")}\n')

            # ===========================================================
            if "BGSLocation" in logtext and "BGSQueuedTerrainInitialLoad" in logtext:
                crash_template("# Checking for ", "LOD Crash....................", "CULPRIT FOUND! #\n", "statC_LOD")
                output.write(f'> Priority : [5] | BGSLocation : {logtext.count("BGSLocation")} | BGSQueuedTerrainInitialLoad : {logtext.count("BGSQueuedTerrainInitialLoad")}\n')

            # ===========================================================
            if "FaderData" in logtext or "FaderMenu" in logtext or "UIMessage" in logtext:
                crash_template("# Checking for ", "MCM Crash....................", "CULPRIT FOUND! #\n", "statC_MCM")
                output.write(f'> Priority : [3] | FaderData : {logtext.count("FaderData")} | FaderMenu : {logtext.count("FaderMenu")} | UIMessage : {logtext.count("UIMessage")}\n')

            # ===========================================================
            if "BGSDecalManager" in logtext or "BSTempEffectGeometryDecal" in logtext:
                crash_template("# Checking for ", "Decal Crash..................", "CULPRIT FOUND! #\n", "statC_Decal")
                output.write(f'> Priority : [5] | BGSDecalManager : {logtext.count("BGSDecalManager")} | BSTempEffectGeometryDecal : {logtext.count("BSTempEffectGeometryDecal")}\n')

            # ===========================================================
            if logtext.count("PipboyMapData") >= 2:
                crash_template("# Checking for ", "Equip Crash..................", "CULPRIT FOUND! #\n", "statC_Equip")
                output.write(f'> Priority : [3] | PipboyMapData : {logtext.count("PipboyMapData")}\n')

            # ===========================================================
            if "Papyrus" in logtext or "VirtualMachine" in logtext or "Assertion failed" in logtext:
                crash_template("# Checking for ", "Script Crash.................", "CULPRIT FOUND! #\n", "statC_Papyrus")
                output.write(f'> Priority : [3] | Papyrus : {logtext.count("Papyrus")} | VirtualMachine : {logtext.count("VirtualMachine")}\n')

            # ===========================================================
            if logtext.count("tbbmalloc.dll") >= 3 or "tbbmalloc" in buff_error:
                crash_template("# Checking for ", "Generic Crash................", "CULPRIT FOUND! #\n", "statC_Generic")
                output.write(f'> Priority : [2] | tbbmalloc.dll : {logtext.count("tbbmalloc.dll")}\n')

            # ===========================================================
            if "LooseFileAsyncStream" in logtext:
                crash_template("# Checking for ", "BA2 Limit Crash..............", "CULPRIT FOUND! #\n", "statC_BA2Limit")
                output.write(f'> Priority : [5] | LooseFileAsyncStream : {logtext.count("LooseFileAsyncStream")}\n')

            # ===========================================================
            if logtext.count("d3d11.dll") >= 3 or "d3d11" in buff_error:
                crash_template("# Checking for ", "Rendering Crash..............", "CULPRIT FOUND! #\n", "statC_Rendering")
                output.write(f'> Priority : [4] | d3d11.dll : {logtext.count("d3d11.dll")}\n')

            # ===========================================================
            if logtext.count("MSVCR110") >= 4 or "MSVCR" in buff_error or "MSVCP" in buff_error:
                crash_template("# Checking for ", "C++ Redist Crash.............", "CULPRIT FOUND! #\n", "statC_Redist")
                output.write(f'> Priority : [3] | MSVCR110.dll : {logtext.count("MSVCR110.dll")}\n')

            # ===========================================================
            if "GridAdjacencyMapNode" in logtext or "PowerUtils" in logtext:
                crash_template("# Checking for ", "Grid Scrap Crash.............", "CULPRIT FOUND! #\n", "statC_GridScrap")
                output.write(f'> Priority : [5] | GridAdjacencyMapNode : {logtext.count("GridAdjacencyMapNode")} | PowerUtils : {logtext.count("PowerUtils")}\n')

            # ===========================================================
            if "HUDCompass" in logtext or "HUDCompassMarker" in logtext or "attachMovie()" in logtext:
                crash_template("# Checking for ", "Map Marker Crash.............", "CULPRIT FOUND! #\n", "statC_MapMarker")
                output.write(f'> Priority : [5] | HUDCompass : {logtext.count("HUDCompass")} | HUDCompassMarker : {logtext.count("HUDCompassMarker")}\n')

            # ===========================================================
            if ("LooseFileStream" in logtext or "BSFadeNode" in logtext or "BSMultiBoundNode" in logtext) and logtext.count("LooseFileAsyncStream") == 0:
                crash_template("# Checking for ", "Mesh (NIF) Crash.............", "CULPRIT FOUND! #\n", "statC_Mesh")
                output.write(f'> Priority : [4] | LooseFileStream : {logtext.count("LooseFileStream")} | BSFadeNode : {logtext.count("BSFadeNode")}\n')
                output.write(f'                   BSMultiBoundNode : {logtext.count("BSMultiBoundNode")}\n')

            # ===========================================================
            if "Create2DTexture" in logtext or "DefaultTexture" in logtext:
                crash_template("# Checking for ", "Texture (DDS) Crash..........", "CULPRIT FOUND! #\n", "statC_Texture")
                output.write(f'> Priority : [3] | Create2DTexture : {logtext.count("Create2DTexture")} | DefaultTexture : {logtext.count("DefaultTexture")}\n')

            # ===========================================================
            if "DefaultTexture_Black" in logtext or "NiAlphaProperty" in logtext:
                crash_template("# Checking for ", "Material (BGSM) Crash........", "CULPRIT FOUND! #\n", "statC_Material")
                output.write(f'> Priority : [3] | DefaultTexture_Black : {logtext.count("DefaultTexture_Black")} | NiAlphaProperty : {logtext.count("NiAlphaProperty")}\n')

            # ===========================================================
            if (logtext.count("bdhkm64.dll") or logtext.count("usvfs::hook_DeleteFileW")) >= 2 or "BSTextureStreamer::Manager" in logtext or "BSTextureStreamer::zlibStreamDetail" in logtext:
                crash_template("# Checking for ", "Antivirus Crash....................", "CULPRIT FOUND! #\n", "statC_Antivirus")
                output.write(f'> Priority : [5] | bdhkm64.dll : {logtext.count("bdhkm64.dll")} | usvfs::hook_DeleteFileW : {logtext.count("usvfs::hook_DeleteFileW")}\n')
                output.write(f'                   BSTextureStreamer::Manager : {logtext.count("BSTextureStreamer::Manager")} | BSTextureStreamer::zlibStreamDetail : {logtext.count("BSTextureStreamer::zlibStreamDetail")}\n')

            # ===========================================================
            if (logtext.count("PathingCell") or logtext.count("BSPathBuilder") or logtext.count("PathManagerServer")) >= 2:
                crash_template("# Checking for ", "NPC Pathing Crash (S)........", "CULPRIT FOUND! #\n", "statC_NPCPathing")
                output.write(f'> Priority : [3] | PathingCell : {logtext.count("PathingCell")} | BSPathBuilder : {logtext.count("BSPathBuilder")}\n')
                output.write(f'                   PathManagerServer : {logtext.count("PathManagerServer")}\n')

            # ==============================
            if (logtext.count("NavMesh") or logtext.count("BSNavmeshObstacleData") or logtext.count("DynamicNavmesh") or logtext.count("PathingRequest")) >= 2:
                crash_template("# Checking for ", "NPC Pathing Crash (D)........", "CULPRIT FOUND! #\n", "statC_NPCPathingD")
                output.write(f'> Priority : [3] | NavMesh : {logtext.count("NavMesh")} | BSNavmeshObstacleData : {logtext.count("BSNavmeshObstacleData")}\n')
                output.write(f'                   DynamicNavmesh : {logtext.count("DynamicNavmesh")} PathingRequest : {logtext.count("PathingRequest")}\n')

            # ==============================
            if "+248B26A" in buff_error or "MovementAgentPathFollowerVirtual" in logtext or "PathingStreamSaveGame" in logtext or "BGSProcedurePatrolExecState" in logtext or "CustomActorPackageData" in logtext:
                crash_template("# Checking for ", "NPC Pathing Crash (F)........", "CULPRIT FOUND! #\n", "statC_NPCPathingF")
                output.write(f'> Priority : [3] | +248B26A | MovementAgentPathFollowerVirtual : {logtext.count("MovementAgentPathFollowerVirtual")} | PathingStreamSaveGame : {logtext.count("PathingStreamSaveGame")}\n')
                output.write(f'                   BGSProcedurePatrolExecState : {logtext.count("BGSProcedurePatrolExecState")} CustomActorPackageData : {logtext.count("CustomActorPackageData")}\n')

            # ===========================================================
            if logtext.count("X3DAudio1_7.dll") >= 3 or logtext.count("XAudio2_7.dll") >= 3 or ("X3DAudio1_7" or "XAudio2_7") in buff_error:
                crash_template("# Checking for ", "Audio Driver Crash...........", "CULPRIT FOUND! #\n", "statC_Audio")
                output.write(f'> Priority : [5] | X3DAudio1_7.dll : {logtext.count("X3DAudio1_7.dll")} | XAudio2_7.dll : {logtext.count("XAudio2_7.dll")}\n')

            # ===========================================================
            if logtext.count("cbp.dll") >= 3 or "skeleton.nif" in logtext or "cbp.dll" in buff_error:
                crash_template("# Checking for ", "Body Physics Crash...........", "CULPRIT FOUND! #\n", "statC_BodyPhysics")
                output.write(f'> Priority : [4] | cbp.dll : {logtext.count("cbp.dll")} | skeleton.nif : {logtext.count("skeleton.nif")}\n')

            # ===========================================================
            if "+0D09AB7" in buff_error or "TESLevItem" in logtext:
                crash_template("# Checking for ", "Leveled List Crash...........", "CULPRIT FOUND! #\n", "statC_LeveledList")
                output.write(f'> Priority : [3] | +0D09AB7 : {logtext.count("+0D09AB7")} | TESLevItem : {logtext.count("TESLevItem")}\n')

            # ===========================================================
            if any("[FF]" in elem for elem in plugins_list) or (logtext.count("BSMemStorage") and logtext.count("DataFileHandleReaderWriter")) >= 2:
                crash_template("# Checking for ", "Plugin Limit Crash...........", "CULPRIT FOUND! #\n", "statC_PluginLimit")
                output.write(f'> Priority : [5] | BSMemStorage : {logtext.count("BSMemStorage")} | DataFileHandleReaderWriter : {logtext.count("DataFileHandleReaderWriter")}\n')

            # ===========================================================
            if "+0DB9300" in buff_error or "GamebryoSequenceGenerator" in logtext:
                crash_template("# Checking for ", "Plugin Order Crash...........", "CULPRIT FOUND! #\n", "statC_PluginOrder")
                output.write(f'> Priority : [5] | +0DB9300 | GamebryoSequenceGenerator : {logtext.count("GamebryoSequenceGenerator")}\n')

            # ===========================================================
            if logtext.count("BSD3DResourceCreator") >= 3:
                crash_template("# Checking for ", "MO2 Extractor Crash..........", "CULPRIT FOUND! #\n", "statC_MO2Unpack")
                output.write(f'> Priority : [3] | BSD3DResourceCreator : {logtext.count("BSD3DResourceCreator")}\n')

            # ===========================================================
            if "+03EE452" in buff_error or "flexRelease_x64" in buff_error or (logtext.count("flexRelease_x64.dll") or logtext.count("CheckRefAgainstConditionsFunc")) >= 2:
                crash_template("# Checking for ", "Nvidia Debris Crash..........", "CULPRIT FOUND! #\n", "statC_NVDebris")
                output.write(f'> Priority : [5] | +03EE452 | flexRelease_x64.dll : {logtext.count("flexRelease_x64.dll")} | CheckRefAgainstConditionsFunc : {logtext.count("CheckRefAgainstConditionsFunc")}\n')

            # ===========================================================
            if logtext.count("nvwgf2umx.dll") >= 10 or "nvwgf2umx" in buff_error or "USER32.dll" in buff_error:
                crash_template("# Checking for ", "Nvidia Driver Crash..........", "CULPRIT FOUND! #\n", "statC_NVDriver")
                output.write(f'> Priority : [5] | nvwgf2umx.dll : {logtext.count("nvwgf2umx.dll")} | USER32.dll : {logtext.count("USER32.dll")}\n')

            # ===========================================================
            if "NVIDIA_Reflex.dll" in logtext and (logtext.count("Buffout4.dll") >= 3 or "3A0000" in buff_error or "AD0000" in buff_error or "8E0000" in buff_error):
                crash_template("# Checking for ", "Nvidia Reflex Crash..........", "CULPRIT FOUND! #\n", "statC_NVReflex")
                output.write(f'> Priority : [4] | *Currently no clear indicators for this crash* \n')

            # ===========================================================
            if (logtext.count("KERNELBASE.dll") or logtext.count("MSVCP140.dll")) >= 3 and "DxvkSubmissionQueue" in logtext:
                crash_template("# Checking for ", "Vulkan Memory Crash..........", "CULPRIT FOUND! #\n", "statC_VulkanMem")
                output.write(f'> Priority : [5] | KERNELBASE.dll : {logtext.count("KERNELBASE.dll")} | MSVCP140.dll : {logtext.count("MSVCP140.dll")}\n')
                output.write(f'                   DxvkSubmissionQueue : {logtext.count("DxvkSubmissionQueue")}\n')

            # ===========================================================
            if "dxvk::DXGIAdapter" in logtext or "dxvk::DXGIFactory" in logtext:
                crash_template("# Checking for ", "Vulkan Settings Crash........", "CULPRIT FOUND! #\n", "statC_VulkanSet")
                output.write(f'> Priority : [5] | dxvk::DXGIAdapter : {logtext.count("dxvk::DXGIAdapter")} | dxvk::DXGIFactory : {logtext.count("dxvk::DXGIFactory")}\n')

            # ===========================================================
            if "BSXAudio2DataSrc" in logtext or "BSXAudio2GameSound" in logtext:
                crash_template("# Checking for ", "Corrupted Audio Crash........", "CULPRIT FOUND! #\n", "statC_CorruptedAudio")
                output.write(f'> Priority : [4] | BSXAudio2DataSrc : {logtext.count("BSXAudio2DataSrc")} | BSXAudio2GameSound : {logtext.count("BSXAudio2GameSound")}\n')

            # ===========================================================
            if "SysWindowCompileAndRun" in logtext or "ConsoleLogPrinter" in logtext:
                crash_template("# Checking for ", "Console Command Crash........", "CULPRIT FOUND! #\n", "statC_ConsoleCommand")
                output.write(f'> Priority : [1] | SysWindowCompileAndRun : {logtext.count("SysWindowCompileAndRun")} | ConsoleLogPrinter : {logtext.count("ConsoleLogPrinter")}\n')

            # ===========================================================
            if "+1B938F0" in buff_error or "AnimTextData\\AnimationFileData" in logtext or "AnimationFileLookupSingletonHelper" in logtext:
                crash_template("# Checking for ", "Game Corruption Crash........", "CULPRIT FOUND! #\n", "statC_GameCorruption")
                output.write(f' Priority : [5] | +1B938F0 | AnimationFileData : {logtext.count("AnimationFileData")} | AnimationFileLookup : {logtext.count("AnimationFileLookupSingletonHelper")}\n')

            # ===========================================================
            if "BGSWaterCollisionManager" in logtext:
                crash_template("# Checking for ", "Water Collision Crash........", "CULPRIT FOUND! #\n", "statC_Water")
                output.write("[!] PLEASE CONTACT ME IF YOU GOT THIS CRASH! (CONTACT INFO BELOW)\n")
                output.write(f'> Priority : [6] | BGSWaterCollisionManager : {logtext.count("BGSWaterCollisionManager")}\n')

            # ===========================================================
            if "ParticleSystem" in logtext:
                crash_template("# Checking for ", "Particle Effects Crash.......", "CULPRIT FOUND! #\n", "statC_Particles")
                output.write(f'> Priority : [4] | ParticleSystem : {logtext.count("ParticleSystem")}\n')

            # ===========================================================
            if logtext.count("PlayerCharacter") >= 1 and (logtext.count("0x00000007") or logtext.count("0x00000014") or logtext.count("0x00000008")) >= 3:
                crash_template("# Checking for ", "Player Character Crash.......", "CULPRIT FOUND! #\n", "statC_Player")
                output.write(f'> Priority : [4] | PlayerCharacter : {logtext.count("PlayerCharacter")} | 0x00000007 : {logtext.count("0x00000007")}\n')
                output.write(f'                   0x00000008 : {logtext.count("0x00000008")} | 0x000000014 : {logtext.count("0x00000014")}\n')

            # ===========================================================
            if "+1FCC07E" in buff_error or "BSAnimationGraphManager" in logtext or "hkbVariableBindingSet" in logtext or "hkbHandIkControlsModifier" in logtext or "hkbBehaviorGraph" in logtext or "hkbModifierList" in logtext:
                crash_template("# Checking for ", "Animation / Physics Crash....", "CULPRIT FOUND! #\n", "statC_AnimationPhysics")
                output.write(f'> Priority : [5] | +1FCC07E | hkbVariableBindingSet : {logtext.count("hkbVariableBindingSet")} | hkbHandIkControlsModifier : {logtext.count("hkbHandIkControlsModifier")}\n')
                output.write(f'                   hkbBehaviorGraph : {logtext.count("hkbBehaviorGraph")} | hkbModifierList : {logtext.count("hkbModifierList")} | BSAnimationGraphManager : {logtext.count("BSAnimationGraphManager")}\n')

            # ===========================================================
            if "DLCBanner05.dds" in logtext:
                crash_template("# Checking for ", "Archive Invalidation Crash...", "CULPRIT FOUND! #\n", "statC_Invalidation")
                output.write(f'> Priority : [5] | DLCBanner05.dds : {logtext.count("DLCBanner05.dds")}\n')

            # ===========================================================
            output.write("\n ---------- Unsolved Crash Culprits Below ---------- \n")
            output.write("[CHECK THE BUFFOUT 4 DICTIONARY DOCUMENT FOR DETAILS]\n\n")
            # ===========================================================

            if "+01B59A4" in buff_error:
                crash_template("# Checking for ", "*[Creation Club Crash].......", "DETECTED! #\n", "statU_CClub")
                output.write(f'> Priority : [3] | +01B59A4\n')

            # ===========================================================
            if "+0B2C44B" in buff_error or "TESObjectARMO" in logtext or "TESObjectWEAP" in logtext or "BGSMod::Attachment" in logtext or "BGSMod::Template" in logtext or "BGSMod::Template::Item" in logtext:
                crash_template("# Checking for ", "*[Item Crash]................", "DETECTED! #\n", "statU_Item")
                output.write(f'> Priority : [5] | +0B2C44B | BGSMod::Attachment : {logtext.count("BGSMod::Attachment")} | BGSMod::Template : {logtext.count("BGSMod::Template")}\n')
                output.write(f'                   TESObjectARMO : {logtext.count("TESObjectARMO")} | TESObjectWEAP : {logtext.count("TESObjectWEAP")}\n')
                output.write(f'                   BGSMod::Template::Item : {logtext.count("BGSMod::Template::Item")}\n')

            # ===========================================================
            if "+0CDAD30" in buff_error or "BGSSaveLoadManager" in logtext or "BGSSaveLoadThread" in logtext or "BGSSaveFormBuffer" in logtext:
                crash_template("# Checking for ", "*[Save Crash]................", "DETECTED! #\n", "statU_Save")
                output.write(f'> Priority : [4] | +0CDAD30 | BGSSaveLoadManager : {logtext.count("BGSSaveLoadManager")}\n')
                output.write(f'                   BGSSaveFormBuffer : {logtext.count("BGSSaveFormBuffer")} | BGSSaveLoadThread : {logtext.count("BGSSaveLoadThread")}\n')

            # ===========================================================
            if "ButtonEvent" in logtext or "MenuControls" in logtext or "MenuOpenCloseHandler" in logtext or "PlayerControls" in logtext or "DXGISwapChain" in logtext:
                crash_template("# Checking for ", "*[Input Crash]...............", "DETECTED! #\n", "statU_Input")
                output.write(f'> Priority : [4] | ButtonEvent : {logtext.count("ButtonEvent")} | MenuControls : {logtext.count("MenuControls")}\n')
                output.write(f'                   MenuOpenCloseHandler : {logtext.count("MenuOpenCloseHandler")} | PlayerControls : {logtext.count("PlayerControls")}\n')
                output.write(f'                   DXGISwapChain : {logtext.count("DXGISwapChain")}\n')

            # ===========================================================
            if ("SS2" in logtext or "StartWorkshop" in logtext or "IsWithinBuildableArea" in logtext) and ("+01F498D" in buff_error or "+03F89A3" in buff_error):
                crash_template("# Checking for ", "*[SS2 / WF Crash]............", "DETECTED! #\n", "statU_SS2WF")
                output.write(f'> Priority : [4] | +01F498D | +03F89A3 | StartWorkshop : {logtext.count("StartWorkshop")} | IsWithinBuildableArea : {logtext.count("IsWithinBuildableArea")}\n')

            # ===========================================================
            if "+1D13DA7" in buff_error and ("BSShader" in logtext or "BSBatchRenderer" in logtext or "ShadowSceneNode" in logtext):
                crash_template("# Checking for ", "*[Looks Menu Crash]..........", "DETECTED! #\n", "statU_LooksMenu")
                output.write(f'> Priority : [5] | +1D13DA7 | BSShader : {logtext.count("BSShader")} | BSBatchRenderer : {logtext.count("BSBatchRenderer")}\n')
                output.write(f'                   ShadowSceneNode : {logtext.count("ShadowSceneNode")}\n')

            # ===========================================================
            if "BGSProcedurePatrol" in logtext or "BGSProcedurePatrolExecState" in logtext or "PatrolActorPackageData" in logtext:
                crash_template("# Checking for ", "*[NPC Patrol Crash]..........", "DETECTED! #\n", "statU_Patrol")
                output.write(f'> Priority : [5] | BGSProcedurePatrol : {logtext.count("BGSProcedurePatrol")} | BGSProcedurePatrolExecStatel : {logtext.count("BGSProcedurePatrolExecState")}\n')
                output.write(f'                   PatrolActorPackageData : {logtext.count("PatrolActorPackageData")}\n')

            # ===========================================================
            if "BSPackedCombinedSharedGeomDataExtra" in logtext or "BSPackedCombinedGeomDataExtra" in logtext or "BGSCombinedCellGeometryDB" in logtext or "BGSStaticCollection" in logtext or "TESObjectCELL" in logtext:
                crash_template("# Checking for ", "*[Precombines Crash].........", "DETECTED! #\n", "statC_Precomb")
                output.write(f'> Priority : [4] | BGSStaticCollection : {logtext.count("BGSStaticCollection")} | BGSCombinedCellGeometryDB : {logtext.count("BGSCombinedCellGeometryDB")}\n')
                output.write(f'                   BSPackedCombinedGeomDataExtra : {logtext.count("BSPackedCombinedGeomDataExtra")} | TESObjectCELL : {logtext.count("TESObjectCELL")}\n')
                output.write(f'                   BSPackedCombinedSharedGeomDataExtra : {logtext.count("BSPackedCombinedSharedGeomDataExtra")}\n')

            # ===========================================================
            if "HUDAmmoCounter" in logtext:
                crash_template("# Checking for ", "*[Ammo Counter Crash]........", "DETECTED! #\n", "statU_HUDAmmo")
                output.write(f'> Priority : [4] | HUDAmmoCounter : {logtext.count("HUDAmmoCounter")}\n')

            # ===========================================================
            if "ShadowSceneNode" in logtext or "myID3D11DeviceContext" in logtext or "BSDeferredDecal" in logtext or "BSDFDecal" in logtext:
                crash_template("# Checking for ", "*[GPU Overclock Crash].......", "DETECTED! #\n", "statU_Overclock")
                output.write(f'> Priority : [2] | ShadowSceneNode : {logtext.count("ShadowSceneNode")} | myID3D11DeviceContext : {logtext.count("myID3D11DeviceContext")}\n')
                output.write(f'                   BSDeferredDecal : {logtext.count("BSDeferredDecal")} | BSDFDecal : {logtext.count("BSDFDecal")}\n')

            # ===========================================================
            if "BGSProjectile" in logtext or "CombatProjectileAimController" in logtext:
                crash_template("# Checking for ", "*[NPC Projectile Crash].....", "DETECTED! #\n", "statU_Projectile")
                output.write(f'> Priority : [5] | BGSProjectile : {logtext.count("BGSProjectile")} | CombatProjectileAimController : {logtext.count("CombatProjectileAimController")}\n')

            # ===========================================================
            if logtext.count("NvCamera64.dll") >= 3 or "NiCamera" in logtext or "WorldRoot Camera" in logtext:
                crash_template("# Checking for ", "*[Camera Position Crash]....", "DETECTED! #\n", "statU_Camera")
                output.write(f'> Priority : [3] | NiCamera : {logtext.count("NiCamera")} | WorldRoot Camera : {logtext.count("WorldRoot Camera")}\n')

            # ===========================================================

            if Culprit_Trap is False:  # DEFINE CHECK IF NO KNOWN CRASH ERRORS / CULPRITS ARE FOUND
                output.writelines(["-----\n",
                                   "# AUTOSCAN FOUND NO CRASH ERRORS / CULPRITS THAT MATCH THE CURRENT DATABASE #\n",
                                   "Check below for mods that can cause frequent crashes and other problems.\n",
                                   "-----\n"])
            else:
                output.writelines(["-----\n",
                                   "* FOR DETAILED DESCRIPTIONS AND POSSIBLE SOLUTIONS TO ANY ABOVE DETECTED CRASH CULPRITS *\n",
                                   "* SEE: https://docs.google.com/document/d/17FzeIMJ256xE85XdjoPvv_Zi3C5uHeSTQh6wOZugs4c *\n",
                                   "-----\n"])

            # =============== MOD / PLUGIN CHECK TEMPLATES ==============
            def check_plugins(mods, mod_trap):
                if plugins_loaded:
                    for line in plugins_list:
                        for elem in mods.keys():
                            if "File:" not in line and "[FE" not in line and mods[elem]["mod"] in line:
                                warn = ''.join(mods[elem]["warn"])
                                output.writelines([f"[!] Found: {line[0:5].strip()} {warn}\n",
                                                   "-----\n"])
                                mod_trap = True
                            elif "File:" not in line and "[FE" in line and mods[elem]["mod"] in line:
                                warn = ''.join(mods[elem]["warn"])
                                output.writelines([f"[!] Found: {line[0:9].strip()} {warn}\n",
                                                   "-----\n"])
                                mod_trap = True
                return mod_trap

            def check_conflicts(mods, mod_trap):
                if plugins_loaded:
                    for elem in mods.keys():
                        if mods[elem]["mod_1"] in plugins_list and mods[elem]["mod_2"] in plugins_list:
                            warn = ''.join(mods[elem]["warn"])
                            output.writelines([f"[!] Found: {warn}\n",
                                               "-----\n"])
                            mod_trap = True
                return mod_trap

            # ================= ALL MOD / PLUGIN CHECKS =================

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS THAT CAN CAUSE FREQUENT CRASHES...\n",
                               "====================================================\n"])
            # Needs 1 empty space as prefix to prevent most duplicates.
            Mod_Trap1 = False
            Mods1 = {
                0: {"mod": " DamageThresholdFramework.esm",
                    "warn": ["DAMAGE THRESHOLD FRAMEWORK \n",
                             "- Can cause crashes in combat on some occasions due to how damage calculations are done."]},

                1: {"mod": " Endless Warfare.esm",
                    "warn": ["ENDLESS WARFARE \n",
                             "- Some enemy spawn points could be bugged or crash the game due to scripts or pathfinding."]},

                2: {"mod": " EPO.esp",
                    "warn": ["EXTREME PARTICLES OVERHAUL \n",
                             "- Can cause particle effects related crashes, its INI file raises particle count to 500000. \n",
                             "  Consider switching to Burst Impact Blast FX: https://www.nexusmods.com/fallout4/mods/57789"]},

                3: {"mod": " SakhalinWasteland",
                    "warn": ["FALLOUT SAKHALIN \n",
                             "- Breaks the precombine system all across Far Harbor which will randomly crash your game."]},

                4: {"mod": " 76HUD",
                    "warn": ["HUD76 HUD REPLACER \n",
                             "- Can sometimes cause interface and pip-boy related bugs, glitches and crashes."]},

                5: {"mod": " Knockout Framework.esm",
                    "warn": ["KNOCKOUT FRAMEWORK \n",
                             "- Confirm that you have installed the latest version (1.4.0+) of this mod. \n",
                             "  Older versions cause weird behavior and crashes during prolonged game sessions. \n",
                             "  Knockout Framework Link: https://www.nexusmods.com/fallout4/mods/27086?tab=files"]},

                6: {"mod": " NCRenegade",
                    "warn": ["NCR RENEGADE ARMOR \n",
                             "- Broken outfit mesh that crashes the game in 3rd person or when NPCs wearing it are hit."]},

                7: {"mod": " Respawnable Legendary Bosses",
                    "warn": ["RESPAWNABLE LEGENDARY BOSSES \n",
                             "- Can sometimes cause Deathclaw / Behemoth boulder projectile crashes for unknown reasons."]},

                8: {"mod": " Scrap Everything - Core",
                    "warn": ["SCRAP EVERYTHING (CORE) \n",
                             "- Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order."]},

                9: {"mod": " Scrap Everything - Ultimate",
                    "warn": ["SCRAP EVERYTHING (ULTIMATE) \n",
                             "- Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order."]},

                10: {"mod": " Shade Girl Leather Outfits",
                     "warn": ["SHADE GIRL LEATHER OUTFITS \n",
                              "- Outfits can crash the game while browsing the armor workbench or upon starting a new game due to bad meshes."]},

                11: {"mod": " SpringCleaning.esm",
                     "warn": ["SPRING CLEANING \n",
                              "- Abandoned and severely outdated mod that breaks precombines and could potentially even break your save file."]},

                12: {"mod": " (STO) NO",
                     "warn": ["STALKER TEXTURE OVERHAUL \n",
                              "- Doesn't work due to incorrect folder structure and has a corrupted dds file that causes Create2DTexture crashes."]},

                13: {"mod": " TacticalTablet.esp",
                     "warn": ["TACTICAL TABLET \n",
                              "- Can cause flickering with certain scopes or crashes while browsing workbenches, most commonly with ECO."]},

                14: {"mod": " True Nights v03.esp",
                     "warn": ["TRUE NIGHTS \n",
                              "- Has an invalid Image Space Adapter (IMAD) Record that will corrupt your save memory and has to be manually fixed."]},

                15: {"mod": " WeaponsFramework",
                     "warn": ["WEAPONS FRAMEWORK BETA \n",
                              "- Will randomly cause crashes when used with Tactical Reload and possibly other weapon or combat related mods. \n"
                              "  Visit Important Patches List article for possible solutions: https://www.nexusmods.com/fallout4/articles/3769"]},

                16: {"mod": " WOTC.esp",
                     "warn": ["WAR OF THE COMMONWEALTH \n",
                              "- Seems responsible for consistent crashes with specific spawn points or randomly during settlement attacks."]}
            }
            Mod_Check1 = False
            if plugins_loaded:
                Mod_Check1 = check_plugins(Mods1, Mod_Trap1)

                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                statM_CHW = 0
                if logtext.count("ClassicHolsteredWeapons") >= 3 or "ClassicHolsteredWeapons" in buff_error:
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS\n",
                                       "AUTOSCAN IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!\n",
                                       "You should disable CHW to further confirm this.\n",
                                       "Visit the main crash logs article for additional solutions.\n",
                                       "-----\n"])
                    statM_CHW += 1
                    Mod_Trap1 = True
                    Culprit_Trap = True
                elif logtext.count("ClassicHolsteredWeapons") >= 2 and ("UniquePlayer.esp" in logtext or "HHS.dll" in logtext or "cbp.dll" in logtext or "Body.nif" in logtext):
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS\n",
                                       "AUTOSCAN IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!\n",
                                       "You should disable CHW to further confirm this.\n",
                                       "Visit the main crash logs article for additional solutions.\n",
                                       "-----\n"])
                    statM_CHW += 1
                    Mod_Trap1 = True
                    Culprit_Trap = True
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
                    Mod_Trap1 = True

            if plugins_loaded and (Mod_Check1 or Mod_Trap1) is True:
                output.writelines(["# [!] CAUTION : ANY ABOVE DETECTED MODS HAVE A MUCH HIGHER CHANCE TO CRASH YOUR GAME! #\n",
                                   "  You can disable any/all of them temporarily to confirm they caused this crash.\n",
                                   "-----\n"])
                statL_scanned += 1
            elif plugins_loaded and (Mod_Check1 and Mod_Trap1) is False:
                output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT MATCH THE CURRENT DATABASE FOR THIS LOG #\n",
                                   "THAT DOESN'T MEAN THERE AREN'T ANY! YOU SHOULD RUN PLUGIN CHECKER IN WRYE BASH.\n",
                                   "Wrye Bash Link: https://www.nexusmods.com/fallout4/mods/20032?tab=files\n",
                                   "-----\n"])
                statL_scanned += 1
            else:
                output.write(Warn_BLOG_NOTE_Plugins)
                statL_incomplete += 1

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS THAT CONFLICT WITH OTHER MODS...\n",
                               "====================================================\n"])
            # Needs 1 empty space as prefix to prevent most duplicates.
            # mod_1 should be less popular mod, mod_2 more popular mod.
            Mod_Trap2 = False
            Mods2 = {
                0: {"mod_1": " BetterPowerArmorRedux.dll",
                    "mod_2": " FloatingDamage.dll",
                    "warn": [" BETTER POWER ARMOR REDUX ❌ CONFLICTS WITH : FLOATING DAMAGE \n",
                             "- Both mods use the same script hooks. This can crash the game or cause weird mod behavior. \n",
                             "- If you encounter problems, Auto-Scanner suggests using one of these mods only, not both."]},

                1: {"mod_1": " BetterPowerArmorRedux.dll",
                    "mod_2": " KnockoutFramework.dll",
                    "warn": [" BETTER POWER ARMOR REDUX ❌ CONFLICTS WITH : KNOCKOUT FRAMEWORK \n",
                             "- Both mods use the same script hooks. This can crash the game or cause weird mod behavior. \n",
                             "- If you encounter problems, Auto-Scanner suggests using one of these mods only, not both."]},

                2: {"mod_1": " BostonFPSFix",
                    "mod_2": " PRP.esp",
                    "warn": ["BOSTON FPS FIX ❌ CONFLICTS WITH : PREVIS REPAIR PACK \n",
                             "- Using both mods can break precombines. Auto-Scanner suggests using Previs Repair Pack only."]},

                3: {"mod_1": " ExtendedWeaponSystem.esm",
                    "mod_2": " TacticalReload.esm",
                    "warn": ["EXTENDED WEAPON SYSTEMS ❌ CONFLICTS WITH : TACTICAL RELOAD \n",
                             "- Using both mods can frequently crash the game. Auto-Scanner suggests using one of these mods only, not both."]},

                4: {"mod_1": " FROST.esp",
                    "mod_2": " PRP.esp",
                    "warn": ["FROST SURVIVAL SIMULATOR ❌ CONFLICTS WITH : PREVIS REPAIR PACK \n",
                             "- For precombine fixes, remove PRP and switch to FROST Cell Fixes (FCF). \n",
                             "- FROST Cell Fixes: https://www.nexusmods.com/fallout4/mods/59652?tab=files"]},

                5: {"mod_1": " DCGuard_Overhaul.esp",
                    "mod_2": " Guards.esp",
                    "warn": ["THE FENS SHERIFF'S DEPARTMENT ❌ CONFLICTS WITH : VARIED DIAMOND CITY GUARDS \n",
                             "- Both mods heavily modify Diamond City Guards records. Auto-Scanner suggests using one of these mods only, not both."]},

                6: {"mod_1": " Fallout4Upscaler.dll",
                    "mod_2": " NVIDIA_Reflex.dll",
                    "warn": ["FALLOUT 4 UPSCALER ❌ CONFLICTS WITH : NVIDIA REFLEX SUPPORT \n",
                             "- Both mods likely use the same DLL hooks. This can crash the game or cause weird mod behavior. \n",
                             "- If you encounter problems or crashes, Auto-Scanner suggests using one of these mods only, not both."]},

                7: {"mod_1": " vulkan",
                    "mod_2": " NVIDIA_Reflex.dll",
                    "warn": ["VULKAN RENDERER ❌ CONFLICTS WITH : NVIDIA REFLEX SUPPORT \n",
                             "- Vulkan Renderer can break GPU recognition from NV Reflex Support. This can crash the game or cause weird mod behavior. \n",
                             "- If you encounter Nvidia Driver crashes, Auto-Scanner suggests using Vulkan Render only. Otherwise, use Nvidia Reflex Support"]},

                8: {"mod_1": " CustomCamera.esp",
                    "mod_2": " CameraTweaks.esp",
                    "warn": ["CUSTOM CAMERA ❌ CONFLICTS WITH : CAMERA TWEAKS \n",
                             "- Both mods make changes to the in-game camera. Auto-Scanner suggests using Camera Tweaks only, since it's an updated alternative."]},

                9: {"mod_1": " MOD_1.esm",
                    "mod_2": " MOD_2.esm",
                    "warn": ["MOD_1_NAME ❌ CONFLICTS WITH : MOD_2_NAME \n",
                             "- TEMPLATE."]},

            }
            Mod_Check2 = False
            if plugins_loaded:
                Mod_Check2 = check_conflicts(Mods2, Mod_Trap2)
                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                # CURRENTLY NONE

            if plugins_loaded and (Mod_Check2 or Mod_Trap2) is True:
                output.writelines(["# AUTOSCAN FOUND MODS THAT ARE INCOMPATIBLE OR CONFLICT WITH YOUR OTHER MODS # \n",
                                   "* YOU SHOULD CHOOSE WHICH MOD TO KEEP AND REMOVE OR DISABLE THE OTHER MOD * \n",
                                   "-----\n"])
            elif plugins_loaded and (Mod_Check2 and Mod_Trap2) is False:
                output.writelines(["# AUTOSCAN FOUND NO MODS THAT ARE INCOMPATIBLE OR CONFLICT WITH YOUR OTHER MODS #\n",
                                   "-----\n"])
            elif plugins_loaded is False:
                output.write(Warn_BLOG_NOTE_Plugins)

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS WITH SOLUTIONS & COMMUNITY PATCHES\n",
                               "====================================================\n"])
            # Needs 1 empty space as prefix to prevent most duplicates.
            Mod_Trap3 = no_repeat1 = no_repeat2 = False
            Mods3 = {
                0: {"mod": " DLCUltraHighResolution.esm",
                    "warn": ["HIGH RESOLUTION DLC. I STRONGLY ADVISE AGAINST USING IT! \n",
                             "- Right click on Fallout 4 in your Steam Library folder, then select Properties \n",
                             "  Switch to the DLC tab and uncheck / disable the High Resolution Texture Pack"]},

                1: {"mod": " AAF.esm",
                    "warn": ["ADVANCED ANIMATION FRAMEWORK \n",
                             "- Latest AAF version only available on Moddingham | AAF Tech Support: https://discord.gg/gWZuhMC \n",
                             "  Latest AAF Link (register / login to download): https://www.moddingham.com/viewtopic.php?t=2 \n",
                             "-----\n",
                             "- Looks Menu versions 1.6.20 & 1.6.19 can frequently break adult mod related (erection) morphs \n",
                             "  If you notice AAF related problems, remove latest version of Looks Menu and switch to 1.6.18"]},

                2: {"mod": " ArmorKeywords.esm",
                    "warn": ["ARMOR AND WEAPONS KEYWORDS\n",
                             "- If you don't rely on AWKCR, consider switching to Equipment and Crafting Overhaul \n",
                             "  Better Alternative: https://www.nexusmods.com/fallout4/mods/67679?tab=files \n",
                             "  Patches to remove AWKCR: https://www.nexusmods.com/fallout4/mods/40752?tab=files"]},

                3: {"mod": " BTInteriors_Project.esp",
                    "warn": ["BEANTOWN INTERIORS \n",
                             "- Usually causes fps drops, stuttering, crashing and culling issues in multiple locations. \n",
                             "  Patch Link: https://www.nexusmods.com/fallout4/mods/53894?tab=files"]},

                4: {"mod": " CombatZoneRestored.esp",
                    "warn": ["COMBAT ZONE RESTORED \n",
                             "- Contains few small issues and NPCs usually have trouble navigating the interior space. \n",
                             "  Patch Link: https://www.nexusmods.com/fallout4/mods/59329?tab=files"]},

                5: {"mod": " D.E.C.A.Y.esp",
                    "warn": ["DECAY BETTER GHOULS \n",
                             "- You have to install DECAY Redux patch to prevent its audio files from crashing the game. \n",
                             "  Patch Link: https://www.nexusmods.com/fallout4/mods/59025?tab=files"]},

                6: {"mod": " EveryonesBestFriend",
                    "warn": ["EVERYONE'S BEST FRIEND \n",
                             "- This mod needs a compatibility patch to properly work with the Unofficial Patch (UFO4P). \n",
                             "  Patch Link: https://www.nexusmods.com/fallout4/mods/43409?tab=files"]},

                7: {"mod": " M8r_Item_Tags",
                    "warn": ["FALLUI ITEM SORTER (OLD) \n",
                             "- This is an outdated item tagging / sorting patch that can cause crashes or conflicts in all kinds of situations. \n",
                             "  I strongly recommend to instead generate your own sorting patch and place it last in your load order. \n",
                             "  That way, you won't experience any conflicts / crashes and even modded items will be sorted. \n",
                             "  Generate Sorting Patch With This: https://www.nexusmods.com/fallout4/mods/48826?tab=files"]},

                8: {"mod": " Fo4FI_FPS_fix",
                    "warn": ["FO4FI FPS FIX \n",
                             "- This mod is severely outdated and will cause crashes even with compatibility patches. \n",
                             "  Better Alternative: https://www.nexusmods.com/fallout4/mods/46403?tab=files"]},

                9: {"mod": " BostonFPSFixAIO.esp",
                    "warn": ["BOSTON FPS FIX \n",
                             "- This mod is severely outdated and will cause crashes even with compatibility patches. \n",
                             "  Better Alternative: https://www.nexusmods.com/fallout4/mods/46403?tab=files"]},

                10: {"mod": " FunctionalDisplays.esp",
                     "warn": ["FUNCTIONAL DISPLAYS \n",
                              "- Frequently causes object model (nif) related crashes and this needs to be manually corrected. \n",
                              "  Advised Fix: Open its Meshes folder and delete everything inside EXCEPT for the Functional Displays folder."]},

                11: {"mod": " skeletonmaleplayer",
                     "warn": ["GENDER SPECIFIC SKELETONS (MALE) \n",
                              "- High chance to cause a crash when starting a new game or during the game intro sequence. \n",
                              "  Advised Fix: Enable the mod only after leaving Vault 111. Existing saves shouldn't be affected."]},

                12: {"mod": " skeletonfemaleplayer",
                     "warn": ["GENDER SPECIFIC SKELETONS (FEMALE) \n",
                              "- High chance to cause a crash when starting a new game or during the game intro sequence. \n",
                              "  Advised Fix: Enable the mod only after leaving Vault 111. Existing saves shouldn't be affected."]},

                13: {"mod": " Give Me That Bottle.esp",
                     "warn": ["GIVE ME THAT BOTTLE \n",
                              "- Can rarely cause crashes in the Pip-Boy inventory menu. Switch to Fill'em Up Again instead. \n",
                              "  Better Alternative: https://www.nexusmods.com/fallout4/mods/12674?tab=files"]},

                14: {"mod": " CapsWidget",
                     "warn": ["HUD CAPS \n",
                              "- Often breaks the Save / Quicksave function due to poor script implementation. \n",
                              "  Advised Fix: Download fixed pex file and place it into HUDCaps/Scripts folder. \n",
                              "  Fix Link: https://drive.google.com/file/d/1egmtKVR7mSbjRgo106UbXv_ySKBg5az2"]},

                15: {"mod": " Homemaker.esm",
                     "warn": ["HOMEMAKER \n",
                              "- Causes a crash while scrolling over Military / BoS fences in the Settlement Menu. \n",
                              "  Patch Link: https://www.nexusmods.com/fallout4/mods/41434?tab=files"]},

                16: {"mod": " Horizon.esm",
                     "warn": ["HORIZON \n",
                              "- I highly recommend installing these patches for 1.8.7 until newer version is released. \n",
                              "  Patch Link 1: https://www.nexusmods.com/fallout4/mods/65911?tab=files \n",
                              "  Patch Link 2: https://www.nexusmods.com/fallout4/mods/61998?tab=files"]},

                17: {"mod": " ESPExplorerFO4.esp",
                     "warn": ["IN GAME ESP EXPLORER \n",
                              "- Can cause a crash when pressing F10 due to a typo in the INI settings. \n",
                              "  Better Alternative: https://www.nexusmods.com/fallout4/mods/56922?tab=files"]},

                18: {"mod": " LegendaryModification.esp",
                     "warn": ["LEGENDARY MODIFICATION \n",
                              "- Old mod plagued with all kinds of bugs and crashes, can conflict with some modded weapons. \n",
                              "  Better Alternative: https://www.nexusmods.com/fallout4/mods/67679?tab=files"]},

                19: {"mod": " LooksMenu Customization Compendium.esp",
                     "warn": ["LOOKS MENU CUSTOMIZATION COMPENDIUM \n",
                              "- Apparently breaks the original Looks Menu mod by turning off some important values. \n",
                              "  Fix Link: https://www.nexusmods.com/fallout4/mods/56465?tab=files"]},

                20: {"mod": " MilitarizedMinutemen.esp",
                     "warn": ["MILITARIZED MINUTEMEN \n"
                              "- Can occasionally crash the game due to a broken mesh on some minutemen outfits. \n"
                              "  Patch Link: https://www.nexusmods.com/fallout4/mods/32369?tab=files"]},

                21: {"mod": " MoreUniques",
                     "warn": ["MORE UNIQUE WEAPONS EXPANSION \n",
                              "- Causes crashes due to broken precombines and compatibility issues with other weapon mods. \n",
                              "  Patch Link: https://www.nexusmods.com/fallout4/mods/54848?tab=files"]},

                22: {"mod": " NAC.es",
                     "warn": ["NATURAL AND ATMOSPHERIC COMMONWEALTH \n",
                              "- If you notice weird looking skin tones with either NAC or NACX, install this patch. \n",
                              "  Patch Link: https://www.nexusmods.com/fallout4/mods/57052?tab=files"]},

                23: {"mod": " Northland Diggers New.esp",
                     "warn": ["NORTHLAND DIGGERS RESOURCES \n",
                              "- Contains various bugs and issues that can cause crashes or negatively affect other mods. \n",
                              "  Fix Link: https://www.nexusmods.com/fallout4/mods/53395?tab=files"]},

                24: {"mod": " Project Zeta.esp",
                     "warn": ["PROJECT ZETA \n",
                              "- Invasion quests seem overly buggy or trigger too frequently, minor sound issues. \n",
                              "  Fix Link: https://www.nexusmods.com/fallout4/mods/65166?tab=files"]},

                25: {"mod": " RaiderOverhaul.esp",
                     "warn": ["RAIDER OVERHAUL \n",
                              "- Old mod that requires several patches to function as intended. Use ONE Version instead. \n",
                              "  Updated ONE Version: https://www.nexusmods.com/fallout4/mods/51658?tab=files"]},

                26: {"mod": " Rusty Face Fix",
                     "warn": ["RUSTY FACE FIX \n",
                              "- Can cause script lag or even crash the game in very rare cases. Switch to REDUX Version instead. \n",
                              "  Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/64270?tab=files"]},

                27: {"mod": " SKKCraftableWeaponsAmmo",
                     "warn": ["SKK CRAFT WEAPONS AND SCRAP AMMO \n",
                              "- Version 008 is incompatible with AWKCR and will cause crashes while saving the game. \n",
                              "  Advised Fix: Use Version 007 or remove AWKCR and switch to Equipment and Crafting Overhaul instead."]},

                28: {"mod": " SOTS.esp",
                     "warn": ["SOUTH OF THE SEA \n",
                              "- Very unstable mod that consistently and frequently causes strange problems and crashes. \n",
                              "  Updated Version: https://www.nexusmods.com/fallout4/mods/63152?tab=files"]},

                29: {"mod": " StartMeUp.esp",
                     "warn": ["START ME UP \n",
                              "- Abandoned mod that can cause infinite loading and other problems. Switch to REDUX Version instead. \n",
                              "  Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/56984?tab=files"]},

                30: {"mod": " SuperMutantRedux.esp",
                     "warn": ["SUPER MUTANT REDUX \n",
                              "- Causes crashes at specific locations or with certain Super Mutant enemies and items. \n",
                              "  Patch Link: https://www.nexusmods.com/fallout4/mods/51353?tab=files"]},

                31: {"mod": " TacticalReload.esm",
                     "warn": ["TACTICAL RELOAD \n",
                              "- Can cause weapon and combat related crashes. TR Expansion For ECO is highly recommended. \n",
                              "  TR Expansion For ECO Link: https://www.nexusmods.com/fallout4/mods/67716?tab=files"]},

                32: {"mod": " Creatures and Monsters.esp",
                     "warn": ["UNIQUE NPCs CREATURES AND MONSTERS \n",
                              "- Causes crashes and breaks precombines at specific locations, some creature spawns are too frequent. \n",
                              "  Patch Link: https://www.nexusmods.com/fallout4/mods/48637?tab=files"]},

                33: {"mod": " ZombieWalkers",
                     "warn": ["ZOMBIE WALKERS \n",
                              "- Version 2.6.3 contains a resurrection script that will regularly crash the game. \n",
                              "  Advised Fix: Make sure you're using the 3.0 Beta version of this mod or newer."]}
            }
            Mod_Check3 = False
            if plugins_loaded:
                Mod_Check3 = check_plugins(Mods3, Mod_Trap3)
                for line in loglines:
                    # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                    if no_repeat1 is False and "File:" not in line and ("Depravity" or "FusionCityRising" or "HotC" or "OutcastsAndRemnants" or "ProjectValkyrie") in line:
                        output.writelines([f"[!] Found: {line[0:9].strip()} THUGGYSMURF QUEST MOD\n",
                                           "If you have Depravity, Fusion City Rising, HOTC, Outcasts and Remnants and/or Project Valkyrie\n",
                                           "install this patch with facegen data, fully generated precomb/previs data and several tweaks.\n",
                                           "Patch Link: https://www.nexusmods.com/fallout4/mods/56876?tab=files\n",
                                           "-----\n"])
                        no_repeat1 = Mod_Trap3 = True

                    if no_repeat2 is False and "File:" not in line and ("CaN.esm" or "AnimeRace_Nanako.esp") in line:
                        output.writelines([f"[!] Found: {line[0:9].strip()} CUSTOM RACE SKELETON MOD\n",
                                           "If you have AnimeRace NanakoChan or Crimes Against Nature, install the Race Skeleton Fixes.\n",
                                           "Skeleton Fixes Link (READ THE DESCRIPTION): https://www.nexusmods.com/fallout4/mods/56101\n"])
                        no_repeat2 = Mod_Trap3 = True

                if "FallSouls.dll" in logtext:
                    output.writelines([f"[!] Found: FALLSOULS UNPAUSED GAME MENUS\n",
                                       "Occasionally breaks the Quests menu, can cause crashes while changing MCM settings.\n",
                                       "Advised Fix: Toggle PipboyMenu in FallSouls MCM settings or completely reinstall the mod.\n",
                                       "-----\n"])
                    Mod_Trap3 = True

            if plugins_loaded and (Mod_Check3 or Mod_Trap3) is True:
                output.writelines([f"# AUTOSCAN FOUND PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                   "[Due to inherent limitations, Auto-Scan will continue detecting certain mods\n",
                                   "even if fixes or patches for them are already installed. You can ignore these.]\n",
                                   "-----\n"])
            elif plugins_loaded and (Mod_Check3 and Mod_Trap3) is False:
                output.writelines([f"# AUTOSCAN FOUND NO PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                   "-----\n"])
            elif plugins_loaded is False:
                output.write(Warn_BLOG_NOTE_Plugins)

            output.writelines(["FOR FULL LIST OF IMPORTANT PATCHES AND FIXES FOR THE BASE GAME AND MODS,\n",
                               "VISIT THIS ARTICLE: https://www.nexusmods.com/fallout4/articles/3769\n",
                               "-----\n"])

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS PATCHED THROUGH OPC INSTALLER...\n",
                               "====================================================\n"])
            # Needs 1 empty space as prefix to prevent most duplicates.
            Mod_Trap4 = False
            Mods4 = {
                0: {"mod": " Beyond the Borders",
                    "warn": "Beyond the Borders"},
                1: {"mod": " Deadly Commonwealth Expansion",
                    "warn": "Deadly Commonwealth Expansion"},
                2: {"mod": " Dogmeat and Strong Armor",
                    "warn": "Dogmeat and Strong Armor"},
                3: {"mod": " DoYourDamnJobCodsworth",
                    "warn": "Do Your Damn JobCodsworth"},
                4: {"mod": " ConcordEXPANDED",
                    "warn": "Concord EXPANDED"},
                5: {"mod": " HagenEXPANDED",
                    "warn": "Hagen EXPANDED"},
                6: {"mod": " GlowingSeaEXPANDED",
                    "warn": "Glowing Sea EXPANDED"},
                7: {"mod": " SalemEXPANDED",
                    "warn": "Salem EXPANDED"},
                8: {"mod": " SwampsEXPANDED",
                    "warn": "Swamps EXPANDED"},
                9: {"mod": " _hod",
                    "warn": "Halls of the Dead"},
                10: {"mod": " ImmersiveBeantown",
                     "warn": "Immersive Beantown"},
                11: {"mod": " CovenantComplex",
                     "warn": "Covenant Complex"},
                12: {"mod": " GunnersPlazaInterior",
                     "warn": "Gunners Plaza Interior"},
                13: {"mod": " ImmersiveHubCity",
                     "warn": "Immersive Hub City"},
                14: {"mod": " Immersive_Lexington",
                     "warn": "Immersive & Extended Lexington"},
                15: {"mod": " Immersive Nahant",
                     "warn": "Immersive & Extended Nahant"},
                16: {"mod": " Immersive S Boston",
                     "warn": "Immersive Military Checkpoint"},
                17: {"mod": " MutilatedDeadBodies",
                     "warn": "Mutilated Dead Bodies"},
                18: {"mod": " Vault4.esp",
                     "warn": "Fourville (Vault 4)"},
                19: {"mod": "atlanticofficesf23",
                     "warn": "Lost Building of Atlantic"},
                20: {"mod": " Minutemen Supply Caches",
                     "warn": "Minutemen Supply Caches"},
                21: {"mod": " moreXplore",
                     "warn": "More Xplore"},
                22: {"mod": " NEST_BUNKER_PROJECT",
                     "warn": "NEST Bunker Project"},
                23: {"mod": " Raider Children.esp",
                     "warn": "Raider Children"},
                24: {"mod": " sectorv",
                     "warn": "Sector V"},
                25: {"mod": " SettlementShelters",
                     "warn": "Settlement Shelters"},
                26: {"mod": " subwayrunnerdynamiclighting",
                     "warn": "Subway Runner (Dynamic Lights)"},
                27: {"mod": " 3DNPC_FO4Settler.esp",
                     "warn": "Settlers of the Commonwealth"},
                28: {"mod": " 3DNPC_FO4.esp",
                     "warn": "Tales from the Commonwealth"},
                29: {"mod": " The Hollow",
                     "warn": "The Hollow"},
                30: {"mod": " nvvault1080",
                     "warn": "Vault 1080 (Vault 80)"},
                31: {"mod": " Vertibird Faction Paint Schemes",
                     "warn": "Vertibird Faction Paint Schemes"},
                32: {"mod": " MojaveImports.esp",
                     "warn": "Wasteland Imports (Mojave Imports)"},
                33: {"mod": " Firelance2.5",
                     "warn": "Xander's Aid"},
                34: {"mod": " zxcMicroAdditions",
                     "warn": "ZXC Micro Additions"}
            }
            Mod_Check4 = False
            if plugins_loaded:
                Mod_Check4 = check_plugins(Mods4, Mod_Trap4)
                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                # CURRENTLY NONE

            if plugins_loaded and (Mod_Check4 or Mod_Trap4) is True:
                output.writelines(["* FOR PATCH REPOSITORY THAT PREVENTS CRASHES AND FIXES PROBLEMS IN THESE AND OTHER MODS,* \n",
                                   "* VISIT OPTIMIZATION PATCHES COLLECTION: https://www.nexusmods.com/fallout4/mods/54872 * \n",
                                   "-----\n"])
            elif plugins_loaded and (Mod_Check4 and Mod_Trap4) is False:
                output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT ARE ALREADY PATCHED THROUGH OPC INSTALLER #\n",
                                   "-----\n"])
            elif plugins_loaded is False:
                output.write(Warn_BLOG_NOTE_Plugins)

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

            if CLAS_config.get("MAIN", "FCX Mode").lower() == "true":
                output.write(Warn_SCAN_NOTE_FCX)
                from Scan_Gamefiles import scan_modfiles
                modfiles_result = scan_modfiles()
                for line in modfiles_result:
                    try:
                        output.writelines(str(line))
                        output.write("\n")
                    except TypeError:
                        output.write(line)
                        output.write("\n")

            if plugins_loaded:
                if any("CanarySaveFileMonitor" in elem for elem in plugins_list):
                    output.write("✔️ *Canary Save File Monitor* is installed.\n  -----\n")
                else:
                    output.writelines(["# ❌ CANARY SAVE FILE MONITOR ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  This is a highly recommended mod that can detect save file corruption.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/44949?tab=files\n",
                                       "  -----\n"])

                if "HighFPSPhysicsFix.dll" in logtext or "HighFPSPhysicsFixVR.dll" in logtext:
                    output.write("✔️ *High FPS Physics Fix* is installed.\n  -----\n")
                else:
                    output.writelines(["# ❌ HIGH FPS PHYSICS FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  This is a mandatory patch / fix that prevents game engine problems.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files\n",
                                       "  -----\n"])

                if any("PPF.esm" in elem for elem in plugins_list):
                    output.write("✔️ *Previs Repair Pack* is installed.\n  -----\n")
                else:
                    output.writelines(["# ❌ PREVIS REPAIR PACK ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  This is a highly recommended mod that can improve performance.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/46403?tab=files\n",
                                       "  -----\n"])

                if any("Unofficial Fallout 4 Patch.esp" in elem for elem in plugins_list):
                    output.write("✔️ *Unofficial Fallout 4 Patch* is installed.\n  -----\n")
                else:
                    output.writelines(["# ❌ UNOFFICIAL FALLOUT 4 PATCH ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  If you own all DLCs, make sure that the Unofficial Patch is installed.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/4598?tab=files\n",
                                       "  -----\n"])

                if "vulkan-1.dll" in logtext and gpu_amd:
                    output.write("✔️ *Vulkan Renderer* is installed.\n  -----\n")
                elif logtext.count("vulkan-1.dll") == 0 and gpu_amd and not gpu_nvidia:
                    output.writelines(["# ❌ VULKAN RENDERER ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  This is a highly recommended mod that can improve performance on AMD GPUs.\n",
                                       "  Installation steps can be found in 'How To Read Crash Logs' PDF / Document.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/48053?tab=files\n",
                                       "  -----\n"])

                if "WeaponDebrisCrashFix.dll" in logtext and gpu_nvidia:
                    output.write("✔️ *Weapon Debris Crash Fix* is installed.\n  -----\n")
                elif "WeaponDebrisCrashFix.dll" in logtext and not gpu_nvidia and gpu_amd:
                    output.writelines(["❌ *Weapon Debris Crash Fix* is installed, but...\n",
                                       "# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #\n",
                                       "  Weapon Debris Crash Fix is only required for Nvidia GPUs (NOT AMD / OTHER)\n",
                                       "  -----\n"])
                if "WeaponDebrisCrashFix.dll" not in logtext and gpu_nvidia:
                    output.writelines(["# ❌ WEAPON DEBRIS CRASH FIX ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  This is a mandatory patch / fix for players with Nvidia graphics cards.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/48078?tab=files\n",
                                       "  -----\n"])

                if "NVIDIA_Reflex.dll" in logtext and gpu_nvidia:
                    output.write("✔️ *Nvidia Reflex Support* is installed.\n  -----\n")
                elif "NVIDIA_Reflex.dll" in logtext and not gpu_nvidia and gpu_amd:
                    output.writelines(["❌ *Nvidia Reflex Support* is installed, but...\n",
                                       "# YOU DON'T HAVE AN NVIDIA GPU OR BUFFOUT 4 CANNOT DETECT YOUR GPU MODEL #\n",
                                       "  Nvidia Reflex Support is only available for Nvidia GPUs (NOT AMD / OTHER)\n",
                                       "  -----\n"])
                if "NVIDIA_Reflex.dll" not in logtext and gpu_nvidia:
                    output.writelines(["# ❌ NVIDIA REFLEX SUPPORT ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n",
                                       "  This is a highly recommended mod that can reduce render latency.\n",
                                       "  Link: https://www.nexusmods.com/fallout4/mods/64459?tab=files\n",
                                       "  -----\n"])
            else:
                output.write(Warn_BLOG_NOTE_Plugins)

            output.writelines(["====================================================\n",
                               "SCANNING THE LOG FOR SPECIFIC (POSSIBLE) CULPRITS...\n",
                               "====================================================\n"])

            list_DETPLUGINS = []
            list_DETFORMIDS = []
            list_ALLPLUGINS = []

            for line in loglines:
                if "MODULES:" in line:  # Check if crash log lists DLL and F4SE modules.
                    module_index = loglines.index(line)
                    next_line = loglines[module_index + 1]
                    if len(next_line) > 1:
                        if ("f4se_1_10_163.dll" in logtext or "f4sevr_1_2_72.dll" in logtext) and "steam_api64.dll" in logtext:
                            break
                        else:
                            output.write(Warn_BLOG_NOTE_Modules)

            output.write("LIST OF (POSSIBLE) PLUGIN CULPRITS:\n")

            for line in loglines:
                if "[" in line and "]" in line:  # Add all lines with Plugin IDs to list.
                    start_index = line.index("[")
                    end_index = line.index("]")
                    if end_index - start_index == 3 or end_index - start_index == 7:
                        list_ALLPLUGINS.append(line.strip())

                if "File:" in line and "Fallout4.esm" not in line:  # Add detected Plugins to list.
                    line = line.replace("File: ", "")
                    line = line.replace('"', '')
                    list_DETPLUGINS.append(line.strip())

            list_DETPLUGINS = list(filter(None, list_DETPLUGINS))  # Remove empty & invalid elements from list.
            list_remove = ["Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm", ""]
            for elem in list_remove:
                if elem in list_DETPLUGINS:
                    list_DETPLUGINS.remove(elem)

            list_DETPLUGINS = Counter(list_DETPLUGINS)
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
                output.writelines(["* AUTOSCAN COULDN'T FIND ANY PLUGIN CULPRITS *\n",
                                   "-----\n"])
            else:
                output.writelines(["-----\n",
                                   "[Last number counts how many times each plugin culprit shows up in the crash log.]\n",
                                   "These Plugins were caught by Buffout 4 and some of them might be responsible for this crash.\n",
                                   "You can try disabling these plugins and recheck your game, though this method can be unreliable.\n",
                                   "-----\n"])

            # ===========================================================

            output.write("LIST OF (POSSIBLE) FORM ID CULPRITS:\n")
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
            list_DETFORMIDS = list(dict.fromkeys(list_DETFORMIDS))  # Removes duplicates as dicts cannot have them.
            for elem in list_DETFORMIDS:
                output.write(f"{elem}\n")

            if not list_DETFORMIDS:
                output.writelines(["* AUTOSCAN COULDN'T FIND ANY FORM ID CULPRITS *\n",
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
                if "Name:" in line or "EditorID:" in line or "Function:" in line or any(elem in line.lower() for elem in List_Files):
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
            if Culprit_Trap is False:
                uCRASH_path = "CLAS-UNSOLVED/" + logname
                shutil.move(logname, uCRASH_path)
                uSCAN_path = "CLAS-UNSOLVED/" + logname + "-AUTOSCAN.md"
                shutil.move(logname + "-AUTOSCAN.md", uSCAN_path)

    # ========================== LOG END ==========================
    time.sleep(0.5)
    print("SCAN COMPLETE! (IT MIGHT TAKE SEVERAL SECONDS FOR SCAN RESULTS TO APPEAR)")
    print("SCAN RESULTS ARE AVAILABLE IN FILES NAMED crash-date-and-time-AUTOSCAN.md")
    print("===============================================================================")
    print("FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,")
    print("VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115")
    print("================================ CONTACT INFO =================================")
    print("DISCORD | Poet#9800 (https://discord.gg/DfFYJtt8p4)")
    print("NEXUS MODS | https://www.nexusmods.com/users/64682231")
    print("SCAN SCRIPT PAGE | https://www.nexusmods.com/fallout4/mods/56255")
    print(random.choice(Sneaky_Tips))

    # ============ CHECK FOR FAULTY LOGS & AUTO-SCANS =============
    list_SCANFAIL = []
    for file in glob(f"{SCAN_folder}/crash-*"):
        scan_name = str(file)
        with open(file, encoding="utf-8", errors="ignore") as LOG_Check:
            Line_Check = LOG_Check.readlines()
            line_count = sum(1 for _ in Line_Check)
            if ".txt" in scan_name or line_count < 20:  # Adjust if necessary. Failed scans are usually 16 lines.
                list_SCANFAIL.append(scan_name)
                statL_failed += 1
                statL_scanned -= 1

    if len(list_SCANFAIL) >= 1:
        print("NOTICE: Auto-Scanner WAS UNABLE TO PROPERLY SCAN THE FOLLOWING LOG(S): ")
        for elem in list_SCANFAIL:
            print(elem)
        print("===============================================================================")
        print("Most common reason for this are logs being incomplete or in the wrong format.")
        print("Make sure that your crash logs are saved with .log file format, NOT .txt!")

    # ====================== TERMINAL OUTPUT END ======================

    print("======================================================================")
    print("\nScanned all available logs in", (str(time.perf_counter() - 0.5 - start_time)[:7]), "seconds.")
    print("Number of Scanned Logs (No Autoscan Errors): ", statL_scanned)
    print("Number of Incomplete Logs (No Plugins List): ", statL_incomplete)
    print("Number of Failed Logs (Autoscan Can't Scan): ", statL_failed)
    print("(Set Stat Logging to true in Scan Crashlogs.ini for additional stats.)")
    print("-----")
    if CLAS_config.getboolean("MAIN", "Stat Logging") is True:
        print(crash_template("Logs with ", "Stack Overflow Crash.........", ".. ", "statC_Overflow"))
        print(crash_template("Logs with ", "Active Effects Crash.........", ".. ", "statC_ActiveEffects"))
        print(crash_template("Logs with ", "Bad Math Crash...............", ".. ", "statC_BadMath"))
        print(crash_template("Logs with ", "Null Crash...................", ".. ", "statC_Null"))
        print(crash_template("Logs with ", "DLL Crash....................", ".. ", "statC_DLL"))
        print(crash_template("Logs with ", "LOD Crash....................", ".. ", "statC_LOD"))
        print(crash_template("Logs with ", "MCM Crash....................", ".. ", "statC_MCM"))
        print(crash_template("Logs with ", "Decal Crash..................", ".. ", "statC_Decal"))
        print(crash_template("Logs with ", "Equip Crash..................", ".. ", "statC_Equip"))
        print(crash_template("Logs with ", "Script Crash.................", ".. ", "statC_Papyrus"))
        print(crash_template("Logs with ", "Generic Crash................", ".. ", "statC_Generic"))
        print(crash_template("Logs with ", "Antivirus Crash..............", ".. ", "statC_Antivirus"))
        print(crash_template("Logs with ", "BA2 Limit Crash..............", ".. ", "statC_BA2Limit"))
        print(crash_template("Logs with ", "Rendering Crash..............", ".. ", "statC_Rendering"))
        print(crash_template("Logs with ", "C++ Redist Crash.............", ".. ", "statC_Redist"))
        print(crash_template("Logs with ", "Grid Scrap Crash.............", ".. ", "statC_GridScrap"))
        print(crash_template("Logs with ", "Map Marker Crash.............", ".. ", "statC_MapMarker"))
        print(crash_template("Logs with ", "Mesh (NIF) Crash.............", ".. ", "statC_Mesh"))
        print(crash_template("Logs with ", "Texture (DDS) Crash..........", ".. ", "statC_Texture"))
        print(crash_template("Logs with ", "Material (BGSM) Crash........", ".. ", "statC_Material"))
        print(crash_template("Logs with ", "NPC Pathing Crash............", ".. ", "statC_NPCPathing"))
        print(crash_template("Logs with ", "Precombines Crash............", ".. ", "statC_Precomb"))
        print(crash_template("Logs with ", "Audio Driver Crash...........", ".. ", "statC_Audio"))
        print(crash_template("Logs with ", "Body Physics Crash...........", ".. ", "statC_BodyPhysics"))
        print(crash_template("Logs with ", "Leveled List Crash...........", ".. ", "statC_LeveledList"))
        print(crash_template("Logs with ", "Plugin Limit Crash...........", ".. ", "statC_PluginLimit"))
        print(crash_template("Logs with ", "Plugin Order Crash...........", ".. ", "statC_PluginOrder"))
        print(crash_template("Logs with ", "MO2 Extractor Crash..........", ".. ", "statC_MO2Unpack"))
        print(crash_template("Logs with ", "Nvidia Debris Crash..........", ".. ", "statC_NVDebris"))
        print(crash_template("Logs with ", "Nvidia Driver Crash..........", ".. ", "statC_NVDriver"))
        print(crash_template("Logs with ", "Nvidia Reflex Crash..........", ".. ", "statC_NVReflex"))
        print(crash_template("Logs with ", "Vulkan Memory Crash..........", ".. ", "statC_VulkanMem"))
        print(crash_template("Logs with ", "Vulkan Settings Crash........", ".. ", "statC_VulkanSet"))
        print(crash_template("Logs with ", "Console Command Crash........", ".. ", "statC_ConsoleCommand"))
        print(crash_template("Logs with ", "Game Corruption Crash........", ".. ", "statC_GameCorruption"))
        print(crash_template("Logs with ", "Water Collision Crash........", ".. ", "statC_Water"))
        print(crash_template("Logs with ", "Particle Effects Crash.......", ".. ", "statC_Particles"))
        print(crash_template("Logs with ", "Player Character Crash.......", ".. ", "statC_Player"))
        print(crash_template("Logs with ", "Animation / Physics Crash....", ".. ", "statC_AnimationPhysics"))
        print(crash_template("Logs with ", "Archive Invalidation Crash...", ".. ", "statC_Invalidation"))
        print("-----")
        print("Crashes caused by Clas. Hols. Weapons....", statM_CHW)
        print("-----")
        print(crash_template("Logs with ", "*[Item Crash]................", ".. ", "statU_Item"))
        print(crash_template("Logs with ", "*[Save Crash]................", ".. ", "statU_Save"))
        print(crash_template("Logs with ", "*[Input Crash]...............", ".. ", "statU_Input"))
        print(crash_template("Logs with ", "*[SS2 / WF Crash]............", ".. ", "statU_SS2WF"))
        print(crash_template("Logs with ", "*[Looks Menu Crash]..........", ".. ", "statU_LooksMenu"))
        print(crash_template("Logs with ", "*[NPC Patrol Crash]..........", ".. ", "statU_Patrol"))
        print(crash_template("Logs with ", "*[Ammo Counter Crash]........", ".. ", "statU_HUDAmmo"))
        print(crash_template("Logs with ", "*[Creation Club Crash].......", ".. ", "statU_CClub"))
        print(crash_template("Logs with ", "*[GPU Overclock Crash].......", ".. ", "statU_Overclock"))
        print(crash_template("Logs with ", "*[NPC Projectile Crash]......", ".. ", "statU_Projectile"))
        print(crash_template("Logs with ", "*[Camera Position Crash].....", ".. ", "statU_Camera"))
        print(" *Unsolved, see How To Read Crash Logs PDF")
        print("===========================================")
    return


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    import argparse

    parser = argparse.ArgumentParser(prog="Buffout 4 Crash Log Auto-Scanner", description="All command-line options are saved to the INI file.")
    # Argument values will simply change INI values since that requires the least refactoring
    # I will figure out a better way in a future iteration, this iteration simply mimics the GUI. - evildarkarchon
    parser.add_argument("--fcx-mode", action=argparse.BooleanOptionalAction, help="Enable (or disable) FCX mode")
    parser.add_argument("--imi-mode", action=argparse.BooleanOptionalAction, help="Enable (or disable) IMI mode")
    parser.add_argument("--stat-logging", action=argparse.BooleanOptionalAction, help="Enable (or disable) Stat Logging")
    parser.add_argument("--move-unsolved", action=argparse.BooleanOptionalAction, help="Enable (or disable) moving unsolved logs to a separate directory")
    parser.add_argument("--ini-path", type=Path, help="Set the directory that stores the game's INI files.")
    parser.add_argument("--scan-path", type=Path, help="Set which directory to scan")
    args = parser.parse_args()

    scan_path: Path = args.scan_path  # VSCode gives me type errors because args.* is set at runtime (doesn't know what types it's dealing with).
    ini_path: Path = args.ini_path  # Using intermediate variables with type annotations to satisfy it.

    # Default output value for an argparse.BooleanOptionalAction is None, and so fails the isinstance check.
    # So it will respect current INI values if not specified on the command line.
    if isinstance(args.fcx_mode, bool) and not args.fcx_mode == CLAS_config.getboolean("MAIN", "FCX Mode"):
        clas_ini_update("FCX Mode", str(args.fcx_mode).lower())

    if isinstance(args.imi_mode, bool) and not args.imi_mode == CLAS_config.getboolean("MAIN", "IMI Mode"):
        clas_ini_update("IMI Mode", str(args.imi_mode).lower())

    if isinstance(args.stat_logging, bool) and not args.stat_logging == CLAS_config.getboolean("MAIN", "Stat Logging"):
        clas_ini_update("Stat Logging", str(args.stat_logging).lower())

    if isinstance(args.move_unsolved, bool) and not args.move_unsolved == CLAS_config.getboolean("MAIN", "Move Unsolved"):
        clas_ini_update("Move Unsolved", str(args.move_unsolved).lower())

    if isinstance(ini_path, Path) and ini_path.resolve().is_dir() and not str(ini_path) == CLAS_config.get("MAIN", "INI Path"):
        clas_ini_update("INI Path", str(Path(ini_path).resolve()))

    if isinstance(scan_path, Path) and scan_path.resolve().is_dir() and not str(scan_path) == CLAS_config.get("MAIN", "Scan Path"):
        clas_ini_update("Scan Path", str(Path(scan_path).resolve()))

    clas_update_run()
    scan_logs()
    os.system("pause")
