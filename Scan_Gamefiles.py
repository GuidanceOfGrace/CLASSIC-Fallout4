import configparser
import hashlib
import os
import platform
import stat
import subprocess
from glob import glob
from pathlib import Path

from CLASlib import CLAS
from Scan_Crashlogs import CLAS_Globals

try:
    import tomlkit
except (ImportError, ModuleNotFoundError):
    subprocess.run(["pip", "install", "tomlkit"], shell=True)
    import tomlkit

if platform.system() == "Windows":
    import ctypes.wintypes

CLAS.clas_ini_create()


# =================== WARNING MESSAGES ==================
# Can change first line to """\ to remove spacing.
CLAS_Globals.Warnings["Warn_CLAS_Broken_F4CINI"] = """
[!] WARNING : YOUR Fallout4Custom.ini FILE MIGHT BE BROKEN
    Disable FCX Mode or delete this INI file and create a new one.
    I also strongly advise using BethINI to readjust your INI settings.
"""
CLAS_Globals.Warnings["Warn_CLAS_Missing_F4SELOG"] = """
[!] WARNING : AUTO-SCANNER CANNOT FIND THE REQUIRED F4SE LOG FILE!
    MAKE SURE THAT FALLOUT 4 SCRIPT EXTENDER IS CORRECTLY INSTALLED!
    F4SE Link (Regular & VR Version): https://f4se.silverlock.org
"""
CLAS_Globals.Warnings["Warn_SCAN_Outdated_F4SE"] = """
# [!] CAUTION : REPORTED F4SE VERSION DOES NOT MATCH THE F4SE VERSION USED BY AUTOSCAN #
      UPDATE FALLOUT 4 SCRIPT EXTENDER IF NECESSARY: https://f4se.silverlock.org
      F4SE VERSION FOR VIRTUAL REALITY IS LOCATED ON THE SAME WEBSITE
"""
CLAS_Globals.Warnings["Warn_SCAN_Missing_F4SE_BO4"] = """
# [!] CAUTION : SCRIPT EXTENDER REPORTS THAT BUFFOUT 4.DLL FAILED TO LOAD OR IS MISSING! #
      Buffout 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359
      Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115
"""
CLAS_Globals.Warnings["Warn_SCAN_Missing_F4SE_CORE"] = """
# [!] CAUTION : AUTO SCANNER CANNOT FIND FALLOUT 4 SCRIPT EXTENDER FILES OR THEY ARE MISSING! #
      FALLOUT 4 SCRIPT EXTENDER (F4SE): (Download Latest Build) https://f4se.silverlock.org
      Extract all files inside *f4se_0_06_XX* folder into your Fallout 4 game folder.
"""
CLAS_Globals.Warnings["Warn_SCAN_Missing_Buffout4"] = """
# [!] CAUTION : AUTO-SCANNER CANNOT FIND BUFFOUT 4 FILES OR THEY ARE MISSING! #
      BUFFOUT 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359
      Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115
"""
CLAS_Globals.Warnings["Warn_SCAN_Missing_ADLIB"] = """
# [!] CAUTION : AUTO SCANNER CANNOT FIND REQUIRED ADDRESS LIBRARY FILE OR IT IS MISSING! #
      ADDRESS LIBRARY: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47327
      ADDRESS LIBRARY VR: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/64879
      Extract the *version.bin* or *version.csv* file manually into your Fallout 4/Data/F4SE/Plugins folder.
"""
CLAS_Globals.Warnings["Warn_SCAN_Log_Errors"] = """
# [!] CAUTION : THE FOLLOWING LOG FILES REPORT ONE OR MORE ERRORS! #
  [ Errors do not necessarily mean that the mod is not working. ]
  -----"""
CLAS_Globals.Warnings["Warn_SCAN_NOTE_Preloader"] = """
# [!] NOTICE : Plugin Preloader is (manually) installed. It may rarely prevent the game from initializing correctly. #
      If the game fails to start after installing this mod, open *xSE PluginPreloader.xml* with a text editor and CHANGE
      <LoadMethod Name=\"ImportAddressHook\"> TO <LoadMethod Name=\"OnThreadAttach\"> OR <LoadMethod Name=\"OnProcessAttach\">
      IF THE GAME STILL REFUSES TO START, COMPLETELY REMOVE xSE PluginPreloader.xml AND IpHlpAPI.dll FROM YOUR FO4 GAME FOLDER
"""
CLAS_Globals.Warnings["Warn_SCAN_NOTE_DLL"] = """
# [!] NOTICE : MAIN ERROR REPORTS THAT A DLL FILE WAS INVOLVED IN THIS CRASH! #
  If the dll from main error belongs to a mod, that mod is likely the culprit.
"""
CLAS_Globals.Warnings["Warn_BLOG_NOTE_Modules"] = """\
# [!] NOTICE : BUFFOUT 4 COULDN'T LIST ALL MODULES OR F4SE IS NOT INSTALLED! #
      CHECK IF SCRIPT EXTENDER (F4SE) IS CORRECTLY INSTALLED! \n")
      Script Extender Link: https://f4se.silverlock.org \n")
"""


def docs_path_check():
    FO4_STEAM_ID = 377160
    Loc_Found = False
    if platform.system() == "Windows":  # Win_Docs | Find where FO4 is installed via Windows
        CSIDL_PERSONAL = 5  # (My) Documents folder from user.
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value.
        User_Documents = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)  # type: ignore
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, User_Documents)  # type: ignore
        Win_Docs = Path(User_Documents.value)
        Loc_Found = True
        return Win_Docs
    else:  # Lin_Docs | Find where FO4 is installed via Steam if Linux
        libraryfolders_path = Path.home().joinpath(".local", "share", "Steam", "steamapps", "common", "libraryfolders.vdf")
        if libraryfolders_path.is_file():
            library_path = None
            with libraryfolders_path.open(encoding="utf-8", errors="ignore") as steam_library_raw:
                steam_library = steam_library_raw.readlines()
            for library_line in steam_library:
                if "path" in library_line:
                    library_path = Path(library_line.split('"')[3])
                if str(FO4_STEAM_ID) in library_line:
                    library_path = library_path.joinpath("steamapps")  # type: ignore
                    Lin_Docs = library_path.joinpath("compatdata", str(FO4_STEAM_ID), "pfx", "drive_c", "users", "steamuser", "My Documents", "My Games", "Fallout4")
                    if library_path.joinpath("common", "Fallout 4").exists() and Lin_Docs.exists():
                        Loc_Found = True
                        return Lin_Docs

    if Loc_Found is False:  # INI_Docs | CHECK CLAS INI IF DOCUMENTS FOLDER IS ALREADY GIVEN.
        if "fallout4" in CLAS_Globals.clas_ini_check("MAIN", "INI Path").lower():
            INI_Line = CLAS_Globals.clas_ini_check("MAIN", "INI Path").strip()
            INI_Docs = Path(INI_Line)
            return INI_Docs
        else:  # Manual_Docs | PROMPT MANUAL INPUT IF DOCUMENTS FOLDER CANNOT BE FOUND.
            print("> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR Fallout4.ini IS LOCATED < <")
            Path_Input = input("(EXAMPLE: C:/Users/Zen/Documents/My Games/Fallout4 | Press ENTER to confirm.)\n> ")
            print("You entered :", Path_Input, "| This path will be automatically added to Scan Crashlogs.ini")
            Manual_Docs = Path(Path_Input.strip())
            CLAS_Globals.clas_ini_update("INI Path", Path_Input)
            return Manual_Docs


# =================== CHECK MAIN FILES ===================
def scan_mainfiles():
    scan_mainfiles_report = []

    # CREATE / OPEN : Fallout4Custom.ini | CHECK : Archive Invalidaton
    if CLAS_Globals.info.FO4_Custom_Path.is_file():
        try:
            os.chmod(CLAS_Globals.info.FO4_Custom_Path, stat.S_IWRITE)
            F4C_config = configparser.ConfigParser()
            F4C_config.optionxform = str  # type: ignore
            F4C_config.read(CLAS_Globals.info.FO4_Custom_Path)
            if "Archive" not in F4C_config.sections():
                F4C_config.add_section("Archive")
            F4C_config.set("Archive", "bInvalidateOlderFiles", "1")
            F4C_config.set("Archive", "sResourceDataDirsFinal", "")
            with open(CLAS_Globals.info.FO4_Custom_Path, "w+", encoding="utf-8", errors="ignore") as FO4_Custom:
                F4C_config.write(FO4_Custom, space_around_delimiters=False)
        except (configparser.MissingSectionHeaderError, configparser.ParsingError, OSError):
            scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_CLAS_Broken_F4CINI"])
    else:
        with open(CLAS_Globals.info.FO4_Custom_Path, "w+", encoding="utf-8", errors="ignore") as FO4_Custom:
            F4C_config = "[Archive]\nbInvalidateOlderFiles=1\nsResourceDataDirsFinal="
            FO4_Custom.write(F4C_config)

    # OPEN : f4se.log | f4sevr.log | CHECK : Game Path | F4SE Version | Errors | Buffout 4 DLL
    Error_List = []
    ADLIB_Loaded = F4SE_Error = F4SE_Version = F4SE_Buffout = False
    if CLAS_Globals.info.FO4_F4SE_Path.is_file():
        with open(CLAS_Globals.info.FO4_F4SE_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for line in Path_Check:
                if "plugin directory" in line:
                    line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                    CLAS_Globals.info.Game_Path = line.replace("\n", "")
                if "0.6.23" in line:
                    F4SE_Version = True
                if "error" in line.lower() or "failed" in line.lower():
                    F4SE_Error = True
                    Error_List.append(line)
                if "buffout4.dll" in line.lower() and "loaded correctly" in line.lower():
                    F4SE_Buffout = True
    elif CLAS_Globals.info.FO4_F4SEVR_Path.is_file():
        with open(CLAS_Globals.info.FO4_F4SEVR_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for line in Path_Check:
                if "plugin directory" in line:
                    line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                    CLAS_Globals.info.Game_Path = line.replace("\n", "")
                if "0.6.20" in line:
                    F4SE_Version = True
                if "error" in line.lower() or "failed" in line.lower():
                    F4SE_Error = True
                    Error_List.append(line)
                if "buffout4.dll" in line.lower() and "loaded correctly" in line.lower():
                    F4SE_Buffout = True
    else:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_CLAS_Missing_F4SELOG"])
        os.system("pause")

    if F4SE_Version == 1:
        scan_mainfiles_report.append("✔️ You have the latest version of Fallout 4 Script Extender (F4SE).\n  -----")
    else:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Outdated_F4SE"])

    if F4SE_Error == 1:
        scan_mainfiles_report.append("#[!] SCRIPT EXTENDER REPORTS THAT THE FOLLOWING PLUGINS FAILED TO LOAD! #\n")
        for elem in Error_List:
            scan_mainfiles_report.append(f"{elem}\n-----")
    else:
        scan_mainfiles_report.append("✔️ Script Extender reports that all DLL mod plugins have loaded correctly.\n  -----")

    if F4SE_Buffout == 1:
        scan_mainfiles_report.append("✔️ Script Extender reports that Buffout 4.dll was found and loaded correctly.\n  -----")
        ADLIB_Loaded = True
    else:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Missing_F4SE_BO4"])

    

    # CHECK DOCUMENTS F4SE FOLDER LOG ERRORS
    def clas_log_errors(log_path):
        list_log_errors = []
        for filename in glob(f"{log_path}/*.log"):
            if not any(substring in filename for substring in ["crash-", "f4se.log", "Fallout4_dxgi.log"]):
                logname = ""
                filepath = Path(filename).resolve()
                if filepath.is_file():
                    try:
                        with filepath.open("r+", encoding="utf-8", errors="ignore") as LOG_Check:
                            Log_Errors = LOG_Check.readlines()
                            for line in Log_Errors:
                                if "error" in line.lower() or "failed" in line.lower() and "keybind" not in line.lower():
                                    logname = str(filepath)
                                    list_log_errors.append(f"  LOG PATH > {logname}\n  ERROR > {line}")
                    except OSError:
                        list_log_errors.append(f"  ❌ Auto Scanner was unable to scan this log file :\n  {logname}")
                        continue
        return list_log_errors

    if len(clas_log_errors(CLAS_Globals.info.FO4_F4SE_Logs)) >= 1:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Log_Errors"])
        for elem in clas_log_errors(CLAS_Globals.info.FO4_F4SE_Logs):
            scan_mainfiles_report.append(elem)
    elif len(clas_log_errors(CLAS_Globals.info.FO4_F4SEVR_Logs)) >= 1:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Log_Errors"])
        for elem in clas_log_errors(CLAS_Globals.info.FO4_F4SEVR_Logs):
            scan_mainfiles_report.append(elem)
    else:
        scan_mainfiles_report.append("✔️ Available logs in your Documents Folder do not report any errors, all is well.\n  -----")
    
    # FILES TO LOOK FOR IN GAME FOLDER ONLY
    Game_Path = Path(rf"{CLAS_Globals.info.Game_Path}")
    CLAS_Globals.info.Game_Scripts = Game_Path.joinpath("Data", "Scripts")
    # ROOT FILES
    CLAS_Globals.info.FO4_EXE = Game_Path.joinpath("Fallout4.exe")
    CLAS_Globals.info.F4CK_EXE = Game_Path.joinpath("CreationKit.exe")
    CLAS_Globals.info.F4CK_Fixes = Game_Path.joinpath("Data", "F4CKFixes")
    CLAS_Globals.info.Steam_INI = Game_Path.joinpath("steam_api.ini")
    CLAS_Globals.info.Preloader_DLL = Game_Path.joinpath("IpHlpAPI.dll")
    CLAS_Globals.info.Preloader_XML = Game_Path.joinpath("xSE PluginPreloader.xml")
    # F4SE FILES
    CLAS_Globals.info.F4SE_DLL = Game_Path.joinpath("f4se_1_10_163.dll")
    CLAS_Globals.info.F4SE_SDLL = Game_Path.joinpath("f4se_steam_loader.dll")
    CLAS_Globals.info.F4SE_Loader = Game_Path.joinpath("f4se_loader.exe")
    # VR FILES
    CLAS_Globals.info.VR_EXE = Game_Path.joinpath("Fallout4VR.exe")
    CLAS_Globals.info.VR_Buffout = Game_Path.joinpath("Data", "F4SE", "Plugins", "msdia140.dll")
    CLAS_Globals.info.F4SE_VRDLL = Game_Path.joinpath("f4sevr_1_2_72.dll")
    CLAS_Globals.info.F4SE_VRLoader = Game_Path.joinpath("f4sevr_loader.exe")
    # BUFFOUT FILES
    CLAS_Globals.info.Buffout_DLL = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.dll")
    CLAS_Globals.info.Buffout_TOML = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.toml")
    CLAS_Globals.info.Address_Library = Game_Path.joinpath("Data", "F4SE", "Plugins", "version-1-10-163-0.bin")
    CLAS_Globals.info.Address_LibraryVR = Game_Path.joinpath("Data", "F4SE", "Plugins", "version-1-2-72-0.csv")
    # FALLLOUT 4 HASHES
    CLAS_Globals.info.FO4_Hash = {"1.10.163": "77fd1be89a959aba78cf41c27f80e8c76e0e42271ccf7784efd9aa6c108c082d83c0b54b89805ec483500212db8dd18538dafcbf75e55fe259abf20d49f10e60"}

    CLAS_Globals.info.docs_file_check(docs_path_check())  # type: ignore

    # CHECK F4SE SCRIPT FILES INTEGRITY

    def f4se_scripts_check(scripts_dir, f4se_scripts):
        script_files = os.listdir(scripts_dir)
        matching_scripts = 0
        for script in script_files:
            if script in f4se_scripts:
                matching_scripts += 1
        scan_mainfiles_report.append(f"  * {matching_scripts} / {len(f4se_scripts)} * F4SE script files were found in your Fallout 4 / Data / Scripts folder.\n  -----")
        return matching_scripts

    f4se_scripts_list = ["Actor.pex", "ActorBase.pex", "Armor.pex", "ArmorAddon.pex", "Cell.pex", "Component.pex", "ConstructibleObject.pex", "DefaultObject.pex", "EncounterZone.pex",
                         "EquipSlot.pex", "F4SE.pex", "FavoritesManager.pex", "Form.pex", "Game.pex", "HeadPart.pex", "Input.pex", "InstanceData.pex", "Location.pex", "Math.pex",
                         "MatSwap.pex", "MiscObject.pex", "ObjectMod.pex", "ObjectReference.pex", "Perk.pex", "ScriptObject.pex", "UI.pex", "Utility.pex", "WaterType.pex", "Weapon.pex"]

    if f4se_scripts_check(CLAS_Globals.info.Game_Scripts, f4se_scripts_list) >= 29:
        scan_mainfiles_report.extend(["✔️ All F4SE Script files are accounted for in your Fallout 4 / Data / Scripts folder.",
                                      "  -----"])
    else:
        scan_mainfiles_report.extend(["# ❌ CAUTION : SOME F4SE SCRIPT FILES ARE MISSING #",
                                      "  YOU NEED TO REINSTALL FALLOUT 4 SCRIPT EXTENDER",
                                      "  F4SE LINK: https://f4se.silverlock.org \n"])

    # CHECK FALLOUT4.EXE INTEGRITY
    if CLAS_Globals.info.FO4_EXE.is_file():
        FO4_EXE_Size = os.path.getsize(CLAS_Globals.info.FO4_EXE)
        if FO4_EXE_Size == 65503104 and hashlib.sha512(CLAS_Globals.info.FO4_EXE.read_bytes()).hexdigest() == CLAS_Globals.info.FO4_Hash["1.10.163"] and not CLAS_Globals.info.Steam_INI.is_file():
            scan_mainfiles_report.extend(["✔️ Your Fallout 4 is updated to version [1.10.163.0]",
                                          "    * This is the version BEFORE the 2023 Update *",
                                          "  -----"])
        # elif FO4_EXE_Size == xxxxxxxx and not CLAS_Globals.info.Steam_INI.is_file(): | RESERVED
        #    scan_mainfiles_report.extend(["✔️ Your Fallout 4 is updated to version [1.xx.xxx.x]",
        #                                  "   * This is the version AFTER the 2023 Update *",
        #                                  "  -----"])
        elif FO4_EXE_Size == 65503104 and not CLAS_Globals.info.Steam_INI.is_file():
            scan_mainfiles_report.append("# ❌ CAUTION : YOUR FALLOUT 4 VERSION IS OUT OF DATE #\n  -----")
        elif FO4_EXE_Size == 65503104 and CLAS_Globals.info.Steam_INI.is_file():  # Intentional, don't change the unicode icon.
            scan_mainfiles_report.append("# \U0001F480 CAUTION : YOUR FALLOUT 4 VERSION IS OUT OF DATE #\n  -----")

    # CHECK FALLOUT 4 ROOT FOLDER LOG ERRORS
    if len(clas_log_errors(CLAS_Globals.info.Game_Path)) >= 1:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Log_Errors"])
        for elem in clas_log_errors(CLAS_Globals.info.Game_Path):
            scan_mainfiles_report.append(f"{elem}\n-----\n")
    else:
        scan_mainfiles_report.append("✔️ Available logs in your Game Folder do not report any additional errors.\n  -----")

    # CHECK BUFFOUT 4 REQUIREMENTS | IMI MODE
    if str(CLAS_Globals.clas_ini_check("MAIN", "IMI Mode")).lower() == "false":
        if CLAS_Globals.info.Preloader_XML.is_file() and CLAS_Globals.info.Preloader_DLL.is_file():
            scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_NOTE_Preloader"])
        else:
            scan_mainfiles_report.append('❌ OPTIONAL: *Plugin Preloader* is NOT (manually) installed.\n  -----')

        if (CLAS_Globals.info.F4SE_VRDLL.is_file() and CLAS_Globals.info.F4SE_VRLoader.is_file()) or (CLAS_Globals.info.F4SE_DLL.is_file() and CLAS_Globals.info.F4SE_Loader.is_file() and CLAS_Globals.info.F4SE_SDLL.is_file()):
            scan_mainfiles_report.append("✔️ REQUIRED: *Fallout 4 Script Extender* is (manually) installed.\n  -----")
        else:
            scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Missing_F4SE_CORE"])

        if CLAS_Globals.info.Address_Library.is_file() or CLAS_Globals.info.Address_LibraryVR.is_file() or ADLIB_Loaded is True:
            scan_mainfiles_report.append("✔️ REQUIRED: *Address Library* is (manually) installed.\n  -----")
        else:
            scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Missing_ADLIB"])

    # MODIFY TOML WRITE PERMISSIONS
    if CLAS_Globals.info.Buffout_TOML.is_file():
        os.chmod(CLAS_Globals.info.Buffout_TOML, stat.S_IWRITE)

    # CHECK BUFFOUT 4 INI SETTINGS AND AUTO ADJUST
    if CLAS_Globals.info.Buffout_TOML.is_file() and CLAS_Globals.info.Buffout_DLL.is_file():
        scan_mainfiles_report.append("✔️ REQUIRED: *Buffout 4* is (manually) installed. Checking configuration...\n  -----")
        with open(CLAS_Globals.info.Buffout_TOML, "r+", encoding="utf-8", errors="ignore") as BUFF_Custom:
            BUFF_config: tomlkit.TOMLDocument = tomlkit.load(BUFF_Custom)

            if CLAS_Globals.info.BO4_Achievements.is_file() and BUFF_config["Patches"]["Achievements"] == True:  # type: ignore
                scan_mainfiles_report.extend(["# ❌ WARNING: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #",
                                              "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.",
                                              "-----"])
                BUFF_config["Patches"]["Achievements"] = False  # type: ignore
            else:
                scan_mainfiles_report.append("✔️ Achievements parameter in *Buffout4.toml* is correctly configured.\n  -----")

            if CLAS_Globals.info.BO4_BakaSH.is_file() and BUFF_config["Patches"]["MemoryManager"] == True:  # type: ignore
                scan_mainfiles_report.extend(["# ❌ WARNING: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #",
                                              "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.",
                                              "-----"])
                BUFF_config["Patches"]["MemoryManager"] = False  # type: ignore
            else:
                scan_mainfiles_report.append("✔️ Memory Manager parameter in *Buffout4.toml* is correctly configured.\n  -----")

            if CLAS_Globals.info.BO4_Looksmenu.is_file() and BUFF_config["Compatibility"]["F4EE"] == False:  # type: ignore
                scan_mainfiles_report.extend(["# ❌ WARNING: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #",
                                              "Auto-Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu.",
                                              "-----"])
                BUFF_config["Compatibility"]["F4EE"] = True  # type: ignore
            else:
                scan_mainfiles_report.append("✔️ Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured.\n  -----")

            if BUFF_config["Patches"]["MaxStdIO"] != 2048:   # type: ignore
                match (BUFF_config["Patches"]["MaxStdIO"]):  # type: ignore
                    case elem if elem < 2048:  # type: ignore
                        scan_mainfiles_report.extend(["# ❌ WARNING: MaxStdIO parameter value in *Buffout4.toml* might be too low.",
                                                      "Auto-Scanner will increase this value to 2048 to prevent BA2 Limit crashes.",
                                                      "-----"])
                    case elem if elem > 2048:  # type: ignore
                        scan_mainfiles_report.extend(["# ❌ WARNING: MaxStdIO parameter value in *Buffout4.toml* might be too high.",   # Placeholder message courtesy of Github Copilot
                                                    "Auto-Scanner will change this value to 2048 to prevent possible crashes.",
                                                    "-----"])
                    case elem if not isinstance(elem, int):  # type: ignore
                        scan_mainfiles_report.extend(["# ❌ WARNING: MaxStdIO parameter value in *Buffout4.toml* is not a number.",   # Another placeholder message courtesy of Github Copilot
                                                    "Auto-Scanner will change this value to 2048.",
                                                    "-----"])
                BUFF_config["Patches"]["MaxStdIO"] = 2048   # type: ignore
            else:
                scan_mainfiles_report.append("✔️ MaxStdIO parameter value in *Buffout4.toml* is correctly configured.\n  -----")

        with open(CLAS_Globals.info.Buffout_TOML, "w+", encoding="utf-8", errors="ignore") as BUFF_Custom:
            tomlkit.dump(BUFF_config, BUFF_Custom)
    else:
        scan_mainfiles_report.append(CLAS_Globals.Warnings["Warn_SCAN_Missing_Buffout4"])

    return scan_mainfiles_report


# =================== CHECK MOD FILES ===================
def scan_modfiles():
    scan_modfiles_report = []

    # CHECK SPECIFIC GAME MODS / EXTENSIONS | IMI MODE
    if str(CLAS_Globals.clas_ini_check("MAIN", "IMI Mode")).lower() == "false":
        scan_modfiles_report.extend(["IF YOU'RE USING DYNAMIC PERFORMANCE TUNER AND/OR LOAD ACCELERATOR,",
                                     "remove these mods completely and switch to High FPS Physics Fix!",
                                     "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files",
                                     "-----"])

        if CLAS_Globals.info.VR_EXE.is_file() and CLAS_Globals.info.VR_Buffout.is_file():
            scan_modfiles_report.append("*✔️ Buffout 4 VR Version* is (manually) installed.\n  -----")
        elif CLAS_Globals.info.VR_EXE.is_file() and not CLAS_Globals.info.VR_Buffout.is_file():
            scan_modfiles_report.extend(["# ❌ BUFFOUT 4 FOR VR VERSION ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                         "  This is a mandatory Buffout 4 port for the VR Version of Fallout 4.",
                                         "  Link: https://www.nexusmods.com/fallout4/mods/64880?tab=files",
                                         "  -----"])
        else:
            scan_modfiles_report.append("❌ *Fallout 4 VR* is NOT installed.\n  -----")

        if (CLAS_Globals.info.F4CK_EXE.is_file() and os.path.exists(CLAS_Globals.info.F4CK_Fixes)) or (isinstance(CLAS_Globals.info.Game_Path, str) and Path(CLAS_Globals.info.Game_Path).joinpath("winhttp.dll").is_file()):  # type: ignore
            scan_modfiles_report.append("✔️ *Creation Kit Fixes* is (manually) installed.\n  -----")
        elif CLAS_Globals.info.F4CK_EXE.is_file() and not os.path.exists(CLAS_Globals.info.F4CK_Fixes):
            scan_modfiles_report.extend(["# ❌ CREATION KIT FIXES ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                         "  This is a highly recommended patch for the Fallout 4 Creation Kit.",
                                         "  Link: https://www.nexusmods.com/fallout4/mods/51165?tab=files",
                                         "  -----"])
        else:
            scan_modfiles_report.append("❌ *Creation Kit* is NOT installed.\n  -----")

    return scan_modfiles_report


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    for line in scan_mainfiles():
        print(line)
    for line in scan_modfiles():
        print(line)
    os.system("pause")
