import os
from CLAS_Database import GALAXY, SYSTEM, PLANET, clas_ini_create
from bs4 import BeautifulSoup  # For parsing HTML / XML (Wrye Plugin Check)

clas_ini_create()

def scan_game_files():
    GALAXY.scan_game_report = []
    PLANET.ini_enable_modding(SYSTEM.FO4_Custom_INI)

    # ============ CHECK DOCUMENTS -> ERRORS IN ALL LOGS ============

    if len(PLANET.se_check_errors(SYSTEM.FO4_F4SE_Path)) >= 1:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
        for elem in PLANET.se_check_errors(SYSTEM.FO4_F4SE_Path):
            GALAXY.scan_game_report.append(elem)
    elif len(PLANET.se_check_errors(SYSTEM.FO4_F4SEVR_Path)) >= 1:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
        for elem in PLANET.se_check_errors(SYSTEM.FO4_F4SEVR_Path):
            GALAXY.scan_game_report.append(elem)
    else:
        GALAXY.scan_game_report.append("-----\n✔️ Available logs in your Documents Folder do not report any errors, all is well.\n  -----")

    # =========== CHECK GAME FOLDER -> ERRORS IN ALL LOGS ===========

    if len(PLANET.se_check_errors(SYSTEM.Game_Path)) >= 1:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_Log_Errors"])
        for elem in PLANET.se_check_errors(SYSTEM.Game_Path):
            GALAXY.scan_game_report.append(f"{elem}\n-----\n")
    else:
        GALAXY.scan_game_report.append("✔️ Available logs in your Game Folder do not report any additional errors.\n  -----")

    # ========== CHECK GAME FOLDER -> XSE SCRIPTS INEGRITY ==========

    if PLANET.f4se_check_scripts(SYSTEM.Game_Scripts, GALAXY.XSE_Scripts_List) >= GALAXY.XSE_Scripts_Count:
        GALAXY.scan_game_report.extend(["✔️ All F4SE script files are accounted for in your Fallout 4 / Data / Scripts folder.",
                                   "  -----"])
    else:
        GALAXY.scan_game_report.extend(["# ❌ CAUTION : SOME F4SE SCRIPT FILES ARE MISSING #",
                                   "  YOU NEED TO REINSTALL FALLOUT 4 SCRIPT EXTENDER",
                                   "  F4SE LINK: https://f4se.silverlock.org \n"])

    PLANET.fo4_check_integrity(SYSTEM.FO4_EXE)
    PLANET.fo4_check_extensions()
    PLANET.bo4_check_required()
    PLANET.bo4_check_settings()
    return GALAXY.scan_game_report

def scan_wbcheck():  # Wrye Plugin Checker
    scan_wbcheck_report = []
    if SYSTEM.WB_Plugin_Check.is_file():
        scan_wbcheck_report.append("✔️ WRYE BASH PLUGIN CHECKER REPORT FOUND! ANALYZING CONTENTS...")
        with open(SYSTEM.WB_Plugin_Check, "r", encoding="utf-8", errors="ignore") as WB_Check:
            soup = BeautifulSoup(WB_Check, "html.parser")
            wb_text = soup.get_text()
            scan_wbcheck_report.append(wb_text)
            # Find all h1 tags and print their text
            # for h1 in soup.find_all("h1"):
            #    scan_wbcheck_report.append(h1.text)

    return scan_wbcheck_report


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    scan_game_report = scan_game_files()
    for item in scan_game_report:
        print(item)
    for line in scan_wbcheck():
        print(line)
    os.system("pause")
