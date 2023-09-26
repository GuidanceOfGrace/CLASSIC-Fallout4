# CLASSIC GUI WITH PySide6 (NOW WORKS WITH 3.11!)
import os
import sys
import time
import platform
import subprocess
import multiprocessing
import soundfile as sfile
import sounddevice as sdev
# sfile and sdev need Numpy
import CLASSIC_Main as CMain
import CLASSIC_ScanGame as CGame
import CLASSIC_ScanLogs as CLogs
from pathlib import Path
from functools import partial
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QUrl, QTimer, Slot
from PySide6.QtGui import QDesktopServices, QPixmap, QIcon
from PySide6.QtWidgets import QDialog, QFileDialog, QSizePolicy, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton

CMain.configure_logging()

# FONTS CONFIG
bold_11 = QtGui.QFont()
bold_11.setPointSize(11)
bold_11.setBold(True)
normal_11 = QtGui.QFont()
normal_11.setPointSize(11)
bold_09 = QtGui.QFont()
bold_09.setPointSize(9)
bold_09.setBold(True)


# ================================================
# DEFINE WINDOW ELEMENT TEMPLATES HERE
# ================================================
def custom_line_box(parent, geometry, object_name, text):
    line_edit = QtWidgets.QLineEdit(parent)
    line_edit.setGeometry(geometry)
    line_edit.setObjectName(object_name)
    line_edit.setText(text)
    return line_edit


def custom_push_button(parent, geometry, object_name, text, font, tooltip="", callback=None):
    button = QtWidgets.QPushButton(parent)
    button.setObjectName(object_name)
    button.setGeometry(geometry)
    button.setToolTip(tooltip)
    button.setText(text)
    button.setFont(font)
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    button.setStyleSheet("color: white; background: rgba(10, 10, 10, 0.75); border-radius: 10px; border : 1px solid white; font-family: Yu Gothic")
    if callback:
        button.clicked.connect(callback)
    return button


def custom_frame(parent, geometry, frame_shape, frame_shadow, object_name):
    frame = QtWidgets.QFrame(parent)
    frame.setGeometry(geometry)
    frame.setFrameShape(frame_shape)
    frame.setFrameShadow(frame_shadow)
    frame.setObjectName(object_name)
    return frame


def custom_label(parent, geometry, text, font, object_name):
    label = QtWidgets.QLabel(parent)
    label.setGeometry(geometry)
    label.setText(text)
    label.setFont(font)
    label.setObjectName(object_name)
    label.setStyleSheet("color: white; font-family: Yu Gothic")
    return label


def custom_popup_window(parent, title, text, height=250, callback=""):
    popup_window = QDialog(parent)
    popup_window.setWindowTitle(title)
    popup_window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    popup_window.setStyleSheet("color: white; background: rgba(10, 10, 10, 1); border : 1px solid black; font-size: 15px")
    popup_window.setGeometry(15, 300, 620, height)

    layout = QVBoxLayout()
    label = QLabel(text, popup_window)
    # label.setAlignment(Qt.AlignTop)
    label.setWordWrap(True)

    # Create a horizontal layout for buttons
    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    ok_button.setMinimumSize(100, 50)
    ok_button.setStyleSheet("color: black; background: rgb(45, 237, 138); font-size: 20px; font-weight: bold")

    close_button = QPushButton("Close")
    close_button.setMinimumSize(100, 50)
    close_button.setStyleSheet("color: black; background: rgb(240, 63, 40); font-size: 20px; font-weight: bold")

    # Connect button signals to actions
    if callback:
        ok_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(callback)))
    else:
        ok_button.clicked.connect(popup_window.accept)
    close_button.clicked.connect(popup_window.reject)

    # Add buttons to the horizontal layout
    button_layout.addWidget(ok_button)
    button_layout.addWidget(close_button)

    # Add widgets to the main layout
    layout.addWidget(label)
    layout.addLayout(button_layout)
    popup_window.setLayout(layout)
    return popup_window


def custom_text_box(parent, geometry, text):
    text_browser = QtWidgets.QTextBrowser(parent)
    text_browser.setGeometry(geometry)
    text_browser.setObjectName("text_browser")
    text_browser.setText(text)
    text_browser.setStyleSheet("color: white; background: rgba(10, 10, 10, 0.75); border-radius: 10px; border : 1px solid white; font-size: 15px")
    return text_browser


def custom_checkbox_widget(parent, pos_x=250, pos_y=250, size=25, check="", label_text="TEST LABEL"):
    checkbox_widget = QWidget(parent)
    checkbox_widget.setGeometry(pos_x, pos_y, 200, 50)
    layout = QHBoxLayout(checkbox_widget)

    # Create QLabel for image & text.
    image_label = QLabel()
    pixmap0 = QPixmap("CLASSIC Data/graphics/unchecked.png")
    pixmap1 = QPixmap("CLASSIC Data/graphics/checked.png")

    image_label.setPixmap(pixmap0)
    image_label.setFixedSize(size, size)
    text_label = QLabel(label_text)
    text_label.setStyleSheet("color: white; font-family: Yu Gothic")

    # Add image & text labels to layout.
    layout.addWidget(image_label)
    layout.addWidget(text_label)
    checkbox_widget.setLayout(layout)

    # Check assigned YAML setting.
    status = CMain.classic_settings(check)
    if status:
        image_label.setPixmap(pixmap1)
    else:
        image_label.setPixmap(pixmap0)

    # Toggle assigned YAML setting.
    def toggle_setting(_):
        nonlocal check
        # Toggle between images when label is clicked.
        if CMain.classic_settings(check):
            CMain.yaml_settings("CLASSIC Settings.yaml", f"CLASSIC_Settings.{check}", False)
            image_label.setPixmap(pixmap0)
        else:
            CMain.yaml_settings("CLASSIC Settings.yaml", f"CLASSIC_Settings.{check}", True)
            image_label.setPixmap(pixmap1)

    image_label.mousePressEvent = toggle_setting
    return checkbox_widget


def papyrus_worker(q, stop_event):
    while not stop_event.is_set():
        papyrus_result = CGame.papyrus_logging()
        q.put(papyrus_result)
        time.sleep(3)


def play_sound(sound_file):
    sound, samplerate = sfile.read(f"CLASSIC Data/sounds/{sound_file}")
    sdev.play(sound, samplerate)
    sdev.wait()


# ================================================
# CLASSIC MAIN WINDOW
# ================================================
class UiCLASSICMainWin(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # MULTIPROCESSING
        self.papyrus_process = None
        self.monitoring_flag = multiprocessing.Value('i', 1)  # Shared Flag Variable

        # BACKGROUND CONFIG
        image_path = "CLASSIC Data/graphics/background.png"
        self.background_label = QtWidgets.QLabel(self)
        self.setCentralWidget(self.background_label)
        pixmap = QtGui.QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # ==================== MAIN WINDOW ITEMS =====================
        # TABS / SCREENS
        self.RegButton_TabMain = custom_push_button(self, QtCore.QRect(0, 0, 325, 48), "RegButton_TabMain", "MAIN OPTIONS", bold_11, "")
        self.RegButton_TabMain.setStyleSheet("color: white; background: rgba(25, 25, 25, 0.90); border-radius: 0px; border : 2px solid white; font-size: 15px")

        self.RegButton_TabBackups = custom_push_button(self, QtCore.QRect(325, 0, 325, 48), "RegButton_TabBackups", "FILE BACKUP", bold_11, "", self.open_tab_backups)
        self.RegButton_TabBackups.setStyleSheet("color: white; background: rgba(10, 10, 10, 0.90); border-radius: 0px; border : 2px dashed white; font-size: 15px")

        # TOP

        # SEPARATOR STAGING MODS FOLDER
        self.LBL_ModsFolder = custom_label(self, QtCore.QRect(20, 80, 260, 20), "STAGING MODS FOLDER", bold_11, "LBL_ModsFolder")
        self.Line_Sep_Mods = custom_frame(self, QtCore.QRect(30, 130, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Mods")
        # BROWSE STAGING MODS FOLDER
        self.Box_SelectedMods = custom_line_box(self, QtCore.QRect(20, 100, 450, 24), "Box_SelectedMods", "(Optional) Press *Browse Folder* to set your staging mods folder location.")
        self.Box_SelectedMods.setStyleSheet("color: darkgray")
        self.RegButton_BrowseMods = custom_push_button(self, QtCore.QRect(490, 100, 130, 24), "RegButton_BrowseMods", "Browse Folder", normal_11, "", self.select_folder_mods)

        # SEPARATOR CUSTOM SCAN FOLDER
        self.LBL_ScanFolder = custom_label(self, QtCore.QRect(20, 155, 260, 20), "CUSTOM SCAN FOLDER", bold_11, "LBL_ScanFolder")
        self.Line_Sep_Scan = custom_frame(self, QtCore.QRect(30, 205, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Scan")
        # BROWSE CUSTOM SCAN FOLDER
        self.Box_SelectedScan = custom_line_box(self, QtCore.QRect(20, 175, 450, 24), "Box_SelectedScan", "(Optional) Press *Browse Folder* to set a different scan folder location.")
        self.Box_SelectedScan.setStyleSheet("color: darkgray")
        self.RegButton_BrowseScan = custom_push_button(self, QtCore.QRect(490, 175, 130, 24), "RegButton_BrowseScan", "Browse Folder", normal_11, "", self.select_folder_scan)

        # TOP MAIN ROW
        self.RegButton_SCAN_LOGS = custom_push_button(self, QtCore.QRect(35, 245, 270, 48), "RegButton_SCAN_LOGS", "SCAN CRASH LOGS", bold_11, "", self.crash_logs_scan)
        self.RegButton_SCAN_LOGS.setStyleSheet("color: black; background: rgba(250, 250, 250, 0.90); border-radius: 10px; border : 1px solid white; font-size: 17px")
        self.RegButton_SCAN_FILES = custom_push_button(self, QtCore.QRect(345, 245, 270, 48), "RegButton_SCAN_FILES", "SCAN GAME FILES", bold_11, "", self.game_files_scan)
        self.RegButton_SCAN_FILES.setStyleSheet("color: black; background: rgba(250, 250, 250, 0.90); border-radius: 10px; border : 1px solid white; font-size: 17px")

        # BOTTOM MAIN ROW
        self.RegButton_ChangeINI = custom_push_button(self, QtCore.QRect(35, 310, 150, 32), "RegButton_ChangeINI", "CHANGE INI PATH", bold_09, "Select folder of the game's main INI files so CLASSIC can use that location.", self.select_folder_ini)
        self.RegButton_OpenSettings = custom_push_button(self, QtCore.QRect(220, 310, 210, 32), "RegButton_OpenSettings", "OPEN CLASSIC SETTINGS", bold_09, "Open the CLASSIC Settings.yaml file in your default text editor.", self.open_settings)
        self.RegButton_CheckUpdates = custom_push_button(self, QtCore.QRect(465, 310, 150, 32), "RegButton_CheckUpdates", "CHECK UPDATES", bold_09, "Check for new CLASSIC versions (CLASSIC does this automatically every 7 days).", self.update_popup)

        # CHECK EXISTING BROWSE PATHS
        SCAN_folder = CMain.classic_settings("SCAN Custom Path")
        if SCAN_folder:
            self.Box_SelectedScan.setText(SCAN_folder.strip())
            self.Box_SelectedScan.setStyleSheet("color: black")
        MODS_folder = CMain.classic_settings("MODS Folder Path")
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder.strip())
            self.Box_SelectedMods.setStyleSheet("color: black")

        # SEGMENT - SETTINGS
        self.Line_Sep_Settings = custom_frame(self, QtCore.QRect(30, 360, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Settings")
        self.LBL_Settings = custom_label(self, QtCore.QRect(260, 380, 180, 16), "CLASSIC SETTINGS", bold_11, "LBL_Settings")
        # CHECKBOXES - Column 1
        self.ChkBT_FCXMode = custom_checkbox_widget(self, pos_x=70, pos_y=400, label_text="FCX MODE", check="FCX Mode")
        self.ChkBT_VRMode = custom_checkbox_widget(self, pos_x=70, pos_y=450, label_text="VR MODE", check="VR Mode")
        # CHECKBOXES - Column 2
        self.ChkBT_SimpleLogs = custom_checkbox_widget(self, pos_x=250, pos_y=400, label_text="SIMPLIFY LOGS", check="Simplify Logs")
        self.ChkBT_ShowFormID = custom_checkbox_widget(self, pos_x=250, pos_y=450, label_text="SHOW FID VALUES", check="Show FormID Values")
        # CHECKBOXES - Column 3
        self.ChkBT_Update = custom_checkbox_widget(self, pos_x=430, pos_y=400, label_text="UPDATE CHECK", check="Update Check")
        self.ChkBT_Unsolved = custom_checkbox_widget(self, pos_x=430, pos_y=450, label_text="MOVE INVALID LOGS", check="Move Unsolved Logs")

        # SEPARATOR WEBSITE LINKS
        self.Line_Sep_Links = custom_frame(self, QtCore.QRect(30, 510, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Links")
        self.LBL_ArtWeb = custom_label(self, QtCore.QRect(200, 530, 590, 20), "ARTICLES / WEBSITES / NEXUS LINKS", bold_11, "LBL_ArtWeb")

        # Articles & Websites - ADD LINK BUTTONS FOR BETHINI, DDS SCANNER & WRYE BASH
        button_data = [
            {"text": "BUFFOUT 4 INSTALLATION", "url": "https://www.nexusmods.com/fallout4/articles/3115"},
            {"text": "FALLOUT 4 SETUP TIPS", "url": "https://www.nexusmods.com/fallout4/articles/4141"},
            {"text": "IMPORTANT PATCHES LIST", "url": "https://www.nexusmods.com/fallout4/articles/3769"},
            {"text": "BUFFOUT 4 NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/47359"},
            {"text": "CLASSIC NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/56255"},
            {"text": "CLASSIC GITHUB", "url": "https://github.com/GuidanceOfGrace/CLASSIC-Fallout4"},
            {"text": "DDS TEXTURE SCANNER", "url": "https://www.nexusmods.com/fallout4/mods/71588"},
            {"text": "BETHINI TOOL", "url": "https://www.nexusmods.com/site/mods/631"},
            {"text": "WRYE BASH TOOL", "url": "https://www.nexusmods.com/fallout4/mods/20032"}
        ]

        # ARRANGE BUTTONS IN GRID
        for i, data in enumerate(button_data):
            button = QtWidgets.QPushButton(self)
            button.setGeometry(QtCore.QRect(45 + i % 3 * 190, 570 + i // 3 * 60, 180, 50))
            button.setObjectName("ArtBT_" + data["text"].replace(" ", ""))
            button.setText(data["text"])
            button.setStyleSheet("color: white; border-radius: 5px; border : 1px solid white; font-size: 11px; font-weight: bold")
            open_url = partial(QDesktopServices.openUrl, QUrl(data["url"]))
            button.clicked.connect(open_url)

        # BOTTOM

        # Button - HELP
        self.RegButton_Help = custom_push_button(self, QtCore.QRect(20, 770, 110, 30), "RegButton_Help", "HELP", normal_11, "", self.help_popup_main)
        # Button - PAPYRUS MONITORING
        self.RegButton_Papyrus = custom_push_button(self, QtCore.QRect(195, 770, 260, 30), "RegButton_Papyrus", "START PAPYRUS MONITORING", bold_11, "", self.toggle_papyrus_worker)
        self.RegButton_Papyrus.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px; border : 1px solid black")
        # Button - EXIT
        self.RegButton_Exit = custom_push_button(self, QtCore.QRect(520, 770, 110, 30), "RegButton_Exit", "EXIT", normal_11, "", lambda: QtWidgets.QApplication.quit())
        # Text Box - SHARED
        self.TXT_Window = custom_text_box(self, QtCore.QRect(20, 810, 610, 120), "Crash Log Auto Scanner & Setup Integrity Checker | Made by: Poet \nContributors: evildarkarchon | kittivelae | AtomicFallout757")

        QtCore.QMetaObject.connectSlotsByName(self)

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
    def open_tab_backups():
        screen_backups = UiCLASSICBackups()
        screen_switch.addWidget(screen_backups)
        screen_switch.setCurrentIndex(screen_switch.currentIndex() + 1)

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
            self.RegButton_Papyrus.setText("STOP PAPYRUS MONITORING")
            self.RegButton_Papyrus.setStyleSheet("background: rgb(240, 63, 40); border-radius: 10px")
        else:
            self.worker_stop_event.set()
            self.worker_process.join()
            self.worker_process = None
            self.RegButton_Papyrus.setText("START PAPYRUS MONITORING")
            self.RegButton_Papyrus.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px")
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
            CMain.yaml_settings("CLASSIC Settings.yaml", f"CLASSIC_Settings.SCAN Custom Path", SCAN_folder)
            self.Box_SelectedScan.setStyleSheet("color: black; font-family: Yu Gothic")

    def select_folder_mods(self):
        MODS_folder = QFileDialog.getExistingDirectory()
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder)
            CMain.yaml_settings("CLASSIC Settings.yaml", f"CLASSIC_Settings.MODS Folder Path", MODS_folder)
            self.Box_SelectedMods.setStyleSheet("color: black; font-family: Yu Gothic")

    def select_folder_ini(self):
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(self, "New INI Path Set", "You have set the new path to: \n" + INI_folder)
            CMain.yaml_settings("CLASSIC Settings.yaml", f"CLASSIC_Settings.INI Folder Path", INI_folder)

        # ================== POP-UPS / WARNINGS =====================

    @staticmethod
    def open_settings():
        settings_file = "CLASSIC Settings.yaml"
        if platform.system() == "Windows":
            subprocess.run(["start", "", settings_file], shell=True)
        else:
            subprocess.Popen(["xdg-open", settings_file])

    def help_popup_main(self):
        help_popup_text = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface.help_popup_main")
        popup = custom_popup_window(self, title="NEED HELP?", text=help_popup_text, height=450, callback="https://discord.com/invite/7ZZbrsGQh4")
        popup.exec()

    def update_popup(self):
        update_popup_text = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface.update_popup_text")
        if CMain.classic_update_check():
            popup = custom_popup_window(self, title="CLASSIC UPDATE", text="You have the latest version of CLASSIC!")
            popup.exec()
        else:
            popup = custom_popup_window(self, title="CLASSIC UPDATE", text=update_popup_text, callback="https://www.nexusmods.com/fallout4/mods/56255?tab=files")
            popup.exec()


class UiCLASSICBackups(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # BACKGROUND CONFIG | UiCLASSICBackups
        image_path = "CLASSIC Data/graphics/background.png"
        self.background_label = QtWidgets.QLabel(self)
        self.setCentralWidget(self.background_label)
        pixmap = QtGui.QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # TABS / SCREENS | UiCLASSICBackups
        self.RegButton_TabMain = custom_push_button(self, QtCore.QRect(0, 0, 325, 48), "RegButton_TabMain", "MAIN OPTIONS", bold_11, "", self.open_tab_mainwin)
        self.RegButton_TabMain.setStyleSheet("color: white; background: rgba(10, 10, 10, 0.90); border-radius: 0px; border : 2px dashed white; font-size: 15px")

        self.RegButton_TabBackups = custom_push_button(self, QtCore.QRect(325, 0, 325, 48), "RegButton_TabBackups", "FILE BACKUP", bold_11, "")
        self.RegButton_TabBackups.setStyleSheet("color: white; background: rgba(25, 25, 25, 0.90); border-radius: 0px; border : 2px solid white; font-size: 15px")

        # EXPLANATIONS | UiCLASSICBackups
        self.LBL_Backup = custom_label(self, QtCore.QRect(30, 65, 590, 20), "BACKUP > Backup files from the game folder into the CLASSIC Backup folder.", normal_11, "LBL_Backup")
        self.LBL_Restore = custom_label(self, QtCore.QRect(30, 85, 590, 20), "RESTORE > Restore file backup from the CLASSIC Backup folder into the game folder.", normal_11, "LBL_Restore")
        self.LBL_Remove = custom_label(self, QtCore.QRect(30, 105, 590, 20), "REMOVE > Remove files only from the game folder without removing existing backups.", normal_11, "LBL_Remove")

        # SCRIPT EXTENDER BACKUP / RESTORE / REMOVE | UiCLASSICBackups
        self.Line_Sep_XSE = custom_frame(self, QtCore.QRect(30, 130, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_XSE")
        self.LBL_XSE = custom_label(self, QtCore.QRect(265, 160, 590, 20), "SCRIPT EXTENDER", bold_11, "LBL_XSE")

        self.RegButton_BackupXSE = custom_push_button(self, QtCore.QRect(30, 205, 180, 48), "RegButton_BackupXSE", "BACKUP XSE", bold_11, "", partial(self.classic_files_manage, "Backup XSE", "BACKUP"))
        self.RegButton_RestoreXSE = custom_push_button(self, QtCore.QRect(235, 205, 180, 48), "RegButton_RestoreXSE", "RESTORE XSE", bold_11, "", partial(self.classic_files_manage, "Backup XSE", "RESTORE"))
        self.RegButton_RestoreXSE.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(250, 250, 250)")
        self.RegButton_RemoveXSE = custom_push_button(self, QtCore.QRect(440, 205, 180, 48), "RegButton_RemoveXSE", "REMOVE XSE", bold_11, "", partial(self.classic_files_manage, "Backup XSE", "REMOVE"))
        self.RegButton_RemoveXSE.setStyleSheet("color: white; border-radius: 10px; border : 2px solid  rgb(240, 63, 40)")

        if os.path.isdir("CLASSIC Backup/Game Files/Backup XSE") and any(Path("CLASSIC Backup/Game Files/Backup XSE").iterdir()):
            self.RegButton_BackupXSE.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px; border : 2px solid black")
            self.RegButton_RestoreXSE.setEnabled(True)
            self.RegButton_RestoreXSE.setStyleSheet("color: black; background: rgb(250, 250, 250); border-radius: 10px; border : 2px solid black;")
        else:
            self.RegButton_BackupXSE.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(45, 237, 138)")
            self.RegButton_RestoreXSE.setEnabled(False)

        # RESHADE BACKUP / RESTORE / REMOVE | UiCLASSICBackups
        self.Line_Sep_RESHADE = custom_frame(self, QtCore.QRect(30, 280, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_RESHADE")
        self.LBL_RESHADE = custom_label(self, QtCore.QRect(295, 310, 590, 20), "RESHADE", bold_11, "LBL_RESHADE")

        self.RegButton_BackupRESHADE = custom_push_button(self, QtCore.QRect(30, 355, 180, 48), "RegButton_BackupRESHADE", "BACKUP RESHADE", bold_11, "", partial(self.classic_files_manage, "Backup RESHADE", "BACKUP"))
        self.RegButton_RestoreRESHADE = custom_push_button(self, QtCore.QRect(235, 355, 180, 48), "RegButton_RestoreRESHADE", "RESTORE RESHADE", bold_11, "", partial(self.classic_files_manage, "Backup RESHADE", "RESTORE"))
        self.RegButton_RestoreRESHADE.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(250, 250, 250)")
        self.RegButton_RemoveRESHADE = custom_push_button(self, QtCore.QRect(440, 355, 180, 48), "RegButton_RemoveRESHADE", "REMOVE RESHADE", bold_11, "", partial(self.classic_files_manage, "Backup RESHADE", "REMOVE"))
        self.RegButton_RemoveRESHADE.setStyleSheet("color: white; border-radius: 10px; border : 2px solid  rgb(240, 63, 40)")

        if os.path.isdir("CLASSIC Backup/Game Files/Backup RESHADE") and any(Path("CLASSIC Backup/Game Files/Backup RESHADE").iterdir()):
            self.RegButton_BackupRESHADE.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px; border : 2px solid black")
            self.RegButton_RestoreRESHADE.setEnabled(True)
            self.RegButton_RestoreRESHADE.setStyleSheet("color: black; background: rgb(250, 250, 250); border-radius: 10px; border : 2px solid black;")
        else:
            self.RegButton_BackupRESHADE.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(45, 237, 138)")
            self.RegButton_RestoreRESHADE.setEnabled(False)

        # VULKAN BACKUP / RESTORE / REMOVE | UiCLASSICBackups
        self.Line_Sep_VULKAN = custom_frame(self, QtCore.QRect(30, 430, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_VULKAN")
        self.LBL_VULKAN = custom_label(self, QtCore.QRect(260, 460, 590, 20), "VULKAN RENDERER", bold_11, "LBL_VULKAN")

        self.RegButton_BackupVULKAN = custom_push_button(self, QtCore.QRect(30, 505, 180, 48), "RegButton_BackupVULKAN", "BACKUP VULKAN", bold_11, "", partial(self.classic_files_manage, "Backup VULKAN", "BACKUP"))
        self.RegButton_RestoreVULKAN = custom_push_button(self, QtCore.QRect(235, 505, 180, 48), "RegButton_RestoreVULKAN", "RESTORE VULKAN", bold_11, "", partial(self.classic_files_manage, "Backup VULKAN", "RESTORE"))
        self.RegButton_RestoreVULKAN.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(250, 250, 250)")
        self.RegButton_RemoveVULKAN = custom_push_button(self, QtCore.QRect(440, 505, 180, 48), "RegButton_RemoveVULKAN", "REMOVE VULKAN", bold_11, "", partial(self.classic_files_manage, "Backup VULKAN", "REMOVE"))
        self.RegButton_RemoveVULKAN.setStyleSheet("color: white; border-radius: 10px; border : 2px solid  rgb(240, 63, 40)")

        if os.path.isdir("CLASSIC Backup/Game Files/Backup VULKAN") and any(Path("CLASSIC Backup/Game Files/Backup VULKAN").iterdir()):
            self.RegButton_BackupVULKAN.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px; border : 2px solid black")
            self.RegButton_RestoreVULKAN.setEnabled(True)
            self.RegButton_RestoreVULKAN.setStyleSheet("color: black; background: rgb(250, 250, 250); border-radius: 10px; border : 2px solid black;")
        else:
            self.RegButton_BackupVULKAN.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(45, 237, 138)")
            self.RegButton_RestoreVULKAN.setEnabled(False)

        # ENB BACKUP / RESTORE / REMOVE | UiCLASSICBackups
        self.Line_Sep_ENB = custom_frame(self, QtCore.QRect(30, 580, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_ENB")
        self.LBL_ENB = custom_label(self, QtCore.QRect(200, 610, 590, 20), "ENHANCED NATURAL BEAUTY ( ENB )", bold_11, "LBL_ENB")

        self.RegButton_BackupENB = custom_push_button(self, QtCore.QRect(30, 655, 180, 48), "RegButton_BackupENB", "BACKUP ENB", bold_11, "", partial(self.classic_files_manage, "Backup ENB", "BACKUP"))
        self.RegButton_RestoreENB = custom_push_button(self, QtCore.QRect(235, 655, 180, 48), "RegButton_RestoreENB", "RESTORE ENB", bold_11, "", partial(self.classic_files_manage, "Backup ENB", "RESTORE"))
        self.RegButton_RestoreENB.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(250, 250, 250)")
        self.RegButton_RemoveENB = custom_push_button(self, QtCore.QRect(440, 655, 180, 48), "RegButton_RemoveENB", "REMOVE ENB", bold_11, "", partial(self.classic_files_manage, "Backup ENB", "REMOVE"))
        self.RegButton_RemoveENB.setStyleSheet("color: white; border-radius: 10px; border : 2px solid  rgb(240, 63, 40)")

        if os.path.isdir("CLASSIC Backup/Game Files/Backup ENB") and any(Path("CLASSIC Backup/Game Files/Backup ENB").iterdir()):
            self.RegButton_BackupENB.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px; border : 2px solid black")
            self.RegButton_RestoreENB.setEnabled(True)
            self.RegButton_RestoreENB.setStyleSheet("color: black; background: rgb(250, 250, 250); border-radius: 10px; border : 2px solid black;")
        else:
            self.RegButton_BackupENB.setStyleSheet("color: white; border-radius: 10px; border : 2px solid rgb(45, 237, 138)")
            self.RegButton_RestoreENB.setEnabled(False)

        # BOTTOM | UiCLASSICBackups

        # Button - HELP | UiCLASSICBackups
        self.RegButton_Help = custom_push_button(self, QtCore.QRect(20, 770, 110, 30), "RegButton_Help", "HELP", normal_11, "", self.help_popup_backup)
        # Button - EXIT | UiCLASSICBackups
        self.RegButton_Exit = custom_push_button(self, QtCore.QRect(520, 770, 110, 30), "RegButton_Exit", "EXIT", normal_11, "", lambda: QtWidgets.QApplication.quit())
        # Text Box - SHARED | UiCLASSICBackups
        self.TXT_Window = custom_text_box(self, QtCore.QRect(20, 810, 610, 120), "Crash Log Auto Scanner & Setup Integrity Checker | Made by: Poet \nContributors: evildarkarchon | kittivelae | AtomicFallout757")

        QtCore.QMetaObject.connectSlotsByName(self)

    @staticmethod
    def open_tab_mainwin():
        screen_switch.setCurrentIndex(screen_switch.currentIndex() - 1)

    def help_popup_backup(self):
        help_popup_text = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface.help_popup_backup")
        popup = custom_popup_window(self, title="NEED HELP?", text=help_popup_text, height=450, callback="https://discord.com/invite/7ZZbrsGQh4")
        popup.exec()

    # noinspection PyMethodMayBeStatic
    def classic_files_manage(self, selected_list, selected_mode="BACKUP"):
        list_name = selected_list.split(" ", 1)

        try:
            CGame.game_files_manage(selected_list, selected_mode)
            if selected_mode == "BACKUP":
                exec(f"self.RegButton_Restore{list_name[1]}.setEnabled(True)")
        except PermissionError:
            print(f"❌ ERROR : UNABLE TO ACCESS FILES FROM YOUR GAME FOLDER.\n   TO RESOLVE THIS PROBLEM, PLEASE RUN CLASSIC IN ADMIN MODE \n")


if __name__ == "__main__":
    CMain.main_generate_required()
    print(CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface.start_message"))
    classic_ver = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info.version")
    app = QtWidgets.QApplication(sys.argv)

    # Add widgets of other "tabs" through function calls, not here.
    screen_switch = QtWidgets.QStackedWidget()
    screen_main = UiCLASSICMainWin()
    screen_switch.addWidget(screen_main)

    # Stuff here acts as defaults, no need to set anywhere else.
    screen_switch.setWindowTitle(f"Crash Log Auto Scanner & Setup Integrity Checker | {classic_ver}")
    screen_switch.setWindowIcon(QIcon("CLASSIC Data/graphics/CLASSIC.ico"))
    screen_switch.setStyleSheet("font-family: Yu Gothic; font-size: 13px")
    screen_switch.setObjectName("CLASSIC_MainWin")
    screen_switch.setFixedWidth(650)
    screen_switch.setFixedHeight(950)

    # Main window to the middle of the screen with 75px top bias.
    screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
    x = (screen_geometry.width() - screen_switch.width()) // 2
    y = (screen_geometry.height() - 75 - screen_switch.height()) // 2
    screen_switch.move(x, y)
    screen_switch.show()
    sys.exit(app.exec())