# CRASH LOG AUTO SCANNER GUI WITH PYQT5 (PYTHON 3.9 COMPLIANT)
# PYQT6 GIVES ERROR DURING PYINSTALLER SETUP (CAN'T FIND DLL)

import sys
import Scan_Crashlogs
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QDesktopServices, QColor, QPalette

CLAS_Current = Scan_Crashlogs.CLAS_Current
CLAS_config = Scan_Crashlogs.CLAS_config
write_ini_value_to_file = Scan_Crashlogs.write_ini_value_to_file


# noinspection PyUnresolvedReferences
class UiClasMainwin(object):
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
        self.RegBT_SCAN = None

        self.TXT_About = None
        self.TXT_Contributors = None
        self.TXT_Window = None

        self.WebBT_Buffout4_Nexus = None
        self.WebBT_CLAS_Github = None
        self.WebBT_CLAS_Nexus = None

    def setup_ui(self, CLAS_MainWin):

        # MAIN WINDOW
        CLAS_MainWin.setObjectName("CLAS_MainWin")
        CLAS_MainWin.setWindowTitle(f"Crash Log Auto Scanner {CLAS_Current[-4:]}")
        CLAS_MainWin.resize(640, 640)
        CLAS_MainWin.setMinimumSize(QtCore.QSize(640, 640))
        CLAS_MainWin.setMaximumSize(QtCore.QSize(640, 640))

        # ==================== MAIN WINDOW ITEMS =====================
        # TOP

        # Text Box - Selected Folder
        self.Line_SelectedFolder = QtWidgets.QLineEdit(CLAS_MainWin)
        self.Line_SelectedFolder.setGeometry(QtCore.QRect(20, 30, 450, 22))
        self.Line_SelectedFolder.setObjectName("Line_SelectedFolder")
        self.Line_SelectedFolder.setStyleSheet("color: darkgray;")
        self.Line_SelectedFolder.setText("(Optional) Press 'Browse Folder...' to set a different scan folder location.")
        if len(CLAS_config.get("MAIN", "Scan Path")) > 1:
            SCAN_folder = CLAS_config.get("MAIN", "Scan Path")
            self.Line_SelectedFolder.setText(SCAN_folder)
        # Change text color to gray.
        LSF_palette = self.Line_SelectedFolder.palette()
        # LSF_palette.setColor(QPalette.text, QColor(Qt.darkgray)) # type: ignore
        self.Line_SelectedFolder.setPalette(LSF_palette)

        # Button - Browse Folder
        self.RegBT_Browse = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Browse.setGeometry(QtCore.QRect(490, 30, 130, 24))
        self.RegBT_Browse.setObjectName("RegBT_Browse")
        self.RegBT_Browse.setText("Browse Folder...")
        self.RegBT_Browse.clicked.connect(self.SelectFolder_SCAN)

        # Button - SCAN (CRASH LOGS)
        self.RegBT_SCAN = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_SCAN.setGeometry(QtCore.QRect(220, 80, 200, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.RegBT_SCAN.setFont(font)
        self.RegBT_SCAN.setObjectName("RegBT_SCAN")
        self.RegBT_SCAN.setText("SCAN LOGS")
        self.RegBT_SCAN.clicked.connect(self.CrashLogs_SCAN)

        # Button - Set INI Path
        self.RegBT_ChangeINI = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_ChangeINI.setGeometry(QtCore.QRect(90, 150, 130, 24))
        self.RegBT_ChangeINI.setObjectName("RegBT_ChangeINI")
        self.RegBT_ChangeINI.setText("CHANGE INI PATH")
        self.RegBT_ChangeINI.setToolTip("Select the folder where your Fallout4.ini is located so the Auto-Scanner can use that new folder location.")
        self.RegBT_ChangeINI.clicked.connect(self.SelectFolder_INI)

        # Button - Check Updates
        self.RegBT_CheckUpdates = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_CheckUpdates.setGeometry(QtCore.QRect(410, 150, 150, 24))
        self.RegBT_CheckUpdates.setObjectName("RegBT_CheckUpdates")
        self.RegBT_CheckUpdates.setText("CHECK FOR UPDATES")
        self.RegBT_CheckUpdates.clicked.connect(self.Update_Popup)

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
        if CLAS_config.getboolean("MAIN", "FCX Mode"):
            self.ChkBT_FCXMode.setChecked(True)
        self.ChkBT_FCXMode.setObjectName("ChkBT_FCXMode")
        self.ChkBT_FCXMode.stateChanged.connect(self.Bool_FCXMode)

        # Check Box - IMI Mode
        self.ChkBT_IMIMode = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_IMIMode.setGeometry(QtCore.QRect(260, 235, 110, 50))
        self.ChkBT_IMIMode.setText("IGNORE ALL\nMANUAL FILE\nINSTALLATION\nWARNINGS")
        self.ChkBT_IMIMode.setToolTip("Enable if you want Auto-Scanner to hide all manual installation warnings. I still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager. ")
        if CLAS_config.getboolean("MAIN", "IMI Mode"):
            self.ChkBT_IMIMode.setChecked(True)
        self.ChkBT_IMIMode.setObjectName("ChkBT_IMIMode")
        self.ChkBT_IMIMode.stateChanged.connect(self.Bool_IMIMode)

        # Check Box - INI Update
        self.ChkBT_Update = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Update.setGeometry(QtCore.QRect(420, 230, 110, 20))
        self.ChkBT_Update.setText("UPDATE CHECK")
        self.ChkBT_Update.setToolTip("Enable if you want Auto-Scanner to check your Python version and if all required packages are installed. ")
        if CLAS_config.getboolean("MAIN", "Update Check"):
            self.ChkBT_Update.setChecked(True)
        self.ChkBT_Update.setObjectName("ChkBT_Update")
        self.ChkBT_Update.stateChanged.connect(self.Bool_INIUpdate)

        # Check Box - INI Stats
        self.ChkBT_Stats = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Stats.setGeometry(QtCore.QRect(100, 270, 120, 20))
        self.ChkBT_Stats.setText("STAT LOGGING")
        self.ChkBT_Stats.setToolTip("Enable if you want Auto-Scanner to show extra stats about scanned logs in the command line window. ")
        if CLAS_config.getboolean("MAIN", "Stat Logging"):
            self.ChkBT_Stats.setChecked(True)
        self.ChkBT_Stats.setObjectName("ChkBT_Stats")
        self.ChkBT_Stats.stateChanged.connect(self.Bool_INIStats)

        # Check Box - INI Unsolved
        self.ChkBT_Unsolved = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Unsolved.setGeometry(QtCore.QRect(420, 270, 130, 20))
        self.ChkBT_Unsolved.setText("MOVE UNSOLVED")
        self.ChkBT_Unsolved.setToolTip("Enable if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder. (Unsolved logs are all crash logs where Auto-Scanner didn't detect any known crash errors or messages.)")
        if CLAS_config.getboolean("MAIN", "Move Unsolved"):
            self.ChkBT_Unsolved.setChecked(True)
        self.ChkBT_Unsolved.setObjectName("ChkBT_Unsolved")
        self.ChkBT_Unsolved.stateChanged.connect(self.Bool_INIUnsolved)

        # SEGMENT - ARTICLES / WEBSITES

        # SEPARATOR LINE 2
        self.Line_Separator_2 = QtWidgets.QFrame(CLAS_MainWin)
        self.Line_Separator_2.setGeometry(QtCore.QRect(40, 310, 560, 20))
        self.Line_Separator_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # type: ignore
        self.Line_Separator_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # type: ignore
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

        # Button - Article Buffout 4
        self.ArtBT_Buffout4 = QtWidgets.QPushButton(CLAS_MainWin)
        self.ArtBT_Buffout4.setGeometry(QtCore.QRect(40, 370, 180, 30))
        self.ArtBT_Buffout4.setObjectName("ArtBT_Buffout4")
        self.ArtBT_Buffout4.setText("BUFFOUT 4 INSTALLATION")
        self.ArtBT_Buffout4.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/articles/3115")))  # type: ignore
        # Button - Article Advanced Troubleshooting
        self.ArtBT_Troubleshoot = QtWidgets.QPushButton(CLAS_MainWin)
        self.ArtBT_Troubleshoot.setGeometry(QtCore.QRect(230, 370, 210, 30))
        self.ArtBT_Troubleshoot.setObjectName("ArtBT_Troubleshoot")
        self.ArtBT_Troubleshoot.setText("ADVANCED TROUBLESHOOTING")
        self.ArtBT_Troubleshoot.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/articles/4141")))  # type: ignore
        # Button - Article Important Patches
        self.ArtBT_Patches = QtWidgets.QPushButton(CLAS_MainWin)
        self.ArtBT_Patches.setGeometry(QtCore.QRect(450, 370, 180, 30))
        self.ArtBT_Patches.setObjectName("ArtBT_Patches")
        self.ArtBT_Patches.setText("IMPORTANT PATCHES LIST")
        self.ArtBT_Patches.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/articles/3769")))  # type: ignore
        # Button - Website Buffout 4
        self.WebBT_Buffout4_Nexus = QtWidgets.QPushButton(CLAS_MainWin)
        self.WebBT_Buffout4_Nexus.setGeometry(QtCore.QRect(40, 420, 180, 30))
        self.WebBT_Buffout4_Nexus.setObjectName("WebBT_Buffout4")
        self.WebBT_Buffout4_Nexus.setText("BUFFOUT 4 NEXUS PAGE")
        self.WebBT_Buffout4_Nexus.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/47359")))  # type: ignore
        # Button - Website CLAS Nexus
        self.WebBT_CLAS_Nexus = QtWidgets.QPushButton(CLAS_MainWin)
        self.WebBT_CLAS_Nexus.setGeometry(QtCore.QRect(230, 420, 210, 30))
        self.WebBT_CLAS_Nexus.setObjectName("WebBT_CLAS_Nexus")
        self.WebBT_CLAS_Nexus.setText("AUTO SCANNER NEXUS PAGE")
        self.WebBT_CLAS_Nexus.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255")))  # type: ignore
        # Button - Website CLAS Github
        self.WebBT_CLAS_Github = QtWidgets.QPushButton(CLAS_MainWin)
        self.WebBT_CLAS_Github.setGeometry(QtCore.QRect(450, 420, 180, 30))
        self.WebBT_CLAS_Github.setObjectName("WebBT_CLAS_Git")
        self.WebBT_CLAS_Github.setText("AUTO SCANNER GITHUB")
        self.WebBT_CLAS_Github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/GuidanceOfGrace/Buffout4-CLAS/releases")))  # type: ignore

        # BOTTOM

        # Button - HELP
        self.RegBT_Help = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Help.setGeometry(QtCore.QRect(20, 480, 110, 24))
        self.RegBT_Help.setObjectName("RegBT_Help")
        self.RegBT_Help.setText("HELP")
        self.RegBT_Help.setToolTip("How To Use CLAS GUI")
        self.RegBT_Help.clicked.connect(self.Help_Popup)
        # Button - EXIT
        self.RegBT_Exit = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Exit.setGeometry(QtCore.QRect(510, 480, 110, 24))
        self.RegBT_Exit.setObjectName("RegBT_Exit")
        self.RegBT_Exit.setText("EXIT")
        self.RegBT_Exit.setToolTip("Exit CLAS GUI")
        self.RegBT_Exit.clicked.connect(CLAS_MainWin.close)

        # TEXT Box - Window
        self.TXT_Window = QtWidgets.QTextBrowser(CLAS_MainWin)
        self.TXT_Window.setGeometry(QtCore.QRect(20, 510, 600, 120))
        self.TXT_Window.setObjectName("TXT_Window")
        # TEXT Label - About
        self.TXT_About = QtWidgets.QLabel(CLAS_MainWin)
        self.TXT_About.setGeometry(QtCore.QRect(30, 520, 320, 16))
        self.TXT_About.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText)  # type: ignore
        self.TXT_About.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)  # type: ignore
        self.TXT_About.setObjectName("TXT_About")
        self.TXT_About.setText("Crash Log Auto Scanner (CLAS) | Made by: Poet #9800")
        # TEXT Label - Contributors
        self.TXT_Contributors = QtWidgets.QLabel(CLAS_MainWin)
        self.TXT_Contributors.setGeometry(QtCore.QRect(30, 540, 340, 16))
        self.TXT_Contributors.setObjectName("TXT_Contributors")
        self.TXT_Contributors.setText("Contributors: evildarkarchon | kittivelae | AtomicFallout757")

        QtCore.QMetaObject.connectSlotsByName(CLAS_MainWin)

        # ================= MAIN BUTTON FUNCTIONS ===================
        # @staticmethod recommended for func that don't call "self".

    @staticmethod
    def CrashLogs_SCAN():
        Scan_Crashlogs.scan_logs()

    def SelectFolder_SCAN(self):
        SCAN_folder = QFileDialog.getExistingDirectory()
        if SCAN_folder:
            self.Line_SelectedFolder.setText(SCAN_folder)  # type: ignore
            write_ini_value_to_file("Scan Path", SCAN_folder)
            # Change text color back to black.
            LSF_palette = self.Line_SelectedFolder.palette()  # type: ignore
            LSF_palette.setColor(QPalette.ColorRole.Text, QColor("black"))  # type: ignore
            self.Line_SelectedFolder.setPalette(LSF_palette)  # type: ignore

    @staticmethod
    def SelectFolder_INI():
        INI_folder = QFileDialog.getExistingDirectory()  # QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(CLAS_MainWin, "New INI Path Set", "You set the new path to: \n" + INI_folder)  # type: ignore
            write_ini_value_to_file("INI Path", INI_folder)

        # ================== POP-UPS / WARNINGS =====================

    @staticmethod
    def Help_Popup():
        QtWidgets.QMessageBox.information(CLAS_MainWin, "Need Help?", "If you have trouble running this program or wish to submit your crash logs for additional help from our support team, join the Collective Modding Discord server. Press OK to open the server link in your browser. \n")
        QDesktopServices.openUrl(QUrl("https://discord.com/invite/7ZZbrsGQh4"))

    @staticmethod
    def Update_Popup():
        if Scan_Crashlogs.run_update():
            QtWidgets.QMessageBox.information(CLAS_MainWin, "CLAS Update", "You have the latest version of Crash Log Auto Scanner!")
        else:
            QtWidgets.QMessageBox.warning(CLAS_MainWin, "CLAS Update", "New Crash Log Auto Scanner version detected!\nPress OK to open the CLAS Nexus Page.")
            QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255?tab=files"))

        # ====================== CHECK BOXES ========================

    def Bool_IMIMode(self):
        if self.ChkBT_IMIMode.isChecked():  # type: ignore
            write_ini_value_to_file("IMI Mode", "true")
        else:
            write_ini_value_to_file("IMI Mode", "false")

    def Bool_INIStats(self):
        if self.ChkBT_Stats.isChecked():  # type: ignore
            write_ini_value_to_file("Stat Logging", "true")
        else:
            write_ini_value_to_file("Stat Logging", "false")

    def Bool_INIUnsolved(self):
        if self.ChkBT_Unsolved.isChecked():  # type: ignore
            write_ini_value_to_file("Move Unsolved", "true")
        else:
            write_ini_value_to_file("Move Unsolved", "false")

    def Bool_INIUpdate(self):
        if self.ChkBT_Update.isChecked():  # type: ignore
            write_ini_value_to_file("Update Check", "true")
        else:
            write_ini_value_to_file("Update Check", "false")

    def Bool_FCXMode(self):
        if self.ChkBT_FCXMode.isChecked():  # type: ignore
            write_ini_value_to_file("FCX Mode", "true")
        else:
            write_ini_value_to_file("FCX Mode", "false")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CLAS_MainWin = QtWidgets.QDialog()
    ui = UiClasMainwin()
    ui.setup_ui(CLAS_MainWin)
    CLAS_MainWin.show()
    sys.exit(app.exec())
