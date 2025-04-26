from src.imports import *
from src.gui.widgets import SearchBar, EngineTypeCombo, ContextMenu
from src.gui.dialogs import PasswordsDialog, GetBookmarkDialog
from urllib.parse import urlparse


class Tab(QWidget):
    def __init__(self, tab_view: QTabWidget, url: str = '', parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0,0,0)

        self.tab_view = tab_view
        self._passwords_dialog = PasswordsDialog(self)

        self.createUI()
        self.createActions()

        if url:
            self.search(url)

    def createUI(self):
        nav_bar = QWidget()
        nav_bar.setFixedHeight(38)
        nav_bar.setLayout(QHBoxLayout())
        nav_bar.layout().setContentsMargins(5, 5, 5, 5)

        back_btn = QPushButton('◀')
        back_btn.setObjectName('searchBarButton')
        back_btn.setShortcut(QKeySequence('Ctrl+left'))
        forward_btn = QPushButton('▶')
        forward_btn.setObjectName('searchBarButton')
        forward_btn.setShortcut(QKeySequence('Ctrl+right'))
        reload_btn = QPushButton('↻')
        reload_btn.setObjectName('searchBarButton')
        reload_btn.setShortcut(QKeySequence('Ctrl+R'))
        menu_btn = QPushButton('···')
        menu_btn.setObjectName('searchBarButton')
        menu_btn.clicked.connect(lambda: self.showMenu(menu_btn))

        self._engine_combo = EngineTypeCombo(self)
        self._search_bar = SearchBar()
        self._search_bar.returnPressed.connect(lambda: self.search(self._search_bar.text()))

        nav_bar.layout().addWidget(back_btn)
        nav_bar.layout().addWidget(forward_btn)
        nav_bar.layout().addWidget(reload_btn)
        nav_bar.layout().addWidget(self._engine_combo)
        nav_bar.layout().addWidget(self._search_bar)
        nav_bar.layout().addWidget(menu_btn)

        profile = QWebEngineProfile('PersistentProfile', self)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setCachePath(ibrowse.cache_dir())
        profile.setPersistentStoragePath(ibrowse.cache_dir())

        page = QWebEnginePage(profile, self)
        self._browser = QWebEngineView()
        self._browser.setPage(page)
        self._browser.urlChanged.connect(self._search_bar.setUrl)
        self._browser.titleChanged.connect(self.updateTab)
        self._browser.iconChanged.connect(self.updateTab)
        self._browser.loadFinished.connect(self.updateTab)
        self._browser.loadFinished.connect(self.tryAutoFillPassword)
        back_btn.clicked.connect(self._browser.back)
        forward_btn.clicked.connect(self._browser.forward)
        reload_btn.clicked.connect(self._browser.reload)

        self.layout().addWidget(nav_bar)
        self.layout().addWidget(self._browser)

    def createActions(self):
        new_tab_action = QAction('New Tab', self)
        new_tab_action.setShortcut(QKeySequence('Ctrl+N'))
        new_tab_action.triggered.connect(self.tab_view.newTab)

        new_window_action = QAction('New Window', self)
        new_window_action.setShortcut(QKeySequence('Ctrl+Shift+N'))
        new_window_action.triggered.connect(self.tab_view.parent().newWindow)

        quick_edit_action = QAction('Quick Edit', self)
        quick_edit_action.setShortcut(QKeySequence('Ctrl+Q'))
        quick_edit_action.triggered.connect(self._search_bar.startEditing)

        self.addAction(new_tab_action)
        self.addAction(new_window_action)
        self.addAction(quick_edit_action)

    def search(self, query: str):
        query = query.strip()

        if query.startswith('https'):
            pass

        elif query.startswith('/'):
            if query == '/exit':
                QApplication.quit()

            elif query == '/help':
                self.tab_view.addTab(self.fromHtml('resources/pages/help.html'), 'Help')
                self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
                return

            elif query == '/welcome':
                self.tab_view.addTab(self.fromHtml('resources/pages/startup.html'), 'Help')
                self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
                return

        elif '.com' in query:
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
            self.tab_view.setTabText(index, (self._browser.title()[:25] + '...')
            if len(self._browser.title()) > 25 else self._browser.title()
                                     )
            self.tab_view.setTabToolTip(index, self._browser.title())
            self.tab_view.setTabIcon(index, self._browser.icon())

    def showMenu(self, button: QPushButton):
        menu = ContextMenu(self)
        menu.setAnimationEnabled(True)

        new_tab_action = QAction('New Tab', self)
        new_tab_action.triggered.connect(self.tab_view.newTab)
        new_window_action = QAction('New Window', self)
        new_window_action.triggered.connect(self.tab_view.parent().newWindow)
        bookmark_tab_action = QAction('Bookmark This Tab', self)
        bookmark_tab_action.triggered.connect(self.bookmark)
        passwords_action = QAction('Passwords...', self)
        passwords_action.triggered.connect(self._passwords_dialog.show)
        bookmarks_menu = ContextMenu('Bookmarks', self)

        for url, name in ibrowse.bookmarks().items():
            action = QWidgetAction(self)
            action.url = url
            action.triggered.connect(lambda _, u=action.url: self.search(u))

            container = QWidget()
            container.setLayout(QHBoxLayout())
            label = QLabel(name)
            remove_btn = QPushButton('✕')
            remove_btn.setFixedWidth(20)
            remove_btn.setToolTip('Remove this bookmark')
            remove_btn.clicked.connect(lambda _, u=action.url: self.removeBookmark(u, bookmarks_menu, action))

            container.layout().addWidget(label)
            container.layout().addStretch()
            container.layout().addWidget(remove_btn)

            action.setDefaultWidget(container)

            bookmarks_menu.addAction(action)

        menu.addAction(new_tab_action)
        menu.addAction(new_window_action)
        menu.addSeparator()
        menu.addAction(bookmark_tab_action)
        menu.addSeparator()
        menu.addAction(passwords_action)
        menu.addMenu(bookmarks_menu)

        menu.exec(self.mapToGlobal(button.pos()))

    def bookmark(self):
        dialog = GetBookmarkDialog(self)
        dialog.url_input.setDefaultValue(self.browser().url().toString())
        dialog.input.setDefaultValue(self.browser().page().title())
        dialog.exec()

        self._search_bar.updateCompleter()

    def removeBookmark(self, url: str, menu: QMenu, action: QAction):
        ibrowse.remove_bookmark(url)

        menu.removeAction(action)
        self._search_bar.updateCompleter()

    def tryAutoFillPassword(self, ok: bool):
        if not ok:
            return

        full_url = self._browser.url().toString()
        parsed = urlparse(full_url)
        netloc = parsed.netloc.lower()
        base_url = f"{parsed.scheme}://{netloc}"

        passwords = ibrowse.passwords()
        creds = None

        if full_url in passwords:
            creds = passwords[full_url]

        elif base_url in passwords:
            creds = passwords[base_url]

        else:
            for key in passwords:
                if key in full_url:
                    creds = passwords[key]
                    break

        if not creds:
            return

        ok = QMessageBox.question(self, 'Password', 'Use saved password for this site?')

        if ok:
            username, password = creds

            js = f"""
            (function autoFill(retries = 20) {{
                if (retries === 0) return;
    
                const inputs = document.querySelectorAll('input');
                let userField = null, passField = null;
    
                for (let i = 0; i < inputs.length; i++) {{
                    const type = inputs[i].type.toLowerCase();
                    if (!userField && (type === 'text' || type === 'email')) userField = inputs[i];
                    if (!passField && type === 'password') passField = inputs[i];
                }}
    
                if (userField && passField) {{
                    userField.value = "{username}";
                    passField.value = "{password}";
                }} else {{
                    setTimeout(() => autoFill(retries - 1), 300);
                }}
            }})();
            """

            self._browser.page().runJavaScript(js)

    def engineCombo(self) -> EngineTypeCombo:
        return self._engine_combo

    def searchBar(self) -> SearchBar:
        return self._search_bar

    def browser(self) -> QWebEngineView:
        return self._browser

    def activeUrl(self) -> QUrl:
        return self._browser.url()
