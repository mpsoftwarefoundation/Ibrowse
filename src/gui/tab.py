from importlib import reload

from src.imports import *
from src.gui.widgets import SearchBar, EngineTypeCombo


class Tab(QWidget):
    def __init__(self, tab_view: QTabWidget, url: str = '', parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0,0,0)

        self.tab_view = tab_view

        self.createUI()

        if url:
            self.search(url)

    def createUI(self):
        nav_bar = QWidget()
        nav_bar.setFixedHeight(38)
        nav_bar.setLayout(QHBoxLayout())
        nav_bar.layout().setContentsMargins(5, 5, 5, 5)

        back_btn = QPushButton('<')
        back_btn.setFixedWidth(20)
        forward_btn = QPushButton('>')
        forward_btn.setFixedWidth(20)
        reload_btn = QPushButton('↺')
        reload_btn.setFixedWidth(20)

        self._engine_combo = EngineTypeCombo(self)
        self._search_bar = SearchBar()
        self._search_bar.returnPressed.connect(lambda: self.search(self._search_bar.text()))

        nav_bar.layout().addWidget(back_btn)
        nav_bar.layout().addWidget(forward_btn)
        nav_bar.layout().addWidget(reload_btn)
        nav_bar.layout().addWidget(self._engine_combo)
        nav_bar.layout().addWidget(self._search_bar)

        self._browser = QWebEngineView()
        self._browser.urlChanged.connect(self._search_bar.setUrl)
        self._browser.titleChanged.connect(self.updateTab)
        self._browser.iconChanged.connect(self.updateTab)
        back_btn.clicked.connect(self._browser.back)
        forward_btn.clicked.connect(self._browser.forward)
        reload_btn.clicked.connect(self._browser.reload)

        self.layout().addWidget(nav_bar)
        self.layout().addWidget(self._browser)

    def search(self, query: str):
        if query.startswith('https'):
            pass

        elif '.' in query.strip():
            query = f'https://{query}'

        else:
            query = f'https://{self._engine_combo.itemData(self._engine_combo.currentIndex())}{query.replace(' ', '+')}'

        self._search_bar.setText(query)
        self._browser.load(QUrl(query))
        self._browser.setFocus()

    def fromHtml(self, file_name: str):
        html = ''

        with open(file_name, 'r') as f:
            html = f.read()

        if html:
            self._browser.setHtml(html)
            self._browser.setFocus()

        return self

    def updateTab(self):
        index = self.tab_view.indexOf(self)

        if index != -1:
            self.tab_view.setTabText(index, self._browser.title())
            self.tab_view.setTabIcon(index, self._browser.icon())

    def engineCombo(self) -> EngineTypeCombo:
        return self._engine_combo

    def searchBar(self) -> SearchBar:
        return self._search_bar

    def browser(self) -> QWebEngineView:
        return self._browser
