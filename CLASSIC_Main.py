import os
import logging
import hashlib
import zipfile
import datetime
import requests
import platform
import ruamel.yaml
import configparser
from pathlib import Path

""" AUTHOR NOTES (POET):
    - REMINDER (JUST FOR ME): REMOVE ANY PERSONAL FOLDER AND FILE PATHS FROM YAML CONFIG FILES BEFORE UPDATING ON NEXUS!
    - REMINDER: 'shadows x from outer scope' means the variable name repeats both in the func and outside all other func.
    - Comments marked as RESERVED in all scripts are intended for future updates or tests, do not edit / move / remove.
    - (..., encoding="utf-8", errors="ignore") needs to go with every opened file because unicode errors are a bitch.
    - If you get a 'charmap' error, you forgot to put encoding='utf-8'! (Required for every YAML file read / write).
    - message_output in a func should be self contained. Don't write to AUTOSCAN output directly, just call func.
    - import shelve if you want to store persistent data that you do not want regular users to access or modify.
    - ALL USED EMOJI IN ONE PLACE: ❓ ❌ ✔️
    -----
    CO-AUTHOR NOTES (NameHere):
    * You can write stuff here so I don't miss it. *
"""


# Logging levels: debug | info | warning | error | critical | Level in basicConfig is minimum and must be UPPERCASE
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename="CLASSIC Journal.log",
        filemode="a",
        format="%(asctime)s | %(levelname)s | %(message)s")


# ================================================
# DEFINE FILE / YAML FUNCTIONS
# ================================================
def remove_readonly(file_path):
    try:
        # Get current file permissions.
        if platform.system() == "Windows":
            permissions = os.stat(file_path).st_mode
        else:
            permissions = os.stat(file_path).st_mode & 0o777

        # Check if file is set to Read-Only.
        if permissions & (os.O_RDONLY | os.O_WRONLY):
            # Remove Read-Only permission (add write permission).
            if platform.system() == "Windows":
                os.chmod(file_path, permissions & ~0o400)
            else:
                os.chmod(file_path, permissions | 0o200)

            logging.debug(f"'{file_path}' is no longer Read-Only.")
        else:
            logging.debug(f"'{file_path}' is not set to Read-Only.")

    except FileNotFoundError:
        logging.error(f"ERROR : '{file_path}' not found.")
    except (ValueError, OSError) as err:
        logging.error(f"ERROR : {err}")


def yaml_get(yaml_path, *key_path):
    yaml = ruamel.yaml.YAML()
    yaml.indent(offset=2)
    yaml.width = 300

    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    value = data
    for key in key_path:
        if key in value:
            value = value[key]
        else:
            return None
    return value


def yaml_update(yaml_path, key_path, new_value):
    yaml = ruamel.yaml.YAML()
    yaml.indent(offset=2)
    yaml.width = 300

    with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
        data = yaml.load(yaml_file)

    keys = key_path.split('.') if isinstance(key_path, str) else key_path
    current = data
    for key in keys[:-1]:
        current = current[key]

    current[keys[-1]] = new_value

    with open(yaml_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(data, yaml_file)


def local_oobe():
    yaml = ruamel.yaml.YAML()
    yaml.indent(offset=2)
    yaml.width = 300
    if not os.path.exists("CLASSIC Data/CLASSIC FO4 Local.yaml"):
        FO4_Local = {"Game_Info": {"Root_Folder_Docs": None,
                                   "Root_Folder_Game": None,
                                   "Game_Folder_Data": None,
                                   "Game_Folder_Scripts": None,
                                   "Game_Folder_CK_Fixes": None,
                                   "Game_File_AddressLib": None,
                                   "Game_File_BuffoutDLL": None,
                                   "Game_File_BuffoutTOML": None,
                                   "Game_File_CK_EXE": None,
                                   "Game_File_EXE": None,
                                   "Game_File_PreloaderDLL": None,
                                   "Game_File_PreloaderXML": None,
                                   "Game_File_SteamINI": None,
                                   "XSE_File_DLL": None,
                                   "XSE_File_Loader": None,
                                   "XSE_File_SteamDLL": None,
                                   "Docs_Folder_XSE": None,
                                   "Docs_File_XSE": None,
                                   "Docs_File_GameMainINI": None,
                                   "Docs_File_GameCustomINI": None,
                                   "Docs_File_GamePrefsINI": None,
                                   "Docs_File_PapyrusLog": None,
                                   "Docs_File_WryeBashPC": None}}
        with open("CLASSIC Data/CLASSIC FO4 Local.yaml", "w", encoding="utf-8", errors="ignore") as file:
            yaml.dump(FO4_Local, file)
    if not os.path.exists("CLASSIC Data/CLASSIC FO4VR Local.yaml"):
        FO4VR_Local = {"GameVR_Info": {"Root_Folder_Docs": None,
                                       "Root_Folder_Game": None,
                                       "Game_Folder_Data": None,
                                       "Game_Folder_Scripts": None,
                                       "Game_Folder_CK_Fixes": None,
                                       "Game_File_AddressLib": None,
                                       "Game_File_BuffoutDLL": None,
                                       "Game_File_BuffoutTOML": None,
                                       "Game_File_CK_EXE": None,
                                       "Game_File_EXE": None,
                                       "Game_File_PreloaderDLL": None,
                                       "Game_File_PreloaderXML": None,
                                       "Game_File_SteamINI": None,
                                       "XSE_File_DLL": None,
                                       "XSE_File_Loader": None,
                                       "XSE_File_SteamDLL": None,
                                       "Docs_Folder_XSE": None,
                                       "Docs_File_XSE": None,
                                       "Docs_File_GameMainINI": None,
                                       "Docs_File_GameCustomINI": None,
                                       "Docs_File_GamePrefsINI": None,
                                       "Docs_File_PapyrusLog": None,
                                       "Docs_File_WryeBashPC": None}}
        with open("CLASSIC Data/CLASSIC FO4VR Local.yaml", "w", encoding="utf-8", errors="ignore") as file:
            yaml.dump(FO4VR_Local, file)


local_oobe()


# ================================================
# CREATE REQUIRED FILES, SETTINGS & UPDATE CHECK
# ================================================
def classic_logging():
    logging.debug("- - - INITIATED LOGGING CHECK")
    if os.path.exists("CLASSIC Journal.log"):
        log_time = datetime.datetime.fromtimestamp(os.path.getmtime("CLASSIC Journal.log"))
        current_time = datetime.datetime.now()
        log_age = current_time - log_time
        if log_age.days > 7:
            try:
                classic_update_check()
                os.remove("CLASSIC Journal.log")  # We do this to trigger an auto update check every X days.
                print("CLASSIC Journal.log has been deleted and regenerated due to being older than 7 days.")
                logging.basicConfig(level=logging.INFO, filename="CLASSIC Journal.log", filemode="a", format="%(asctime)s | %(levelname)s | %(message)s")
            except (ValueError, OSError) as err:
                print(f"An error occurred while deleting CLASSIC Journal.log: {err}")
                classic_update_check()


def classic_data_extract():
    if not os.path.exists("CLASSIC Data/databases/CLASSIC Main.yaml"):
        if os.path.exists("CLASSIC Data/CLASSIC Data.zip"):
            with zipfile.ZipFile("CLASSIC Data/CLASSIC Data.zip", "r") as zip_data:
                zip_data.extractall("CLASSIC Data")
        elif os.path.exists("CLASSIC Data.zip"):
            with zipfile.ZipFile("CLASSIC Data.zip", "r") as zip_data:
                zip_data.extractall("CLASSIC Data")
        else:
            print("❌ ERROR : UNABLE TO FIND CLASSIC Data.zip! This archive is required for CLASSIC to function.")
            print("Please ensure that you have extracted all CLASSIC files into the same folder after downloading.")
            os.system("pause")

    if not os.path.exists("CLASSIC Data/databases/FO4 FID Main.txt"):
        if os.path.exists("CLASSIC Data/CLASSIC Data.zip"):
            with zipfile.ZipFile("CLASSIC Data/CLASSIC Data.zip", "r") as zip_data:
                zip_data.extract("databases/FO4 FID Main.txt", "CLASSIC Data")
        elif os.path.exists("CLASSIC Data.zip"):
            with zipfile.ZipFile("CLASSIC Data.zip", "r") as zip_data:
                zip_data.extract("databases/FO4 FID Main.txt", "CLASSIC Data")
        else:
            print("❌ ERROR : UNABLE TO FIND CLASSIC Data.zip! CLASSIC will not be able to show FormID values.")
            print("Please ensure that you have extracted all CLASSIC files into the same folder after downloading.")


def classic_settings(setting=None):
    if not os.path.exists("CLASSIC Settings.yaml"):
        default_settings = yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info", "default_settings")
        with open('CLASSIC Settings.yaml', 'w', encoding='utf-8') as file:
            file.write(default_settings)
    if setting is not None:
        get_setting = yaml_get("CLASSIC Settings.yaml", "CLASSIC_Settings", setting)
        return get_setting


def classic_ignorefile():
    if not os.path.exists("CLASSIC Ignore.yaml"):
        default_ignorefile = yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info", "default_ignorefile")
        with open('CLASSIC Ignore.yaml', 'w', encoding='utf-8') as file:
            file.write(default_ignorefile)


def classic_update_check():
    classic_outdated = """\
❌ WARNING : YOUR CLASSIC VERSION IS OUT OF DATE!
Please download the latest version from here:
https://www.nexusmods.com/fallout4/mods/56255
"""
    classic_unable = """\
❌ WARNING : CLASSIC WAS UNABLE TO CHECK FOR UPDATES, BUT WILL CONTINUE SCANNING.
CHECK FOR ANY CLASSIC UPDATES HERE: https://www.nexusmods.com/fallout4/mods/56255
"""

    logging.debug("- - - INITIATED UPDATE CHECK")
    if classic_settings("Update Check"):
        classic_local = yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info", "version")
        print("❓ (Needs internet connection) CHECKING FOR NEW CLASSIC VERSIONS...")
        print("   (You can disable this check in the EXE or CLASSIC Settings.yaml) \n")
        try:  # DON'T FORGET TO UPDATE GITHUB AND NEXUS LINKS FOR SPECIFIC GAME VERSIONS!
            response = requests.get("https://api.github.com/repos/GuidanceOfGrace/CLASSIC-Fallout4/releases/latest", timeout=30)
            if not response.status_code == requests.codes.ok:
                response.raise_for_status()
            classic_ver_received = response.json()["name"]
            print(f"Your CLASSIC Version: {classic_local}\nNewest CLASSIC Version: {classic_ver_received}\n")
            if classic_ver_received == classic_local:
                print("✔️ You have the latest version of CLASSIC! \n")
                return True
            else:
                print(classic_outdated)
        except (ValueError, OSError, requests.exceptions.RequestException) as err:
            print(err)
            print(classic_unable)
    else:
        print("\n❌ NOTICE: UPDATE CHECK IS DISABLED IN CLASSIC Settings.yaml \n")
        print("===============================================================================")
    return False


# ================================================
# CHECK DEFAULT DOCUMENTS & GAME FOLDERS / FILES
# ================================================

# =========== CHECK DOCUMENTS FOLDER PATH -> GET GAME DOCUMENTS FOLDER ===========
def docs_path_find():
    logging.debug("- - - INITIATED DOCS PATH CHECK")
    game_sid = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_SteamID")
    if not classic_settings("VR Mode"):
        game_docs_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_Docs_Name")
    else:
        game_docs_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_Docs_Name")

    def get_windows_docs_path():
        import ctypes.wintypes
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        win_buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, win_buffer)
        win_docs = os.path.join(win_buffer.value, fr"My Games\{game_docs_name}")
        if not classic_settings("VR Mode"):
            yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Root_Folder_Docs", win_docs)
        else:
            yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Root_Folder_Docs", f"{win_docs}")

    def get_linux_docs_path():
        libraryfolders_path = Path.home().joinpath(".local", "share", "Steam", "steamapps", "common", "libraryfolders.vdf")
        if libraryfolders_path.is_file():
            library_path = Path()
            with libraryfolders_path.open(encoding="utf-8", errors="ignore") as steam_library_raw:
                steam_library = steam_library_raw.readlines()
            for library_line in steam_library:
                if "path" in library_line:
                    library_path = Path(library_line.split('"')[3])
                if str(game_sid) in library_line:
                    library_path = library_path.joinpath("steamapps")
                    linux_docs = library_path.joinpath("compatdata", str(game_sid), "pfx", "drive_c", "users", "steamuser", "My Documents", "My Games", game_docs_name)
                    if not classic_settings("VR Mode"):
                        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Root_Folder_Docs", linux_docs)
                    else:
                        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Root_Folder_Docs", f"{linux_docs}")

    def get_manual_docs_path():
        print(f"> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR {game_docs_name}.ini IS LOCATED < <")
        path_input = input(f"(EXAMPLE: C:/Users/Zen/Documents/My Games/{game_docs_name} | Press ENTER to confirm.)\n> ")
        print(f"You entered: {path_input} | This path will be automatically added to CLASSIC Settings.yaml")
        manual_docs = Path(path_input.strip())
        if not classic_settings("VR Mode"):
            yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Root_Folder_Docs", manual_docs)
        else:
            yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Root_Folder_Docs", manual_docs)

    # =========== CHECK IF GAME DOCUMENTS FOLDER PATH WAS GENERATED AND FOUND ===========
    if not classic_settings("VR Mode"):
        docs_path = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Root_Folder_Docs")
    else:
        docs_path = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Root_Folder_Docs")
    if docs_path is None:
        if platform.system() == "Windows":
            get_windows_docs_path()
        else:
            get_linux_docs_path()

    if not classic_settings("VR Mode"):
        docs_path = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Root_Folder_Docs")
    else:
        docs_path = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Root_Folder_Docs")
    try:  # In case .exists() complains about checking a None value.
        if not Path(docs_path).exists():
            get_manual_docs_path()
    except (ValueError, OSError):
        get_manual_docs_path()


def docs_generate_paths():
    logging.debug("- - - INITIATED DOCS PATH GENERATION")
    if not classic_settings("VR Mode"):
        docs_path = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Root_Folder_Docs")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_Folder_XSE", fr"{docs_path}\F4SE")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_File_GameCustomINI", fr"{docs_path}\Fallout4Custom.ini")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_File_GameMainINI", fr"{docs_path}\Fallout4.ini")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_File_GamePrefsINI", fr"{docs_path}\Fallout4Prefs.ini")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_File_PapyrusLog", fr"{docs_path}\Logs\Script\Papyrus.0.log")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_File_WryeBashPC", fr"{docs_path}\ModChecker.html")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Docs_File_XSE", fr"{docs_path}\F4SE\f4se.log")

    else:
        docs_path = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Root_Folder_Docs")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_Folder_XSE", fr"{docs_path}\F4SE")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_File_GameCustomINI", fr"{docs_path}\Fallout4VRCustom.ini")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_File_GameMainINI", fr"{docs_path}\Fallout4VR.ini")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_File_GamePrefsINI", fr"{docs_path}\Fallout4VRPrefs.ini")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_File_PapyrusLog", fr"{docs_path}\Logs\Script\Papyrus.0.log")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_File_WryeBashPC", fr"{docs_path}\ModChecker.html")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Docs_File_XSE", fr"{docs_path}\F4SE\f4sevr.log")


# =========== CHECK DOCUMENTS XSE FILE -> GET GAME ROOT FOLDER PATH ===========
def game_path_find():
    logging.debug("- - - INITIATED GAME PATH CHECK")
    Docs_File_XSE = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Docs_File_XSE")

    if not classic_settings("VR Mode"):
        game_root_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_Root_Name")
        xse_acronym = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "XSE_Acronym")
    else:
        game_root_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_Root_Name")
        xse_acronym = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "XSE_Acronym")

    if Path(Docs_File_XSE).is_file():
        with open(Docs_File_XSE, "r", encoding="utf-8", errors="ignore") as LOG_Check:
            Path_Check = LOG_Check.readlines()
            for logline in Path_Check:
                if "plugin directory" in logline:
                    logline = logline[19:].replace("\\Data\\F4SE\\Plugins", "")
                    game_path = logline.replace("\n", "")
                    if not game_path or not Path(game_path).exists():
                        print(f"> > PLEASE ENTER THE FULL DIRECTORY PATH WHERE YOUR {game_root_name} IS LOCATED < <")
                        path_input = input(fr"(EXAMPLE: C:\Steam\steamapps\common\{game_root_name} | Press ENTER to confirm.)\n> ")
                        print(f"You entered: {path_input} | This path will be automatically added to CLASSIC Settings.yaml")
                        game_path = Path(path_input.strip())

                    if not classic_settings("VR Mode"):
                        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Root_Folder_Game", str(game_path))
                    else:
                        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Root_Folder_Game", str(game_path))
    else:
        print(f"❌ CAUTION : THE {xse_acronym.lower()}.log FILE IS MISSING FROM YOUR GAME DOCUMENTS FOLDER! \n")
        print(f"   You need to run the game at least once with {xse_acronym.lower()}_loader.exe \n")
        print("    After that, try running CLASSIC again! \n-----\n")


def game_generate_paths():
    logging.debug("- - - INITIATED GAME PATH GENERATION")
    if not classic_settings("VR Mode"):
        game_path = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Root_Folder_Game")
        # GAME FOLDERS
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_Folder_Data", fr"{game_path}Data")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_Folder_Scripts", fr"{game_path}Data\Scripts")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_Folder_CK_Fixes", fr"{game_path}Data\F4CKFixes")
        # GAME FILES
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_AddressLib", fr"{game_path}Data\F4SE\Plugins\version-1-10-163-0.bin")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_BuffoutDLL", fr"{game_path}Data\F4SE\Plugins\Buffout4.dll")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_BuffoutTOML", fr"{game_path}Data\F4SE\Plugins\Buffout4\config.toml")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_CK_EXE", fr"{game_path}CreationKit.exe")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_EXE", fr"{game_path}Fallout4.exe")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_PreloaderDLL", fr"{game_path}IpHlpAPI.dll")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_PreloaderXML", fr"{game_path}xSE PluginPreloader.xml")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.Game_File_SteamINI", fr"{game_path}steam_api.ini")
        # GAME F4SE
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.XSE_File_DLL", fr"{game_path}f4se_1_10_163.dll")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.XSE_File_Loader", fr"{game_path}f4se_loader.exe")
        yaml_update("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info.XSE_File_SteamDLL", fr"{game_path}f4se_steam_loader.dll")
    else:
        gamevr_path = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Root_Folder_Game")
        # VR FOLDERS
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_Folder_Data", fr"{gamevr_path}Data")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_Folder_Scripts", fr"{gamevr_path}Data\Scripts")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_Folder_CK_Fixes", fr"{gamevr_path}Data\F4CKFixes")
        # VR FILES
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_AddressLib", fr"{gamevr_path}\Data\F4SE\Plugins\version-1-2-72-0.csv")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_BuffoutDLL", fr"{gamevr_path}\Data\F4SE\Plugins\msdia140.dll")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_BuffoutTOML", fr"{gamevr_path}\Data\F4SE\Plugins\Buffout4.toml")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_CK_EXE", fr"{gamevr_path}CreationKit.exe")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_EXE", fr"{gamevr_path}\Fallout4VR.exe")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_PreloaderDLL", fr"{gamevr_path}IpHlpAPI.dll")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_PreloaderXML", fr"{gamevr_path}xSE PluginPreloader.xml")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.Game_File_SteamINI", fr"{gamevr_path}steam_api.ini")
        # VR F4SE
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.XSE_File_DLL", fr"{gamevr_path}\f4sevr_1_2_72.dll")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.XSE_File_Loader", fr"{gamevr_path}\f4sevr_loader.exe.exe")
        yaml_update("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info.XSE_File_SteamDLL", fr"{gamevr_path}\f4sevr_steam_loader.dll")


# =========== CHECK GAME EXE FILE -> GET PATH AND HASHES ===========
def game_check_integrity() -> str:
    logging.debug("- - - INITIATED GAME INTEGRITY CHECK")
    message_list = []

    if not classic_settings("VR Mode"):
        steam_ini_local = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Game_File_SteamINI")
        exe_hash_old = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_HashedMain", "1.10.163")
        # exe_hash_new = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_HashedMain", "1.xx.xxx") | RESERVED FOR 2023 UPDATE
        game_exe_local = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Game_File_EXE")
        game_root_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_Root_Name")
    else:
        steam_ini_local = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Game_File_SteamINI")
        exe_hash_old = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_HashedMain", "1.10.163")
        # exe_hash_new = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_HashedMain", "1.xx.xxx") | RESERVED FOR 2023 UPDATE
        game_exe_local = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Game_File_EXE")
        game_root_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_Root_Name")

    game_exe_path = Path(game_exe_local)
    steam_ini_path = Path(steam_ini_local)
    if game_exe_path.is_file():
        with open(game_exe_path, "rb") as f:
            file_contents = f.read()
            # Algo should match the one used for Database YAML!
            exe_hash_local = hashlib.sha256(file_contents).hexdigest()
            # print(f"LOCAL: {exe_hash_local}\nDATABASE: {exe_hash_old}")
            if exe_hash_local == exe_hash_old and not steam_ini_path.exists():
                message_list.append(f"✔️ You have the latest version of {game_root_name}! \n-----\n")
            elif steam_ini_path.exists():
                message_list.append(f"\U0001F480 CAUTION : YOUR {game_root_name} GAME / EXE VERSION IS OUT OF DATE \n-----\n")
            else:
                message_list.append(f"❌ CAUTION : YOUR {game_root_name} GAME / EXE VERSION IS OUT OF DATE \n-----\n")

        if "Program Files" not in str(game_exe_path):
            message_list.append(f"✔️ Your {game_root_name} game files are installed outside of the Program Files folder! \n-----\n")
        else:
            message_list.extend([f"❌ CAUTION : Your {game_root_name} game files are installed inside of the Program Files folder!",
                                 "   Having the game installed here might cause Windows UAC to block some mods from working properly.",
                                 "   To ensure that everything works, move your Game or entire Steam folder outside of Program Files.",
                                 "-----"])

    message_output = "".join(message_list)
    return message_output


# =========== CHECK GAME XSE SCRIPTS -> GET PATH AND HASHES ===========
def xse_check_integrity() -> str:  # RESERVED | NEED VR HASH/FILE CHECK
    logging.debug("- - - INITIATED XSE INTEGRITY CHECK")
    message_list = []
    failed_list = []
    catch_errors = yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "catch_log_errors")
    if not classic_settings("VR Mode"):
        xse_acronym = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "XSE_Acronym")
        xse_log_file = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Docs_File_XSE")
        xse_full_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "XSE_FullName")
        xse_ver_latest = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "XSE_Ver_Latest")
        addlib_file = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Game_File_AddressLib")
    else:
        xse_acronym = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "XSE_Acronym")
        xse_log_file = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Docs_File_XSE")
        xse_full_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "XSE_FullName")
        xse_ver_latest = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "XSE_Ver_Latest")
        addlib_file = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Game_File_AddressLib")

    if Path(addlib_file).exists():
        message_list.append(f"✔️ REQUIRED: *Address Library* for Script Extender is installed! \n-----\n")
    else:
        message_list.append(yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Warnings_MODS", "Warn_ADLIB_Missing"))

    if Path(xse_log_file).exists():
        message_list.append(f"✔️ REQUIRED: *{xse_full_name}* is installed! \n-----\n")
        with open(xse_log_file, "r", encoding="utf-8", errors="ignore") as xse_log:
            xse_data = xse_log.readlines()
        if str(xse_ver_latest) in xse_data[0]:
            message_list.append(f"✔️ You have the latest version of *{xse_full_name}*! \n-----\n")
        else:
            message_list.append(yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Warnings_XSE", "Warn_Outdated"))
        for line in xse_data:
            if any(item.lower() in line.lower() for item in catch_errors):
                failed_list.append(line)

        if failed_list:
            message_list.append(f"#❌ CAUTION : {xse_acronym}.log REPORTS THE FOLLOWING ERRORS #\n")
            for elem in failed_list:
                message_list.append(f"ERROR > {elem.strip()} \n-----\n")
    else:
        message_list.extend([f"❌ CAUTION : *{xse_acronym.lower()}.log* FILE IS MISSING FROM YOUR DOCUMENTS FOLDER! \n",
                             f"   You need to run the game at least once with {xse_acronym.lower()}_loader.exe \n",
                             "    After that, try running CLASSIC again! \n-----\n"])

    message_output = "".join(message_list)
    return message_output


def xse_check_hashes() -> str:
    logging.debug("- - - INITIATED XSE FILE HASH CHECK")
    message_list = []
    xse_script_missing = xse_script_mismatch = False
    if not classic_settings("VR Mode"):
        xse_hashedscripts = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "XSE_HashedScripts")
        game_folder_scripts = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Game_Folder_Scripts")
    else:
        xse_hashedscripts = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "XSE_HashedScripts")
        game_folder_scripts = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Game_Folder_Scripts")

    xse_hashedscripts_local = {key: None for key in xse_hashedscripts.keys()}
    for key in xse_hashedscripts_local:
        script_path = Path(fr"{game_folder_scripts}\{str(key)}")
        if script_path.is_file():
            with open(script_path, "rb") as f:
                file_contents = f.read()
                # Algo should match the one used for Database YAML!
                file_hash = hashlib.sha256(file_contents).hexdigest()
                xse_hashedscripts_local[key] = str(file_hash)

    for key in xse_hashedscripts:
        if key in xse_hashedscripts_local:
            hash1 = xse_hashedscripts[key]
            hash2 = xse_hashedscripts_local[key]
            if hash1 == hash2:
                pass
            elif hash2 is None:  # Can only be None if not hashed in the first place, meaning it is missing.
                message_list.append(f"❌ CAUTION : {key} Script Extender file is missing from your game Scripts folder! \n-----\n")
                xse_script_missing = True
            else:
                message_list.append(f"[!] CAUTION : {key} Script Extender file is outdated or overriden by another mod! \n-----\n")
                xse_script_mismatch = True

    if xse_script_missing:
        message_list.append(yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Warnings_XSE", "Warn_Missing"))
    if xse_script_mismatch:
        message_list.append(yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Warnings_XSE", "Warn_Mismatch"))
    if not xse_script_missing and not xse_script_mismatch:
        message_list.append("✔️ All Script Extender files have been found and accounted for! \n-----\n")

    message_output = "".join(message_list)
    return message_output


# ================================================
# CHECK DOCUMENTS GAME INI FILES & INI SETTINGS
# ================================================
def docs_check_folder():
    message_list = []
    if not classic_settings("VR Mode"):
        game_docs_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_Docs_Name")
    else:
        game_docs_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_Docs_Name")

    if "onedrive" in game_docs_name.lower():
        message_list.extend([f"❌ CAUTION : MICROSOFT ONEDRIVE IS OVERRIDING YOUR DOCUMENTS FOLDER PATH! \n",
                             f"   This can sometimes cause various save file and file permissions problems. \n",
                             "    To avoid this, disable Documents folder backup in your OneDrive settings. \n-----\n"])
    message_output = "".join(message_list)
    return message_output


# =========== CHECK DOCS MAIN INI -> CHECK EXISTENCE & CORRUPTION ===========
def docs_check_ini(ini_name) -> str:
    logging.info(f"- - - INITIATED {ini_name} CHECK")
    message_list = []

    if not classic_settings("VR Mode"):
        root_folder_docs = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Root_Folder_Docs")
        game_docs_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Game_Info", "Game_Docs_Name")
    else:
        root_folder_docs = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Root_Folder_Docs")
        game_docs_name = yaml_get("CLASSIC Data/databases/CLASSIC FO4VR.yaml", "GameVR_Info", "Game_Docs_Name")

    ini_file_list = list(Path(root_folder_docs).glob("*.ini"))
    ini_path = Path(root_folder_docs).joinpath(ini_name)
    if any(ini_name.lower() in file.name.lower() for file in ini_file_list):
        try:
            remove_readonly(ini_path)

            INI_config = configparser.ConfigParser()
            INI_config.optionxform = str
            INI_config.read(ini_path)
            message_list.append(f"✔️ No obvious corruption detected in {ini_name}, file seems OK! \n-----\n")

            if ini_name.lower() == f"{game_docs_name.lower()}custom.ini":
                if "Archive" not in INI_config.sections():
                    message_list.extend(["❌ WARNING : Archive Invalidation / Loose Files setting is not enabled. \n",
                                         "  CLASSIC will now enable this setting automatically in the game INI files. \n-----\n"])
                    try:
                        INI_config.add_section("Archive")
                    except configparser.DuplicateSectionError:
                        pass
                else:
                    message_list.append("✔️ Archive Invalidation / Loose Files setting is already enabled! \n-----\n")

                INI_config.set("Archive", "bInvalidateOlderFiles", "1")
                INI_config.set("Archive", "sResourceDataDirsFinal", "")

                with open(ini_path, "w+", encoding="utf-8", errors="ignore") as ini_file:
                    INI_config.write(ini_file, space_around_delimiters=False)

        except PermissionError:
            message_list.extend([f"[!] CAUTION : YOUR {ini_name} FILE IS SET TO READ ONLY. \n",
                                 "     PLEASE REMOVE THE READ ONLY PROPERTY FROM THIS FILE, \n",
                                 "     SO CLASSIC CAN MAKE THE REQUIRED CHANGES TO IT. \n-----\n"])

        except (configparser.MissingSectionHeaderError, configparser.ParsingError, ValueError, OSError):
            message_list.extend([f"[!] CAUTION : YOUR {ini_name} FILE IS VERY LIKELY BROKEN, PLEASE CREATE A NEW ONE \n",
                                 f"    Delete this file from your Documents/My Games/{game_docs_name} folder, then press \n",
                                 f"    *Scan Game Files* in CLASSIC to generate a new {ini_name} file. \n-----\n"])
    else:
        if ini_name.lower() == f"{game_docs_name.lower()}.ini":
            message_list.extend([f"❌ CAUTION : {ini_name} FILE IS MISSING FROM YOUR DOCUMENTS FOLDER! \n",
                                 f"   You need to run the game at least once with {game_docs_name}Launcher.exe \n",
                                 "    This will create files and INI settings required for the game to run. \n-----\n"])

        if ini_name.lower() == f"{game_docs_name.lower()}custom.ini":
            with open(ini_path, "a", encoding="utf-8", errors="ignore") as ini_file:
                message_list.extend(["❌ WARNING : Archive Invalidation / Loose Files setting is not enabled. \n",
                                     "  CLASSIC will now enable this setting automatically in the game INI files. \n-----\n"])
                customini_config = yaml_get("CLASSIC Data/databases/CLASSIC FO4.yaml", "Default_FO4Custom")
                ini_file.write(customini_config)

    message_output = "".join(message_list)
    return message_output


# =========== OTHER ===========
def main_combined_result():
    combined_return = [game_check_integrity(), xse_check_integrity(), xse_check_hashes(),
                       docs_check_ini("Fallout4.ini"), docs_check_ini("Fallout4Custom.ini"), docs_check_ini("Fallout4Prefs.ini")]
    combined_result = "".join(combined_return)
    return combined_result


def main_generate_required():
    configure_logging()
    classic_logging()
    classic_data_extract()
    classic_ver = yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info", "version")
    print(f"Hello World! | Crash Log Auto Scanner & Setup Integrity Checker | {classic_ver} | Fallout 4")
    print("REMINDER: COMPATIBLE CRASH LOGS MUST START WITH 'crash-' AND MUST HAVE .log EXTENSION \n")
    print("❓ PLEASE WAIT WHILE CLASSIC CHECKS YOUR SETTINGS AND GAME SETUP...")
    logging.debug(f"> > > STARTED {classic_ver}")

    classic_settings()
    classic_ignorefile()
    if not classic_settings("VR Mode"):
        root_folder_game = yaml_get("CLASSIC Data/CLASSIC FO4 Local.yaml", "Game_Info", "Root_Folder_Game")
    else:
        root_folder_game = yaml_get("CLASSIC Data/CLASSIC FO4VR Local.yaml", "GameVR_Info", "Root_Folder_Game")

    if not root_folder_game:
        docs_path_find()
        docs_generate_paths()
        game_path_find()
        game_generate_paths()

    print("✔️ ALL CLASSIC AND GAME SETTINGS CHECKS HAVE BEEN PERFORMED!")
    print("    YOU CAN NOW SCAN YOUR CRASH LOGS, GAME AND/OR MOD FILES \n")


if __name__ == "__main__":  # AKA only autorun / do the following when NOT imported.
    main_generate_required()
    classic_update_check()
    os.system("pause")