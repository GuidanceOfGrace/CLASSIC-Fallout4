import configparser
import hashlib
import os
import platform
import stat
from dataclasses import dataclass, field
from glob import glob
from pathlib import Path

from Scan_Crashlogs import CLAS_config, clas_ini_create, clas_ini_update

if platform.system() == "Windows":
    import ctypes.wintypes
clas_ini_create()


def clas_ini_check(section: str, value: str):
    if isinstance(section, str) and isinstance(value, str):
        return CLAS_config.get(section, value)
    else:
        return CLAS_config.get(str(section), str(value))


# =================== WARNING MESSAGES ==================
# Can change first line to """\ to remove spacing.
Warn_CLAS_Broken_F4CINI = """
[!] WARNING : YOUR Fallout4Custom.ini FILE MIGHT BE BROKEN
    Disable FCX Mode or delete this INI file and create a new one.
    I also strongly advise using BethINI to readjust your INI settings.
"""
Warn_CLAS_Missing_F4SELOG = """
[!] WARNING : AUTO-SCANNER CANNOT FIND THE REQUIRED F4SE LOG FILE!
    MAKE SURE THAT FALLOUT 4 SCRIPT EXTENDER IS CORRECTLY INSTALLED!
    F4SE Link (Regular & VR Version): https://f4se.silverlock.org
"""
Warn_SCAN_Outdated_F4SE = """
# [!] CAUTION : REPORTED F4SE VERSION DOES NOT MATCH THE F4SE VERSION USED BY AUTOSCAN #
      UPDATE FALLOUT 4 SCRIPT EXTENDER IF NECESSARY: https://f4se.silverlock.org
      F4SE VERSION FOR VIRTUAL REALITY IS LOCATED ON THE SAME WEBSITE
"""
Warn_SCAN_Missing_F4SE_BO4 = """
# [!] CAUTION : SCRIPT EXTENDER REPORTS THAT BUFFOUT 4.DLL FAILED TO LOAD OR IS MISSING! #
      Buffout 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359
      Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115
"""
Warn_SCAN_Missing_F4SE_CORE = """
# [!] CAUTION : AUTO SCANNER CANNOT FIND FALLOUT 4 SCRIPT EXTENDER FILES OR THEY ARE MISSING! #
      FALLOUT 4 SCRIPT EXTENDER (F4SE): (Download Latest Build) https://f4se.silverlock.org
      Extract all files inside *f4se_0_06_XX* folder into your Fallout 4 game folder.
"""
Warn_SCAN_Missing_Buffout4 = """
# [!] CAUTION : AUTO-SCANNER CANNOT FIND BUFFOUT 4 FILES OR THEY ARE MISSING! #
      BUFFOUT 4: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47359
      Follow Buffout 4 installation steps here: https://www.nexusmods.com/fallout4/articles/3115
"""
Warn_SCAN_Missing_ADLIB = """
# [!] CAUTION : AUTO SCANNER CANNOT FIND ADDRESS LIBRARY FILE OR IT IS MISSING! #
      ADDRESS LIBRARY: (ONLY Use Manual Download Option) https://www.nexusmods.com/fallout4/mods/47327
      Extract the *version-1-10-163-0.bin* file manually into your Fallout 4/Data/F4SE/Plugins folder.
"""
Warn_SCAN_Log_Errors = """
# [!] CAUTION : THE FOLLOWING LOG FILES REPORT ONE OR MORE ERRORS! #
  [ You should open these files and check what errors are shown. ]
-----
"""
Warn_SCAN_NOTE_Preloader = """
# [!] NOTICE : Plugin Preloader is (manually) installed. It may rarely prevent the game from initializing correctly. #
      If the game fails to start after installing this mod, open *xSE PluginPreloader.xml* with a text editor and CHANGE
      <LoadMethod Name=\"ImportAddressHook\"> TO <LoadMethod Name=\"OnThreadAttach\"> OR <LoadMethod Name=\"OnProcessAttach\">
      IF THE GAME STILL REFUSES TO START, COMPLETELY REMOVE xSE PluginPreloader.xml AND IpHlpAPI.dll FROM YOUR FO4 GAME FOLDER
"""
Warn_SCAN_NOTE_DLL = """
# [!] NOTICE : MAIN ERROR REPORTS THAT A DLL FILE WAS INVOLVED IN THIS CRASH! #
  If the dll from main error belongs to a mod, that mod is likely the culprit.
"""
Warn_BLOG_NOTE_Modules = """\
# [!] NOTICE : BUFFOUT 4 COULDN'T LIST ALL MODULES OR F4SE IS NOT INSTALLED! #
      CHECK IF SCRIPT EXTENDER (F4SE) IS CORRECTLY INSTALLED! \n")
      Script Extender Link: https://f4se.silverlock.org \n")
"""


# =================== DEFINE LOCAL FILES ===================
@dataclass
class Info:
    # FO4 GAME FILES
    Address_Library: Path = field(default_factory=Path)
    Buffout_DLL: Path = field(default_factory=Path)
    Buffout_INI: Path = field(default_factory=Path)
    Buffout_TOML: Path = field(default_factory=Path)
    F4CK_EXE: Path = field(default_factory=Path)
    F4CK_Fixes: Path = field(default_factory=Path)
    F4SE_DLL: Path = field(default_factory=Path)
    F4SE_Loader: Path = field(default_factory=Path)
    F4SE_SDLL: Path = field(default_factory=Path)
    F4SE_VRDLL: Path = field(default_factory=Path)
    F4SE_VRLoader: Path = field(default_factory=Path)
    FO4_EXE: Path = field(default_factory=Path)
    Game_Path: str = field(default_factory=str)
    Game_Scripts: Path = field(default_factory=Path)
    Preloader_DLL: Path = field(default_factory=Path)
    Preloader_XML: Path = field(default_factory=Path)
    Steam_INI: Path = field(default_factory=Path)
    VR_Buffout: Path = field(default_factory=Path)
    VR_EXE: Path = field(default_factory=Path)
    # FO4 DOC FILES
    BO4_Achievements: Path = field(default_factory=Path)
    BO4_Looksmenu: Path = field(default_factory=Path)
    BO4_BakaSH: Path = field(default_factory=Path)
    FO4_F4SE_Logs: str = field(default_factory=str)
    FO4_F4SE_Path: Path = field(default_factory=Path)
    FO4_F4SEVR_Path: Path = field(default_factory=Path)
    FO4_Custom_Path: Path = field(default_factory=Path)
    FO4_Hash: dict[str, str] = field(default_factory=dict)

    def docs_file_check(self, docs_location: Path):
        self.BO4_Achievements = docs_location.joinpath("My Games", "Fallout4", "F4SE", "achievements.log")
        self.BO4_Looksmenu = docs_location.joinpath("My Games", "Fallout4", "F4SE", "f4ee.log")
        self.BO4_BakaSH = docs_location.joinpath("My Games", "Fallout4", "F4SE", "BakaScrapHeap.log")
        self.FO4_F4SE_Logs = str(docs_location.joinpath("My Games", "Fallout4", "F4SE"))
        self.FO4_F4SE_Path = docs_location.joinpath("My Games", "Fallout4", "F4SE", "f4se.log")
        self.FO4_F4SEVR_Path = docs_location.joinpath("My Games", "Fallout4", "F4SE", "f4sevr.log")
        self.FO4_Custom_Path = docs_location.joinpath("My Games", "Fallout4", "Fallout4Custom.ini")


info = Info()


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
        if "fallout4" in clas_ini_check("MAIN", "INI Path").lower():
            INI_Line = clas_ini_check("MAIN", "INI Path").strip()
            INI_Docs = Path(INI_Line)
            return INI_Docs
        else:  # Manual_Docs | PROMPT MANUAL INPUT IF DOCUMENTS FOLDER CANNOT BE FOUND.
            print("> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR Fallout4.ini IS LOCATED < <")
            Path_Input = input("(EXAMPLE: C:/Users/Zen/Documents/My Games/Fallout4 | Press ENTER to confirm.)\n> ")
            print("You entered :", Path_Input, "| This path will be automatically added to Scan Crashlogs.ini")
            Manual_Docs = Path(Path_Input.strip())
            clas_ini_update("INI Path", Path_Input)
            return Manual_Docs


info.docs_file_check(docs_path_check())  # type: ignore


# =================== CHECK MAIN FILES ===================
def scan_mainfiles():
    global info
    scan_mainfiles_report = []

    # CREATE / OPEN : Fallout4Custom.ini | CHECK : Archive Invalidaton
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
        except (configparser.MissingSectionHeaderError, configparser.ParsingError, OSError):
            scan_mainfiles_report.append(Warn_CLAS_Broken_F4CINI)
    else:
        with open(info.FO4_Custom_Path, "w+", encoding="utf-8", errors="ignore") as FO4_Custom:
            F4C_config = "[Archive]\nbInvalidateOlderFiles=1\nsResourceDataDirsFinal="
            FO4_Custom.write(F4C_config)

    # OPEN : f4se.log | f4sevr.log | CHECK : Game Path | F4SE Version | Errors | Buffout 4 DLL
    Error_List = []
    ALIB_Loaded = F4SE_Error = F4SE_Version = F4SE_Buffout = False
    if info.FO4_F4SE_Path.is_file():
        with open(info.FO4_F4SE_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for line in Path_Check:
                if "plugin directory" in line:
                    line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                    info.Game_Path = line.replace("\n", "")
                if "0.6.23" in line:
                    F4SE_Version = True
                if "error" in line.lower() or "failed" in line.lower():
                    F4SE_Error = True
                    Error_List.append(line)
                if "buffout4.dll" in line.lower() and "loaded correctly" in line.lower():
                    F4SE_Buffout = True
    elif info.FO4_F4SEVR_Path.is_file():
        with open(info.FO4_F4SEVR_Path, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for line in Path_Check:
                if "plugin directory" in line:
                    line = line[19:].replace("\\Data\\F4SE\\Plugins", "")
                    info.Game_Path = line.replace("\n", "")
                if "0.6.20" in line:
                    F4SE_Version = True
                if "error" in line.lower() or "failed" in line.lower():
                    F4SE_Error = True
                    Error_List.append(line)
                if "buffout4.dll" in line.lower() and "loaded correctly" in line.lower():
                    F4SE_Buffout = True
    else:
        scan_mainfiles_report.append(Warn_CLAS_Missing_F4SELOG)
        os.system("pause")

    if F4SE_Version == 1:
        scan_mainfiles_report.append("✔️ You have the latest version of Fallout 4 Script Extender (F4SE).\n  -----")
    else:
        scan_mainfiles_report.append(Warn_SCAN_Outdated_F4SE)

    if F4SE_Error == 1:
        scan_mainfiles_report.append("#[!] SCRIPT EXTENDER REPORTS THAT THE FOLLOWING PLUGINS FAILED TO LOAD! #\n")
        for elem in Error_List:
            scan_mainfiles_report.append(f"{elem}\n-----")
    else:
        scan_mainfiles_report.append("✔️ Script Extender reports that all DLL mod plugins have loaded correctly.\n  -----")

    if F4SE_Buffout == 1:
        scan_mainfiles_report.append("✔️ Script Extender reports that Buffout 4.dll was found and loaded correctly.\n  -----")
        ALIB_Loaded = True
    else:
        scan_mainfiles_report.append(Warn_SCAN_Missing_F4SE_BO4)

    # CHECK DOCUMENTS F4SE FOLDER LOG ERRORS
    def clas_log_errors(log_path):
        list_log_errors = []
        for filename in glob(f"{log_path}/*.log"):
            if not any(substring in filename for substring in ["crash-", "f4se.log", "Fallout4_dxgi.log"]):
                filepath = Path(filename).resolve()
                if filepath.is_file():
                    try:
                        with filepath.open("r+", encoding="utf-8", errors="ignore") as LOG_Check:
                            Log_Errors = LOG_Check.read()
                            if "error" in Log_Errors.lower() or "failed" in Log_Errors.lower():
                                logname = str(filepath)
                                list_log_errors.append(logname)
                    except OSError:
                        list_log_errors.append(str(filepath))
                        continue
        return list_log_errors

    if len(clas_log_errors(info.FO4_F4SE_Logs)) >= 1:
        scan_mainfiles_report.append(Warn_SCAN_Log_Errors)
        for elem in clas_log_errors(info.FO4_F4SE_Logs):
             scan_mainfiles_report.append(f"{elem}\n-----\n")
    else:
        scan_mainfiles_report.append("✔️ Available logs in your Documents Folder do not report any errors, all is well.\n  -----")

    # FILES TO LOOK FOR IN GAME FOLDER ONLY
    Game_Path = Path(rf"{info.Game_Path}")
    info.Game_Scripts = Game_Path.joinpath("Data", "Scripts")
    # ROOT FILES
    info.FO4_EXE = Game_Path.joinpath("Fallout4.exe")
    info.F4CK_EXE = Game_Path.joinpath("CreationKit.exe")
    info.F4CK_Fixes = Game_Path.joinpath("Data", "F4CKFixes")
    info.Steam_INI = Game_Path.joinpath("steam_api.ini")
    info.Preloader_DLL = Game_Path.joinpath("IpHlpAPI.dll")
    info.Preloader_XML = Game_Path.joinpath("xSE PluginPreloader.xml")
    # F4SE FILES
    info.F4SE_DLL = Game_Path.joinpath("f4se_1_10_163.dll")
    info.F4SE_SDLL = Game_Path.joinpath("f4se_steam_loader.dll")
    info.F4SE_Loader = Game_Path.joinpath("f4se_loader.exe")
    # VR FILES
    info.VR_EXE = Game_Path.joinpath("Fallout4VR.exe")
    info.VR_Buffout = Game_Path.joinpath("Data", "F4SE", "Plugins", "msdia140.dll")
    info.F4SE_VRDLL = Game_Path.joinpath("f4sevr_1_2_72.dll")
    info.F4SE_VRLoader = Game_Path.joinpath("f4sevr_loader.exe")
    # BUFFOUT FILES
    info.Buffout_DLL = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.dll")
    info.Buffout_INI = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.ini")
    info.Buffout_TOML = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.toml")
    info.Address_Library = Game_Path.joinpath("Data", "F4SE", "Plugins", "version-1-10-163-0.bin")
    # FALLLOUT 4 HASHES
    info.FO4_Hash = {"1.10.163": "77fd1be89a959aba78cf41c27f80e8c76e0e42271ccf7784efd9aa6c108c082d83c0b54b89805ec483500212db8dd18538dafcbf75e55fe259abf20d49f10e60"}

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

    if f4se_scripts_check(info.Game_Scripts, f4se_scripts_list) >= 29:
        scan_mainfiles_report.extend(["✔️ All F4SE Script files are accounted for in your Fallout 4 / Data / Scripts folder.",
                                      "  -----"])
    else:
        scan_mainfiles_report.extend(["# ❌ CAUTION : SOME F4SE SCRIPT FILES ARE MISSING #",
                                      "  YOU NEED TO REINSTALL FALLOUT 4 SCRIPT EXTENDER",
                                      "  F4SE LINK: https://f4se.silverlock.org \n"])

    # CHECK FALLOUT4.EXE INTEGRITY
    if info.FO4_EXE.is_file():
        FO4_EXE_Size = os.path.getsize(info.FO4_EXE)
        if FO4_EXE_Size == 65503104 and hashlib.sha512(info.FO4_EXE.read_bytes()).hexdigest() == info.FO4_Hash["1.10.163"] and not info.Steam_INI.is_file():
            scan_mainfiles_report.extend(["✔️ Your Fallout 4 is updated to version [1.10.163.0]",
                                          "    * This is the version BEFORE the 2023 Update *",
                                          "  -----"])
        # elif FO4_EXE_Size == xxxxxxxx and not info.Steam_INI.is_file(): | RESERVED
        #    scan_mainfiles_report.extend(["✔️ Your Fallout 4 is updated to version [1.xx.xxx.x]",
        #                                  "   * This is the version AFTER the 2023 Update *",
        #                                  "  -----"])
        elif FO4_EXE_Size == 65503104 and not info.Steam_INI.is_file():
            scan_mainfiles_report.append("# ❌ CAUTION : YOUR FALLOUT 4 VERSION IS OUT OF DATE #\n  -----")
        elif FO4_EXE_Size == 65503104 and info.Steam_INI.is_file():  # Intentional, don't change the unicode icon.
            scan_mainfiles_report.append("# \U0001F480 CAUTION : YOUR FALLOUT 4 VERSION IS OUT OF DATE #\n  -----")

    # CHECK FALLOUT 4 ROOT FOLDER LOG ERRORS
    if len(clas_log_errors(info.Game_Path)) >= 1:
        scan_mainfiles_report.append(Warn_SCAN_Log_Errors)
        for elem in clas_log_errors(info.Game_Path):
             scan_mainfiles_report.append(f"{elem}\n-----\n")
    else:
        scan_mainfiles_report.append("✔️ Available logs in your Game Folder do not report any additional errors.\n  -----")

    # CHECK BUFFOUT 4 REQUIREMENTS | IMI MODE
    if str(clas_ini_check("MAIN", "IMI Mode")).lower() == "false":
        if info.Preloader_XML.is_file() and info.Preloader_DLL.is_file():
            scan_mainfiles_report.append(Warn_SCAN_NOTE_Preloader)
        else:
            scan_mainfiles_report.append('❌ OPTIONAL: *Plugin Preloader* is NOT (manually) installed.\n  -----')

        if (info.F4SE_VRDLL.is_file() and info.F4SE_VRLoader.is_file()) or (info.F4SE_DLL.is_file() and info.F4SE_Loader.is_file() and info.F4SE_SDLL.is_file()):
            scan_mainfiles_report.append("✔️ REQUIRED: *Fallout 4 Script Extender* is (manually) installed.\n  -----")
        else:
            scan_mainfiles_report.append(Warn_SCAN_Missing_F4SE_CORE)

        if info.Address_Library.is_file() or ALIB_Loaded is True:
            scan_mainfiles_report.append("✔️ REQUIRED: *Address Library* is (manually) installed.\n  -----")
        else:
            scan_mainfiles_report.append(Warn_SCAN_Missing_ADLIB)

    # RENAME TOML BECAUSE PYTHON CAN'T WRITE TO IT
    if info.Buffout_TOML.is_file():
        try:
            os.chmod(info.Buffout_TOML, stat.S_IWRITE)
            os.rename(info.Buffout_TOML, info.Buffout_INI)
        except (FileExistsError, OSError):
            os.remove(info.Buffout_INI)
            os.chmod(info.Buffout_TOML, stat.S_IWRITE)
            os.rename(info.Buffout_TOML, info.Buffout_INI)

    # AVOID CONFIGPARSER BECAUSE OF DUPLICATE COMMENT IN Buffout4.toml
    # To preserve original toml formatting, just stick to replace.

    # CHECK BUFFOUT 4 INI SETTINGS AND AUTO ADJUST
    if info.Buffout_INI.is_file() and info.Buffout_DLL.is_file():
        scan_mainfiles_report.append("✔️ REQUIRED: *Buffout 4* is (manually) installed. Checking configuration...\n  -----")
        with open(info.Buffout_INI, "r+", encoding="utf-8", errors="ignore") as BUFF_Custom:
            BUFF_config = BUFF_Custom.read()
            BUFF_lines = BUFF_config.splitlines()
            for line in BUFF_lines:
                if "=" in line and "symcache" not in line.lower():
                    if any(setting in line for setting in ["true", "false", "-1", "2048", "4096", "8192"]):
                        pass
                    else:
                        scan_mainfiles_report.extend(["# [!] CAUTION : THE FOLLOWING *Buffout4.toml* VALUE OR PARAMETER IS INVALID #",
                                                     f"{line}",
                                                      "[ Correct all typos / formatting / capitalized letters from this line in Buffout4.toml.]",
                                                      "-----"])

            if info.BO4_Achievements.is_file() and "Achievements = true" in BUFF_config:
                scan_mainfiles_report.extend(["# ❌ WARNING: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #",
                                              "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.",
                                              "-----"])
                BUFF_config = BUFF_config.replace("Achievements = true", "Achievements = false")
            else:
                scan_mainfiles_report.append("✔️ Achievements parameter in *Buffout4.toml* is correctly configured.\n  -----")

            if info.BO4_BakaSH.is_file() and "MemoryManager = true" in BUFF_config:
                scan_mainfiles_report.extend(["# ❌ WARNING: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #",
                                              "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4.",
                                              "-----"])
                BUFF_config = BUFF_config.replace("MemoryManager = true", "MemoryManager = false")
            else:
                scan_mainfiles_report.append("✔️ Memory Manager parameter in *Buffout4.toml* is correctly configured.\n  -----")

            if info.BO4_Looksmenu.is_file() and "F4EE = false" in BUFF_config:
                scan_mainfiles_report.extend(["# ❌ WARNING: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #",
                                              "Auto-Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu.",
                                              "-----"])
                BUFF_config = BUFF_config.replace("F4EE = false", "F4EE = true")
            else:
                scan_mainfiles_report.append("✔️ Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured.\n  -----")

            if "MaxStdIO = -1" in BUFF_config or "MaxStdIO = 512" in BUFF_config:
                scan_mainfiles_report.extend(["# ❌ WARNING: MaxStdIO parameter value in *Buffout4.toml* might be too low.",
                                              "Auto-Scanner will increase this value to 8192 to prevent BA2 Limit crashes.",
                                              "-----"])
                BUFF_config = BUFF_config.replace("MaxStdIO = -1", "MaxStdIO = 8192")
                BUFF_config = BUFF_config.replace("MaxStdIO = 512", "MaxStdIO = 8192")
            else:
                scan_mainfiles_report.append("✔️ MaxStdIO parameter value in *Buffout4.toml* is correctly configured.\n  -----")

        with open(info.Buffout_INI, "w+", encoding="utf-8", errors="ignore") as BUFF_Custom:
            BUFF_Custom.write(BUFF_config)
    else:
        scan_mainfiles_report.append(Warn_SCAN_Missing_Buffout4)

    if info.Buffout_INI.is_file():  # CONVERT INI BACK TO TOML
        try:
            os.chmod(info.Buffout_INI, stat.S_IWRITE)
            os.rename(info.Buffout_INI, info.Buffout_TOML)
        except (FileExistsError, OSError):
            os.remove(info.Buffout_TOML)
            os.chmod(info.Buffout_INI, stat.S_IWRITE)
            os.rename(info.Buffout_INI, info.Buffout_TOML)

    return scan_mainfiles_report


# =================== CHECK MOD FILES ===================
def scan_modfiles():
    global info
    scan_modfiles_report = []

    # CHECK SPECIFIC GAME MODS / EXTENSIONS | IMI MODE
    if str(clas_ini_check("MAIN", "IMI Mode")).lower() == "false":
        scan_modfiles_report.extend(["IF YOU'RE USING DYNAMIC PERFORMANCE TUNER AND/OR LOAD ACCELERATOR,",
                                     "remove these mods completely and switch to High FPS Physics Fix!",
                                     "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files",
                                     "-----"])

        if info.VR_EXE.is_file() and info.VR_Buffout.is_file():
            scan_modfiles_report.append("*✔️ Buffout 4 VR Version* is (manually) installed.\n  -----")
        elif info.VR_EXE.is_file() and not info.VR_Buffout.is_file():
            scan_modfiles_report.extend(["# ❌ BUFFOUT 4 FOR VR VERSION ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                         "  This is a mandatory Buffout 4 port for the VR Version of Fallout 4.",
                                         "  Link: https://www.nexusmods.com/fallout4/mods/64880?tab=files",
                                         "  -----"])
        else:
            scan_modfiles_report.append("❌ *Fallout 4 VR* is NOT installed.\n  -----")

        if (info.F4CK_EXE.is_file() and os.path.exists(info.F4CK_Fixes)) or (isinstance(info.Game_Path, str) and Path(info.Game_Path).joinpath("winhttp.dll").is_file()):  # type: ignore
            scan_modfiles_report.append("✔️ *Creation Kit Fixes* is (manually) installed.\n  -----")
        elif info.F4CK_EXE.is_file() and not os.path.exists(info.F4CK_Fixes):
            scan_modfiles_report.extend(["# ❌ CREATION KIT FIXES ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                         "  This is a highly recommended patch for the Fallout 4 Creation Kit.",
                                         "  Link: https://www.nexusmods.com/fallout4/mods/51165?tab=files\n",
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
