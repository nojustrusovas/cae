# main/subwindows/ui/newgameui.py

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QCheckBox, QComboBox , QLabel, QLineEdit,
                               QPushButton, QSpinBox, QTabWidget, QWidget)


class UI(object):
    def initUI(self, newgame):
        if not newgame.objectName():
            newgame.setObjectName(u"newgame")
        newgame.resize(463, 362)

        # Back button
        self.back_button = QPushButton(newgame)
        self.back_button.setObjectName(u"back_button")
        self.back_button.setGeometry(QRect(10, 10, 51, 32))
        font = QFont()
        font.setBold(False)
        font.setItalic(False)
        self.back_button.setFont(font)

        # Help button
        self.help_button = QPushButton(newgame)
        self.help_button.setObjectName(u"help_button")
        self.help_button.setGeometry(QRect(70, 10, 31, 32))
        font1 = QFont()
        font1.setBold(True)
        font1.setItalic(False)
        self.help_button.setFont(font1)

        # Tabs
        self.game_tabs = QTabWidget(newgame)
        self.game_tabs.setObjectName(u"game_tabs")
        self.game_tabs.setGeometry(QRect(20, 47, 421, 151))
        self.game_tabs.setTabPosition(QTabWidget.North)
        self.game_tabs.setTabShape(QTabWidget.Rounded)
        self.game_tabs.setUsesScrollButtons(False)
        self.game_tabs.setTabBarAutoHide(False)
        self.enginetab = QWidget()
        self.enginetab.setObjectName(u"enginetab")

        self.enginetype_label = QLabel(self.enginetab)
        self.enginetype_label.setObjectName(u"enginetype_label")
        self.enginetype_label.setGeometry(QRect(10, 10, 81, 31))
        self.enginetype_combo = QComboBox(self.enginetab)
        self.enginetype_combo.addItem("")
        self.enginetype_combo.setObjectName(u"enginetype_combo")
        self.enginetype_combo.setGeometry(QRect(90, 12, 103, 32))
        self.depth_label = QLabel(self.enginetab)
        self.depth_label.setObjectName(u"depth_label")
        self.depth_label.setGeometry(QRect(10, 50, 81, 31))
        self.depth_spin = QSpinBox(self.enginetab)
        self.depth_spin.setObjectName(u"depth_spin")
        self.depth_spin.setGeometry(QRect(100, 55, 42, 22))
        self.depth_spin.setMinimum(1)
        self.depth_spin.setMaximum(5)
        self.depth_sublabel = QLabel(self.enginetab)
        self.depth_sublabel.setObjectName(u"depth_sublabel")
        self.depth_sublabel.setGeometry(QRect(23, 72, 61, 21))
        self.depth_sublabel.hide()
        font2 = QFont()
        font2.setPointSize(10)
        font2.setItalic(True)
        self.depth_sublabel.setFont(font2)

        self.game_tabs.addTab(self.enginetab, "")
        self.playertab = QWidget()
        self.playertab.setObjectName(u"playertab")
        self.rotate_checkbox = QCheckBox(self.playertab)
        self.rotate_checkbox.setObjectName(u"rotate_checkbox")
        self.rotate_checkbox.setGeometry(QRect(10, 10, 161, 31))
        self.player1_name_label = QLabel(self.playertab)
        self.player1_name_label.setObjectName(u"player1_name_label")
        self.player1_name_label.setGeometry(QRect(13, 40, 91, 31))
        self.player2_name_label = QLabel(self.playertab)
        self.player2_name_label.setObjectName(u"player2_name_label")
        self.player2_name_label.setGeometry(QRect(203, 40, 91, 31))
        self.player1_name_entry = QLineEdit(self.playertab)
        self.player1_name_entry.setObjectName(u"player1_name_entry")
        self.player1_name_entry.setGeometry(QRect(10, 70, 151, 31))
        self.player1_name_entry.setMaxLength(15)
        self.player1_name_entry.setStyleSheet('QLineEdit {\n	border: 2px solid #474747;\n	border-radius: 15px;\n	color: #FFFFFF;\n	padding-left: 10px;\n	padding-right: 10px;\n	background-color: #393939;\n}')
        self.player1_name_entry.setPlaceholderText('Player 1')
        self.player2_name_entry = QLineEdit(self.playertab)
        self.player2_name_entry.setObjectName(u"player2_name_entry")
        self.player2_name_entry.setGeometry(QRect(200, 70, 151, 31))
        self.player2_name_entry.setMaxLength(15)
        self.player2_name_entry.setStyleSheet('QLineEdit {\n	border: 2px solid #474747;\n	border-radius: 15px;\n	color: #FFFFFF;\n	padding-left: 10px;\n	padding-right: 10px;\n	background-color: #393939;\n}')
        self.player2_name_entry.setPlaceholderText('Player 2')       
        self.game_tabs.addTab(self.playertab, "")

        # FEN entry
        self.fen_edit = QLineEdit(newgame)
        self.fen_edit.setObjectName(u"fen_edit")
        self.fen_edit.setGeometry(QRect(240, 239, 181, 31))
        self.fen_edit.setStyleSheet('QLineEdit {\n	border: 2px solid #474747;\n	border-radius: 15px;\n	color: #FFFFFF;\n	padding-left: 10px;\n	padding-right: 10px;\n	background-color: #393939;\n}')
        font3 = QFont()
        font3.setPointSize(10)
        self.fen_edit.setFont(font3)
        self.fen_edit.setPlaceholderText('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.fen_edit.hide()
        self.fen_checkbox = QCheckBox(newgame)
        self.fen_checkbox.setObjectName(u"fen_checkbox")
        self.fen_checkbox.setGeometry(QRect(240, 213, 101, 20))

        # Start as selection
        self.startas_label = QLabel(newgame)
        self.startas_label.setObjectName(u"startas_label")
        self.startas_label.setGeometry(QRect(30, 245, 81, 31))
        self.startas_combo = QComboBox(newgame)
        self.startas_combo.addItem("")
        self.startas_combo.addItem("")
        self.startas_combo.addItem("")
        self.startas_combo.setObjectName(u"startas_combo")
        self.startas_combo.setGeometry(QRect(90, 247, 103, 32))

        # Time format selection
        self.time_label = QLabel(newgame)
        self.time_label.setObjectName(u"time_label")
        self.time_label.setGeometry(QRect(30, 209, 81, 31))
        self.time_combo = QComboBox(newgame)
        self.time_combo.addItem("")
        self.time_combo.addItem("")
        self.time_combo.addItem("")
        self.time_combo.addItem("")
        self.time_combo.addItem("")
        self.time_combo.addItem("")
        self.time_combo.setObjectName(u"time_combo")
        self.time_combo.setGeometry(QRect(110, 210, 103, 32))

        # Newgame and loadgame button
        self.newgame_button = QPushButton(newgame)
        self.newgame_button.setObjectName(u"newgame_button")
        self.newgame_button.setGeometry(QRect(10, 320, 101, 32))
        self.newgame_button.setFont(font1)
        self.loadgame_button = QPushButton(newgame)
        self.loadgame_button.setObjectName(u"loadgame_button")
        self.loadgame_button.setGeometry(QRect(120, 320, 91, 32))

        self.retranslateUI(newgame)
        self.game_tabs.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(newgame)

    def retranslateUI(self, newgame):
        newgame.setWindowTitle(QCoreApplication.translate("newgame", u"New game configuration", None))
        self.back_button.setText(QCoreApplication.translate("newgame", u"Back", None))
        self.help_button.setText(QCoreApplication.translate("newgame", u"?", None))
        self.enginetype_label.setText(QCoreApplication.translate("newgame", u"Engine type:", None))
        self.enginetype_combo.setItemText(0, QCoreApplication.translate("newgame", u"Default", None))

        self.depth_label.setText(QCoreApplication.translate("newgame", u"Engine depth:", None))
        self.depth_sublabel.setText(QCoreApplication.translate("newgame", u"(Difficulty)", None))
        self.game_tabs.setTabText(self.game_tabs.indexOf(self.enginetab), QCoreApplication.translate("newgame", u"vs Engine", None))
        self.rotate_checkbox.setText(QCoreApplication.translate("newgame", u"Rotate board per turn", None))
        self.player1_name_label.setText(QCoreApplication.translate("newgame", u"Player 1 name:", None))
        self.player2_name_label.setText(QCoreApplication.translate("newgame", u"Player 2 name:", None))
        self.game_tabs.setTabText(self.game_tabs.indexOf(self.playertab), QCoreApplication.translate("newgame", u"vs Player", None))
        self.startas_label.setText(QCoreApplication.translate("newgame", u"Start as:", None))
        self.fen_checkbox.setText(QCoreApplication.translate("newgame", u"Custom Fen", None))
        self.time_label.setText(QCoreApplication.translate("newgame", u"Time format:", None))
        self.startas_combo.setItemText(0, QCoreApplication.translate("newgame", u"Random", None))
        self.startas_combo.setItemText(1, QCoreApplication.translate("newgame", u"White", None))
        self.startas_combo.setItemText(2, QCoreApplication.translate("newgame", u"Black", None))

        self.time_combo.setItemText(0, QCoreApplication.translate("newgame", u"None", None))
        self.time_combo.setItemText(1, QCoreApplication.translate("newgame", u"Classic", None))
        self.time_combo.setItemText(2, QCoreApplication.translate("newgame", u"Standard", None))
        self.time_combo.setItemText(3, QCoreApplication.translate("newgame", u"Rapid", None))
        self.time_combo.setItemText(4, QCoreApplication.translate("newgame", u"Blitz", None))
        self.time_combo.setItemText(5, QCoreApplication.translate("newgame", u"Bullet", None))

        self.newgame_button.setText(QCoreApplication.translate("newgame", u"New Game", None))
        self.loadgame_button.setText(QCoreApplication.translate("newgame", u"Load Game", None))

# Info window -----
        
class UI_InfoWindow(object):
    def initUI(self, newgame):
        if not newgame.objectName():
            newgame.setObjectName(u"newgame")

        # Text
        self.text = QLabel(newgame)
        self.text.setObjectName(u"text")
        self.text.setGeometry(QRect(30, 10, 271, 51))
        self.text.setWordWrap(True)
        self.text_2 = QLabel(newgame)
        self.text_2.setObjectName(u"text_2")
        self.text_2.setGeometry(QRect(95, 46, 131, 16))

        # Ok button
        self.ok_button = QPushButton(newgame)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setGeometry(QRect(110, 80, 100, 32))

        self.retranslateUI()

        QMetaObject.connectSlotsByName(newgame)

    def retranslateUI(self):
        self.text.setText(QCoreApplication.translate("newgame", u"Invalid FEN string input. Try again or continue", None))
        self.text_2.setText(QCoreApplication.translate("newgame", u"with default position?", None))
        self.ok_button.setText(QCoreApplication.translate("newgame", u"OK", None))

# Help window -----
        
class UIPage1(object):
    def initUI(self, newgamehelp):
        if not newgamehelp.objectName():
            newgamehelp.setObjectName(u"newgamehelp")
        newgamehelp.resize(400, 300)

        # Back button
        self.back_button = QPushButton(newgamehelp)
        self.back_button.setObjectName(u"back_button")
        self.back_button.setEnabled(False)
        self.back_button.setGeometry(QRect(10, 260, 61, 32))

        # Next button
        self.next_button = QPushButton(newgamehelp)
        self.next_button.setObjectName(u"next_button")
        self.next_button.setGeometry(QRect(80, 260, 61, 32))
        self.next_button.setEnabled(True)

        # Page 1 Heading
        self.heading = QLabel(newgamehelp)
        self.heading.setObjectName(u"heading")
        self.heading.setGeometry(QRect(10, 20, 201, 16))
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.heading.setFont(font)

        # Page 1 Heading description
        self.description_1 = QLabel(newgamehelp)
        self.description_1.setObjectName(u"description_1")
        self.description_1.setGeometry(QRect(10, 40, 351, 16))
        font_1 = QFont()
        font_1.setPointSize(12)
        self.description_1.setFont(font_1)

        # Page 1 Sub-heading
        self.subheading_1 = QLabel(newgamehelp)
        self.subheading_1.setObjectName(u"subheading_1")
        self.subheading_1.setGeometry(QRect(10, 72, 351, 16))
        font_2 = QFont()
        font_2.setPointSize(12)
        font_2.setBold(True)
        self.subheading_1.setFont(font_2)

        # Page 1 Sub-heading description
        self.description_2 = QLabel(newgamehelp)
        self.description_2.setObjectName(u"description_2")
        self.description_2.setGeometry(QRect(10, 89, 351, 51))
        self.description_2.setFont(font_1)
        self.description_2.setWordWrap(True)

        # Page 1 Sub-heading 2
        self.subheading_2 = QLabel(newgamehelp)
        self.subheading_2.setObjectName(u"subheading_2")
        self.subheading_2.setGeometry(QRect(10, 160, 351, 16))
        self.subheading_2.setFont(font_2)

        # Page 1 Sub-heading 2 description
        self.description_3 = QLabel(newgamehelp)
        self.description_3.setObjectName(u"description_3")
        self.description_3.setGeometry(QRect(10, 170, 351, 51))
        self.description_3.setFont(font_1)
        self.description_3.setWordWrap(True)

        # Page counter
        self.counter = QLabel(newgamehelp)
        self.counter.setObjectName(u"counter")
        self.counter.setGeometry(QRect(150, 267, 31, 16))
        font_3 = QFont()
        font_3.setPointSize(10)
        font_3.setItalic(True)
        self.counter.setFont(font_3)

        self.retranslateUI()
        QMetaObject.connectSlotsByName(newgamehelp)
    
    def retranslateUI(self):
        self.back_button.setText(QCoreApplication.translate("newgamehelp", u"Back", None))
        self.next_button.setText(QCoreApplication.translate("newgamehelp", u"Next", None))
        self.heading.setText(QCoreApplication.translate("newgamehelp", u"Opponent type and options", None))
        self.description_1.setText(QCoreApplication.translate("newgamehelp", u"Choose to play against a chess engine or a second player.", None))
        self.subheading_1.setText(QCoreApplication.translate("newgamehelp", u"Chess engine", None))
        self.description_2.setText(QCoreApplication.translate("newgamehelp", u"Select between the types of chess engines used, as well as that type's depth. Engine depth directly contributes to the engine's difficulty.", None))
        self.subheading_2.setText(QCoreApplication.translate("newgamehelp", u"Second player", None))
        self.description_3.setText(QCoreApplication.translate("newgamehelp", u"Play against a local second player, and choose whether the board flips vertically after each move.", None))
        self.counter.setText(QCoreApplication.translate("newgamehelp", u"1/3", None))

class UIPage2(object):
    def initUI(self, newgamehelp):
        if not newgamehelp.objectName():
            newgamehelp.setObjectName(u"newgamehelp")
        newgamehelp.resize(400, 300)

        # Back button
        self.back_button = QPushButton(newgamehelp)
        self.back_button.setObjectName(u"back_button")
        self.back_button.setEnabled(True)
        self.back_button.setGeometry(QRect(10, 260, 61, 32))

        # Next button
        self.next_button = QPushButton(newgamehelp)
        self.next_button.setObjectName(u"next_button")
        self.next_button.setGeometry(QRect(80, 260, 61, 32))
        self.next_button.setEnabled(True)

        # Page 2 Heading
        self.heading = QLabel(newgamehelp)
        self.heading.setObjectName(u"heading")
        self.heading.setGeometry(QRect(10, 20, 201, 16))
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.heading.setFont(font)

        # Page 2 Heading description
        self.description_1 = QLabel(newgamehelp)
        self.description_1.setObjectName(u"description_1")
        self.description_1.setGeometry(QRect(10, 40, 351, 16))
        font_1 = QFont()
        font_1.setPointSize(12)
        self.description_1.setFont(font_1)

        # Page 2 Sub-heading
        self.sub_heading = QLabel(newgamehelp)
        self.sub_heading.setObjectName(u"sub_heading")
        self.sub_heading.setGeometry(QRect(10, 72, 351, 16))
        font_2 = QFont()
        font_2.setPointSize(12)
        font_2.setBold(True)
        self.sub_heading.setFont(font_2)

        # Page 2 Sub-heading description
        self.description_2 = QLabel(newgamehelp)
        self.description_2.setObjectName(u"description_2")
        self.description_2.setGeometry(QRect(10, 80, 351, 51))
        self.description_2.setFont(font_1)
        self.description_2.setWordWrap(True)

        # Page 2 Time format descriptions
        self.description_3 = QLabel(newgamehelp)
        self.description_3.setObjectName(u"description_3")
        self.description_3.setGeometry(QRect(20, 130, 251, 21))
        self.description_3.setFont(font_1)
        self.description_3.setWordWrap(True)
        self.description_4 = QLabel(newgamehelp)
        self.description_4.setObjectName(u"description_4")
        self.description_4.setGeometry(QRect(20, 150, 271, 21))
        self.description_4.setFont(font_1)
        self.description_4.setWordWrap(True)
        self.description_5 = QLabel(newgamehelp)
        self.description_5.setObjectName(u"description_5")
        self.description_5.setGeometry(QRect(20, 170, 281, 21))
        self.description_5.setFont(font_1)
        self.description_5.setWordWrap(True)
        self.description_6 = QLabel(newgamehelp)
        self.description_6.setObjectName(u"description_6")
        self.description_6.setGeometry(QRect(20, 190, 281, 21))
        self.description_6.setFont(font_1)
        self.description_6.setWordWrap(True)

        # Page counter
        self.counter = QLabel(newgamehelp)
        self.counter.setObjectName(u"counter")
        self.counter.setGeometry(QRect(150, 267, 31, 16))
        font_3 = QFont()
        font_3.setPointSize(10)
        font_3.setItalic(True)
        self.counter.setFont(font_3)

        self.retranslateUI()
        QMetaObject.connectSlotsByName(newgamehelp)
    
    def retranslateUI(self):
        self.back_button.setText(QCoreApplication.translate("newgamehelp", u"Back", None))
        self.next_button.setText(QCoreApplication.translate("newgamehelp", u"Next", None))
        self.heading.setText(QCoreApplication.translate("newgamehelp", u"Other options", None))
        self.description_1.setText(QCoreApplication.translate("newgamehelp", u"Additional configurations to set up for the game.", None))
        self.sub_heading.setText(QCoreApplication.translate("newgamehelp", u"Time format", None))
        self.description_2.setText(QCoreApplication.translate("newgamehelp", u"The time format determines the amount of time each side has before a forfeit. Choose None to play without a time limit.", None))
        self.description_3.setText(QCoreApplication.translate("newgamehelp", u"Classic - 30 minutes a side (~1 hour game)", None))
        self.description_4.setText(QCoreApplication.translate("newgamehelp", u"Standard - 10 minutes a side (~20 minute game)", None))
        self.description_5.setText(QCoreApplication.translate("newgamehelp", u"Rapid - 5 minutes a side (~10 minute game)", None))
        self.description_6.setText(QCoreApplication.translate("newgamehelp", u"Bullet - 1 minutes a side (~2 minute game)", None))
        self.counter.setText(QCoreApplication.translate("newgamehelp", u"2/3", None))

class UIPage3(object):
    def initUI(self, newgamehelp):
        if not newgamehelp.objectName():
            newgamehelp.setObjectName(u"newgamehelp")
        newgamehelp.resize(400, 300)

        # Back button
        self.back_button = QPushButton(newgamehelp)
        self.back_button.setObjectName(u"back_button")
        self.back_button.setGeometry(QRect(10, 260, 61, 32))
        self.back_button.setEnabled(True)

        # Next button
        self.next_button = QPushButton(newgamehelp)
        self.next_button.setObjectName(u"next_button")
        self.next_button.setEnabled(False)
        self.next_button.setGeometry(QRect(80, 260, 61, 32))

        # Page 3 Sub-heading 1
        self.subheading_1 = QLabel(newgamehelp)
        self.subheading_1.setObjectName(u"subheading_1")
        self.subheading_1.setGeometry(QRect(10, 20, 351, 16))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.subheading_1.setFont(font)

        # Page 3 Sub-heading 1 description
        self.description_1 = QLabel(newgamehelp)
        self.description_1.setObjectName(u"description_1")
        self.description_1.setGeometry(QRect(10, 40, 351, 51))
        font1 = QFont()
        font1.setPointSize(12)
        self.description_1.setFont(font1)
        self.description_1.setWordWrap(True)

        # Page 3 Sub-heading 2
        self.subheading_2 = QLabel(newgamehelp)
        self.subheading_2.setObjectName(u"subheading_2")
        self.subheading_2.setGeometry(QRect(10, 120, 351, 16))
        self.subheading_2.setFont(font)

        # Page 3 Sub-heading 2 description
        self.description_2 = QLabel(newgamehelp)
        self.description_2.setObjectName(u"description_2")
        self.description_2.setGeometry(QRect(10, 140, 351, 51))
        self.description_2.setFont(font1)
        self.description_2.setWordWrap(True)

        # Page counter
        self.counter = QLabel(newgamehelp)
        self.counter.setObjectName(u"counter")
        self.counter.setGeometry(QRect(150, 267, 31, 16))
        font_3 = QFont()
        font_3.setPointSize(10)
        font_3.setItalic(True)
        self.counter.setFont(font_3)

        self.retranslateUI()
        QMetaObject.connectSlotsByName(newgamehelp)
    
    def retranslateUI(self):
        self.back_button.setText(QCoreApplication.translate("page3", u"Back", None))
        self.next_button.setText(QCoreApplication.translate("page3", u"Next", None))
        self.subheading_1.setText(QCoreApplication.translate("page3", u"Custom FEN", None))
        self.description_1.setText(QCoreApplication.translate("page3", u"Choose to play from a custom position using FEN notation. If checked, enter a valid fen string else the game will start from the default position.", None))
        self.subheading_2.setText(QCoreApplication.translate("page3", u"Start as", None))
        self.description_2.setText(QCoreApplication.translate("page3", u"When playing against the chess engine, this option will determine the player's starting colour. Else, the option will determine the colour of the starting player (player 1).", None))
        self.counter.setText(QCoreApplication.translate("newgamehelp", u"3/3", None))