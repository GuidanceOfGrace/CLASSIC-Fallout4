import configparser
import hashlib
import os
import platform
import re
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import requests
import tomlkit

if platform.system() == "Windows":
    import ctypes.wintypes

'''AUTHOR NOTES (POET):
- In cases where output.write is used instead of output.writelines, this was done to more easily copy-paste content.
- Comments marked as RESERVED in all scripts are intended for future updates or tests, do not edit / move / remove.
- (..., encoding="utf-8", errors="ignore") needs to go with every opened file because unicode errors are a bitch.
'''


# =================== CLAS TOML FILE ===================
def clas_toml_create():
    if not os.path.exists("CLAS Settings.toml"):  # INI FILE FORCLAS
        toml_settings = """[MAIN]
# This file contains settings for both source scripts and Crash Log Auto Scanner.exe
# Set to true if you want CLAS to check that you have the latest version of CLAS.
"Update Check" = true

# FCX - File Check Xtended | Set to true if you want CLAS to check the integrity of your game files and core mods.
"FCX Mode" = true

# IMI - Ignore Manual Installation | Set to true if you want CLAS to hide / ignore all manual installation warnings.
# I still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager.
"IMI Mode" = false

# Set to true if you want CLAS to show extra stats about scanned logs in the command line window.
"Stat Logging" = false

# Set to true if you want CLAS to move all unsolved logs and their autoscans to CL-UNSOLVED folder.
# Unsolved logs are all crash logs where CLAS didn't detect any known crash errors or messages.
"Move Unsolved" = false

# Set or copy-paste your INI directory path below. Example: INI Path = C:/Users/Zen/Documents/My Games/Fallout4
# Only required if Profile Specific INIs are enabled in MO2 or you moved your Documents folder somewhere else.
# I highly recommend that you disable Profile Specific Game INI Files in MO2, located in Tools > Profiles...
"INI Path" = ""

# Set or copy-paste your custom scan folder path below, from which your crash logs will be scanned.
# If no path is set, CLAS will search for logs in the same folder from which you are running the exe.
"Scan Path" = ""
"""
        toml_data = tomlkit.parse(toml_settings)
        with open("CLAS Settings.toml", "w+", encoding="utf-8", errors="ignore") as TOML_Autoscan:
            TOML_Autoscan.write(toml_data.as_string())


clas_toml_create()


# ================= INI UPDATE FUNCTIONS =================
def clas_toml_update(section: Union[str, bool], value: Union[str, bool]):  # For checking & writing to INI.
    UNIVERSE.CLAS_config[section] = value

    with open("CLAS Settings.toml", "w+", encoding="utf-8", errors="ignore") as TOML:
        TOML.write(UNIVERSE.CLAS_TOML.as_string())


def mods_ini_config(file_path, section, key, new_value=None):
    mod_config = configparser.ConfigParser()
    mod_config.optionxform = str  # type: ignore
    mod_config.read(file_path)

    if section not in mod_config:
        raise configparser.Error(f"ERROR : Section '{section}' does not exist in '{file_path}'")
    if key not in mod_config[section]:
        raise configparser.Error(f"ERROR : Key '{key}' does not exist in section '{section}'")

    # If new_value is specified, update the value in INI.
    if new_value is not None:
        mod_config[section][key] = new_value
        with open(file_path, 'w') as config_file:
            mod_config.write(config_file)
        return new_value

    # Return current value of the key.
    return mod_config[section][key]


# ================= CLAS UPDATE FUNCTIONS ================
# Don't forget to update the API link for specific games.
def clas_update_check():
    if UNIVERSE.CLAS_config["Update Check"] is True:
        print("\n ❓ CHECKING FOR NEW CRASH LOG AUTO SCANNER (CLAS) UPDATES...")
        print("    (You can disable this check in the EXE or CLAS Settings.ini)")
        try:
            response = requests.get("https://api.github.com/repos/GuidanceOfGrace/Buffout4-CLAS/releases/latest")  # type: ignore
            CLAS_Received = response.json()["name"]
            if CLAS_Received == UNIVERSE.CLAS_Current:
                print("\n ✔️ You have the latest version of CLAS! \n")
                return True
            else:
                print(GALAXY.Warnings["Warn_CLAS_Outdated"])
                print("===============================================================================")
        except (OSError, requests.exceptions.RequestException):
            print(GALAXY.Warnings["Warn_CLAS_Update_Failed"])
            print("===============================================================================")
    else:
        print("\n ❌ NOTICE: UPDATE CHECK IS DISABLED IN CLAS INI SETTINGS \n")
        print("===============================================================================")
    return False


class ClasUniversalVars:  # Set comment_prefixes to unused char to keep INI comments.
    with open("CLAS Settings.toml", "r", encoding="utf-8", errors="ignore") as toml_in:
        CLAS_TOML: tomlkit.TOMLDocument = tomlkit.parse(toml_in.read())
    CLAS_config: tomlkit.items.Table = CLAS_TOML["MAIN"] # type: ignore
    
    CLAS_Current = "CLAS v6.95"
    CLAS_Date = "250423"

    LOG_Errors_Catch = ("critical", "error", "failed")

    LOG_Errors_Exclude = ("keybind", "failed to open pdb", "failed to register method", "failed to get next record",
                          "no errors with this", "unable to locate pdb")

    LOG_Files_Exclude = ("crash-", "cbpfo4.log", "CreationKit", "DumpStack.log", "f4se.log", "Fallout4_dxgi.log", "HHS.log")

    Crash_Records_Catch = LOG_Errors_Catch + ("editorid:", "file:", "function:", "name:", ".bgsm", ".bto", ".btr", ".dds", ".dll+", ".fuz", ".hkb", ".hkx",
                                              ".ini", ".nif", ".pex", ".swf", ".strings", ".txt", ".uvd", ".wav", ".xwm", "data\\", "data/")
    
    LOG_Catch_Pattern = re.compile('|'.join(re.escape(pattern) for pattern in LOG_Errors_Catch), re.IGNORECASE) # Equivalent to any() without the need for a loop.
    LOG_Exclude_Pattern = re.compile('^(?!' + '|'.join(re.escape(err) for err in LOG_Errors_Exclude) + ')', re.IGNORECASE) # Equivalent to all() without the need for a loop.
    LOG_Files_Exclude_Pattern = re.compile('^(?!' + '|'.join(re.escape(err) for err in LOG_Files_Exclude) + ')', re.IGNORECASE)


UNIVERSE = ClasUniversalVars()


class ClasSpecificVars:
    Game_Name = "Fallout 4"
    Game_Docs = "Fallout4"
    Game_Docs_Found = False
    Game_SID = 377160  # Steam ID Number
    Game_Size_OLD = 65503104  # Old Valid EXE Size
    Game_Size_NEW = 00000000  # New Valid EXE Size
    Game_HASH = {
        "1.10.163": "77fd1be89a959aba78cf41c27f80e8c76e0e42271ccf7784efd9aa6c108c082d83c0b54b89805ec483500212db8dd18538dafcbf75e55fe259abf20d49f10e60",
        "Actor.pex": "9333aa9b33d6009933afc3a1234a89ca93b5522ea186b44bc6c78846ed5a82c4",
        "ActorBase.pex": "cb5d29fead7df77eca8674101abdc57349a8cf345f18c3ddd6ef8d94ad254da7",
        "Armor.pex": "2bc34ab0d58f701e8684fc911742257e0768bd3e63b1eb8bdb2e043e7b67346b",
        "ArmorAddon.pex": "5d9ff578b6e401526dbddedf93bdbccb4e202dba2b8b2e77809140b48fc8c1af",
        "Cell.pex": "25d742d4fbe274fe5b8b3adc3775964ab9e22c1f32c47d5d3102b735c5b4e190",
        "Component.pex": "80eef0f21bb7b1b9882c4a953a24aff3df8095f8464c006a96fafc0858f9b889",
        "ConstructibleObject.pex": "51bdb39c81465bfbbbe509dc0a1ed40baebf4791cb35c978108e4334bcabc017",
        "DefaultObject.pex": "715dff0394599587c4596488d66aab4d91311361a3ebec24a91d0ce1ddf39d77",
        "EncounterZone.pex": "be0efccf70adc3a6a28f2465044d4df44cf7abe409c8624f6695d9a193eb96b6",
        "EquipSlot.pex": "0e00da824263e60041086cc721896aeb304c7ec6d38fba1f548df96fda0c9ff3",
        "F4SE.pex": "7d3b1be07259c9078c7f3f60cdf12041401024485750a303b0faec686a25047a",
        "FavoritesManager.pex": "aed53963a5e725cea561f67525c1d50297c7a8410e6a5738b00356908d5daca7",
        "Form.pex": "3ac9cd7ecb22d377800ca316413eb1d8f4def3ff3721a14b4c6fa61500f9f568",
        "Game.pex": "19c858908f1a2054755b602121e5944dbbfb1ee0be38a24a532e6ab2f9390f4d",
        "HeadPart.pex": "d25869fbf81b7d351e71cd17b6913cae01dd1b58ba76419050df6af1ed6525af",
        "Input.pex": "9509a73024680963b8446b57247fdf160513a540531e87a0e2faedb610b1ffcd",
        "InstanceData.pex": "57e68c4b355a94b709950ccec297b3d466f1d25e5029fed9e1423e8a12dd179f",
        "Location.pex": "3538c0aaa4fe450828aee3848fe317c1654c8ed39bd811be9cff22a1e7618b49",
        "Math.pex": "9bb0019795b85076837ac6845d0c79d65c9826739e59c43b97cfb949f611e822",
        "MatSwap.pex": "b49d34fe1b6387d19df5140ddfbd9c340d3b10fc396e003142cdc755dc6815fc",
        "MiscObject.pex": "7615656ab2867c5502507d1189cf7f938919dc585608698d2f31f782d858d23c",
        "ObjectMod.pex": "d02235b5013375bf0c7785408380b3a567697879a966818df883256031b8a2b8",
        "ObjectReference.pex": "97cfd2749b70545c9378955b09a898631fa03a0e235623b76f2c5631f2801be5",
        "Perk.pex": "04a9d0309198cbeb3a419265490be03e051d35b17b7f8ce749ffc4ea0673e16c",
        "ScriptObject.pex": "a395b7fc15b193b6d8ef0184dff6293100e79ec4dd431d85e10515da46e0502c",
        "UI.pex": "6b7a65b8be433bcb99dbe07d4ca9e9de2fa94140d402247b877351c2b34a36d5",
        "Utility.pex": "e10d65904d0a1e9ee568bdaba02636f0183bfa9565b4056758b1461540f9be75",
        "WaterType.pex": "c4f8589ed33f72265e95a6bec2c9cab58667795e972bcf5f7d17c40deed43207",
        "Weapon.pex": "f39cf899d90d47d694873ccaa2a72308c6717f5e36a302d6f95243e53672d77d"}
    GameVR_HASH = {}  # RESERVED

    XSE_Symbol = "F4SE"
    XSE_Handle = "Fallout 4 Script Extender (F4SE)"
    XSEOG_Latest = "0.6.23"
    XSEVR_Latest = "0.6.20"
    CRASHGEN_Handle = "Buffout 4"
    CRASHGEN_DLL = "buffout4.dll"
    CRASHGEN_OLD = "Buffout 4 v1.26.2"
    CRASHGEN_NEW = "Buffout 4 v1.31.1 Feb 28 2023 00:32:02"
    ADLIB_Loaded = False

    scan_game_report = []

    Game_Plugins_Exclude = ("Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm")

    Crash_Records_Exclude = Game_Plugins_Exclude + ('""', "...", "Buffout4.dll+", "d3d11.dll+", "dxgi.dll+", "[FE:", "f4se", "KERNEL", "kernel32.dll+", "MSVC", "ntdll", "flexRelease_x64.dll+",
                                                    "nvcuda64.dll+", "cudart64_75.dll+", "nvwgf2umx.dll+", "nvumdshimx.dll+", "steamclient64.dll+", "Unhandled", "USER32", "usvfs_x64", "vrclient_x64.dll+", "win32u")

    XSE_Scripts_Count = 29

    XSE_Scripts_List = ("Actor.pex", "ActorBase.pex", "Armor.pex", "ArmorAddon.pex", "Cell.pex", "Component.pex", "ConstructibleObject.pex", "DefaultObject.pex",
                        "EncounterZone.pex", "EquipSlot.pex", "F4SE.pex", "FavoritesManager.pex", "Form.pex", "Game.pex", "HeadPart.pex", "Input.pex", "InstanceData.pex", "Location.pex",
                        "Math.pex", "MatSwap.pex", "MiscObject.pex", "ObjectMod.pex", "ObjectReference.pex", "Perk.pex", "ScriptObject.pex", "UI.pex", "Utility.pex", "WaterType.pex", "Weapon.pex")

    # ===================== FLAVOR TEXT =====================
    Sneaky_Tips = ("\nRandom Hint: [Ctrl] + [F] is a handy-dandy key combination. You should use it more often. Please.\n",
                   "\nRandom Hint: Patrolling the Buffout 4 Nexus Page almost makes you wish this joke was more overused.\n",
                   "\nRandom Hint: You have a crash log where CLAS couldn't find any solutions? Feel free to send it to me.\n",
                   "\nRandom Hint: 20% of all crashes are caused by Classic Holstered Weapons mod. 80% of all statistics are made up.\n",
                   "\nRandom Hint: No, I don't know why your game froze instead of crashed. But I know someone who might know; Google.\n",
                   "\nRandom Hint: Spending 5 morbillion hours asking for help can save you from 5 minutes of reading the documentation.\n",
                   "\nRandom Hint: When necessary, make sure that crashes are consistent or repeatable, since in rare cases they aren't.\n",
                   "\nRandom Hint: When posting crash logs, it's helpful to mention the last thing you were doing before the crash happened.\n",
                   "\nRandom Hint: Be sure to revisit both Buffout 4 Crash Article and CLAS Nexus Page from time to time to check for updates.\n")

    # ================== WB PLUGIN CHECKER ==================
    # Can change first line to """\ to remove the spacing.

    WB_Problems = {
        "Corrupted": """\
    ❓ Wrye Bash could not read these plugins, as they might be corrupted.
       You should resave them in Creation Kit and then check if problems persist.
       If WB still reports these as corrupted after resaving, remove them completely.
""",
        "Incorrect ESL Flag": """\
    ❓ These plugins have an incorrectly assigned ESL flag or extension.
       Remove the ESL flag with FO4Edit or rename the extension to .esp.
       These plugins could potentially crash the game if you don't do this.
""",
        "Missing Masters": """\
    ❓ These plugins have missing requirements (required mods cannot be found).
       Either install missing requirements or completely remove these plugins.
""",
        "Delinquent Masters": """\
    ❓ These plugins are not in the correct load order. You should run Wrye Bash
       and reorder plugins with orange checkboxes until they turn green or yellow.
       Incorrect load order will either crash the game or break some ingame items.
""",
        "Old Header Form Versions": """\
    ❓ These plugins have a header that is older than the minimum Creation Kit version.
       Such plugins need to be resaved in Creation Kit to fix the incorrect header.
""",
        "Deleted Navmeshes": """\
    ❓ These plugins have deleted navmeshes. They can often cause a crash
       in specific areas. Try to find a patch that fixes their navmeshes
       or disable these plugins first if you ever get a navmesh crash.
""",
        "Deleted Base Records": """\
    ❓ These plugins have deleted base records. They might cause a crash
       and deleted records can only be manually restored with FO4Edit.
""",
        "HITMEs": """\
    ❓ These plugins contain Higher Index Than Masterlist Entries, which are mainly
       caused by improper FO4Edit or CK edits. Resave these plugins in Creation Kit.
       If HITMEs persist, such plugins may not work correctly and could cause a crash.
""",
        "Duplicate FormIDs": """\
    ❓ These Form IDs occur at least twice in the listed plugins. This is undefined behavior
       that may result in crashes or unpredictable issues and this can only be fixed in FO4Edit.
       Contact the mod authors and consider uninstalling these plugins if you encounter problems.
""",
        "Record Type Collisions": """\
    ❓ These Records are overriding each other, but have different record types. This behavior
       can often lead to crashes or cause various issues and this can only be fixed in FO4Edit.
       Contact the mod authors and consider uninstalling these plugins if you encounter problems.
""",
        "Probable Injected Collisions": """\
    ❓ These Injected Records are overriding each other, but have different Editor IDs.
       This can cause some problems and their Editor IDs should be renamed to match each other.
       Contact the mod authors and consider uninstalling these plugins if you encounter problems.
""",
        # =================== SEARCH IN TITLE ===================
        "Invalid": """\
    ❓ These plugins were made with a non-standard or invalid Creation Kit version.
       Resave these plugins in Creation Kit and check if problems or errors persist.
""",
        "Cleaning With": """\
    ❓ These plugins have ITMs or UDRs which can be cleaned manually with
       Quick Auto Clean or automatically with Plugin Auto Cleaning Tool.
"""}

    # =================== WARNING MESSAGES ==================
    # Can change first line to """\ to remove the spacing.

    Warnings = {
        "Warn_CLAS_Outdated": """
❌ WARNING : YOUR CLAS VERSION IS OUT OF DATE!
   Please download the latest version from here:
   https://www.nexusmods.com/fallout4/mods/56255
""",
        "Warn_CLAS_Update_Failed": """
❌ WARNING : AN ERROR OCCURRED! CLAS WAS UNABLE TO CHECK FOR UPDATES, BUT WILL CONTINUE SCANNING.
   CHECK FOR ANY CLAS UPDATES HERE: https://www.nexusmods.com/fallout4/mods/56255
""",
        "Warn_SCAN_Arch_Inv": """
❌ Archive Invalidation / Loose Files setting is not enabled.
   CLAS will now enable this setting automatically in the INI.
""",
        "Warn_SCAN_FCX_Enabled": """\
* NOTICE: FCX MODE IS ENABLED. AUTOSCAN MUST BE RUN BY ORIGINAL USER FOR CORRECT DETECTION *
[ To disable mod & game files detection, disable FCX Mode in the exe or CLAS Settings.ini ]

""",
        "Warn_SCAN_FCX_Disabled": """\
* NOTICE: FCX MODE IS DISABLED. YOU CAN ENABLE IT TO DETECT PROBLEMS IN MOD & GAME FILES *
[ FCX Mode can be enabled in the exe or CLAS Settings.ini located in your CLAS folder. ]

""",
        "Warn_SCAN_Log_Errors": """
# [!] CAUTION : THE FOLLOWING LOG FILES REPORT ONE OR MORE ERRORS! #
  [ Errors do not necessarily mean that the mod is not working. ]
  -----
""",
        "Warn_SCAN_NOTE_DLL": """\
* NOTICE : MAIN ERROR REPORTS THAT A DLL FILE WAS INVOLVED IN THIS CRASH! *
  If the dll from main error belongs to a mod, that mod is likely the culprit.

""",
        "Warn_SCAN_NOTE_WryeCheck": """\
* ❌ NOTICE : PLUGIN CHECKER REPORT FROM WRYE BASH WAS NOT FOUND *
  To check your load order and detect additional problems; install and run Wrye Bash,
  then select View > Plugin Checker from the top bar in the main Wrye Bash window.
  WB Link (Use MANUAL DOWNLOAD): https://www.nexusmods.com/fallout4/mods/20032
""",

        "Warn_TOML_Achievements": """\
# ❌ CAUTION : Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #
  FIX: Open *Buffout4.toml* and change Achievements parameter to FALSE, this prevents conflicts with Buffout 4.
  -----
""",
        "Warn_TOML_Memory": """\
# ❌ CAUTION : Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #
  FIX: Open *Buffout4.toml* and change MemoryManager parameter to FALSE, this prevents conflicts with Buffout 4.
  -----
""",
        "Warn_TOML_F4EE": """\
# ❌ CAUTION : Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #
  FIX: Open *Buffout4.toml* and change F4EE parameter to TRUE, this prevents bugs and crashes from Looks Menu.
  -----
""",
        "Warn_TOML_STDIO": """\
# ❌ CAUTION : MaxStdIO parameter value in *Buffout4.toml* might be too low. #
  FIX: Open *Buffout4.toml* and change MaxStdIO value to 2048, this might prevent some crashes or bugs.
  -----
""",
        "Warn_SCAN_Outdated_Buffout4": """
# [!] CAUTION : REPORTED BUFFOUT 4 VERSION DOES NOT MATCH THE VERSION USED BY AUTOSCAN #
  UPDATE BUFFOUT 4 IF NECESSARY: https://www.nexusmods.com/fallout4/mods/64880
""",
        "Warn_BLOG_NOTE_Plugins": """\
# [!] NOTICE : BUFFOUT 4 COULDN'T LOAD THE PLUGIN LIST FOR THIS CRASH LOG! #
  Autoscan cannot continue. Try scanning a different crash log
  OR copy-paste your *loadorder.txt* into your CLAS folder.
  -----
""",
        "Warn_CLAS_Broken_F4CINI": """
[!] WARNING : YOUR Fallout4Custom.ini FILE MIGHT BE BROKEN
    Disable FCX Mode or delete this INI file and create a new one.
    I also strongly advise using BethINI to readjust your INI settings.
    -----
""",
        "Warn_CLAS_Missing_F4SELOG": """
[!] WARNING : AUTO-SCANNER CANNOT FIND THE REQUIRED F4SE LOG FILE!
    MAKE SURE THAT FALLOUT 4 SCRIPT EXTENDER IS CORRECTLY INSTALLED!
    F4SE Link (Regular & VR Version): https://f4se.silverlock.org
""",
        "Warn_SCAN_Outdated_F4SE": """
# [!] CAUTION : REPORTED F4SE VERSION DOES NOT MATCH THE F4SE VERSION USED BY AUTOSCAN #
      UPDATE FALLOUT 4 SCRIPT EXTENDER IF NECESSARY: https://f4se.silverlock.org
      F4SE VERSION FOR VIRTUAL REALITY IS LOCATED ON THE SAME WEBSITE
""",
        "Warn_SCAN_Missing_F4SE_BO4": """
# [!] CAUTION : SCRIPT EXTENDER REPORTS THAT BUFFOUT 4.DLL FAILED TO LOAD OR IS MISSING! #
      Buffout 4: (Use MANUAL DOWNLOAD) https://www.nexusmods.com/fallout4/mods/47359
      Use the Buffout 4 guide here: https://www.nexusmods.com/fallout4/articles/3115
""",
        "Warn_SCAN_Missing_F4SE_CORE": """
# [!] CAUTION : AUTO SCANNER CANNOT FIND FALLOUT 4 SCRIPT EXTENDER FILES OR THEY ARE MISSING! #
      FALLOUT 4 SCRIPT EXTENDER (F4SE): (Download Latest Build) https://f4se.silverlock.org
      Extract all files inside *f4se_0_06_XX* folder into your Fallout 4 game folder.
""",
        "Warn_SCAN_Missing_Buffout4": """
# [!] CAUTION : AUTO-SCANNER CANNOT FIND BUFFOUT 4 FILES OR THEY ARE MISSING! #
      BUFFOUT 4: (Use MANUAL DOWNLOAD) https://www.nexusmods.com/fallout4/mods/47359
      Use the Buffout 4 guide here: https://www.nexusmods.com/fallout4/articles/3115
""",
        "Warn_SCAN_Missing_ADLIB": """
# [!] CAUTION : AUTO SCANNER CANNOT FIND REQUIRED ADDRESS LIBRARY FILE OR IT IS MISSING! #
      ADDRESS LIBRARY: (Use MANUAL DOWNLOAD) https://www.nexusmods.com/fallout4/mods/47327
      ADDRESS LIBRARY VR: (Use MANUAL DOWNLOAD) https://www.nexusmods.com/fallout4/mods/64879
      Manually extract either *version.bin* or *version.csv* into Fallout 4/Data/F4SE/Plugins
""",
        "Warn_SCAN_NOTE_Preloader": """
* NOTICE : Plugin Preloader is (manually) installed. It may rarely prevent the game from initializing correctly. *
  If the game fails to start after installing this mod, open *xSE PluginPreloader.xml* with a text editor and CHANGE
  <LoadMethod Name=\"ImportAddressHook\"> TO <LoadMethod Name=\"OnThreadAttach\"> OR <LoadMethod Name=\"OnProcessAttach\">
  IF THE GAME STILL REFUSES TO START, COMPLETELY REMOVE xSE PluginPreloader.xml AND IpHlpAPI.dll FROM YOUR FO4 GAME FOLDER
"""}


GALAXY = ClasSpecificVars()


# DO NOT USE @staticmethod FOR ANY, NOT CALLABLE FOR PYINSTALLER
# =================== DEFINE LOCAL FILES ===================
@dataclass
class ClasLocalFiles:
    # GENERAL GAME FILES
    Game_EXE: Path = field(default_factory=Path)
    Game_Path: str = field(default_factory=str)
    Game_Root: Path = field(default_factory=Path)
    Game_Data: Path = field(default_factory=Path)
    Game_Scripts: Path = field(default_factory=Path)
    CreationKit_EXE: Path = field(default_factory=Path)
    CreationKit_Fixes: Path = field(default_factory=Path)
    XSE_DLL: Path = field(default_factory=Path)
    XSE_Loader: Path = field(default_factory=Path)
    XSE_SteamDLL: Path = field(default_factory=Path)
    XSE_VRDLL: Path = field(default_factory=Path)
    XSE_VRLoader: Path = field(default_factory=Path)
    # FO4 GAME FILES
    Address_Library: Path = field(default_factory=Path)
    Address_LibraryVR: Path = field(default_factory=Path)
    Buffout_DLL: Path = field(default_factory=Path)
    Buffout_TOML: Path = field(default_factory=Path)
    Preloader_DLL: Path = field(default_factory=Path)
    Preloader_XML: Path = field(default_factory=Path)
    Steam_INI: Path = field(default_factory=Path)
    VR_Buffout: Path = field(default_factory=Path)
    VR_EXE: Path = field(default_factory=Path)
    WB_Plugin_Check: Path = field(default_factory=Path)
    # FO4 DOC FILES
    BO4_Achievements_LOG: Path = field(default_factory=Path)
    BO4_LooksMenu_LOG: Path = field(default_factory=Path)
    BO4_BakaSH_LOG: Path = field(default_factory=Path)
    FO4_F4SE_Path: str = field(default_factory=str)
    FO4_F4SEVR_Path: str = field(default_factory=str)
    FO4_F4SE_LOG: Path = field(default_factory=Path)
    FO4_F4SEVR_LOG: Path = field(default_factory=Path)
    FO4_Custom_INI: Path = field(default_factory=Path)
    FO4_Hash: dict[str, str] = field(default_factory=dict)

    def docs_file_check(self, docs_location: Path):
        self.BO4_Achievements_LOG = docs_location.joinpath("My Games", "Fallout4", "F4SE", "achievements.log")
        self.BO4_LooksMenu_LOG = docs_location.joinpath("My Games", "Fallout4", "F4SE", "f4ee.log")
        self.BO4_BakaSH_LOG = docs_location.joinpath("My Games", "Fallout4", "F4SE", "BakaScrapHeap.log")
        self.FO4_F4SE_Path = str(docs_location.joinpath("My Games", "Fallout4", "F4SE"))
        self.FO4_F4SE_LOG = docs_location.joinpath("My Games", "Fallout4", "F4SE", "f4se.log")
        self.FO4_F4SEVR_Path = str(docs_location.joinpath("My Games", "Fallout4VR", "F4SE"))
        self.FO4_F4SEVR_LOG = docs_location.joinpath("My Games", "Fallout4VR", "F4SE", "f4sevr.log")
        self.FO4_Custom_INI = docs_location.joinpath("My Games", "Fallout4", "Fallout4Custom.ini")
        self.WB_Plugin_Check = docs_location.joinpath("My Games", "Fallout4", "ModChecker.html")

        # =========== CHECK DOCUMENTS -> CHECK GAME PATH ===========

        '''GPT Changes:
        In this updated version, I've made the following changes:

Used snake_case for function and variable names.
Used f-strings for better string formatting.
Added type hints to the function signatures.
Replaced print and string concatenation with f-strings.'''

    def docs_path_check(self):
        def get_windows_docs_path() -> Path:
            CSIDL_PERSONAL = 5
            SHGFP_TYPE_CURRENT = 0
            user_documents = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, user_documents)
            win_docs = Path(user_documents.value)
            GALAXY.Game_Docs_Found = True
            return win_docs

        def get_linux_docs_path() -> Optional[Path]:
            libraryfolders_path = Path.home().joinpath(".local", "share", "Steam", "steamapps", "common", "libraryfolders.vdf")
            if libraryfolders_path.is_file():
                library_path = Path()
                with libraryfolders_path.open(encoding="utf-8", errors="ignore") as steam_library_raw:
                    steam_library = steam_library_raw.readlines()
                for library_line in steam_library:
                    if "path" in library_line:
                        library_path = Path(library_line.split('"')[3])
                    if str(GALAXY.Game_SID) in library_line:
                        library_path = library_path.joinpath("steamapps")
                        lin_docs = library_path.joinpath("compatdata", str(GALAXY.Game_SID), "pfx", "drive_c", "users", "steamuser", "My Documents", "My Games", GALAXY.Game_Docs)
                        if library_path.joinpath("common", GALAXY.Game_Name).exists() and lin_docs.exists():
                            GALAXY.Game_Docs_Found = True
                            return lin_docs
            return None

        def get_ini_docs_path() -> Optional[Path]:
            if str(GALAXY.Game_Docs).lower() in UNIVERSE.CLAS_config["INI Path"].lower():
                ini_line = UNIVERSE.CLAS_config["INI Path"].strip()
                ini_docs = Path(ini_line)
                return ini_docs
            return None

        def get_manual_docs_path() -> Path:
            print(f"> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR {GALAXY.Game_Docs}.ini IS LOCATED < <")
            path_input = input(f"(EXAMPLE: C:/Users/Zen/Documents/My Games/{GALAXY.Game_Docs} | Press ENTER to confirm.)\n> ")
            print(f"You entered: {path_input} | This path will be automatically added to CLAS Settings.ini")
            manual_docs = Path(path_input.strip())
            clas_toml_update("INI Path", str(path_input))
            return manual_docs

        if platform.system() == "Windows":
            docs_path = get_windows_docs_path()
        else:
            docs_path = get_linux_docs_path()

        if not docs_path:
            docs_path = get_ini_docs_path()

        if not docs_path:
            docs_path = get_manual_docs_path()

        return docs_path

    # =========== CHECK DOCUMENTS -> GAME PATH & XSE LOGS ===========
    # Don't forget to check both OG and VR script extender logs!

    def game_path_check(self):
        def get_game_path_and_flags(logfile):
            XSE_Error = XSE_Version = XSE_Crash_DLL = False
            Game_Path = None
            Error_List = []

            with open(logfile, "r", encoding="utf-8", errors="ignore") as LOG_Check:
                Path_Check = LOG_Check.readlines()

                for logline in Path_Check:
                    if "plugin directory" in logline:
                        logline = logline[19:].replace("\\Data\\F4SE\\Plugins", "")
                        Game_Path = logline.replace("\n", "")
                    if GALAXY.XSEOG_Latest in logline or GALAXY.XSEVR_Latest in logline:
                        XSE_Version = True
                    if UNIVERSE.LOG_Catch_Pattern.search(logline) and all(err not in logline.lower() for err in UNIVERSE.LOG_Errors_Exclude):
                        XSE_Error = True
                        Error_List.append(logline)
                    if GALAXY.CRASHGEN_DLL in logline.lower() and "loaded correctly" in logline.lower():
                        XSE_Crash_DLL = True

            return Game_Path, XSE_Error, XSE_Version, XSE_Crash_DLL, Error_List

        logfile = self.FO4_F4SE_LOG
        if self.FO4_F4SEVR_LOG.is_file():
            logfile = self.FO4_F4SEVR_LOG

        if not self.FO4_F4SE_LOG.is_file() and not self.FO4_F4SEVR_LOG.is_file():
            GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_CLAS_Missing_F4SELOG"])
            os.system("pause")

        Game_Path, XSE_Error, XSE_Version, XSE_Crash_DLL, Error_List = get_game_path_and_flags(logfile)

        if XSE_Version:
            GALAXY.scan_game_report.append(f"✔️ You have the latest version of {GALAXY.XSE_Handle}\n  -----")
        else:
            GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Outdated_F4SE"])

        if XSE_Error:
            GALAXY.scan_game_report.append("# ❌ SCRIPT EXTENDER REPORTS THAT THE FOLLOWING PLUGINS FAILED TO LOAD! #\n")
            for elem in Error_List:
                GALAXY.scan_game_report.append(f"{elem}\n-----")
        else:
            GALAXY.scan_game_report.append("✔️ Script Extender reports that all DLL mod plugins have loaded correctly.\n  -----")

        if XSE_Crash_DLL:
            GALAXY.scan_game_report.append(f"✔️ Script Extender reports that {GALAXY.CRASHGEN_Handle} was found and loaded correctly.\n  -----")
            GALAXY.ADLIB_Loaded = True
        else:
            GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Missing_F4SE_BO4"])

        if not Game_Path:
            raise FileNotFoundError("❌ ERROR: Could not find game path in F4SE log file.")  # This is to appease VSCode's type checker. The extremely remote possibility that it could return None freaks is out.

        return Game_Path


SYSTEM = ClasLocalFiles()
SYSTEM.docs_file_check(SYSTEM.docs_path_check())  # type: ignore


class ClasCheckFiles:
    # ROOT FOLDERS
    SYSTEM.Game_Root = Path(SYSTEM.game_path_check())
    SYSTEM.Game_Data = SYSTEM.Game_Root.joinpath("Data")
    SYSTEM.Game_Scripts = SYSTEM.Game_Root.joinpath("Data", "Scripts")
    # ROOT FILES
    SYSTEM.Game_EXE = SYSTEM.Game_Root.joinpath("Fallout4.exe")
    SYSTEM.CreationKit_EXE = SYSTEM.Game_Root.joinpath("CreationKit.exe")
    SYSTEM.CreationKit_Fixes = SYSTEM.Game_Root.joinpath("Data", "F4CKFixes")
    SYSTEM.Steam_INI = SYSTEM.Game_Root.joinpath("steam_api.ini")
    SYSTEM.Preloader_DLL = SYSTEM.Game_Root.joinpath("IpHlpAPI.dll")
    SYSTEM.Preloader_XML = SYSTEM.Game_Root.joinpath("xSE PluginPreloader.xml")
    # F4SE FILES
    SYSTEM.XSE_DLL = SYSTEM.Game_Root.joinpath("f4se_1_10_163.dll")
    SYSTEM.XSE_SteamDLL = SYSTEM.Game_Root.joinpath("f4se_steam_loader.dll")
    SYSTEM.XSE_Loader = SYSTEM.Game_Root.joinpath("f4se_loader.exe")
    # VR FILES
    SYSTEM.VR_EXE = SYSTEM.Game_Root.joinpath("Fallout4VR.exe")
    SYSTEM.VR_Buffout = SYSTEM.Game_Root.joinpath("Data", "F4SE", "Plugins", "msdia140.dll")
    SYSTEM.XSE_VRDLL = SYSTEM.Game_Root.joinpath("f4sevr_1_2_72.dll")
    SYSTEM.XSE_VRLoader = SYSTEM.Game_Root.joinpath("f4sevr_loader.exe")
    # BUFFOUT FILES
    SYSTEM.Buffout_DLL = SYSTEM.Game_Root.joinpath("Data", "F4SE", "Plugins", "Buffout4.dll")
    SYSTEM.Buffout_TOML = SYSTEM.Game_Root.joinpath("Data", "F4SE", "Plugins", "Buffout4.toml")
    SYSTEM.Address_Library = SYSTEM.Game_Root.joinpath("Data", "F4SE", "Plugins", "version-1-10-163-0.bin")
    SYSTEM.Address_LibraryVR = SYSTEM.Game_Root.joinpath("Data", "F4SE", "Plugins", "version-1-2-72-0.csv")
    # GAME EXE HASH
    if SYSTEM.Game_EXE.is_file():
        SYSTEM.EXE_Local_Hash = hashlib.sha512(SYSTEM.Game_EXE.read_bytes()).hexdigest()  # type: ignore
    elif SYSTEM.VR_EXE.is_file():
        SYSTEM.EXE_Local_Hash = hashlib.sha512(SYSTEM.VR_EXE.read_bytes()).hexdigest()  # type: ignore

    # ============== CHECK GAME PATH -> PROGRAM FILES ==============

    def game_check_folderpath(self):
        game_folderpath = SYSTEM.game_path_check()
        if re.search(r"C:\\Program Files( \(x86\))?", game_folderpath, re.IGNORECASE):
            GALAXY.scan_game_report.extend([f"❌ CAUTION : Your {GALAXY.Game_Name} game files are installed inside of the Program Files folder!",
                                            "   Having the game installed here might cause Windows UAC to block some mods from working properly.",
                                            "   To ensure that everything works, move your Game or entire Steam folder outside of Program Files.",
                                            "  -----"])
        else:
            GALAXY.scan_game_report.append(f"✔️ Your {GALAXY.Game_Name} game files are installed outside of Program Files folder. \n  -----")

    # ===== CHECK DOCUMENTS -> ENABLE ARCH. INV. / LOOSE FILES =====

    def ini_enable_modding(self):
        if SYSTEM.FO4_Custom_INI.is_file():
            try:
                os.chmod(SYSTEM.FO4_Custom_INI, stat.S_IWRITE)
                INI_config = configparser.ConfigParser()
                INI_config.optionxform = str  # type: ignore
                INI_config.read(SYSTEM.FO4_Custom_INI)
                if "Archive" not in INI_config.sections():
                    GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Arch_Inv"])
                    INI_config.add_section("Archive")
                else:
                    GALAXY.scan_game_report.append("✔️ Archive Invalidation / Loose Files setting is already enabled in game INI files.")
                INI_config.set("Archive", "bInvalidateOlderFiles", "1")
                INI_config.set("Archive", "sResourceDataDirsFinal", "")
                with open(SYSTEM.FO4_Custom_INI, "w+", encoding="utf-8", errors="ignore") as INI_custom:
                    INI_config.write(INI_custom, space_around_delimiters=False)
            except (configparser.MissingSectionHeaderError, configparser.ParsingError, OSError):
                GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_CLAS_Broken_F4CINI"])
        else:
            with open(SYSTEM.FO4_Custom_INI, "a", encoding="utf-8", errors="ignore") as INI_custom:
                GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Arch_Inv"])
                INI_config = "[Archive]\nbInvalidateOlderFiles=1\nsResourceDataDirsFinal="
                INI_custom.write(INI_config)

    # ============ CHECK DOCUMENTS -> ERRORS IN ALL LOGS ============
    # Don't forget to check both OG and VR script extender logs!

    '''GPT Change List:
    Separated the error log line filtering into a separate function, get_error_log_lines(), to improve code readability.
    Removed the unnecessary logname variable.
    Used the extend() method instead of looping through list_log_errors to append elements.
    Replaced the if len(list_log_errors) >= 1 with a more Pythonic if list_log_errors:.'''

    def log_check_errors(self, log_path, log_source):
        def get_error_log_lines(filepath):
            with filepath.open("r", encoding="utf-8", errors="ignore") as log_file:
                log_lines = log_file.readlines()

            error_lines = [
                line for line in log_lines
                if UNIVERSE.LOG_Catch_Pattern.search(line) and
                not UNIVERSE.LOG_Files_Exclude_Pattern.search(line)
            ]

            return error_lines

        list_log_errors = []

        for filename in Path(log_path).glob("*.log"):
            if UNIVERSE.LOG_Files_Exclude_Pattern.search(filename.name):
                continue

            try:
                filepath = filename.resolve()
                if filepath.is_file():
                    error_lines = get_error_log_lines(filepath)
                    list_log_errors.extend(
                        f"  LOG PATH > {filepath}\n  ERROR > {line}\n  -----"
                        for line in error_lines
                    )
            except (PermissionError, OSError):
                list_log_errors.append(f"  ❌ CLAS was unable to scan this log file :\n  {filename}")
                continue

        if list_log_errors:
            GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
            GALAXY.scan_game_report.extend(list_log_errors)
        else:
            GALAXY.scan_game_report.append(
                f"  -----\n✔️ Available logs in your {log_source} Folder do not report any additional errors. \n  -----"
            )

    # ========== CHECK GAME FOLDER -> XSE SCRIPTS INTEGRITY =========
    # RESERVED | ADJUST FOR OTHER GAMES

    def xse_check_scripts(self, scripts_path, scripts_list):
        matching_scripts = 0
        try:
            script_files = os.listdir(scripts_path)
            matching_scripts = sum(script_files.count(script) for script in scripts_list)
            GALAXY.scan_game_report.append(f"  * {matching_scripts} / {len(scripts_list)} * F4SE script files were found in your Fallout 4 / Data / Scripts folder. \n  -----")
        except (PermissionError, FileNotFoundError):
            GALAXY.scan_game_report.append("  ❌ CLAS was unable to detect F4SE script files. Check if F4SE is correctly installed! \n  -----")
        return matching_scripts

    def xse_check_hashes(self, scripts_path, hash_list):
        matching_hashes = True
        try:
            for filename in os.listdir(scripts_path):
                if filename in hash_list:
                    # If file is in the dictionary, calculate hash value.
                    file_path = os.path.join(scripts_path, filename)
                    with open(file_path, "rb") as f:
                        file_contents = f.read()
                    # Algo should match the one used for dictionary.
                    file_hash = hashlib.sha256(file_contents).hexdigest()

                    # Compare local hash with dictionary value.
                    if file_hash != hash_list[filename]:
                        matching_hashes = False
                        GALAXY.scan_game_report.append(f"[!] CAUTION : {filename} does not match its original hash!")
        except (PermissionError, FileNotFoundError):
            GALAXY.scan_game_report.append("  ❌ CLAS was unable to detect F4SE script hashes. Check if F4SE is correctly installed! \n  -----")
        return matching_hashes

    # =========== CHECK GAME FOLDER -> GAME EXE INTEGRITY ===========
    # RESERVED | ADJUST FOR OTHER GAMES

    def game_check_integrity(self, exe_filepath):
        if exe_filepath.is_file():
            if SYSTEM.EXE_Local_Hash == GALAXY.Game_HASH["1.10.163"] and not SYSTEM.Steam_INI.is_file():  # type: ignore
                GALAXY.scan_game_report.extend(["✔️ Your Fallout 4 is updated to version [1.10.163.0]",
                                                "    * This is the version BEFORE the 2023 Update * \n"])
            # elif EXE_Local_Hash == GALAXY.Game_HASH["1.xx.xxx.x"] and not SYSTEM.Steam_INI.is_file(): | RESERVED
            #    GALAXY.scan_game_report.extend(["✔️ Your Fallout 4 is updated to version [1.xx.xxx.x]",
            #                                  "   * This is the version AFTER the 2023 Update * \n"])
            elif not SYSTEM.Steam_INI.is_file():
                GALAXY.scan_game_report.append("# ❌ CAUTION : YOUR FALLOUT 4 VERSION IS OUT OF DATE #\n")
            elif SYSTEM.Steam_INI.is_file():  # INTENTIONAL, DO NOT CHANGE THE UNICODE ICON.
                GALAXY.scan_game_report.append("# \U0001F480 CAUTION : YOUR FALLOUT 4 VERSION IS OUT OF DATE #\n")

    # ============ CHECK GAME FOLDER -> GAME EXTENSIONS =============
    # RESERVED | ADJUST FOR OTHER GAMES

    def game_check_extensions(self):
        if str(UNIVERSE.CLAS_config["IMI Mode"]).lower() == "false":
            GALAXY.scan_game_report.extend(["IF YOU ARE USING DYNAMIC PERFORMANCE TUNER AND/OR LOAD ACCELERATOR,",
                                            "remove these mods completely and switch to High FPS Physics Fix!",
                                            "Link: https://www.nexusmods.com/fallout4/mods/44798?tab=files \n"])

            if SYSTEM.VR_EXE.is_file() and SYSTEM.VR_Buffout.is_file():
                GALAXY.scan_game_report.append("*✔️ Buffout 4 VR Version* is (manually) installed.\n  -----")
            elif SYSTEM.VR_EXE.is_file() and not SYSTEM.VR_Buffout.is_file():
                GALAXY.scan_game_report.extend(["# ❌ BUFFOUT 4 FOR VR VERSION ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                                "  This is a mandatory Buffout 4 port for the VR Version of Fallout 4.",
                                                "  Link: https://www.nexusmods.com/fallout4/mods/64880?tab=files",
                                                "  -----"])
            else:
                GALAXY.scan_game_report.append("❌ *Fallout 4 VR* is NOT installed.\n  -----")

            if (SYSTEM.CreationKit_EXE.is_file() and os.path.exists(SYSTEM.CreationKit_Fixes)) or (isinstance(SYSTEM.Game_Path, str) and Path(SYSTEM.Game_Path).joinpath("winhttp.dll").is_file()):  # type: ignore
                GALAXY.scan_game_report.append("✔️ *Creation Kit Fixes* is (manually) installed.\n  -----")
            elif SYSTEM.CreationKit_EXE.is_file() and not os.path.exists(SYSTEM.CreationKit_Fixes):
                GALAXY.scan_game_report.extend(["# ❌ CREATION KIT FIXES ISN'T INSTALLED OR AUTOSCAN CANNOT DETECT IT #",
                                                "  This is a highly recommended patch for the Fallout 4 Creation Kit.",
                                                "  Link: https://www.nexusmods.com/fallout4/mods/51165?tab=files",
                                                "  -----"])
            else:
                GALAXY.scan_game_report.append("❌ *Creation Kit* is NOT installed.\n  -----")

    # ========= CHECK GAME FOLDER -> BUFFOUT 4 REQUIREMENTS =========
    # RESERVED | ADJUST FOR OTHER GAMES

    def bo4_check_required(self):
        if str(UNIVERSE.CLAS_config["IMI Mode"]).lower() == "false":
            if SYSTEM.Preloader_XML.is_file() and SYSTEM.Preloader_DLL.is_file():
                GALAXY.scan_game_report.append(fr"{GALAXY.Warnings['Warn_SCAN_NOTE_Preloader']}")
            else:
                GALAXY.scan_game_report.append('❌ OPTIONAL: *Plugin Preloader* is NOT (manually) installed.\n  -----')

            if (SYSTEM.XSE_VRDLL.is_file() and SYSTEM.XSE_VRLoader.is_file()) or (SYSTEM.XSE_DLL.is_file() and SYSTEM.XSE_Loader.is_file() and SYSTEM.XSE_SteamDLL.is_file()):
                GALAXY.scan_game_report.append("✔️ REQUIRED: *Fallout 4 Script Extender* is (manually) installed.\n  -----")
            else:
                GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Missing_F4SE_CORE"])

            if SYSTEM.Address_Library.is_file() or SYSTEM.Address_LibraryVR.is_file() or GALAXY.ADLIB_Loaded is True:
                GALAXY.scan_game_report.append("✔️ REQUIRED: *Address Library* is (manually) installed.\n  -----")
            else:
                GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Missing_ADLIB"])

    # =========== CHECK GAME FOLDER -> BUFFOUT 4 SETTINGS ===========
    # RESERVED | ADJUST FOR OTHER GAMES

    def check_and_update_config(self, config, section, key, expected_value, warning_msg, report):
        current_value = config[section][key]
        if current_value != expected_value:
            report.extend(warning_msg)
            report.append("-----")
            config[section][key] = expected_value
        else:
            report.append(f"✔️ {key} parameter in *Buffout4.toml* is correctly configured.\n  -----")

    def bo4_check_settings(self):
        if SYSTEM.Buffout_TOML.is_file() and SYSTEM.Buffout_DLL.is_file():
            os.chmod(SYSTEM.Buffout_TOML, stat.S_IWRITE)  # MODIFY TOML WRITE PERMISSIONS
            GALAXY.scan_game_report.append("✔️ REQUIRED: *Buffout 4* is (manually) installed. Checking configuration...\n  -----")

            with open(SYSTEM.Buffout_TOML, "r+", encoding="utf-8", errors="ignore") as BUFF_Custom:
                BUFF_config: tomlkit.TOMLDocument = tomlkit.load(BUFF_Custom)

                if SYSTEM.Buffout_TOML.is_file():
                    self.check_and_update_config(BUFF_config, "Patches", "Achievements", False,
                                                 ["# ❌ WARNING: Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements parameter is set to TRUE #",
                                                  "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4."],
                                                 GALAXY.scan_game_report)

                if SYSTEM.BO4_BakaSH_LOG.is_file():
                    self.check_and_update_config(BUFF_config, "Patches", "MemoryManager", False,
                                                 ["# ❌ WARNING: Baka ScrapHeap is installed, but MemoryManager parameter is set to TRUE #",
                                                  "Auto-Scanner will change this parameter to FALSE to prevent conflicts with Buffout 4."],
                                                 GALAXY.scan_game_report)

                if SYSTEM.BO4_LooksMenu_LOG.is_file():
                    self.check_and_update_config(BUFF_config, "Compatibility", "F4EE", True,
                                                 ["# ❌ WARNING: Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE #",
                                                  "Auto-Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu."],
                                                 GALAXY.scan_game_report)

                if BUFF_config["Patches"]["MaxStdIO"] < 2048:  # type: ignore
                    self.check_and_update_config(BUFF_config, "Patches", "MaxStdIO", 2048,
                                                 ["# ❌ WARNING: MaxStdIO parameter value in *Buffout4.toml* might be too low.",
                                                  "Auto-Scanner will increase this value to 2048 to prevent possible crashes."],
                                                 GALAXY.scan_game_report)
                elif BUFF_config["Patches"]["MaxStdIO"] > 2048:  # type: ignore
                    self.check_and_update_config(BUFF_config, "Patches", "MaxStdIO", 2048,
                                                 ["# ❌ WARNING: MaxStdIO parameter value in *Buffout4.toml* might be too high.",
                                                  "Auto-Scanner will decrease this value to 2048 to prevent possible crashes."],
                                                 GALAXY.scan_game_report)

            with open(SYSTEM.Buffout_TOML, "w+", encoding="utf-8", errors="ignore") as BUFF_Custom:
                tomlkit.dump(BUFF_config, BUFF_Custom)

        else:
            GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Missing_Buffout4"])


PLANET = ClasCheckFiles()


class ClasCheckMods:
    # 1) CHECKING FOR MODS THAT CAN CAUSE FREQUENT CRASHES | Leave 1 empty space as prefix to prevent most duplicates.
    Mods1 = {
        0: {"mod": " DamageThresholdFramework.esm",
            "warn": ["DAMAGE THRESHOLD FRAMEWORK \n",
                     "[Can cause crashes in combat on some occasions due to how damage calculations are done.]"]},

        1: {"mod": " Endless Warfare.esm",
            "warn": ["ENDLESS WARFARE \n",
                     "[Some enemy spawn points could be bugged or crash the game due to scripts or pathfinding.]"]},

        2: {"mod": " EPO.esp",
            "warn": ["EXTREME PARTICLES OVERHAUL \n",
                     "[Can cause particle effects related crashes, consider switching to Burst Impact Blast FX.] \n",
                     "[Burst Impact Blast FX: https://www.nexusmods.com/fallout4/mods/57789?tab=files]"]},

        3: {"mod": " SakhalinWasteland",
            "warn": ["FALLOUT SAKHALIN \n",
                     "[Breaks the precombine system all across Far Harbor which will randomly crash your game.]"]},

        4: {"mod": " 76HUD",
            "warn": ["HUD76 HUD REPLACER \n",
                     "[Can sometimes cause interface and pip-boy related bugs, glitches and crashes.]"]},

        6: {"mod": " NCRenegade",
            "warn": ["NCR RENEGADE ARMOR \n",
                     "[Broken outfit mesh that crashes the game in 3rd person or when NPCs wearing it are hit.]"]},

        7: {"mod": " Respawnable Legendary Bosses",
            "warn": ["RESPAWNABLE LEGENDARY BOSSES \n",
                     "[Can sometimes cause Deathclaw / Behemoth boulder projectile crashes for unknown reasons.]"]},

        8: {"mod": " Scrap Everything - Core",
            "warn": ["SCRAP EVERYTHING (CORE) \n",
                     "[Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order.]"]},

        9: {"mod": " Scrap Everything - Ultimate",
            "warn": ["SCRAP EVERYTHING (ULTIMATE) \n",
                     "[Weird crashes and issues due to multiple unknown problems. This mod must be always last in your load order.]"]},

        10: {"mod": " Shade Girl Leather Outfits",
             "warn": ["SHADE GIRL LEATHER OUTFITS \n",
                      "[Outfits can crash the game while browsing the armor workbench or upon starting a new game due to bad meshes.]"]},

        11: {"mod": " SpringCleaning.esm",
             "warn": ["SPRING CLEANING \n",
                      "[Abandoned and severely outdated mod that breaks precombines and could potentially even break your save file.]"]},

        12: {"mod": " (STO) NO",
             "warn": ["STALKER TEXTURE OVERHAUL \n",
                      "[Doesn't work due to incorrect folder structure and has a corrupted dds file that causes Create2DTexture crashes.]"]},

        13: {"mod": " TacticalTablet.esp",
             "warn": ["TACTICAL TABLET \n",
                      "[Can cause flickering with certain scopes or crashes while browsing workbenches, most commonly with ECO.]"]},

        14: {"mod": " True Nights v03.esp",
             "warn": ["TRUE NIGHTS \n",
                      "[Has an invalid Image Space Adapter (IMAD) Record that will corrupt your save memory and has to be manually fixed.]"]},

        15: {"mod": " WeaponsFramework",
             "warn": ["WEAPONS FRAMEWORK BETA \n",
                      "[Will randomly cause crashes when used with Tactical Reload and possibly other weapon or combat related mods.]\n"
                      "[Visit Important Patches List article for possible solutions: https://www.nexusmods.com/fallout4/articles/3769]"]},

        16: {"mod": " WOTC.esp",
             "warn": ["WAR OF THE COMMONWEALTH \n",
                      "[Seems responsible for consistent crashes with specific spawn points or random ones during settlement attacks.]"]}
    }

    # 2) CHECKING FOR MODS THAT CONFLICT WITH OTHER MODS | Leave 1 empty space as prefix to prevent most duplicates.
    # mod_1 should be less popular mod, mod_2 more popular mod.
    Mods2 = {
        0: {"mod_1": " BetterPowerArmorRedux.dll",
            "mod_2": " FloatingDamage.dll",
            "warn": [" BETTER POWER ARMOR REDUX ❌ CONFLICTS WITH : FLOATING DAMAGE \n",
                     "[Both mods use the same script hooks. This can crash the game or cause weird mod behavior.]\n",
                     "[If you encounter problems, You should use only one of these mods, not both at the same time.]"]},

        1: {"mod_1": " BetterPowerArmorRedux.dll",
            "mod_2": " KnockoutFramework.dll",
            "warn": [" BETTER POWER ARMOR REDUX ❌ CONFLICTS WITH : KNOCKOUT FRAMEWORK \n",
                     "[Both mods use the same script hooks. This can crash the game or cause weird mod behavior.]\n",
                     "[If you encounter problems, You should use only one of these mods, not both at the same time.]"]},

        2: {"mod_1": " BostonFPSFix",
            "mod_2": " PRP.esp",
            "warn": ["BOSTON FPS FIX ❌ CONFLICTS WITH : PREVIS REPAIR PACK \n",
                     "[Using both mods can break precombines. CLAS suggests using Previs Repair Pack only.]"]},

        3: {"mod_1": " ExtendedWeaponSystem.esm",
            "mod_2": " TacticalReload.esm",
            "warn": ["EXTENDED WEAPON SYSTEMS ❌ CONFLICTS WITH : TACTICAL RELOAD \n",
                     "[Using both mods can frequently crash the game. You should use only one of these mods, not both at the same time.]"]},

        4: {"mod_1": " FROST.esp",
            "mod_2": " PRP.esp",
            "warn": ["FROST SURVIVAL SIMULATOR ❌ CONFLICTS WITH : PREVIS REPAIR PACK \n",
                     "[For precombine fixes, remove PRP and switch to FROST Cell Fixes (FCF).]\n",
                     "[FROST Cell Fixes: https://www.nexusmods.com/fallout4/mods/59652?tab=files]"]},

        5: {"mod_1": " DCGuard_Overhaul.esp",
            "mod_2": " Guards.esp",
            "warn": ["THE FENS SHERIFF'S DEPARTMENT ❌ CONFLICTS WITH : VARIED DIAMOND CITY GUARDS \n",
                     "[Both mods heavily modify Diamond City Guards records. You should use only one of these mods, not both at the same time.]"]},

        6: {"mod_1": " Fallout4Upscaler.dll",
            "mod_2": " NVIDIA_Reflex.dll",
            "warn": ["FALLOUT 4 UPSCALER ❌ CONFLICTS WITH : NVIDIA REFLEX SUPPORT \n",
                     "[Both mods likely use the same DLL hooks. This can crash the game or cause weird mod behavior.]\n",
                     "[If you encounter problems or crashes, You should use only one of these mods, not both at the same time.]"]},

        7: {"mod_1": " vulkan",
            "mod_2": " NVIDIA_Reflex.dll",
            "warn": ["VULKAN RENDERER ❌ CONFLICTS WITH : NVIDIA REFLEX SUPPORT \n",
                     "[Vulkan Renderer can break GPU recognition from NV Reflex Support. This can crash the game or cause weird mod behavior.]\n",
                     "[If you encounter Nvidia Driver crashes, CLAS suggests using Vulkan Render only. Otherwise, use Nvidia Reflex Support.]"]},

        8: {"mod_1": " CustomCamera.esp",
            "mod_2": " CameraTweaks.esp",
            "warn": ["CUSTOM CAMERA ❌ CONFLICTS WITH : CAMERA TWEAKS \n",
                     "[Both mods make changes to the in-game camera. CLAS suggests using Camera Tweaks only, since it's an updated alternative.]"]},

        9: {"mod_1": " UniquePlayer.esp",
            "mod_2": " ClassicHolsteredWeapons",
            "warn": ["UNIQUE PLAYER ❌ CONFLICTS WITH : CLASSIC HOLSTERED WEAPONS \n",
                     "[Classic Holstered Weapons will not work correctly with mods that modify the player skeleton or add new skeleton paths.]\n",
                     "[If you encounter problems or crashes, see here how to add additional skeletons: https://www.nexusmods.com/fallout4/articles/2496]"]},

        10: {"mod_1": " HHS.dll",
             "mod_2": " ClassicHolsteredWeapons",
             "warn": ["HIGH HEELS SYSTEM ❌ CONFLICTS WITH : CLASSIC HOLSTERED WEAPONS \n",
                      "[Classic Holstered Weapons will not work correctly with mods that modify the player skeleton or add new skeleton paths.]\n",
                      "[If you encounter problems or crashes, see here how to add additional skeletons: https://www.nexusmods.com/fallout4/articles/2496]"]},

        11: {"mod_1": " cbp.dll",
             "mod_2": " ClassicHolsteredWeapons",
             "warn": ["CBP PHYSICS ❌ CONFLICTS WITH : CLASSIC HOLSTERED WEAPONS \n",
                      "[Classic Holstered Weapons will not work correctly with mods that modify the player skeleton or add new skeleton paths.]\n",
                      "[If you encounter problems or crashes, see here how to add additional skeletons: https://www.nexusmods.com/fallout4/articles/2496]"]},

        12: {"mod_1": " ArmorKeywords.esm",
             "mod_2": " SKKCraftableWeaponsAmmo.esp",
             "warn": ["ARMOR AND WEAPON KEYWORDS ❌ CONFLICTS WITH : SKK CRAFT WEAPONS AND SCRAP AMMO \n",
                      "[SKK Craft Weapons & Ammo Version 008 is incompatible with AWKCR and will cause crashes while saving the game.]\n",
                      "[If you encounter problems or crashes, remove AWKCR and / or switch to Equipment and Crafting Overhaul instead.]"]},

    }

    # 3) CHECKING FOR MODS WITH SOLUTIONS & COMMUNITY PATCHES | Leave 1 empty space as prefix to prevent most duplicates.
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
                     "- This mod needs a compatibility patch to forward changes made by the Unofficial Patch. \n",
                     "  Patch Link: https://drive.google.com/file/d/1JJvrnaxmui22P1X44V2VTkifjmfahtLM \n",
                     "  [If you have Horizon installed or don't use UFO4P, this patch is not needed.]"]},

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
                     "- This mod is severely outdated. Either install the PRP patch or switch to PRP entirely. \n",
                     "  Patch Link: https://www.nexusmods.com/fallout4/mods/59021?tab=files \n",
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

        16: {"mod": " LegendaryModification.esp",
             "warn": ["LEGENDARY MODIFICATION \n",
                      "- Old mod plagued with all kinds of bugs and crashes, can conflict with some modded weapons. \n",
                      "  Better Alternative: https://www.nexusmods.com/fallout4/mods/67679?tab=files"]},

        17: {"mod": " LooksMenu Customization Compendium.esp",
             "warn": ["LOOKS MENU CUSTOMIZATION COMPENDIUM \n",
                      "- If you are getting broken hair colors, install this mod and make sure it loads after LMCC. \n",
                      "  Mod Link: https://www.nexusmods.com/fallout4/mods/18287?tab=files"]},

        18: {"mod": " MilitarizedMinutemen.esp",
             "warn": ["MILITARIZED MINUTEMEN \n"
                      "- Can occasionally crash the game due to a broken mesh on some minutemen outfits. \n"
                      "  Patch Link: https://www.nexusmods.com/fallout4/mods/32369?tab=files"]},

        19: {"mod": " MoreUniques",
             "warn": ["MORE UNIQUE WEAPONS EXPANSION \n",
                      "- Causes crashes due to broken precombines and compatibility issues with other weapon mods. \n",
                      "  Patch Link: https://www.nexusmods.com/fallout4/mods/54848?tab=files"]},

        20: {"mod": " NAC.es",
             "warn": ["NATURAL AND ATMOSPHERIC COMMONWEALTH \n",
                      "- If you notice weird looking skin tones with either NAC or NACX, install this patch. \n",
                      "  Patch Link: https://www.nexusmods.com/fallout4/mods/57052?tab=files"]},

        21: {"mod": " Northland Diggers New.esp",
             "warn": ["NORTHLAND DIGGERS RESOURCES \n",
                      "- Contains various bugs and issues that can cause crashes or negatively affect other mods. \n",
                      "  Fix Link: https://www.nexusmods.com/fallout4/mods/53395?tab=files"]},

        22: {"mod": " Project Zeta.esp",
             "warn": ["PROJECT ZETA \n",
                      "- Invasion quests seem overly buggy or trigger too frequently, minor sound issues. \n",
                      "  Fix Link: https://www.nexusmods.com/fallout4/mods/65166?tab=files"]},

        23: {"mod": " RaiderOverhaul.esp",
             "warn": ["RAIDER OVERHAUL \n",
                      "- Old mod that requires several patches to function as intended. Use ONE Version instead. \n",
                      "  Updated ONE Version: https://www.nexusmods.com/fallout4/mods/51658?tab=files"]},

        24: {"mod": " Rusty Face Fix",
             "warn": ["RUSTY FACE FIX \n",
                      "- Make sure you have the latest 2.0 version installed or try the REDUX Version instead. \n",
                      "  Original Rusty Face Fix: https://www.nexusmods.com/fallout4/mods/31028?tab=files \n",
                      "  Alternative REDUX Version: https://www.nexusmods.com/fallout4/mods/64270?tab=files"]},

        25: {"mod": " SOTS.esp",
             "warn": ["SOUTH OF THE SEA \n",
                      "- Very unstable mod that consistently and frequently causes strange problems and crashes. \n",
                      "  Updated Version: https://www.nexusmods.com/fallout4/mods/63152?tab=files"]},

        26: {"mod": " StartMeUp.esp",
             "warn": ["START ME UP \n",
                      "- Abandoned mod that can cause infinite loading and other problems. Switch to REDUX Version instead. \n",
                      "  Updated REDUX Version: https://www.nexusmods.com/fallout4/mods/56984?tab=files"]},

        27: {"mod": " SuperMutantRedux.esp",
             "warn": ["SUPER MUTANT REDUX \n",
                      "- Causes crashes at specific locations or with certain Super Mutant enemies and items. \n",
                      "  Patch Link: https://www.nexusmods.com/fallout4/mods/51353?tab=files"]},

        28: {"mod": " TacticalReload.esm",
             "warn": ["TACTICAL RELOAD \n",
                      "- Can cause weapon and combat related crashes. TR Expansion For ECO is highly recommended. \n",
                      "  TR Expansion For ECO Link: https://www.nexusmods.com/fallout4/mods/67716?tab=files"]},

        29: {"mod": " Creatures and Monsters.esp",
             "warn": ["UNIQUE NPCs CREATURES AND MONSTERS \n",
                      "- Causes crashes and breaks precombines at specific locations, some creature spawns are too frequent. \n",
                      "  Patch Link: https://www.nexusmods.com/fallout4/mods/48637?tab=files"]},

    }

    # 4) CHECKING FOR MODS PATCHED THROUGH OPC INSTALLER | Leave 1 empty space as prefix to prevent most duplicates.
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
        19: {"mod": " atlanticofficesf23",
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


MOON = ClasCheckMods()
