import ibrowse
from PyQt6.QtCore import QPoint, QTimer, QMimeData, QUrl, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragLeaveEvent, QDropEvent, QDragEnterEvent, QDragMoveEvent, QIcon, QKeySequence
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTabBar, QTabWidget, QWidget, QWidgetAction
from src.gui.tab import Tab
from src.gui.dialogs import PasswordsDialog
from src.gui.context_menu import ContextMenu


class TabBar(QTabBar):
    def __init__(self, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self._tab_view = tab_view

    def mouseDoubleClickEvent(self, event):
        if not self._tab_view.widget(self.tabAt(event.pos())):
            super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        if not hasattr(self, 'menu'):
            self.menu = ContextMenu(self)

        self.menu.clear()

        tab = self._tab_view.widget(self.tabAt(event.pos()))

        if tab:
            if tab.isLocked():
                unlock_tab_action = self.menu.addAction('Unlock This Tab')
                unlock_tab_action.triggered.connect(lambda: self.unlockTab(tab))

            else:
                lock_tab_action = self.menu.addAction('Lock This Tab')
                lock_tab_action.triggered.connect(lambda: self.lockTab(tab))

        self.menu.exec(event.pos())

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

            self.createPlaceholderTab()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.removePlaceholderTab()

        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isValid() and url.scheme().startswith("http"):
                    self._tab_view.newTabFromUrl(url)

            event.acceptProposedAction()

        self.removePlaceholderTab()

    def lockTab(self, tab):
        tab.setLocked(True)
        index = self._tab_view.indexOf(tab)

        self.setTabEnabled(index, False)
        self.setTabIcon(index, QIcon('resources/icons/ui/locked_icon.svg'))
        self.setTabToolTip(index, 'This tab is locked')

        self.setCurrentIndex(index)

    def unlockTab(self, tab):
        tab.setLocked(False)
        index = self._tab_view.indexOf(tab)

        if not self.isTabEnabled(index):
            self.setTabEnabled(index, True)
            self.setTabIcon(index, tab.browser().icon())
            self.setTabToolTip(index, tab.browser().title())

    def createPlaceholderTab(self):
        if not hasattr(self, 'dummy_tab'):
            self.dummy_tab = QWidget()
            self._tab_view.addTab(self.dummy_tab, 'Drop the url to add it')

    def removePlaceholderTab(self):
        if hasattr(self, 'dummy_tab'):
            self._tab_view.removeTab(self._tab_view.indexOf(self.dummy_tab))

            del self.dummy_tab


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(TabBar(self, self))
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self._passwords_dialog = PasswordsDialog(self)

        self.tabBarDoubleClicked.connect(self.newTab)
        self.tabCloseRequested.connect(self.closeTab)

        self.createActions()

    def createActions(self):
        new_tab_action = self.addAction('New Tab')
        new_tab_action.setShortcut(QKeySequence('Ctrl+N'))
        new_tab_action.triggered.connect(self.insertNewTab)

        new_window_action = self.addAction('New Window')
        new_window_action.setShortcut(QKeySequence('Ctrl+Shift+N'))
        new_window_action.triggered.connect(self.parent().newWindow)

        close_tab_action = self.addAction('Close Tab')
        close_tab_action.setShortcut(QKeySequence('Ctrl+E'))
        close_tab_action.triggered.connect(lambda: self.closeTab(self.currentIndex()))

        password_manager_action = self.addAction('Password Manager')
        password_manager_action.setShortcut(QKeySequence('Ctrl+K'))
        password_manager_action.triggered.connect(lambda: self.currentTab().passwordManager().show())

        bookmark_tab_action = self.addAction('Bookmark This Tab')
        bookmark_tab_action.setShortcut(QKeySequence('Ctrl+B'))
        bookmark_tab_action.triggered.connect(lambda: self.currentTab().bookmark())

        jump_to_search_action = self.addAction('Jump To Search Bar')
        jump_to_search_action.setShortcut(QKeySequence('Ctrl+/'))
        jump_to_search_action.triggered.connect(self.startEditing)

        quick_search_action = self.addAction('Quick Search')
        quick_search_action.setShortcut(QKeySequence('Ctrl+Q'))
        quick_search_action.triggered.connect(lambda: self.currentTab().quickSearch())

        print_page_action = self.addAction('Print')
        print_page_action.setShortcut(QKeySequence('Ctrl+P'))
        print_page_action.triggered.connect(lambda: self.currentTab().printPreview())

        self.addAction(new_tab_action)
        self.addAction(new_window_action)
        self.addAction(close_tab_action)
        self.addAction(password_manager_action)
        self.addAction(bookmark_tab_action)
        self.addAction(quick_search_action)

    def showMenu(self, button: QPushButton):
        if not hasattr(self, 'menu'):
            self.menu = ContextMenu(self)
            self.menu.setAnimationEnabled(True)

            new_tab_action = QAction('New Tab', self)
            new_tab_action.triggered.connect(self.insertNewTab)
            new_window_action = QAction('New Window', self)
            new_window_action.triggered.connect(self.parent().newWindow)
            bookmark_tab_action = QAction('Bookmark This Tab', self)
            bookmark_tab_action.triggered.connect(lambda: self.currentTab().bookmark())
            passwords_action = QAction('Passwords...', self)
            passwords_action.triggered.connect(self._passwords_dialog.show)

            if not hasattr(self, 'bookmarks_menu'):
                self.bookmarks_menu = ContextMenu('Bookmarks', self)

            smooth_scrolling_action = QAction('Smooth Scrolling (Requires Restart)', self)
            smooth_scrolling_action.setCheckable(True)
            smooth_scrolling_action.setChecked(ibrowse.smooth_scrolling_enabled())
            smooth_scrolling_action.triggered.connect(lambda: self.currentTab().enableSmoothScrolling(smooth_scrolling_action))
            clear_caches_action = QAction('Clear Caches', self)
            clear_caches_action.triggered.connect(lambda: self.currentTab().clearCaches())

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
            action.triggered.connect(lambda _, u=action.url: self.currentTab().search(u))

            container = QWidget()
            container.setLayout(QHBoxLayout())
            label = QLabel(name)
            label.setToolTip('Open this bookmark')
            remove_btn = QPushButton(QIcon('resources/icons/ui/close_icon.svg'), '', self)
            remove_btn.setFixedWidth(20)
            remove_btn.setToolTip('Remove this bookmark')
            remove_btn.clicked.connect(lambda _, u=action.url: self.currentTab().removeBookmark(u, self.bookmarks_menu, action))

            container.layout().addWidget(label)
            container.layout().addStretch()
            container.layout().addWidget(remove_btn)

            action.setDefaultWidget(container)

            self.bookmarks_menu.addAction(action)

        self.menu.exec(self.currentTab().mapToGlobal(button.pos()))

    def startEditing(self):
        self.currentTab().searchBar().startEditing()

    def forward(self):
        self.currentTab().browser().forward()

    def back(self):
        self.currentTab().browser().back()

    def insertNewTab(self):
        tab = Tab(self, self.parent().profile(), parent=self).fromHtml('resources/pages/new_tab.html')
        self.insertTab(self.currentIndex() + 1, tab, 'New Tab')
        self.setCurrentIndex(self.indexOf(tab))

        QTimer.singleShot(300, self.startEditing)

    def newTab(self, start_editing=True):
        tab = Tab(self, self.parent().profile(), parent=self).fromHtml('resources/pages/new_tab.html')
        self.addTab(tab, 'New Tab')
        self.setCurrentIndex(self.indexOf(tab))

        if start_editing:
            QTimer.singleShot(300, self.startEditing)

    def newTabFromUrl(self, url: QUrl):
        tab = Tab(self, self.parent().profile(), url=url.toString(), parent=self)
        self.addTab(tab, '')
        self.setCurrentIndex(self.count() - 1)

    def updateTab(self):
        index = self.currentIndex()

        if index != -1:
            tab = self.currentTab()

            self.setTabText(index, (tab.browser().title()[:25] + '...') if len(tab.browser().title()) > 25 else tab.browser().title())

            self.setTabToolTip(index, tab.browser().title())
            self.setTabIcon(index, tab.browser().icon())

    def closeTab(self, index: int):
        tab = self.widget(index)

        if tab is not None:
            tab.browser().stopMedia()
            tab.browser().deleteLater()
            tab.deleteLater()

        self.removeTab(index)

        if self.count() == 0:
            self.parent().close()

    def currentTab(self) -> Tab:
        return self.widget(self.currentIndex())

    def passwordManager(self) -> PasswordsDialog:
        return self._passwords_dialog
