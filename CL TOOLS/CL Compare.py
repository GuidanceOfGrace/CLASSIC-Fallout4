import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("error_code", type=str, help="Specify the error code you want to run log comparisons for.", nargs="?", default=str(Path.cwd()))
args = parser.parse_args()

# Resolve the path to the directory to be scanned and extract its name
folder_name = Path(args.error_code).resolve().name
scanpath = Path(args.error_code).resolve()

# Print a welcome message
print("Hello World! | Crash Logs Compare | Fallout 4")

# Initialize master lists and a list of items to remove from the lists
master_list_p = set()
master_list_m = set()
list_remove = {"Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm", ""}

# Process each log file in the directory and update the master lists
for file_index, file_path in enumerate(scanpath.glob("crash-*.log"), start=1):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        all_lines = f.readlines()

    # Find the indices of the plugin list and the F4SE plugin list
    plugin_idx = f4se_idx = int()
    for i, line in enumerate(all_lines):
        if "F4SE PLUGINS" in line:
            f4se_idx = i + 1
        elif "PLUGINS" in line:
            plugin_idx = i + 1

    # Extract the plugin and F4SE plugin lists from the log file
    plugins_unstripped = all_lines[plugin_idx:]
    f4sep_unstripped = all_lines[f4se_idx:plugin_idx - 1]

    # Create sets of plugins and F4SE plugins to perform set intersection
    plugin_list = set()
    f4sep_list = set()

    for elem in plugins_unstripped:
        plugin_list.add(elem[9:].strip() if "[FE" in elem else elem[5:].strip())

    for elem in f4sep_unstripped:
        if "Buffout4.dll" not in elem:
            f4sep_list.add(elem.strip())

    # If this is the first file, initialize the master lists
    if file_index == 1:
        master_list_p = plugin_list
        master_list_m = f4sep_list
    else:  # Otherwise, update the master lists
        master_list_p &= plugin_list
        master_list_m &= f4sep_list

    # Remove items from the master lists
    master_list_p -= list_remove
    master_list_m -= list_remove

# Write the results to a markdown file
with open(scanpath / f"{folder_name}-RESULT.md", "w") as f:
    f.write(f"LIST OF PLUGINS SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : {folder_name}\n")
    for item in sorted(master_list_p):
        f.write(f"{item}\n")
    if not master_list_p:
        f.write("- SCRIPT FOUND 0 MATCHING PLUGINS\n")
    f.write(f"\nLIST OF F4SE DLLs SEEN IN ALL AVAILABLE CRASH LOGS WITH THIS STACK CALL : {folder_name}\n")
    for item in sorted(master_list_m):
        f.write(f"{item}\n")
    if not master_list_m:
        f.write("- SCRIPT FOUND 0 MATCHING F4SE DLLs\n")

print("COMPARISON COMPLETE! Check the -RESULTS.md output!")
