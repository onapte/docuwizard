from PySide6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QFrame,
    QSizePolicy,
    QLayout,
    QWidgetItem,
    QScrollArea,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
)

from PySide6.QtGui import QPixmap, QImage, QDrag, QGuiApplication, QWheelEvent, QPainter
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize, QMimeData
from PIL import Image, ImageEnhance
import math


class ZoomableImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._pixmap = None
        self._scale_factor = 1.0

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._scale_factor = 1.0
        self.update_scaled_pixmap()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self._scale_factor *= 1.1
        else:
            self._scale_factor /= 1.1
        self.update_scaled_pixmap()

    def update_scaled_pixmap(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                self._pixmap.size() * self._scale_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled)



class ImagePreviewerDialog(QDialog):
    def __init__(self, image_paths, start_index=0, images_settings=None, parent=None):
        super().__init__()

        self.setWindowTitle("Image Editor")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        self.image_paths = image_paths
        self.index = start_index
        self.images_settings = images_settings if images_settings is not None else {}
        self.init_image_settings()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.image_label = ZoomableImageLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)

        self.rotation_slider = CircularSlider()
        self.rotation_slider.angleChanged.connect(self.update_rotation)

        self.saturation_slider = CircularSlider(label="Saturation")
        self.saturation_slider.angleChanged.connect(self.update_saturation)

        self.contrast_slider = CircularSlider(label="Contrast")
        self.contrast_slider.angleChanged.connect(self.update_contrast)

        self.stack_widget = QStackedWidget()
        self.setup_tool_panels()

        self.prev_button = QPushButton("◀")
        self.prev_button.clicked.connect(self.show_prev)

        self.next_button = QPushButton("▶")
        self.next_button.clicked.connect(self.show_next)

        self.confirm_button = QPushButton("Apply changes")
        self.confirm_button.setFixedWidth(160)
        self.confirm_button.clicked.connect(self.confirm_settings)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(160)
        self.cancel_button.clicked.connect(self.reset_all_settings)

        self.tool_list = QListWidget()
        self.tool_list.setStyleSheet("font-size: 14px; color: white;")
        tool_items = ["Rotation", "Brightness", "Contrast", "Saturation"]
        for tool in tool_items:
            item = QListWidgetItem(tool)
            item.setSizeHint(QSize(120, 40))
            self.tool_list.addItem(item)
        self.tool_list.currentRowChanged.connect(self.stack_widget.setCurrentIndex)
        self.tool_list.setMaximumWidth(150)
        self.tool_list.setFixedHeight(len(tool_items) * 50)
        self.tool_list.setSpacing(5)

        tool_layout = QVBoxLayout()
        tool_layout.addStretch()
        tool_layout.addWidget(self.tool_list)
        tool_layout.addStretch()

        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.confirm_button)
        buttons_layout.addStretch()

        editor_layout = QVBoxLayout()
        editor_layout.addWidget(self.scroll_area, stretch=4)
        editor_layout.addWidget(self.stack_widget, stretch=1)
        editor_layout.addLayout(nav_layout)
        editor_layout.addLayout(buttons_layout)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addLayout(tool_layout)
        main_layout.addLayout(editor_layout, stretch=4)

        self.setLayout(main_layout)
        self.load_image()

    def init_image_settings(self):
        for path in self.image_paths:
            if path not in self.images_settings:
                self.images_settings[path] = {
                    'rotation': {'angle': 0},
                    'brightness': {'factor': 1.0},
                    'contrast': {'factor': 1.0},
                    'saturation': {'factor': 1.0},
                }

    def update_brightness(self, value):
        path = self.image_paths[self.index]
        self.images_settings[path]['brightness']['factor'] = value / 100.0
        self.render_image()

    def update_rotation(self, angle):
        path = self.image_paths[self.index]
        self.images_settings[path]['rotation']['angle'] = angle
        self.render_image()

    def show_prev(self):
        if self.index > 0:
            self.index -= 1
            self.load_image()

    def show_next(self):
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.load_image()

    def setup_tool_panels(self):
        def centered_slider_widget(slider: QWidget):
            wrapper = QWidget()
            layout = QVBoxLayout(wrapper)
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(slider)
            return wrapper

        self.stack_widget.addWidget(centered_slider_widget(self.rotation_slider))
        self.brightness_slider = CircularSlider(label="Brightness")
        self.brightness_slider.setValue(100)
        self.brightness_slider.angleChanged.connect(self.update_brightness)
        self.stack_widget.addWidget(centered_slider_widget(self.brightness_slider))
        self.stack_widget.addWidget(centered_slider_widget(self.contrast_slider))
        self.stack_widget.addWidget(centered_slider_widget(self.saturation_slider))

    def update_contrast(self, value):
        path = self.image_paths[self.index]
        self.images_settings[path]['contrast']['factor'] = value / 100.0
        self.render_image()

    def update_saturation(self, value):
        path = self.image_paths[self.index]
        self.images_settings[path]['saturation']['factor'] = value / 100.0
        self.render_image()

    def load_image(self):
        path = self.image_paths[self.index]
        self.rotation_slider.setValue(self.images_settings[path]['rotation']['angle'])
        self.brightness_slider.setValue(int(self.images_settings[path]['brightness']['factor'] * 100))
        self.contrast_slider.setValue(int(self.images_settings[path]['contrast']['factor'] * 100))
        self.saturation_slider.setValue(int(self.images_settings[path]['saturation']['factor'] * 100))
        self.render_image()

    def render_image(self):
        path = self.image_paths[self.index]
        image = Image.open(path).convert("RGBA")

        settings = self.images_settings[path]
        image = image.rotate(-settings['rotation']['angle'], expand=True)
        image = ImageEnhance.Brightness(image).enhance(settings['brightness']['factor'])
        image = ImageEnhance.Contrast(image).enhance(settings['contrast']['factor'])
        image = ImageEnhance.Color(image).enhance(settings['saturation']['factor'])

        qt_image = QImage(
            image.tobytes("raw", "RGBA"),
            image.width,
            image.height,
            QImage.Format_RGBA8888
        )
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def reset_all_settings(self):
        for path in self.image_paths:
            self.images_settings[path] = {
                'rotation': {'angle': 0},
                'brightness': {'factor': 1.0},
                'contrast': {'factor': 1.0},
                'saturation': {'factor': 1.0},
            }
        self.accept()

    def get_images_settings(self):
        return self.images_settings

    def confirm_settings(self):
        path = self.image_paths[self.index]
        self.images_settings[path]['rotation']['angle'] = self.rotation_slider.value()
        self.images_settings[path]['brightness']['factor'] = self.brightness_slider.value() / 100.0
        self.images_settings[path]['contrast']['factor'] = self.contrast_slider.value() / 100.0
        self.images_settings[path]['saturation']['factor'] = self.saturation_slider.value() / 100.0
        self.accept()



class ThumbnailLabel(QLabel):
    doubleClicked = Signal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(100, 100)
        self.setScaledContents(True)

        pixmap = QPixmap(image_path)
        self.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("margin: 5px;")
        self.setAcceptDrops(True)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit(self.image_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.image_path)
            drag.setMimeData(mime)
            drag.setPixmap(self.pixmap().scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            drag.setHotSpot(event.pos())
            drag.exec(Qt.MoveAction)



class ThumbnailContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.container_layout = FlowLayout()
        self.setLayout(self.container_layout)

    def add_thumbnail(self, thumb: ThumbnailLabel):
        self.container_layout.addWidget(thumb)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        path = event.mimeData().text()
        dragged = None
        index_to_remove = -1

        for i in range(self.container_layout.count()):
            item = self.container_layout.itemAt(i)
            if isinstance(item.widget(), ThumbnailLabel) and item.widget().image_path == path:
                dragged = item.widget()
                index_to_remove = i
                break

        if dragged:
            pos = event.position().toPoint()
            target_index = self._find_insert_index(pos)

            if 0 <= index_to_remove < self.container_layout.count():
                item = self.container_layout.takeAt(index_to_remove)
                item.widget().setParent(None) 

            self.container_layout._items.insert(target_index, QWidgetItem(dragged))
            self.container_layout.invalidate()
            self.container_layout.update()
            self.container_layout.setGeometry(self.geometry())
            event.acceptProposedAction()

    def _find_insert_index(self, pos: QPoint):
        for i in range(self.container_layout.count()):
            item = self.container_layout.itemAt(i)
            if item.widget().geometry().contains(pos):
                return i
        return self.container_layout.count()



class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=10):
        super().__init__(parent)
        self._items = []
        self.setSpacing(spacing)
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def _create_item(self, widget):
        self.addChildWidget(widget)
        return QWidgetItem(widget)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self._items:
            widget = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class CircularSlider(QWidget):
    angleChanged = Signal(int)

    def __init__(self, parent=None, label="Rotation"):
        super().__init__(parent)
        self._angle = 0
        self.label = label
        self.setFixedSize(160, 180)
        self.setStyleSheet("color: white; font-weight: bold;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2 + 10)
        radius = 60

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.gray)
        for i in range(10, 0, -1):
            painter.setOpacity(0.01 * i)
            painter.drawEllipse(center, radius + i, radius + i)

        painter.setOpacity(1.0)
        painter.setPen(Qt.lightGray)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius, radius)

        painter.setPen(Qt.cyan)
        painter.drawArc(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 90 * 16, -self._angle * 16)

        painter.setPen(Qt.white)
        painter.setFont(painter.font())
        painter.drawText(center.x() - 20, center.y() + 5, f"{self._angle}°")
        painter.setPen(Qt.cyan)
        painter.setFont(painter.font())
        painter.drawText(QRect(0, 0, self.width(), 30), Qt.AlignCenter, self.label)

    def mousePressEvent(self, event):
        self.update_angle(event.pos())

    def mouseMoveEvent(self, event):
        self.update_angle(event.pos())

    def update_angle(self, pos):
        dx = pos.x() - self.width() / 2
        dy = pos.y() - self.height() / 2
        angle = int((180 / 3.14159) * -1 * (math.atan2(dy, dx))) % 360
        self._angle = angle
        self.angleChanged.emit(angle)
        self.update()

    def value(self):
        return self._angle

    def setValue(self, angle):
        self._angle = angle
        self.update()
