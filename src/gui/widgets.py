from src.imports import *


class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('searchBar')
        self.setPlaceholderText('Search...')
        self.installEventFilter(self)

        self._mouse_pressed = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self._mouse_pressed = True
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        super().focusInEvent(event)

        if self._mouse_pressed:
            self._mouse_pressed = False
            QTimer.singleShot(0, self.selectAll)

    def setUrl(self, url: QUrl):
        self.blockSignals(True)
        self.setText(url.toString())
        self.blockSignals(False)


class EngineTypeCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._engine_types = {
            'Google': 'google.com/search?q=',
            'DuckDuckGo': 'duckduckgo.com/?q=',
            'Bing': 'bing.com/search?q=',
            'Yahoo': 'search.yahoo.com/search?p=',
            'Startpage': 'startpage.com/sp/search?query=',
            'Ecosia': 'ecosia.org/search?q=',
            'Qwant': 'qwant.com/?q=',
            'Yandex': 'yandex.com/search/?text=',
            'Brave': 'search.brave.com/search?q=',
            'Mojeek': 'mojeek.com/search?q='
        }
        self._engine_type = 'google.com/search?q='

        self.createTypes()

    def createTypes(self):
        for k, v in self._engine_types.items():
            self.addItem(k, v)


class PageTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.parent().close()
            return

        self.removeTab(index)
