# CRASH LOG AUTO SCANNER (CLAS) | By Poet (The Sound Of Snow)
import json
import os
import random
import re
import shutil
import time
from collections import Counter
from pathlib import Path

import pkg_resources

from CLAS_Database import (GALAXY, MOON, UNIVERSE, clas_toml_create,
                           clas_toml_update, clas_update_check)

clas_toml_create()
clas_update_check()

plugins_pattern = re.compile(r"(.+?)(\.[esp|esm|esl]+)$", re.IGNORECASE | re.MULTILINE)
LCL_skip_list = []
if not os.path.exists("CLAS Ignore.txt"):  # Local plugin skip / ignore list.
    with open("CLAS Ignore.txt", "w", encoding="utf-8", errors="ignore") as CLAS_Ignore:
        CLAS_Ignore.write("Write plugin names you want CLAS to ignore here. (ONE PLUGIN PER LINE)\n")
else:
    with open("CLAS Ignore.txt", "r", encoding="utf-8", errors="ignore") as CLAS_Ignore:
        LCL_skip_list = [line.group() for line in plugins_pattern.finditer(CLAS_Ignore.read())]

# =================== TERMINAL OUTPUT START ====================
print(f"Hello World! | Crash Log Auto Scanner (CLAS) | Version {UNIVERSE.CLAS_Current[-4:]} | Fallout 4")
print("ELIGIBLE CRASH LOGS MUST START WITH 'crash-' AND HAVE .log FILE EXTENSION \n")


def culprit_data():
    try:
        json_path = pkg_resources.resource_filename(__name__, "crash_culprits.json")
        with open(json_path, encoding="utf-8", errors="ignore") as f:
            Culprits = json.load(f)
    except FileNotFoundError:
        json_path = os.path.join(os.path.dirname(__file__), "crash_culprits.json")
        with open(json_path, encoding="utf-8", errors="ignore") as f:
            Culprits = json.load(f)
    return Culprits


def scan_logs():
    # =================== IMPORTED DATA AND REGEX PATTERNS ===================
    Culprits = culprit_data()
    plugin_id_pattern = re.compile(r'\[[0-9A-Fa-f]{2,6}\]')
    detected_plugin_pattern = re.compile(r'File:\s+"?([^"]+)"?')
    form_id_pattern = re.compile(r'(Form ID:|FormID:)\s*0x([0-9A-Fa-f]+)')
    nvidia_pattern = re.compile(r'GPU.*Nvidia', re.IGNORECASE)
    amd_pattern = re.compile(r'GPU.*AMD', re.IGNORECASE)
    records_pattern = re.compile('|'.join(re.escape(pattern) for pattern in UNIVERSE.Crash_Records_Catch))
    records_exclude_pattern = re.compile('|'.join(re.escape(pattern) for pattern in GALAXY.Crash_Records_Exclude))
    # unhandled_exception_pattern = re.compile(r"Unhandled exception.*\+(.*)", re.IGNORECASE)
    unhandled_exception_pattern = re.compile(r"Unhandled exception.*(\+.{7})(.*)", re.IGNORECASE)
    buffout4_pattern = re.compile(r"Buffout 4.* (.*)", re.IGNORECASE)
    # =================== HELPER FUNCTIONS ===================

    def process_file_data(file: Path):
        logpath = file.resolve()
        scanpath = logpath.with_name(logpath.stem + "-AUTOSCAN.md")
        logname = logpath.name
        logtext = logpath.read_text(encoding="utf-8", errors="ignore")

        loglines = logtext.strip().splitlines()

        loglines = list(map(str.strip, loglines))

        return scanpath, logname, logtext, loglines

    def process_log_sections(loglines):
        index_stack = len(loglines) - 1
        index_plugins = 1
        plugins_loaded = False

        for index, line in enumerate(loglines):
            if "MODULES:" in line:
                index_stack = index
            if GALAXY.XSE_Symbol not in line and "PLUGINS:" in line:
                index_plugins = index
            if "[00]" in line:
                plugins_loaded = True
                break

        section_stack_list = loglines[:index_stack]
        section_stack_text = str(section_stack_list)
        section_plugins_list = loglines[index_plugins:]

        loadorder_path = Path("loadorder.txt")

        if loadorder_path.exists():
            plugins_loaded = True
            plugin_format = loadorder_path.read_text(encoding="utf-8", errors="ignore").strip().splitlines()

            section_plugins_list = ["[00]"] if not any("[00]" in elem for elem in plugin_format) else []
            section_plugins_list += [f"[LO] {line.strip()}" for line in plugin_format]

        return section_stack_list, section_stack_text, section_plugins_list, plugins_loaded

    def extract_plugin_ids(loglines):
        # Use a list comprehension to filter the loglines that match the pattern
        return [line for line in loglines if plugin_id_pattern.search(line) and "Modified by:" not in line]

    def extract_detected_plugins(loglines):
        # Use a list comprehension to filter the loglines that match the pattern and not Fallout4.esm
        detected_plugins = [match.group(1) for line in loglines if (match := detected_plugin_pattern.search(line)) and "Fallout4.esm" not in line]

        return sorted(detected_plugins)

    def filter_excluded_plugins(detected_plugins, excluded_plugins):
        return [plugin for plugin in detected_plugins if plugin not in excluded_plugins]

    def find_plugin_culprits(all_plugins, detected_plugins):
        culprits = set()
        counter = Counter(detected_plugins)
        for elem in all_plugins:
            matches = [item for item in detected_plugins if item in elem]
            if matches:
                culprits.update(matches)  # This line replaces the previous four lines, achieving the same result
        return sorted(culprits), counter

    def write_plugin_culprits(output, culprits, detected_plugins_counter):
        if not culprits:
            output.writelines(["* CLAS COULDN'T FIND ANY PLUGIN CULPRITS *\n",
                               "-----\n"])
        else:
            for matches in culprits:
                if isinstance(matches, str):
                    output.write(f"- {matches} : {detected_plugins_counter[matches]}\n")
                else:
                    output.write(f"- {' '.join(matches)} : {detected_plugins_counter[matches[-1]]}\n")
            output.writelines(["-----\n",
                               "[Last number counts how many times each plugin culprit shows up in the crash log.]\n",
                               "These Plugins were caught by Buffout 4 and some of them might be responsible for this crash.\n",
                               "You can try disabling these plugins and recheck your game, though this method can be unreliable.\n",
                               "-----\n"])

    '''GPT Changes Part 1:
    In the updated version, I've made the following changes:

Simplified the string manipulations by normalizing the line and plugin strings at the beginning of the loops.
Used more descriptive variable names like plugin instead of elem.
Removed the redundant id_only variable and used line directly.
Removed unnecessary string replacements with spaces.
Added a return statement to return the form_ids list.
These changes should make the function more readable and easier to maintain.'''

    '''GPT Changes Part 2:
    In the updated version, I've added the missing else block to handle the case when plugins_loaded is False.
    The function now appends the line directly to the form_ids list in that case. The rest of the function remains the same as in the previous improvement.'''  # I initially forgot to paste the whole function.

    def extract_form_ids(loglines, plugins_loaded, section_plugins_list):
        form_ids = []

        for line in loglines:
            match = form_id_pattern.search(line)
            if match and "0xFF" not in line:
                # Extract the matched Form ID
                form_id = match.group(2).strip()
                if plugins_loaded:
                    for plugin in section_plugins_list:
                        plugin = plugin.replace(":", "").strip()
                        if "[FE" not in plugin:
                            if plugin[1:3] == form_id[:2]:
                                form_ids.append(f"Form ID: {form_id} | {plugin}")
                        elif "[FE" in plugin:
                            if plugin[1:6] == form_id[:5]:
                                form_ids.append(f"Form ID: {form_id} | {plugin}")
                else:
                    form_ids.append(form_id)

        return sorted(set(form_ids))

    def write_form_id_culprits(output, form_ids):
        if not form_ids:
            output.writelines(["* CLAS COULDN'T FIND ANY FORM ID CULPRITS *\n",
                               "-----\n"])
        else:
            for elem in form_ids:
                output.write(f"{elem}\n")
            output.writelines(["-----\n",
                               "These Form IDs were caught by Buffout 4 and some of them might be related to this crash.\n",
                               "You can try searching any listed Form IDs in FO4Edit and see if they lead to relevant records.\n",
                               "-----\n"])

    def extract_named_records(section_stack_list):
        named_records = []
        for line in section_stack_list:
            if records_pattern.search(line.lower()):
                if not records_exclude_pattern.search(line):
                    line = re.sub('"', '', line)
                    named_records.append(line.strip())
        named_records = sorted(named_records)
        return dict(Counter(named_records))

    def write_named_records(output, named_records):
        '''nr = set(named_records.keys())  # I picked set because a dict_keys object is based on the set built-in type (same for items and values).
        for item in nr:
            if plugins_pattern.search(item):
                del named_records[item]'''  # demo code for the plugin extension regular expression, removes a plugin from the named records dictionary if it matches the pattern.

        if not named_records:
            output.writelines(["* CLAS COULDN'T FIND ANY NAMED RECORDS *\n",
                               "-----\n"])
        else:
            for item in named_records:
                output.write("{} : {} \n".format(item, named_records[item]))
            output.writelines(["-----\n",
                               "[Last number counts how many times each named record shows up in the crash log.]\n",
                               "These records were caught by Buffout 4 and some of them might be related to this crash.\n",
                               "Named records should give extra info on involved game objects, record types or mod files.\n",
                               "-----\n"])

    '''GPT Changes:
    Introduced a new variable mod_condition to store the mod's condition.
    Added two new optional keys nvidia_specific and amd_specific to the mod dictionary, which will be checked before writing any output.
    Removed the redundant nested conditionals, and replaced them with a single continue statement.
    Combined the two separate output writing blocks into one, reducing code duplication.'''

    def check_core_mods():
        Core_Mods = {
            'Canary Save File Monitor': {
                'condition': re.search('CanarySaveFileMonitor', logtext, re.IGNORECASE),
                'description': 'This is a highly recommended mod that can detect save file corruption.',
                'link': 'https://www.nexusmods.com/fallout4/mods/44949?tab=files'
            },
            'High FPS Physics Fix': {
                'condition': re.search(r"HighFPSPhysicsFix(?:VR)?\.dll", logtext, re.IGNORECASE),
                'description': 'This is a mandatory patch / fix that prevents game engine problems.',
                'link': 'https://www.nexusmods.com/fallout4/mods/44798?tab=files'
            },
            'Previs Repair Pack': {
                'condition': re.search("PPF.esm", logtext, re.IGNORECASE),
                'description': 'This is a highly recommended mod that can improve performance.',
                'link': 'https://www.nexusmods.com/fallout4/mods/46403?tab=files'
            },
            'Unofficial Fallout 4 Patch': {
                'condition': re.search("Unofficial Fallout 4 Patch.esp", logtext, re.IGNORECASE),
                'description': 'If you own all DLCs, make sure that the Unofficial Patch is installed.',
                'link': 'https://www.nexusmods.com/fallout4/mods/4598?tab=files'
            },
            'Vulkan Renderer': {
                'condition': re.search("vulkan-1.dll", logtext, re.IGNORECASE),
                'description': 'This is a highly recommended mod that can improve performance on AMD GPUs.',
                'link': 'https://www.nexusmods.com/fallout4/mods/48053?tab=files',
                'amd_specific': True
            },
            'Nvidia Weapon Debris Fix': {
                'condition': re.search('WeaponDebrisCrashFix.dll', logtext, re.IGNORECASE),
                'description': 'This is a mandatory patch / fix required for any and all Nvidia GPU models.',
                'link': 'https://www.nexusmods.com/fallout4/mods/48078?tab=files',
                'nvidia_specific': True
            },
            'Nvidia Reflex Support': {
                'condition': re.search('NVIDIA_Reflex.dll', logtext, re.IGNORECASE),
                'description': 'This is a highly recommended mod that can improve performance on Nvidia GPUs.',
                'link': 'https://www.nexusmods.com/fallout4/mods/64459?tab=files',
                'nvidia_specific': True
            }
        }
        if plugins_loaded:
            def write_installed(output, mod_name):
                output.write(f"✔️ *{mod_name}* is installed.\n  -----\n")

            def write_not_installed(output, mod_name, mod_data):
                output.write(f"# ❌ {mod_name.upper()} IS NOT INSTALLED OR CLAS CANNOT DETECT IT #\n"
                             f"  {mod_data['description']}\n"
                             f"  Link: {mod_data['link']}\n"
                             "  -----\n")

            def write_nvidia_warning(output, mod_name):
                output.write(f"# ❓ {mod_name.upper()} IS INSTALLED BUT... #\n"
                             "   NVIDIA GPU WAS NOT DETECTED, THIS MOD WILL DO NOTHING!\n"
                             f"   You should uninstall {mod_name} to avoid any problems.\n"
                             "  -----\n")

            for mod_name, mod_data in Core_Mods.items():
                mod_condition = mod_data['condition']
                nvidia_specific = mod_data.get('nvidia_specific', False)
                amd_specific = mod_data.get('amd_specific', False)

                if gpu_amd or gpu_other:
                    if nvidia_specific and mod_condition:
                        write_nvidia_warning(output, mod_name)
                        continue
                    if amd_specific:
                        if mod_condition:
                            write_installed(output, mod_name)
                        else:
                            write_not_installed(output, mod_name, mod_data)
                        continue
                    if nvidia_specific:
                        continue

                if gpu_nvidia:
                    if amd_specific or "Vulkan" in mod_name:
                        continue
                    if nvidia_specific:
                        if mod_condition:
                            write_installed(output, mod_name)
                        else:
                            write_not_installed(output, mod_name, mod_data)
                        continue

                if not (amd_specific or nvidia_specific):
                    if mod_condition:
                        write_installed(output, mod_name)
                    else:
                        write_not_installed(output, mod_name, mod_data)
        else:
            output.write(GALAXY.Warnings["Warn_BLOG_NOTE_Plugins"])

    def culprit_check(output, logtext, section_stack_text):
        # "xxxxx" are placeholders since None values are non iterable.
        Special_Cases = {
            'Nvidia_Crashes': ['Nvidia Debris Crash', 'Nvidia Driver Crash', 'Nvidia Reflex Crash'],
            'Vulkan_Crashes': ['Vulkan Memory Crash', 'Vulkan Settings Crash'],
            'Player_Character_Crash': ['Player Character Crash']
        }

        def check_conditions(culprit_name, error_conditions, stack_conditions):
            def search_any(patterns, text):
                return any(pattern in text for pattern in patterns)

            if culprit_name in Special_Cases['Nvidia_Crashes']:
                nvidia_match = re.search("nvidia", logtext, re.IGNORECASE)
                return bool(nvidia_match) and search_any(stack_conditions, section_stack_text)
            elif culprit_name in Special_Cases['Vulkan_Crashes']:
                vulkan_match = re.search("vulkan", logtext, re.IGNORECASE)
                return bool(vulkan_match) and search_any(stack_conditions, section_stack_text)
            elif culprit_name in Special_Cases['Player_Character_Crash']:
                return any(section_stack_text.count(item) >= 3 for item in stack_conditions)
            else:
                return search_any(error_conditions, crash_error) or search_any(stack_conditions, section_stack_text)

        Culprit_Trap = False
        for culprit_name, culprit_data in Culprits.items():

            # Wrap any keys with single items into a list
            error_conditions = culprit_data['error_conditions']
            if isinstance(error_conditions, str):
                error_conditions = [error_conditions]
            stack_conditions = culprit_data['stack_conditions']
            if isinstance(stack_conditions, str):
                stack_conditions = [stack_conditions]

            # Check culprit keys in crash log
            if check_conditions(culprit_name, error_conditions, stack_conditions):
                output.write(f"{culprit_data['description']}  -----\n")
                Culprit_Trap = True

        return Culprit_Trap

    # ==================== AUTOSCAN REPORT ====================
    print("PERFORMING SCAN... \n")
    statL_scanned = statL_incomplete = statL_failed = statM_CHW = 0
    start_time = time.perf_counter()

    SCAN_folder = UNIVERSE.CLAS_config["Scan_Path"] if UNIVERSE.CLAS_config["Scan_Path"] else os.getcwd()

    if UNIVERSE.CLAS_config["FCX_Mode"]:
        from CLAS_ScanFiles import (scan_game_files, scan_mod_inis,
                                    scan_wryecheck)
        GALAXY.scan_game_report = []
        scan_game_files()
        scan_wryecheck()
        scan_mod_inis()

    for file in Path(SCAN_folder).glob("crash-*.log"):
        scanpath, logname, logtext, loglines = process_file_data(file)

        with scanpath.open("w", encoding="utf-8", errors="ignore") as output:
            def build_header(logname, clas_version):
                header = (f"{logname} | Scanned with Crash Log Auto Scanner (CLAS) version {clas_version}\n",
                          "# FOR BEST VIEWING EXPERIENCE OPEN THIS FILE IN NOTEPAD++ | BEWARE OF FALSE POSITIVES #\n",
                          "====================================================\n")
                return header

            output.writelines(build_header(logname, UNIVERSE.CLAS_Current[-4:]))

            # DEFINE LINE INDEXES HERE
            crash_ver_match = buffout4_pattern.search(logtext)
            crash_ver = crash_ver_match.group() if crash_ver_match else "❌ Buffout Version Not Found"
            error_match = unhandled_exception_pattern.search(logtext)
            crash_error = error_match.group() if error_match else "❌ Error Not Found"
            
            section_stack_list, section_stack_text, section_plugins_list, plugins_loaded = process_log_sections(loglines)

            # BUFFOUT VERSION CHECK
            output.writelines([f"Main Error: {crash_error}\n",
                               "====================================================\n",
                               f"Detected Buffout Version: {crash_ver}\n",
                               f"Latest Buffout Version: {GALAXY.CRASHGEN_OLD[10:17]} / NG: {GALAXY.CRASHGEN_NEW[10:17]}\n"])

            if crash_ver.casefold() == GALAXY.CRASHGEN_OLD.casefold():
                output.write("✔️ You have the latest version of Buffout 4!")
            elif crash_ver.casefold() == GALAXY.CRASHGEN_NEW.casefold():
                output.write("✔️ You have the latest version of Buffout 4 NG!")
            else:
                output.write(GALAXY.Warnings["Warn_SCAN_Outdated_Buffout4"])

            output.writelines(["\n====================================================\n",
                               "CHECKING IF NECESSARY FILES/SETTINGS ARE CORRECT...\n",
                               "====================================================\n"])

            fcx_mode = UNIVERSE.CLAS_config["FCX_Mode"]

            if fcx_mode == "true":
                output.write(GALAXY.Warnings["Warn_SCAN_FCX_Enabled"])
                for item in GALAXY.scan_game_report:
                    output.write(f"{item}\n")
            else:
                output.write(GALAXY.Warnings["Warn_SCAN_FCX_Disabled"])

                achievements_status = "Achievements: true" in logtext
                memory_manager_status = "MemoryManager: true" in logtext
                f4ee_status = "F4EE: false" in logtext

                if (achievements_status and "achievements.dll" in logtext) or (achievements_status and "UnlimitedSurvivalMode.dll" in logtext):
                    output.write(GALAXY.Warnings["Warn_TOML_Achievements"])
                else:
                    output.write("✔️ Achievements parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

                if memory_manager_status and "BakaScrapHeap.dll" in logtext:
                    output.write(GALAXY.Warnings["Warn_TOML_Memory"])
                else:
                    output.write("✔️ Memory Manager parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

                if f4ee_status and "f4ee.dll" in logtext:
                    output.write(GALAXY.Warnings["Warn_TOML_F4EE"])
                else:
                    output.write("✔️ Looks Menu (F4EE) parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

            output.writelines(["====================================================\n",
                               "CHECKING IF LOG MATCHES ANY KNOWN CRASH CULPRITS...\n",
                               "====================================================\n"])

            # ====================== HEADER CULPRITS =====================

            if ".dll" in crash_error.lower() and "tbbmalloc" not in crash_error.lower():
                output.write(GALAXY.Warnings["Warn_SCAN_NOTE_DLL"])

            # ====================== GPU Variables ======================
            gpu_nvidia = any(nvidia_pattern.search(line) for line in loglines)
            gpu_amd = any(amd_pattern.search(line) for line in loglines) if not gpu_nvidia else False
            gpu_other = True if not gpu_nvidia and not gpu_amd else False  # INTEL GPUs & Other Undefine
            assert not (gpu_nvidia and gpu_amd), "❌ ERROR : Both GPU types detected in the log file!"

            # =================== CRASH CULPRITS CHECK ==================
            Culprit_Trap = culprit_check(output, logtext, section_stack_text)

            if Culprit_Trap is False:  # DEFINE CHECK IF NO KNOWN CRASH ERRORS / CULPRITS ARE FOUND
                output.writelines(["# CLAS FOUND NO CRASH ERRORS / CULPRITS THAT MATCH THE CURRENT DATABASE #\n",
                                   "Check below for mods that can cause frequent crashes and other problems.\n",
                                   "-----\n"])
            else:
                output.writelines(["* FOR DETAILED DESCRIPTIONS AND POSSIBLE SOLUTIONS TO ANY ABOVE DETECTED CRASH CULPRITS *\n",
                                   "* SEE: https://docs.google.com/document/d/17FzeIMJ256xE85XdjoPvv_Zi3C5uHeSTQh6wOZugs4c *\n",
                                   "-----\n"])

            # =============== MOD / PLUGIN CHECK TEMPLATES ==============
            def check_plugins(mods, mod_trap, plugins_loaded, section_plugins_list, LCL_skip_list):
                if not plugins_loaded:
                    return mod_trap
                mods_found = set()
                for line in section_plugins_list:
                    for mod_data in mods:  # changed from mods.values()
                        mod_data_match = mod_data["mod"].search(line)
                        if "File:" not in line and mod_data_match and mod_data_match.group() not in LCL_skip_list:
                            warn = ''.join(mod_data["warn"])
                            prefix = line[0:5] if "[FE" not in line else line[0:9]
                            if mod_data_match.group() not in mods_found:
                                output.writelines([f"[!] Found: {prefix} {warn}\n", "-----\n"])
                            mods_found.add(mod_data_match.group())
                            mod_trap = True

                return mod_trap

            def check_conflicts(mods, mod_trap, plugins_loaded, logtext):
                if not plugins_loaded:
                    return mod_trap

                for mod_data in mods:  # changed from mods.values()
                    mod1_match = mod_data["mod_1"].search(logtext)
                    mod2_match = mod_data["mod_2"].search(logtext)
                    if mod1_match and mod2_match:
                        warn = ''.join(mod_data["warn"])
                        output.writelines([f"[!] CAUTION : {warn}\n", "-----\n"])
                        mod_trap = True

                return mod_trap

            # ================= ALL MOD / PLUGIN CHECKS =================

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS THAT CAN CAUSE FREQUENT CRASHES...\n",
                               "====================================================\n"])

            def check_special_mods(logtext, crash_error, output, statM_CHW):
                found = False

                if logtext.count("ClassicHolsteredWeapons") >= 3 or "ClassicHolsteredWeapons" in crash_error:
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS\n",
                                       "CLAS IS PRETTY CERTAIN THAT CHW CAUSED THIS CRASH!\n",
                                       "You should disable CHW to further confirm this.\n",
                                       "-----\n"])
                    statM_CHW += 1
                    found = True
                elif "ClassicHolsteredWeapons" in logtext and "d3d11" in crash_error:
                    output.writelines(["[!] Found: CLASSIC HOLSTERED WEAPONS, BUT...\n",
                                       "CLAS CANNOT ACCURATELY DETERMINE IF CHW CAUSED THIS CRASH OR NOT.\n",
                                       "You should open CHW's ini file and change IsHolsterVisibleOnNPCs to 0.\n",
                                       "This usually prevents most common crashes with Classic Holstered Weapons.\n",
                                       "-----\n"])
                return found

            def process_mod_check_results(Mod_Check1, Mod_Trap1, output, statL_scanned):
                if (Mod_Check1 or Mod_Trap1) is True:
                    output.writelines(["# [!] CAUTION : ANY ABOVE DETECTED MODS HAVE A MUCH HIGHER CHANCE TO CRASH YOUR GAME! #\n",
                                       "  You can disable any/all of them temporarily to confirm they caused this crash.\n",
                                       "-----\n"])
                    statL_scanned += 1
                elif (Mod_Check1 and Mod_Trap1) is False:
                    output.writelines(["# CLAS FOUND NO PROBLEMATIC MODS THAT MATCH THE CURRENT DATABASE FOR THIS LOG #\n",
                                       "THAT DOESN'T MEAN THERE AREN'T ANY! YOU SHOULD RUN PLUGIN CHECKER IN WRYE BASH.\n",
                                       "Plugin Checker Instructions: https://www.nexusmods.com/fallout4/articles/4141\n",
                                       "-----\n"])
                    statL_scanned += 1
                return statL_scanned

            Mod_Trap1 = False
            if plugins_loaded:
                Mod_Check1 = check_plugins(MOON.Mods1, Mod_Trap1, plugins_loaded, section_plugins_list, LCL_skip_list)

                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                Mod_Trap1 = check_special_mods(logtext, crash_error, output, statM_CHW)

                statL_scanned = process_mod_check_results(Mod_Check1, Mod_Trap1, output, statL_scanned)
            else:
                output.write(GALAXY.Warnings["Warn_BLOG_NOTE_Plugins"])
                statL_incomplete += 1

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS THAT CONFLICT WITH OTHER MODS...\n",
                               "====================================================\n"])

            Mod_Trap2 = False
            if plugins_loaded:
                Mod_Check2 = check_conflicts(MOON.Mods2, Mod_Trap2, plugins_loaded, logtext)

                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                # CURRENTLY NONE

                if (Mod_Check2 or Mod_Trap2) is True:
                    output.writelines(["# CLAS FOUND MODS THAT ARE INCOMPATIBLE OR CONFLICT WITH YOUR OTHER MODS # \n",
                                       "* YOU SHOULD CHOOSE WHICH MOD TO KEEP AND REMOVE OR DISABLE THE OTHER MOD * \n",
                                       "-----\n"])
                elif (Mod_Check2 and Mod_Trap2) is False:
                    output.writelines(["# CLAS FOUND NO MODS THAT ARE INCOMPATIBLE OR CONFLICT WITH YOUR OTHER MODS #\n",
                                       "-----\n"])
            else:
                output.write(GALAXY.Warnings["Warn_BLOG_NOTE_Plugins"])

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS WITH SOLUTIONS & COMMUNITY PATCHES\n",
                               "====================================================\n"])

            def check_special_mods_with_solutions(logtext, output):
                found = False

                thuggy_smurf_mods = ("Depravity", "FusionCityRising", "HotC", "OutcastsAndRemnants", "ProjectValkyrie")
                custom_race_mods = ("CaN.esm", "AnimeRace_Nanako.esp")
                fall_souls_mod = "FallSouls.dll"

                def write_output(message):
                    nonlocal found
                    output.writelines(message)
                    found = True

                if any(item in logtext for item in thuggy_smurf_mods):
                    write_output([f"[!] Found: [XX] THUGGYSMURF QUEST MOD(S)\n",
                                  "If you have Depravity, Fusion City Rising, HOTC, Outcasts and Remnants and/or Project Valkyrie\n",
                                  "install this patch with facegen data, fully generated precomb/previs data and several tweaks.\n",
                                  "Patch Link: https://www.nexusmods.com/fallout4/mods/56876?tab=files\n",
                                  "-----\n"])

                if any(item in logtext for item in custom_race_mods):
                    write_output([f"[!] Found: [XX] CUSTOM RACE SKELETON MOD(S)\n",
                                  "If you have AnimeRace NanakoChan or Crimes Against Nature, install the Race Skeleton Fixes.\n",
                                  "Skeleton Fixes Link (READ THE DESCRIPTION): https://www.nexusmods.com/fallout4/mods/56101\n",
                                  "-----\n"])

                if fall_souls_mod in logtext:
                    write_output([f"[!] Found: FALLSOULS UNPAUSED GAME MENUS\n",
                                  "Occasionally breaks the Quests menu, can cause crashes while changing MCM settings.\n",
                                  "Advised Fix: Toggle PipboyMenu in FallSouls MCM settings or completely reinstall the mod.\n",
                                  "-----\n"])

                return found

            Mod_Trap3 = False
            if plugins_loaded:
                Mod_Check3 = check_plugins(MOON.Mods3, Mod_Trap3, plugins_loaded, section_plugins_list, LCL_skip_list)

                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                Mod_Trap3 = check_special_mods_with_solutions(logtext, output)

                if Mod_Check3 or Mod_Trap3 is True:
                    output.writelines([f"# CLAS FOUND PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                       "[Due to limitations, CLAS will show warnings for some mods even if fixes or patches are already installed.]\n",
                                       "[To hide these warnings, you can add their plugin names to the CLAS Ignore.txt file. ONE PLUGIN PER LINE.]\n",
                                       "-----\n"])
                elif Mod_Check3 and Mod_Trap3 is False:
                    output.writelines([f"# CLAS FOUND NO PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                       "-----\n"])
            else:
                output.write(GALAXY.Warnings["Warn_BLOG_NOTE_Plugins"])

            output.writelines(["FOR FULL LIST OF IMPORTANT PATCHES AND FIXES FOR THE BASE GAME AND MODS,\n",
                               "VISIT THIS ARTICLE: https://www.nexusmods.com/fallout4/articles/3769\n",
                               "-----\n"])

            output.writelines(["====================================================\n",
                               "CHECKING FOR MODS PATCHED THROUGH OPC INSTALLER...\n",
                               "====================================================\n"])

            Mod_Trap4 = False
            if plugins_loaded:
                Mod_Check4 = check_plugins(MOON.Mods4, Mod_Trap4, plugins_loaded, section_plugins_list, LCL_skip_list)

                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                # CURRENTLY NONE

                if (Mod_Check4 or Mod_Trap4) is True:
                    output.writelines(["* FOR PATCH REPOSITORY THAT PREVENTS CRASHES AND FIXES PROBLEMS IN THESE AND OTHER MODS,* \n",
                                       "* VISIT OPTIMIZATION PATCHES COLLECTION: https://www.nexusmods.com/fallout4/mods/54872 * \n",
                                       "-----\n"])
                elif (Mod_Check4 and Mod_Trap4) is False:
                    output.writelines(["# CLAS FOUND NO PROBLEMATIC MODS THAT ARE ALREADY PATCHED THROUGH OPC INSTALLER #\n",
                                       "-----\n"])
            else:
                output.write(GALAXY.Warnings["Warn_BLOG_NOTE_Plugins"])

            output.writelines(["====================================================\n",
                               "CHECKING IF IMPORTANT PATCHES & FIXES ARE INSTALLED\n",
                               "====================================================\n"])

            # 5) CHECKING IF IMPORTANT PATCHES & FIXES ARE INSTALLED
            check_core_mods()

            output.writelines(["====================================================\n",
                               "SCANNING THE LOG FOR SPECIFIC (POSSIBLE) CULPRITS...\n",
                               "====================================================\n"])
            output.write("LIST OF (POSSIBLE) PLUGIN CULPRITS:\n")

            list_ALLPLUGINS = extract_plugin_ids(loglines)
            list_DETPLUGINS = extract_detected_plugins(loglines)
            list_DETPLUGINS = filter_excluded_plugins(list_DETPLUGINS, GALAXY.Game_Plugins_Exclude)

            culprits, culprits_counter = find_plugin_culprits(list_ALLPLUGINS, list_DETPLUGINS)
            write_plugin_culprits(output, culprits, culprits_counter)

            # ===========================================================

            list_DETFORMIDS = extract_form_ids(loglines, plugins_loaded, section_plugins_list)

            output.write("LIST OF (POSSIBLE) FORM ID CULPRITS:\n")
            write_form_id_culprits(output, list_DETFORMIDS)

            # ===========================================================

            list_records = extract_named_records(section_stack_list)

            output.write("LIST OF DETECTED (NAMED) RECORDS:\n")
            write_named_records(output, list_records)

            output.writelines(["FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,\n",
                               "VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115\n",
                               "===============================================================================\n",
                               f"END OF AUTOSCAN | Author / Made By: Poet#9800 (DISCORD) | {UNIVERSE.CLAS_Date}\n",
                               "CONTRIBUTORS | evildarkarchon | kittivelae | AtomicFallout757\n",
                               "CLAS | https://www.nexusmods.com/fallout4/mods/56255"])

    # ================== TERMINAL SCAN COMPLETE ==================
    time.sleep(0.5)
    print("SCAN COMPLETE! (IT MIGHT TAKE SEVERAL SECONDS FOR SCAN RESULTS TO APPEAR)")
    print("SCAN RESULTS ARE AVAILABLE IN FILES NAMED crash-date-and-time-AUTOSCAN.md \n")
    print("FOR FULL LIST OF MODS THAT CAUSE PROBLEMS, THEIR ALTERNATIVES AND DETAILED SOLUTIONS,")
    print("VISIT THE BUFFOUT 4 CRASH ARTICLE: https://www.nexusmods.com/fallout4/articles/3115 \n")
    print("================================ CONTACT INFO =================================")
    print("DISCORD | Poet#9800 (https://discord.gg/DfFYJtt8p4)")
    print("NEXUS PROFILE | https://www.nexusmods.com/users/64682231")
    print("CLAS NEXUS PAGE | https://www.nexusmods.com/fallout4/mods/56255")
    print(random.choice(GALAXY.Sneaky_Tips))

    '''GPT Changes:
    Replaced variable names with more descriptive alternatives.
Used pathlib for file path manipulation.
Simplified the check for failed scans using the Path methods.
These changes should make the code more readable and easier to maintain.'''

    # ==== CHECK FAULTY FILES | HIDE USERNAME | MOVE UNSOLVED ====
    failed_scans = []
    homedir = Path.home()

    for crash_file_path in Path(SCAN_folder).glob("crash-*"):
        file_move = False
        scan_file_path = crash_file_path
        if crash_file_path.suffix == ".log":
            scan_file_path = crash_file_path.with_name(crash_file_path.stem + "-AUTOSCAN.md")

        with open(crash_file_path, "r", encoding="utf-8", errors="ignore") as crash_file:
            file_contents = crash_file.read()
            crash_file.seek(0)
            line_count = sum(1 for _ in crash_file)

        if homedir.name in file_contents:
            file_contents = file_contents.replace(f"{homedir.parent}\\{homedir.name}", "******").replace(f"{homedir.parent}/{homedir.name}", "******")
            with open(crash_file_path, "w", encoding="utf-8", errors="ignore") as crash_file:
                crash_file.write(file_contents)

        if "FOUND NO CRASH ERRORS" in file_contents:
            file_move = True

        if ".txt" in crash_file_path.name or line_count < 20:
            failed_scans.append(crash_file_path.name)
            statL_failed += 1
            statL_scanned -= 1
            file_move = True

        if file_move and UNIVERSE.CLAS_config["Move_Unsolved"]:
            unsolved_folder = "CLAS UNSOLVED"
            Path(unsolved_folder).mkdir(exist_ok=True)
            crash_move = Path(unsolved_folder, crash_file_path.name)
            scan_move = Path(unsolved_folder, scan_file_path.name)

            if crash_file_path.exists():
                shutil.move(crash_file_path, crash_move)
            if scan_file_path.exists():
                shutil.move(scan_file_path, scan_move)

    if failed_scans:
        print("NOTICE : CLAS WAS UNABLE TO PROPERLY SCAN THE FOLLOWING LOG(S):")
        print('\n'.join(failed_scans))
        print("===============================================================================")
        print("Most common reason for this are logs being incomplete or in the wrong format.")
        print("Make sure that your crash logs are saved with .log file format, NOT .txt!")

    # ====================== TERMINAL OUTPUT END ======================
    print("===============================================================================")
    print(f"\nScanned all available logs in ({str(time.perf_counter() - 0.5 - start_time)[:7]}) seconds.")
    print(f"Number of Scanned Logs (No Autoscan Errors): {statL_scanned}")
    print(f"Number of Incomplete Logs (No Plugins List): {statL_incomplete}")
    print(f"Number of Failed Logs (Autoscan Can't Scan): {statL_failed}")
    print("-----")
    print("SCAN RESULTS ARE AVAILABLE IN FILES NAMED crash-date-and-time-AUTOSCAN.md")
    print("PLEASE OPEN THESE FILES WITH NOTEPAD++ OR SIMILAR AND READ GIVEN RESULTS")
    # Trying to generate Stat Logging for 0 valid logs can crash the script.
    if statL_scanned == 0:
        print(" ❌ CLAS found no crash logs to scan.")
        print("    There are no statistics to show.\n")
    return


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    import argparse

    parser = argparse.ArgumentParser(prog="Crash Log Auto Scanner (CLAS)", description="All command-line options are saved to the INI file.")
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
    if isinstance(args.fcx_mode, bool) and not args.fcx_mode == UNIVERSE.CLAS_config["FCX_Mode"]:
        clas_toml_update("FCX_Mode", args.fcx_mode)

    if isinstance(args.imi_mode, bool) and not args.imi_mode == UNIVERSE.CLAS_config["IMI_Mode"]:
        clas_toml_update("IMI_Mode", args.imi_mode)

    if isinstance(args.stat_logging, bool) and not args.stat_logging == UNIVERSE.CLAS_config["Stat_Logging"]:
        clas_toml_update("Stat_Logging", args.stat_logging)

    if isinstance(args.move_unsolved, bool) and not args.move_unsolved == UNIVERSE.CLAS_config["Move_Unsolved"]:
        clas_toml_update("Move_Unsolved", args.move_unsolved)

    if isinstance(ini_path, Path) and ini_path.resolve().is_dir() and not str(ini_path) == UNIVERSE.CLAS_config["INI_Path"]:
        clas_toml_update("INI_Path", str(Path(ini_path).resolve()))

    if isinstance(scan_path, Path) and scan_path.resolve().is_dir() and not str(scan_path) == UNIVERSE.CLAS_config["Scan_Path"]:
        clas_toml_update("Scan_Path", str(Path(scan_path).resolve()))

    scan_logs()
    os.system("pause")
