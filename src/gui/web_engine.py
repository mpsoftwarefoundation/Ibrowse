from src.imports import *


class WebEnginePage(QWebEnginePage):
    def __init__(self, profile, tab_view):
        super().__init__(profile, tab_view)
        self.tab_view = tab_view


class WebEngineView(QWebEngineView):
    def __init__(self, page: WebEnginePage, parent=None):
        super().__init__(parent)
        self.setPage(page)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.customContextMenuRequested.connect(self.showMenu)

    def showMenu(self, event):
        menu = self.createStandardContextMenu()
        menu.exec(self.mapToGlobal(event))
