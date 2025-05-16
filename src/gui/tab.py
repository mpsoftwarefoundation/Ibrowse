import os
import subprocess
import sys
import ibrowse
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QKeySequence, QAction, QIcon
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QWidgetAction, QLabel, QMenu,
    QMessageBox)
from src.gui.dialogs import PasswordsDialog, CreateBookmarkDialog
from src.gui.web_engine import WebEnginePage, WebEngineView
from src.gui.widgets import SearchBar, QuickSearchBar, EngineTypeCombo, ContextMenu
from urllib.parse import urlparse


class Tab(QWidget):
    def __init__(self, tab_view, profile: QWebEngineProfile, url: str = '', parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.tab_view = tab_view
        self.profile = profile
        self._passwords_dialog = PasswordsDialog(self)

        self.createUI()
        self.createBrowser()

        if url:
            self.search(url)

    def close(self):
        self.tab_view.closeTab(self.tab_view.indexOf(self))

    def createUI(self):
        nav_bar = QWidget()
        nav_bar.setFixedHeight(30)
        nav_bar.setLayout(QHBoxLayout())
        nav_bar.layout().setContentsMargins(5, 5, 5, 0)

        back_btn = QPushButton(QIcon('resources/icons/ui/back_icon.svg'), '', self)
        back_btn.setObjectName('searchBarButton')
        back_btn.setToolTip('Navigate backwards')
        forward_btn = QPushButton(QIcon('resources/icons/ui/forward_icon.svg'), '', self)
        forward_btn.setObjectName('searchBarButton')
        forward_btn.setToolTip('Navigate forwards')
        reload_btn = QPushButton(QIcon('resources/icons/ui/reload_icon.svg'), '', self)
        reload_btn.setObjectName('searchBarButton')
        reload_btn.setShortcut(QKeySequence('Ctrl+R'))
        reload_btn.setToolTip('Reload the current page')
        menu_btn = QPushButton(QIcon('resources/icons/ui/menu_access_icon.svg'), '', self)
        menu_btn.setObjectName('searchBarButton')
        menu_btn.setToolTip('Ibrowse menu')
        menu_btn.clicked.connect(lambda: self.showMenu(menu_btn))

        self._engine_combo = EngineTypeCombo(self)
        self._engine_combo.setCurrentText(ibrowse.preferred_browser())
        self._engine_combo.setToolTip('Change the preferred search engine')
        self._search_bar = SearchBar()
        self._search_bar.setToolTip('Enter a url or search query')
        self._search_bar.returnPressed.connect(lambda: self.search(self._search_bar.text()))

        nav_bar.layout().addWidget(back_btn)
        nav_bar.layout().addWidget(forward_btn)
        nav_bar.layout().addWidget(reload_btn)
        nav_bar.layout().addWidget(self._engine_combo)
        nav_bar.layout().addWidget(self._search_bar)
        nav_bar.layout().addWidget(menu_btn)

        self._page = WebEnginePage(self.profile, self.tab_view)
        self._browser = WebEngineView(self._page, self.tab_view, self)
        back_btn.clicked.connect(self._browser.back)
        forward_btn.clicked.connect(self._browser.forward)
        reload_btn.clicked.connect(self._browser.reload)

        self.layout().addWidget(nav_bar)
        self.layout().addWidget(self._browser)

    def createBrowser(self):
        self._browser.urlChanged.connect(self._search_bar.setUrl)
        self._browser.titleChanged.connect(self.updateTab)
        self._browser.iconChanged.connect(self.updateTab)
        self._browser.loadFinished.connect(self.updateTab)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self._browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, ibrowse.smooth_scrolling_enabled())

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

            elif query == '/welcome':
                self.tab_view.addTab(self.fromHtml('resources/pages/startup.html'), 'Help')
                self.tab_view.setCurrentIndex(self.tab_view.count() - 1)

            elif query == '/newtab':
                self.tab_view.newTab()

            elif query == '/newwindow':
                self.tab_view.parent().newWindow()

            elif query == '/close':
                self.close()

            else:
                self.tab_view.addTab(self.fromHtml('resources/pages/help.html'), 'Help')
                self.tab_view.setCurrentIndex(self.tab_view.count() - 1)

            return

        elif '.com' in query:
            query = f'https://{query}'

        else:
            query = f'https://{self._engine_combo.itemData(self._engine_combo.currentIndex())}{query.replace(' ', '+')}'

        self._search_bar.setText(query)
        self._browser.load(QUrl(query))
        self._browser.setFocus()

    def quickSearch(self):
        if not hasattr(self, 'quick_search_bar'):
            self.quick_search_bar = QuickSearchBar(self)
            self.quick_search_bar.setUrl(self._search_bar.text())

        self.quick_search_bar.exec()

    def fromHtml(self, file_name: str):
        html = ibrowse.read_html(file_name)

        if html:
            self._browser.urlChanged.disconnect(self._search_bar.setUrl)
            self._browser.setHtml(html, QUrl('about:blank'))
            self._browser.setFocus()
            self._browser.urlChanged.connect(self._search_bar.setUrl)

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
        if not hasattr(self, 'menu'):
            self.menu = ContextMenu(self)
            self.menu.setAnimationEnabled(True)

            new_tab_action = QAction('New Tab', self)
            new_tab_action.triggered.connect(self.tab_view.insertNewTab)
            new_window_action = QAction('New Window', self)
            new_window_action.triggered.connect(self.tab_view.parent().newWindow)
            bookmark_tab_action = QAction('Bookmark This Tab', self)
            bookmark_tab_action.triggered.connect(self.bookmark)
            passwords_action = QAction('Passwords...', self)
            passwords_action.triggered.connect(self._passwords_dialog.show)

            if not hasattr(self, 'bookmarks_menu'):
                self.bookmarks_menu = ContextMenu('Bookmarks', self)

            smooth_scrolling_action = QAction('Smooth Scrolling (Requires Restart)', self)
            smooth_scrolling_action.setCheckable(True)
            smooth_scrolling_action.setChecked(ibrowse.smooth_scrolling_enabled())
            smooth_scrolling_action.triggered.connect(lambda: self.enableSmoothScrolling(smooth_scrolling_action))
            clear_caches_action = QAction('Clear Caches (Requires Restart)', self)
            clear_caches_action.triggered.connect(self.clearCaches)

            self.menu.addAction(new_tab_action)
            self.menu.addAction(new_window_action)
            self.menu.addSeparator()
            self.menu.addAction(bookmark_tab_action)
            self.menu.addSeparator()
            self.menu.addAction(passwords_action)
            self.menu.addMenu(self.bookmarks_menu)
            self.menu.addSeparator()
            self.menu.addAction(smooth_scrolling_action)
            self.menu.addAction(clear_caches_action)

        self.bookmarks_menu.clear()

        for url, name in ibrowse.bookmarks().items():
            action = QWidgetAction(self)
            action.url = url
            action.triggered.connect(lambda _, u=action.url: self.search(u))

            container = QWidget()
            container.setLayout(QHBoxLayout())
            label = QLabel(name)
            remove_btn = QPushButton(QIcon('resources/icons/ui/close_icon.svg'), '', self)
            remove_btn.setFixedWidth(20)
            remove_btn.setToolTip('Remove this bookmark')
            remove_btn.clicked.connect(lambda _, u=action.url: self.removeBookmark(u, self.bookmarks_menu, action))

            container.layout().addWidget(label)
            container.layout().addStretch()
            container.layout().addWidget(remove_btn)

            action.setDefaultWidget(container)

            self.bookmarks_menu.addAction(action)

        self.menu.exec(self.mapToGlobal(button.pos()))

    def bookmark(self):
        dialog = CreateBookmarkDialog(self)
        dialog.url_input.setDefaultValue(self._browser.url().toString())
        dialog.input.setDefaultValue(self._browser.page().title())
        dialog.exec()

        self._search_bar.updateCompleter()

    def removeBookmark(self, url: str, menu: QMenu, action: QAction):
        ibrowse.remove_bookmark(url)

        menu.removeAction(action)
        self._search_bar.updateCompleter()

    def enableSmoothScrolling(self, action: QAction):
        ibrowse.set_smooth_scrolling(action.isChecked())

        self.tab_view.parent().restart()

    def clearCaches(self):
        ok = QMessageBox.warning(self,
                                 'Warning',
                                 'Clearing caches will delete all browsing data!\n\n'
                                 'This process is safe, but you will be logged out of all '
                                 'websites and cookies will be deleted. Are you sure you want '
                                 'to do this?',
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if ok == QMessageBox.StandardButton.Yes:
            clear_script = os.path.join(ibrowse.config_dir(), 'clear_caches.py')

            with open(clear_script, "w") as f:
                f.write(f"""
import time
import shutil
import os

time.sleep(1.5)  # wait for app to fully close

cache_dir = r"{ibrowse.cache_dir()}"

if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir, ignore_errors=True)
    
os.mkdir(r"{ibrowse.config_dir()}/cache")
            """)

            subprocess.Popen([sys.executable, clear_script], close_fds=True)

            self.tab_view.parent().restart()

    def engineCombo(self) -> EngineTypeCombo:
        return self._engine_combo

    def searchBar(self) -> SearchBar:
        return self._search_bar

    def page(self) -> QWebEnginePage:
        return self._page

    def passwordManager(self) -> PasswordsDialog:
        return self._passwords_dialog

    def browser(self) -> QWebEngineView:
        return self._browser

    def activeUrl(self) -> QUrl:
        return self._browser.url()
