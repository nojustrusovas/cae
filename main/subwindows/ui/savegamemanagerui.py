# main/subwindows/ui/savegamemanagerui.py

from PySide6.QtCore import QRect, QSize, QEvent, QObject
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
        self.parentgamewidgets = []
        self.games = []
        self.parent.current_widget = None

        # Buttons
        self.back_button = QPushButton(savegamemanager)
        self.back_button.setText('Back')
        self.back_button.setGeometry(QRect(10, 10, 61, 32))

        # Combos
        self.sort_label = QLabel(savegamemanager)
        self.sort_label.setText('Sort by:')
        self.sort_label.setGeometry(QRect(90, 16, 58, 16))
        self.sort_combo = QComboBox(savegamemanager)
        self.sort_combo.addItem(u'Game ID ↓')
        self.sort_combo.addItem(u'Game ID ↑')
        self.sort_combo.addItem(u'Date ↓')
        self.sort_combo.addItem(u'Date ↑')
        self.sort_combo.setGeometry(QRect(140, 10, 109, 32))

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
        self.games = savegamemanager.parent.getAllIDS()
        for i in self.games:
            savegamemanager.parent.loadANIIL(i)
            data = savegamemanager.parent.getANIILData()
            if data[3] == 'True':
                completed = 'Completed'
            else:
                completed = 'In progress'
            if data[6] == '0':
                time = 'No time'
            elif data[6] == '1':
                time = 'Classic'
            elif data[6] == '2':
                time = 'Standard'
            elif data[6] == '3':
                time = 'Rapid'
            elif data[6] == '4':
                time = 'Blitz'
            elif data[6] == '5':
                time = 'Bullet'
            if data[7] == 'True':
                saved = True
            else:
                saved = False
            gamewidget = GameWidget(self.scroll_area_contents, f'{data[1]} - {data[2]}', data[0], f'{completed}, Depth {data[5]}, {time}', self, savegamemanager, saved)
            self.vertical_layout.addWidget(gamewidget.gamewidget)
            self.gamewidgets.append(gamewidget.gamewidget)
            self.parentgamewidgets.append(gamewidget)
        self.vertical_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_area_contents)
        savegamemanager.refreshGames()
    
    def refreshList(self, savegamemanager, ids) -> None:
        # Clear layout
        for i in reversed(range(self.vertical_layout.count())): 
            self.vertical_layout.itemAt(i).widget().setParent(None)
        self.gamewidgets = []
        self.parentgamewidgets = []

        for i in ids:
            savegamemanager.parent.loadANIIL(i)
            data = savegamemanager.parent.getANIILData()
            if data[3] == 'True':
                completed = 'Completed'
            else:
                completed = 'In progress'
            if data[6] == '0':
                time = 'No time'
            elif data[6] == '1':
                time = 'Classic'
            elif data[6] == '2':
                time = 'Standard'
            elif data[6] == '3':
                time = 'Rapid'
            elif data[6] == '4':
                time = 'Blitz'
            elif data[6] == '5':
                time = 'Bullet'
            if data[7] == 'True':
                saved = True
            else:
                saved = False
            gamewidget = GameWidget(self.scroll_area_contents, f'{data[1]} - {data[2]}', data[0], f'{completed}, Depth {data[5]}, {time}', self, savegamemanager, saved)
            self.vertical_layout.addWidget(gamewidget.gamewidget)
            self.gamewidgets.append(gamewidget.gamewidget)
            self.parentgamewidgets.append(gamewidget)
        #self.scroll_area.setWidget(self.scroll_area_contents)

    def deleteAt(self, index, gameid):
        self.vertical_layout.itemAt(index).widget().setParent(None)
        self.parent.parent.loadANIIL(gameid)
        self.parent.parent.deleteANIIL()
        self.games.pop(index)
        self.gamewidgets.pop(index)
        self.parentgamewidgets.pop(index)
        self.refreshGames()
    
    def refreshGames(self):
        self.parent.refreshGames()

class GameWidget(QObject):
    def __init__(self, parent, localtime: str, gameid: int, settings: str, savegamemanagerui, savegamemanager, saved: bool):
        super().__init__()
        self.parent = savegamemanagerui
        self.savegamemanager = savegamemanager
        self.saved = saved
        self.gamewidget = QWidget(parent)
        self.gamewidget.setObjectName(str(gameid))
        self.gameid = str(gameid)
        self.gamewidget.setMinimumSize(QSize(791, 71))
        self.gamewidget.setStyleSheet(u".QWidget {\n"
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

        self.localtime_label = QLabel(self.gamewidget)
        self.localtime_label.setGeometry(QRect(20, 10, 161, 21))
        self.localtime_label.setFont(font)
        self.localtime_label.setText(localtime)

        self.gameid_label = QLabel(self.gamewidget)
        self.gameid_label.setGeometry(QRect(195, 10, 31, 21))
        self.gameid_label.setFont(font1)
        self.gameid_label.setText(f'#{str(gameid)}')
        self.gameid_label.setStyleSheet('color: #8D8D8D')

        self.settings_label = QLabel(self.gamewidget)
        self.settings_label.setGeometry(QRect(20, 40, 251, 21))
        self.settings_label.setFont(font2)
        self.settings_label.setText(settings)

        # Buttons
        self.save_button = QWidget(self.gamewidget)
        self.save_button.setObjectName(u'Save')
        self.save_button.setGeometry(QRect(653, 12, 48, 48))
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
        self.save_button.installEventFilter(self)
        self.save_icon = QSvgWidget(self.save_button)
        self.save_icon.setObjectName('iconSave')
        self.save_icon.setGeometry(QRect(8, 8, 32, 32))
        if not self.saved:
            self.save_icon.load('main/images/save.svg')
        else:
            self.save_icon.load('main/images/save-active.svg')
        self.save_icon.setToolTip('Bookmark game for easier access')
        self.save_icon.setToolTipDuration(5000)
        self.save_icon.show()

        self.delete_button = QWidget(self.gamewidget)
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
        self.delete_button.installEventFilter(self)
        self.delete_icon = QSvgWidget(self.delete_button)
        self.delete_icon.setObjectName('iconDelete')
        self.delete_icon.setGeometry(QRect(8, 8, 32, 32))
        self.delete_icon.load('main/images/delete.svg')
        self.delete_icon.setToolTip('Deletes saved game')
        self.delete_icon.setToolTipDuration(5000)
        self.delete_icon.show()

        self.play_button = QWidget(self.gamewidget)
        self.play_button.setObjectName(u'Play')
        self.play_button.setGeometry(QRect(767, 12, 48, 48))
        self.play_button.setStyleSheet(u"QWidget#Play {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 0);\n"
"	border: 0.5px solid #454545;\n"
"}\n"
"\n"
"QWidget#Play:hover {\n"
"	border-radius: 10px;\n"
"	background-color: rgba(255, 255, 255, 10);\n"
"	border: 2px solid #65D95B;\n"
"}")
        self.play_button.installEventFilter(self)
        self.play_icon = QSvgWidget(self.play_button)
        self.play_icon.setObjectName('iconPlay')
        self.play_icon.setGeometry(QRect(11, 12, 24, 24))
        self.play_icon.load('main/images/play.svg')
        self.play_icon.setToolTip('Play this selected game')
        self.play_icon.setToolTipDuration(5000)
        self.play_icon.show()

        self.play_button.hide()
        self.save_button.hide()
        self.delete_button.hide()

        # Saved icon
        self.saved_icon = QSvgWidget(self.gamewidget)
        self.saved_icon.setObjectName('iconSaved')
        self.saved_icon.setGeometry(QRect(12, 12, 16, 16))
        self.saved_icon.load('main/images/save-active.svg')
        self.saved_icon.setToolTip('Saved')
        self.saved_icon.setToolTipDuration(5000)
        self.saved_icon.hide()

        if self.saved:
            self.markAsSaved()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            if obj.objectName() == 'Save':
                self.buttonHover(1)
            elif obj.objectName() == 'Delete':
                self.buttonHover(2)
            elif obj.objectName() == 'Play':
                self.buttonHover(3)
        elif event.type() == QEvent.Leave:
            if obj.objectName() == 'Save':
                self.buttonUnHover(1)
            elif obj.objectName() == 'Delete':
                self.buttonUnHover(2)
            elif obj.objectName() == 'Play':
                self.buttonUnHover(3)
        elif event.type() == QEvent.MouseButtonPress:
            if obj.objectName() == 'Save':
                self.savegamemanager.parent.loadANIIL(self.gameid)
                if self.saved:
                    self.markAsSaved(False)
                    self.savegamemanager.parent.current_data_file.setSaved(False)
                else:
                    self.markAsSaved()
                    self.savegamemanager.parent.current_data_file.setSaved()
                self.saved = not self.saved
                if not self.saved:
                    self.save_icon.load('main/images/save-hover.svg')
                else:
                    self.save_icon.load('main/images/save-active.svg')
                self.parent.current_widget = self
                self.parent.refreshGames()
            elif obj.objectName() == 'Delete':
                target_index = self.parent.games.index(self.gameid)
                self.parent.current_widget = self
                self.parent.deleteAt(target_index, self.gameid)
            elif obj.objectName() == 'Play':
                pass
    
    def buttonHover(self, index) -> None:
        if index == 1:
            if not self.saved:
                self.save_icon.load('main/images/save-hover.svg')
            else:
                self.save_icon.load('main/images/save-active.svg')
        if index == 2:
            self.delete_icon.load('main/images/delete-hover.svg')
        if index == 3:
            self.play_icon.load('main/images/play-hover.svg')

    def buttonUnHover(self, index) -> None:
        if index == 1:
            if not self.saved:
                self.save_icon.load('main/images/save.svg')
            else:
                self.save_icon.load('main/images/save-active.svg')
        if index == 2:
            self.delete_icon.load('main/images/delete.svg')
        if index == 3:
            self.play_icon.load('main/images/play.svg')

    def markAsSaved(self, bool=True) -> None:
        if bool:
            self.localtime_label.setGeometry(QRect(32, 10, 161, 21))
            self.saved_icon.show()
        else:
            self.localtime_label.setGeometry(QRect(20, 10, 161, 21))
            self.saved_icon.hide()