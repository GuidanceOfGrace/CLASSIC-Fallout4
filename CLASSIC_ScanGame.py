import os
import struct
import shutil
import logging
import tomlkit
import subprocess
import configparser
import CLASSIC_Main as CMain
from functools import lru_cache
from bs4 import BeautifulSoup
from pathlib import Path

CMain.configure_logging()


# ================================================
# DEFINE MAIN FILE / YAML FUNCTIONS
# ================================================
def mod_ini_config(ini_path, section, key, new_value=None):
    try:
        mod_config = configparser.ConfigParser()
        mod_config.optionxform = str
        mod_config.read(ini_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"ERROR: File '{ini_path}' not found")

    if section not in mod_config:
        raise configparser.Error(f"ERROR : Section '{section}' does not exist in '{ini_path}'")
    if key not in mod_config[section]:
        raise configparser.Error(f"ERROR : Key '{key}' does not exist in section '{section}'")

    # If new_value is specified, update value in INI.
    if new_value is not None:
        mod_config.set(section, key, str(new_value))
        with open(ini_path, 'w') as config_file:
            mod_config.write(config_file)
        return new_value

    value = mod_config[section][key].lower()
    if value in ("1", "true"):
        return True
    elif value in ("0", "false"):
        return False

    return mod_config[section][key]


def mod_toml_config(toml_path, section, key, new_value=None):
    # Read the TOML file
    with open(toml_path, 'r') as toml_file:
        data = tomlkit.parse(toml_file.read())

    if section in data:
        if key in data[section]:
            current_value = data[section][key]

            # If a new value is provided, update the key
            if new_value is not None:
                data[section][key] = new_value
                with open(toml_path, 'w') as toml_file:
                    toml_file.write(data.as_string())

            return current_value
        else:
            return None  # Key not found in the section.
    else:
        return None  # Section not found in the TOML.


# ================================================
# CHECK BUFFOUT CONFIG SETTINGS
# ================================================
def check_crashgen_settings():
    CMain.vrmode_check()
    message_list = []
    crashgen_toml_path = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Game_File_BuffoutTOML")
    crashgen_logname = CMain.yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", f"Game{CMain.vr}_Info", "CRASHGEN_LogName")
    xse_folder = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Docs_Folder_XSE")
    if Path(crashgen_toml_path).exists():
        if mod_toml_config(crashgen_toml_path, "Patches", "Achievements") and any("achievements" in file.lower() for file in xse_folder):
            message_list.extend(["# ❌ CAUTION : The Achievements Mod and/or Unlimited Survival Mode is installed, but Achievements is set to TRUE # \n",
                                 f"    Auto Scanner will change this parameter to FALSE to prevent conflicts with {crashgen_logname}. \n-----\n"])
            mod_toml_config(crashgen_toml_path, "Patches", "Achievements", "False")
        else:
            message_list.append(f"✔️ Achievements parameter is correctly configured in your {crashgen_logname} settings! \n-----\n")

        if mod_toml_config(crashgen_toml_path, "Patches", "MemoryManager") and any("bakascrapheap" in file.lower() for file in xse_folder):
            message_list.extend(["# ❌ CAUTION : The Baka ScrapHeap Mod is installed, but MemoryManager parameter is set to TRUE # \n",
                                 f"    Auto Scanner will change this parameter to FALSE to prevent conflicts with {crashgen_logname}. \n-----\n"])
            mod_toml_config(crashgen_toml_path, "Patches", "MemoryManager", "False")
        else:
            message_list.append(f"✔️ Memory Manager parameter is correctly configured in your {crashgen_logname} settings! \n-----\n")

        if mod_toml_config(crashgen_toml_path, "Compatibility", "F4EE") and any("f4ee" in file.lower() for file in xse_folder):
            message_list.extend(["# ❌ CAUTION : Looks Menu is installed, but F4EE parameter under [Compatibility] is set to FALSE # \n",
                                 f"    Auto Scanner will change this parameter to TRUE to prevent bugs and crashes from Looks Menu. \n-----\n"])
            mod_toml_config(crashgen_toml_path, "Compatibility", "F4EE", "True")
        else:
            message_list.append(f"✔️ F4EE (Looks Menu) parameter is correctly configured in your {crashgen_logname} settings! \n-----\n")
    else:
        message_list.extend([f"# [!] NOTICE : Unable to find the {crashgen_logname} config file, settings check will be skipped. # \n",
                             f"  To ensure this check doesn't get skipped, {crashgen_logname} has to be installed manually. \n",
                             "  [ If you are using Mod Organizer 2, you need to run CLASSIC through a shortcut in MO2. ] \n-----\n"])

    message_output = "".join(message_list)
    return message_output


# ================================================
# CHECK ERRORS IN LOG FILES FOR GIVEN FOLDER
# ================================================
def check_log_errors(folder_path):
    message_list = []
    errors_list = []
    catch_errors = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "catch_log_errors")
    ignore_logs_list = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "exclude_log_files")
    ignore_logs_errors = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "exclude_log_errors")

    valid_log_files = [file for file in Path(folder_path).glob("*.log") if "crash-" not in file.name]
    for file in valid_log_files:
        if all(part.lower() not in str(file).lower() for part in ignore_logs_list):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as log_file:
                    log_data = log_file.readlines()
                for line in log_data:
                    if any(item.lower() in line.lower() for item in catch_errors):
                        if all(elem.lower() not in line.lower() for elem in ignore_logs_errors):
                            errors_list.append(f"ERROR > {line}")

                if errors_list:
                    message_list.extend(["[!] CAUTION : THE FOLLOWING LOG FILE REPORTS ONE OR MORE ERRORS! \n",
                                         "[ Errors do not necessarily mean that the mod is not working. ] \n",
                                         f"\nLOG PATH > {file} \n"])
                    for elem in errors_list:
                        message_list.append(elem)

                    message_list.append(f"\n* TOTAL NUMBER OF DETECTED LOG ERRORS * : {len(errors_list)} \n")

            except (PermissionError, OSError):
                message_list.append(f"❌ ERROR : Unable to scan this log file :\n  {file}")
                logging.warning(f"> ! > DETECT LOG ERRORS > UNABLE TO SCAN : {file}")
                continue

    message_output = "".join(message_list)
    return message_output


# ================================================
# CHECK XSE PLUGINS FOLDER IN GAME DATA
# ================================================
def check_xse_plugins():  # RESERVED | Might be expanded upon in the future.
    CMain.vrmode_check()
    message_list = []
    plugins_folder = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Game_Folder_Plugins")
    adlib_versions = {"VR Mode": ("version-1-2-72-0.csv", "Virtual Reality (VR) version", "https://www.nexusmods.com/fallout4/mods/64879?tab=files"),
                      "Non-VR Mode": ("version-1-10-163-0.bin", "Non-VR (Regular) version", "https://www.nexusmods.com/fallout4/mods/47327?tab=files"),
                      }
    enabled_mode = "VR Mode" if CMain.classic_settings("VR Mode") else "Non-VR Mode"
    selected_version = adlib_versions[enabled_mode]
    other_version = adlib_versions["VR Mode" if enabled_mode == "Non-VR Mode" else "Non-VR Mode"]

    if Path(plugins_folder).joinpath(selected_version[0]).exists():
        message_list.append("✔️ You have the latest version of the Address Library file! \n-----\n")
    elif Path(plugins_folder).joinpath(other_version[0]).exists():
        message_list.extend([f"❌ CAUTION : You have installed the wrong version of the Address Library file! \n",
                             f"  Remove the current Address Library file and install the {selected_version[1]}.\n",
                             f"  Link: {selected_version[2]} \n-----\n"])
    else:
        message_list.extend(["❓ NOTICE : Unable to find the Address Library file or your version is outdated! \n",
                             "  Please ensure that Address Libray is installed and that you have the latest version. \n",
                             f"  Link: {selected_version[2]} \n-----\n"])

    message_output = "".join(message_list)
    return message_output


# ================================================
# PAPYRUS MONITORING / LOGGING
# ================================================
def papyrus_logging():
    CMain.vrmode_check()
    message_list = []
    papyrus_path = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Docs_File_PapyrusLog")

    count_dumps = count_stacks = count_warnings = count_errors = 0
    if Path(papyrus_path).exists():
        with open(papyrus_path, "r", encoding="utf-8", errors="ignore") as papyrus_log:
            papyrus_data = papyrus_log.readlines()
        for line in papyrus_data:
            if "Dumping Stacks" in line:
                count_dumps += 1
            elif "Dumping Stack" in line:
                count_stacks += 1
            elif " warning: " in line:
                count_warnings += 1
            elif " error: " in line:
                count_errors += 1

        if count_dumps != 0:
            ratio = count_dumps / count_stacks
        else:
            ratio = 0

        message_list.extend([f"NUMBER OF DUMPS     : {count_dumps} \n",
                             f"NUMBER OF STACKS     : {count_stacks} \n",
                             f"DUMPS/STACKS RATIO : {round(ratio, 3)} \n",
                             f"NUMBER OF WARNINGS : {count_warnings} \n",
                             f"NUMBER OF ERRORS   : {count_errors}"])
    else:
        message_list.extend(["[!] ERROR : UNABLE TO FIND *Papyrus.0.log* (LOGGING IS DISABLED OR YOU DIDN'T RUN THE GAME) \n",
                             "ENABLE PAPYRUS LOGGING MANUALLY OR WITH BETHINI AND START THE GAME TO GENERATE THE LOG FILE \n",
                             "BethINI Link | Standalone Version : https://www.nexusmods.com/fallout4/mods/67?tab=files"])

    message_output = "".join(message_list)
    return message_output, count_dumps


# ================================================
# WRYE BASH - PLUGIN CHECKER
# ================================================
def scan_wryecheck():
    CMain.vrmode_check()
    message_list = []
    wrye_missinghtml = CMain.yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Warnings_MODS", "Warn_WRYE_MissingHTML")
    wrye_plugincheck = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Docs_File_WryeBashPC")
    wrye_warnings = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Wrye_Warn")

    if Path(wrye_plugincheck).is_file():
        message_list.extend(["\n✔️ WRYE BASH PLUGIN CHECKER REPORT WAS FOUND! ANALYZING CONTENTS... \n",
                             "  [This report is located in your Documents/My Games/Fallout4 folder.] \n",
                             "  [To hide this report, remove *ModChecker.html* from the same folder.] \n"])
        with open(wrye_plugincheck, "r", encoding="utf-8", errors="ignore") as WB_Check:
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
            if title != "Active Plugins:" and len(title) < 32:
                diff = 32 - len(title)
                left = diff // 2
                right = diff - left
                message_list.append("\n   " + "=" * left + f" {title} " + "=" * right + "\n")
            elif title != "Active Plugins:":
                message_list.append(title)

            if title == "ESL Capable":
                esl_count = sum(1 for _ in plugin_list)
                message_list.extend([f"❓ There are {esl_count} plugins that can be given the ESL flag. This can be done with \n",
                                     "  the SimpleESLify script to avoid reaching the plugin limit (254 esm/esp). \n",
                                     "  SimpleESLify: https://www.nexusmods.com/skyrimspecialedition/mods/27568 \n  -----\n"])

            for warn_name, warn_desc in wrye_warnings.items():
                if warn_name == title:
                    message_list.append(warn_desc)
                elif warn_name in title:
                    message_list.append(warn_desc)

            if title != "ESL Capable" and title != "Active Plugins:":
                for elem in plugin_list:
                    message_list.append(f"    > {elem} \n")

        message_list.extend(["\n❔ For more info about the above detected problems, see the WB Advanced Readme \n",
                             "  For more details about solutions, read the Advanced Troubleshooting Article \n",
                             "  Advanced Troubleshooting: https://www.nexusmods.com/fallout4/articles/4141 \n",
                             "  Wrye Bash Advanced Readme Documentation: https://wrye-bash.github.io/docs/ \n",
                             "  [ After resolving any problems, run Plugin Checker in Wrye Bash again! ] \n\n"])
    else:
        message_list.append(wrye_missinghtml)

    message_output = "".join(message_list)
    return message_output


# ================================================
# CHECK MOD INI FILES
# ================================================
def scan_mod_inis():  # Mod INI files check.
    CMain.vrmode_check()
    message_list = []
    vsync_list = []
    game_root = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Root_Folder_Game")

    for root, dirs, files in os.walk(game_root):
        for file in files:
            ini_path = os.path.join(root, file)
            if ".ini" in file.lower():
                with open(ini_path, "r", encoding="utf-8", errors="ignore") as ini_file:
                    ini_data = ini_file.read()
                if "sstartingconsolecommand" in ini_data.lower():
                    message_list.extend([f"[!] NOTICE: {ini_path} contains the *sStartingConsoleCommand* setting. \n",
                                         "In rare cases, this setting can slow down the initial game startup time for some players. \n",
                                         "You can test your initial startup time difference by removing this setting from the INI file. \n-----\n"])

            if file.lower() == "dxvk.conf":
                if mod_ini_config(ini_path, "Fallout4.exe", "dxgi.syncInterval") is True:
                    vsync_list.append(f"{ini_path} | SETTING: dxgi.syncInterval \n")

            if file.lower() == "enblocal.ini":
                if mod_ini_config(ini_path, "ENGINE", "ForceVSync") is True:
                    vsync_list.append(f"{ini_path} | SETTING: ForceVSync \n")

            if file.lower() == "espexplorer.ini":  # ESP Explorer Maintenance | 42520
                if "; F10" in mod_ini_config(ini_path, "General", "HotKey"):
                    mod_ini_config(ini_path, "General", "HotKey", "0x79")
                    logging.info(f"> > > PERFORMED INI HOTKEY FIX FOR {file}")
                    message_list.append(f"> Performed INI Hotkey Fix For : {file} \n")

            if file.lower() == "epo.ini":
                if int(mod_ini_config(ini_path, "Particles", "iMaxDesired")) > 5000:
                    mod_ini_config(ini_path, "Particles", "iMaxDesired", "5000")
                    logging.info(f"> > > PERFORMED INI PARTICLE COUNT FIX FOR {file}")
                    message_list.append(f"> Performed INI Particle Count Fix For : {file} \n")

            if file.lower() == "f4ee.ini":  # Looks Menu & LMCC | 12631
                if mod_ini_config(ini_path, "CharGen", "bUnlockHeadParts") == 0:
                    mod_ini_config(ini_path, "CharGen", "bUnlockHeadParts", "1")
                    logging.info(f"> > > PERFORMED INI HEAD PARTS UNLOCK FOR {file}")
                    message_list.append(f"> Performed INI Head Parts Unlock For : {file} \n")

                if mod_ini_config(ini_path, "CharGen", "bUnlockTints") == 0:
                    mod_ini_config(ini_path, "CharGen", "bUnlockTints", "1")
                    logging.info(f"> > > PERFORMED INI FACE TINTS UNLOCK FOR {file}")
                    message_list.append(f"> Performed INI Face Tints Unlock For : {file} \n")

            if file.lower() == "fallout4_test.ini":  # CREATION KIT
                if mod_ini_config(ini_path, "CreationKit", "VSyncRender") is True:
                    vsync_list.append(f"{ini_path} | SETTING: VSyncRender \n")

            if file.lower() == "highfpsphysicsfix.ini":  # High FPS Physics Fix | 44798
                if mod_ini_config(ini_path, "Main", "EnableVSync"):
                    vsync_list.append(f"{ini_path} | SETTING: EnableVSync \n")

                if float(mod_ini_config(ini_path, "Limiter", "LoadingScreenFPS")) < 600.0:
                    mod_ini_config(ini_path, "Limiter", "LoadingScreenFPS", "600.0")
                    logging.info(f"> > > PERFORMED INI LOADING SCREEN FPS FIX FOR {file}")
                    message_list.append(f"> Performed INI Loading Screen FPS Fix For : {file} \n")

            if file.lower() == "longloadingtimesfix.ini":
                if mod_ini_config(ini_path, "Limiter", "EnableVSync") is True:
                    vsync_list.append(f"{ini_path} | SETTING: EnableVSync \n")

            if file.lower() == "reshade.ini":
                if mod_ini_config(ini_path, "APP", "ForceVsync") is True:
                    vsync_list.append(f"{ini_path} | SETTING: ForceVsync \n")

    if vsync_list:
        message_list.append("* NOTICE : VSYNC IS CURRENTLY ENABLED IN THE FOLLOWING FILES * \n")
    message_output = "".join(message_list) + "".join(vsync_list)
    return message_output


# ================================================
# CHECK ALL UNPACKED / LOOSE MOD FILES
# ================================================
def scan_mods_unpacked():
    CMain.vrmode_check()
    message_list = []
    cleanup_list = []
    modscan_list = []

    xse_acronym = CMain.yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", f"Game{CMain.vr}_Info", "XSE_Acronym")
    xse_scriptfiles = CMain.yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", f"Game{CMain.vr}_Info", "XSE_HashedScripts")

    misc_path = "CLASSIC Misc"
    mod_path = CMain.classic_settings("MODS Folder Path")
    if mod_path:
        if Path(mod_path).exists():
            filter_names = ["readme", "changes", "changelog", "change log"]
            print("✔️ MODS FOLDER PATH FOUND! PERFORMING INITIAL MOD FILES CLEANUP...")
            for root, dirs, files in os.walk(mod_path, topdown=False):
                for dirname in dirs:
                    main_path = root.replace(mod_path, "")
                    # ================================================
                    # DETECT MODS WITH AnimationFileData
                    if dirname.lower() == "animationfiledata":
                        root_main = main_path.split(os.path.sep)[1]
                        modscan_list.append(f"[-] NOTICE (ANIMDATA) : {root_main} > CONTAINS CUSTOM ANIMATION FILE DATA \n")
                    # ================================================
                    # (RE)MOVE REDUNDANT FOMOD FOLDERS
                    elif dirname.lower() == "fomod":
                        fomod_folder_path = os.path.join(root, dirname)
                        relative_path = os.path.relpath(fomod_folder_path, mod_path)
                        new_folder_path = os.path.join(misc_path, relative_path)

                        cleanup_list.append(f"MOVED > {fomod_folder_path} FOLDER TO > {misc_path} \n")
                        shutil.move(fomod_folder_path, new_folder_path)

                for filename in files:
                    main_path = root.replace(mod_path, "")
                    # ================================================
                    # DETECT DDS FILES WITH INCORRECT DIMENSIONS
                    if ".dds" in filename.lower():
                        dds_file_path = os.path.join(root, filename)
                        with open(dds_file_path, 'rb') as dds_file:
                            dds_data = dds_file.read()
                        if dds_data[:4] == b'DDS ':
                            width = struct.unpack('<I', dds_data[12:16])[0]
                            height = struct.unpack('<I', dds_data[16:20])[0]
                            if width % 2 != 0 or height % 2 != 0:
                                modscan_list.append(f"[!] CAUTION (DDS-DIMS) : {dds_file_path} > {width}x{height} > DDS DIMENSIONS ARE NOT DIVISIBLE BY 2 \n")
                    # ================================================
                    # DETECT INVALID TEXTURE FILE FORMATS
                    elif (".tga" or ".png") in filename.lower():
                        inv_file_path = os.path.join(root, filename)
                        modscan_list.append(f"[-] NOTICE (-FORMAT-) : {inv_file_path} > HAS THE WRONG TEXTURE FORMAT, SHOULD BE DDS \n")
                    # ================================================
                    # DETECT INVALID SOUND FILE FORMATS
                    elif (".mp3" or ".m4a") in filename.lower():
                        root_main = main_path.split(os.path.sep)[1]
                        modscan_list.append(f"[-] NOTICE (-FORMAT-) : {root_main} > {filename} > HAS THE WRONG SOUND FORMAT, SHOULD BE XWM OR WAV \n")
                    # ================================================
                    # DETECT MODS WITH SCRIPT EXTENDER FILE COPIES
                    elif any(filename.lower() == key.lower() for key in xse_scriptfiles) and "workshop framework" not in root.lower():
                        xse_file_path = os.path.join(root, filename)
                        if f"Scripts\\{filename}" in xse_file_path:
                            root_main = main_path.split(os.path.sep)[1]
                            modscan_list.append(f"[!] CAUTION (XSE-COPY) : {root_main} > CONTAINS ONE OR SEVERAL COPIES OF *{xse_acronym}* SCRIPT FILES \n")
                    # ================================================
                    # DETECT MODS WITH PRECOMBINE / PREVIS FILES
                    elif (".csg" or ".cdx" or ".uvd" or "_oc.nif") in filename.lower() and "previs repair pack" not in root.lower():
                        root_main = main_path.split(os.path.sep)[1]
                        modscan_list.append(f"[-] NOTICE (-PREVIS-) : {root_main} > CONTAINS CUSTOM PRECOMBINE / PREVIS FILES \n")
                    # ================================================
                    # (RE)MOVE REDUNDANT README / CHANGELOG FILES
                    elif any(names.lower() in filename.lower() for names in filter_names) and filename.lower().endswith(".txt"):
                        readme_file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(readme_file_path, mod_path)
                        new_file_path = os.path.join(misc_path, relative_path)

                        # Create subdirectories if they don't exist.
                        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                        cleanup_list.append(f"MOVED > {readme_file_path} FILE TO > {misc_path} \n")
                        shutil.move(readme_file_path, new_file_path)

            print("✔️ CLEANUP COMPLETE! NOW ANALYZING ALL UNPACKED/LOOSE MOD FILES...")
            message_list.append(CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Mods_Warn", "Mods_Reminders"))
            message_list.append("========= RESULTS FROM UNPACKED / LOOSE FILES =========\n")
        else:
            message_list.append(CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Mods_Warn", "Mods_Path_Invalid"))
    else:
        message_list.append(CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Mods_Warn", "Mods_Path_Missing"))

    modscan_unique_list = list(sorted(set(modscan_list)))
    message_output = "".join(message_list) + "".join(cleanup_list) + "".join(modscan_unique_list)
    return message_output


# ================================================
# CHECK ALL ARCHIVED / BA2 MOD FILES
# ================================================
def scan_mods_archived():
    CMain.vrmode_check()
    message_list = []
    modscan_list = []

    xse_acronym = CMain.yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", f"Game{CMain.vr}_Info", "XSE_Acronym")
    xse_scriptfiles = CMain.yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", f"Game{CMain.vr}_Info", "XSE_HashedScripts")

    CLASSIC_folder = Path.cwd()
    bsarch_path = r"CLASSIC Data\BSArch.exe"
    bsarch_path_full = fr"{CLASSIC_folder}\{bsarch_path}"
    mod_path = CMain.classic_settings("MODS Folder Path")
    if mod_path:
        if Path(mod_path).exists():
            if Path(bsarch_path).exists():
                print("✔️ ALL REQUIREMENTS SATISFIED! NOW ANALYZING ALL BA2 MOD ARCHIVES...")
                message_list.append("\n========== RESULTS FROM ARCHIVED / BA2 FILES ==========\n")
                for root, dirs, files in os.walk(mod_path, topdown=False):
                    for filename in files:
                        if "textures.ba2" in filename.lower():
                            main_path = root.replace(mod_path, "")
                            ba2_file_path = os.path.join(root, filename)
                            command_dump = f'"{bsarch_path_full}" "{ba2_file_path}" -dump'

                            archived_dump = subprocess.run(command_dump, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                            if archived_dump.returncode == 0:
                                archived_output = archived_dump.stdout
                                # ================================================
                                # DETECT DDS FILES WITH INCORRECT DIMENSIONS
                                output_split = archived_output.split("\n")
                                output_list = [item for item in output_split if item]
                                for index, line in enumerate(output_list):
                                    if ".dds" in line.lower():
                                        dds_meta = output_list[index + 2]
                                        dds_meta_split = dds_meta.split(":")
                                        width = dds_meta_split[1].replace("  Height", "").strip()
                                        height = dds_meta_split[2].replace("  CubeMap", "").strip()
                                        if width.isdecimal() and height.isdecimal():
                                            if int(width) % 2 != 0 or int(height) % 2 != 0:
                                                root_main = main_path.split(os.path.sep)[1]
                                                modscan_list.append(f"[!] CAUTION (DDS-DIMS) : ({root_main}) {line} > {width}x{height} > DDS DIMENSIONS ARE NOT DIVISIBLE BY 2 \n")
                                    # ================================================
                                    # DETECT INVALID TEXTURE FILE FORMATS
                                    elif (".tga" or ".png") in line.lower():
                                        root_main = main_path.split(os.path.sep)[1]
                                        modscan_list.append(f"[-] NOTICE (-FORMAT-) : ({root_main}) {line} > HAS THE WRONG TEXTURE FORMAT, SHOULD BE DDS \n")
                            else:
                                error_message = archived_dump.stderr
                                print("Command failed with error:\n", error_message)

                        elif "main.ba2" in filename.lower():
                            main_path = root.replace(mod_path, "")
                            ba2_file_path = os.path.join(root, filename)
                            command_list = f'"{bsarch_path_full}" "{ba2_file_path}" -list'
                            archived_list = subprocess.run(command_list, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                            if archived_list.returncode == 0:
                                archived_output = archived_list.stdout
                                # ================================================
                                # DETECT INVALID SOUND FILE FORMATS
                                if (".mp3" or ".m4a") in archived_output.lower():
                                    root_main = main_path.split(os.path.sep)[1]
                                    modscan_list.append(f"[-] NOTICE (-FORMAT-) : {root_main} > CONTAINS SOUND FILES IN THE WRONG FORMAT \n")
                                # ================================================
                                # DETECT MODS WITH AnimationFileData
                                if "animationfiledata" in archived_output.lower():
                                    root_main = main_path.split(os.path.sep)[1]
                                    modscan_list.append(f"[-] NOTICE (ANIMDATA) : {root_main} > CONTAINS CUSTOM ANIMATION FILE DATA \n")
                                # ================================================
                                # DETECT MODS WITH SCRIPT EXTENDER FILE COPIES
                                if any(f"scripts\\{key.lower()}" in archived_output.lower() for key in xse_scriptfiles) and "workshop framework" not in root.lower():
                                    root_main = main_path.split(os.path.sep)[1]
                                    modscan_list.append(f"[!] CAUTION (XSE-COPY) : {root_main} > CONTAINS ONE OR SEVERAL COPIES OF *{xse_acronym}* SCRIPT FILES \n")
                                # ================================================
                                # DETECT MODS WITH PRECOMBINE / PREVIS FILES
                                if (".uvd" or "_oc.nif") in archived_output.lower() and "previs repair pack" not in root.lower():
                                    root_main = main_path.split(os.path.sep)[1]
                                    modscan_list.append(f"[-] NOTICE (-PREVIS-) : {root_main} > CONTAINS CUSTOM PRECOMBINE / PREVIS FILES \n")
                            else:
                                error_message = archived_list.stderr
                                print("Command failed with error:\n", error_message)
            else:
                message_list.append(CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Mods_Warn", "Mods_BSArch_Missing"))
        else:
            message_list.append(CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Mods_Warn", "Mods_Path_Invalid"))
    else:
        message_list.append(CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "Mods_Warn", "Mods_Path_Missing"))

    modscan_unique_list = list(sorted(set(modscan_list)))
    message_output = "".join(message_list) + "".join(modscan_unique_list)
    return message_output


@lru_cache
def game_combined_result():
    CMain.vrmode_check()
    docs_path = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Root_Folder_Docs")
    game_path = CMain.yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", f"Game{CMain.vr}_Info", "Root_Folder_Game")
    combined_return = [check_xse_plugins(), check_crashgen_settings(), check_log_errors(docs_path), check_log_errors(game_path), scan_wryecheck(), scan_mod_inis()]
    combined_result = "".join(combined_return)
    return combined_result


@lru_cache
def mods_combined_result():  # KEEP THESE SEPARATE SO THEY ARE NOT INCLUDED IN AUTOSCAN REPORTS
    combined_return = [scan_mods_unpacked(), scan_mods_archived()]
    combined_result = "".join(combined_return)
    return combined_result


def write_combined_results():
    game_result = game_combined_result()
    mods_result = mods_combined_result()
    with open("CLASSIC Scan Results.md", "w", encoding="utf-8", errors="ignore") as scan_report:
        scan_report.write(game_result + mods_result)


if __name__ == "__main__":
    CMain.main_generate_required()
    print(game_combined_result())
    print(mods_combined_result())
    write_combined_results()
    os.system("pause")