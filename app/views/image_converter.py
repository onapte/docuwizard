from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QScrollArea,
    QHBoxLayout
)

from PIL import Image
from app.image_export.utils import ImagePreviewerDialog, ThumbnailLabel, FlowLayout

from app.image_export.styles import (
    upload_button_style,
    thumbnail_style,
    global_style
)


class ImageExportView(QWidget):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.images_settings = dict()
        self.setStyleSheet(global_style)

        self.view_layout = QVBoxLayout(self)
        self.view_layout.setContentsMargins(10, 10, 10, 10)
        self.view_layout.setSpacing(10)

        self.upload_button = QPushButton("Upload images")
        self.upload_button.setFixedWidth(180)
        self.upload_button.setStyleSheet(upload_button_style)
        self.upload_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.upload_button.clicked.connect(self.upload_images)

        self.upload_layout = QHBoxLayout()
        self.upload_layout.addStretch()
        self.upload_layout.addWidget(self.upload_button)
        self.upload_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.flow_layout = FlowLayout(self.scroll_content)
        self.scroll_content.setLayout(self.flow_layout)
        self.scroll_area.setWidget(self.scroll_content)

        self.convert_button = QPushButton("Convert to PDF")
        self.convert_button.setStyleSheet("border-radius: 0px; padding: 6px;")
        self.convert_button.clicked.connect(self.convert_to_pdf)

        self.convert_layout = QHBoxLayout()
        self.convert_layout.addStretch()
        self.convert_layout.addWidget(self.convert_button)
        self.convert_layout.addStretch()

        self.view_layout.addLayout(self.upload_layout)
        self.view_layout.addWidget(self.scroll_area)
        self.view_layout.addLayout(self.convert_layout)

    def upload_images(self):
        filters = "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", filters)
        if files:
            self.image_paths = files
            self.render_thumbnails()

    def render_thumbnails(self):
        for i in reversed(range(self.flow_layout.count())):
            item = self.flow_layout.takeAt(i)
            if item:
                item.widget().deleteLater()

        for path in self.image_paths:
            thumb = ThumbnailLabel(path)
            thumb.setFixedSize(120, 120)
            thumb.setStyleSheet(thumbnail_style)
            thumb.doubleClicked.connect(self.open_image_editor)
            self.flow_layout.addWidget(thumb)

    def open_image_editor(self, image_path):
        index = self.image_paths.index(image_path)

        dialog = ImagePreviewerDialog(self.image_paths, index, self.images_settings)
        if dialog.exec():
            self.images_settings = dialog.get_images_settings()

    def apply_settings(self, ordered_paths):
        processed_images = []

        for path in ordered_paths:
            image = Image.open(path).convert("RGB")
            settings = self.images_settings.get(path, {})
            rotation = settings.get('rotation', {}).get('angle', 0)
            if rotation != 0:
                image = image.rotate(-rotation, expand=True)
            processed_images.append(image)

        return processed_images

    def convert_to_pdf(self):
        if not self.image_paths:
            QMessageBox.warning(self, "No Images", "Please upload images first.")
            return
        
        ordered_paths = []
        for i in range(self.flow_layout.count()):
            widget = self.flow_layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailLabel):
                ordered_paths.append(widget.image_path)

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")

        if save_path:
            try:
                processed_images = self.apply_settings(ordered_paths)

                processed_images[0].save(save_path, save_all=True, append_images=processed_images[1:])
                QMessageBox.information(self, "Success", "PDF created successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to convert: {str(e)}")