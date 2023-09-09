=====================================================================================================
# CLASSIC CHANGELOG #

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
- *Simlify Logs* setting that removes some useless and redundant lines from crash log files.
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