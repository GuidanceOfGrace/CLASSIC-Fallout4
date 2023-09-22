# CLASSIC GUI WITH PySide6 (NOW WORKS WITH 3.11!)
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
from functools import partial
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QUrl, QTimer, Slot
from PySide6.QtGui import QDesktopServices, QPixmap, QIcon
from PySide6.QtWidgets import QDialog, QFileDialog, QSizePolicy, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton

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


def custom_popup_window(parent, title, text, height=240, callback=""):
    popup_window = QDialog(parent)
    popup_window.setWindowTitle(title)
    popup_window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    popup_window.setStyleSheet("color: white; background: rgba(10, 10, 10, 1); border : 1px solid black; font-family: Yu Gothic; font-size: 15px")
    popup_window.setGeometry(15, 250, 620, height)

    layout = QVBoxLayout()
    label = QLabel(text, popup_window)
    # label.setAlignment(Qt.AlignTop)
    label.setWordWrap(True)

    # Create a horizontal layout for buttons
    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    ok_button.setMinimumSize(100, 50)
    ok_button.setStyleSheet("color: black; background: rgb(45, 237, 138); font-family: Yu Gothic; font-size: 20px; font-weight: bold")

    close_button = QPushButton("Close")
    close_button.setMinimumSize(100, 50)
    close_button.setStyleSheet("color: black; background: rgb(240, 63, 40); font-family: Yu Gothic; font-size: 20px; font-weight: bold")

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
    text_browser.setStyleSheet("color: white; background: rgba(10, 10, 10, 0.75); border-radius: 10px; border : 1px solid white; font-family: Yu Gothic; font-size: 15px")
    return text_browser


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
    def setup_ui(self):
        classic_ver = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Info.version")
        self.setWindowTitle(f"Crash Log Auto Scanner & Setup Integrity Checker | {classic_ver}")
        self.setWindowIcon(QIcon("CLASSIC Data/graphics/CLASSIC.ico"))
        self.setStyleSheet("font-family: Yu Gothic; font-size: 13px")
        self.setObjectName("CLASSIC_MainWin")
        self.resize(650, 900)
        self.setMinimumSize(QtCore.QSize(650, 900))
        self.setMaximumSize(QtCore.QSize(650, 900))

    def custom_checkbox_widget(self, pos_x=250, pos_y=250, size=25, check="", label_text="TEST LABEL", image_o="CLASSIC Data/graphics/unchecked.png", image_x="CLASSIC Data/graphics/checked.png"):
        checkbox_widget = QWidget(self)
        checkbox_widget.setGeometry(pos_x, pos_y, 200, 50)
        layout = QHBoxLayout(checkbox_widget)

        # Create QLabel for image & text.
        image_label = QLabel()
        pixmap0 = QPixmap(image_o)
        pixmap1 = QPixmap(image_x)

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

    def __init__(self):
        super().__init__()

        self.setup_ui()

        # MULTIPROCESSING
        self.papyrus_process = None
        self.monitoring_flag = multiprocessing.Value('i', 1)  # Shared Flag Variable

        # FONTS CONFIG
        bold_11 = QtGui.QFont()
        bold_11.setPointSize(11)
        bold_11.setBold(True)
        normal_11 = QtGui.QFont()
        normal_11.setPointSize(11)
        bold_09 = QtGui.QFont()
        bold_09.setPointSize(9)
        bold_09.setBold(True)

        # BACKGROUND CONFIG
        image_path = "CLASSIC Data/graphics/background.png"
        self.background_label = QtWidgets.QLabel(self)
        self.setCentralWidget(self.background_label)
        pixmap = QtGui.QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # ==================== MAIN WINDOW ITEMS =====================
        # TOP

        # SEPARATOR STAGING MODS FOLDER
        self.LBL_ModsFolder = custom_label(self, QtCore.QRect(20, 30, 260, 20), "STAGING MODS FOLDER", bold_11, "LBL_ModsFolder")
        self.Line_Sep_Mods = custom_frame(self, QtCore.QRect(30, 80, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Mods")
        # BROWSE STAGING MODS FOLDER
        self.Box_SelectedMods = custom_line_box(self, QtCore.QRect(20, 50, 450, 22), "Box_SelectedMods", "(Optional) Press *Browse Folder* to set your staging mods folder location.")
        self.Box_SelectedMods.setStyleSheet("color: darkgray; font-family: Yu Gothic; font-size: 13px")
        self.RegButton_BrowseMods = custom_push_button(self, QtCore.QRect(490, 50, 130, 24), "RegButton_BrowseMods", "Browse Folder", normal_11, "", self.select_folder_mods)

        # SEPARATOR CUSTOM SCAN FOLDER
        self.LBL_ScanFolder = custom_label(self, QtCore.QRect(20, 100, 260, 20), "CUSTOM SCAN FOLDER", bold_11, "LBL_ScanFolder")
        self.Line_Sep_Scan = custom_frame(self, QtCore.QRect(30, 150, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Scan")
        # BROWSE CUSTOM SCAN FOLDER
        self.Box_SelectedScan = custom_line_box(self, QtCore.QRect(20, 120, 450, 22), "Box_SelectedScan", "(Optional) Press *Browse Folder* to set a different scan folder location.")
        self.Box_SelectedScan.setStyleSheet("color: darkgray; font-family: Yu Gothic; font-size: 13px")
        self.RegButton_BrowseScan = custom_push_button(self, QtCore.QRect(490, 120, 130, 24), "RegButton_BrowseScan", "Browse Folder", normal_11, "", self.select_folder_scan)

        # TOP MAIN ROW
        self.RegButton_SCAN_LOGS = custom_push_button(self, QtCore.QRect(35, 185, 270, 48), "RegButton_SCAN_LOGS", "SCAN CRASH LOGS", bold_11, "", self.crash_logs_scan)
        self.RegButton_SCAN_LOGS.setStyleSheet("color: black; background: rgba(250, 250, 250, 0.90); border-radius: 10px; border : 1px solid white; font-family: Yu Gothic; font-size: 17px")
        self.RegButton_SCAN_FILES = custom_push_button(self, QtCore.QRect(345, 185, 270, 48), "RegButton_SCAN_FILES", "SCAN GAME FILES", bold_11, "", self.game_files_scan)
        self.RegButton_SCAN_FILES.setStyleSheet("color: black; background: rgba(250, 250, 250, 0.90); border-radius: 10px; border : 1px solid white; font-family: Yu Gothic; font-size: 17px")

        # BOTTOM MAIN ROW
        self.RegButton_ChangeINI = custom_push_button(self, QtCore.QRect(35, 250, 150, 32), "RegButton_ChangeINI", "CHANGE INI PATH", bold_09, "Select the folder where Fallout4.ini is located so CLASSIC can use that new location.", self.select_folder_ini)
        self.RegButton_OpenSettings = custom_push_button(self, QtCore.QRect(220, 250, 210, 32), "RegButton_OpenSettings", "OPEN CLASSIC SETTINGS", bold_09, "Open the CLASSIC Settings.yaml file in your default text editor.", self.open_settings)
        self.RegButton_CheckUpdates = custom_push_button(self, QtCore.QRect(465, 250, 150, 32), "RegButton_CheckUpdates", "CHECK UPDATES", bold_09, "Check for new CLASSIC versions (CLASSIC does this automatically every 7 days).", self.update_popup)

        # CHECK EXISTING BROWSE PATHS
        SCAN_folder = CMain.classic_settings("SCAN Custom Path")
        if SCAN_folder:
            self.Box_SelectedScan.setText(SCAN_folder.strip())
            self.Box_SelectedScan.setStyleSheet("color: black; font-family: Yu Gothic; font-size: 13px")
        MODS_folder = CMain.classic_settings("MODS Folder Path")
        if MODS_folder:
            self.Box_SelectedMods.setText(MODS_folder.strip())
            self.Box_SelectedMods.setStyleSheet("color: black; font-family: Yu Gothic; font-size: 13px")

        # SEGMENT - SETTINGS
        self.Line_Sep_Settings = custom_frame(self, QtCore.QRect(30, 300, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Settings")
        self.LBL_Settings = custom_label(self, QtCore.QRect(260, 320, 180, 16), "CLASSIC SETTINGS", bold_11, "LBL_Settings")
        # CHECKBOXES - Column 1
        self.ChkBT_FCXMode = self.custom_checkbox_widget(pos_x=70, pos_y=340, label_text="FCX MODE", check="FCX Mode")
        self.ChkBT_VRMode = self.custom_checkbox_widget(pos_x=70, pos_y=390, label_text="VR MODE", check="VR Mode")
        # CHECKBOXES - Column 2
        self.ChkBT_SimpleLogs = self.custom_checkbox_widget(pos_x=250, pos_y=340, label_text="SIMPLIFY LOGS", check="Simplify Logs")
        self.ChkBT_ShowFormID = self.custom_checkbox_widget(pos_x=250, pos_y=390, label_text="SHOW FID VALUES", check="Show FormID Values")
        # CHECKBOXES - Column 3
        self.ChkBT_Update = self.custom_checkbox_widget(pos_x=430, pos_y=340, label_text="UPDATE CHECK", check="Update Check")
        self.ChkBT_Unsolved = self.custom_checkbox_widget(pos_x=430, pos_y=390, label_text="MOVE INVALID LOGS", check="Move Unsolved Logs")

        # SEPARATOR WEBSITE LINKS
        self.Line_Sep_Links = custom_frame(self, QtCore.QRect(30, 450, 590, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Sep_Links")
        self.LBL_ArtWeb = custom_label(self, QtCore.QRect(200, 470, 590, 20), "ARTICLES / WEBSITES / NEXUS LINKS", bold_11, "LBL_ArtWeb")

        # Articles & Websites - ADD LINK BUTTONS FOR BETHINI, DDS SCANNER & WRYE BASH
        button_data = [
            {"text": "BUFFOUT 4 INSTALLATION", "url": "https://www.nexusmods.com/fallout4/articles/3115"},
            {"text": "FALLOUT 4 SETUP TIPS", "url": "https://www.nexusmods.com/fallout4/articles/4141"},
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
            button = QtWidgets.QPushButton(self)
            button.setGeometry(QtCore.QRect(45 + i % 3 * 190, 505 + i // 3 * 60, 180, 50))
            button.setObjectName("ArtBT_" + data["text"].replace(" ", ""))
            button.setText(data["text"])
            button.setStyleSheet("color: white; border-radius: 5px; border : 1px solid white; font-family: Yu Gothic; font-size: 11px; font-weight: bold")
            open_url = partial(QDesktopServices.openUrl, QUrl(data["url"]))
            button.clicked.connect(open_url)

        # BOTTOM

        # Button - HELP
        self.RegButton_Help = custom_push_button(self, QtCore.QRect(20, 720, 110, 30), "RegButton_Help", "HELP", normal_11, "", self.help_popup)
        # Button - PAPYRUS MONITORING
        self.RegButton_Papyrus = custom_push_button(self, QtCore.QRect(195, 720, 260, 30), "RegButton_Papyrus", "START PAPYRUS MONITORING", bold_11, "", self.toggle_papyrus_worker)
        self.RegButton_Papyrus.setStyleSheet("color: black; background: rgb(45, 237, 138); border-radius: 10px; border : 1px solid black; font-family: Yu Gothic; font-size: 13px; font-weight: bold")
        # Button - EXIT
        self.RegButton_Exit = custom_push_button(self, QtCore.QRect(520, 720, 110, 30), "RegButton_Exit", "EXIT", normal_11, "", self.close)
        # Text Box - SHARED
        self.TXT_Window = custom_text_box(self, QtCore.QRect(20, 760, 610, 120), "Crash Log Auto Scanner & Setup Integrity Checker | Made by: Poet \nContributors: evildarkarchon | kittivelae | AtomicFallout757")

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

    def help_popup(self):
        help_popup_text = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface.help_popup_text")
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


if __name__ == "__main__":
    CMain.main_generate_required()
    start_message = CMain.yaml_settings("CLASSIC Data/databases/CLASSIC Main.yaml", "CLASSIC_Interface.start_message")
    print(start_message)
    app = QtWidgets.QApplication(sys.argv)
    ui = UiCLASSICMainWin()
    ui.show()
    sys.exit(app.exec())