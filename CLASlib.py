import configparser
import os
from dataclasses import dataclass, field
from io import TextIOWrapper
from typing import Iterable
from pathlib import Path

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
    Game_Path: Path = field(default_factory=Path)


    def clas_ini_update(self, section: str, value: str):  # Convenience function for a code snippet that's repeated many times throughout both scripts.
        if isinstance(section, str) and isinstance(value, str):
            self.CLAS_Config["MAIN"][section] = value
        else:
            self.CLAS_Config["MAIN"][str(section)] = str(value)

        with open("Scan Crashlogs.ini", "w+", encoding="utf-8", errors="ignore") as INI_AUTOSCAN:
            self.CLAS_Config.write(INI_AUTOSCAN)

CLAS_Globals = CLASGlobal()
CLAS_Globals.CLAS_Config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="$")
CLAS_Globals.CLAS_Config.optionxform = str  # type: ignore
CLAS_Globals.CLAS_Config.read("Scan Crashlogs.ini")

class CLAS:
    def __init__(self, text: str, lines: list, filehandle: TextIOWrapper):
        self.text: str = text
        self.lines: list = lines
        self.filehandle: TextIOWrapper = filehandle
        self.buff_error: str = lines[3].strip()
        self.buff_ver: str = lines[1].strip()

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
        if isinstance(input_text, Iterable) and not isinstance(input_text, str): # string is considered iterable by the typing module.
            self.filehandle.writelines(input_text)
        else:
            self.filehandle.write(input_text)
    
    # =============== CRASH / STAT CHECK TEMPLATE ===============
    def crash_template_write(self, crash_prefix, crash_main, crash_suffix, crash_stat):
        if "CULPRIT FOUND" in crash_suffix or "DETECTED" in crash_suffix:
            CLAS_Globals.Culprit_Trap = True

        self.filehandle.write(f"{crash_prefix}{crash_main}{crash_suffix}")
        try:
            if crash_stat in CLAS_Globals.crash_template_stats.keys():
                CLAS_Globals.crash_template_stats[crash_stat] += 1
            else:
                CLAS_Globals.crash_template_stats[crash_stat] = 0
        except KeyError:
            CLAS_Globals.crash_template_stats = {**CLAS_Globals.crash_template_stats, crash_stat: 0}
        return CLAS_Globals.crash_template_stats[crash_stat]
