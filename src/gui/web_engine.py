from src.imports import *
from src.gui.widgets import ContextMenu


class WebEnginePage(QWebEnginePage):
    def __init__(self, profile, tab_view):
        super().__init__(profile, tab_view)
        self.tab_view = tab_view


class WebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
