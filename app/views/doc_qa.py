from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QSplitter,
)
from PySide6.QtCore import Qt, QTimer
from app.rag.utils import DocumentViewer
from app.rag.utils import ChatInterface


class DocumentQAView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Question-Answering")

        self.doc = {
            "path": "",
            "extension": ""
        }

        self.view_layout = QVBoxLayout()

        self.upload_button = QPushButton("Upload PDF")
        self.upload_button.clicked.connect(self.upload_document)
        self.view_layout.addWidget(self.upload_button)

        self.splitter = QSplitter(Qt.Horizontal)
        self.view_layout.addWidget(self.splitter)

        self.viewer = DocumentViewer()
        self.chat = ChatInterface()

        self.splitter.addWidget(self.viewer)
        self.splitter.addWidget(self.chat)
        self.splitter.setHandleWidth(0)
        self.splitter.setChildrenCollapsible(False)

        QTimer.singleShot(0, self.set_splitter_half)

        self.setLayout(self.view_layout)

    def upload_document(self):
        filters = "PDF files (*.pdf)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Select document", "", filters)

        if file_path:
            self.doc["path"] = file_path
            self.doc["extension"] = file_path.split(".")[-1]

            self.viewer.load_pdf(file_path)

            print(f"[INFO] PDF widget added.")

    def set_splitter_half(self):
        total_width = self.splitter.width()

        self.splitter.setSizes([total_width, total_width])

        self.chat.setMinimumWidth(total_width)
        self.chat.setMaximumWidth(total_width)