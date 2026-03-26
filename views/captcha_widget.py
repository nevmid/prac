import random

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QMouseEvent, QIcon
import os

class DraggableImage(QPushButton):
    def __init__(self, pixmap, original_pos, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())
        self.setFixedSize(pixmap.size())
        self.original_pos = original_pos
        self.current_pos = original_pos
        self.drag_start_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self.drag_start_position:
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.objectName())
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    def set_position(self, pos):
        self.current_pos = pos
        self.move(pos.x(), pos.y())


class CaptchaWidget(QWidget):
    captcha_completed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tiles = []
        self.correct_positions = {}
        self.current_positions = {}

        self.setAcceptDrops(True)

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(200, 200)

        self.setStyleSheet("background-color: #f0f0f0; border: 2px solid #ccc;")

        self.load_images()

        self.shuffle_tiles()

    def load_images(self):
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')

        positions = [(0, 0), (100, 0), (0, 100), (100, 100)]

        for i in range(4):
            img_path = os.path.join(assets_dir, f"{i + 1}.png")
            pixmap = QPixmap(img_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            tile = DraggableImage(pixmap, positions[i], self)
            tile.setObjectName(f"tile_{i}")
            self.tiles.append(tile)
            self.correct_positions[tile] = positions[i]

    def shuffle_tiles(self):
        rand_positions = list(self.correct_positions.values())
        random.shuffle(rand_positions)

        for tile in self.tiles:
            pos = rand_positions.pop()
            tile.set_position(QtCore.QPoint(pos[0], pos[1]))
            self.current_positions[tile] = pos

    def dragEnterEvent(self, event):
        if event.source() in self.tiles:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        source = event.source()

        if source and source in self.tiles:
            target_pos = (event.pos().x() - 50, event.pos().y() - 50)

            closest_pos = min(self.correct_positions.values(),
                              key=lambda p: ((p[0] - target_pos[0]) ** 2 + (p[1] - target_pos[1]) ** 2))

            target_tile = None

            for tile, pos in self.current_positions.items():
                if pos == closest_pos:
                    target_tile = tile
                    break

            if target_tile:
                sourse_pos = self.current_positions[source]
                source.set_position(QtCore.QPoint(closest_pos[0], closest_pos[1]))
                self.current_positions[source] = closest_pos

                target_tile.set_position(QtCore.QPoint(sourse_pos[0], sourse_pos[1]))
                self.current_positions[target_tile] = sourse_pos

            self.check_complete()

    def check_complete(self):
        is_complete = True
        for tile, pos in self.current_positions.items():
            if pos != self.correct_positions[tile]:
                is_complete = False
                break

        self.captcha_completed.emit(is_complete)
        return is_complete