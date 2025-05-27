from PyQt6.QtCore import QTimer, QMimeData, QUrl, Qt
from PyQt6.QtGui import QDragLeaveEvent, QDropEvent, QDragEnterEvent, QDragMoveEvent, QKeySequence
from PyQt6.QtWidgets import QTabBar, QTabWidget, QWidget
from src.gui.tab import Tab


class TabBar(QTabBar):
    def __init__(self, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self._tab_view = tab_view

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

        quick_edit_action = self.addAction('Quick Edit')
        quick_edit_action.setShortcut(QKeySequence('Ctrl+Q'))
        quick_edit_action.triggered.connect(lambda: self.currentTab().quickSearch())

        self.addAction(new_tab_action)
        self.addAction(new_window_action)
        self.addAction(close_tab_action)
        self.addAction(password_manager_action)
        self.addAction(bookmark_tab_action)
        self.addAction(quick_edit_action)

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
