# CRASH LOG AUTO SCANNER GUI WITH PYQT5 (PYTHON 3.9 COMPLIANT)
# PYQT6 GIVES ERROR DURING PYINSTALLER CONVERSION (CAN'T FIND DLL)

import os
import sys
import shutil
import configparser
import Scan_Crashlogs
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QDesktopServices, QColor, QPalette
from PyQt5.QtCore import Qt, QUrl

CLAS_config = Scan_Crashlogs.CLAS_config
write_ini_value_to_file = Scan_Crashlogs.write_ini_value_to_file

class Ui_CLAS_MainWin(object):
    def setupUi(self, CLAS_MainWin):

        # MAIN WINDOW
        CLAS_MainWin.setObjectName("CLAS_MainWin")
        CLAS_MainWin.resize(640, 640)
        CLAS_MainWin.setMinimumSize(QtCore.QSize(640, 640))
        CLAS_MainWin.setMaximumSize(QtCore.QSize(640, 640))
        
        # ==================== MAIN WINDOW ITEMS =====================
        # TOP

        # Text Box - Selected Folder
        self.Line_SelectedFolder = QtWidgets.QLineEdit(CLAS_MainWin)
        self.Line_SelectedFolder.setGeometry(QtCore.QRect(20, 30, 450, 22))
        self.Line_SelectedFolder.setObjectName("Line_SelectedFolder")
        self.Line_SelectedFolder.setText("(Optional) Press 'Browse Folder...' to set a different scan folder location.")
        if len(CLAS_config["MAIN"]["Scan Path"]) > 1:
            SCAN_folder = CLAS_config["MAIN"]["Scan Path"]
            self.Line_SelectedFolder.setText(SCAN_folder)
        # Change text color to gray.
        LSF_palette = self.Line_SelectedFolder.palette()
        LSF_palette.setColor(QPalette.Text, QColor(Qt.darkGray)) # type: ignore
        self.Line_SelectedFolder.setPalette(LSF_palette)
        
        # Button - Browse Folder
        self.RegBT_Browse = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Browse.setGeometry(QtCore.QRect(490, 30, 130, 24))
        self.RegBT_Browse.setObjectName("RegBT_Browse")
        self.RegBT_Browse.clicked.connect(self.SelectFolder_SCAN)
        
        # Button - SCAN (CRASH LOGS)
        self.RegBT_SCAN = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_SCAN.setGeometry(QtCore.QRect(220, 80, 200, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.RegBT_SCAN.setFont(font)
        self.RegBT_SCAN.setObjectName("RegBT_SCAN")
        self.RegBT_SCAN.clicked.connect(self.CrashLogs_SCAN)
        
        # Button - Set INI Path
        self.RegBT_ChangeINI = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_ChangeINI.setGeometry(QtCore.QRect(90, 150, 130, 24))
        self.RegBT_ChangeINI.setObjectName("RegBT_ChangeINI")
        self.RegBT_ChangeINI.clicked.connect(self.SelectFolder_INI)
        
        # Button - Check Updates
        self.RegBT_CheckUpdates = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_CheckUpdates.setGeometry(QtCore.QRect(410, 150, 130, 24))
        self.RegBT_CheckUpdates.setObjectName("RegBT_CheckUpdates")
        self.RegBT_CheckUpdates.clicked.connect(self.Update_Popup)

        # SEGMENT - SETTINGS

        # SEPARATOR LINE 1
        self.Line_Separator_1 = QtWidgets.QFrame(CLAS_MainWin)
        self.Line_Separator_1.setGeometry(QtCore.QRect(40, 180, 560, 20))
        self.Line_Separator_1.setFrameShape(QtWidgets.QFrame.HLine) # type: ignore
        self.Line_Separator_1.setFrameShadow(QtWidgets.QFrame.Sunken) # type: ignore
        self.Line_Separator_1.setObjectName("Line_Separator_1")
        # SEPARATOR TEXT 1 (SETTINGS)
        self.LBL_Settings = QtWidgets.QLabel(CLAS_MainWin)
        self.LBL_Settings.setGeometry(QtCore.QRect(290, 200, 60, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.LBL_Settings.setFont(font)
        self.LBL_Settings.setObjectName("LBL_Settings")
        
        # Check Box - FCX Mode
        self.ChkBT_FCXMode = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_FCXMode.setGeometry(QtCore.QRect(100, 230, 110, 20))
        if CLAS_config.getboolean("MAIN", "FCX Mode"):
            self.ChkBT_FCXMode.setChecked(True)
        self.ChkBT_FCXMode.setObjectName("ChkBT_FCXMode")
        self.ChkBT_FCXMode.stateChanged.connect(self.Bool_FCXMode)
        
        # Check Box - IMI Mode
        self.ChkBT_IMIMode = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_IMIMode.setGeometry(QtCore.QRect(260, 235, 110, 50))
        if CLAS_config.getboolean("MAIN", "IMI Mode"):
            self.ChkBT_IMIMode.setChecked(True)
        self.ChkBT_IMIMode.setObjectName("ChkBT_IMIMode")
        self.ChkBT_IMIMode.stateChanged.connect(self.Bool_IMIMode)
        
        # Check Box - INI Update
        self.ChkBT_Update = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Update.setGeometry(QtCore.QRect(420, 230, 110, 20))
        if CLAS_config.getboolean("MAIN", "Update Check"):
            self.ChkBT_Update.setChecked(True)
        self.ChkBT_Update.setObjectName("ChkBT_Update")
        self.ChkBT_Update.stateChanged.connect(self.Bool_INIUpdate)

        # Check Box - INI Stats
        self.ChkBT_Stats = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Stats.setGeometry(QtCore.QRect(100, 270, 120, 20))
        if CLAS_config.getboolean("MAIN", "Stat Logging"):
            self.ChkBT_Stats.setChecked(True)
        self.ChkBT_Stats.setObjectName("ChkBT_Stats")
        self.ChkBT_Stats.stateChanged.connect(self.Bool_INIStats)
        
        # Check Box - INI Unsolved
        self.ChkBT_Unsolved = QtWidgets.QCheckBox(CLAS_MainWin)
        self.ChkBT_Unsolved.setGeometry(QtCore.QRect(420, 270, 120, 20))
        if CLAS_config.getboolean("MAIN", "Move Unsolved"):
            self.ChkBT_Unsolved.setChecked(True)
        self.ChkBT_Unsolved.setObjectName("ChkBT_Unsolved")
        self.ChkBT_Unsolved.stateChanged.connect(self.Bool_INIUnsolved)

        # SEGMENT - ARTICLES / WEBSITES

        # SEPARATOR LINE 2
        self.Line_Separator_2 = QtWidgets.QFrame(CLAS_MainWin)
        self.Line_Separator_2.setGeometry(QtCore.QRect(40, 310, 560, 20))
        self.Line_Separator_2.setFrameShape(QtWidgets.QFrame.HLine) # type: ignore
        self.Line_Separator_2.setFrameShadow(QtWidgets.QFrame.Sunken) # type: ignore
        self.Line_Separator_2.setObjectName("Line_Separator_2")
        # SEPARATOR TEXT 2 (ARTICLES / WEBSITES)
        self.LBL_ArtWeb = QtWidgets.QLabel(CLAS_MainWin)
        self.LBL_ArtWeb.setGeometry(QtCore.QRect(250, 330, 140, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.LBL_ArtWeb.setFont(font)
        self.LBL_ArtWeb.setObjectName("LBL_ArtWeb")
        
        # Button - Article Buffout 4
        self.ArtBT_Bufout4 = QtWidgets.QPushButton(CLAS_MainWin)
        self.ArtBT_Bufout4.setGeometry(QtCore.QRect(40, 370, 150, 30))
        self.ArtBT_Bufout4.setObjectName("ArtBT_Bufout4")
        self.ArtBT_Bufout4.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/articles/3115")))
        # Button - Article Advanced Troubleshooting
        self.ArtBT_Trblshoot = QtWidgets.QPushButton(CLAS_MainWin)
        self.ArtBT_Trblshoot.setGeometry(QtCore.QRect(220, 370, 200, 30))
        self.ArtBT_Trblshoot.setObjectName("ArtBT_Trblshoot")
        self.ArtBT_Trblshoot.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/articles/4141")))
        # Button - Article Important Patches 
        self.ArtBT_Patches = QtWidgets.QPushButton(CLAS_MainWin)
        self.ArtBT_Patches.setGeometry(QtCore.QRect(450, 370, 150, 30))
        self.ArtBT_Patches.setObjectName("ArtBT_Patches")
        self.ArtBT_Patches.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/articles/3769")))
        # Button - Website Buffout 4
        self.WebBT_Buffout4 = QtWidgets.QPushButton(CLAS_MainWin)
        self.WebBT_Buffout4.setGeometry(QtCore.QRect(40, 420, 150, 30))
        self.WebBT_Buffout4.setObjectName("WebBT_Buffout4")
        self.WebBT_Buffout4.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/47359")))
        # Button - Website CLAS Nexus
        self.WebBT_CLAS_Nexus = QtWidgets.QPushButton(CLAS_MainWin)
        self.WebBT_CLAS_Nexus.setGeometry(QtCore.QRect(220, 420, 200, 30))
        self.WebBT_CLAS_Nexus.setObjectName("WebBT_CLAS_Nexus")
        self.WebBT_CLAS_Nexus.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255")))
        # Button - Website CLAS Github
        self.WebBT_CLAS_Git = QtWidgets.QPushButton(CLAS_MainWin)
        self.WebBT_CLAS_Git.setGeometry(QtCore.QRect(450, 420, 150, 30))
        self.WebBT_CLAS_Git.setObjectName("WebBT_CLAS_Git")
        self.WebBT_CLAS_Git.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/GuidanceOfGrace/Buffout4-CLAS/releases")))
        
        # BOTTOM
        
        # Button - HELP
        self.RegBT_Help = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Help.setGeometry(QtCore.QRect(20, 480, 110, 24))
        self.RegBT_Help.setObjectName("RegBT_Help")
        self.RegBT_Help.clicked.connect(self.Help_Popup)
        # Button - EXIT
        self.RegBT_Exit = QtWidgets.QPushButton(CLAS_MainWin)
        self.RegBT_Exit.setGeometry(QtCore.QRect(510, 480, 110, 24))
        self.RegBT_Exit.setObjectName("RegBT_Exit")
        self.RegBT_Exit.clicked.connect(CLAS_MainWin.close)
        
        # TEXT Box - Window
        self.TXT_Window = QtWidgets.QTextBrowser(CLAS_MainWin)
        self.TXT_Window.setGeometry(QtCore.QRect(20, 510, 600, 120))
        self.TXT_Window.setObjectName("TXT_Window")
        # TEXT Label - About
        self.TXT_About = QtWidgets.QLabel(CLAS_MainWin)
        self.TXT_About.setGeometry(QtCore.QRect(30, 520, 300, 16))
        self.TXT_About.setInputMethodHints(QtCore.Qt.ImhHiddenText) # type: ignore
        self.TXT_About.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop) # type: ignore
        self.TXT_About.setObjectName("TXT_About")
        # TEXT Label - Contributors
        self.TXT_Contributors = QtWidgets.QLabel(CLAS_MainWin)
        self.TXT_Contributors.setGeometry(QtCore.QRect(30, 540, 340, 16))
        self.TXT_Contributors.setObjectName("TXT_Contributors")

        self.retranslateUi(CLAS_MainWin)
        QtCore.QMetaObject.connectSlotsByName(CLAS_MainWin)

        # ================= MAIN BUTTON FUNCTIONS ===================
    def CrashLogs_SCAN(self):
        Scan_Crashlogs.scan_logs()

    def SelectFolder_SCAN(self):
        SCAN_folder = QFileDialog.getExistingDirectory()
        if SCAN_folder:
            self.Line_SelectedFolder.setText(SCAN_folder)
            write_ini_value_to_file("Scan Path", SCAN_folder)
            # Change text color back to black.
            LSF_palette = self.Line_SelectedFolder.palette()
            LSF_palette.setColor(QPalette.Text, QColor(Qt.black)) # type: ignore
            self.Line_SelectedFolder.setPalette(LSF_palette)

    def SelectFolder_INI(self):
        INI_folder = QFileDialog.getExistingDirectory() #QFileDialog.getOpenFileName(filter="*.ini")
        if INI_folder:
            QtWidgets.QMessageBox.information(CLAS_MainWin, "New INI Path Set", "You set the new path to: \n" + INI_folder) # type: ignore
            write_ini_value_to_file("INI Path", INI_folder)
        
        # ================== POP-UPS / WARNINGS =====================
        
    def Help_Popup(self):
        QtWidgets.QMessageBox.information(CLAS_MainWin, "Need Help?", "If you have trouble running this program or wish to submit your crash logs for additional help from our support team, join the Collective Modding Discord server. Press OK to open the server in your browser. \n")
        QDesktopServices.openUrl(QUrl("https://discord.com/invite/7ZZbrsGQh4"))
        
    def Update_Popup(self):
        if Scan_Crashlogs.run_update():
            QtWidgets.QMessageBox.information(CLAS_MainWin, "CLAS Update", "You have the latest version of Crash Log Auto Scanner!")
        else:
            QtWidgets.QMessageBox.warning(CLAS_MainWin, "CLAS Update", "New Crash Log Auto Scanner version detected!\nPress OK to open the CLAS Nexus Page.")
            QDesktopServices.openUrl(QUrl("https://www.nexusmods.com/fallout4/mods/56255?tab=files"))

        # ====================== CHECK BOXES ========================

    def Bool_IMIMode(self):
        if self.ChkBT_IMIMode.isChecked():
            write_ini_value_to_file("IMI Mode", "true")
        else:
            write_ini_value_to_file("IMI Mode", "false")

    def Bool_INIStats(self):
        if self.ChkBT_Stats.isChecked():
            write_ini_value_to_file("Stat Logging", "true")
        else:
            write_ini_value_to_file("Stat Logging", "false")

    def Bool_INIUnsolved(self):
        if self.ChkBT_Unsolved.isChecked():
            write_ini_value_to_file("Move Unsolved", "true")
        else:
            write_ini_value_to_file("Move Unsolved", "false")

    def Bool_INIUpdate(self):
        if self.ChkBT_Update.isChecked():
            write_ini_value_to_file("Update Check", "true")
        else:
            write_ini_value_to_file("Update Check", "false")

    def Bool_FCXMode(self):
        if self.ChkBT_FCXMode.isChecked():
            write_ini_value_to_file("FCX Mode", "true")
        else:
            write_ini_value_to_file("FCX Mode", "false")
            
        # ======================== METADATA =========================

    def retranslateUi(self, CLAS_MainWin):
        _translate = QtCore.QCoreApplication.translate
        CLAS_MainWin.setWindowTitle(_translate("CLAS_MainWin", "Crash Log Auto Scanner GUI 6.06"))
        self.ArtBT_Bufout4.setText(_translate("CLAS_MainWin", "BUFFOUT 4 INSTALLATION"))
        self.ArtBT_Patches.setText(_translate("CLAS_MainWin", "IMPORTANT PATCHES LIST"))
        self.ArtBT_Trblshoot.setText(_translate("CLAS_MainWin", "ADVANCED TROUBLESHOOTING"))
        self.ChkBT_FCXMode.setText(_translate("CLAS_MainWin", "FCX MODE"))
        self.ChkBT_FCXMode.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>Enable if you want Auto-Scanner to check if Buffout 4 and its requirements are installed correctly.</p></body></html>"))
        self.ChkBT_IMIMode.setText(_translate("CLAS_MainWin", "IGNORE ALL\nMANUAL FILE\nINSTALLATION\nWARNINGS"))
        self.ChkBT_IMIMode.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>Enable if you want Auto-Scanner to hide all manual installation warnings. I still highly recommend that you install all Buffout 4 files and requirements manually, WITHOUT a mod manager. </p></body></html>"))
        self.ChkBT_Stats.setText(_translate("CLAS_MainWin", "STAT LOGGING"))
        self.ChkBT_Stats.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>Enable if you want Auto-Scanner to show extra stats about scanned logs in the command line window. </p></body></html>"))
        self.ChkBT_Unsolved.setText(_translate("CLAS_MainWin", "MOVE UNSOLVED"))
        self.ChkBT_Unsolved.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>Enable if you want Auto-Scanner to move all unsolved logs and their autoscans to CL-UNSOLVED folder. (Unsolved logs are all crash logs where Auto-Scanner didn\'t detect any known crash errors or messages.)</p></body></html>"))
        self.ChkBT_Update.setText(_translate("CLAS_MainWin", "UPDATE CHECK"))
        self.ChkBT_Update.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>Enable if you want Auto-Scanner to check your Python version and if all required packages are installed. </p></body></html>"))
        self.LBL_ArtWeb.setText(_translate("CLAS_MainWin", "ARTICLES / WEBSITES"))
        self.LBL_Settings.setText(_translate("CLAS_MainWin", "SETTINGS"))
        self.RegBT_Browse.setText(_translate("CLAS_MainWin", "Browse Folder..."))
        self.RegBT_ChangeINI.setText(_translate("CLAS_MainWin", "CHANGE INI PATH"))
        self.RegBT_ChangeINI.setToolTip(_translate("CLAS_MainWin", "Select the folder where your Fallout4.ini is located so the Auto-Scanner can use that new folder location."))
        self.RegBT_CheckUpdates.setText(_translate("CLAS_MainWin", "CHECK FOR UPDATES"))
        self.RegBT_Exit.setText(_translate("CLAS_MainWin", "EXIT"))
        self.RegBT_Exit.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>Exit CLAS GUI</p></body></html>"))
        self.RegBT_Help.setText(_translate("CLAS_MainWin", "HELP"))
        self.RegBT_Help.setToolTip(_translate("CLAS_MainWin", "<html><head/><body><p>How To Use CLAS GUI</p></body></html>"))
        self.RegBT_SCAN.setText(_translate("CLAS_MainWin", "SCAN LOGS"))
        self.TXT_About.setText(_translate("CLAS_MainWin", "Crash Log Auto Scanner (CLAS) | Made by: Poet #9800"))
        self.TXT_Contributors.setText(_translate("CLAS_MainWin", "Contributors: evildarkarchon | kittivelae | AtomicFallout757"))
        self.WebBT_Buffout4.setText(_translate("CLAS_MainWin", "BUFFOUT 4 NEXUS PAGE"))
        self.WebBT_CLAS_Git.setText(_translate("CLAS_MainWin", "AUTO SCANNER GITHUB"))
        self.WebBT_CLAS_Nexus.setText(_translate("CLAS_MainWin", "AUTO SCANNER NEXUS PAGE"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CLAS_MainWin = QtWidgets.QDialog()
    ui = Ui_CLAS_MainWin()
    ui.setupUi(CLAS_MainWin)
    CLAS_MainWin.show()
    sys.exit(app.exec_())
