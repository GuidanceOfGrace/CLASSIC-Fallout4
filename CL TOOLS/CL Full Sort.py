import os
import shutil
from glob import glob


def main():
    sort_fail_list = []
    print("Hello World! | Crash Logs Sort | Fallout 4")

    for file in glob("crash-*.log"):
        error_num, plugin_idx, check_valid = process_log(file)

        if check_valid == True and plugin_idx and not os.path.exists(error_num):
            os.mkdir(error_num)
            shutil.move(file, error_num)
        elif check_valid == True and plugin_idx:
            shutil.move(file, error_num)
        else:
            sort_fail_list.append(file)

    display_failed_logs(sort_fail_list)
    print("SORTING COMPLETE! Check the newly created folders!")
    os.system("pause")


def process_log(file):
    with open(file, "r+", encoding="utf-8", errors="ignore") as error_check:
        all_lines = error_check.readlines()

    error_line = all_lines[3]
    error_num = error_line[-8:].strip()

    plugin_idx, check_valid = find_plugin_index_and_validate(all_lines, error_line)

    return error_num, plugin_idx, check_valid


def find_plugin_index_and_validate(all_lines, error_line):
    plugin_idx = 0
    check_valid = False
    for line in all_lines:
        if "F4SE" not in line and "PLUGINS:" in line:
            plugin_idx = all_lines.index(line)
        if "[00]" in line:
            check_valid = True
    if "exception" not in error_line.lower():
        check_valid = False

    return plugin_idx, check_valid


def display_failed_logs(sort_fail_list):
    if len(sort_fail_list) >= 1:
        print("NOTICE: SCRIPT WAS UNABLE TO PROPERLY SORT THE FOLLOWING LOG(S): ")
        for elem in sort_fail_list:
            print(elem)
        print("-----")
        print("(These logs most likely have wrong formatting or don't have a plugin list.)")
