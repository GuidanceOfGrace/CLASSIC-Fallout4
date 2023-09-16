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
from PySide6.QtCore import QUrl, QTimer, Slot
from PySide6.QtGui import QColor, QDesktopServices, QPalette, QPixmap
from PySide6.QtWidgets import QFileDialog, QSizePolicy, QWidget, QLabel, QHBoxLayout

CMain.configure_logging()


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
    button.setStyleSheet("border-radius: 10px; border : 2px solid black")
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
    return label


def custom_check_box(parent, geometry, text, tooltip, checked, object_name, disabled=False):
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


def custom_popup_box(parent, title, text, open_url):
    popup_box = QtWidgets.QMessageBox(parent)
    popup_box.setIcon(QtWidgets.QMessageBox.Question)

    popup_box.setWindowTitle(title)
    popup_box.setText(text)  # RESERVED | popup_box.setInformativeText("...")
    popup_box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    if popup_box.exec() != QtWidgets.QMessageBox.Cancel:
        QDesktopServices.openUrl(QUrl(open_url))
    return popup_box


def custom_text_box(parent, geometry, text):
    text_browser = QtWidgets.QTextBrowser(parent)
    text_browser.setGeometry(geometry)
    text_browser.setObjectName("text_browser")
    text_browser.setText(text)
    font = QtGui.QFont()
    font.setPointSize(13)
    text_browser.setFont(font)
    return text_browser


def set_color_text(object_name, text_color):
    custom_color = object_name.palette()
    custom_color.setColor(QPalette.Text, QColor(text_color))
    object_name.setPalette(custom_color)


def papyrus_worker(q, stop_event):
    while not stop_event.is_set():
        papyrus_result = CGame.papyrus_logging()
        q.put(papyrus_result)
        time.sleep(3)


def play_sound(sound_file):
    sound, samplerate = sfile.read(f"CLASSIC Data/sounds/{sound_file}")
    sdev.play(sound, samplerate)
    sdev.wait()


class CustomCheckBoxWidget(QWidget):
    def __init__(self, parent=None, pos_x=350, pos_y=400, size=25, label_text="TEST LABEL", image_o="CLASSIC Data/graphics/unchecked.png", image_x="CLASSIC Data/graphics/checked.png"):
        super().__init__(parent)
        self.setGeometry(pos_x, pos_y, 150, 50)

        layout = QHBoxLayout(self)

        # Create QLabel for image & text.
        self.image_label = QLabel()
        self.pixmap1 = QPixmap(image_o)
        self.pixmap2 = QPixmap(image_x)

        self.image_label.setPixmap(self.pixmap1)
        self.image_label.setFixedSize(size, size)
        self.text_label = QLabel(label_text)

        # Add image & text labels to layout.
        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

        self.image_label.mousePressEvent = self.toggle_pixmap

    def toggle_pixmap(self, event):
        # Toggle between two images when label is clicked.
        if self.image_label.pixmap() == self.pixmap1:
            self.image_label.setPixmap(self.pixmap2)
        else:
            self.image_label.setPixmap(self.pixmap1)


# ================================================
# CLASSIC MAIN WINDOW
# ================================================
class UiCLASSICMainWin(QtWidgets.QMainWindow):
    def setup_ui(self):
        classic_ver = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info", "version")
        self.setWindowTitle(f"Crash Log Auto Scanner & Setup Integrity Checker | {classic_ver}")
        self.setObjectName("CLASSIC_MainWin")
        self.resize(640, 800)
        self.setMinimumSize(QtCore.QSize(640, 800))
        self.setMaximumSize(QtCore.QSize(640, 800))

    def configure_window(self):
        main_app = QtWidgets.QApplication.instance()
        main_font = self.font()
        # main_font.setPointSize(13)
        main_font.setFamily("Yu Gothic")
        main_app.setFont(main_font)

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.configure_window()

        # MULTIPROCESSING
        self.papyrus_process = None
        self.monitoring_flag = multiprocessing.Value('i', 1)  # Shared Flag Variable

        # FONTS CONFIG
        bold_11 = QtGui.QFont()
        bold_11.setPointSize(11)
        bold_11.setBold(True)
        normal_11 = QtGui.QFont()
        normal_11.setPointSize(11)

        # BACKGROUND CONFIG
        image_path = "CLASSIC Data/graphics/background.png"
        self.background_label = QtWidgets.QLabel(self)
        self.setCentralWidget(self.background_label)
        pixmap = QtGui.QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # ==================== MAIN WINDOW ITEMS =====================
        # TOP
        # self.custom_checkbox = CustomCheckBoxWidget(pos_x=50, pos_y=50, size=25, label_text="TEST LABEL", image_o="CLASSIC Data/graphics/unchecked.png", image_x="CLASSIC Data/graphics/checked.png")
        # self.setCentralWidget(self.custom_checkbox)

        # SEPARATOR STAGING MODS FOLDER
        self.LBL_ModsFolder = custom_label(self, QtCore.QRect(20, 30, 260, 16), "STAGING MODS FOLDER", bold_11, "LBL_ModsFolder")
        self.Line_Sep_Mods = custom_frame(self, QtCore.QRect(40, 80, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Mods")
        # BROWSE STAGING MODS FOLDER
        self.Box_SelectedMods = custom_line_box(self, QtCore.QRect(20, 50, 450, 22), "Box_SelectedMods", "(Optional) Press *Browse Folder* to set your staging mods folder location.")
        set_color_text(self.Box_SelectedMods, "darkgray")
        self.RegButton_BrowseMods = custom_push_button(self, QtCore.QRect(490, 50, 130, 24), "RegButton_BrowseMods", "Browse Folder", normal_11, "", self.select_folder_mods)

        # SEPARATOR CUSTOM SCAN FOLDER
        self.LBL_ScanFolder = custom_label(self, QtCore.QRect(20, 100, 260, 16), "CUSTOM SCAN FOLDER", bold_11, "LBL_ScanFolder")
        self.Line_Sep_Scan = custom_frame(self, QtCore.QRect(40, 150, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Scan")
        # BROWSE CUSTOM SCAN FOLDER
        self.Box_SelectedScan = custom_line_box(self, QtCore.QRect(20, 120, 450, 22), "Box_SelectedScan", "(Optional) Press *Browse Folder* to set a different scan folder location.")
        set_color_text(self.Box_SelectedScan, "darkgray")
        self.RegButton_BrowseScan = custom_push_button(self, QtCore.QRect(490, 120, 130, 24), "RegButton_BrowseScan", "Browse Folder", normal_11, "", self.select_folder_scan)

        # TOP MAIN ROW
        self.RegButton_SCAN_LOGS = custom_push_button(self, QtCore.QRect(35, 185, 270, 48), "RegButton_SCAN_LOGS", "SCAN CRASH LOGS", bold_11, "", self.crash_logs_scan)
        self.RegButton_SCAN_FILES = custom_push_button(self, QtCore.QRect(335, 185, 270, 48), "RegButton_SCAN_FILES", "SCAN GAME FILES", bold_11, "", self.game_files_scan)

        # BOTTOM MAIN ROW
        self.RegButton_ChangeINI = custom_push_button(self, QtCore.QRect(35, 250, 150, 32), "RegButton_ChangeINI", "CHANGE INI PATH", normal_11, "Select the folder where Fallout4.ini is located so CLASSIC can use that new location.", self.select_folder_ini)
        self.RegButton_CheckUpdates = custom_push_button(self, QtCore.QRect(455, 250, 150, 32), "RegButton_CheckUpdates", "CHECK FOR UPDATES", normal_11, "", self.update_popup)

        # CHECK EXISTING BROWSE PATHS
        SCAN_folder = CMain.classic_settings("SCAN Custom Path")
        if SCAN_folder:
            self.Box_SelectedScan.setText(SCAN_folder.strip())
            set_color_text(self.Box_SelectedScan, "black")
        MODS_folder = CMain.classic_settings("MODS Folder Path")
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder.strip())
            set_color_text(self.Box_SelectedMods, "black")

        # SEGMENT - SETTINGS
        self.Line_Sep_Settings = custom_frame(self, QtCore.QRect(40, 300, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Settings")
        self.LBL_Settings = custom_label(self, QtCore.QRect(245, 320, 180, 16), "CLASSIC SETTINGS", bold_11, "LBL_Settings")
        # Column 1
        self.ChkBT_FCXMode = custom_check_box(self, QtCore.QRect(90, 350, 150, 20), "FCX MODE", "Enable if you want CLASSIC to check the integrity of your game and mod files.", CMain.classic_settings("FCX Mode"), "ChkBT_FCXMode")
        self.ChkBT_VRMode = custom_check_box(self, QtCore.QRect(90, 380, 150, 20), "VR MODE", "Enable if you want CLASSIC to prioritize scanning the Virtual Reality (VR) version of your game.", CMain.classic_settings("VR Mode"), "ChkBT_VRMode")
        # Column 2
        self.ChkBT_SimpleLogs = custom_check_box(self, QtCore.QRect(260, 350, 150, 20), "SIMPLIFY LOGS", "Enable if you want CLASSIC to remove some unnecessary info from your crash log files.", CMain.classic_settings("Simplify Logs"), "ChkBT_SimpleLogs")
        self.ChkBT_ShowFormID = custom_check_box(self, QtCore.QRect(260, 380, 150, 20), "SHOW FID VALUES", "Enable if you want CLASSIC to look up FormID values (names) while scanning crash logs.", CMain.classic_settings("Show FormID Values"), "ChkBT_ShowFormID")
        # Column 3
        self.ChkBT_Update = custom_check_box(self, QtCore.QRect(430, 350, 150, 20), "UPDATE CHECK", "Enable if you want CLASSIC to periodically check for its own updates online through GitHub.", CMain.classic_settings("Update Check"), "ChkBT_Update")
        self.ChkBT_Unsolved = custom_check_box(self, QtCore.QRect(430, 380, 150, 20), "MOVE INVALID LOGS", "Enable if you want CLASSIC to move all invalid crash logs to CLASSIC Misc folder.)", CMain.classic_settings("Move Unsolved Logs"), "ChkBT_Unsolved")

        # SEPARATOR WEBSITE LINKS
        self.Line_Sep_Links = custom_frame(self, QtCore.QRect(40, 410, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Links")
        self.LBL_ArtWeb = custom_label(self, QtCore.QRect(185, 430, 560, 16), "ARTICLES / WEBSITES / NEXUS LINKS", bold_11, "LBL_ArtWeb")

        # Articles & Websites - ADD LINK BUTTONS FOR BETHINI, DDS SCANNER & WRYE BASH
        button_data = [
            {"text": "BUFFOUT 4 INSTALLATION", "url": "https://www.nexusmods.com/fallout4/articles/3115"},
            {"text": "ADDITIONAL TIPS", "url": "https://www.nexusmods.com/fallout4/articles/4141"},
            {"text": "IMPORTANT PATCHES LIST", "url": "https://www.nexusmods.com/fallout4/articles/3769"},
            {"text": "BUFFOUT 4 NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/47359"},
            {"text": "CLASSIC NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/56255"},
            {"text": "CLASSIC GITHUB", "url": "https://github.com/GuidanceOfGrace/CLASSIC-Fallout4"},
            {"text": "DDS TEXTURE SCANNER", "url": "https://www.nexusmods.com/fallout4/mods/71588"},
            {"text": "BETHINI TOOL", "url": "https://www.nexusmods.com/fallout4/mods/67"},
            {"text": "WRYE BASH TOOL", "url": "https://www.nexusmods.com/fallout4/mods/20032"}
        ]

        # ARRANGE BUTTONS IN GRID
        for i, data in enumerate(button_data):
            font = QtGui.QFont()
            font.setPointSize(9)
            button = QtWidgets.QPushButton(self)
            button.setGeometry(QtCore.QRect(40 + i % 3 * 190, 460 + i // 3 * 50, 180, 32))
            button.setObjectName("ArtBT_" + data["text"].replace(" ", ""))
            button.setFont(font)
            button.setText(data["text"])
            open_url = partial(QDesktopServices.openUrl, QUrl(data["url"]))
            button.clicked.connect(open_url)

        # BOTTOM

        # Button - HELP
        self.RegButton_Help = custom_push_button(self, QtCore.QRect(20, 620, 110, 30), "RegButton_Help", "HELP", normal_11, "How To Use CLASSIC GUI", self.help_popup)
        # Button - PAPYRUS MONITORING
        self.RegButton_Papyrus = custom_push_button(self, QtCore.QRect(205, 620, 240, 30), "RegButton_Papyrus", "START PAPYRUS MONITORING", bold_11, "PLACEHOLDER", self.toggle_papyrus_worker)
        # Button - EXIT
        self.RegButton_Exit = custom_push_button(self, QtCore.QRect(510, 620, 110, 30), "RegButton_Exit", "EXIT", normal_11, "Exit CLASSIC GUI", UiCLASSICMainWin.close)
        # Text Box - SHARED
        self.TXT_Window = custom_text_box(self, QtCore.QRect(20, 660, 600, 120), "Crash Log Auto Scanner & Setup Integrity Checker | Made by: Poet \nContributors: evildarkarchon | kittivelae | AtomicFallout757")

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
            self.RegButton_Papyrus.setText("STOP PAPYRUS MONITORING")
        else:
            self.worker_stop_event.set()
            self.worker_process.join()
            self.worker_process = None
            self.RegButton_Papyrus.setText("START PAPYRUS MONITORING")
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
            set_color_text(self.Box_SelectedScan, "black")

    def select_folder_mods(self):
        MODS_folder = QFileDialog.getExistingDirectory()
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder)
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.MODS Folder Path", MODS_folder)
            set_color_text(self.Box_SelectedMods, "black")

    def select_folder_ini(self):
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(self, "New INI Path Set", "You have set the new path to: \n" + INI_folder)
            CMain.yaml_update("CLASSIC Settings.yaml", f"CLASSIC_Settings.INI Folder Path", INI_folder)

        # ================== POP-UPS / WARNINGS =====================

    def help_popup(self):
        help_popup_text = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface", "help_popup_text")
        custom_popup_box(self, "Need Help?", help_popup_text, "https://discord.com/invite/7ZZbrsGQh4")

    def update_popup(self):
        update_popup_text = CMain.yaml_get("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface", "update_popup_text")
        if CMain.classic_update_check():
            QtWidgets.QMessageBox.information(self, "CLASSIC Update", "You have the latest version of CLASSIC!")
        else:
            QtWidgets.QMessageBox.warning(self, "CLASSIC Update", update_popup_text)
            QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255?tab=files"))


if __name__ == "__main__":
    CMain.main_generate_required()
    start_message = """\
PRESS *SCAN CRASH LOGS* BUTTON TO SCAN ALL AVAILABLE BUFFOUT 4 CRASH LOGS

PRESS *SCAN GAME FILES* BUTTON TO CHECK YOUR FALLOUT 4 GAME & MOD FILES

IF YOU ARE USING MOD ORGANIZER 2, YOU NEED TO RUN CLASSIC WITH THE MO2 SHORTCUT
CHECK THE INCLUDED CLASSIC Readme.md FILE FOR MORE DETAILS AND INSTRUCTIONS
"""
    print(start_message)
    app = QtWidgets.QApplication(sys.argv)
    ui = UiCLASSICMainWin()
    ui.show()
    sys.exit(app.exec())