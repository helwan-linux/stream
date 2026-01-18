from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QLabel, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon # استيراد مكتبة الأيقونات
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # إعدادات النافذة الأساسية
        self.setWindowTitle("Helwan Stream")
        self.resize(850, 650)
        
        # --- إضافة أيقونة البرنامج ---
        icon_path = os.path.join("assets", "icons", "stream.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # ---------------------------

        # Central Widget - العنصر المركزي اللي بيشيل كل حاجة
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layouts - تنظيم العناصر (رأسي للنافذة وأفقي للبحث)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.search_layout = QHBoxLayout()
        
        # 1. Search Section - شريط البحث والزرار
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for paradise fruits (videos)...")
        
        self.search_button = QPushButton("Search")
        
        # 2. Results Section - قائمة عرض النتائج
        self.results_list = QListWidget()
        # تفعيل خاصية القائمة المختصرة (كليك يمين) عشان نستخدمها في main.py [cite: 7]
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # 3. Progress Section - شريط تقدم التحميل
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # مخفي افتراضياً [cite: 9]
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        # 4. Status Bar - شريط الحالة في أسفل البرنامج
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_label") # لسهولة التنسيق في QSS [cite: 12]
        
        # Assemble UI - تجميع الأجزاء في الهيكل
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        
        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addWidget(self.results_list)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.status_label)
        
        # التنسيق يتم استدعاؤه من ملف style.qss الخارجي [cite: 9]
        self.setStyleSheet("QLabel#status_label { color: gold; font-weight: bold; }")
