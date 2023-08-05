# CRASH LOG AUTO SCANNER GUI WITH PySide6 (PYTHON 3.9 COMPLIANT)
import platform  # RESERVED FOR FUTURE UPDATE
import sys
from functools import partial
from pathlib import Path
from urllib.parse import urlparse

import requests
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QDesktopServices, QPalette
from PySide6.QtWidgets import QApplication, QFileDialog

from CLAS_Database import (GALAXY, UNIVERSE, clas_toml_create,
                           clas_toml_update, clas_update_check)
from CLAS_ScanLogs import scan_logs

current_platform = platform.system()
if current_platform == 'Windows':
    version = platform.release()
    if version.startswith('10') or version.startswith('11'):
        QApplication.setStyle("Fusion")
        sys.argv += ['-platform', 'windows:darkmode=2']

clas_toml_create()


def create_custom_line_edit(parent, geometry, object_name, text, text_color="black"):
    """
    Creates a custom QLineEdit widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        object_name (str): The object name of the widget.
        text (str): The initial text of the widget.
        text_color (str): The color of the text. Default is "black".

    Returns:
        QLineEdit: The created QLineEdit widget.

    Example:
        >>> parent = QtWidgets.QWidget()
        >>> geometry = QtCore.QRect(0, 0, 100, 20)
        >>> object_name = "myLineEdit"
        >>> text = "Hello, world!"
        >>> text_color = "red"
        >>> line_edit = create_custom_line_edit(parent, geometry, object_name, text, text_color)
    """
    line_edit = QtWidgets.QLineEdit(parent)
    line_edit.setGeometry(geometry)
    line_edit.setObjectName(object_name)
    line_edit.setText(text)
    palette = line_edit.palette()
    palette.setColor(QPalette.Text, QColor(text_color))  # type: ignore
    line_edit.setPalette(palette)
    return line_edit


def create_custom_push_button(parent, geometry, object_name, text, font, tooltip="", callback=None):
    """
    Creates a custom QPushButton widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        object_name (str): The object name of the widget.
        text (str): The text of the widget.
        font (QFont): The font of the widget.
        tooltip (str): The tooltip of the widget. Default is an empty string.
        callback (function): The callback function to be called when the button is clicked. Default is None.

    Returns:
        QPushButton: The created QPushButton widget.

    Example:
        >>> parent = QtWidgets.QWidget()
        >>> geometry = QtCore.QRect(0, 0, 100, 20)
        >>> object_name = "myPushButton"
        >>> text = "Click me!"
        >>> font = QtGui.QFont("Arial", 12)
        >>> tooltip = "This is a tooltip."
        >>> callback = my_callback_function
        >>> push_button = create_custom_push_button(parent, geometry, object_name, text, font, tooltip, callback)
    """
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
    """
    Creates a simple QPushButton widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        object_name (str): The object name of the widget.
        text (str): The text of the widget.
        tooltip (str): The tooltip of the widget.
        callback (function): The callback function to be called when the button is clicked.

    Returns:
        QPushButton: The created QPushButton widget.

    Example:
        >>> parent = QtWidgets.QWidget()
        >>> geometry = QtCore.QRect(0, 0, 100, 20)
        >>> object_name = "myPushButton"
        >>> text = "Click me!"
        >>> tooltip = "This is a tooltip."
        >>> callback = my_callback_function
        >>> push_button = create_simple_button(parent, geometry, object_name, text, tooltip, callback)
    """
    button = QtWidgets.QPushButton(parent)
    button.setGeometry(geometry)
    button.setObjectName(object_name)
    button.setText(text)
    button.setToolTip(tooltip)
    button.clicked.connect(callback)
    return button


def create_custom_frame(parent, geometry, frame_shape, frame_shadow, object_name):
    """
    Creates a custom QFrame widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        frame_shape (QFrame.Shape): The shape of the frame.
        frame_shadow (QFrame.Shadow): The shadow of the frame.
        object_name (str): The object name of the widget.

    Returns:
        QFrame: The created QFrame widget.
    """
    frame = QtWidgets.QFrame(parent)
    frame.setGeometry(geometry)
    frame.setFrameShape(frame_shape)
    frame.setFrameShadow(frame_shadow)
    frame.setObjectName(object_name)
    return frame


def create_custom_label(parent, geometry, text, font, object_name):
    """
    Creates a custom QLabel widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        text (str): The text of the widget.
        font (QFont): The font of the widget.
        object_name (str): The object name of the widget.

    Returns:
        QLabel: The created QLabel widget.
    """
    label = QtWidgets.QLabel(parent)
    label.setGeometry(geometry)
    label.setText(text)
    label.setFont(font)
    label.setObjectName(object_name)
    return label


def create_custom_check_box(parent, geometry, text, tooltip, checked, object_name, disabled=False):
    """
    Creates a custom QCheckBox widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        text (str): The text of the widget.
        tooltip (str): The tooltip of the widget.
        checked (bool): Whether the checkbox is checked.
        object_name (str): The object name of the widget.
        disabled (bool): Whether the checkbox is disabled. Default is False.

    Returns:
        QCheckBox: The created QCheckBox widget.
    """
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
    """
    Creates a QLabel widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        text (str): The text of the widget.
        geometry (QRect): The geometry of the widget.

    Returns:
        QLabel: The created QLabel widget.
    """
    label = QtWidgets.QLabel(parent)
    label.setGeometry(geometry)
    label.setObjectName("label")
    label.setText(text)
    return label


def create_text_browser(parent, geometry, text):
    """
    Creates a QTextBrowser widget with the specified properties.

    Args:
        parent (QWidget): The parent widget.
        geometry (QRect): The geometry of the widget.
        text (str): The initial text of the widget.

    Returns:
        QTextBrowser: The created QTextBrowser widget.
    """
    text_browser = QtWidgets.QTextBrowser(parent)
    text_browser.setGeometry(geometry)
    text_browser.setObjectName("text_browser")
    text_browser.setPlainText(text)
    return text_browser

# noinspection PyUnresolvedReferences


class UiCLASMainWin(object):
    def __init__(self, CLAS_MainWin):
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

        self.returnPressed = False

        self.Line_SelectedFolder = create_custom_line_edit(CLAS_MainWin, QtCore.QRect(20, 30, 450, 22), "Line_SelectedFolder", "(Optional) Press 'Browse Folder...' to set a different scan folder location.", "darkgray")
        self.Line_SelectedFolder.returnPressed.connect(lambda: self.SelectFolder_SCAN_LE(self.Line_SelectedFolder.text()))
        self.Line_SelectedFolder.returnPressed.connect(self.is_return_pressed)
        self.RegBT_Browse = create_simple_button(CLAS_MainWin, QtCore.QRect(490, 30, 130, 24), "RegBT_Browse", "Browse Folder...", "", self.SelectFolder_SCAN)
        self.RegBT_SCAN_LOGS = create_custom_push_button(CLAS_MainWin, QtCore.QRect(220, 80, 200, 40), "RegBT_SCAN_LOGS", "SCAN LOGS", font_bold_10, "", self.CrashLogs_SCAN)
        self.RegBT_SCAN_FILES = create_custom_push_button(CLAS_MainWin, QtCore.QRect(245, 140, 150, 32), "RegBT_SCAN_FILES", "Scan Game Files", font_bold_10, "", self.Gamefiles_SCAN)
        self.RegBT_ChangeINI = create_custom_push_button(CLAS_MainWin, QtCore.QRect(90, 140, 130, 32), "RegBT_ChangeINI", "CHANGE INI PATH", font_10, "Select the folder where your Fallout4.ini is located so the Auto-Scanner can use that new folder location.", self.SelectFolder_INI)
        self.RegBT_CheckUpdates = create_custom_push_button(CLAS_MainWin, QtCore.QRect(420, 140, 140, 32), "RegBT_CheckUpdates", "CHECK FOR UPDATES", font_10, "", self.Update_Popup)

        SCAN_folder = UNIVERSE.CLAS_config["Scan_Path"].strip()
        if len(SCAN_folder) > 1:
            self.Line_SelectedFolder.setText(SCAN_folder)

        # SEGMENT - SETTINGS

        self.Line_Separator_1 = create_custom_frame(CLAS_MainWin, QtCore.QRect(40, 180, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Separator_1")
        self.LBL_Settings = create_custom_label(CLAS_MainWin, QtCore.QRect(290, 200, 60, 16), "SETTINGS", font_bold_10, "LBL_Settings")
        self.ChkBT_FCXMode = create_custom_check_box(CLAS_MainWin, QtCore.QRect(100, 230, 110, 20), "FCX MODE", "Enable if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly.", UNIVERSE.CLAS_config["FCX_Mode"], "ChkBT_FCXMode")
        # self.ChkBT_IMIMode = create_custom_check_box(CLAS_MainWin, QtCore.QRect(260, 210, 110, 100), "IGNORE ALL\nMANUAL FILE\nINSTALLATION\nWARNINGS", "Enable if you want Auto-Scanner to hide all manual installation warnings.\nI still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager.", UNIVERSE.CLAS_config["IMI_Mode"], "ChkBT_IMIMode")
        self.ChkBT_IMIMode = create_custom_check_box(CLAS_MainWin, QtCore.QRect(100, 270, 255, 20), "IGNORE MANUAL INSTALL WARNINGS", "Enable if you want Auto-Scanner to hide all manual installation warnings.\nI still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager.", UNIVERSE.CLAS_config["IMI_Mode"], "ChkBT_IMIMode")
        self.ChkBT_Update = create_custom_check_box(CLAS_MainWin, QtCore.QRect(430, 230, 110, 20), "UPDATE CHECK", "Enable if you want Auto-Scanner to check your Python version and if all required packages are installed.", UNIVERSE.CLAS_config["Update_Check"], "ChkBT_Update")
        self.ChkBT_PasteBin = create_custom_check_box(CLAS_MainWin, QtCore.QRect(220, 230, 200, 20), "DOWNLOAD FROM PASTEBIN", "Enable if you want Auto-Scanner to download your crashlog from Pastebin instead of a local directory.", checked=False, object_name="ChkBT_pastebin")
        # self.ChkBT_Stats = create_custom_check_box(CLAS_MainWin, QtCore.QRect(100, 270, 120, 20), "STAT LOGGING", "*DEPRECATED* This checkbox used to enable more detailed statistics but since those statistics are not collected anymore it does nothing.", UNIVERSE.CLAS_config["Stat_Logging"], "ChkBT_Stats", disabled=True)  # Does this do anything anymore?
        clas_toml_update("Stat_Logging", False)
        self.ChkBT_Unsolved = create_custom_check_box(CLAS_MainWin, QtCore.QRect(430, 270, 130, 20), "MOVE UNSOLVED", "Enable if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder.\n(Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages.)", UNIVERSE.CLAS_config["Move_Unsolved"], "ChkBT_Unsolved")

        # SEGMENT - ARTICLES / WEBSITES

        # SEPARATOR LINE 2
        self.Line_Separator_2 = create_custom_frame(CLAS_MainWin, QtCore.QRect(40, 310, 560, 20), QtWidgets.QFrame.Shape.HLine, QtWidgets.QFrame.Shadow.Sunken, "Line_Separator_2")
        # SEPARATOR TEXT 2 (ARTICLES / WEBSITES)
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
        font_8 = QtGui.QFont()
        font_8.setPointSize(8)
        # ARRANGE BUTTONS IN GRID
        for i, data in enumerate(button_data):
            button = QtWidgets.QPushButton(CLAS_MainWin)
            button.setGeometry(QtCore.QRect(40 + i % 3 * 190, 370 + i // 3 * 50, 180, 32))
            button.setObjectName("ArtBT_" + data["text"].replace(" ", ""))
            button.setFont(font_8)
            button.setText(data["text"])
            open_url = partial(QDesktopServices.openUrl, QUrl(data["url"]))
            button.clicked.connect(open_url)

        # BOTTOM

        # Button - HELP
        self.RegBT_Help = create_custom_push_button(CLAS_MainWin, QtCore.QRect(20, 480, 110, 24), "RegBT_Help", "HELP", font_10, "How To Use CLAS GUI", self.Help_Popup)
        # Button - EXIT
        self.RegBT_Exit = create_custom_push_button(CLAS_MainWin, QtCore.QRect(510, 480, 110, 24), "RegBT_Exit", "EXIT", font_10, "Exit CLAS GUI", CLAS_MainWin.close)

        # Usage
        self.TXT_Window = create_text_browser(CLAS_MainWin, QtCore.QRect(20, 510, 600, 120), "Crash Log Auto Scanner (CLAS) | Made by: Poet #9800\nContributors: evildarkarchon | kittivelae | AtomicFallout757")

        # ====================== CHECK BOXES ========================

        self.ChkBT_IMIMode.clicked.connect(lambda: clas_toml_update("IMI_Mode", True) if self.ChkBT_IMIMode.isChecked() else clas_toml_update("IMI_Mode", False))
        # self.ChkBT_Stats.clicked.connect(lambda: self.update_toml_config(self.ChkBT_Stats, "Stat_Logging"))
        self.ChkBT_Unsolved.clicked.connect(lambda: clas_toml_update("Move_Unsolved", True) if self.ChkBT_Unsolved.isChecked() else clas_toml_update("Move_Unsolved", False))
        self.ChkBT_Update.clicked.connect(lambda: clas_toml_update("Update_Check", True) if self.ChkBT_Update.isChecked() else clas_toml_update("Update_Check", False))
        self.ChkBT_FCXMode.clicked.connect(lambda: clas_toml_update("FCX_Mode", True) if self.ChkBT_FCXMode.isChecked() else clas_toml_update("FCX_Mode", False))
        self.ChkBT_PasteBin.clicked.connect(self.Pastebin_Mode)

        QtCore.QMetaObject.connectSlotsByName(CLAS_MainWin)

        # ================= MAIN BUTTON FUNCTIONS ===================
        # @staticmethod recommended for func that don't call "self".
    def is_return_pressed(self):
        if not self.returnPressed:
            self.returnPressed = True
            return
        else:
            self.returnPressed = False
            return

    def Pastebin_Mode(self):
        if self.ChkBT_PasteBin.isChecked():
            self.Line_SelectedFolder.returnPressed.disconnect()
            self.RegBT_Browse.setText("Download...")
            self.Line_SelectedFolder.setText("Enter the Pastebin URL of your crashlog here and press Return/Enter.")
            self.RegBT_SCAN_LOGS.clicked.disconnect()
            self.RegBT_SCAN_LOGS.clicked.connect(lambda: self.PasteBin_SCAN(self.Line_SelectedFolder.text()))
        else:
            self.Line_SelectedFolder.returnPressed.disconnect()
            self.Line_SelectedFolder.returnPressed.connect(self.SelectFolder_SCAN_LE)
            self.Line_SelectedFolder.returnPressed.connect(self.is_return_pressed)
            self.RegBT_Browse.setText("Browse Folder...")
            if not UNIVERSE.CLAS_config["Scan_Path"]:
                self.Line_SelectedFolder.setText("(Optional) Press 'Browse Folder...' to set a different scan folder location.")
            else:
                self.Line_SelectedFolder.setText(UNIVERSE.CLAS_config["Scan_Path"])
            self.RegBT_SCAN_LOGS.clicked.disconnect()
            self.RegBT_SCAN_LOGS.clicked.connect(self.CrashLogs_SCAN)

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

    def PasteBin_SCAN(self, url=""):
        if not url:
            url = self.Line_SelectedFolder.text()

        parsed_url = urlparse(url)
        url_path = list(parsed_url.path.split("/"))  # using list() to make sure that the url_path is a list.

        if parsed_url.scheme != "https" or parsed_url.netloc != "pastebin.com" or "raw" in url_path:
            QtWidgets.QMessageBox.warning(CLAS_MainWin, "Invalid URL", "The URL you entered is invalid. Please enter a valid Pastebin URL.")
            return

        if not Path.cwd().joinpath("pastebin").exists():
            Path.cwd().joinpath("pastebin").mkdir()

        UNIVERSE.CLAS_config["Scan_Path"] = str(Path.cwd().joinpath("pastebin"))

        url = url.replace("https://pastebin.com/", "https://pastebin.com/raw/")
        request = requests.get(url, timeout=30)
        try:
            if not request.status_code == requests.codes.ok:  # type: ignore
                request.raise_for_status()
            with open(Path.cwd().joinpath("pastebin", f"crash-pastebin-{url_path[1]}.log"), "w") as f:
                f.write(request.text.strip())
            scan_logs()
        except requests.HTTPError:
            QtWidgets.QMessageBox.warning(CLAS_MainWin, "HTTP Error", "The URL you entered returned an HTTP error. Please enter a valid Pastebin URL.")

    def SelectFolder_SCAN_LE(self, directory):
        if directory:
            clas_toml_update("Scan_Path", directory)
            # Change text color back to black.
            LSF_palette = self.Line_SelectedFolder.palette()
            LSF_palette.setColor(QPalette.ColorRole.Text, QColor("black"))
            self.Line_SelectedFolder.setPalette(LSF_palette)

    def SelectFolder_SCAN(self):
        SCAN_folder = QFileDialog.getExistingDirectory()
        if SCAN_folder:
            self.Line_SelectedFolder.setText(SCAN_folder)
            clas_toml_update("Scan_Path", SCAN_folder)
            # Change text color back to black.
            LSF_palette = self.Line_SelectedFolder.palette()
            LSF_palette.setColor(QPalette.ColorRole.Text, QColor("black"))
            self.Line_SelectedFolder.setPalette(LSF_palette)

    @staticmethod
    def SelectFolder_INI():
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(CLAS_MainWin, "New INI Path Set", "You have set the new path to: \n" + INI_folder)
            clas_toml_update("INI_Path", INI_folder)

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
    ui = UiCLASMainWin(CLAS_MainWin)
    CLAS_MainWin.show()
    sys.exit(app.exec())
