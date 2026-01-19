import os
import urllib.request
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ImageLoader(QThread):
    """خيط مستقل لتحميل الصور من الإنترنت"""
    finished = pyqtSignal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            # مهلة 3 ثوانٍ لتحميل الصورة
            data = urllib.request.urlopen(self.url, timeout=3).read()
            image = QImage()
            if image.loadFromData(data):
                pixmap = QPixmap.fromImage(image)
                self.finished.emit(pixmap)
        except:
            pass

class VideoCard(QWidget):
    def __init__(self, title, uploader, duration, thumbnail_url):
        super().__init__()
        layout = QHBoxLayout(self)
        
        text_layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: bold; color: gold; font-size: 13px;")
        
        self.info_label = QLabel(f"{uploader} • {duration}")
        self.info_label.setStyleSheet("color: #888888; font-size: 11px;")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.info_label)
        
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(120, 68)
        self.thumb_label.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 4px;")
        self.thumb_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.thumb_label)
        layout.addLayout(text_layout)

        # بدء تحميل الصورة في الخلفية
        self.set_thumbnail(thumbnail_url)

    def set_thumbnail(self, url):
        # وضع أيقونة مؤقتة لحين اكتمال التحميل
        self.thumb_label.setText("⌛")
        
        if url and url.startswith("http"):
            self.loader = ImageLoader(url)
            self.loader.finished.connect(self.apply_pixmap)
            self.loader.start()
        else:
            self.apply_default_icon()

    def apply_pixmap(self, pixmap):
        """تحديث الصورة بمجرد اكتمال التحميل"""
        self.thumb_label.setPixmap(pixmap.scaled(120, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def apply_default_icon(self):
        icon_path = os.path.join("assets", "icons", "stream.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.thumb_label.setPixmap(pixmap.scaled(120, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.thumb_label.setText("🎬")
            self.thumb_label.setStyleSheet("color: gold; font-size: 24px; background-color: #1a1a1a;")
