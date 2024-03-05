# main/subwindows/ui/savegamemanagerui.py

from PySide6.QtCore import QRect, QSize
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QPushButton, QScrollArea, QWidget, QVBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget

class UI(object):
    def initUI(self, savegamemanager):
        self.parent = savegamemanager
        if not savegamemanager.objectName():
            savegamemanager.setObjectName(u"savegamemanager")
        savegamemanager.resize(900, 600)
        self.gamewidgets = []

        # Buttons
        self.back_button = QPushButton(savegamemanager)
        self.back_button.setText('Back')
        self.back_button.setGeometry(QRect(10, 10, 61, 32))

        # Combos
        self.sort_label = QLabel(savegamemanager)
        self.sort_label.setText('Sort by:')
        self.sort_label.setGeometry(QRect(90, 16, 58, 16))
        self.sort_combo = QComboBox(savegamemanager)
        self.sort_combo.addItem('Game ID')
        self.sort_combo.addItem('Date')
        self.sort_combo.setGeometry(QRect(140, 10, 103, 32))

        self.filter_label = QLabel(savegamemanager)
        self.filter_label.setText('Filter by:')
        self.filter_label.setGeometry(QRect(260, 16, 58, 16))
        self.filter_combo = QComboBox(savegamemanager)
        self.filter_combo.addItem('None')
        self.filter_combo.addItem('Saved only')
        self.filter_combo.addItem('Completed')
        self.filter_combo.addItem('Uncompleted')
        self.filter_combo.addItem('Two player')
        self.filter_combo.addItem('Engine')
        self.filter_combo.addItem('Not recent')
        self.filter_combo.setGeometry(QRect(314, 10, 131, 32))

        # Divider
        self.divider = QFrame(savegamemanager)
        self.divider.setGeometry(QRect(10, 46, 871, 16))
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)

        # Scroll area
        self.scroll_area = QScrollArea(savegamemanager)
        self.scroll_area.setGeometry(QRect(20, 70, 861, 511))
        self.scroll_area.setMinimumSize(QSize(861, 511))
        self.scroll_area.setMaximumSize(QSize(861, 511))
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_contents = QWidget()
        self.scroll_area_contents.setGeometry(QRect(0, 0, 859, 509))
        self.vertical_layout = QVBoxLayout(self.scroll_area_contents)
        games = savegamemanager.parent.getAllGames()
        num_games = len(games) + 8
        for i in range(num_games):
            gamewidget = self.GameWidget(self.scroll_area_contents, '17/08/23 - 20:30', i+1, 'Completed, Depth 5, No time')
            self.vertical_layout.addWidget(gamewidget)
        self.vertical_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_area_contents)

    def GameWidget(self, parent, localtime: str, gameid: int, settings: str) -> QWidget:
        gamewidget = QWidget(parent)
        gamewidget.setObjectName('GameWidget')
        gamewidget.setMinimumSize(QSize(791, 71))
        gamewidget.setStyleSheet(u"QWidget#GameWidget {\n"
"	background-color: #2C2C2C;\n"
"	border-radius: 15px;\n"
"}")
        
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(False)
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(False)

        # Labels

        self.localtime_label = QLabel(gamewidget)
        self.localtime_label.setGeometry(QRect(20, 10, 131, 21))
        self.localtime_label.setFont(font)
        self.localtime_label.setText(localtime)

        self.gameid_label = QLabel(gamewidget)
        self.gameid_label.setGeometry(QRect(160, 10, 31, 21))
        self.gameid_label.setFont(font1)
        self.gameid_label.setText(f'#{str(gameid)}')
        self.gameid_label.setStyleSheet('color: #8D8D8D')

        self.settings_label = QLabel(gamewidget)
        self.settings_label.setGeometry(QRect(20, 40, 251, 21))
        self.settings_label.setFont(font2)
        self.settings_label.setText(settings)

        # Buttons
        self.save_button = QWidget(gamewidget)
        self.save_button.setObjectName(u'Save')
        self.save_button.setGeometry(QRect(767, 12, 48, 48))
        self.save_button.setStyleSheet(u"QWidget#Save {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0.5px solid #454545;\n"
"}\n"
"\n"
"QWidget#Save:hover {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 10);\n"
"	border: 1px solid #FFFFFF;\n"
"}")
        self.save_icon = QSvgWidget(self.save_button)
        self.save_icon.setObjectName('iconSave')
        self.save_icon.setGeometry(QRect(8, 8, 32, 32))
        self.save_icon.load('main/images/save.svg')
        self.save_icon.setToolTip('Bookmark game for easier access.')
        self.save_icon.setToolTipDuration(5000)
        self.save_icon.show()

        self.delete_button = QWidget(gamewidget)
        self.delete_button.setObjectName(u'Delete')
        self.delete_button.setGeometry(QRect(710, 12, 48, 48))
        self.delete_button.setStyleSheet(u"QWidget#Delete {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0.5px solid #454545;\n"
"}\n"
"\n"
"QWidget#Delete:hover {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 10);\n"
"	border: 1px solid #FFFFFF;\n"
"}")
        self.save_icon = QSvgWidget(self.delete_button)
        self.save_icon.setObjectName('iconDelete')
        self.save_icon.setGeometry(QRect(8, 8, 32, 32))
        self.save_icon.load('main/images/delete.svg')
        self.save_icon.setToolTip('Deletes saved game.')
        self.save_icon.setToolTipDuration(5000)
        self.save_icon.show()

        self.gamewidgets.append(gamewidget)
        return gamewidget
