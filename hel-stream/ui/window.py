from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QLabel, QProgressBar, QSplitter, QComboBox, QListWidgetItem, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os

# تأكد أن ملف engine.py موجود في نفس المجلد
try:
    from engine import UniversalStreamEngine
except ImportError:
    from core.engine import UniversalStreamEngine

# كلاس التحميل في الخلفية - ضروري جداً عشان العداد يخرج من الترمينال للبرنامج
class DownloadThread(QThread):
    # إشارة بتبعتها الواجهة لنفسها (النسبة، السرعة)
    progress_update = pyqtSignal(float, str)

    def __init__(self, url, path):
        super().__init__()
        self.url = url
        self.path = path

    def run(self):
        import subprocess
        import re

        # أمر التحميل المباشر اللي بيطبع في الترمينال
        cmd = [
            'yt-dlp', 
            '--newline', 
            '--progress', 
            '--progress-template', '%(progress._percent_str)s|%(progress._speed_str)s',
            '-o', f'{self.path}/%(title)s.%(ext)s',
            self.url
        ]

        # فتح "ماسورة" (Pipe) لقراءة الكلام اللي بيطلع في الترمينال
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in process.stdout:
            # قراءة السطر المطبوع: " 45.2%|3.5MiB/s"
            if '|' in line:
                try:
                    parts = line.split('|')
                    percent = float(parts[0].replace('%', '').strip())
                    speed = parts[1].strip()
                    # إرسال البيانات للواجهة فوراً
                    self.progress_update.emit(percent, speed)
                except:
                    continue

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. تعريف المحرك وربطه بالواجهة (أهم خطوة للعداد)
        self.engine = UniversalStreamEngine()
        self.engine.progress_signal.connect(self.update_progress)
        
        self.setWindowTitle("Helwan Stream")
        self.resize(1100, 700) 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # --- 1. Search Bar ---
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for videos...")
        self.search_button = QPushButton("Search")
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Auto", "1080p", "720p", "480p", "360p", "Audio Only"])
        self.quality_combo.setFixedWidth(100)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.quality_combo)
        self.search_layout.addWidget(self.search_button)
        self.main_layout.addLayout(self.search_layout)

        # --- 2. Direct Link Bar ---
        self.url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Direct Link here (YouTube, TikTok, X...)")
        
        self.play_url_button = QPushButton("Play Link")
        self.play_url_button.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        
        self.url_button = QPushButton("Download Link")
        self.url_button.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        
        self.url_layout.addWidget(self.url_input)
        self.url_layout.addWidget(self.play_url_button)
        self.url_layout.addWidget(self.url_button)
        self.main_layout.addLayout(self.url_layout)

        # --- 3. Splitter ---
        self.splitter = QSplitter(Qt.Horizontal)
        self.results_container = QWidget()
        res_layout = QVBoxLayout(self.results_container)
        res_layout.addWidget(QLabel("🔍 Search Results"))
        self.results_list = QListWidget()
        res_layout.addWidget(self.results_list)

        self.playlist_container = QWidget()
        play_layout = QVBoxLayout(self.playlist_container)
        play_layout.addWidget(QLabel("📋 Up Next (Playlist)"))
        self.playlist_list = QListWidget()
        play_layout.addWidget(self.playlist_list)

        self.splitter.addWidget(self.results_container)
        self.splitter.addWidget(self.playlist_container)
        self.main_layout.addWidget(self.splitter)
        
        # --- 4. Download Progress ---
        self.download_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.download_label = QLabel("") 
        self.download_label.setVisible(False)
        
        self.download_layout.addWidget(self.progress_bar)
        self.download_layout.addWidget(self.download_label)
        self.main_layout.addLayout(self.download_layout)
        
        self.status_label = QLabel("Ready")
        self.main_layout.addWidget(self.status_label)

        # --- 5. Buttons Logic ---
        self.search_button.clicked.connect(self.handle_search)
        self.search_input.returnPressed.connect(self.handle_search)
        self.play_url_button.clicked.connect(self.handle_play_link)
        self.url_button.clicked.connect(self.handle_direct_link)
        self.results_list.itemClicked.connect(self.on_item_clicked)

    def handle_search(self):
        query = self.search_input.text().strip()
        if not query: return
        
        self.status_label.setText(f"🔍 جاري البحث عن '{query}' في كافة المنصات...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        QApplication.processEvents() 
        
        self.results_list.clear()
        try:
            results = self.engine.search(query) 
            if not results:
                self.status_label.setText("❌ لم يتم العثور على نتائج.")
                return
                
            for res in results:
                item = QListWidgetItem(f"{res['title']} [{res['source']}]")
                item.setData(Qt.UserRole, res['url'])
                self.results_list.addItem(item)
            
            self.status_label.setText(f"✅ تم العثور على {len(results)} نتيجة")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"⚠️ فشل البحث: {str(e)}")

    def on_item_clicked(self, item):
        url = item.data(Qt.UserRole)
        self.url_input.setText(url)

    def handle_play_link(self):
        url = self.url_input.text().strip()
        if url:
            self.status_label.setText(f"Streaming: {url}")
            # تشغيل mpv في عملية منفصلة تماماً بعيداً عن البرنامج
            import subprocess
            subprocess.Popen(['mpv', url, '--no-terminal'])

    def handle_direct_link(self):
        url = self.url_input.text().strip()
        save_path = os.path.expanduser("~/Downloads")
        
        self.progress_bar.setVisible(True)
        self.dl_thread = DownloadThread(url, save_path)
        # ربط الإشارة بدالة التحديث
        self.dl_thread.progress_update.connect(self.update_progress)
        self.dl_thread.start()

    def update_progress(self, percent, speed):
        # تحويل لـ float ثم int لضمان عدم حدوث Crash
        p_float = float(percent)
        self.progress_bar.setValue(int(p_float))
        self.download_label.setText(f"🚀 Speed: {speed} | {int(p_float)}%")
        
        # إجبار الواجهة على التحديث حتى لو الجهاز مضغوط
        self.progress_bar.repaint() 
        QApplication.processEvents() 

        if p_float >= 100:
            self.status_label.setText("✅ تم التحميل بنجاح!")

    def get_selected_quality(self):
        return self.quality_combo.currentText()
