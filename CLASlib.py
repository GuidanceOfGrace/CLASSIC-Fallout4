import configparser
import os
from dataclasses import dataclass, field
from io import TextIOWrapper
from typing import Iterable
from pathlib import Path
from Scan_Crashlogs import CLAS_Globals

# =================== DEFINE LOCAL FILES ===================


@dataclass
class Info:
    # FO4 GAME FILES
    Address_Library: Path = field(default_factory=Path)
    Address_LibraryVR: Path = field(default_factory=Path)
    Buffout_DLL: Path = field(default_factory=Path)
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
        self.FO4_F4SEVR_Logs = str(docs_location.joinpath("My Games", "Fallout4VR", "F4SE"))
        self.FO4_F4SEVR_Path = docs_location.joinpath("My Games", "Fallout4VR", "F4SE", "f4sevr.log")
        self.FO4_Custom_Path = docs_location.joinpath("My Games", "Fallout4", "Fallout4Custom.ini")

@dataclass
class CLASGlobal:
    CLAS_Updated: bool = field(default=False)
    CLAS_Current: str = field(default_factory=str)
    CLAS_Date: str = field(default_factory=str)
    CLAS_Config: configparser.ConfigParser = field(default_factory=configparser.ConfigParser)
    Warnings: dict[str, str] = field(default_factory=dict)
    Culprit_Trap: bool = field(default=False)
    crash_template_stats: dict[str, int] = field(default_factory=dict)
    Sneaky_Tips: list = field(default_factory=list)
    info: Info = field(default_factory=Info)

    def __post_init__(self):
        self.info = Info()
        # FILES TO LOOK FOR IN GAME FOLDER ONLY
        Game_Path = Path(rf"{self.info.Game_Path}")
        self.info.Game_Scripts = Game_Path.joinpath("Data", "Scripts")
        # ROOT FILES
        self.info.FO4_EXE = Game_Path.joinpath("Fallout4.exe")
        self.info.F4CK_EXE = Game_Path.joinpath("CreationKit.exe")
        self.info.F4CK_Fixes = Game_Path.joinpath("Data", "F4CKFixes")
        self.info.Steam_INI = Game_Path.joinpath("steam_api.ini")
        self.info.Preloader_DLL = Game_Path.joinpath("IpHlpAPI.dll")
        self.info.Preloader_XML = Game_Path.joinpath("xSE PluginPreloader.xml")
        # F4SE FILES
        self.info.F4SE_DLL = Game_Path.joinpath("f4se_1_10_163.dll")
        self.info.F4SE_SDLL = Game_Path.joinpath("f4se_steam_loader.dll")
        self.info.F4SE_Loader = Game_Path.joinpath("f4se_loader.exe")
        # VR FILES
        self.info.VR_EXE = Game_Path.joinpath("Fallout4VR.exe")
        self.info.VR_Buffout = Game_Path.joinpath("Data", "F4SE", "Plugins", "msdia140.dll")
        self.info.F4SE_VRDLL = Game_Path.joinpath("f4sevr_1_2_72.dll")
        self.info.F4SE_VRLoader = Game_Path.joinpath("f4sevr_loader.exe")
        # BUFFOUT FILES
        self.info.Buffout_DLL = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.dll")
        self.info.Buffout_TOML = Game_Path.joinpath("Data", "F4SE", "Plugins", "Buffout4.toml")
        self.info.Address_Library = Game_Path.joinpath("Data", "F4SE", "Plugins", "version-1-10-163-0.bin")
        self.info.Address_LibraryVR = Game_Path.joinpath("Data", "F4SE", "Plugins", "version-1-2-72-0.csv")
        # FALLLOUT 4 HASHES
        self.info.FO4_Hash = {"1.10.163": "77fd1be89a959aba78cf41c27f80e8c76e0e42271ccf7784efd9aa6c108c082d83c0b54b89805ec483500212db8dd18538dafcbf75e55fe259abf20d49f10e60"}

        self.CLAS_config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="$")
        self.CLAS_config.optionxform = str  # type: ignore
        self.CLAS_config.read("Scan Crashlogs.ini")

    def clas_ini_check(self, section: str, value: str):
        if isinstance(section, str) and isinstance(value, str):
            return self.CLAS_config[section][value]
        else:
            return self.CLAS_config[str(section)][str(value)]

    def clas_ini_update(self, section: str, value: str):  # Convenience function for a code snippet that's repeated many times throughout both scripts.
        if isinstance(section, str) and isinstance(value, str):
            self.CLAS_Config["MAIN"][section] = value
        else:
            self.CLAS_Config["MAIN"][str(section)] = str(value)

        with open("Scan Crashlogs.ini", "w+", encoding="utf-8", errors="ignore") as INI_AUTOSCAN:
            self.CLAS_Config.write(INI_AUTOSCAN)


class CLAS(CLASGlobal):
    def __init__(self, text: str, lines: list, filehandle: TextIOWrapper):
        self.text = text
        self.lines = lines
        self.filehandle = filehandle
        self.buff_error = lines[3].strip()
        self.buff_ver = lines[1].strip()
        self.globals = globals

    @staticmethod
    # =================== CLAS INI FILE ===================
    def clas_ini_create():
        if not os.path.exists("Scan Crashlogs.ini"):  # INI FILE FOR AUTO-SCANNER
            INI_Settings = ["[MAIN]\n",
                            "# This file contains configuration settings for both Scan_Crashlogs.py and Crash Log Auto Scanner.exe \n",
                            "# Set to true if you want Auto-Scanner to check Python modules and if latest CLAS version is installed. \n",
                            "Update Check = true\n\n",
                            "# FCX - File Check eXtended | If Auto-Scanner fails to scan your logs, revert this setting back to false. \n",
                            "# Set to true if you want Auto-Scanner to check if your game files and Buffout 4 are installed correctly. \n",
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

    def write_file(self, input_text: str | Iterable):
        if isinstance(input_text, Iterable) and not isinstance(input_text, str): # string is iterable, but we don't want to write it line by line, so we check for that.
            self.filehandle.writelines(input_text)
        else:
            self.filehandle.write(input_text)
    
    # =============== CRASH / STAT CHECK TEMPLATE ===============
    def crash_template_write(self, crash_prefix, crash_main, crash_suffix, crash_stat):
        if "CULPRIT FOUND" in crash_suffix or "DETECTED" in crash_suffix:
            self.globals.Culprit_Trap = True

        self.filehandle.write(f"{crash_prefix}{crash_main}{crash_suffix}")

        if crash_stat in self.globals.crash_template_stats.keys():
            self.globals.crash_template_stats[crash_stat] += 1
        else:
            self.globals.crash_template_stats[crash_stat] = 0
        return self.globals.crash_template_stats[crash_stat]
    
    @staticmethod
    def crash_template_read(crash_prefix, crash_main, crash_suffix, crash_stat):
        if "Logs with" in crash_prefix:  # FOR STAT LOGGING
            print(f"{crash_prefix}{crash_main}{crash_suffix}", end='')
        return CLAS_Globals.crash_template_stats[crash_stat]