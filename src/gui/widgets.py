from src.imports import *


COMMANDS = ['/exit',
            '/close',
            '/help',
            '/welcome',
            ]


class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('searchBar')
        self.setPlaceholderText('Search...')
        self.installEventFilter(self)

        self._mouse_pressed = False
        self._first_focus = True

        self.updateCompleter()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self._mouse_pressed = True
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        super().focusInEvent(event)

        if self._first_focus:
            self._first_focus = False
            QTimer.singleShot(0, self.selectAll)
        elif self._mouse_pressed:
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
        items = COMMANDS

        for url, name in ibrowse.bookmarks().items():
            items.append(url)

        self._completer = QCompleter(items)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(self._completer)


class QuickSearchBar(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Popup)
        self.setObjectName('blankWidget')

        self.createUI()

    def exec(self, pos=None):
        if pos:
            super().exec(pos)
            return

        parent_center = self.parent().rect().center()
        global_center = self.parent().mapToGlobal(parent_center)
        target_width = 400
        target_height = 50

        start_rect = QRect(
            global_center.x(),
            global_center.y(),
            1,
            1
        )
        end_rect = QRect(
            global_center.x() - target_width // 2,
            global_center.y() - target_height // 2,
            target_width,
            target_height
        )

        self.setGeometry(start_rect)
        self.container.setFixedSize(target_width, target_height)
        self.updateCompleter()
        self.startEditing()

        self.show()

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def createUI(self):
        self.container = QWidget(self)
        self.container.setLayout(QVBoxLayout())

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search...')
        self.search_box.setFixedSize(375, 30)
        self.search_box.returnPressed.connect(lambda: self.search(self.search_box.text()))
        self.container.layout().addWidget(self.search_box, alignment=Qt.AlignmentFlag.AlignCenter)

        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(self.container)

        self.addAction(widget_action)

    def search(self, text: str):
        self.parent().search(text)
        self.animateClose()

    def startEditing(self):
        self.search_box.setFocus()
        self.search_box.selectAll()

    def setUrl(self, url):
        self.search_box.setText(url)

    def updateCompleter(self):
        items = COMMANDS

        for url, name in ibrowse.bookmarks().items():
            items.append(url)

        self._completer = QCompleter(items)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.search_box.setCompleter(self._completer)

    def animateClose(self):
        current_geometry = self.geometry()
        end_rect = QRect(
            current_geometry.center().x(),
            current_geometry.center().y(),
            1,
            1
        )

        self.close_animation = QPropertyAnimation(self, b'geometry')
        self.close_animation.setDuration(200)
        self.close_animation.setStartValue(current_geometry)
        self.close_animation.setEndValue(end_rect)
        self.close_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.close_animation.finished.connect(self.close)
        self.close_animation.start()


class EngineTypeCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

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


class ContextMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(150, 30)

        self._animation_enabled = False

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        else:
            m = ContextMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m

    def exec(self, pos=None):
        if pos and self.animationEnabled():
            screen_rect = QApplication.primaryScreen().availableGeometry()

            menu_size = self.sizeHint()

            if pos.x() + menu_size.width() > screen_rect.right():
                pos.setX(screen_rect.right() - menu_size.width())

            if pos.y() + menu_size.height() > screen_rect.bottom():
                pos.setY(screen_rect.bottom() - menu_size.height())

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
