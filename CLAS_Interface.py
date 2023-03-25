# CRASH LOG AUTO SCANNER GUI WITH PySide6 (PYTHON 3.9 COMPLIANT)
import sys
from CLAS_Database import UNIVERSE, GALAXY, clas_ini_create, clas_ini_update, clas_update_check
from CLAS_ScanLogs import scan_logs
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPalette
from PySide6.QtWidgets import QFileDialog

clas_ini_create()


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
        self.Line_SelectedFolder = QtWidgets.QLineEdit(CLAS_MainWin)
        self.Line_SelectedFolder.setGeometry(QtCore.QRect(20, 30, 450, 22))
        self.Line_SelectedFolder.setObjectName("Line_SelectedFolder")
        SCAN_folder = UNIVERSE.CLAS_config["MAIN"]["Scan Path"].strip()
        if len(SCAN_folder) > 1:
            self.Line_SelectedFolder.setText(SCAN_folder)
        else:
            self.Line_SelectedFolder.setText("(Optional) Press 'Browse Folder...' to set a different scan folder location.")
        # Change text color to gray.
        LSF_palette = self.Line_SelectedFolder.palette()
        LSF_palette.setColor(QPalette.Text, QColor("darkgray"))  # type: ignore
        self.Line_SelectedFolder.setPalette(LSF_palette)

        # Button - Browse Folder
        self.RegBT_Browse = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Browse.setGeometry(QtCore.QRect(490, 30, 130, 24))
        self.RegBT_Browse.setObjectName("RegBT_Browse")
        self.RegBT_Browse.setText("Browse Folder...")
        self.RegBT_Browse.clicked.connect(self.SelectFolder_SCAN)  # type: ignore

        # Button - SCAN LOGS (CRASH LOGS)
        self.RegBT_SCAN_LOGS = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_SCAN_LOGS.setGeometry(QtCore.QRect(220, 80, 200, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.RegBT_SCAN_LOGS.setFont(font)
        self.RegBT_SCAN_LOGS.setObjectName("RegBT_SCAN_LOGS")
        self.RegBT_SCAN_LOGS.setText("SCAN LOGS")
        self.RegBT_SCAN_LOGS.clicked.connect(self.CrashLogs_SCAN)  # type: ignore

        # Button - SCAN FILES (GAME FILES)
        self.RegBT_SCAN_FILES = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_SCAN_FILES.setGeometry(QtCore.QRect(245, 150, 150, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.RegBT_SCAN_FILES.setFont(font)
        self.RegBT_SCAN_FILES.setObjectName("RegBT_SCAN_FILES")
        self.RegBT_SCAN_FILES.setText("Scan Game Files")
        self.RegBT_SCAN_FILES.clicked.connect(self.Gamefiles_SCAN)  # type: ignore

        # Button - Set INI Path
        self.RegBT_ChangeINI = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_ChangeINI.setGeometry(QtCore.QRect(90, 150, 130, 32))
        self.RegBT_ChangeINI.setObjectName("RegBT_ChangeINI")
        self.RegBT_ChangeINI.setText("CHANGE INI PATH")
        self.RegBT_ChangeINI.setToolTip("Select the folder where your Fallout4.ini is located so the Auto-Scanner can use that new folder location.")
        self.RegBT_ChangeINI.clicked.connect(self.SelectFolder_INI)  # type: ignore

        # Button - Check Updates
        self.RegBT_CheckUpdates = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_CheckUpdates.setGeometry(QtCore.QRect(420, 150, 140, 32))
        self.RegBT_CheckUpdates.setObjectName("RegBT_CheckUpdates")
        self.RegBT_CheckUpdates.setText("CHECK FOR UPDATES")
        self.RegBT_CheckUpdates.clicked.connect(self.Update_Popup)  # type: ignore

        # SEGMENT - SETTINGS

        # SEPARATOR LINE 1
        self.Line_Separator_1 = QtWidgets.QFrame(CLAS_MainWin)
        self.Line_Separator_1.setGeometry(QtCore.QRect(40, 180, 560, 20))
        self.Line_Separator_1.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # type: ignore
        self.Line_Separator_1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # type: ignore
        self.Line_Separator_1.setObjectName("Line_Separator_1")
        # SEPARATOR TEXT 1 (SETTINGS)
        self.LBL_Settings = QtWidgets.QLabel(CLAS_MainWin)
        self.LBL_Settings.setGeometry(QtCore.QRect(290, 200, 60, 16))
        self.LBL_Settings.setText("SETTINGS")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.LBL_Settings.setFont(font)
        self.LBL_Settings.setObjectName("LBL_Settings")

        # Check Box - FCX Mode
        self.ChkBT_FCXMode = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_FCXMode.setGeometry(QtCore.QRect(100, 230, 110, 20))
        self.ChkBT_FCXMode.setText("FCX MODE")
        self.ChkBT_FCXMode.setToolTip("Enable if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly.")
        if UNIVERSE.CLAS_config.getboolean("MAIN", "FCX Mode"):
            self.ChkBT_FCXMode.setChecked(True)
        self.ChkBT_FCXMode.setObjectName("ChkBT_FCXMode")

        # Check Box - IMI Mode
        self.ChkBT_IMIMode = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_IMIMode.setGeometry(QtCore.QRect(260, 210, 100, 100))
        self.ChkBT_IMIMode.setText("IGNORE ALL\nMANUAL FILE\nINSTALLATION\nWARNINGS")
        self.ChkBT_IMIMode.setToolTip("Enable if you want Auto-Scanner to hide all manual installation warnings.\nI still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager. ")
        if UNIVERSE.CLAS_config.getboolean("MAIN", "IMI Mode"):
            self.ChkBT_IMIMode.setChecked(True)
        self.ChkBT_IMIMode.setObjectName("ChkBT_IMIMode")

        # Check Box - INI Update
        self.ChkBT_Update = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Update.setGeometry(QtCore.QRect(430, 230, 110, 20))
        self.ChkBT_Update.setText("UPDATE CHECK")
        self.ChkBT_Update.setToolTip("Enable if you want Auto-Scanner to check your Python version and if all required packages are installed. ")
        if UNIVERSE.CLAS_config.getboolean("MAIN", "Update Check"):
            self.ChkBT_Update.setChecked(True)
        self.ChkBT_Update.setObjectName("ChkBT_Update")

        # Check Box - INI Stats
        self.ChkBT_Stats = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Stats.setGeometry(QtCore.QRect(100, 270, 120, 20))
        self.ChkBT_Stats.setText("STAT LOGGING")
        self.ChkBT_Stats.setToolTip("Enable if you want Auto-Scanner to show extra stats about scanned logs in the command line window. ")
        if UNIVERSE.CLAS_config.getboolean("MAIN", "Stat Logging"):
            self.ChkBT_Stats.setChecked(True)
        self.ChkBT_Stats.setObjectName("ChkBT_Stats")

        # Check Box - INI Unsolved
        self.ChkBT_Unsolved = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Unsolved.setGeometry(QtCore.QRect(430, 270, 130, 20))
        self.ChkBT_Unsolved.setText("MOVE UNSOLVED")
        self.ChkBT_Unsolved.setToolTip(
            "Enable if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder.\n(Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages.)")
        if UNIVERSE.CLAS_config.getboolean("MAIN", "Move Unsolved"):
            self.ChkBT_Unsolved.setChecked(True)
        self.ChkBT_Unsolved.setObjectName("ChkBT_Unsolved")

        # SEGMENT - ARTICLES / WEBSITES

        # SEPARATOR LINE 2
        self.Line_Separator_2 = QtWidgets.QFrame(CLAS_MainWin)
        self.Line_Separator_2.setGeometry(QtCore.QRect(40, 310, 560, 20))
        self.Line_Separator_2.setFrameShape(QtWidgets.QFrame.HLine)  # type: ignore
        self.Line_Separator_2.setFrameShadow(QtWidgets.QFrame.Sunken)  # type: ignore
        self.Line_Separator_2.setObjectName("Line_Separator_2")
        # SEPARATOR TEXT 2 (ARTICLES / WEBSITES)
        self.LBL_ArtWeb = QtWidgets.QLabel(CLAS_MainWin)
        self.LBL_ArtWeb.setGeometry(QtCore.QRect(250, 330, 140, 16))
        self.LBL_ArtWeb.setText("ARTICLES / WEBSITES")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.LBL_ArtWeb.setFont(font)
        self.LBL_ArtWeb.setObjectName("LBL_ArtWeb")

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
        self.RegBT_Help = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Help.setGeometry(QtCore.QRect(20, 480, 110, 24))
        self.RegBT_Help.setObjectName("RegBT_Help")
        self.RegBT_Help.setText("HELP")
        self.RegBT_Help.setToolTip("How To Use CLAS GUI")
        self.RegBT_Help.clicked.connect(self.Help_Popup)  # type: ignore
        # Button - EXIT
        self.RegBT_Exit = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Exit.setGeometry(QtCore.QRect(510, 480, 110, 24))
        self.RegBT_Exit.setObjectName("RegBT_Exit")
        self.RegBT_Exit.setText("EXIT")
        self.RegBT_Exit.setToolTip("Exit CLAS GUI")
        self.RegBT_Exit.clicked.connect(CLAS_MainWin.close)  # type: ignore

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
            clas_ini_update(config_key, "true")
        else:
            clas_ini_update(config_key, "false")

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
            clas_ini_update("Scan Path", SCAN_folder)
            # Change text color back to black.
            LSF_palette = self.Line_SelectedFolder.palette()  # type: ignore
            LSF_palette.setColor(QPalette.ColorRole.Text, QColor("black"))  # type: ignore
            self.Line_SelectedFolder.setPalette(LSF_palette)  # type: ignore

    @staticmethod
    def SelectFolder_INI():
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(CLAS_MainWin, "New INI Path Set", "You have set the new path to: \n" + INI_folder)  # type: ignore
            clas_ini_update("INI Path", INI_folder)

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
-----
PRESS 'SCAN LOGS' BUTTON TO SCAN ALL AVAILABLE BUFFOUT 4 CRASH LOGS
OR
PRESS 'Scan Game Files' BUTTON TO CHECK YOUR FALLOUT 4 GAME FILES
-----
    """
    print(gui_prompt)
    app = QtWidgets.QApplication(sys.argv)
    CLAS_MainWin = QtWidgets.QDialog()
    ui = UiCLASMainWin()
    ui.setup_ui(CLAS_MainWin)
    CLAS_MainWin.show()
    sys.exit(app.exec())
