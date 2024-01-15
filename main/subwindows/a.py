from PySide6.QtCore import  Qt


























































# Executes upon mouse click
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        self.click_pos = ( event.pos().x(), event.pos().y() )
        print(f'Detected left-click at {self.click_pos}.')
        tile_pos = self.findTile(self.click_pos)
        tile = self.ui.board_layout.itemAtPosition(tile_pos[1], tile_pos[0]).widget()
        print(tile.objectName())
        tile.setStyleSheet('background-color: #EAECA0')
    return True