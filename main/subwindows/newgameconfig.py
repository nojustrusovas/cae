# main/subwindows/newgameconfig.py

from PySide6.QtWidgets import QWidget, QMainWindow, QStackedWidget
from PySide6.QtGui import QCloseEvent
from subwindows.ui import newgameui


class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = newgameui.UI()
        self.windowstack: list = []
        self.helpwindow = HelpWindow(self)
        self.infowindow = InfoWindow(self)

        self.customfen = False

        self.render()

    # Render UI elements for sub window
    def render(self) -> None:
        self.ui.initUI(self)

        self.ui.back_button.clicked.connect(self.parent.previousSubwindow)
        self.ui.help_button.clicked.connect(self.openHelpWindow)
        self.ui.newgame_button.clicked.connect(self.finishConfig)
        self.ui.fen_checkbox.toggled.connect(self.stateChange)

    # Update window data
    def refresh(self) -> None:
        self.parent.setFixedSize(463, 362)
        self.parent.setWindowTitle('Game configuration')

    def stateChange(self):
        # Flip bool value
        self.customfen = not self.customfen

        if self.customfen:
            self.ui.fen_edit.show()
        else:
            self.ui.fen_edit.hide()
            self.ui.fen_edit.setText('')

    # Final validation for new game
    def finishConfig(self):
            # Check if FEN is valid
            if self.customfen:
                if self.validateFEN(self.ui.fen_edit.text()):
                    fen = self.ui.fen_edit.text()
                else:
                    self.displayInfoWindow()
                    return
            else:
                # Default FEN
                fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
            
            # Valid configurations to send as data
            gametype = self.ui.game_tabs.currentIndex()
            if gametype == 0:
                enginetype = 'default'
                enginedepth = self.ui.depth_spin.value()
                rotateboard = None
                player1_name = 'Player'
                player2_name = 'Engine'
            else:
                rotateboard = self.ui.rotate_checkbox.isChecked()
                player1_name = self.ui.player1_name_entry.text()
                if player1_name == '':
                    player1_name = 'Player 1'
                player2_name = self.ui.player2_name_entry.text()
                if player2_name == '':
                    player2_name = 'Player 2'
                enginetype = None
                enginedepth = None

            timeformat = self.ui.time_combo.currentIndex()
            defaultcolor = self.ui.startas_combo.currentIndex()

            self.configurations = (gametype, enginetype, enginedepth, rotateboard,
                                   player1_name, player2_name, timeformat, defaultcolor, fen)
            
            self.parent.setCurrentSubwindow(2)

    # Close all open windows before changing sub window
    def closeWindows(self) -> None:
        if len(self.windowstack) != 0:
            for window in self.windowstack:
                window.close()

    def openHelpWindow(self) -> None:
        self.helpwindow.show()
        self.windowstack.append(self.helpwindow)

    # Validates custom FEN string
    def validateFEN(self, fen: str) -> bool:
        fen = fen.strip()
        fen = fen.split(' ')
        fen = fen[0]

        # FEN string must contain 7 breaks '/'
        if fen.count('/') != 7:
            return False
        
        # FEN string should not have a break at the beginning or end
        if (fen[0] == '/') or (fen[-1] == '/'):
            return False
        
        # FEN string should not have repeated breaks
        try:
            fen.index('//')
        except ValueError: # ValueError if no repeated breaks are found
            pass
        else:
            return False

        # FEN string should have a piece value of 8 in each rank
        valid_chars = ['p', 'r', 'n', 'b', 'q', 'k']
        fen_segments = fen.split('/')
        for segment in fen_segments:
            segment_value = 0
            chars = list(segment)
            for char in chars:
                if char.isalpha():
                    segment_value += 1
                    # Check for valid characters
                    if char.lower() not in valid_chars:
                        return False
                    
                elif char.isnumeric():
                    segment_value += int(char)
                    # Check for valid integers
                    if (int(char) == 0) or (int(char) == 9):
                        return False
                else:
                    # Prevents non alpha-numeric characters
                    return False
            
            # Total value of a row has to equal to 8
            if segment_value != 8:
                return False
        
        # Check for a king for both sides
        if (fen.count('k') != 1) or (fen.count('K') != 1):
            return False

        return True

    def displayInfoWindow(self) -> None:
        self.infowindow.show()
        self.windowstack.append(self.infowindow)


class InfoWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = newgameui.UI_InfoWindow()

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.ui.initUI(self)
        self.setFixedSize(330, 125)
        self.setWindowTitle('Error')

        self.ui.ok_button.clicked.connect(self.closeWindow)

    def closeWindow(self) -> None:
        self.parent.windowstack.pop()
        self.close()

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)


class HelpWindow(QMainWindow):
    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent = parent
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.setWindowTitle('Help and information')
        self.setFixedSize(400, 300)

        # Page 1
        page = HelpWindowPage(self, newgameui.UIPage1())
        self.pages.addWidget(page)

         # Page 2
        page = HelpWindowPage(self, newgameui.UIPage2())
        self.pages.addWidget(page)
        
        # Page 3
        page = HelpWindowPage(self, newgameui.UIPage3())
        self.pages.addWidget(page)

        self.pages.setCurrentIndex(0)

    def previousPage(self) -> None:
        self.pages.setCurrentIndex(self.pages.currentIndex() - 1)
        self.pages.currentWidget().render()

    def nextPage(self) -> None:
        self.pages.setCurrentIndex(self.pages.currentIndex() + 1)
        self.pages.currentWidget().render()

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)

class HelpWindowPage(QWidget):
    def __init__(self, parent: QMainWindow, ui):
        super().__init__()
        self.parent = parent
        self.ui = ui

        self.render()

    # Render UI elements for the page
    def render(self) -> None:
        self.ui.initUI(self)

        self.ui.back_button.clicked.connect(self.parent.previousPage)
        self.ui.next_button.clicked.connect(self.parent.nextPage)