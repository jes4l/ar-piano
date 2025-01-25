from PyQt5 import QtCore, QtWidgets
import sys
import pygame


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(645, 245)
        self.mw = MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # -------------- White Keys --------------
        self.c4 = QtWidgets.QPushButton(self.centralwidget)
        self.c4.setGeometry(QtCore.QRect(20, 30, 41, 181))
        self.c4.setStyleSheet("#c4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#c4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.c4.setText("")
        self.c4.setObjectName("c4")

        self.d4 = QtWidgets.QPushButton(self.centralwidget)
        self.d4.setGeometry(QtCore.QRect(60, 30, 41, 181))
        self.d4.setStyleSheet("#d4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#d4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.d4.setText("")
        self.d4.setObjectName("d4")

        self.e4 = QtWidgets.QPushButton(self.centralwidget)
        self.e4.setGeometry(QtCore.QRect(100, 30, 41, 181))
        self.e4.setStyleSheet("#e4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#e4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.e4.setText("")
        self.e4.setObjectName("e4")

        self.f4 = QtWidgets.QPushButton(self.centralwidget)
        self.f4.setGeometry(QtCore.QRect(140, 30, 41, 181))
        self.f4.setStyleSheet("#f4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#f4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.f4.setText("")
        self.f4.setObjectName("f4")

        self.g4 = QtWidgets.QPushButton(self.centralwidget)
        self.g4.setGeometry(QtCore.QRect(180, 30, 41, 181))
        self.g4.setStyleSheet("#g4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#g4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.g4.setText("")
        self.g4.setObjectName("g4")

        self.a4 = QtWidgets.QPushButton(self.centralwidget)
        self.a4.setGeometry(QtCore.QRect(220, 30, 41, 181))
        self.a4.setStyleSheet("#a4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#a4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.a4.setText("")
        self.a4.setObjectName("a4")

        self.b4 = QtWidgets.QPushButton(self.centralwidget)
        self.b4.setGeometry(QtCore.QRect(260, 30, 41, 181))
        self.b4.setStyleSheet("#b4{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#b4:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.b4.setText("")
        self.b4.setObjectName("b4")

        self.c5 = QtWidgets.QPushButton(self.centralwidget)
        self.c5.setGeometry(QtCore.QRect(300, 30, 41, 181))
        self.c5.setStyleSheet("#c5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#c5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.c5.setText("")
        self.c5.setObjectName("c5")

        self.d5 = QtWidgets.QPushButton(self.centralwidget)
        self.d5.setGeometry(QtCore.QRect(340, 30, 41, 181))
        self.d5.setStyleSheet("#d5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#d5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.d5.setText("")
        self.d5.setObjectName("d5")

        self.e5 = QtWidgets.QPushButton(self.centralwidget)
        self.e5.setGeometry(QtCore.QRect(380, 30, 41, 181))
        self.e5.setStyleSheet("#e5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#e5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.e5.setText("")
        self.e5.setObjectName("e5")

        self.f5 = QtWidgets.QPushButton(self.centralwidget)
        self.f5.setGeometry(QtCore.QRect(420, 30, 41, 181))
        self.f5.setStyleSheet("#f5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#f5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.f5.setText("")
        self.f5.setObjectName("f5")

        self.g5 = QtWidgets.QPushButton(self.centralwidget)
        self.g5.setGeometry(QtCore.QRect(460, 30, 41, 181))
        self.g5.setStyleSheet("#g5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#g5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.g5.setText("")
        self.g5.setObjectName("g5")

        self.a5 = QtWidgets.QPushButton(self.centralwidget)
        self.a5.setGeometry(QtCore.QRect(500, 30, 41, 181))
        self.a5.setStyleSheet("#a5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#a5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.a5.setText("")
        self.a5.setObjectName("a5")

        self.b5 = QtWidgets.QPushButton(self.centralwidget)
        self.b5.setGeometry(QtCore.QRect(540, 30, 41, 181))
        self.b5.setStyleSheet("#b5{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#b5:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.b5.setText("")
        self.b5.setObjectName("b5")

        self.c6 = QtWidgets.QPushButton(self.centralwidget)
        self.c6.setGeometry(QtCore.QRect(580, 30, 41, 181))
        self.c6.setStyleSheet("#c6{\n"
                              "background-color: rgb(242, 242, 242);\n"
                              "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, "
                              "x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), "
                              "stop:1 rgba(255, 255, 255, 255));\n"
                              "}\n"
                              "#c6:pressed{\n"
                              "background-color: rgb(250, 250, 250);\n"
                              "}")
        self.c6.setText("")
        self.c6.setObjectName("c6")

        # -------------- Black Keys --------------
        self.c40 = QtWidgets.QPushButton(self.centralwidget)
        self.c40.setGeometry(QtCore.QRect(40, 30, 31, 111))
        self.c40.setStyleSheet("#c40{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#c40:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.c40.setText("")
        self.c40.setObjectName("c40")

        self.d40 = QtWidgets.QPushButton(self.centralwidget)
        self.d40.setGeometry(QtCore.QRect(80, 30, 31, 111))
        self.d40.setStyleSheet("#d40{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#d40:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.d40.setText("")
        self.d40.setObjectName("d40")

        self.f40 = QtWidgets.QPushButton(self.centralwidget)
        self.f40.setGeometry(QtCore.QRect(160, 30, 31, 111))
        self.f40.setStyleSheet("#f40{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#f40:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.f40.setText("")
        self.f40.setObjectName("f40")

        self.g40 = QtWidgets.QPushButton(self.centralwidget)
        self.g40.setGeometry(QtCore.QRect(200, 30, 31, 111))
        self.g40.setStyleSheet("#g40{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#g40:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.g40.setText("")
        self.g40.setObjectName("g40")

        self.a40 = QtWidgets.QPushButton(self.centralwidget)
        self.a40.setGeometry(QtCore.QRect(240, 30, 31, 111))
        self.a40.setStyleSheet("#a40{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#a40:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.a40.setText("")
        self.a40.setObjectName("a40")

        self.c50 = QtWidgets.QPushButton(self.centralwidget)
        self.c50.setGeometry(QtCore.QRect(320, 30, 31, 111))
        self.c50.setStyleSheet("#c50{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#c50:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.c50.setText("")
        self.c50.setObjectName("c50")

        self.d50 = QtWidgets.QPushButton(self.centralwidget)
        self.d50.setGeometry(QtCore.QRect(360, 30, 31, 111))
        self.d50.setStyleSheet("#d50{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#d50:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.d50.setText("")
        self.d50.setObjectName("d50")

        self.f50 = QtWidgets.QPushButton(self.centralwidget)
        self.f50.setGeometry(QtCore.QRect(440, 30, 31, 111))
        self.f50.setStyleSheet("#f50{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#f50:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.f50.setText("")
        self.f50.setObjectName("f50")

        self.g50 = QtWidgets.QPushButton(self.centralwidget)
        self.g50.setGeometry(QtCore.QRect(480, 30, 31, 111))
        self.g50.setStyleSheet("#g50{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#g50:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.g50.setText("")
        self.g50.setObjectName("g50")

        self.a50 = QtWidgets.QPushButton(self.centralwidget)
        self.a50.setGeometry(QtCore.QRect(520, 30, 31, 111))
        self.a50.setStyleSheet("#a50{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, "
                               "x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), "
                               "stop:1 rgba(255, 255, 255, 255));\n"
                               "}\n"
                               "#a50:pressed{\n"
                               "background-color: rgb(0, 0, 0);\n"
                               "}")
        self.a50.setText("")
        self.a50.setObjectName("a50")

        # Ensure stacking order is correct for black/white keys
        self.c4.raise_()
        self.d4.raise_()
        self.c40.raise_()
        self.e4.raise_()
        self.f4.raise_()
        self.d40.raise_()
        self.g4.raise_()
        self.a4.raise_()
        self.b4.raise_()
        self.c5.raise_()
        self.d5.raise_()
        self.a5.raise_()
        self.e5.raise_()
        self.g5.raise_()
        self.f5.raise_()
        self.b5.raise_()
        self.c6.raise_()
        self.f40.raise_()
        self.g40.raise_()
        self.a40.raise_()
        self.c50.raise_()
        self.d50.raise_()
        self.f50.raise_()
        self.g50.raise_()
        self.a50.raise_()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Dictionary to hold noteName -> pygame.mixer.Sound
        self.sounds = {}

        # Connect all keys to the same handler
        self.c4.clicked.connect(self.play_sound)
        self.d4.clicked.connect(self.play_sound)
        self.e4.clicked.connect(self.play_sound)
        self.f4.clicked.connect(self.play_sound)
        self.g4.clicked.connect(self.play_sound)
        self.a4.clicked.connect(self.play_sound)
        self.b4.clicked.connect(self.play_sound)
        self.c5.clicked.connect(self.play_sound)
        self.d5.clicked.connect(self.play_sound)
        self.e5.clicked.connect(self.play_sound)
        self.f5.clicked.connect(self.play_sound)
        self.g5.clicked.connect(self.play_sound)
        self.a5.clicked.connect(self.play_sound)
        self.b5.clicked.connect(self.play_sound)
        self.c6.clicked.connect(self.play_sound)

        self.c40.clicked.connect(self.play_sound)
        self.d40.clicked.connect(self.play_sound)
        self.f40.clicked.connect(self.play_sound)
        self.g40.clicked.connect(self.play_sound)
        self.a40.clicked.connect(self.play_sound)
        self.c50.clicked.connect(self.play_sound)
        self.d50.clicked.connect(self.play_sound)
        self.f50.clicked.connect(self.play_sound)
        self.g50.clicked.connect(self.play_sound)
        self.a50.clicked.connect(self.play_sound)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Piano"))

        # Optional keyboard shortcuts:
        self.c4.setShortcut(_translate("MainWindow", "q"))
        self.c40.setShortcut(_translate("MainWindow", "2"))
        self.d4.setShortcut(_translate("MainWindow", "w"))
        self.d40.setShortcut(_translate("MainWindow", "3"))
        self.e4.setShortcut(_translate("MainWindow", "e"))
        self.f4.setShortcut(_translate("MainWindow", "r"))
        self.f40.setShortcut(_translate("MainWindow", "5"))
        self.g4.setShortcut(_translate("MainWindow", "t"))
        self.g40.setShortcut(_translate("MainWindow", "6"))
        self.a4.setShortcut(_translate("MainWindow", "y"))
        self.a40.setShortcut(_translate("MainWindow", "7"))
        self.b4.setShortcut(_translate("MainWindow", "u"))
        self.c5.setShortcut(_translate("MainWindow", "c"))
        self.d5.setShortcut(_translate("MainWindow", "v"))
        self.e5.setShortcut(_translate("MainWindow", "b"))
        self.f5.setShortcut(_translate("MainWindow", "n"))
        self.g5.setShortcut(_translate("MainWindow", "m"))
        self.a5.setShortcut(_translate("MainWindow", ","))
        self.b5.setShortcut(_translate("MainWindow", "."))
        self.c6.setShortcut(_translate("MainWindow", "/"))
        self.c50.setShortcut(_translate("MainWindow", "f"))
        self.d50.setShortcut(_translate("MainWindow", "g"))
        self.f50.setShortcut(_translate("MainWindow", "j"))
        self.g50.setShortcut(_translate("MainWindow", "k"))
        self.a50.setShortcut(_translate("MainWindow", "l"))

    def load_sounds(self):
        """
        Load each note as a pygame.mixer.Sound object.
        Each button's objectName() must match these filenames.
        """
        base_path = "C:/Users/LLR User/Desktop/music/Sounds/"  # Adjust if needed

        # White keys
        self.sounds["c4"] = pygame.mixer.Sound(base_path + "c4.wav")
        self.sounds["d4"] = pygame.mixer.Sound(base_path + "d4.wav")
        self.sounds["e4"] = pygame.mixer.Sound(base_path + "e4.wav")
        self.sounds["f4"] = pygame.mixer.Sound(base_path + "f4.wav")
        self.sounds["g4"] = pygame.mixer.Sound(base_path + "g4.wav")
        self.sounds["a4"] = pygame.mixer.Sound(base_path + "a4.wav")
        self.sounds["b4"] = pygame.mixer.Sound(base_path + "b4.wav")
        self.sounds["c5"] = pygame.mixer.Sound(base_path + "c5.wav")
        self.sounds["d5"] = pygame.mixer.Sound(base_path + "d5.wav")
        self.sounds["e5"] = pygame.mixer.Sound(base_path + "e5.wav")
        self.sounds["f5"] = pygame.mixer.Sound(base_path + "f5.wav")
        self.sounds["g5"] = pygame.mixer.Sound(base_path + "g5.wav")
        self.sounds["a5"] = pygame.mixer.Sound(base_path + "a5.wav")
        self.sounds["b5"] = pygame.mixer.Sound(base_path + "b5.wav")
        self.sounds["c6"] = pygame.mixer.Sound(base_path + "c6.wav")

        # Black keys
        self.sounds["c40"] = pygame.mixer.Sound(base_path + "c40.wav")
        self.sounds["d40"] = pygame.mixer.Sound(base_path + "d40.wav")
        self.sounds["f40"] = pygame.mixer.Sound(base_path + "f40.wav")
        self.sounds["g40"] = pygame.mixer.Sound(base_path + "g40.wav")
        self.sounds["a40"] = pygame.mixer.Sound(base_path + "a40.wav")
        self.sounds["c50"] = pygame.mixer.Sound(base_path + "c50.wav")
        self.sounds["d50"] = pygame.mixer.Sound(base_path + "d50.wav")
        self.sounds["f50"] = pygame.mixer.Sound(base_path + "f50.wav")
        self.sounds["g50"] = pygame.mixer.Sound(base_path + "g50.wav")
        self.sounds["a50"] = pygame.mixer.Sound(base_path + "a50.wav")

    def play_sound(self):
        """
        Called when a note button is clicked.
        We'll figure out which button was clicked
        and play the associated sound.
        """
        note_name = self.mw.sender().objectName()  # e.g. "c4", "d4", "c40"
        if note_name in self.sounds:
            self.sounds[note_name].play()


def main():
    # 1. Initialize Pygame (including the audio mixer)
    pygame.init()
    pygame.mixer.init()

    # 2. Create the PyQt application
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    # 3. Set up the UI
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # 4. Load all the .wav files into Pygame mixer
    ui.load_sounds()

    # 5. Show the window and start the Qt event loop
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
