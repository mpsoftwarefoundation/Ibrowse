from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QTabWidget
from src.gui.tab import Tab


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        switch_tab_next_action = self.addAction('Switch To Next Tab')
        switch_tab_next_action.setShortcut(QKeySequence('Ctrl+right'))
        switch_tab_next_action.triggered.connect(self.nextTab)

        switch_tab_prev_action = self.addAction('Switch To Previous Tab')
        switch_tab_prev_action.setShortcut(QKeySequence('Ctrl+left'))
        switch_tab_prev_action.triggered.connect(self.previousTab)

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

    def nextTab(self):
        self.setCurrentIndex((self.currentIndex() + 1) % self.count())

    def previousTab(self):
        self.setCurrentIndex((self.currentIndex() - 1) % self.count())

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
        self.removeTab(index)

        if self.count() == 0:
            self.parent().close()

    def currentTab(self) -> Tab:
        return self.widget(self.currentIndex())
