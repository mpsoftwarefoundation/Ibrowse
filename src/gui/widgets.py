from src.imports import *
import ibrowse


class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('searchBar')
        self.setPlaceholderText('Search...')
        self.installEventFilter(self)

        self._mouse_pressed = False

        self.updateCompleter()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self._mouse_pressed = True
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        super().focusInEvent(event)

        if self._mouse_pressed:
            self._mouse_pressed = False
            QTimer.singleShot(0, self.selectAll)

    def startEditing(self):
        self.setFocus()
        self.selectAll()

    def setUrl(self, url: QUrl):
        self.blockSignals(True)
        self.setText(url.toString())
        self.blockSignals(False)

    def updateCompleter(self):
        items = ['/exit', '/help']

        for url, name in ibrowse.bookmarks().items():
            items.append(url)

        self._completer = QCompleter(items)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(self._completer)


class EngineTypeCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._engine_types = {
            'Google': 'google.com/search?q=',
            'DuckDuckGo': 'duckduckgo.com/?q=',
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


class PageTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.parent().close()
            return

        self.removeTab(index)


class ContextMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setObjectName('customMenu')
        self.setMinimumSize(150, 30)

        self.radius = 10
        self._animation_enabled = False

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        else:
            m = ContextMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m

    def resizeEvent(self, event):
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
        path.addRoundedRect(rect, self.radius, self.radius)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))  # Set the color
        self.setPalette(palette)

        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region)

    def exec(self, pos=None):
        if pos and self.animationEnabled():
            screen_rect = QApplication.primaryScreen().availableGeometry()

            # Get the menu's size (this is available after it's created)
            menu_size = self.sizeHint()

            # Check if the menu would go off the right or bottom of the screen
            if pos.x() + menu_size.width() > screen_rect.right():
                pos.setX(screen_rect.right() - menu_size.width())
            if pos.y() + menu_size.height() > screen_rect.bottom():
                pos.setY(screen_rect.bottom() - menu_size.height())

            # If animation is enabled
            self.animation = QPropertyAnimation(self, b'pos')
            self.animation.setDuration(100)
            self.animation.setStartValue(QPoint(pos.x(), pos.y() + 10))
            self.animation.setEndValue(pos)

            self.animation.start()

        super().exec(pos)

    def setAnimationEnabled(self, enabled: bool):
        self._animation_enabled = enabled

    def animationEnabled(self):
        return self._animation_enabled


class StringInput(QWidget):
    def __init__(self, title: str,
                 layout: QVBoxLayout or QHBoxLayout,
                 placeholder: str = '',
                 on_change=None,
                 parent=None):
        super().__init__(parent)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._title = title
        self._placeholder = placeholder
        self._default_value = ''
        self._on_change = on_change

        self._create()

    def _create(self):
        self._label = QLabel(self._title, self)
        self._input = QLineEdit(self)
        self._input.setPlaceholderText(self._placeholder)
        self._input.setText(self._default_value)

        if self._on_change:
            self._input.textChanged.connect(self._on_change)

        self.layout().addWidget(self._label)
        self.layout().addWidget(self._input)

    def _update(self):
        self._label.setText(self._title)
        self._input.setPlaceholderText(self._placeholder)
        self._input.setText(self._default_value)

    def setTitle(self, title: str):
        self._title = title

        self._update()

    def setPlaceholder(self, text: str):
        self._placeholder = text

        self._update()

    def setDefaultValue(self, value: str):
        self._default_value = value

        self._update()

    def title(self) -> str:
        return self._title

    def placeholder(self) -> str:
        return self._placeholder

    def defaultValue(self) -> str:
        return self._default_value

    def value(self) -> str:
        return self._input.text()
