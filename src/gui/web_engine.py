from src.imports import *


class WebEnginePage(QWebEnginePage):
    def __init__(self, profile, tab_view):
        super().__init__(profile, tab_view)
        self.tab_view = tab_view


class WebEngineView(QWebEngineView):
    def __init__(self, page: WebEnginePage, tab_view, parent=None):
        super().__init__(parent)
        self.setPage(page)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.tab_view = tab_view

        self.customContextMenuRequested.connect(self.showMenu)

    def showMenu(self, pos: QPoint):
        menu = self.createStandardContextMenu()
        menu.removeAction(self.pageAction(QWebEnginePage.WebAction.DownloadLinkToDisk))
        menu.removeAction(self.pageAction(QWebEnginePage.WebAction.InspectElement))
        menu.removeAction(self.pageAction(QWebEnginePage.WebAction.ViewSource))
        data = self.lastContextMenuRequest()

        menu.addSeparator()

        print_action = menu.addAction('Print...')
        print_action.triggered.connect(self.printPage)

        if not hasattr(self, 'connected_actions'):
            self.connected_actions = True
            self.pageAction(
                QWebEnginePage.WebAction.SavePage
            ).triggered.connect(self.savePage)
            self.pageAction(
                QWebEnginePage.WebAction.DownloadImageToDisk
            ).triggered.connect(lambda: self.saveImage(data))
            self.pageAction(
                QWebEnginePage.WebAction.OpenLinkInNewTab
            ).triggered.connect(lambda: self.openLinkInNewTab(data))
            self.pageAction(
                QWebEnginePage.WebAction.OpenLinkInNewWindow
            ).triggered.connect(lambda: self.openLinkInNewWindow(data))
            self.pageAction(
                QWebEnginePage.WebAction.CopyImageToClipboard
            ).triggered.connect(lambda: self.copyImage(data))
            self.pageAction(
                QWebEnginePage.WebAction.CopyImageUrlToClipboard
            ).triggered.connect(lambda: self.copyImageUrl(data))

        menu.exec(self.mapToGlobal(pos))

    def savePage(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  'Save Page',
                                                  self.url().toString(),
                                                  'HTML files (*.html *.htm)')

        if filename and filename.endswith(('.html', '.htm')):
            ibrowse.write_html(filename, self.page().toHtml(print))

    def saveImage(self, data: QWebEngineContextMenuRequest):
        response = requests.get(data.mediaUrl().toString())

        if response.status_code == 200:
            url_filename = data.mediaUrl().toString().split('/')[-1]
            filename, _ = QFileDialog.getSaveFileName(self,
                                                      'Save Image As',
                                                      url_filename,
                                                      'All files (*.)')

            if filename and '.' in filename:
                ibrowse.write_bytes(filename, response.content)

    def copyImage(self, data: QWebEngineContextMenuRequest):
        image_url = data.mediaUrl().toString()
        response = requests.get(image_url)

        if response.status_code == 200:
            image = QImage.fromData(response.content)

            if not image.isNull():
                clipboard = QApplication.clipboard()
                clipboard.setImage(image)

    def copyImageUrl(self, data: QWebEngineContextMenuRequest):
        image_url = data.mediaUrl().toString()

        clipboard = QApplication.clipboard()
        clipboard.setText(image_url)

    def printPage(self, data: QWebEngineContextMenuRequest):
        pass

    def openLinkInNewTab(self, data: QWebEngineContextMenuRequest):
        self.tab_view.newTabFromUrl(data.linkUrl())

    def openLinkInNewWindow(self, data: QWebEngineContextMenuRequest):
        self.tab_view.parent().newWindowFromUrl(data.linkUrl())
