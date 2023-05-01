import json

input_dict = {
            'Stack Overflow Crash': {
                'error_conditions': "EXCEPTION_STACK_OVERFLOW", 'stack_conditions': "xxxxx",
                'description': '# Checking for Stack Overflow Crash......... CULPRIT FOUND! > Severity : [5] #\n'},

            'Active Effects Crash': {
                'error_conditions': "0x000100000000", 'stack_conditions': "xxxxx",
                'description': '# Checking for Active Effects Crash......... CULPRIT FOUND! > Severity : [5] #\n'},

            'Bad Math Crash': {
                'error_conditions': "EXCEPTION_INT_DIVIDE_BY_ZERO", 'stack_conditions': "xxxxx",
                'description': '# Checking for Bad Math Crash............... CULPRIT FOUND! > Severity : [5] #\n'},

            'Null Crash': {
                'error_conditions': "0x000000000000", 'stack_conditions': "xxxxx",
                'description': '# Checking for Null Crash................... CULPRIT FOUND! > Severity : [5] #\n'},

            # ====================== STACK CULPRITS ======================

            'DLL Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "DLCBannerDLC01.dds",
                'description': '# Checking for DLL Crash.................... CULPRIT FOUND! > Severity : [5] #\n'},

            'LOD Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSLocation", "BGSQueuedTerrainInitialLoad"),
                'description': '# Checking for LOD Crash.................... CULPRIT FOUND! > Severity : [5] #\n'},

            'MCM Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("FaderData", "FaderMenu", "UIMessage"),
                'description': '# Checking for MCM Crash.................... CULPRIT FOUND! > Severity : [3] #\n'},

            'Decal Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSDecalManager", "BSTempEffectGeometryDecal"),
                'description': '# Checking for Decal Crash.................. CULPRIT FOUND! > Severity : [5] #\n'},

            'Equip Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "PipboyMapData",
                'description': '# Checking for Equip Crash.................. CULPRIT FOUND! > Severity : [3] #\n'},

            'Script Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("Papyrus", "VirtualMachine", "Assertion failed"),
                'description': '# Checking for Script Crash................. CULPRIT FOUND! > Severity : [3] #\n'},

            'Generic Crash': {
                'error_conditions': "tbbmalloc", 'stack_conditions': "xxxxx",
                'description': '# Checking for Generic Crash................ CULPRIT FOUND! > Severity : [2] #\n'},

            'Antivirus Crash': {
                'error_conditions': ("24A48D48", "bdhkm64.dll"), 'stack_conditions': ("usvfs::hook_DeleteFileW", "::Manager", "::zlibStreamDetail"),
                'description': '# Checking for Antivirus Crash.............. CULPRIT FOUND! > Severity : [5] #\n'},

            'BA2 Limit Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "LooseFileAsyncStream",
                'description': '# Checking for BA2 Limit Crash.............. CULPRIT FOUND! > Severity : [5] #\n'},

            'Rendering Crash': {
                'error_conditions': "d3d11", 'stack_conditions': "xxxxx",
                'description': '# Checking for Rendering Crash.............. CULPRIT FOUND! > Severity : [4] #\n'},

            'C++ Redist Crash': {
                'error_conditions': ("MSVCR", "MSVCP"), 'stack_conditions': "xxxxx",
                'description': '# Checking for C++ Redist Crash............. CULPRIT FOUND! > Severity : [3] #\n'},

            'Grid Scrap Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("GridAdjacencyMapNode", "PowerUtils"),
                'description': '# Checking for Grid Scrap Crash............. CULPRIT FOUND! > Severity : [5] #\n'},

            'Map Marker Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("HUDCompass", "HUDCompassMarker", "attachMovie()"),
                'description': '# Checking for Map Marker Crash............. CULPRIT FOUND! > Severity : [5] #\n'},

            'Mesh (NIF) Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("LooseFileStream", "BSFadeNode", "BSMultiBoundNode"),
                'description': '# Checking for Mesh (NIF) Crash............. CULPRIT FOUND! > Severity : [4] #\n'},

            'Texture (DDS) Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("Create2DTexture", "DefaultTexture"),
                'description': '# Checking for Texture (DDS) Crash.......... CULPRIT FOUND! > Severity : [4] #\n'},

            'Material (BGSM) Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("DefaultTexture_Black", "NiAlphaProperty"),
                'description': '# Checking for Material (BGSM) Crash........ CULPRIT FOUND! > Severity : [3] #\n'},

            'NPC Pathing Crash (S)': {
                'error_conditions': "xxxxx", 'stack_conditions': ("NavMesh", "PathingCell", "BSPathBuilder", "PathManagerServer"),
                'description': '# Checking for NPC Pathing Crash (S)........ CULPRIT FOUND! > Severity : [3] #\n'},

            'NPC Pathing Crash (D)': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BSNavmeshObstacleData", "DynamicNavmesh", "PathingRequest"),
                'description': '# Checking for NPC Pathing Crash (D)........ CULPRIT FOUND! > Severity : [3] #\n'},

            'NPC Pathing Crash (F)': {
                'error_conditions': "+248B26A", 'stack_conditions': ("MovementAgentPathFollowerVirtual", "PathingStreamSaveGame", "BGSProcedurePatrolExecState", "CustomActorPackageData"),
                'description': '# Checking for NPC Pathing Crash (F)........ CULPRIT FOUND! > Severity : [3] #\n'},

            'Audio Driver Crash': {
                'error_conditions': ("X3DAudio1_7", "XAudio2_7"), 'stack_conditions': ("X3DAudio1_7.dll", "XAudio2_7.dll"),
                'description': '# Checking for Audio Driver Crash........... CULPRIT FOUND! > Severity : [5] #\n'},

            'Body Physics Crash': {
                'error_conditions': "cbp.dll", 'stack_conditions': ("skeleton.nif", "cbp.dll"),
                'description': '# Checking for Body Physics Crash........... CULPRIT FOUND! > Severity : [4] #\n'},

            'Leveled List Crash': {
                'error_conditions': "+0D09AB7", 'stack_conditions': "TESLevItem",
                'description': '# Checking for Leveled List Crash........... CULPRIT FOUND! > Severity : [3] #\n'},

            'Plugin Limit Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("[FF]", "BSMemStorage", "DataFileHandleReaderWriter"),
                'description': '# Checking for Plugin Limit Crash........... CULPRIT FOUND! > Severity : [5] #\n'},

            'Plugin Order Crash': {
                'error_conditions': "+0DB9300", 'stack_conditions': "GamebryoSequenceGenerator",
                'description': '# Checking for Plugin Order Crash........... CULPRIT FOUND! > Severity : [5] #\n'},

            'MO2 Extractor Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "BSD3DResourceCreator",
                'description': '# Checking for MO2 Extractor Crash.......... CULPRIT FOUND! > Severity : [3] #\n'},

            'Nvidia Debris Crash': {
                'error_conditions': ("+03EE452", "flexRelease_x64"), 'stack_conditions': ("flexRelease_x64.dll", "CheckRefAgainstConditionsFunc"),
                'description': '# Checking for Nvidia Debris Crash.......... CULPRIT FOUND! > Severity : [5] #\n'},

            'Nvidia Driver Crash': {
                'error_conditions': ("nvwgf2umx", "USER32"), 'stack_conditions': ("nvwgf2umx.dll", "USER32.dll"),
                'description': '# Checking for Nvidia Driver Crash.......... CULPRIT FOUND! > Severity : [5] #\n'},

            'Nvidia Reflex Crash': {
                'error_conditions': ("3A0000", "AD0000", "8E0000", "NVIDIA_Reflex", "Buffout4"), 'stack_conditions': "NVIDIA_Reflex.dll",
                'description': '# Checking for Nvidia Reflex Crash.......... CULPRIT FOUND! > Severity : [4] #\n'},

            'Vulkan Memory Crash': {
                'error_conditions': ("KERNELBASE", "MSVCP140"), 'stack_conditions': ("KERNELBASE.dll", "MSVCP140.dll", "DxvkSubmissionQueue"),
                'description': '# Checking for Vulkan Memory Crash.......... CULPRIT FOUND! > Severity : [4] #\n'},

            'Vulkan Settings Crash': {
                'error_conditions': ("+00CD99B", "amdvlk64"), 'stack_conditions': ("amdvlk64.dll", "dxvk::DXGIAdapter", "dxvk::DXGIFactory", "VirtualLinearAllocatorWithNode"),
                'description': '# Checking for Vulkan Settings Crash........ CULPRIT FOUND! > Severity : [5] #\n'},

            'Corrupted Audio Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BSXAudio2DataSrc", "BSXAudio2GameSound"),
                'description': '# Checking for Corrupted Audio Crash........ CULPRIT FOUND! > Severity : [4] #\n'},

            'Console Command Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("SysWindowCompileAndRun", "ConsoleLogPrinter"),
                'description': '# Checking for Console Command Crash........ CULPRIT FOUND! > Severity : [1] #\n'},

            'Game Corruption Crash': {
                'error_conditions': "+1B938F0", 'stack_conditions': ("AnimTextData\\AnimationFileData", "AnimationFileLookupSingletonHelper"),
                'description': '# Checking for Game Corruption Crash........ CULPRIT FOUND! > Severity : [5] #\n'},

            'Water Collision Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "BGSWaterCollisionManager",
                'description': '# Checking for Water Collision Crash........ CULPRIT FOUND! > Severity : [6] #\n [!] PLEASE CONTACT ME IF YOU GOT THIS CRASH! (CONTACT INFO BELOW)\n'},

            'Particle Effects Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "ParticleSystem",
                'description': '# Checking for Particle Effects Crash....... CULPRIT FOUND! > Severity : [4] #\n'},

            'Player Character Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': ("PlayerCharacter", "0x00000007", "0x00000008", "0x00000014"),
                'description': '# Checking for Player Character Crash....... CULPRIT FOUND! > Severity : [3] #\n'},

            'Animation / Physics Crash': {
                'error_conditions': "+1FCC07E", 'stack_conditions': ("BSAnimationGraphManager", "hkbVariableBindingSet", "hkbHandIkControlsModifier", "hkbBehaviorGraph", "hkbModifierList"),
                'description': '# Checking for Animation / Physics Crash.... CULPRIT FOUND! > Severity : [5] #\n'},

            'Archive Invalidation Crash': {
                'error_conditions': "xxxxx", 'stack_conditions': "DLCBanner05.dds",
                'description': '# Checking for Archive Invalidation Crash... CULPRIT FOUND! > Severity : [5] #\n'},

            # ================== LOW ACCURACY CULPRITS ===================

            '*[Creation Club Crash]': {
                'error_conditions': "+01B59A4", 'stack_conditions': "xxxxx",
                'description': '  Checking for *[Creation Club Crash]......... DETECTED! > Severity : [1] *\n'},

            '*[Item Crash]': {
                'error_conditions': "+0B2C44B", 'stack_conditions': ("TESObjectARMO", "TESObjectWEAP", "BGSMod::Attachment", "BGSMod::Template", "BGSMod::Template::Item"),
                'description': '  Checking for *[Item Crash].................. DETECTED! > Severity : [1] *\n'},

            '*[Save Crash]': {
                'error_conditions': "+0CDAD30", 'stack_conditions': ("BGSSaveLoadManager", "BGSSaveLoadThread", "BGSSaveFormBuffer"),
                'description': '  Checking for *[Save Crash].................. DETECTED! > Severity : [1] *\n'},

            '*[Input Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("ButtonEvent", "MenuControls", "MenuOpenCloseHandler", "PlayerControls", "DXGISwapChain"),
                'description': '  Checking for *[Input Crash]................. DETECTED! > Severity : [1] *\n'},

            '*[SS2 / WF Crash]': {
                'error_conditions': ("+01F498D", "+03F89A3"), 'stack_conditions': ("StartWorkshop", "IsWithinBuildableArea", "PlayerControls", "DXGISwapChain"),
                'description': '  Checking for *[SS2 / WF Crash].............. DETECTED! > Severity : [1] *\n'},

            '*[Looks Menu Crash]': {
                'error_conditions': ("+1D13DA7", "F4EE"), 'stack_conditions': ("BSShader", "BSBatchRenderer", "ShadowSceneNode"),
                'description': '  Checking for *[Looks Menu Crash]............ DETECTED! > Severity : [1] *\n'},

            '*[NPC Patrol Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSProcedurePatrol", "BGSProcedurePatrolExecState", "PatrolActorPackageData"),
                'description': '  Checking for *[NPC Patrol Crash]............ DETECTED! > Severity : [1] *\n'},

            '*[Precombines Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BSPackedCombined", "BGSCombinedCellGeometryDB", "BGSStaticCollection", "TESObjectCELL"),
                'description': '  Checking for *[Precombines Crash]........... DETECTED! > Severity : [1] *\n'},

            '*[GPU Overclock Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("myID3D11DeviceContext", "BSDeferredDecal", "BSDFDecal"),
                'description': '  Checking for *[GPU Overclock Crash]......... DETECTED! > Severity : [1] *\n'},

            '*[NPC Projectile Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': ("BGSProjectile", "CombatProjectileAimController"),
                'description': '  Checking for *[NPC Projectile Crash]........ DETECTED! > Severity : [1] *\n'},

            '*[Camera Position Crash]': {
                'error_conditions': "NvCamera64", 'stack_conditions': ("NvCamera64.dll", "NiCamera", "WorldRoot Camera"),
                'description': '  Checking for *[Camera Position Crash]....... DETECTED! > Severity : [1] *\n'},

            '*[HUD / Interface Crash]': {
                'error_conditions': "xxxxx", 'stack_conditions': "HUDAmmoCounter",
                'description': '  Checking for *[HUD / Interface Crash]....... DETECTED! > Severity : [1] *\n'},
        }

with open('crash_culprits.json', 'w') as fp:
    json.dump(input_dict, fp, indent=4)