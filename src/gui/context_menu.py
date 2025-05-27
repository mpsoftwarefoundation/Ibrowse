import ibrowse
from PyQt6.QtCore import QEvent, QTimer, QUrl, Qt, QRect, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtWidgets import (QLineEdit, QCompleter, QMenu, QVBoxLayout, QWidget, QWidgetAction, QComboBox, QApplication,
    QHBoxLayout, QLabel)
from src.gui.commands import COMMANDS


class ContextMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(150, 30)

        self._animation_enabled = False

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        else:
            m = ContextMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m

    def exec(self, pos=None):
        if pos and self.animationEnabled():
            screen_rect = QApplication.primaryScreen().availableGeometry()

            menu_size = self.sizeHint()

            if pos.x() + menu_size.width() > screen_rect.right():
                pos.setX(screen_rect.right() - menu_size.width())

            if pos.y() + menu_size.height() > screen_rect.bottom():
                pos.setY(screen_rect.bottom() - menu_size.height())

            self.animation = QPropertyAnimation(self, b'pos')
            self.animation.setDuration(100)
            self.animation.setStartValue(QPoint(pos.x(), pos.y() + 10))
            self.animation.setEndValue(pos)

            self.animation.start()

        super().exec(pos)

    def setAnimationEnabled(self, enabled: bool):
        self._animation_enabled = enabled

    def animationEnabled(self):
        return self._animation_enabled
