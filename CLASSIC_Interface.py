# CLASSIC GUI WITH PySide6 (NOW WORKS WITH 3.11!)
import sys
import time
import multiprocessing
import soundfile as sfile
import sounddevice as sdev
# sfile and sdev need Numpy
import CLASSIC_Main as CMain
import CLASSIC_ScanGame as CGame
import CLASSIC_ScanLogs as CLogs
from functools import partial
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QUrl, QTimer, Slot
from PySide6.QtGui import QColor, QDesktopServices, QPalette
from PySide6.QtWidgets import QFileDialog
CMain.configure_logging()
'''import platform  # RESERVED FOR FUTURE UPDATE
current_platform = platform.system()
if current_platform == 'Windows':
    version = platform.release()
    if version.startswith('10') or version.startswith('11'):
        QApplication.setStyle("Fusion")
        sys.argv += ['-platform', 'windows:darkmode=2']
'''


# ================================================
# DEFINE WINDOW ELEMENT TEMPLATES HERE
# ================================================
def create_custom_line_edit(parent, geometry, object_name, text, text_color="black"):
    line_edit = QtWidgets.QLineEdit(parent)
    line_edit.setGeometry(geometry)
    line_edit.setObjectName(object_name)
    line_edit.setText(text)
    palette = line_edit.palette()
    palette.setColor(QPalette.Text, QColor(text_color))  # type: ignore
    line_edit.setPalette(palette)
    return line_edit


def create_custom_push_button(parent, geometry, object_name, text, font, tooltip="", callback=None):
    button = QtWidgets.QPushButton(parent)
    button.setGeometry(geometry)
    button.setObjectName(object_name)
    button.setText(text)
    button.setFont(font)
    button.setToolTip(tooltip)
    if callback:
        button.clicked.connect(callback)
    return button


def create_simple_button(parent, geometry, object_name, text, tooltip, callback):
    button = QtWidgets.QPushButton(parent)
    button.setGeometry(geometry)
    button.setObjectName(object_name)
    button.setText(text)
    button.setToolTip(tooltip)
    button.clicked.connect(callback)
    return button


def create_custom_frame(parent, geometry, frame_shape, frame_shadow, object_name):
    frame = QtWidgets.QFrame(parent)
    frame.setGeometry(geometry)
    frame.setFrameShape(frame_shape)
    frame.setFrameShadow(frame_shadow)
    frame.setObjectName(object_name)
    return frame


def create_custom_label(parent, geometry, text, font, object_name):
    label = QtWidgets.QLabel(parent)
    label.setGeometry(geometry)
    label.setText(text)
    label.setFont(font)
    label.setObjectName(object_name)
    return label


def create_custom_check_box(parent, geometry, text, tooltip, checked, object_name, disabled=False):
    check_box = QtWidgets.QCheckBox(parent)
    check_box.setGeometry(geometry)
    check_box.setText(text)
    check_box.setToolTip(tooltip)
    if checked and not disabled:
        check_box.setChecked(True)
    check_box.setObjectName(object_name)
    if disabled:
        check_box.setEnabled(False)
        check_box.setChecked(False)
        check_box.setStyleSheet("color: gray;")
    return check_box


def create_label(parent, text, geometry):
    label = QtWidgets.QLabel(parent)
    label.setGeometry(geometry)
    label.setObjectName("label")
    label.setText(text)
    return label


def create_text_browser(parent, geometry, text):
    text_browser = QtWidgets.QTextBrowser(parent)
    text_browser.setGeometry(geometry)
    text_browser.setObjectName("text_browser")
    text_browser.setPlainText(text)
    return text_browser


def papyrus_worker(q, stop_event):
    while not stop_event.is_set():
        papyrus_result = CGame.papyrus_logging()
        q.put(papyrus_result)
        time.sleep(3)


def play_sound(sound_file):
    sound, samplerate = sfile.read(f"CLASSIC Config/{sound_file}")
    sdev.play(sound, samplerate)
    sdev.wait()


# ================================================
# CLASSIC MAIN WINDOW
# ================================================
class UiCLASSICMainWin(object):
    def __init__(self, classic_main_win):
        # MAIN WINDOW
        classic_ver = CMain.yaml_get("CLASSIC Config/CLASSIC Main.yaml", "CLASSIC_Info", "version")
        classic_main_win.setObjectName("CLASSIC_MainWin")
        classic_main_win.setWindowTitle(f"Crash Log Auto Scanner & Setup Integrity Checker | {classic_ver}")
        classic_main_win.resize(640, 800)
        classic_main_win.setMinimumSize(QtCore.QSize(640, 800))
        classic_main_win.setMaximumSize(QtCore.QSize(640, 800))
        classic_main_win.setWindowFlags(classic_main_win.windowFlags() | Qt.WindowMinimizeButtonHint)  # type: ignore
        # MULTIPROCESSING
        self.papyrus_process = None
        self.monitoring_flag = multiprocessing.Value('i', 1)  # Shared Flag Variable

        # ==================== MAIN WINDOW ITEMS =====================
        # TOP

        # Text Box - Selected Folder
        font_bold_10 = QtGui.QFont()
        font_bold_10.setPointSize(10)
        font_bold_10.setBold(True)
        font_10 = QtGui.QFont()
        font_10.setPointSize(10)

        # SEPARATOR STAGING MODS FOLDER
        self.LBL_ModsFolder = create_custom_label(classic_main_win, QtCore.QRect(20, 30, 260, 16), "STAGING MODS FOLDER", font_bold_10, "LBL_ModsFolder")
        self.Line_Sep_Mods = create_custom_frame(classic_main_win, QtCore.QRect(40, 80, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Mods")
        # BROWSE STAGING MODS FOLDER
        self.Box_SelectedMods = create_custom_line_edit(classic_main_win, QtCore.QRect(20, 50, 450, 22), "Box_SelectedMods", "(Optional) Press 'Browse Folder...' to set your staging mods folder location.", "darkgray")
        self.RegBT_BrowseMods = create_simple_button(classic_main_win, QtCore.QRect(490, 50, 130, 24), "RegBT_BrowseMods", "Browse Folder...", "", self.select_folder_mods)

        # SEPARATOR CUSTOM SCAN FOLDER
        self.LBL_ScanFolder = create_custom_label(classic_main_win, QtCore.QRect(20, 100, 260, 16), "CUSTOM SCAN FOLDER", font_bold_10, "LBL_ScanFolder")
        self.Line_Sep_Scan = create_custom_frame(classic_main_win, QtCore.QRect(40, 150, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Scan")
        # BROWSE CUSTOM SCAN FOLDER
        self.Box_SelectedScan = create_custom_line_edit(classic_main_win, QtCore.QRect(20, 120, 450, 22), "Box_SelectedScan", "(Optional) Press 'Browse Folder...' to set a different scan folder location.", "darkgray")
        self.RegBT_BrowseScan = create_simple_button(classic_main_win, QtCore.QRect(490, 120, 130, 24), "RegBT_BrowseScan", "Browse Folder...", "", self.select_folder_scan)

        # TOP MAIN ROW
        self.RegBT_SCAN_LOGS = create_custom_push_button(classic_main_win, QtCore.QRect(35, 185, 270, 48), "RegBT_SCAN_LOGS", "SCAN CRASH LOGS", font_bold_10, "", self.crash_logs_scan)
        self.RegBT_SCAN_FILES = create_custom_push_button(classic_main_win, QtCore.QRect(335, 185, 270, 48), "RegBT_SCAN_FILES", "SCAN GAME FILES", font_bold_10, "", self.game_files_scan)
        # BOTTOM MAIN ROW
        self.RegBT_ChangeINI = create_custom_push_button(classic_main_win, QtCore.QRect(35, 250, 150, 32), "RegBT_ChangeINI", "CHANGE INI PATH", font_10, "Select the folder where Fallout4.ini is located so CLASSIC can use that new folder location.", self.select_folder_ini)
        self.RegBT_CheckUpdates = create_custom_push_button(classic_main_win, QtCore.QRect(455, 250, 150, 32), "RegBT_CheckUpdates", "CHECK FOR UPDATES", font_10, "", self.update_popup)

        # CHECK EXISTING BROWSE PATHS
        SCAN_folder = CMain.classic_settings("SCAN Custom Path")
        if SCAN_folder:
            self.Box_SelectedScan.setText(SCAN_folder.strip())
            palette = self.Box_SelectedScan.palette()
            palette.setColor(QPalette.Text, QColor(Qt.black))
            self.Box_SelectedScan.setPalette(palette)
        MODS_folder = CMain.classic_settings("MODS Folder Path")
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder.strip())
            palette = self.Box_SelectedMods.palette()
            palette.setColor(QPalette.Text, QColor(Qt.black))
            self.Box_SelectedMods.setPalette(palette)

        # SEGMENT - SETTINGS
        self.Line_Sep_Settings = create_custom_frame(classic_main_win, QtCore.QRect(40, 300, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Settings")
        self.LBL_Settings = create_custom_label(classic_main_win, QtCore.QRect(260, 320, 180, 16), "CLASSIC SETTINGS", font_bold_10, "LBL_Settings")
        # Column 1
        self.ChkBT_FCXMode = create_custom_check_box(classic_main_win, QtCore.QRect(90, 350, 150, 20), "FCX MODE", "Enable if you want CLASSIC to check the integrity of your game and mod files.", CMain.classic_settings("FCX Mode"), "ChkBT_FCXMode")
        self.ChkBT_VRMode = create_custom_check_box(CLASSIC_MainWin, QtCore.QRect(90, 380, 150, 20), "VR MODE", "Enable if you want CLASSIC to prioritize scanning the Virtual Reality (VR) version of your game.", CMain.classic_settings("Show Statistics"), "ChkBT_VRMode")
        # Column 2
        self.ChkBT_SimpleLogs = create_custom_check_box(classic_main_win, QtCore.QRect(260, 350, 150, 20), "SIMPLIFY LOGS", "Enable if you want CLASSIC to remove some unnecessary info from your crash log files.", CMain.classic_settings("Simplify Logs"), "ChkBT_SimpleLogs")
        self.ChkBT_ShowFormID = create_custom_check_box(classic_main_win, QtCore.QRect(260, 380, 150, 20), "SHOW FID VALUES", "Enable if you want CLASSIC to look up FormID values (names) while scanning crash logs.", CMain.classic_settings("Show FormID Values"), "ChkBT_ShowFormID")
        # Column 3
        self.ChkBT_Update = create_custom_check_box(classic_main_win, QtCore.QRect(430, 350, 150, 20), "UPDATE CHECK", "Enable if you want CLASSIC to periodically check for its own updates online through GitHub.", CMain.classic_settings("Update Check"), "ChkBT_Update")
        self.ChkBT_Unsolved = create_custom_check_box(classic_main_win, QtCore.QRect(430, 380, 150, 20), "MOVE INVALID LOGS", "Enable if you want CLASSIC to move all invalid crash logs to CLASSIC Misc folder.)", CMain.classic_settings("Move Unsolved Logs"), "ChkBT_Unsolved")

        # SEPARATOR WEBSITE LINKS
        self.Line_Sep_Links = create_custom_frame(classic_main_win, QtCore.QRect(40, 410, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Links")
        self.LBL_ArtWeb = create_custom_label(classic_main_win, QtCore.QRect(205, 430, 260, 16), "ARTICLES / WEBSITES / NEXUS LINKS", font_bold_10, "LBL_ArtWeb")

        # Articles & Websites - ADD LINK BUTTONS FOR BETHINI, DDS SCANNER & WRYE BASH
        button_data = [
            {"text": "BUFFOUT 4 INSTALLATION", "url": "https://www.nexusmods.com/fallout4/articles/3115"},
            {"text": "ADVANCED TROUBLESHOOTING", "url": "https://www.nexusmods.com/fallout4/articles/4141"},
            {"text": "IMPORTANT PATCHES LIST", "url": "https://www.nexusmods.com/fallout4/articles/3769"},
            {"text": "BUFFOUT 4 NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/47359"},
            {"text": "CLASSIC NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/56255"},
            {"text": "CLASSIC GITHUB", "url": "https://github.com/GuidanceOfGrace/Buffout4-CLAS/releases"},
            {"text": "DDS TEXTURE SCANNER", "url": "https://www.nexusmods.com/fallout4/mods/71588"},
            {"text": "BETHINI TOOL", "url": "https://www.nexusmods.com/fallout4/mods/67"},
            {"text": "WRYE BASH TOOL", "url": "https://www.nexusmods.com/fallout4/mods/20032"}
        ]

        # ARRANGE BUTTONS IN GRID
        for i, data in enumerate(button_data):
            font = QtGui.QFont()
            font.setPointSize(8)
            button = QtWidgets.QPushButton(classic_main_win)
            button.setGeometry(QtCore.QRect(40 + i % 3 * 190, 460 + i // 3 * 50, 180, 32))
            button.setObjectName("ArtBT_" + data["text"].replace(" ", ""))
            button.setFont(font)
            button.setText(data["text"])
            open_url = partial(QDesktopServices.openUrl, QUrl(data["url"]))
            button.clicked.connect(open_url)

        # BOTTOM

        # Button - HELP
        self.RegBT_Help = create_custom_push_button(classic_main_win, QtCore.QRect(20, 620, 110, 30), "RegBT_Help", "HELP", font_10, "How To Use CLASSIC GUI", self.help_popup)
        # Button - PAPYRUS MONITORING
        self.RegBT_Papyrus = create_custom_push_button(classic_main_win, QtCore.QRect(205, 620, 220, 30), "RegBT_Papyrus", "START PAPYRUS MONITORING", font_bold_10, "PLACEHOLDER", self.toggle_papyrus_worker)
        # Button - EXIT
        self.RegBT_Exit = create_custom_push_button(classic_main_win, QtCore.QRect(510, 620, 110, 30), "RegBT_Exit", "EXIT", font_10, "Exit CLASSIC GUI", classic_main_win.close)

        # Usage
        self.TXT_Window = create_text_browser(classic_main_win, QtCore.QRect(20, 660, 600, 120), "Crash Log Auto Scanner & Setup Integrity Checker | Made by: Poet \nContributors: evildarkarchon | kittivelae | AtomicFallout757")

        # ====================== CHECK BOXES ========================
        # Column 1
        self.ChkBT_FCXMode.clicked.connect(lambda: self.update_yaml_config(self.ChkBT_FCXMode, "FCX Mode"))
        self.ChkBT_VRMode.clicked.connect(lambda: self.update_yaml_config(self.ChkBT_VRMode, "VR Mode"))
        # Column 2
        self.ChkBT_SimpleLogs.clicked.connect(lambda: self.update_yaml_config(self.ChkBT_SimpleLogs, "Simplify Logs"))
        self.ChkBT_ShowFormID.clicked.connect(lambda: self.update_yaml_config(self.ChkBT_ShowFormID, "Show FormID Values"))
        # Column 3
        self.ChkBT_Unsolved.clicked.connect(lambda: self.update_yaml_config(self.ChkBT_Unsolved, "Move Unsolved Logs"))
        self.ChkBT_Update.clicked.connect(lambda: self.update_yaml_config(self.ChkBT_Update, "Update Check"))

        QtCore.QMetaObject.connectSlotsByName(classic_main_win)

        # ================= PAPYRUS WORKER =================
        self.result_queue = multiprocessing.Queue()
        self.worker_stop_event = multiprocessing.Event()
        self.worker_process = None

        self.timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.update_text_window)
        self.timer.start(5000)  # Update every 5 seconds.

        self.is_worker_running = False

    # ================= MAIN BUTTON FUNCTIONS ===================
    # @staticmethod recommended for func that don't call "self".

    @staticmethod
    def update_yaml_config(checkbox, config_key):
        if checkbox.isChecked():
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.{config_key}", True)
        else:
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.{config_key}", False)

    @staticmethod
    def crash_logs_scan():
        CLogs.crashlogs_scan()
        play_sound("classic_notify.wav")

    @staticmethod
    def game_files_scan():
        print(CGame.game_combined_result())
        print(CGame.mods_combined_result())
        play_sound("classic_notify.wav")

    @Slot()
    def toggle_papyrus_worker(self):
        if not self.is_worker_running:
            self.worker_stop_event.clear()
            self.worker_process = multiprocessing.Process(target=papyrus_worker, args=(self.result_queue, self.worker_stop_event))
            self.worker_process.daemon = True
            self.worker_process.start()
            self.RegBT_Papyrus.setText("STOP PAPYRUS MONITORING")
        else:
            self.worker_stop_event.set()
            self.worker_process.join()
            self.worker_process = None
            self.RegBT_Papyrus.setText("START PAPYRUS MONITORING")
        self.is_worker_running = not self.is_worker_running

    def update_text_window(self):
        while not self.result_queue.empty():
            queue_result = self.result_queue.get()  # papyrus_result
            old_papyrus_text = self.TXT_Window.toPlainText()
            new_papyrus_text, new_dump_count = queue_result[:2]
            old_dump_count = next((line for line in old_papyrus_text.split("\n") if "DUMPS" in line), None)
            if old_dump_count and new_dump_count > int(old_dump_count.split(" : ")[1]):
                play_sound("classic_error.wav")
                time.sleep(3)
            self.TXT_Window.setPlainText(new_papyrus_text)

    def select_folder_scan(self):
        SCAN_folder = QFileDialog.getExistingDirectory()
        if SCAN_folder:
            self.Box_SelectedScan.setText(SCAN_folder)
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.SCAN Custom Path", SCAN_folder)
            TXT_palette = self.Box_SelectedScan.palette()
            TXT_palette.setColor(QPalette.ColorRole.Text, QColor("black"))
            self.Box_SelectedScan.setPalette(TXT_palette)

    def select_folder_mods(self):
        MODS_folder = QFileDialog.getExistingDirectory()
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder)
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.MODS Folder Path", MODS_folder)
            TXT_palette = self.Box_SelectedMods.palette()
            TXT_palette.setColor(QPalette.ColorRole.Text, QColor("black"))
            self.Box_SelectedMods.setPalette(TXT_palette)

    @staticmethod
    def select_folder_ini():
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(CLASSIC_MainWin, "New INI Path Set", "You have set the new path to: \n" + INI_folder)
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.INI Folder Path", INI_folder)

        # ================== POP-UPS / WARNINGS =====================

    @staticmethod
    def help_popup():
        help_popup_text = CMain.yaml_get("CLASSIC Config/CLASSIC Main.yaml", "CLASSIC_Interface", "help_popup_text")
        QtWidgets.QMessageBox.information(CLASSIC_MainWin, "Need Help?", help_popup_text)
        QDesktopServices.openUrl(QUrl("https://discord.com/invite/7ZZbrsGQh4"))

    @staticmethod
    def update_popup():
        update_popup_text = CMain.yaml_get("CLASSIC Config/CLASSIC Main.yaml", "CLASSIC_Interface", "update_popup_text")
        if CMain.classic_update_version():
            QtWidgets.QMessageBox.information(CLASSIC_MainWin, "CLASSIC Update", "You have the latest version of CLASSIC!")
        else:
            QtWidgets.QMessageBox.warning(CLASSIC_MainWin, "CLASSIC Update", update_popup_text)
            QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255?tab=files"))


if __name__ == "__main__":
    CMain.main_generate_required()
    gui_message = """\
PRESS *SCAN CRASH LOGS* BUTTON TO SCAN ALL AVAILABLE BUFFOUT 4 CRASH LOGS

PRESS *SCAN GAME FILES* BUTTON TO CHECK YOUR FALLOUT 4 GAME & MOD FILES

IF YOU ARE USING MOD ORGANIZER 2, YOU NEED TO RUN CLASSIC WITH THE MO2 SHORTCUT
CHECK THE INCLUDED CLASSIC Readme.md FILE FOR MORE DETAILS AND INSTRUCTIONS
"""
    print(gui_message)
    app = QtWidgets.QApplication(sys.argv)
    CLASSIC_MainWin = QtWidgets.QDialog()
    ui = UiCLASSICMainWin(CLASSIC_MainWin)
    CLASSIC_MainWin.show()
    sys.exit(app.exec())