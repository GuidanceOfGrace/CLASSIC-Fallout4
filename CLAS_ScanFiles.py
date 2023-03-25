import os
from CLAS_Database import GALAXY, SYSTEM, PLANET, clas_ini_create
from bs4 import BeautifulSoup  # For parsing HTML / XML (Wrye Plugin Check)

clas_ini_create()
GALAXY.scan_game_report = []


def scan_game_files():
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
        GALAXY.scan_game_report.append("  -----\n✔️ Available logs in your Documents Folder do not report any errors, all is well.\n  -----")

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

    PLANET.fo4_check_integrity(SYSTEM.Game_EXE)
    PLANET.fo4_check_extensions()
    PLANET.bo4_check_required()
    PLANET.bo4_check_settings()


def scan_wryecheck():  # Wrye Plugin Checker
    if SYSTEM.WB_Plugin_Check.is_file():
        GALAXY.scan_game_report.extend(["✔️ WRYE BASH PLUGIN CHECKER REPORT WAS FOUND! ANALYZING CONTENTS...",
                                        "  [This report is located in your Documents/My Games/Fallout4 folder.]",
                                        "  [To hide this report, remove *ModChecker.html* from the same folder.]"])
        with open(SYSTEM.WB_Plugin_Check, "r", encoding="utf-8", errors="ignore") as WB_Check:
            WB_HTML = WB_Check.read()

        # Parse the HTML code using BeautifulSoup.
        soup = BeautifulSoup(WB_HTML, 'html.parser')

        for h3 in soup.find_all('h3'):  # Find all <h3> elems and loop through them.
            title = h3.get_text()  # Get title of current <h3> and create plugin list.
            plugin_list = []

            for p in h3.find_next_siblings('p'):  # Find all <p> elements that come after current <h3> element.
                if p.find_previous_sibling('h3') == h3:  # Check if current <p> elem is under same <h3> elem as previous <p>.
                    text = p.get_text().strip().replace("•\xa0 ", "")
                    if '.esp' in text or ".esl" in text or ".esm" in text:  # Get text of <p> elem and check plugin extensions.
                        plugin_list.append(text)
                else:  # If current <p> elem is under a different <h3> elem, break loop.
                    break
            # Format title and list of plugins.
            if len(title) < 32:
                diff = 32 - len(title)
                left = diff // 2
                right = diff - left
                GALAXY.scan_game_report.append("\n   " + "=" * left + f" {title} " + "=" * right + "\n")
            else:
                GALAXY.scan_game_report.append(title)

            if title == "ESL Capable":
                esl_count = sum(1 for _ in plugin_list)
                GALAXY.scan_game_report.extend([f"    ❓ There are {esl_count} plugins that can be given the ESL flag. This can be done",
                                                "        with SimpleESLify script to avoid reaching the plugin limit (254 esm/esp)."])

            for problem_name, problem_desc in GALAXY.WB_Problems.items():
                if problem_name == title:
                    GALAXY.scan_game_report.append(problem_desc)
                elif problem_name in title:
                    GALAXY.scan_game_report.append(problem_desc)

            if title != "ESL Capable":
                for elem in plugin_list:
                    GALAXY.scan_game_report.append(f"   > {elem}")

        GALAXY.scan_game_report.extend(["\n  ❔ For more info about the above detected problems, read the WB Advanced Readme",
                                        "     For more details about solutions, read the Advanced Troubleshooting Article",
                                        "     Advanced Troubleshooting: https://www.nexusmods.com/fallout4/articles/4141",
                                        "     WB Advanced Readme: https://wrye-bash.github.io/docs/ \n"])
    else:
        GALAXY.scan_game_report.append(GALAXY.Warnings["Warn_SCAN_NOTE_WryeCheck"])


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    scan_game_files()
    scan_wryecheck()
    for item in GALAXY.scan_game_report:
        print(item)
    os.system("pause")
