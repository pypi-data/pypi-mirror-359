from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
import sys
class DriizzyyuiGUI(QWidget):
    def __init__(self, client_cls):
        super().__init__()
        self.client_cls = client_cls
        self.client = None
        self.channels = []
        self.setWindowTitle("Driizzyyui Selfbot GUI")
        self._build_ui()
    def _build_ui(self):
        self.layout = QVBoxLayout()
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Discord User Token")
        self.layout.addWidget(self.token_input)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        self.layout.addWidget(self.login_btn)
        self.user_info = QLabel("Not logged in.")
        self.layout.addWidget(self.user_info)
        self.channel_select = QComboBox()
        self.channel_select.setEnabled(False)
        self.layout.addWidget(self.channel_select)
        msg_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Type a message")
        self.msg_input.setEnabled(False)
        self.send_btn = QPushButton("Send")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.handle_send)
        msg_layout.addWidget(self.msg_input)
        msg_layout.addWidget(self.send_btn)
        self.layout.addLayout(msg_layout)
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.layout.addWidget(self.chat_box)
        self.setLayout(self.layout)
        self.channel_select.currentIndexChanged.connect(self.load_channel_messages)
    def handle_login(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Error", "Please enter a token.")
            return
        try:
            self.client = self.client_cls(token)
            user = self.client.fetch_user()
            self.user_info.setText(f"Logged in as: {user['username']}#{user['discriminator']}")
            self.channels = self.client.fetch_channels()
            self.channel_select.clear()
            for ch in self.channels:
                name = ch.get("name", f"DM: {ch.get('recipients',[{}])[0].get('username','Unknown')}")
                self.channel_select.addItem(f"{name} ({ch['id']})", ch['id'])
            self.channel_select.setEnabled(True)
            self.msg_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.load_channel_messages()
        except Exception as e:
            QMessageBox.critical(self, "Login failed", str(e))
    def load_channel_messages(self):
        if not self.client or not self.channels:
            return
        ch_index = self.channel_select.currentIndex()
        if ch_index == -1:
            return
        channel_id = self.channel_select.itemData(ch_index)
        try:
            messages = self.client.fetch_messages(channel_id, limit=20)
            self.chat_box.clear()
            for msg in reversed(messages):
                author = msg["author"]["username"]
                content = msg["content"]
                self.chat_box.append(f"<b>{author}:</b> {content}")
        except Exception as e:
            self.chat_box.setText(f"Failed to load messages: {e}")
    def handle_send(self):
        ch_index = self.channel_select.currentIndex()
        if ch_index == -1:
            QMessageBox.warning(self, "Error", "No channel selected.")
            return
        channel_id = self.channel_select.itemData(ch_index)
        content = self.msg_input.text().strip()
        if not content:
            return
        try:
            self.client.send_message(channel_id, content)
            self.load_channel_messages()
            self.msg_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Send failed", str(e))
    def show(self):
        super().show()
        if not QApplication.instance():
            app = QApplication(sys.argv)
            app.exec_()