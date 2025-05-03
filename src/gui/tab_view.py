from src.imports import *
from src.gui.tab import Tab


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self.tabBarDoubleClicked.connect(self.newTab)
        self.tabCloseRequested.connect(self.closeTab)

        self.createUI()
        self.createActions()

    def createUI(self):
        add_tab_btn = QToolButton(self)
        add_tab_btn.setObjectName('searchBarButton')
        add_tab_btn.setText('+')
        add_tab_btn.setAutoRaise(True)
        add_tab_btn.setToolTip('Create a new tab')
        add_tab_btn.clicked.connect(self.newTab)

        self.setCornerWidget(add_tab_btn, Qt.Corner.TopRightCorner)

    def createActions(self):
        new_tab_action = self.addAction('New Tab')
        new_tab_action.setShortcut(QKeySequence('Ctrl+N'))
        new_tab_action.triggered.connect(self.newTab)

        new_window_action = self.addAction('New Window')
        new_window_action.setShortcut(QKeySequence('Ctrl+Shift+N'))
        new_window_action.triggered.connect(self.parent().newWindow)

        close_tab_action = self.addAction('Close Tab')
        close_tab_action.setShortcut(QKeySequence('Ctrl+E'))
        close_tab_action.triggered.connect(lambda: self.currentWidget().close())

        password_manager_action = self.addAction('Password Manager')
        password_manager_action.setShortcut(QKeySequence('Ctrl+K'))
        password_manager_action.triggered.connect(lambda: self.currentWidget().passwordManager().show())

        bookmark_tab_action = self.addAction('Bookmark This Tab')
        bookmark_tab_action.setShortcut(QKeySequence('Ctrl+B'))
        bookmark_tab_action.triggered.connect(lambda: self.currentWidget().bookmark())

        quick_edit_action = self.addAction('Quick Edit')
        quick_edit_action.setShortcut(QKeySequence('Ctrl+Q'))
        quick_edit_action.triggered.connect(lambda: self.currentWidget().quickSearch())

        self.addAction(new_tab_action)
        self.addAction(new_window_action)
        self.addAction(close_tab_action)
        self.addAction(password_manager_action)
        self.addAction(bookmark_tab_action)
        self.addAction(quick_edit_action)

    def startEditing(self):
        self.currentWidget().searchBar().startEditing()

    def forward(self):
        self.currentWidget().browser().forward()

    def back(self):
        self.currentWidget().browser().back()

    def newTab(self):
        tab = Tab(self, self.parent().profile(), parent=self).fromHtml('resources/pages/new_tab.html')
        self.insertTab(self.currentIndex() + 1, tab, 'New Tab')
        self.setCurrentIndex(self.indexOf(tab))

        QTimer.singleShot(300, self.startEditing)

    def newTabFromUrl(self, url: QUrl):
        tab = Tab(self, self.parent().profile(), url=url.toString(), parent=self)
        self.addTab(tab, '')
        self.setCurrentIndex(self.count() - 1)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.removeTab(index)
            self.parent().close()

        self.removeTab(index)
        self.update()
