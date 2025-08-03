from PySide6.QtWidgets import (
    QTabWidget,
    QMainWindow,
)

from .views.image_converter import ImageExportView
from .views.doc_qa import DocumentQAView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DocuWizard")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_tabs()

    def init_tabs(self):
        image_export_tab = ImageExportView()
        self.tabs.addTab(image_export_tab, "Image export")

        qa_tab = DocumentQAView()
        self.tabs.addTab(qa_tab, "QA with LLM")