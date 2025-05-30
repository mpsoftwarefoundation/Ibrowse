import os
import subprocess
import sys
import ibrowse
from urllib.parse import urlparse
from PyQt6.QtCore import QEventLoop, QPointF, QSize, QUrl, QTemporaryFile
from PyQt6.QtGui import QKeySequence, QAction, QIcon, QPainter
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QWidgetAction, QLabel, QMenu,
    QMessageBox)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from src.gui.dialogs import CreateBookmarkDialog
from src.gui.web_engine import WebEnginePage, WebEngineView
from src.gui.engine_selector import EngineSelector
from src.gui.search_bar import SearchBar
from src.gui.quick_search_bar import QuickSearchBar


class Tab(QWidget):
    def __init__(self, tab_view, profile: QWebEngineProfile, url: str = '', parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.tab_view = tab_view
        self.profile = profile
        self._print_result_loop = QEventLoop()
        self._printer = None

        self.createUI()
        self.createBrowser()

        if url:
            self.search(url)

    def close(self):
        self.tab_view.closeTab(self.tab_view.indexOf(self))

    def createUI(self):
        nav_bar = QWidget()
        nav_bar.setObjectName('navBar')
        nav_bar.setFixedHeight(35)
        nav_bar.setLayout(QHBoxLayout())
        nav_bar.layout().setContentsMargins(5, 5, 5, 0)

        size = QSize(25, 30)

        back_btn = QPushButton(QIcon('resources/icons/ui/back_icon.svg'), '', self)
        back_btn.setFixedSize(size)
        back_btn.setObjectName('button')
        back_btn.setToolTip('Navigate backwards')
        forward_btn = QPushButton(QIcon('resources/icons/ui/forward_icon.svg'), '', self)
        forward_btn.setFixedSize(size)
        forward_btn.setObjectName('button')
        forward_btn.setToolTip('Navigate forwards')
        reload_btn = QPushButton(QIcon('resources/icons/ui/reload_icon.svg'), '', self)
        reload_btn.setFixedSize(size)
        reload_btn.setObjectName('button')
        reload_btn.setShortcut(QKeySequence('Ctrl+R'))
        reload_btn.setToolTip('Reload the current page')
        menu_btn = QPushButton(QIcon('resources/icons/ui/menu_access_icon.svg'), '', self)
        menu_btn.setFixedSize(size)
        menu_btn.setObjectName('button')
        menu_btn.setToolTip('Ibrowse Menu')
        menu_btn.clicked.connect(lambda: self.tab_view.showMenu(menu_btn))

        self._engine_combo = EngineSelector(self)
        self._engine_combo.setFixedHeight(size.height())
        self._engine_combo.setCurrentText(ibrowse.preferred_browser())
        self._engine_combo.setToolTip('Change the preferred search engine')
        self._search_bar = SearchBar()
        self._search_bar.setFixedHeight(size.height())
        self._search_bar.setToolTip('Enter a url or search query')
        self._search_bar.returnPressed.connect(lambda: self.search(self._search_bar.text()))

        combo_search_container = QWidget()
        combo_search_container.setLayout(QHBoxLayout())
        combo_search_container.layout().setContentsMargins(0, 0, 0, 0)
        combo_search_container.layout().setSpacing(0)
        combo_search_container.layout().addWidget(self._engine_combo)
        combo_search_container.layout().addWidget(self._search_bar)

        nav_bar.layout().addWidget(back_btn)
        nav_bar.layout().addWidget(forward_btn)
        nav_bar.layout().addWidget(reload_btn)
        nav_bar.layout().addWidget(combo_search_container)
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
        self._browser.titleChanged.connect(self.tab_view.updateTab)
        self._browser.iconChanged.connect(self.tab_view.updateTab)
        self._browser.loadFinished.connect(self.tab_view.updateTab)
        self._browser.printFinished.connect(self.printFinished)
        self._browser.printRequested.connect(self.printPreview)
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
                self.tab_view.addTab(self.fromHtml('resources/pages/help.html'), '')
                self.tab_view.setCurrentIndex(self.tab_view.count() - 1)

            elif query == '/welcome':
                self.tab_view.addTab(self.fromHtml('resources/pages/startup.html'), '')
                self.tab_view.setCurrentIndex(self.tab_view.count() - 1)

            elif query == '/whatsnew':
                self.tab_view.addTab(self.fromHtml('resources/pages/whats_new.html'), '')
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

        elif query.startswith('http'):
            pass

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

    def printPreview(self):
        if self._printer is None:
            self._printer = QPrinter()

        preview = QPrintPreviewDialog(self._printer, self._browser)
        preview.paintRequested.connect(self.printDocument)

        preview.exec()

    def printDocument(self, printer: QPrinter):
        self._browser.print(printer)

        self._print_result_loop.exec(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

    def printFinished(self, success: bool):
        if not success:
            painter = QPainter()

            if painter.begin(self._printer):
                font = painter.font()
                font.setPixelSize(20)
                painter.setFont(font)
                painter.drawText(QPointF(10,25), 'Could not generate print preview.')
                painter.end()

        self._print_result_loop.quit()

    def clearCaches(self):
        self.profile.clearHttpCache()
        self.profile.clearAllVisitedLinks()

    def fromHtml(self, file_name: str):
        html = ibrowse.read_html(file_name)

        if html:
            self._browser.urlChanged.disconnect(self._search_bar.setUrl)
            self._browser.setHtml(html, QUrl('about:blank'))
            self._browser.setFocus()
            self._browser.urlChanged.connect(self._search_bar.setUrl)

        return self

    def engineCombo(self) -> EngineSelector:
        return self._engine_combo

    def searchBar(self) -> SearchBar:
        return self._search_bar

    def page(self) -> QWebEnginePage:
        return self._page

    def browser(self) -> QWebEngineView:
        return self._browser

    def activeUrl(self) -> QUrl:
        return self._browser.url()
