# main/subwindows/ui/homepageui.py

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QPushButton


class UI(object):
    def initUI(self, homepage):
        if not homepage.objectName():
            homepage.setObjectName(u"homepage")
        homepage.resize(517, 295)

        # Title
        self.title = QLabel(homepage)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(100, 70, 331, 31))
        font = QFont()
        font.setPointSize(23)
        font.setBold(True)
        self.title.setFont(font)

        # Play button
        self.play_button = QPushButton(homepage)
        self.play_button.setObjectName(u"play_button")
        self.play_button.setGeometry(QRect(80, 170, 101, 32))
        font1 = QFont()
        font1.setBold(True)
        self.play_button.setFont(font1)

        # Practice button
        self.practice_button = QPushButton(homepage)
        self.practice_button.setObjectName(u"practice_button")
        self.practice_button.setGeometry(QRect(210, 170, 101, 32))
        font2 = QFont()
        font2.setBold(False)
        self.practice_button.setFont(font2)

        # Quit button
        self.quit_button = QPushButton(homepage)
        self.quit_button.setObjectName(u"quit_button")
        self.quit_button.setGeometry(QRect(340, 170, 101, 32))
        font3 = QFont()
        font3.setBold(False)
        font3.setItalic(False)
        font3.setUnderline(False)
        font3.setStrikeOut(False)
        self.quit_button.setFont(font3)

        self.retranslateUI(homepage)
        QMetaObject.connectSlotsByName(homepage)

    def retranslateUI(self, homepage):
        homepage.setWindowTitle(QCoreApplication.translate("homepage", u"Homepage", None))
        self.title.setText(QCoreApplication.translate("homepage", u"Chess Application and Engine", None))
        self.play_button.setText(QCoreApplication.translate("homepage", u"Play", None))
        self.practice_button.setText(QCoreApplication.translate("homepage", u"Practice", None))
        self.quit_button.setText(QCoreApplication.translate("homepage", u"Quit", None))


class PracticeWindowUI(object):
     
    def initUI(self, practicewindow):
        if not practicewindow.objectName():
            practicewindow.setObjectName(u'practicewindow')

        practicewindow.resize(284, 100)

        # Subtitle
        self.subtitle = QLabel(practicewindow)
        self.subtitle.setObjectName(u"subtitle")
        self.subtitle.setGeometry(QRect(100, 10, 91, 20))
        font = QFont()
        font.setItalic(True)
        self.subtitle.setFont(font)

        # Analysis button
        self.analysis_button = QPushButton(practicewindow)
        self.analysis_button.setObjectName(u"analysis_button")
        self.analysis_button.setGeometry(QRect(30, 40, 100, 32))
        font1 = QFont()
        font1.setBold(False)
        self.analysis_button.setFont(font1)

        # Practice button
        self.practice_button = QPushButton(practicewindow)
        self.practice_button.setObjectName(u"practice_button")
        self.practice_button.setGeometry(QRect(150, 40, 100, 32))
        self.practice_button.setFont(font1)

        self.retranslateUI(practicewindow)

        QMetaObject.connectSlotsByName(practicewindow)

    def retranslateUI(self, practicewindow):
        practicewindow.setWindowTitle(QCoreApplication.translate("practicewindow", u"Homepage", None))
        self.subtitle.setText(QCoreApplication.translate("practicewindow", u"Select mode:", None))
        self.analysis_button.setText(QCoreApplication.translate("practicewindow", u"Analysis", None))
        self.practice_button.setText(QCoreApplication.translate("practicewindow", u"Practice", None))