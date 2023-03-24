import argparse
import os
from glob import glob
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("error_code", type=str, help="Specify the error code you want to run log comparisons for.", nargs="?", default=str(Path.cwd()))
    args = parser.parse_args()

    folder_name = Path(args.error_code).resolve().name
    scanpath = str(Path(args.error_code).resolve())
    print("Hello World! | Crash Logs Compare | Fallout 4")

    master_list_p = []
    master_list_m = []
    process_files(scanpath, master_list_p, master_list_m)

    list_remove = ["Fallout4.esm", "DLCCoast.esm", "DLCNukaWorld.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCworkshop02.esm", "DLCworkshop03.esm", ""]
    for elem in list_remove:
        if elem in master_list_p:
            master_list_p.remove(elem)
        if elem in master_list_m:
            master_list_m.remove(elem)

    write_results(scanpath, folder_name, master_list_p, master_list_m, args.error_code)


def process_files(scanpath, master_list_p, master_list_m):
    file_index = 0

    for file in glob(f"{scanpath}/crash-*.log"):
        file_index += 1
        plugin_idx = 0
        f4se_idx = 0
        with open(file, "r+", encoding="utf-8", errors="ignore") as plugin_check:
            all_lines = plugin_check.readlines()
        for line in all_lines:
            if "PLUGINS" in line and "F4SE" not in line:
                plugin_idx = all_lines.index(line) + 1
            if "F4SE PLUGINS" in line:
                f4se_idx = all_lines.index(line) + 1

        plugins_unstripped = all_lines[plugin_idx:]
        f4sep_unstripped = all_lines[f4se_idx:plugin_idx - 1]

        if file_index == 1:
            master_list_p, master_list_m = process_first_file(master_list_p, master_list_m, plugins_unstripped, f4sep_unstripped)
        else:
            master_list_p, master_list_m = process_subsequent_files(master_list_p, master_list_m, plugins_unstripped, f4sep_unstripped)


def process_first_file(master_list_p, master_list_m, plugins_unstripped, f4sep_unstripped):
    for elem in plugins_unstripped:
        if "[FE" in elem:
            master_list_p.append(elem[9:].strip())
        else:
            master_list_p.append(elem[5:].strip())
    for elem in f4sep_unstripped:
        if "Buffout4.dll" not in elem:
            master_list_m.append(elem.strip())
    return master_list_p, master_list_m


def process_subsequent_files(master_list_p, master_list_m, plugins_unstripped, f4sep_unstripped):
    plugin_list = [elem[9:].strip() if "[FE" in elem else elem[5:].strip() for elem in plugins_unstripped]
    f4sep_list = [elem.strip() for elem in f4sep_unstripped if "Buffout4.dll" not in elem]

    master_list_p = set(master_list_p).intersection(plugin_list)
    master_list_m = set(master_list_m).intersection(f4sep_list)
    return master_list_p, master_list_m

def write_results(scanpath, folder_name, master_list_p, master_list_m, error_code):
    with open(f"{scanpath}/{error_code}-RESULTS.md", "w+", encoding="utf-8", errors="ignore") as results:
        results.write(f"# Results for {folder_name}\n\n")
        results.write("## Plugins\n\n")
        for elem in master_list_p:
            results.write(f"- {elem}\n")
        results.write("\n## F4SE Plugins\n\n")
        for elem in master_list_m:
            results.write(f"- {elem}\n")

print("COMPARISON COMPLETE! Check the -RESULTS.md output!")
os.system("pause")
