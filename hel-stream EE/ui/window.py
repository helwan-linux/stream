from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QLabel, QProgressBar, QSplitter, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helwan Stream")
        self.resize(1100, 700) 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.search_layout = QHBoxLayout()
        
        # مدخلات البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for videos...")
        self.search_button = QPushButton("Search")
        
        # --- إضافة اختيار الجودة (الضربة الأولى) ---
        self.quality_combo = QComboBox()
        # جودات قياسية للمستخدم العادي، والمحرك اللي عدلناه هيوفقها مع المتاح
        self.quality_combo.addItems(["Auto", "1080p", "720p", "480p", "360p", "Audio Only"])
        self.quality_combo.setFixedWidth(100)
        self.quality_combo.setToolTip("Select Stream/Download Quality")
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.quality_combo) # أضفناه جنب البحث
        self.search_layout.addWidget(self.search_button)
        self.main_layout.addLayout(self.search_layout)

        # تقسيم الشاشة برمجياً 
        self.splitter = QSplitter(Qt.Horizontal)

        # حاوية النتائج
        self.results_container = QWidget()
        res_layout = QVBoxLayout(self.results_container)
        res_layout.addWidget(QLabel("🔍 Search Results"))
        self.results_list = QListWidget()
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        res_layout.addWidget(self.results_list)

        # حاوية قائمة التشغيل (Playlist) 
        self.playlist_container = QWidget()
        play_layout = QVBoxLayout(self.playlist_container)
        play_layout.addWidget(QLabel("📋 Up Next (Playlist)"))
        self.playlist_list = QListWidget()
        self.playlist_list.setContextMenuPolicy(Qt.CustomContextMenu)
        play_layout.addWidget(self.playlist_list)

        self.splitter.addWidget(self.results_container)
        self.splitter.addWidget(self.playlist_container)
        self.splitter.setStretchFactor(0, 3) 
        self.splitter.setStretchFactor(1, 1)

        self.main_layout.addWidget(self.splitter)
        
        # --- شريط التحميل (الضربة الثانية) ---
        self.download_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.download_label = QLabel("") # لإظهار سرعة التحميل أو النسبة
        self.download_label.setVisible(False)
        
        self.download_layout.addWidget(self.progress_bar)
        self.download_layout.addWidget(self.download_label)
        self.main_layout.addLayout(self.download_layout)
        
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_label")
        self.main_layout.addWidget(self.status_label)

    # دالة مساعدة للحصول على الجودة المختارة حالياً
    def get_selected_quality(self):
        return self.quality_combo.currentText()
