=====================================================================================================
# CHANGELOG #

6.85
- Some mod warnings for *MODS THAT CAN CAUSE FREQUENT CRASHES* have been adjusted and/or removed.
- CLAS will now warn you if Nvidia specific mods are installed, but AMD video card was detected.
- Game Files scan will now warn you if the game is installed inside of *Program Files* folder.
- Game Files scan will now analyze F4SE script file hashes and warn you if any are corrupted.
- Game Files scan will now analyze INI files from mods and make adjustments when necessary.
- [If using MO2, make sure to run CLAS within MO2 (create shortcut) for this to work.]

* OTHER FILES *
- General minor changes and additions to *CLAS Readme*.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.

6.77
- CLAS will now analyze the Plugin Checker report from Wrye Bash while *FCX Mode = true*.
- Game Files scan will now show whether Archive Invalidation is already enabled or not.
- Fixed detection for *DETECTED (NAMED) RECORDS* which broke in the previous update.
- Fixed detection for *IMPORTANT PATCHES & FIXES* which also broke for some mods.
- Adjusted Nvidia specific error messages so they never appear for AMD cards.
- Articles / Websites buttons are now visually a bit larger in the GUI.

6.70
- Fixed detection for most error messages in *KNOWN CRASH CULPRITS*.
- Fixed CLAS update messages not showing up under certain conditions.
- Adjusted detection for *Vulkan Memory Crash* to prevent false positives.

- You can now ignore mods by adding their plugin names to *CLAS Ignore.txt*
- [Ignored mods will not show any warnings in CLAS. ONE PLUGIN PER LINE]
- [Ignored mods will still show up if there are serious mod conflicts.]

6.66 | "No Step On Snek" Update
* MAIN SCRIPT *
- Various parity updates between *Crash Log Auto Scanner* and *Plugin Auto Cleaning Tool*
- Reformatted and standardized most of the code for easier additions and porting functionality.
- Buffout 4 NG/VR will now be the recommended Buffout version by default until further notice.
- Fixed missing Scripts folder crash that occured if F4SE wasn't already manually installed.
- Keybind errors from *xSE PluginPreloader.log* are now excluded to prevent false positives.
- Creation Kit logs are now excluded from error detection to prevent false positives.
- Removed F4SE check for crash logs as this became redundant with game files check.
- Improved detection for some crash culprits and adjusted report formatting style.
- Added detection for *.dll* files for the *List Of Detected (Named) Records*.
- [Log and culprit stats are currently disabled until a better method is found.]

* OTHER FILES *
- Renamed INI file for adjusting *Crash Log Auto Scanner* settings to *CLAS Settings.ini*
- Removed python requirements and other related python warnings from the CLAS executable.
- Raw scripts are no longer included with CLAS files on Nexus, they are now exlusive to GitHub.
- [You can still find the raw scripts on CLAS Github page, they're not required to run the EXE.]

6.55
* MAIN SCRIPT *
- Fixed incorrect Fallout 4 VR Documents file path, should also resolve all false positives.
- Updated version check for Buffout 4 NG / VR [ Buffout4 v1.31.1 Feb 28 2023 00:28:17 ].
- Improved detection accuracy for *Vulkan Settings Crash*, crash info has been updated.
- Auto-Scanner will now show the full error line along with its related log file path.
- Added detection for *VR Address Library For F4SEVR* for the VR version of the game.

* CLAS GUI *
- Added the classic *Minimize* button to the main program window.

6.50
* MAIN SCRIPT *
- HOTFIX : MaxStdIO value will be now set to 2048 (instead of 8192), to prevent game crashes.

6.45
* MAIN SCRIPT *
- Auto-Scanner now checks the MaxStdIO value in *Buffout4.toml* and will warn you if it needs adjusting.
- Expanded *Buffout4.toml* checks to cover more valid settings and prevent false positive warnings.
- Fixed wrong message being sometimes incorrectly displayed when no crash culprits are found.
- Various fixes and adjustments for the detection of mods that conflict with other mods.
- Moved all *Classic Holstered Weapons* conflict warnings to the relevant segment.
- Implemented hash based check for *Fallout4.exe* for better accuracy.

* OTHER FILES *
- *CL TOOLS* folder renamed to *CLAS TOOLS*
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.

6.35
* MAIN SCRIPT *
- General code optimization for statistics logging, fixed minor stat tracking issues.
- Fixed Auto-Scanner scanning the wrong folder when looking for dll log errors.
- Fixed the FormType error / crash due to some weird output & text parsing.
- Adjusted *Plugin Limit Crash* detection to prevent false positives.
- Added detection for 5 new mods that conflict with other mods.
- Added detection for the following crash types:
> Nvidia Reflex Crash
> *[SS2 / WF Crash]
> *[Camera Position Crash]

* OTHER FILES *
- Upgraded the EXE interface to use PyQt6 / PySide6 thanks to [evildarkarchon] on GitHub.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.

6.25
* MAIN SCRIPT *
- Adjusted all warning / caution messages to show up only when their specific conditions are met.
- Auto-Scanner now checks for reported errors in log files located in the Fallout 4 root folder.
- Auto-Scanner now checks the *Fallout4.exe* version which will be useful at a later date.
- Auto-Scanner now checks if all required F4SE script files are found and accounted for.
- Auto-Scanner should now correctly warn you if your current Python version is older than *3.9*.
- Added a new segment named *CHECKING FOR MODS THAT CONFLICT WITH OTHER MODS*
- Moved all local Fallout 4 & Buffout 4 file checks to a separate script *Scan_Gamefiles.py*.
[You can run Scan_Gamefiles.py yourself to get a report about file warnings and suggestions.]
[Changing IMI Mode to true in Scan Crashlogs.ini will ignore some warnings for convenience.]

* CLAS GUI *
- Added *Scan Game Files* button that runs previously mentioned *Scan_Gamefiles.py* script.
- Slight adjustments to some options and text positions, added some basic instructions.

6.11
* MAIN SCRIPT *
- Fixed an issue where Auto-Scanner would do the opposite of intended while *Move Unsolved = true*.
- Auto-Scanner should now warn you when trying to scan *.txt* crash logs (only *.log* are allowed).
- Expanded exception parameters when *Fallout4Custom.ini* cannot be automatically modified.
- Fixed the timing for *Scanned all available logs in X seconds* while using the GUI.
- Changed *Bitdefender Crash* to *Antivirus Crash*, crash info has been updated.
- Update checks are now skipped entirely if any error occurs to prevent crashes.
- Adjusted text and updated links for some detected mods and plugins.
- Added detection for functions for the *List Of Detected (Named) Records*.
- Added detection for *NPC Pathing Crash* caused by followers / companions.
- Added detection for the *[GPU Overclock Crash]* | Expect false positives.
[Crash info was already listed, but detection wasn't implemented until now.]

* CLAS GUI *
- General code optimization and cleanup to resolve / suppress various IDE warnings.
- Now merged both scripts into the EXE, this should prevent some specific crashes.

* OTHER FILES *
- General improvements to *CL Compare.py* thanks to [evildarkarchon] on GitHub.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.

6.06
* MAIN SCRIPT *
- Added *IMI Mode* to Auto-Scanner INI settings, which allows you to ignore / hide manual installation warnings.
- Fixed Auto-Scanner saving *-AUTOSCAN.md* files in the root folder instead of any custom set path.
- Fixed all instances of duplicate text in the terminal due to recent code changes.
- Fixed the update check function for the 6th and last time.

* CLAS GUI *
- Fixed INI settings not updating immedialtely on first launch thanks to [evildarkarchon] on GitHub.
- Fixed *Check For Updates* so it no longer warns about an update if you have the latest version.

6.00 | Major Update | The GUI is here!
* MAIN SCRIPT *
- Fixed a major problem in code logic that made Auto-Scanner fail to detect some crash messages / errors.
- Fixed an issue where Auto-Scanner would sometimes look for Buffout 4 files even if they didn't exist.
- Fixed an issue where load order from provided *loadorder.txt* would be sometimes completely ignored.
- Fixed an issue where Auto-Scanner sometimes failed to detect *Precombines Crash* messages / errors.
- Fixed wrong link given for *Previs Repair Pack*, it was linking to *High FPS Physics Fix* instead.
- Fixed several issues where Auto-Scanner would sometimes fail to scan logs due to unicode errors.
- Fixed an issue where Auto-Scanner sometimes failed to install / detect required Python modules.
- Fixed and optimized the update check code, fingers crossed it doesn't break anything again...
- Merged detection for *[Bad INI Crash]* with the *[Save Crash]*, crash info has been updated.
- Added a warning message when Auto-Scanner detects *Fallout4Custom.ini* file corruption.
- Improved detection accuracy for *Weapon Debris Crash* and *NPC Pathing Crash*.
- Readjusted a couple of crash message / error prioritiy designations.
- Added counters for detected *Form IDs* and *Named Records*.
- Added support for VR (Virtual Reality) crash logs.
- Added detection for the following crash types:
> *Game Corruption Crash*
> *Leveled List Crash*
> *[Looks Menu Crash]*

- These crash messages / errors are no longer Unsolved, crash info has been updated:
> *Player Character Crash*
> *Precombines Crash*

* OTHER FILES *
- Crash Log Auto Scanner.exe has an interface from which you can adjust settings and visit important articles in a few clicks.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.

5.99-A | Hotfix
* MAIN SCRIPT *
- Implemented fixes for several errors and issues based on bug reports and thanks to [evildarkarchon] on GitHub.
- Auto-Scanner no longer ignores certain records while detecting files for the *List Of Detected (Named) Records*
 [Better to expand detection and have it rarely report false postivies, than to skip detected records entirely.]
- Fixed some cases where load order would be ignored even if *loadorder.txt* was provided.
- Fixed duplicate Looks Menu (F4EE) parameter report.
- Fixed some minor formatting issues.

5.99
* MAIN SCRIPT *
- Auto-Scanner now checks for some types of Buffout4.toml corruption / invalid settings.
- Fixed Update Check not working correctly while *Update Check = true*
- Added detection for *Map Marker Crash* and *C++ Redist Crash*
- Additional fixes for minor internal bugs and issues.

* OTHER FILES *
- Several improvements and fixes for *CL Full Scan* and *CL Compare* thanks to [evildarkarchon] on GitHub.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.

5.95
* MAIN SCRIPT *
- Added a slight delay before scan completes so text can show up correctly in the terminal.
- Fixed several minor internal bugs and issues thanks to [evildarkarchon] on GitHub.
- Adjusted *List Of Detected (Named) Records* to not report *.esm* & *.esl* files.
- Adjusted code logic for *Plugin Limit Crash* for more accurate detection.

* OTHER FILES *
- Fixed infinte loop in *Scan Crashlogs.exe* during update checks while *Update Check = true*

5.90
* MAIN SCRIPT *
- Minor adjustments to text in the Auto-Scanner terminal window to prevent weird behavior.
- Merged commit created by [evildarkarchon] on GitHub that cleans up some things with *FCX Mode*
- Fixed Auto-Scanner reporting *Animation / Physics Crash* and *Player Character Crash* false positives.

* OTHER FILES *
- *Scan Crashlogs.exe* no longer checks for updates to prevent infinite looping problems.

5.88
* MAIN SCRIPT *
- Cleaned up and optimized most legacy code.
- Fixed code logic that would sometimes fail to detect *Classic Holstered Weapons* mod.
- Removed unnecessary package install line during update checks while *Update Check = true*
- *List Of (Possible) Form ID Culripts* segment will now show which plugin the detected Form ID belongs to.
- Auto-Scanner will no longer warn about missing Buffout 4 / Address Lib. files if DLL logs report no errors.
- Fixed code logic that would sometimes fail to detect named records for the *List Of Detected (Named) Records*
- Removed *List Of Possible File Culprits* segment and merged its output with the *List Of Detected (Named) Records*

5.77
* MAIN SCRIPT *
- Fixed crash / error when a crash log fails to list any plugins and modules.
- Fixed Nvidia specific mod detection reporting false positives on AMD GPUs.
- Added detection for 3 new mods with community patches and solutions.
- Added detection for Creation Kit Fixes and Buffout 4 VR Version.
- Minor text adjustments for some segments in AUTOSCAN.md output.

5.66
* MAIN SCRIPT *
- Fixed code for reading / writing Fallout4Custom.ini while *FCX Mode = true*
- Fixed code that forgot to update most INI config files while *FCX Mode = true*
- Fixed Permission Error if Fallout4Custom.ini or Buffout4.toml were set to Read Only.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.
- Merged "multiple small fixes and changes" commit created by [evildarkarchon] on GitHub.

5.55
* MAIN SCRIPT *
- Updated Windows 7 link for the latest Python versions (https://github.com/adang1345/PythonWin7).
- Auto-Scanner checking for package updates can now be enabled / disabled in *Scan Crashlogs.ini*
- Ajusted access permissions for f4se.log to prevent permission crashes / errors with OneDrive.
- Adjusted fix instructions for the "In Game ESP Explorer" mod.
- Switched to configparser for reading / writing INI files.

5.50
* MAIN SCRIPT *
- Fixed wrong code capitalization in a single line thanks to [evildarkarchon].
- Implemented a much better way to look up the user's current *Documents* directory path.
- Fixed a few crashes / errors caused while Auto-Scanner tried to edit or rename *Buffout4.toml*
- Added detection for Nvidia Reflex Support and Vulkan Renderer under the Important Patches & Fixes segment.
- Added detection for *[Creation Club Crash] | Completely disabling all Creation Club content should prevent this crash.
- Fixed crash / error caused when Buffout 4 wasn't already (manually) installed while *FCX Mode = true* in *Scan Crashlogs.ini*
  [Keep in mind that I strongly recommend having Buffout 4 and all its requirements manually installed, without a mod manager.]

5.40
* MAIN SCRIPT *
- Added detection for 3 new mods with community patches and solutions.
- Refactored code for renaming Buffout4.toml to prevent errors / crashes.
- Added support for Fallout 4 directory paths on Unix/Linux thanks to [kittivelae].
- Fallout4Custom.ini check will be perfomed only if *FCX Mode = true* in *Scan Crashlogs.ini*

* OTHER FILES *
*CL Compare.py* will now also compare F4SE Plugins (.dll files | MODULES are excluded).
*CL Compare.py* now generates a message in -RESULT.md if no matching plugins were found.

5.25
* MAIN SCRIPT *
- Added detection for 4 new mods with community patches and solutions.
- Removed and refactored some unnecessary code for optimization purposes.
- Auto-Scanner will now try to check itself for updates from the GitHub page each time you run it.
- Fixed several oversights regarding plugin detection if Auto-Scanner detects that *loadorder.txt* exists.
- Fixed wrong description while FCX Mode is enabled when changing F4EE from FALSE to TRUE in Buffout4.toml.
- Auto-Scanner now checks if important mods and fixes are installed. Can't believe I didn't implement this sooner...

5.15
* MAIN SCRIPT *
- Auto-Scanner is now available on GitHub! https://github.com/GuidanceOfGrace/Buffout4-CLAS
- Added missing Water Collision Crash stat logging while *Stat Logging = true* in *Scan Crashlogs.ini*
- Auto-Scanner now checks if *loadorder.txt* is located in the same folder where you run the script from.
  [If it's found, Auto-Scanner will ignore plugins from all crash logs and scan only the plugins from loadorder.txt]
  [Useful if you want to prevent Auto-Scanner from detecting certain plugins, as you can easily edit loadorder.txt]

* OTHER FILES *
- Additional adjustments to CL Full Scan.py and CL Compare.py to prevent scripts from crashing.
- Small changes and fixes for the Readme documentation.

5.05 (Hotfix)
* MAIN SCRIPT *
- Changed code logic for detecting locations of required log and ini files to prevent crashes.

* OTHER FILES *
- Added Unicode encoding to CL Full Scan.py and CL Compare.py so they are much less likely to crash.

5.00 
* MAIN SCRIPT *
- Auto updates for pip package installation will now stay disabled by default until I find actual packages to install.
- Main cmd terminal will show basic stats. For additional stats, set Stat Logging to *true* in *Scan Crashlogs.ini*.
- Auto-Scanner now sets FCX Mode to *true* by default upon generating its ini file. (Open ini for more details.)
- Auto-Scanner no longer checks if Fallout4.ini exists, since the file is no longer checked for anything else.
- Auto-Scanner no longer prompts to manually input the game path, a better alternative method was found.
- Auto-Scanner will prompt to manually input the Fallout4.ini path if known default paths aren't found.
- Various text formatting changes to make important messages more noticeable in -AUTOSCAN.md outputs.
- Added detection for Water Collision Crash. If you get this crash error/message, contact me asap.
- Adjusted code logic for Console Command Crash to reduce the amount of false positives.
- Fixed errors with "'Address_Library' / 'FO4_Custom_Path' is not defined".

+ If FCX Mode is *true*, Auto-Scanner checks for errors in log files inside your Documents\My Games\Fallout4\F4SE folder.
+ If FCX Mode is *true*, Auto-Scanner checks for errors and correct Buffout 4 \ F4SE installation in the f4se.log file.
  [f4se.log is located in Documents\My Games\Fallout4\F4SE folder and auto-generates after each game run.]

* OTHER FILES *
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.
- Removed text about Scan Crashlogs FCX.py from *Scan Readme.md*, since that's now a setting in *Scan Crashlogs.ini*

- *Scan Crashlogs.ini* (generates after running the main script) has a new setting called *Move Unsolved = false*
  [Set to true if you want Auto-Scanner to move all unsolved logs and their autoscans to CLAS-UNSOLVED folder.]
  [Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages.]

- *Scan Crashlogs.ini* (generates after running the main script) has a new setting called *INI Path = *
  [Only required if Profile Specific INIs are enabled in MO2 or you moved your Documents folder somewhere else.]
  [I highly recommend that you disable Profile Specific Game INI Files in MO2, located in Tools > Profiles...]
  
4.20 (The Funny Number Update)
- Auto-Scanner now auto-generates a custom ini file to save some of its confguration settings.
  [Check the file after running the script once to see and modify available settings.]

- Fixed unsolved [Precombines Crash] counting the wrong error messages when detected.
- Removed Autoscan logging for Buffout4.toml settings from the script, as this was unnecessary.
- Added script details and instructions on how to read AUTOSCAN.md outputs to Scan Readme.md file.
- Adjusted POSSIBLE FORM ID CULRIPTS code logic to not look for dynamic IDs (those that start with FF).

+ If FCX Mode is *true*, Auto-Scanner will automatically try to correct settings in Buffout4.toml if needed.
+ If FCX Mode is *true*, Auto-Scanner will check if Buffout 4 files/requirements are correctly installed.

4.10
- Hotfix: Auto-Scanner now checks multiple drives to find required folders & INI files.
- Fixed prompt for having to manually enter the game path if game folder wasn't detected.
- [This should also fix false positives given by Auto-Scanner versions 4.00 and 4.04.]

4.04
- Hotfix: Changed how Fallout4Custom.ini is created/accessed so it hopefully doesn't fail.
- Forgot to include the PDF in version 4.00. You can always use the online version:
- [Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.]

4.00
> Major Change: Auto-Scanner now checks if all Buffout 4 files are correctly installed/configured.
  It also checks if Archive Invalidation / Loose Files setting is enabled and automatically
  adds required text to Fallout4Custom.ini to force-enable that setting if necessary.
  (Auto-Scanner may ask that you input your Fallout 4 game path if it's not found.)

- Auto-Scanner will now automatically update pip installer for future use of Python Modules.
- Added detection for F4SE, Buffout 4, Address Library (& Plugin Preloader) installation.
- Fixed code logic for "Rendering Crash" to increase detection accuracy.
- Added detection for 3 new mods with community patches and solutions.

3.50
- General code improvements and optimization for my own sanity.
- Fixed code logic for Plugin Limit Crash to reduce false positives.
- Added detection for around 5 new mods with community patches and solutions.
- Added short descriptions about issues and possible solutions for most detected mods.
- Updated *HOW TO READ CRASH LOGS* PDF so it matches the latest online Google Docs version.
- Auto-Scanner now checks for all known game file extensions when looking for FILE CULPRITS.
- Auto-Scanner should no longer make duplicate plugin / mod reports, let me know if it still does.
- Expanded "NPC Pathing Crash" to also cover dynamic pathing / pathfinding error messages.
- Improved code logic for few other crash messages / errors to increase detection accuracy.
- Added detection for the following crash types (unconfirmed only, check PDF for details):
> *[Item Crash]
> *[Input Crash]
> *[Bad INI Crash]
> *[NPC Patrol Crash]
> *[NPC Projectile Crash]

3.20
- Updated advised fix instructions for HUD Caps mod.
- Improved detection logic for some mods to reduce duplicate reports.
- Added detection for around 10 new mods with community patches and solutions.
- Added detection for 4 new unsolved crash messages and errors (see PDF).
- Added detection for the MO2 Extractor Crash

3.11
- Fixed code logic for Audio Driver Crash to reduce false positives.
- Fixed code logic and added detection for .DDS and .SWF files in POSSIBLE FILE CULPRITS
- Improved code logic for some crash messages / errors to increase detection accuracy.
- Added detection for the following crash types:
> LOD Crash
> Decal Crash
> Vulkan Memory Crash
> Vulkan Settings Crash
> Corrupted Audio Crash

3.00
> Major Change: Auto-Scanner archive now contains a PDF file named *HOW TO READ CRASH LOGS*
(It's a dictionary of all known crash messages / errors and their solutions, alternatives and fixes.)
(I've removed the same info from crash log article because Nexus formatting is absolutely awful.)

- Removed check for TBB Redistributables as they are no longer required for Buffout 1.25.0+
- Fixed Windows 7 support. You should still install Python with Win7 support from the link.
- Fixed detection priority for CHW and mods that are guaranteed to crash with it.
- Moved Unofficial Patch detection to "MODS WITH SOLUTIONS AND ALTERNATIVES"
- Added detection for the official High Resolution Textures DLC (HD DLC). It's crap, don't use it.
- Added detection for possible file culprits, mainly .NIF and .BGSM , but other types might show up.
- Added detection for 4 new mods that frequently cause crashes listed in the main crash log article.
- Added detection for around 7 new crash messages / errors now listed in the included PDF document. 
- Changed names of some crash messages / errors so they better signify the underlying problem.
- Changed AUTOSCAN output format from .txt to .md for better readability and formatting.
- Added statistics logging at the end of Scan Crashlogs main terminal window.
- Various minor improvements and optimizations to Auto-Scanner code.

2.00
> Major Improvement: Auto-Scanner will now scan all available crash logs in one run.
(This also completely removes the need to copy-paste crash log names each time.)

- Added Priority Levels to each crash culprit. Handy when there are multiple culprits.
(Higher Priority Level means the crash was more likely caused by that exact culprit.)

- Auto-Scanner now also checks if any Autoscan results came out empty due to errors.
- Changed AUTOSCAN output format from .log to .txt (also helps with sorting).
- Main Error is now listed at the top of each AUTOSCAN result for clarity sake.
- Additional improvements to plugin detection to further reduce duplicate reports.
- Added additional check for new Papyrus | VirtualMachine (Papyrus Crash).
- Fixed incorrectly capitalized hyperlinks so they actually work.
- Corrected plugin detection for the Subway Runner mod.
- Renamed "Object Nif Crash" to "Object Model Crash".
- Updated example gif with the new instructions.

1.22
- Small improvements to plugin detection in order to reduce duplicate reports.
- Added additional check for yet undefined 0x0 Crash (Zero Crash). If you get it, please upload it to one of listed sites.
- Improved Classic Holstered Weapons detection logic so it gives a warning if you have mods that are guaranteed to crash with CHW.

1.20
- Upgrade: Auto-Scanner now lists Plugin IDs next to detected plugins whenever possible, as suggested by user: 1ae0bfb8
(Makes it much easier to tell if first two (or three if esl flagged) Form ID numbers match any Plugin ID numbers.)

- Improved "LIST OF (POSSIBLE) PLUGIN CULRIPTS" logic so it doesn't list empty spaces or base game plugins.
- Corrected nvwgf2umx.dll (Nvidia Driver Crash) detection logic so it's less likely to give false positives.

- Renamed "Weapon Physics Crash" to "Weapon Animation Crash" so it's less likely to be mistaken for Weapon Debris Crash
- Renamed "Havok Physics Crash" to "Body Physics Crash" so it better reflects the actual problem when such is detected.
- Added various other improvements and details to the script. Updated Scan Example.gif and added Scan Changelog.txt.

Version 1.13
- Hotfix: Small adjustment to Achievements settings detection logic so it doesn't leave false positives.

Version 1.11
- Beta release. May contain false positives. Please report if it does.