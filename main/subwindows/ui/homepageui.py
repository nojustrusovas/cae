# main/subwindows/ui/homepageui.py

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtSvgWidgets import QSvgWidget


class UI(object):
    def initUI(self, homepage):
        if not homepage.objectName():
            homepage.setObjectName(u"homepage")
        homepage.resize(517, 295)

        # Title
        self.title = QSvgWidget(homepage)
        self.title.setGeometry(QRect(156, 40, 209, 96))
        self.title.load('main/images/title.svg')
        self.title.show()

        # Play button
        self.play_button = QWidget(homepage)
        self.play_button.setObjectName(u'Play')
        self.play_button.setGeometry(QRect(60, 170, 121, 31))
        self.play_button.setStyleSheet(u"QWidget {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0.5px solid #454545;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 10);\n"
"	border: 1px solid #FFFFFF;\n"
"}")
        self.play_label = QLabel(self.play_button)
        self.play_label.setText('PLAY')
        self.play_label.setGeometry(QRect(45, 8, 41, 16))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.play_label.setFont(font)
        self.play_label.setStyleSheet(u"QLabel {\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0px solid #FFFFFF;\n"
"}")

        # Practice button
        self.practice_button = QWidget(homepage)
        self.practice_button.setObjectName(u'Practice')
        self.practice_button.setGeometry(QRect(200, 170, 121, 31))
        self.practice_button.setStyleSheet(u"QWidget {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0.5px solid #454545;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 10);\n"
"	border: 1px solid #FFFFFF;\n"
"}")
        self.practice_label = QLabel(self.practice_button)
        self.practice_label.setText('PRACTICE')
        self.practice_label.setGeometry(QRect(33, 8, 61, 16))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.practice_label.setFont(font1)
        self.practice_label.setStyleSheet(u"QLabel {\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0px solid #FFFFFF;\n"
"}")
        # self.practice_button = QPushButton(homepage)
        # self.practice_button.setObjectName(u"practice_button")
        # self.practice_button.setGeometry(QRect(210, 170, 101, 32))
        # font2 = QFont()
        # font2.setBold(False)
        # self.practice_button.setFont(font2)

        # Quit button
        self.quit_button = QWidget(homepage)
        self.quit_button.setObjectName(u'Quit')
        self.quit_button.setGeometry(QRect(340, 170, 121, 31))
        self.quit_button.setStyleSheet(u"QWidget {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0.5px solid #454545;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 10);\n"
"	border: 1px solid #FFFFFF;\n"
"}")
        self.quit_label = QLabel(self.quit_button)
        self.quit_label.setText('QUIT')
        self.quit_label.setGeometry(QRect(45, 8, 61, 16))
        self.quit_label.setFont(font1)
        self.quit_label.setStyleSheet(u"QLabel {\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0px solid #FFFFFF;\n"
"}")

        self.retranslateUI(homepage)
        QMetaObject.connectSlotsByName(homepage)

    def retranslateUI(self, homepage):
        homepage.setWindowTitle(QCoreApplication.translate("homepage", u"Homepage", None))


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