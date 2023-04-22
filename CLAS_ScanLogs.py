# CRASH LOG AUTO SCANNER (CLAS) | By Poet (The Sound Of Snow)
import os
import random
import shutil
import time
from collections import Counter
from glob import glob
from pathlib import Path

from CLAS_Database import (GALAXY, MOON, UNIVERSE, clas_ini_create,
                           clas_ini_update, clas_update_check)

clas_ini_create()
clas_update_check()

LCL_skip_list = []
if not os.path.exists("CLAS Ignore.txt"):  # Local plugin skip / ignore list.
    with open("CLAS Ignore.txt", "w", encoding="utf-8", errors="ignore") as CLAS_Ignore:
        CLAS_Ignore.write("Write plugin names you want CLAS to ignore here. (ONE PLUGIN PER LINE)\n")
else:
    with open("CLAS Ignore.txt", "r", encoding="utf-8", errors="ignore") as CLAS_Ignore:
        LCL_skip_list = [line.strip() for line in CLAS_Ignore.readlines()[1:]]
        for i in range(len(LCL_skip_list)):
            if not LCL_skip_list[i].startswith(' '):
                LCL_skip_list[i] = ' ' + LCL_skip_list[i]

# =================== TERMINAL OUTPUT START ====================
print(f"Hello World! | Crash Log Auto Scanner (CLAS) | Version {UNIVERSE.CLAS_Current[-4:]} | Fallout 4")
print("ELIGIBLE CRASH LOGS MUST START WITH 'crash-' AND HAVE .log FILE EXTENSION \n")


def scan_logs():
    # =================== HELPER FUNCTIONS ===================
    def process_log_sections(loglines):
        index_stack = len(loglines) - 1
        index_plugins = 1
        plugins_loaded = False

        for line in loglines:
            if "MODULES:" in line:
                index_stack = loglines.index(line)
            if GALAXY.XSE_Symbol not in line and "PLUGINS:" in line:
                index_plugins = loglines.index(line)
            if "[00]" in line:
                plugins_loaded = True
                break

        section_stack_list = loglines[:index_stack]
        section_stack_text = str(section_stack_list)
        section_plugins_list = loglines[index_plugins:]

        if os.path.exists("loadorder.txt"):
            plugins_loaded = True
            section_plugins_list = []

            with open("loadorder.txt", "r", encoding="utf-8", errors="ignore") as loadorder_check:
                plugin_format = loadorder_check.readlines()

                if len(plugin_format) >= 1 and not any("[00]" in elem for elem in section_plugins_list):
                    section_plugins_list.append("[00]")

                for line in plugin_format:
                    line = "[LO] " + line.strip()
                    section_plugins_list.append(line)

        return section_stack_list, section_stack_text, section_plugins_list, plugins_loaded

    def extract_plugin_ids(loglines):
        plugin_ids = []
        for line in loglines:
            if "[" in line and "]" in line and "Modified by:" not in line:
                start_index = line.index("[")
                end_index = line.index("]")
                if end_index - start_index == 3 or end_index - start_index == 7:
                    plugin_ids.append(line.strip())
        return plugin_ids

    def extract_detected_plugins(loglines):
        detected_plugins = set()
        for line in loglines:
            if "File:" in line and "Fallout4.esm" not in line:
                line = line.replace("File: ", "").replace('"', '').strip()
                if line.strip():
                    detected_plugins.add(line.strip())
        return sorted(detected_plugins)

    def filter_excluded_plugins(detected_plugins, excluded_plugins):
        return [plugin for plugin in detected_plugins if plugin not in excluded_plugins]

    def find_plugin_culprits(all_plugins, detected_plugins):
        culprits = set()
        counter = Counter(detected_plugins)
        for elem in all_plugins:
            matches = [item for item in detected_plugins if item in elem]
            if matches and len(matches) > 1:
                culprits = set(matches)
            elif matches and len(matches) == 1:
                culprits.add(matches[0])
        return sorted(culprits), counter

    def write_plugin_culprits(output, culprits, detected_plugins_counter):
        if not culprits:
            output.writelines(["* AUTOSCAN COULDN'T FIND ANY PLUGIN CULPRITS *\n",
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
            if ("Form ID:" in line or "FormID:" in line) and "0xFF" not in line:
                # Normalize the line
                line = line.replace("0x", "").replace("Form ID: ", "").replace("FormID: ", "").strip()

                if plugins_loaded:
                    for plugin in section_plugins_list:
                        # Normalize the plugin
                        plugin = plugin.replace(":", "").strip()

                        # Handle plugins without "[FE"
                        if "]" in plugin and "[FE" not in plugin:
                            if plugin[2:4] == line[:2]:
                                form_ids.append(f"Form ID: {line} | {plugin}")

                        # Handle plugins with "[FE"
                        elif "[FE" in plugin:
                            if plugin[2:7] == line[:5]:
                                form_ids.append(f"Form ID: {line} | {plugin}")
                else:
                    form_ids.append(line.strip())

        return sorted(set(form_ids))

    def write_form_id_culprits(output, form_ids):
        if not form_ids:
            output.writelines(["* AUTOSCAN COULDN'T FIND ANY FORM ID CULPRITS *\n",
                               "-----\n"])
        else:
            for elem in form_ids:
                output.write(f"{elem}\n")
            output.writelines(["-----\n",
                               "These Form IDs were caught by Buffout 4 and some of them might be related to this crash.\n",
                               "You can try searching any listed Form IDs in FO4Edit and see if they lead to relevant records.\n",
                               "-----\n"])

    def extract_named_records(section_stack_list, crash_records_catch, crash_records_exclude):
        named_records = []
        for line in section_stack_list:
            if any(elem in line.lower() for elem in crash_records_catch):
                if not any(elem in line for elem in crash_records_exclude):
                    line = line.replace('"', '')
                    named_records.append(line.strip())
        named_records = sorted(named_records)
        return dict(Counter(named_records))

    def write_named_records(output, named_records):
        if not named_records:
            output.writelines(["* AUTOSCAN COULDN'T FIND ANY NAMED RECORDS *\n",
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
                'condition': 'CanarySaveFileMonitor' in logtext,
                'description': 'This is a highly recommended mod that can detect save file corruption.',
                'link': 'https://www.nexusmods.com/fallout4/mods/44949?tab=files'
            },
            'High FPS Physics Fix': {
                'condition': 'HighFPSPhysicsFix.dll' in logtext or 'HighFPSPhysicsFixVR.dll' in logtext,
                'description': 'This is a mandatory patch / fix that prevents game engine problems.',
                'link': 'https://www.nexusmods.com/fallout4/mods/44798?tab=files'
            },
            'Previs Repair Pack': {
                'condition': 'PPF.esm' in logtext,
                'description': 'This is a highly recommended mod that can improve performance.',
                'link': 'https://www.nexusmods.com/fallout4/mods/46403?tab=files'
            },
            'Unofficial Fallout 4 Patch': {
                'condition': 'Unofficial Fallout 4 Patch.esp' in logtext,
                'description': 'If you own all DLCs, make sure that the Unofficial Patch is installed.',
                'link': 'https://www.nexusmods.com/fallout4/mods/4598?tab=files'
            },
            'Vulkan Renderer': {
                'condition': 'vulkan-1.dll' in logtext,
                'description': 'This is a highly recommended mod that can improve performance on AMD GPUs.',
                'link': 'https://www.nexusmods.com/fallout4/mods/48053?tab=files',
                'amd_specific': True
            },
            'Nvidia Weapon Debris Fix': {
                'condition': 'WeaponDebrisCrashFix.dll' in logtext,
                'description': 'This is a mandatory patch / fix required for any and all Nvidia GPU models.',
                'link': 'https://www.nexusmods.com/fallout4/mods/48078?tab=files',
                'nvidia_specific': True
            },
            'Nvidia Reflex Support': {
                'condition': 'NVIDIA_Reflex.dll' in logtext,
                'description': 'This is a highly recommended mod that can improve performance on Nvidia GPUs.',
                'link': 'https://www.nexusmods.com/fallout4/mods/64459?tab=files',
                'nvidia_specific': True
            }
        }

        if plugins_loaded:
            for mod_name, mod_data in Core_Mods.items():
                mod_condition = mod_data['condition']
                nvidia_specific = mod_data.get('nvidia_specific', False)  # If the key doesn't exist, return False
                amd_specific = mod_data.get('amd_specific', False)

                if gpu_amd or gpu_other:
                    if nvidia_specific:
                        if mod_condition:
                            output.write(f"# ❓ {mod_name.upper()} IS INSTALLED BUT... #\n"
                                         "   NVIDIA GPU WAS NOT DETECTED, THIS MOD WILL DO NOTHING!\n"
                                         f"   You should uninstall {mod_name} to avoid any problems.\n"
                                         "  -----\n")
                        continue
                    elif amd_specific:
                        continue

                elif gpu_nvidia and "Vulkan" in mod_name:
                    continue

                if mod_condition:
                    output.write(f"✔️ *{mod_name}* is installed.\n  -----\n")
                else:
                    output.write(f"# ❌ {mod_name.upper()} IS NOT INSTALLED OR AUTOSCAN CANNOT DETECT IT #\n"
                                 f"  {mod_data['description']}\n"
                                 f"  Link: {mod_data['link']}\n"
                                 "  -----\n")

        else:
            output.write(GALAXY.Warnings["Warn_BLOG_NOTE_Plugins"])

    def culprit_check(output, logtext, section_stack_text):
        # "xxxxx" are placeholders since None values are non iterable.
        Culprits = {
            'Stack Overflow Crash': {
                'error_conditions': "EXCEPTION_STACK_OVERFLOW", 'stack_conditions': "xxxxx",
                'description': '# Checking for Stack Overflow Crash......... CULPRIT FOUND! > Priority : [5] #\n'},

            'Active Effects Crash': {
                'error_conditions': "0x000100000000", 'stack_conditions': "xxxxx",
                'description': '# Checking for Active Effects Crash......... CULPRIT FOUND! > Priority : [5] #\n'},

            'Bad Math Crash': {
                'error_conditions': "EXCEPTION_INT_DIVIDE_BY_ZERO", 'stack_conditions': "xxxxx",
                'description': '# Checking for Bad Math Crash............... CULPRIT FOUND! > Priority : [5] #\n'},

            'Null Crash': {
                'error_conditions': "0x000000000000", 'stack_conditions': "xxxxx",
                'description': '# Checking for Null Crash................... CULPRIT FOUND! > Priority : [5] #\n'},

            # ====================== STACK CULPRITS ======================

            'DLL Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "DLCBannerDLC01.dds",
                'description': '# Checking for DLL Crash.................... CULPRIT FOUND! > Priority : [5] #\n'},

            'LOD Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSLocation", "BGSQueuedTerrainInitialLoad"),
                'description': '# Checking for LOD Crash.................... CULPRIT FOUND! > Priority : [5] #\n'},

            'MCM Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("FaderData", "FaderMenu", "UIMessage"),
                'description': '# Checking for MCM Crash.................... CULPRIT FOUND! > Priority : [3] #\n'},

            'Decal Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSDecalManager", "BSTempEffectGeometryDecal"),
                'description': '# Checking for Decal Crash.................. CULPRIT FOUND! > Priority : [5] #\n'},

            'Equip Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "PipboyMapData",
                'description': '# Checking for Equip Crash.................. CULPRIT FOUND! > Priority : [3] #\n'},

            'Script Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("Papyrus", "VirtualMachine", "Assertion failed"),
                'description': '# Checking for Script Crash................. CULPRIT FOUND! > Priority : [3] #\n'},

            'Generic Crash': {
                'error_conditions': "tbbmalloc", 'stack_conditions': "xxxxx",
                'description': '# Checking for Generic Crash................ CULPRIT FOUND! > Priority : [2] #\n'},

            'Antivirus Crash': {
                'error_conditions': ("24A48D48", "bdhkm64.dll"), 'stack_conditions': ("usvfs::hook_DeleteFileW", "::Manager", "::zlibStreamDetail"),
                'description': '# Checking for Antivirus Crash.............. CULPRIT FOUND! > Priority : [5] #\n'},

            'BA2 Limit Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "LooseFileAsyncStream",
                'description': '# Checking for BA2 Limit Crash.............. CULPRIT FOUND! > Priority : [5] #\n'},

            'Rendering Crash': {
                'error_conditions': "d3d11", 'stack_conditions': "xxxxx",
                'description': '# Checking for Rendering Crash.............. CULPRIT FOUND! > Priority : [4] #\n'},

            'C++ Redist Crash': {
                'error_conditions': ("MSVCR", "MSVCP"), 'stack_conditions': "xxxxx",
                'description': '# Checking for C++ Redist Crash............. CULPRIT FOUND! > Priority : [3] #\n'},

            'Grid Scrap Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("GridAdjacencyMapNode", "PowerUtils"),
                'description': '# Checking for Grid Scrap Crash............. CULPRIT FOUND! > Priority : [5] #\n'},

            'Map Marker Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("HUDCompass", "HUDCompassMarker", "attachMovie()"),
                'description': '# Checking for Map Marker Crash............. CULPRIT FOUND! > Priority : [5] #\n'},

            'Mesh (NIF) Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("LooseFileStream", "BSFadeNode", "BSMultiBoundNode"),
                'description': '# Checking for Mesh (NIF) Crash............. CULPRIT FOUND! > Priority : [4] #\n'},

            'Texture (DDS) Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("Create2DTexture", "DefaultTexture"),
                'description': '# Checking for Texture (DDS) Crash.......... CULPRIT FOUND! > Priority : [4] #\n'},

            'Material (BGSM) Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("DefaultTexture_Black", "NiAlphaProperty"),
                'description': '# Checking for Material (BGSM) Crash........ CULPRIT FOUND! > Priority : [3] #\n'},

            'NPC Pathing Crash (S)': {
                'error_conditions': "xxxxx", 'stack_conditions': ("NavMesh", "PathingCell", "BSPathBuilder", "PathManagerServer"),
                'description': '# Checking for NPC Pathing Crash (S)........ CULPRIT FOUND! > Priority : [3] #\n'},

            'NPC Pathing Crash (D)': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BSNavmeshObstacleData", "DynamicNavmesh", "PathingRequest"),
                'description': '# Checking for NPC Pathing Crash (D)........ CULPRIT FOUND! > Priority : [3] #\n'},

            'NPC Pathing Crash (F)': {
                'error_conditions': "+248B26A", 'stack_conditions': ("MovementAgentPathFollowerVirtual", "PathingStreamSaveGame", "BGSProcedurePatrolExecState", "CustomActorPackageData"),
                'description': '# Checking for NPC Pathing Crash (F)........ CULPRIT FOUND! > Priority : [3] #\n'},

            'Audio Driver Crash': {
                'error_conditions': ("X3DAudio1_7", "XAudio2_7"), 'stack_conditions': ("X3DAudio1_7.dll", "XAudio2_7.dll"),
                'description': '# Checking for Audio Driver Crash........... CULPRIT FOUND! > Priority : [5] #\n'},

            'Body Physics Crash': {
                'error_conditions': "cbp.dll", 'stack_conditions': ("skeleton.nif", "cbp.dll"),
                'description': '# Checking for Body Physics Crash........... CULPRIT FOUND! > Priority : [4] #\n'},

            'Leveled List Crash': {
                'error_conditions': "+0D09AB7", 'stack_conditions': "TESLevItem",
                'description': '# Checking for Leveled List Crash........... CULPRIT FOUND! > Priority : [3] #\n'},

            'Plugin Limit Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("[FF]", "BSMemStorage", "DataFileHandleReaderWriter"),
                'description': '# Checking for Plugin Limit Crash........... CULPRIT FOUND! > Priority : [5] #\n'},

            'Plugin Order Crash': {
                'error_conditions': "+0DB9300", 'stack_conditions': "GamebryoSequenceGenerator",
                'description': '# Checking for Plugin Order Crash........... CULPRIT FOUND! > Priority : [5] #\n'},

            'MO2 Extractor Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "BSD3DResourceCreator",
                'description': '# Checking for MO2 Extractor Crash.......... CULPRIT FOUND! > Priority : [3] #\n'},

            'Nvidia Debris Crash': {
                'error_conditions': ("+03EE452", "flexRelease_x64"), 'stack_conditions': ("flexRelease_x64.dll", "CheckRefAgainstConditionsFunc"),
                'description': '# Checking for Nvidia Debris Crash.......... CULPRIT FOUND! > Priority : [5] #\n'},

            'Nvidia Driver Crash': {
                'error_conditions': ("nvwgf2umx", "USER32"), 'stack_conditions': ("nvwgf2umx.dll", "USER32.dll"),
                'description': '# Checking for Nvidia Driver Crash.......... CULPRIT FOUND! > Priority : [5] #\n'},

            'Nvidia Reflex Crash': {
                'error_conditions': ("3A0000", "AD0000", "8E0000", "NVIDIA_Reflex", "Buffout4"), 'stack_conditions': "NVIDIA_Reflex.dll",
                'description': '# Checking for Nvidia Reflex Crash.......... CULPRIT FOUND! > Priority : [4] #\n'},

            'Vulkan Memory Crash': {
                'error_conditions': ("KERNELBASE", "MSVCP140"), 'stack_conditions': ("KERNELBASE.dll", "MSVCP140.dll", "DxvkSubmissionQueue"),
                'description': '# Checking for Vulkan Memory Crash.......... CULPRIT FOUND! > Priority : [4] #\n'},

            'Vulkan Settings Crash': {
                'error_conditions': ("+00CD99B", "amdvlk64"), 'stack_conditions': ("amdvlk64.dll", "dxvk::DXGIAdapter", "dxvk::DXGIFactory", "VirtualLinearAllocatorWithNode"),
                'description': '# Checking for Vulkan Settings Crash........ CULPRIT FOUND! > Priority : [5] #\n'},

            'Corrupted Audio Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BSXAudio2DataSrc", "BSXAudio2GameSound"),
                'description': '# Checking for Corrupted Audio Crash........ CULPRIT FOUND! > Priority : [4] #\n'},

            'Console Command Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("SysWindowCompileAndRun", "ConsoleLogPrinter"),
                'description': '# Checking for Console Command Crash........ CULPRIT FOUND! > Priority : [1] #\n'},

            'Game Corruption Crash': {
                'error_conditions': "+1B938F0", 'stack_conditions': ("AnimTextData\\AnimationFileData", "AnimationFileLookupSingletonHelper"),
                'description': '# Checking for Game Corruption Crash........ CULPRIT FOUND! > Priority : [5] #\n'},

            'Water Collision Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "BGSWaterCollisionManager",
                'description': '# Checking for Water Collision Crash........ CULPRIT FOUND! > Priority : [6] #\n [!] PLEASE CONTACT ME IF YOU GOT THIS CRASH! (CONTACT INFO BELOW)\n'},

            'Particle Effects Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "ParticleSystem",
                'description': '# Checking for Particle Effects Crash....... CULPRIT FOUND! > Priority : [4] #\n'},

            'Player Character Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("PlayerCharacter", "0x00000007", "0x00000008", "0x00000014"),
                'description': '# Checking for Player Character Crash....... CULPRIT FOUND! > Priority : [3] #\n'},

            'Animation / Physics Crash': {
                'error_conditions': "+1FCC07E", 'stack_conditions': ("BSAnimationGraphManager", "hkbVariableBindingSet", "hkbHandIkControlsModifier", "hkbBehaviorGraph", "hkbModifierList"),
                'description': '# Checking for Animation / Physics Crash.... CULPRIT FOUND! > Priority : [5] #\n'},

            'Archive Invalidation Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "DLCBanner05.dds",
                'description': '# Checking for Archive Invalidation Crash... CULPRIT FOUND! > Priority : [5] #\n'},

            # ================== LOW ACCURACY CULPRITS ===================

            '*[Creation Club Crash]': {
                'error_conditions': "+01B59A4", 'stack_conditions': "xxxxx",
                'description': '  Checking for *[Creation Club Crash]......... DETECTED! > Priority : [1] *\n'},

            '*[Item Crash]': {
                'error_conditions': "+0B2C44B", 'stack_conditions': ("TESObjectARMO", "TESObjectWEAP", "BGSMod::Attachment", "BGSMod::Template", "BGSMod::Template::Item"),
                'description': '  Checking for *[Item Crash].................. DETECTED! > Priority : [1] *\n'},

            '*[Save Crash]': {
                'error_conditions': "+0CDAD30", 'stack_conditions': ("BGSSaveLoadManager", "BGSSaveLoadThread", "BGSSaveFormBuffer"),
                'description': '  Checking for *[Save Crash].................. DETECTED! > Priority : [1] *\n'},

            '*[Input Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("ButtonEvent", "MenuControls", "MenuOpenCloseHandler", "PlayerControls", "DXGISwapChain"),
                'description': '  Checking for *[Input Crash]................. DETECTED! > Priority : [1] *\n'},

            '*[SS2 / WF Crash]': {
                'error_conditions': ("+01F498D", "+03F89A3"), 'stack_conditions': ("StartWorkshop", "IsWithinBuildableArea", "PlayerControls", "DXGISwapChain"),
                'description': '  Checking for *[SS2 / WF Crash].............. DETECTED! > Priority : [1] *\n'},

            '*[Looks Menu Crash]': {
                'error_conditions': ("+1D13DA7", "F4EE"), 'stack_conditions': ("BSShader", "BSBatchRenderer", "ShadowSceneNode"),
                'description': '  Checking for *[Looks Menu Crash]............ DETECTED! > Priority : [1] *\n'},

            '*[NPC Patrol Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSProcedurePatrol", "BGSProcedurePatrolExecState", "PatrolActorPackageData"),
                'description': '  Checking for *[NPC Patrol Crash]............ DETECTED! > Priority : [1] *\n'},

            '*[Precombines Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BSPackedCombined", "BGSCombinedCellGeometryDB", "BGSStaticCollection", "TESObjectCELL"),
                'description': '  Checking for *[Precombines Crash]........... DETECTED! > Priority : [1] *\n'},

            '*[GPU Overclock Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("myID3D11DeviceContext", "BSDeferredDecal", "BSDFDecal"),
                'description': '  Checking for *[GPU Overclock Crash]......... DETECTED! > Priority : [1] *\n'},

            '*[NPC Projectile Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSProjectile", "CombatProjectileAimController"),
                'description': '  Checking for *[NPC Projectile Crash]........ DETECTED! > Priority : [1] *\n'},

            '*[Camera Position Crash]': {
                'error_conditions': "NvCamera64", 'stack_conditions': ("NvCamera64.dll", "NiCamera", "WorldRoot Camera"),
                'description': '  Checking for *[Camera Position Crash]....... DETECTED! > Priority : [1] *\n'},

            '*[HUD / Interface Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': "HUDAmmoCounter",
                'description': '  Checking for *[HUD / Interface Crash]....... DETECTED! > Priority : [1] *\n'},
        }

        Special_Cases = {
            'Nvidia_Crashes': ['Nvidia Debris Crash', 'Nvidia Driver Crash', 'Nvidia Reflex Crash'],
            'Vulkan_Crashes': ['Vulkan Memory Crash', 'Vulkan Settings Crash'],
            'Player_Character_Crash': ['Player Character Crash']
        }

        def check_conditions(culprit_name, error_conditions, stack_conditions):
            if culprit_name in Special_Cases['Nvidia_Crashes']:
                return "nvidia" in logtext.lower() and any(item in section_stack_text for item in stack_conditions)
            elif culprit_name in Special_Cases['Vulkan_Crashes']:
                return "vulkan" in logtext.lower() and any(item in section_stack_text for item in stack_conditions)
            elif culprit_name in Special_Cases['Player_Character_Crash']:
                return any(section_stack_text.count(item) >= 3 for item in stack_conditions)
            else:
                return any(item in crash_error for item in error_conditions) or any(item in section_stack_text for item in stack_conditions)

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

    def process_file_data(file):
        logpath = Path(file).resolve()
        scanpath = logpath.with_name(logpath.stem + "-AUTOSCAN.md")
        logname = logpath.name
        logtext = logpath.read_text(encoding="utf-8", errors="ignore")

        with logpath.open(encoding="utf-8", errors="ignore") as f:
            loglines = f.readlines()

        loglines = list(map(str.strip, loglines))

        return logpath, scanpath, logname, logtext, loglines

    # ==================== AUTOSCAN REPORT ====================
    print("PERFORMING SCAN... \n")
    statL_scanned = statL_incomplete = statL_failed = statM_CHW = 0
    start_time = time.perf_counter()

    SCAN_folder = os.getcwd()
    if len(UNIVERSE.CLAS_config["MAIN"]["Scan Path"]) > 1:
        SCAN_folder = UNIVERSE.CLAS_config["MAIN"]["Scan Path"]

    if UNIVERSE.CLAS_config["MAIN"]["FCX Mode"].lower() == "true":
        from CLAS_ScanFiles import (scan_game_files, scan_mod_inis,
                                    scan_wryecheck)
        GALAXY.scan_game_report = []
        scan_game_files()
        scan_wryecheck()
        scan_mod_inis()

    for file in glob(f"{SCAN_folder}/crash-*.log"):
        logpath, scanpath, logname, logtext, loglines = process_file_data(file)  # logpath doesn't seem to be used anywhere besides generating scanpath, keeping it in case it's needed later.

        with scanpath.open("w", encoding="utf-8", errors="ignore") as output:
            output.writelines([f"{logname} | Scanned with Crash Log Auto Scanner (CLAS) version {UNIVERSE.CLAS_Current[-4:]} \n",
                               "# FOR BEST VIEWING EXPERIENCE OPEN THIS FILE IN NOTEPAD++ | BEWARE OF FALSE POSITIVES # \n",
                               "====================================================\n"])
            # DEFINE LINE INDEXES HERE
            crash_ver = loglines[1].strip()
            crash_error = loglines[2].strip() if loglines[2] and not loglines[2] == "\n" else loglines[3].strip()
            assert len(crash_error) > 0

            section_stack_list, section_stack_text, section_plugins_list, plugins_loaded = process_log_sections(loglines)

            # BUFFOUT VERSION CHECK
            output.writelines([f"Main Error: {crash_error}\n",
                               "====================================================\n",
                               f"Detected Buffout Version: {crash_ver.strip()}\n",
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

            if UNIVERSE.CLAS_config["MAIN"]["FCX Mode"].lower() == "true":
                output.write(GALAXY.Warnings["Warn_SCAN_FCX_Enabled"])
                for item in GALAXY.scan_game_report:
                    output.write(f"{item}\n")
            else:
                output.write(GALAXY.Warnings["Warn_SCAN_FCX_Disabled"])
                # CHECK BUFFOUT 4 TOML SETTINGS IN CRASH LOG ONLY
                if ("Achievements: true" in logtext and "achievements.dll" in logtext) or ("Achievements: true" in logtext and "UnlimitedSurvivalMode.dll" in logtext):
                    output.write(GALAXY.Warnings["Warn_TOML_Achievements"])
                else:
                    output.write("✔️ Achievements parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

                if "MemoryManager: true" in logtext and "BakaScrapHeap.dll" in logtext:
                    output.write(GALAXY.Warnings["Warn_TOML_Memory"])
                else:
                    output.write("✔️ Memory Manager parameter in *Buffout4.toml* is correctly configured.\n  -----\n")

                if "F4EE: false" in logtext and "f4ee.dll" in logtext:
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
            gpu_nvidia = any("GPU" in line and "Nvidia" in line for line in loglines)
            gpu_amd = any("GPU" in line and "AMD" in line for line in loglines) if not gpu_nvidia else False
            gpu_other = True if not gpu_nvidia and not gpu_amd else False  # INTEL GPUs & Other Undefined
            assert not (gpu_nvidia and gpu_amd), "❌ ERROR : Both GPU types detected in the log file!"

            # =================== CRASH CULPRITS CHECK ==================
            Culprit_Trap = culprit_check(output, logtext, section_stack_text)

            if Culprit_Trap is False:  # DEFINE CHECK IF NO KNOWN CRASH ERRORS / CULPRITS ARE FOUND
                output.writelines(["# AUTOSCAN FOUND NO CRASH ERRORS / CULPRITS THAT MATCH THE CURRENT DATABASE #\n",
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

                for line in section_plugins_list:
                    for mod_name, mod_data in mods.items():
                        if "File:" not in line and mod_data["mod"] in line and mod_data["mod"] not in LCL_skip_list:
                            warn = ''.join(mod_data["warn"])
                            prefix = line[0:5].strip() if "[FE" not in line else line[0:9].strip()
                            output.writelines([f"[!] Found: {prefix} {warn}\n", "-----\n"])
                            mod_trap = True

                return mod_trap

            def check_conflicts(mods, mod_trap, plugins_loaded, logtext):
                if not plugins_loaded:
                    return mod_trap

                for mod_data in mods.values():
                    if mod_data["mod_1"] in logtext and mod_data["mod_2"] in logtext:
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
                    output.writelines(["# AUTOSCAN FOUND MODS THAT ARE INCOMPATIBLE OR CONFLICT WITH YOUR OTHER MODS # \n",
                                       "* YOU SHOULD CHOOSE WHICH MOD TO KEEP AND REMOVE OR DISABLE THE OTHER MOD * \n",
                                       "-----\n"])
                elif (Mod_Check2 and Mod_Trap2) is False:
                    output.writelines(["# AUTOSCAN FOUND NO MODS THAT ARE INCOMPATIBLE OR CONFLICT WITH YOUR OTHER MODS #\n",
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

                if any(item in logtext for item in thuggy_smurf_mods):
                    output.writelines([f"[!] Found: [XX] THUGGYSMURF QUEST MOD(S)\n",
                                       "If you have Depravity, Fusion City Rising, HOTC, Outcasts and Remnants and/or Project Valkyrie\n",
                                       "install this patch with facegen data, fully generated precomb/previs data and several tweaks.\n",
                                       "Patch Link: https://www.nexusmods.com/fallout4/mods/56876?tab=files\n",
                                       "-----\n"])
                    found = True

                if any(item in logtext for item in custom_race_mods):
                    output.writelines([f"[!] Found: [XX] CUSTOM RACE SKELETON MOD(S)\n",
                                       "If you have AnimeRace NanakoChan or Crimes Against Nature, install the Race Skeleton Fixes.\n",
                                       "Skeleton Fixes Link (READ THE DESCRIPTION): https://www.nexusmods.com/fallout4/mods/56101\n"])
                    found = True

                if "FallSouls.dll" in logtext:
                    output.writelines([f"[!] Found: FALLSOULS UNPAUSED GAME MENUS\n",
                                       "Occasionally breaks the Quests menu, can cause crashes while changing MCM settings.\n",
                                       "Advised Fix: Toggle PipboyMenu in FallSouls MCM settings or completely reinstall the mod.\n",
                                       "-----\n"])
                    found = True

                return found

            Mod_Trap3 = False
            if plugins_loaded:
                Mod_Check3 = check_plugins(MOON.Mods3, Mod_Trap3, plugins_loaded, section_plugins_list, LCL_skip_list)

                # =============== SPECIAL MOD / PLUGIN CHECKS ===============
                Mod_Trap3 = check_special_mods_with_solutions(logtext, output)

                if Mod_Check3 or Mod_Trap3 is True:
                    output.writelines([f"# AUTOSCAN FOUND PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
                                       "[Due to limitations, CLAS will show warnings for some mods even if fixes or patches are already installed.]\n",
                                       "[To hide these warnings, you can add their plugin names to the CLAS Ignore.txt file. ONE PLUGIN PER LINE.]\n",
                                       "-----\n"])
                elif Mod_Check3 and Mod_Trap3 is False:
                    output.writelines([f"# AUTOSCAN FOUND NO PROBLEMATIC MODS WITH SOLUTIONS AND COMMUNITY PATCHES #\n",
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
                    output.writelines(["# AUTOSCAN FOUND NO PROBLEMATIC MODS THAT ARE ALREADY PATCHED THROUGH OPC INSTALLER #\n",
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

            list_records = extract_named_records(section_stack_list, UNIVERSE.Crash_Records_Catch, GALAXY.Crash_Records_Exclude)

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

        if file_move and UNIVERSE.CLAS_config.getboolean("MAIN", "Move Unsolved"):
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
    if isinstance(args.fcx_mode, bool) and not args.fcx_mode == UNIVERSE.CLAS_config.getboolean("MAIN", "FCX Mode"):
        clas_ini_update("FCX Mode", str(args.fcx_mode).lower())

    if isinstance(args.imi_mode, bool) and not args.imi_mode == UNIVERSE.CLAS_config.getboolean("MAIN", "IMI Mode"):
        clas_ini_update("IMI Mode", str(args.imi_mode).lower())

    if isinstance(args.stat_logging, bool) and not args.stat_logging == UNIVERSE.CLAS_config.getboolean("MAIN", "Stat Logging"):
        clas_ini_update("Stat Logging", str(args.stat_logging).lower())

    if isinstance(args.move_unsolved, bool) and not args.move_unsolved == UNIVERSE.CLAS_config.getboolean("MAIN", "Move Unsolved"):
        clas_ini_update("Move Unsolved", str(args.move_unsolved).lower())

    if isinstance(ini_path, Path) and ini_path.resolve().is_dir() and not str(ini_path) == UNIVERSE.CLAS_config["MAIN"]["INI Path"]:
        clas_ini_update("INI Path", str(Path(ini_path).resolve()))

    if isinstance(scan_path, Path) and scan_path.resolve().is_dir() and not str(scan_path) == UNIVERSE.CLAS_config["MAIN"]["Scan Path"]:
        clas_ini_update("Scan Path", str(Path(scan_path).resolve()))

    scan_logs()
    os.system("pause")
