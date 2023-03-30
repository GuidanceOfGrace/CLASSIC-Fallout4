import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", type=str, nargs="?", default=Path.cwd(),
                        help="Specify the directory to scan for crash logs (default: current directory)")
    args = parser.parse_args()

    # Initialize variables and print a welcome message
    sort_fail_list = []
    print("Hello World! | Crash Logs Sort | Fallout 4")

    # Process each log file and move it to the appropriate directory
    for file_path in Path(args.scan_dir).glob("crash-*.log"):
        error_num, plugin_idx, check_valid = process_log(file_path)

        if check_valid and plugin_idx:
            target_dir = Path(args.scan_dir) / error_num
            target_dir.mkdir(exist_ok=True)
            shutil.move(file_path, target_dir)
        else:
            sort_fail_list.append(str(file_path))

    # Display the list of failed logs and print a completion message
    display_failed_logs(sort_fail_list)
    print("SORTING COMPLETE! Check the newly created folders!")
    input("Press Enter to continue...")


def process_log(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        all_lines = f.readlines()

    error_line = all_lines[3]
    error_num = error_line[-8:].strip()

    plugin_idx, check_valid = find_plugin_index_and_validate(all_lines, error_line)

    return error_num, plugin_idx, check_valid


def find_plugin_index_and_validate(all_lines, error_line):
    plugin_idx = 0
    check_valid = False
    for i, line in enumerate(all_lines):
        if "PLUGINS:" in line:
            plugin_idx = i
        if "[00]" in line:
            check_valid = True
    if "exception" not in error_line.lower():
        check_valid = False

    return plugin_idx, check_valid


def display_failed_logs(sort_fail_list):
    if sort_fail_list:
        print("NOTICE: SCRIPT WAS UNABLE TO PROPERLY SORT THE FOLLOWING LOG(S):")
        print("\n".join(sort_fail_list))
        print("-----")
        print("(These logs most likely have wrong formatting or don't have a plugin list.)")