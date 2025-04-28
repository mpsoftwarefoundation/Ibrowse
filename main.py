from src.imports import *
from src.gui.tab import Tab
from src.gui.tab_view import PageTabWidget
from mp_software_stylesheets.styles import IBROWSECSS


class Ibrowse(QMainWindow):
    def __init__(self, profile=None):
        super().__init__()
        self.setWindowTitle('Ibrowse')
        self.setWindowIcon(QIcon('resources/icons/ibrowse_icon.svg'))
        self.resize(1000, 800)

        if profile:
            self._profile = profile

        else:
            self._profile = QWebEngineProfile('PersistentProfile', self)
            self._profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
            self._profile.setCachePath(ibrowse.cache_dir())
            self._profile.setPersistentStoragePath(ibrowse.cache_dir())

        self.createUI()

    def closeEvent(self, event):
        if self.tab_view.count() > 0:
            tabs = []

            for i in range(self.tab_view.count()):
                tab = self.tab_view.widget(i)
                tabs.append(tab.activeUrl().toString())

            ibrowse.set_previous_tabs(tabs)
            ibrowse.set_preferred_browser(self.tab_view.currentWidget().engineCombo().currentText())

        else:
            ibrowse.set_previous_tabs([])

        super().closeEvent(event)

    def createUI(self):
        self.tab_view = PageTabWidget(self)

        self.setCentralWidget(self.tab_view)

    def loadTabs(self):
        if len(ibrowse.previous_tabs()) > 0:
            for url in ibrowse.previous_tabs():
                if not 'https' in url:
                    break

                tab = Tab(self.tab_view, self._profile, url=url, parent=self)
                self.tab_view.addTab(tab, '')

            return

        self.tab_view.addTab(
            Tab(self.tab_view, self._profile, parent=self).fromHtml('resources/pages/startup.html'),
            'Welcome'
        )

    def loadDefaultTab(self):
        self.tab_view.addTab(
            Tab(self.tab_view, self._profile, parent=self).fromHtml('resources/pages/startup.html'),
            'Welcome'
        )

    def openFromArg(self, arg: str):
        if os.path.exists(arg):
            tab = Tab(self.tab_view, self._profile, parent=self).fromHtml(arg)

            self.tab_view.addTab(tab, 'File')
            self.tab_view.setCurrentWidget(tab)

        else:
            tab = Tab(self.tab_view, self._profile, url=arg, parent=self)

            self.tab_view.addTab(tab, '')
            self.tab_view.setCurrentWidget(tab)

    def newWindow(self):
        window = Ibrowse(self._profile)
        window.show()
        window.loadDefaultTab()

        QTimer.singleShot(300, window.tab_view.startEditing)

        self.window = window

    def newWindowFromUrl(self, url: QUrl):
        window = Ibrowse(self._profile)
        window.show()
        window.tab_view.newTabFromUrl(url)

        self.window = window

    def profile(self):
        return self._profile


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(IBROWSECSS)

    window = Ibrowse()
    window.show()

    app.processEvents()

    window.loadTabs()

    if len(sys.argv) > 1:
        window.openFromArg(sys.argv[1])

    # Crash handler
    def handle_exception(exctype, value, tb):
        QMessageBox.critical(window, 'Error:(', f'Ibrowse encountered an error:\n\n{value}\n')
        sys.__excepthook__(exctype, value, tb)

    # Set the global exception hook
    sys.excepthook = handle_exception

    sys.exit(app.exec())

if __name__ == '__main__':
    main()