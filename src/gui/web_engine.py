from src.imports import *


class WebEnginePage(QWebEnginePage):
    def __init__(self, profile, tab_view):
        super().__init__(profile, tab_view)
        self.tab_view = tab_view