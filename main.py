import sys

from src.gui.widgets import PageTabWidget
from src.imports import *
from src.gui.tab import Tab
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
        self.tab_view.addTab(Tab(self.tab_view, parent=self), 'Welcome')

        self.setCentralWidget(self.tab_view)

    def createActions(self):
        new_tab_action = QAction(self)
        new_tab_action.setShortcut(QKeySequence('Ctrl+N'))
        new_tab_action.triggered.connect(self.newTab)
        self.addAction(new_tab_action)

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