# graphic.py
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit
)
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPalette

#   Simple data container
class Player:
    def __init__(self, name: str, player_class: str):
        self.name = name
        self.player_class = player_class

#   Signal bridge
class GuiBridge(QObject):
    update_table = pyqtSignal(list)
    append_text = pyqtSignal(str, str) # text, color


#   Main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TF2 Stat Tracker")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

#       Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #333333; color: #f0f0f0; gridline-color: #555555; alternate-background-color: #3c3c3c; }"
            "QHeaderView::section { background-color: #555555; color: #FFA500; font-weight: bold; }")
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Name", "Class"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

#       Output box
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFixedHeight(120)

        layout.addWidget(self.output_box)

    def update_players(self, players):
        self.table.setRowCount(len(players))
        for row, player in enumerate(players):
            self.table.setItem(row, 0, QTableWidgetItem(player.name))
            self.table.setItem(row, 1, QTableWidgetItem(player.current_class))

    def append_output(self, text: str, color: str = None):
        """Append text with optional color"""
        if color:
            colored_text = f'<span style="color:{color}">{text}</span>'
        else:
            colored_text = text
        self.output_box.append(colored_text)


#   Module state
_bridge = GuiBridge()

_window = None


#   Public API
def update_data(players):
    """Update table rows"""
    _bridge.update_table.emit(players)


def output_text(text: str, color: str = None):
    """Append text to bottom output box with optional color"""
    _bridge.append_text.emit(text, color)
dark_style = "QWidget { background-color: #2b2b2b; color: #f0f0f0; } QTableWidget { background-color: #3c3c3c; color: #f0f0f0; gridline-color: #555555; } QHeaderView::section { background-color: #444444; color: #f0f0f0; } QTextEdit { background-color: #3c3c3c; color: #f0f0f0; border: 1px solid #555555; } QPushButton { background-color: #555555; color: #f0f0f0; border: 1px solid #777777; padding: 5px; } QPushButton:hover { background-color: #666666; }"


def run():
    """Start GUI (must be called from main thread)"""
    global _window
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_style)
    _window = MainWindow()
    _window.show()

    _bridge.update_table.connect(_window.update_players)
    _bridge.append_text.connect(_window.append_output)

    sys.exit(app.exec_())
