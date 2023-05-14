# CRASH LOG AUTO SCANNER GUI WITH PySide6 (PYTHON 3.9 COMPLIANT)
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPalette
from PySide6.QtWidgets import QApplication, QFileDialog
from CLAS_Database import (GALAXY, UNIVERSE, clas_toml_create, clas_toml_update, clas_update_check)
from CLAS_ScanLogs import scan_logs

'''import platform  # RESERVED FOR FUTURE UPDATE
current_platform = platform.system()
if current_platform == 'Windows':
    version = platform.release()
    if version.startswith('10') or version.startswith('11'):
        QApplication.setStyle("Fusion")
        sys.argv += ['-platform', 'windows:darkmode=2']
'''
clas_toml_create()


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


def create_custom_check_box(parent, geometry, text, tooltip, checked, object_name):
    check_box = QtWidgets.QCheckBox(parent)
    check_box.setGeometry(geometry)
    check_box.setText(text)
    check_box.setToolTip(tooltip)
    if checked:
        check_box.setChecked(True)
    check_box.setObjectName(object_name)
    return check_box


def create_label(parent, text, geometry):
    label = QtWidgets.QLabel(parent)
    label.setGeometry(geometry)
    label.setObjectName("label")
    label.setText(text)
    return label


def create_text_browser(parent, geometry):
    text_browser = QtWidgets.QTextBrowser(parent)
    text_browser.setGeometry(geometry)
    text_browser.setObjectName("text_browser")
    return text_browser

# noinspection PyUnresolvedReferences


class UiCLASMainWin(object):
    def __init__(self):
        self.ArtBT_Buffout4 = None
        self.ArtBT_Patches = None
        self.ArtBT_Troubleshoot = None

        self.ChkBT_FCXMode = None
        self.ChkBT_IMIMode = None
        self.ChkBT_Stats = None
        self.ChkBT_Unsolved = None
        self.ChkBT_Update = None

        self.LBL_ArtWeb = None
        self.LBL_Settings = None

        self.Line_SelectedFolder = None
        self.Line_Separator_1 = None
        self.Line_Separator_2 = None

        self.RegBT_Browse = None
        self.RegBT_ChangeINI = None
        self.RegBT_CheckUpdates = None
        self.RegBT_Exit = None
        self.RegBT_Help = None
        self.RegBT_SCAN_LOGS = None
        self.RegBT_SCAN_FILES = None

        self.TXT_About = None
        self.TXT_Contributors = None
        self.TXT_Window = None

        self.WebBT_Buffout4_Nexus = None
        self.WebBT_CLAS_Github = None
        self.WebBT_CLAS_Nexus = None

    def setup_ui(self, CLAS_MainWin):

        # MAIN WINDOW
        CLAS_MainWin.setObjectName("CLAS_MainWin")
        CLAS_MainWin.setWindowTitle(f"Crash Log Auto Scanner {UNIVERSE.CLAS_Current[-4:]}")
        CLAS_MainWin.resize(640, 640)
        CLAS_MainWin.setMinimumSize(QtCore.QSize(640, 640))
        CLAS_MainWin.setMaximumSize(QtCore.QSize(640, 640))
        CLAS_MainWin.setWindowFlags(CLAS_MainWin.windowFlags() | Qt.WindowMinimizeButtonHint)  # type: ignore

        # ==================== MAIN WINDOW ITEMS =====================
        # TOP

        # Text Box - Selected Folder
        font_bold_10 = QtGui.QFont()
        font_bold_10.setPointSize(10)
        font_bold_10.setBold(True)
        font_10 = QtGui.QFont()
        font_10.setPointSize(10)

        self.Line_SelectedFolder = create_custom_line_edit(CLAS_MainWin, QtCore.QRect(20, 30, 450, 22), "Line_SelectedFolder", "(Optional) Press 'Browse Folder...' to set a different scan folder location.", "darkgray")
        self.RegBT_Browse = create_simple_button(CLAS_MainWin, QtCore.QRect(490, 30, 130, 24), "RegBT_Browse", "Browse Folder...", "", self.SelectFolder_SCAN)
        self.RegBT_SCAN_LOGS = create_custom_push_button(CLAS_MainWin, QtCore.QRect(220, 80, 200, 40), "RegBT_SCAN_LOGS", "SCAN LOGS", font_bold_10, "", self.CrashLogs_SCAN)
        self.RegBT_SCAN_FILES = create_custom_push_button(CLAS_MainWin, QtCore.QRect(245, 140, 150, 32), "RegBT_SCAN_FILES", "Scan Game Files", font_bold_10, "", self.Gamefiles_SCAN)
        self.RegBT_ChangeINI = create_custom_push_button(CLAS_MainWin, QtCore.QRect(90, 140, 130, 32), "RegBT_ChangeINI", "CHANGE INI PATH", font_10, "Select the folder where your Fallout4.ini is located so the Auto-Scanner can use that new folder location.", self.SelectFolder_INI)
        self.RegBT_CheckUpdates = create_custom_push_button(CLAS_MainWin, QtCore.QRect(420, 140, 140, 32), "RegBT_CheckUpdates", "CHECK FOR UPDATES", font_10, "", self.Update_Popup)

        SCAN_folder = UNIVERSE.CLAS_config["Scan Path"].strip()
        if len(SCAN_folder) > 1:
            self.Line_SelectedFolder.setText(SCAN_folder)

        # SEGMENT - SETTINGS

        self.Line_Separator_1 = create_custom_frame(CLAS_MainWin, QtCore.QRect(40, 180, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Separator_1")
        self.LBL_Settings = create_custom_label(CLAS_MainWin, QtCore.QRect(290, 200, 60, 16), "SETTINGS", font_bold_10, "LBL_Settings")
        self.ChkBT_FCXMode = create_custom_check_box(CLAS_MainWin, QtCore.QRect(100, 230, 110, 20), "FCX MODE", "Enable if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly.", UNIVERSE.CLAS_config["FCX Mode"], "ChkBT_FCXMode")
        self.ChkBT_IMIMode = create_custom_check_box(CLAS_MainWin, QtCore.QRect(260, 210, 110, 100), "IGNORE ALL\nMANUAL FILE\nINSTALLATION\nWARNINGS", "Enable if you want Auto-Scanner to hide all manual installation warnings.\nI still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager.", UNIVERSE.CLAS_config["IMI Mode"], "ChkBT_IMIMode")
        self.ChkBT_Update = create_custom_check_box(CLAS_MainWin, QtCore.QRect(430, 230, 110, 20), "UPDATE CHECK", "Enable if you want Auto-Scanner to check your Python version and if all required packages are installed.", UNIVERSE.CLAS_config["Update Check"], "ChkBT_Update")
        self.ChkBT_Stats = create_custom_check_box(CLAS_MainWin, QtCore.QRect(100, 270, 120, 20), "STAT LOGGING", "Enable if you want Auto-Scanner to show extra stats about scanned logs in the command line window.", UNIVERSE.CLAS_config["Stat Logging"], "ChkBT_Stats")
        self.ChkBT_Unsolved = create_custom_check_box(CLAS_MainWin, QtCore.QRect(430, 270, 130, 20), "MOVE UNSOLVED", "Enable if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder.\n(Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages.)", UNIVERSE.CLAS_config["Move Unsolved"], "ChkBT_Unsolved")

        # SEGMENT - ARTICLES / WEBSITES

        # SEPARATOR LINE 2
        self.Line_Separator_2 = create_custom_frame(CLAS_MainWin, QtCore.QRect(40, 310, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Separator_2")
        # SEPARATOR TEXT 2 (ARTICLES / WEBSITES)
        self.LBL_ArtWeb = QtWidgets.QLabel(CLAS_MainWin)
        self.LBL_ArtWeb.setGeometry(QtCore.QRect(250, 330, 140, 16))
        self.LBL_ArtWeb.setText("ARTICLES / WEBSITES")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.LBL_ArtWeb.setFont(font)
        self.LBL_ArtWeb.setObjectName("LBL_ArtWeb")
        self.LBL_ArtWeb = create_custom_label(CLAS_MainWin, QtCore.QRect(250, 330, 140, 16), "ARTICLES / WEBSITES", font_bold_10, "LBL_ArtWeb")

        # Articles & Websites
        button_data = [
            {"text": "BUFFOUT 4 INSTALLATION", "url": "https://www.nexusmods.com/fallout4/articles/3115"},
            {"text": "ADVANCED TROUBLESHOOTING", "url": "https://www.nexusmods.com/fallout4/articles/4141"},
            {"text": "IMPORTANT PATCHES LIST", "url": "https://www.nexusmods.com/fallout4/articles/3769"},
            {"text": "BUFFOUT 4 NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/47359"},
            {"text": "AUTO SCANNER NEXUS PAGE", "url": "https://www.nexusmods.com/fallout4/mods/56255"},
            {"text": "AUTO SCANNER GITHUB", "url": "https://github.com/GuidanceOfGrace/Buffout4-CLAS/releases"}
        ]

        # ARRANGE BUTTONS IN GRID
        for i, data in enumerate(button_data):
            font = QtGui.QFont()
            font.setPointSize(8)
            button = QtWidgets.QPushButton(CLAS_MainWin)
            button.setGeometry(QtCore.QRect(40 + i % 3 * 190, 370 + i // 3 * 50, 180, 32))
            button.setObjectName("ArtBT_" + data["text"].replace(" ", ""))
            button.setFont(font)
            button.setText(data["text"])
            button.clicked.connect(lambda url=data["url"]: QDesktopServices.openUrl(QUrl(url)))  # type: ignore

        # BOTTOM

        # Button - HELP
        self.RegBT_Help = create_custom_push_button(CLAS_MainWin, QtCore.QRect(20, 480, 110, 24), "RegBT_Help", "HELP", font_10, "How To Use CLAS GUI", self.Help_Popup)
        # Button - EXIT
        self.RegBT_Exit = create_custom_push_button(CLAS_MainWin, QtCore.QRect(510, 480, 110, 24), "RegBT_Exit", "EXIT", font_10, "Exit CLAS GUI", CLAS_MainWin.close)

        # Usage
        self.TXT_Window = create_text_browser(CLAS_MainWin, QtCore.QRect(20, 510, 600, 120))
        self.TXT_About = create_label(CLAS_MainWin, "Crash Log Auto Scanner (CLAS) | Made by: Poet #9800", QtCore.QRect(30, 520, 320, 16))
        self.TXT_Contributors = create_label(CLAS_MainWin, "Contributors: evildarkarchon | kittivelae | AtomicFallout757", QtCore.QRect(30, 540, 340, 16))

        # ====================== CHECK BOXES ========================

        self.ChkBT_IMIMode.clicked.connect(lambda: self.update_ini_config(self.ChkBT_IMIMode, "IMI Mode"))  # type: ignore
        self.ChkBT_Stats.clicked.connect(lambda: self.update_ini_config(self.ChkBT_Stats, "Stat Logging"))  # type: ignore
        self.ChkBT_Unsolved.clicked.connect(lambda: self.update_ini_config(self.ChkBT_Unsolved, "Move Unsolved"))  # type: ignore
        self.ChkBT_Update.clicked.connect(lambda: self.update_ini_config(self.ChkBT_Update, "Update Check"))  # type: ignore
        self.ChkBT_FCXMode.clicked.connect(lambda: self.update_ini_config(self.ChkBT_FCXMode, "FCX Mode"))  # type: ignore

        QtCore.QMetaObject.connectSlotsByName(CLAS_MainWin)

        # ================= MAIN BUTTON FUNCTIONS ===================
        # @staticmethod recommended for func that don't call "self".

    @staticmethod
    def update_ini_config(checkbox, config_key):
        if checkbox.isChecked():
            clas_toml_update(config_key, True)
        else:
            clas_toml_update(config_key, False)

    @staticmethod
    def CrashLogs_SCAN():
        scan_logs()

    @staticmethod
    def Gamefiles_SCAN():
        from CLAS_ScanFiles import scan_game_files, scan_wryecheck
        GALAXY.scan_game_report = []
        scan_game_files()
        scan_wryecheck()
        for item in GALAXY.scan_game_report:
            print(item)

    def SelectFolder_SCAN(self):
        SCAN_folder = QFileDialog.getExistingDirectory()
        if SCAN_folder:
            self.Line_SelectedFolder.setText(SCAN_folder)  # type: ignore
            clas_toml_update("Scan Path", SCAN_folder)
            # Change text color back to black.
            LSF_palette = self.Line_SelectedFolder.palette()  # type: ignore
            LSF_palette.setColor(QPalette.ColorRole.Text, QColor("black"))  # type: ignore
            self.Line_SelectedFolder.setPalette(LSF_palette)  # type: ignore

    @staticmethod
    def SelectFolder_INI():
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(CLAS_MainWin, "New INI Path Set", "You have set the new path to: \n" + INI_folder)  # type: ignore
            clas_toml_update("INI Path", INI_folder)

        # ================== POP-UPS / WARNINGS =====================

    @staticmethod
    def Help_Popup():
        QtWidgets.QMessageBox.information(CLAS_MainWin, "Need Help?",
                                          "If you have trouble running this program or wish to submit your crash logs for additional help from our support team, join the Collective Modding Discord server. Press OK to open the server link in your browser. \n")
        QDesktopServices.openUrl(QUrl("https://discord.com/invite/7ZZbrsGQh4"))

    @staticmethod
    def Update_Popup():
        if clas_update_check():
            QtWidgets.QMessageBox.information(CLAS_MainWin, "CLAS Update", "You have the latest version of Crash Log Auto Scanner!")
        else:
            QtWidgets.QMessageBox.warning(CLAS_MainWin, "CLAS Update", "New Crash Log Auto Scanner version detected!\nPress OK to open the CLAS Nexus Page.")
            QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255?tab=files"))


if __name__ == "__main__":
    gui_prompt = """\
PRESS 'SCAN LOGS' BUTTON TO SCAN ALL AVAILABLE BUFFOUT 4 CRASH LOGS

PRESS 'Scan Game Files' BUTTON TO CHECK YOUR FALLOUT 4 GAME FILES

IF YOU ARE USING MOD ORGANIZER 2, RUN CLAS THROUGH THE MO2 SHORTCUT
DON'T FORGET TO CHECK THE CLAS README FOR MORE DETAILS AND INSTRUCTIONS
"""
    print(gui_prompt)
    app = QtWidgets.QApplication(sys.argv)
    CLAS_MainWin = QtWidgets.QDialog()
    ui = UiCLASMainWin()
    ui.setup_ui(CLAS_MainWin)
    CLAS_MainWin.show()
    sys.exit(app.exec())
