from src.imports import *
from src.gui.tab import Tab
from src.gui.widgets import PageTabWidget
from mp_software_stylesheets.styles import IBROWSECSS


class Ibrowse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ibrowse')
        self.setWindowIcon(QIcon('resources/icons/ibrowse_icon.svg'))
        self.resize(1000, 800)

        self.createUI()
        self.createActions()

    def createUI(self):
        self.tab_view = PageTabWidget(self)

        welcome_page = Tab(self.tab_view, parent=self)
        self.tab_view.addTab(welcome_page.fromHtml('resources/pages/startup.html'), 'Welcome')

        self.setCentralWidget(self.tab_view)

    def createActions(self):
        new_tab_action = QAction(self)
        new_tab_action.setShortcut(QKeySequence('Ctrl+N'))
        new_tab_action.triggered.connect(self.newTab)

        search_action = QAction(self)
        search_action.setShortcut(QKeySequence('Ctrl+Q'))
        search_action.triggered.connect(self.tab_view.currentWidget().searchBar().startEditing)

        back_action = QAction(self)
        back_action.setShortcut(QKeySequence('Ctrl+left'))
        back_action.triggered.connect(self.tab_view.currentWidget().browser().back)

        forward_action = QAction(self)
        forward_action.setShortcut(QKeySequence('Ctrl+right'))
        forward_action.triggered.connect(self.tab_view.currentWidget().browser().forward)

        reload_action = QAction(self)
        reload_action.setShortcut(QKeySequence('Ctrl+R'))
        reload_action.triggered.connect(self.tab_view.currentWidget().browser().reload)

        self.addAction(new_tab_action)
        self.addAction(search_action)
        self.addAction(back_action)
        self.addAction(forward_action)

    def newTab(self):
        self.tab_view.addTab(Tab(self.tab_view, 'google.com', parent=self), 'New Tab')
        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(IBROWSECSS)

    window = Ibrowse()
    window.show()

    # Crash handler
    def handle_exception(exctype, value, tb):
        QMessageBox.critical(window, 'Error:(', f'IBrowse encountered an error:\n\n{value}\n')
        sys.__excepthook__(exctype, value, tb)

    # Set the global exception hook
    sys.excepthook = handle_exception

    app.exec()

if __name__ == '__main__':
    main()