=====================================================================================================
# CLASSIC CHANGELOG #

7.20
*NEW FEATURES*
- CLASSIC now automatically creates backups of your game's main EXE files.
- CLASSIC now automatically checks for F4SE updates from the official website.
- Added hash checks for Script Extender files from the VR version of the game.
- Added the Address Library file check (required for Script Extender and some mods).
- CLASSIC now checks if given folder for the INI path actually exists before adding it.
- Added options to Backup / Restore / Remove files from *ENB, Reshade and Vulkan Renderer*
[These options are located under the new tab in the CLASSIC interface. See Readme PDF for details].
- All invalid crash logs and file backups are now stored and separated into *CLASSIC Backup* folder.

*CHANGES*
- *Crash Logs Scan* is now ~25% faster.
- Improved visuals of interface popup boxes.
- Re-centered a few misaligned interface elements.
- Updated BethINI link to the new BethINI PIE version.
- Additional fixes for Fallout 4 VR file and folder paths detection.
- Converted CLASSIC Readme to PDF with better formatting and more info.
- Fixed crash log files not being excluded from general log files error search.
- Fixed incorrect detection of Script Extender file copies during *Game Files Scan*.
- Fixed an issue where certain plugins were not detected under *Possible Plugin Suspects*.

7.10
*NEW FEATURES*
- CLASSIC will now extract required files from *CLASSIC Data.zip* if they are not found.
- Default *Fallout4Custom.ini* settings are now accessible through *CLASSIC FO4.yaml*
[These settings will be auto generated if Fallout4Custom.ini doesn't already exist.]

*CHANGES*
- The CLASSIC interface has a brand new look.
- Fixed *AttributeError* in the mod_ini_config().
- Fixed some minor formatting bugs for *-AUTOSCAN.md* files.
- Fixed incorrect generation of Fallout 4 VR file and folder paths.
- Updated *CLASSIC Readme* with explanations for all of the new features.
- CLASSIC now keeps AUTOSCAN report files in the same folder with their crash logs.
- Changed the file structure, now all required files are organized inside *CLASSIC Data* folder.
[Please report if it still fails to generate your Fallout 4 VR file and folder paths in CLASSIC FO4VR.yaml]

7.07 | "Everything Everywhere All At Once" Update
*NEW FEATURES*
- CLASSIC will automatically check for its own updates every 7 days.
- CLASSIC will warn you if MS OneDrive is overriding your Documents folder location.
- CLASSIC will automatically grab all crash log files from the Script Extender folder.
- CLASSIC will play a short notification sound once crash logs and game file scans are done.
- Various CLASSIC settings were moved to YAML files for much easier access and editing.
- Various CLASSIC functions and tasks are now automatically logged to *CLASSIC Journal.log*
- Extended scan support for crash logs from new and old Buffout 4 versions.
- Extended compatibility and features for Virtual Reality (VR) version of the game.
- *VR Mode* setting that will prioritize scanning files from the VR version of the game.
- *Simplify Logs* setting that removes some useless and redundant lines from crash log files.
- *Show FID Values* setting that will look up FormID values for Possible FormID Suspects.
- Papyrus Log monitoring built into the GUI. Also plays a warning sound when things go bad.
- Buttons for quick access to the DDS Texture Scanner, Wrye Bash and BethINI Nexus pages.
- Ability to scan all mod files from your Staging Mods Folder to detect these issues:
	> Check if DDS texture file dimensons are not divisible by 2 (Ex. 1024 x 1025)
	> Check if texture files are in the wrong format (TGA or PNG instead of DDS)
	> Check if sound files are in the wrong format (MP3 or M4A instead of XWM or WAV)
	> Check which mods have custom precombine / previs data (so you can load them after PRP)
	> Check which mods have custom animation file data (to narrow down Animation Data Crashes)
	> Check which mods have copies of Script Extender files (to prevent problems and crashes)
- Mod files scan will also move any found fomod and readme files to the CLASSIC Misc folder.
- You can also generate FormID values for all active mods, so AUTOSCAN reports can use them.
- AUTOSCAN reports will now additionally provide the following information:
	> List all mod INI files and settings that have enabled game *VSync*, if any.
	> Show how many times each Possible FormID Suspect appears in the crash log.
	> Warn you if *Fallout4.ini, Fallout4Prefs.ini or Fallout4Custom.ini* become corrupted.
	> Notify you when Buffout 4 fixes in the TOML config file get changed or disabled.
	> Show an additional warning if you went over the Plugin Limit (254 esm/esp).

*CHANGES*
- Complete code rewrite that will make all future versions much more stable and expandable.
- *Game Corruption Crash* renamed to *Animation Data Crash*, crash info has been updated.
- Several code optimizations thanks to [evildarkarchon] on GitHub, plus many bugs squashed.
- Added few redundant / irrelevant errors to the internal exclusion list so they are ignored.