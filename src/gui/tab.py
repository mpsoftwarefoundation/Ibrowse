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
        self.engine_combo = EngineTypeCombo(self)
        self.search_bar = SearchBar()
        self.search_bar.returnPressed.connect(lambda: self.search(self.search_bar.text()))
        nav_bar.layout().addWidget(back_btn)
        nav_bar.layout().addWidget(forward_btn)
        nav_bar.layout().addWidget(reload_btn)
        nav_bar.layout().addWidget(self.engine_combo)
        nav_bar.layout().addWidget(self.search_bar)

        self.browser = QWebEngineView()
        self.browser.urlChanged.connect(self.search_bar.setUrl)
        self.browser.titleChanged.connect(self.updateTab)
        self.browser.iconChanged.connect(self.updateTab)
        back_btn.clicked.connect(self.browser.back)
        forward_btn.clicked.connect(self.browser.forward)
        reload_btn.clicked.connect(self.browser.reload)

        self.layout().addWidget(nav_bar)
        self.layout().addWidget(self.browser)

    def search(self, query: str):
        if query.startswith('https'):
            pass

        elif '.' in query.strip():
            query = f'https://{query}'

        else:
            query = f'https://{self.engine_combo.itemData(self.engine_combo.currentIndex())}{query.replace(' ', '+')}'

        self.search_bar.setText(query)
        self.browser.load(QUrl(query))
        self.browser.setFocus()

    def fromHtml(self, file_name: str):
        html = ''

        with open(file_name, 'r') as f:
            html = f.read()

        if html:
            self.browser.setHtml(html)
            self.browser.setFocus()

        return self

    def updateTab(self):
        index = self.tab_view.indexOf(self)

        if index != -1:
            self.tab_view.setTabText(index, self.browser.title())
            self.tab_view.setTabIcon(index, self.browser.icon())
