import os
import urllib.request
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class VideoCard(QWidget):
    def __init__(self, title, uploader, duration, thumbnail_url):
        super().__init__()
        layout = QHBoxLayout(self)
        
        # حاوية النصوص (العنوان والبيانات)
        text_layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: bold; color: gold; font-size: 13px;")
        
        self.info_label = QLabel(f"{uploader} • {duration}")
        self.info_label.setStyleSheet("color: #888888; font-size: 11px;")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.info_label)
        
        # حاوية الصورة (Thumbnail)
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(120, 68)
        self.thumb_label.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 4px;")
        
        # استدعاء دالة تعيين الصورة
        self.set_thumbnail(thumbnail_url)
        
        layout.addWidget(self.thumb_label)
        layout.addLayout(text_layout)

    def set_thumbnail(self, url):
        # المسار الرسمي لأيقونة البرنامج بناءً على إفادتك [cite: 14]
        icon_path = os.path.join("assets", "icons", "stream.png")

        # 1. محاولة تحميل صورة الفيديو من الإنترنت (لو مش ملف محلي)
        if url and url.startswith("http"):
            try:
                # محاولة تحميل الصورة بمهلة ثانية واحدة لمنع التجمد
                data = urllib.request.urlopen(url, timeout=1).read()
                image = QImage()
                image.loadFromData(data)
                pixmap = QPixmap.fromImage(image)
                self.thumb_label.setPixmap(pixmap.scaled(120, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
            except:
                pass # إذا فشل التحميل ننتقل للأيقونة الافتراضية

        # 2. إذا كان ملف محلي أو فشل التحميل، نضع أيقونة stream.png الأصلية
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.thumb_label.setPixmap(pixmap.scaled(120, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.thumb_label.setAlignment(Qt.AlignCenter)
        else:
            # 3. الحل الأخير (Fallback) في حالة عدم وجود الملفين
            self.thumb_label.setText("🎬")
            self.thumb_label.setAlignment(Qt.AlignCenter)
            self.thumb_label.setStyleSheet("color: gold; font-size: 24px; background-color: #1a1a1a;")
