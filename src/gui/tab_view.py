from src.imports import *
from src.gui.tab import Tab


class PageTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabBar().setUsesScrollButtons(False)

        self.tabBarDoubleClicked.connect(self.newTab)
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
        tab = Tab(self, self.parent().profile(), parent=self).fromHtml('resources/pages/new_tab.html')
        self.addTab(tab, 'New Tab')
        self.setCurrentIndex(self.count() - 1)

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
