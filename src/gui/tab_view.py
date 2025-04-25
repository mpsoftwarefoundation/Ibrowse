from src.imports import *
from src.gui.tab import Tab


class PageTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabBar().setUsesScrollButtons(False)

        self.tabCloseRequested.connect(self.closeTab)

        self.createUI()

    def createUI(self):
        add_tab_btn = QToolButton(self)
        add_tab_btn.setObjectName('searchBarButton')
        add_tab_btn.setText('+')
        add_tab_btn.setAutoRaise(True)
        add_tab_btn.clicked.connect(self.newTab)

        self.setCornerWidget(add_tab_btn, Qt.Corner.TopRightCorner)

    def startEditing(self):
        self.currentWidget().searchBar().startEditing()

    def forward(self):
        self.currentWidget().browser().forward()

    def back(self):
        self.currentWidget().browser().back()

    def newTab(self):
        self.addTab(Tab(self, 'google.com', parent=self), 'New Tab')
        self.setCurrentIndex(self.count() - 1)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.parent().close()
            return

        self.removeTab(index)
        self.update()
