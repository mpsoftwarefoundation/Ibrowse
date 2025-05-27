from PyQt6.QtWidgets import QComboBox


class EngineSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)

        self._engine_types = {
            'Google': 'google.com/search?q=',
            'DuckDuckGo': 'duckduckgo.com/?q=',
            'YouTube': 'youtube.com/results?search_query=',
            'Bing': 'bing.com/search?q=',
            'Yahoo': 'search.yahoo.com/search?p=',
            'Startpage': 'startpage.com/sp/search?query=',
            'Ecosia': 'ecosia.org/search?q=',
            'Qwant': 'qwant.com/?q=',
            'Yandex': 'yandex.com/search/?text=',
            'Brave': 'search.brave.com/search?q=',
            'Mojeek': 'mojeek.com/search?q='
        }
        self._engine_type = 'google.com/search?q='

        self.createTypes()

    def createTypes(self):
        for k, v in self._engine_types.items():
            self.addItem(k, v)
