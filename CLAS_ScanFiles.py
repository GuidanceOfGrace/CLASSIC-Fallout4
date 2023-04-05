import os
from typing import List

from bs4 import BeautifulSoup  # For parsing HTML / XML (Wrye Plugin Check)

from CLAS_Database import (GALAXY, PLANET, SYSTEM, clas_ini_create,
                           mods_ini_config)

clas_ini_create()
GALAXY.scan_game_report = []


def scan_game_files():
    PLANET.game_check_folderpath()
    PLANET.ini_enable_modding()

    # ============ CHECK DOCUMENTS -> ERRORS IN ALL LOGS ============

    if len(PLANET.xse_check_errors(SYSTEM.FO4_F4SE_Path)) >= 1:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
        for elem in PLANET.xse_check_errors(SYSTEM.FO4_F4SE_Path):
            GALAXY.scan_game_report.append(elem)

    elif len(PLANET.xse_check_errors(SYSTEM.FO4_F4SEVR_Path)) >= 1:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
        for elem in PLANET.xse_check_errors(SYSTEM.FO4_F4SEVR_Path):
            GALAXY.scan_game_report.append(elem)

    else:
        GALAXY.scan_game_report.append("  -----\n✔️ Available logs in your Documents Folder do not report any errors, all is well.\n  -----")

    # =========== CHECK GAME FOLDER -> ERRORS IN ALL LOGS ===========

    if len(PLANET.xse_check_errors(SYSTEM.Game_Path)) >= 1:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
        for elem in PLANET.xse_check_errors(SYSTEM.Game_Path):
            GALAXY.scan_game_report.append(f"{elem}\n-----\n")
    else:
        GALAXY.scan_game_report.append(f"✔️ Available logs in your {GALAXY.Game_Name} Game Folder do not report any additional errors.\n  -----")

    # ========== CHECK GAME FOLDER -> XSE SCRIPTS INEGRITY ==========

    if PLANET.xse_check_scripts(SYSTEM.Game_Scripts, GALAXY.XSE_Scripts_List) >= GALAXY.XSE_Scripts_Count:
        GALAXY.scan_game_report.append("✔️ All F4SE script files are accounted for in your Fallout 4 / Data / Scripts folder.\n  -----")
    else:
        GALAXY.scan_game_report.extend(["# ❌ CAUTION : SOME F4SE SCRIPT FILES ARE LIKELY MISSING #",
                                        "  YOU SHOULD REINSTALL FALLOUT 4 SCRIPT EXTENDER",
                                        "  F4SE LINK: https://f4se.silverlock.org \n"])

    if PLANET.xse_check_hashes(SYSTEM.Game_Scripts, GALAXY.Game_HASH):
        GALAXY.scan_game_report.append("✔️ All F4SE script files have correct hashes (scripts not modified or corrupted).\n  -----")
    else:
        GALAXY.scan_game_report.extend(["  ❌ CAUTION : THESE SCRIPT EXTENDER FILES ARE EITHER CORRUPTED OR MODIFIED BY OTHER MODS",
                                        "     THIS CAN NEGATIVELY AFFECT SCRIPT EXTENDER AND CRASH THE GAME, SO EITHER REINSTALL F4SE",
                                        "     OR REMOVE MATCHING SCRIPT FILES FROM MODS THAT INCORRECTLY OVERRIDE ORIGINAL F4SE SCRIPTS \n"])

    PLANET.game_check_integrity(SYSTEM.Game_EXE)
    PLANET.game_check_extensions()
    PLANET.bo4_check_required()
    PLANET.bo4_check_settings()


def parse_wb_html(wb_html: str) -> List[str]:
    soup = BeautifulSoup(wb_html, 'html.parser')
    report = []

    for h3 in soup.find_all('h3'):
        title = h3.get_text()
        plugin_list = []

        for p in h3.find_next_siblings('p'):
            if p.find_previous_sibling('h3') == h3:
                text = p.get_text().strip().replace("•\xa0 ", "")
                if '.esp' in text or ".esl" in text or ".esm" in text:
                    plugin_list.append(text)
            else:
                break

        report.append((title, plugin_list))

    return report


def format_report(parsed_report: List[str]) -> List[str]:
    formatted_report = []

    for title, plugin_list in parsed_report:
        if len(title) < 32:
            diff = 32 - len(title)
            left = diff // 2
            right = diff - left
            formatted_report.append("\n   " + "=" * left + f" {title} " + "=" * right + "\n")
        else:
            formatted_report.append(title)

        if title == "ESL Capable":
            esl_count = sum(1 for _ in plugin_list)
            formatted_report.extend([f"    ❓ There are {esl_count} plugins that can be given the ESL flag. This can be done",
                                     "        with SimpleESLify script to avoid reaching the plugin limit (254 esm/esp)."])

        for problem_name, problem_desc in GALAXY.WB_Problems.items():
            if problem_name == title:
                formatted_report.append(problem_desc)
            elif problem_name in title:
                formatted_report.append(problem_desc)

        if title != "ESL Capable":
            for elem in plugin_list:
                formatted_report.append(f"   > {elem}")

    return formatted_report


def scan_wryecheck():
    if SYSTEM.WB_Plugin_Check.is_file():
        GALAXY.scan_game_report.extend(["✔️ WRYE BASH PLUGIN CHECKER REPORT WAS FOUND! ANALYZING CONTENTS...",
                                        "  [This report is located in your Documents/My Games/Fallout4 folder.]",
                                        "  [To hide this report, remove *ModChecker.html* from the same folder.]"])

        with open(SYSTEM.WB_Plugin_Check, "r", encoding="utf-8", errors="ignore") as WB_Check:
            WB_HTML = WB_Check.read()

        parsed_report = parse_wb_html(WB_HTML)
        formatted_report = format_report(parsed_report)
        GALAXY.scan_game_report.extend(formatted_report)

        GALAXY.scan_game_report.extend(["\n  ❔ For more info about the above detected problems, read the WB Advanced Readme",
                                        "     For more details about solutions, read the Advanced Troubleshooting Article",
                                        "     Advanced Troubleshooting: https://www.nexusmods.com/fallout4/articles/4141",
                                        "     Wrye Bash Advanced Readme Documentation: https://wrye-bash.github.io/docs/ \n"])
    else:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_NOTE_WryeCheck"])


def scan_mod_inis():  # Mod INI files check.
    for root, _, files in os.walk(SYSTEM.Game_Data):
        for file in files:
            ini_path = os.path.join(root, file)
            if file == "ESPExplorer.ini":  # ESP Explorer Maintenance | 42520
                if "; F10" in mods_ini_config(ini_path, "General", "HotKey"):
                    mods_ini_config(ini_path, "General", "HotKey", "0x79")
                    GALAXY.scan_game_report.append(f"Values Corrected In : {file}")

            if file == "EPO.ini":
                if int(mods_ini_config(ini_path, "Particles", "iMaxDesired")) > 5000:
                    mods_ini_config(ini_path, "Particles", "iMaxDesired", "5000")
                    GALAXY.scan_game_report.append(f"Values Corrected In : {file}")

            if file == "HighFPSPhysicsFix.ini":  # High FPS Physics Fix | 44798
                if float(mods_ini_config(ini_path, "Limiter", "LoadingScreenFPS")) < 600.0:
                    mods_ini_config(ini_path, "Limiter", "LoadingScreenFPS", "600.0")
                    GALAXY.scan_game_report.append(f"Values Corrected In : {file}")


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    scan_game_files()
    scan_wryecheck()
    scan_mod_inis()
    for item in GALAXY.scan_game_report:
        print(item)
    os.system("pause")
