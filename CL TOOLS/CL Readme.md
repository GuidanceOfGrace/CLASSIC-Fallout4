# THESE SCRIPTS ARE MAINLY INTENDED FOR USERS THAT KEEP A LARGE DATABASE OF CRASH LOG FILES #
* THE LARGER THE DATABASE, THE BETTER THE RESULTS. AT LEAST 200 CRASH LOG FILES RECOMMENDED *

* CL Compare.py * AND * CL Full Sort.py * can be used to narrow the same call stacks in crash logs down to specific mod plugins.
The more crash logs (in terms of quantity) and the more varied crash logs (from many different players) you have
for any specific call stack address, the more accurate the results should be for that specific call stack.

# HOW TO USE #

1.) Place * CL Full Sort.py * into the folder with all of your crash logs and run the script.
> This will create a bunch of folders and move each log to the folder that matches their call stack address.

2.) Place * CL Compare.py * into desired call stack folder created from Step 1.) and run the script (FOLDER SHOULD HAVE AT LEAST 2 CRASH LOGS).
> This will compare plugin lists from each crash log in that folder and create a list of all plugins that all of these logs share together.

3.) Check the -RESULT.md output file. It will only show the mod plugins found in EVERY crash log in that folder.
> Therefore, these crashes with the same call stack address were likely caused by one of the listed plugins.

4.) Report any interesting findings to me, if you're so inclined. You know where to find me. 

TIP 1: * CL Compare.py * will only work if there are AT LEAST 2 crash logs for the comparison. You can't compare a single crash log with itself, obviously.

TIP 2: Some crashes can be caused by .dll (f4se) plugins or exclusively mod files (textures, meshes, etc.), so these scripts will never be 100% effective.

TIP 3: If -RESULT.md output file is empty, that means the crash logs SHARE TOGETHER 0 PLUGINS (There's not a single specific plugin that apprears in all logs.)
> Keep in mind that the script ignores Official Game DLCs from being listed in -RESULT.md (results with only Unofficial Fallout 4 Patch will always be a dud.)

TIP 4: If you need crash logs with a specific call stack address, feel free to contact me and I'll provide, if I have any that match.
> You can also check the Collective Modding Discord Server and download any crash logs yourself from the relevant thread in 🚨-fo4-crash-logs channel.

TIP 5: The call stack address can be longer than 7 characters in rare cases, this could rarely mess up the results until I find a better way to handle such cases.
> You can double-check by comparing the call stack address (all chars after "+" in EXCEPTION_ACCESS_VIOLATION line / main error) with the folder name (they should match).
