from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QWidget, QHBoxLayout, QLabel


class StringInput(QWidget):
    def __init__(self, title: str,
                 layout: QVBoxLayout | QHBoxLayout,
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
