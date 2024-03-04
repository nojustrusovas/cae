# main/subwindows/ui/savegamemanagerui.py

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QPushButton, QScrollArea, QWidget

class UI(object):
    def initUI(self, savegamemanager):
        self.parent = savegamemanager
        if not savegamemanager.objectName():
            savegamemanager.setObjectName(u"savegamemanager")
        savegamemanager.resize(900, 600)

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
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area_contents = QWidget()
        self.scroll_area_contents.setGeometry(QRect(0, 0, 859, 509))
        self.scroll_area.setWidget(self.scroll_area_contents)