import os
import markdown

from PySide6.QtCore import QUrl
from PySide6.QtGui import QTextCursor

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QSizePolicy,
    QTextEdit, QPushButton
)

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

from .llm_router import prepare_doc_retrieval, query_llm


class DocumentViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.file_path = None

        self.viewer_layout = QVBoxLayout(self)
        self.pdf_view = QWebEngineView()
        self.pdf_view.settings().setAttribute(
            self.pdf_view.settings().WebAttribute.PluginsEnabled, True
        )
        self.pdf_view.settings().setAttribute(
            self.pdf_view.settings().WebAttribute.PdfViewerEnabled, True
        )

        self.path_label = QLabel("")
        self.path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.viewer_layout.addWidget(self.path_label)

        self.load_pdf("")

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search text in PDF...")
        self.search_bar.returnPressed.connect(self.run_search)

        self.viewer_layout.addWidget(self.search_bar)
        self.viewer_layout.addWidget(self.pdf_view)

    def load_pdf(self, file_path: str):
        if os.path.exists(file_path):
            self.file_path = file_path
            print(f"[INFO] PDF file exists. Loading....")
            pdf_url = QUrl.fromLocalFile(self.file_path)
            pdf_url.setFragment("zoom=page-width")
            self.pdf_view.setUrl(pdf_url)
            self.path_label.setText(self.file_path)
            print(f"[INFO] PDF file loaded.")

            prepare_doc_retrieval(self.file_path)

        else:
            self.path_label.setText("PDF file not found.")
            self.pdf_view.setHtml("<h2 style='color:red; text-align:center;'>File not found.</h2>")

    def run_search(self):
        query = self.search_bar.text().strip()
        if query:
            self.pdf_view.page().findText(query, QWebEnginePage.FindFlag.FindCaseSensitively)



class ChatInterface(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.title = QLabel("Chat with DocuWizard Assistant")
        self.title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 6px;")

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                border: none;
                font-size: 14px;
                padding: 4px;
                background: transparent;
            }
        """)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your question here...")
        self.input_field.returnPressed.connect(self.handle_user_input)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 6px;
                font-size: 14px;
            }
        """)

        self.send_button = QPushButton("Send")
        self.send_button.setFixedHeight(36)
        self.send_button.clicked.connect(self.handle_user_input)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        layout.addWidget(self.title)
        layout.addWidget(self.chat_area)
        layout.addLayout(input_layout)

    def append_message(self, text: str, sender: str):
        bg_color = "#d0e7ff" if sender == "user" else "#d0ffd6"
        align = "right" if sender == "user" else "left"
        name = "You" if sender == "user" else "Assistant"

        html_body = markdown.markdown(text, extensions=["extra", "sane_lists"])

        bubble_html = f"""
        <table width="100%" cellspacing="0" cellpadding="4">
        <tr>
            <td align="{align}">
                <div style="
                    background-color: {bg_color};
                    color: #000;
                    border-radius: 10px;
                    padding: 8px 12px;
                    display: inline-block;
                    max-width: 60%;
                    font-size: 14px;">
                    <b>{name}:</b> {html_body}
                </div>
            </td>
        </tr>
        </table>
        """

        self.chat_area.insertHtml(bubble_html)
        self.chat_area.insertHtml("<br>")
        self.chat_area.moveCursor(QTextCursor.End)

    def handle_user_input(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return

        self.append_message(user_text, sender="user")
        self.input_field.clear()

        response = query_llm(user_text, "online")
        self.append_message(response, sender="assistant")