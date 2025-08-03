global_style = """
    QWidget {
        background-color: #1e1e1e;
        color: #f0f0f0;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
    }

    QPushButton {
        background-color: #0078d7;
        color: white;
        padding: 8px 14px;
        border-radius: 6px;
    }

    QPushButton:hover {
        background-color: #2893ff;
    }

    QPushButton:pressed {
        background-color: #005bb5;
    }

    QScrollArea {
        border: none;
    }
"""

upload_button_style = """
    QPushButton {
        background-color: #007BFF;
        color: white;
        padding: 8px 16px;
        font-size: 13px;
        border-radius: 6px;
    }

    QPushButton:hover {
        background-color: #0056b3;
    }
"""

thumbnail_style = """
    QLabel {
        border-radius: 8px;
        background-color: #2a2a2a;
        border: 2px solid transparent;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.4);
    }

    QLabel:hover {
        border: 2px solid #5dade2;
        background-color: #333333;
    }
"""