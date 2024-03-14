# main/subwindows/savegamemanager.py

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QWidget, QMainWindow
from subwindows.ui import savegamemanagerui

class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = savegamemanagerui.UI()
        self.windowstack: list = []

        self.render()
    
    def render(self) -> None:
        self.ui.initUI(self)

        for gamewidget in self.ui.gamewidgets:
            gamewidget.installEventFilter(self)
        self.ui.back_button.clicked.connect(self.parent.previousSubwindow)
        self.ui.sort_combo.currentIndexChanged.connect(self.refreshGames)
        self.ui.filter_combo.currentIndexChanged.connect(self.refreshGames)

    def refresh(self, data) -> None:
        self.parent.setFixedSize(900, 600)
        self.parent.setWindowTitle('Save game manager')

    def refreshGames(self) -> None:
        'Refreshes the list of game widgets according to the new filter and sort choices.'
        sort_index = self.ui.sort_combo.currentIndex()
        filter_index = self.ui.filter_combo.currentIndex()
        # Handle Sorts
        if sort_index == 0:
            ids = self.sortByID(True)
        elif sort_index == 1:
            ids = self.sortByID(False)
        elif sort_index == 2:
            ids = self.sortByDate(True)
        elif sort_index == 3:
            ids = self.sortByDate(False)
        ids = self.sortSaved(ids) # Auto-sort saved to top
        # Handle Filters
        if filter_index == 0:
            pass
        elif filter_index == 1:
            ids = self.filterSaved(ids)
        elif filter_index == 2:
            ids = self.filterCompleted(ids)
        elif filter_index == 3:
            ids = self.filterCompleted(ids, False)
        elif filter_index == 4:
            ids = self.filterTwoPlayer(ids)
        elif filter_index == 5:
            ids = self.filterEngine(ids)
        self.ui.refreshList(self, ids)
        for gamewidget in self.ui.gamewidgets:
            gamewidget.installEventFilter(self)

    # Sorting algorithms
    def sortSaved(self, ids) -> list[int]:
        new = []
        temp = []
        # Add saved to top
        for id in ids:
            self.parent.loadANIIL(id)
            data = self.parent.getANIILData()
            if data[7] == 'True':
                new.append(id)
            else:
                temp.append(id)
        # Add rest
        for id in temp:
            new.append(id)
        return new
    def sortByID(self, increasing: bool) -> list[int]:
        'Sorts games by their ID in either increasing or decreasing order.'
        original: list[int] = self.parent.getAllIDS()
        if increasing:
            return original
        else:
            return list(reversed(original))   
    def insertionSort(self, array, index) -> None:
        for step in range(1, len(array)):
            key = array[step][index]
            key_arr = array[step].copy()
            j = step - 1
            
            while j >= 0 and key < array[j][index]:
                if index == 2:
                    array[j + 1] = array[j].copy()
                    j = j - 1
                elif index == 1 and (key_arr[2] == array[j][2]):
                    array[j + 1] = array[j].copy()
                    j = j - 1
                elif index == 0 and (key_arr[1] == array[j][1]) and (key_arr[2] == array[j][2]):
                    array[j + 1] = array[j].copy()
                    j = j - 1
                else:
                    break
            array[j + 1] = key_arr
    def sortByDate(self, increasing: bool) -> list[int]:
        'Sorts games by their date in either increasing or decreasing order.'
        original: list[int] = self.parent.getAllIDS()
        dates = []
        # Get list of dates
        for id in original:
            self.parent.loadANIIL(id)
            date: str = self.parent.getANIILData()[2]
            date = date.split('.')
            date = [int(x) for x in date] #list[str] -> list[int]
            date.append(id)
            dates.append(date)

        self.insertionSort(dates, 2) # Sort years
        self.insertionSort(dates, 1) # Sort months
        self.insertionSort(dates, 0) # Sort days

        # Set IDs to correct positions
        new = []
        for date in dates:
            new.append(date[3])

        if increasing:
            return new
        else:
            return list(reversed(new))

    # Filtering algotithms
    def filterCompleted(self, ids, completed=True) -> list[int]:
        new = []
        if completed:
            for id in ids:
                self.parent.loadANIIL(id)
                data = self.parent.getANIILData()
                if data[3] == 'True':
                    new.append(id)
        else:
            for id in ids:
                self.parent.loadANIIL(id)
                data = self.parent.getANIILData()
                if data[3] == 'False':
                    new.append(id)
        return new
    def filterTwoPlayer(self, ids) -> list[int]:
        new = []
        for id in ids:
            self.parent.loadANIIL(id)
            data = self.parent.getANIILData()
            if data[5] == '0':
                new.append(id)
        return new
    def filterEngine(self, ids) -> list[int]:
        new = []
        for id in ids:
            self.parent.loadANIIL(id)
            data = self.parent.getANIILData()
            if data[5] != '0':
                new.append(id)
        return new
    def filterSaved(self, ids) -> list[int]:
        new = []
        for id in ids:
            self.parent.loadANIIL(id)
            data = self.parent.getANIILData()
            if data[7] == 'True':
                new.append(id)
        return new

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Enter:
                if obj.objectName().isnumeric():
                    for gamewidget in self.ui.parentgamewidgets:
                        if gamewidget.gameid == obj.objectName():
                            # Execute
                            gamewidget.gamewidget.setStyleSheet(u".QWidget {\n"
    "	background-color: #2C2C2C;\n"
    "	border-radius: 15px;\n"
    "	border: 0.5px solid #4E4E4E;\n"
    "}")
                            gamewidget.play_button.show()
                            gamewidget.save_button.show()
                            gamewidget.delete_button.show()
            elif event.type() == QEvent.Leave:
                if obj.objectName().isnumeric():
                    for gamewidget in self.ui.parentgamewidgets:
                        if gamewidget.gameid == obj.objectName():
                            # Execute
                            gamewidget.gamewidget.setStyleSheet(u".QWidget {\n"
    "	background-color: #2C2C2C;\n"
    "	border-radius: 15px;\n"
    "}")
                            gamewidget.play_button.hide()
                            gamewidget.save_button.hide()
                            gamewidget.delete_button.hide()
        except AttributeError as e:
            print(f'<Savegamemanager> Exception raised: {e}')
        return False
    
    # Close all open windows before changing sub window
    def closeWindows(self) -> None:
        if len(self.windowstack) != 0:
            for window in self.windowstack:
                window.close()