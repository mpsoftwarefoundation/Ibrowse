from src.imports import *
from src.gui.widgets import StringInput


class PasswordsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Password Manager')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setLayout(QVBoxLayout())
        self.resize(500, 300)

        self.createUI()
        self.createList()

    def createUI(self):
        add_password_btn = QPushButton('+')
        add_password_btn.setFixedWidth(25)
        add_password_btn.clicked.connect(self.addPassword)

        search_box = QLineEdit()
        search_box.setPlaceholderText('Search Passwords...')
        search_box.textChanged.connect(self.searchPasswords)

        self.password_list = QListWidget(self)
        self.password_list.setObjectName('listWidget')
        self.password_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        self.layout().addWidget(add_password_btn)
        self.layout().addWidget(search_box)
        self.layout().addSpacing(10)
        self.layout().addWidget(self.password_list)

    def createList(self):
        self.password_list.clear()
        self.items = []

        for url, value in ibrowse.passwords().items():
            item = QListWidgetItem(url)
            item.username = value[0]
            item.password = value[1]

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            copy_username_btn = QPushButton('[U]')
            copy_username_btn.setFixedWidth(20)
            copy_username_btn.setToolTip('Copy username')
            copy_username_btn.clicked.connect(lambda _, i=item: QApplication.clipboard().setText(i.username))
            copy_password_btn = QPushButton('[P]')
            copy_password_btn.setFixedWidth(20)
            copy_password_btn.setToolTip('Copy password')
            copy_password_btn.clicked.connect(lambda _, i=item: QApplication.clipboard().setText(i.password))
            delete_btn = QPushButton('✕')
            delete_btn.setFixedWidth(20)
            delete_btn.setToolTip('Delete password')
            delete_btn.clicked.connect(lambda _, i=item: self.deletePassword(i))
            container.layout().addStretch()
            container.layout().addWidget(copy_username_btn)
            container.layout().addWidget(copy_password_btn)
            container.layout().addWidget(delete_btn)

            self.password_list.addItem(item)
            self.password_list.setItemWidget(item, container)

            self.items.append((item, url))

    def addPassword(self):
        dialog = CreateNewPasswordDialog(self)
        dialog.exec()

        self.createList()

    def deletePassword(self, item: QListWidgetItem):
        ibrowse.remove_password(item.text())

        self.createList()

    def searchPasswords(self, text: str):
        text = text.lower()

        for item, key in self.items:
            is_match = text in key.lower()
            item.setHidden(not is_match)


class CreateNewPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Create New Password')
        self.setLayout(QVBoxLayout())
        self.resize(400, 300)

        self.createUI()

    def createUI(self):
        self.url_input = StringInput(title='URL:', layout=QVBoxLayout(), placeholder='Enter a valid URL')
        self.username_input = StringInput(title='Username:', layout=QVBoxLayout(), placeholder='Enter the username')
        self.password_input = StringInput(title='Password:', layout=QVBoxLayout(), placeholder='Enter the password')
        self.password_input._input.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.ButtonRole.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.url_input)
        self.layout().addSpacing(10)
        self.layout().addWidget(self.username_input)
        self.layout().addSpacing(10)
        self.layout().addWidget(self.password_input)
        self.layout().addStretch()
        self.layout().addWidget(self.button_group)

    def accept(self):
        ibrowse.add_password(self.url_input.value(), self.username_input.value(), self.password_input.value())

        self.close()


class GetBookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Create New Value')
        self.setLayout(QVBoxLayout())
        self.resize(400, 300)

        self.createUI()

    def createUI(self):
        self.url_input = StringInput(title='URL:', layout=QVBoxLayout(), placeholder='Enter a valid URL')
        self.input = StringInput(title='Bookmark Name:', layout=QVBoxLayout(), placeholder='Enter a bookmark name')

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.ButtonRole.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.url_input)
        self.layout().addSpacing(10)
        self.layout().addWidget(self.input)
        self.layout().addStretch()
        self.layout().addWidget(self.button_group)

    def accept(self):
        ibrowse.add_bookmark(self.url_input.value(), self.input.value())

        self.close()
