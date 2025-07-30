from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont
class DriizzyyuiChatMessageWidget(QWidget):
    def __init__(self, username, content, parent=None):
        super().__init__(parent)
        self.username_label = QLabel(username)
        self.username_label.setFont(QFont("Arial", weight=QFont.Bold))
        self.content_label = QLabel(content)
        self.content_label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.content_label)
        self.setLayout(layout)