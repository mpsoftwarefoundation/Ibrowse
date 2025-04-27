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

    def showEvent(self, event):
        self.createList()

        super().showEvent(event)

    def createUI(self):
        container = QWidget()
        container.setObjectName('searchBarButton')
        container.setLayout(QHBoxLayout())
        container.layout().setContentsMargins(0, 0, 0, 0)

        add_password_btn = QPushButton('+')
        add_password_btn.setObjectName('searchBarButton')
        add_password_btn.setFixedWidth(25)
        add_password_btn.clicked.connect(self.addPassword)
        import_from_chrome_btn = QPushButton('📁')
        import_from_chrome_btn.setObjectName('searchBarButton')
        import_from_chrome_btn.clicked.connect(self.importFromChrome)
        self.search_box = QLineEdit()
        self.search_box.setFixedHeight(30)
        self.search_box.setPlaceholderText('Search Passwords...')
        self.search_box.textChanged.connect(self.searchPasswords)

        container.layout().addWidget(add_password_btn)
        container.layout().addWidget(import_from_chrome_btn)
        container.layout().addWidget(self.search_box)

        self.password_list = QListWidget(self)
        self.password_list.setObjectName('listWidget')
        self.password_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.password_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.password_list.setWordWrap(True)
        self.password_list.setUniformItemSizes(True)
        self.password_list.itemDoubleClicked.connect(self.editPassword)

        self.layout().addWidget(container)
        self.layout().addSpacing(10)
        self.layout().addWidget(self.password_list)

    def createList(self):
        self.password_list.clear()
        self.items = []

        for url, value in ibrowse.passwords().items():
            item = QListWidgetItem(url)
            item.url = url
            item.username = value[0]
            item.password = value[1]

            container = QWidget()
            container.setLayout(QHBoxLayout())
            container.layout().setContentsMargins(0, 0, 0, 0)

            edit_password_btn = QPushButton('✏️')
            edit_password_btn.setFixedWidth(20)
            edit_password_btn.setToolTip('Edit saved password')
            edit_password_btn.clicked.connect(lambda _, i=item: self.editPassword(i))
            copy_username_btn = QPushButton('👤')
            copy_username_btn.setFixedWidth(20)
            copy_username_btn.setToolTip('Copy username')
            copy_username_btn.clicked.connect(lambda _, i=item: QApplication.clipboard().setText(i.username))
            copy_password_btn = QPushButton('🔑')
            copy_password_btn.setFixedWidth(20)
            copy_password_btn.setToolTip('Copy password')
            copy_password_btn.clicked.connect(lambda _, i=item: QApplication.clipboard().setText(i.password))
            delete_btn = QPushButton('✕')
            delete_btn.setFixedWidth(20)
            delete_btn.setToolTip('Delete password')
            delete_btn.clicked.connect(lambda _, i=item: self.deletePassword(i))
            container.layout().addStretch()
            container.layout().addWidget(edit_password_btn)
            container.layout().addWidget(copy_username_btn)
            container.layout().addWidget(copy_password_btn)
            container.layout().addWidget(delete_btn)

            self.password_list.addItem(item)
            self.password_list.setItemWidget(item, container)

            self.items.append((item, url))

        if self.search_box.text():
            self.searchPasswords(self.search_box.text())
            return

    def addPassword(self):
        dialog = CreatePasswordDialog(self)
        dialog.exec()

        self.createList()

    def deletePassword(self, item: QListWidgetItem):
        ibrowse.remove_password(item.url)

        self.password_list.takeItem(self.password_list.row(item))

    def editPassword(self, item: QListWidgetItem):
        dialog = CreatePasswordDialog(self)
        dialog.setWindowTitle('Edit Password')
        dialog.url_input.setDefaultValue(item.url)
        dialog.username_input.setDefaultValue(item.username)
        dialog.password_input.setDefaultValue(item.password)

        old = dialog.url_input.value()

        dialog.exec()

        if dialog.url_input.value() != old:
            self.password_list.takeItem(self.password_list.row(item))

        self.createList()

    def searchPasswords(self, text: str):
        text = text.lower()

        for item, key in self.items:
            is_match = text in key.lower()
            item.setHidden(not is_match)

    def importFromChrome(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            'Open Chrome Password File',
            '',
            'Comma Separated Value (*.csv) files'
        )

        if file:
            with open(file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    url = row.get('origin', '') or row.get('origin_url', '') or row.get('url', '')
                    username = row.get('username', '') or row.get('username_value', '')
                    password = row.get('password', '') or row.get('password_value', '')

                    if url and username and password:
                        ibrowse.add_password(url, username, password)

            self.createList()


class CreatePasswordDialog(QDialog):
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
        if not self.url_input.value() or not self.username_input.value() or not self.password_input.value():
            raise Exception('Input values cannot be empty')

        ibrowse.add_password(self.url_input.value(), self.username_input.value(), self.password_input.value())
        self.close()


class CreateBookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Create New Bookmark')
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
        if not self.url_input.value() or not self.input.value():
            raise Exception('Input values cannot be empty')

        ibrowse.add_bookmark(self.url_input.value(), self.input.value())
        self.close()
