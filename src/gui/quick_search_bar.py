import ibrowse
from PyQt6.QtCore import QEvent, QTimer, QUrl, Qt, QRect, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtWidgets import (QLineEdit, QCompleter, QMenu, QVBoxLayout, QWidget, QWidgetAction, QComboBox, QApplication,
    QHBoxLayout, QLabel)
from src.gui.commands import COMMANDS


class QuickSearchBar(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self.setWindowFlag(Qt.WindowType.Popup)
        self.setObjectName('quickSearchBar')

        self.createUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.animateClose()

        else:
            super().keyPressEvent(event)

    def exec(self, pos=None):
        if pos:
            super().exec(pos)
            return

        parent_center = self.parent().rect().center()
        global_center = self.parent().mapToGlobal(parent_center)
        target_width = 400
        target_height = 60

        start_rect = QRect(
            global_center.x(),
            global_center.y(),
            1,
            1
        )
        end_rect = QRect(
            global_center.x() - target_width // 2,
            global_center.y() - target_height // 2,
            target_width,
            target_height
        )

        self.setGeometry(start_rect)
        self.container.setFixedSize(target_width, target_height)
        self.updateCompleter()
        self.startEditing()

        self.show()

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def createUI(self):
        self.container = QWidget(self)
        self.container.setLayout(QVBoxLayout())

        self.search_box = QLineEdit()
        self.search_box.setObjectName('quickSearchBar')
        self.search_box.setPlaceholderText('Search...')
        self.search_box.setFixedSize(375, 40)
        self.search_box.returnPressed.connect(lambda: self.search(self.search_box.text()))
        self.container.layout().addWidget(self.search_box, alignment=Qt.AlignmentFlag.AlignCenter)

        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(self.container)

        self.addAction(widget_action)

    def search(self, text: str):
        self.parent().search(text)
        self.animateClose()

    def startEditing(self):
        self.search_box.setFocus()
        self.search_box.selectAll()

    def setUrl(self, url):
        self.search_box.setText(url)

    def updateCompleter(self):
        items = COMMANDS

        for url, name in ibrowse.bookmarks().items():
            items.append(url)

        self._completer = QCompleter(items)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.search_box.setCompleter(self._completer)

    def animateClose(self):
        current_geometry = self.geometry()
        end_rect = QRect(
            current_geometry.center().x(),
            current_geometry.center().y(),
            1,
            1
        )

        self.close_animation = QPropertyAnimation(self, b'geometry')
        self.close_animation.setDuration(200)
        self.close_animation.setStartValue(current_geometry)
        self.close_animation.setEndValue(end_rect)
        self.close_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.close_animation.finished.connect(self.close)
        self.close_animation.start()
