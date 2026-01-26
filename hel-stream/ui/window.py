from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
							 QLineEdit, QPushButton, QListWidget, QLabel, QProgressBar, QSplitter, QComboBox, QListWidgetItem, QApplication , QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
from core.player import PlayerManager

import psutil
# تأكد أن ملف engine.py موجود في نفس المجلد
try:
	from engine import UniversalStreamEngine
except ImportError:
	from core.engine import UniversalStreamEngine

# كلاس التحميل في الخلفية - ضروري جداً عشان العداد يخرج من الترمينال للبرنامج
class DownloadThread(QThread):
	progress_update = pyqtSignal(float, str)

	# 1. تحديث الـ __init__ لتقبل الجودة (quality)
	def __init__(self, url, path, quality): 
		super().__init__()
		self.url = url
		self.path = path
		self.quality = quality # حفظ الجودة المختارة

	def run(self):
		import subprocess
		
		# 2. منطق اختيار الصيغة بناءً على طلب المستخدم
		if self.quality == "Audio Only":
			# أمر تحميل الصوت وتحويله لـ mp3
			format_args = ['-f', 'bestaudio/best', '--extract-audio', '--audio-format', 'mp3']
		elif self.quality == "Auto":
			format_args = ['-f', 'bestvideo+bestaudio/best']
		else:
			# تنظيف الجودة (مثلاً 144p تصبح 144) 
			res = self.quality.replace('p', '')
			# اختيار جودة الفيديو المطلوبة أو أقل + الصوت 
			format_args = ['-f', f'bestvideo[height<={res}]+bestaudio/best']

		# 3. بناء الأمر النهائي مع دعم aria2c للسرعة القصوى 
		cmd = [
			'yt-dlp', 
			'--newline', 
			'--progress', 
			'--progress-template', '%(progress._percent_str)s|%(progress._speed_str)s',
			'--external-downloader', 'aria2c',
			'--external-downloader-args', '-x 16 -s 16 -k 1M',
			*format_args, # إضافة وسائط الجودة هنا
			'-o', f'{self.path}/%(title)s.%(ext)s',
			self.url
		]

		
		#self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
		self.process = subprocess.Popen(
			cmd,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True,
			start_new_session=True   # <-- مهم جدًا
		)

		for line in self.process.stdout:
			if '|' in line:
				try:
					parts = line.split('|')
					percent = float(parts[0].replace('%', '').strip())
					speed = parts[1].strip()
					self.progress_update.emit(percent, speed)
				except:
					continue

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		
		self.player = PlayerManager()
		
		# 1. تعريف المحرك وربطه بالواجهة (أهم خطوة للعداد)
		self.engine = UniversalStreamEngine()
		self.engine.progress_signal.connect(self.update_progress)
		
		self.setWindowTitle("Helwan Stream")
		self.resize(1100, 700) 
		
		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)
		self.main_layout = QVBoxLayout(self.central_widget)
		
		# أزرار إضافية
		self.extra_layout = QHBoxLayout()
		self.help_btn = QPushButton("Help ❓")
		self.about_btn = QPushButton("About ℹ️")
		
		self.extra_layout.addStretch() # دفع الأزرار لليمين
		self.extra_layout.addWidget(self.help_btn)
		self.extra_layout.addWidget(self.about_btn)
		self.main_layout.addLayout(self.extra_layout)

		# ربط الأزرار بالدوال
		self.help_btn.clicked.connect(self.show_help)
		self.about_btn.clicked.connect(self.show_about)
		
		# --- 1. Search Bar ---
		self.search_layout = QHBoxLayout()
		self.search_input = QLineEdit()
		# Updated Placeholder
		self.search_input.setPlaceholderText("Search for video title, channel, or keywords...")
		self.search_button = QPushButton("Search")
		
		self.quality_combo = QComboBox()
		self.quality_combo.addItems(["Auto", "1080p", "720p", "480p", "360p", "240p", "144p", "Audio Only"])
		self.quality_combo.setFixedWidth(100)
		
		self.search_layout.addWidget(self.search_input)
		self.search_layout.addWidget(self.quality_combo)
		self.search_layout.addWidget(self.search_button)
		self.main_layout.addLayout(self.search_layout)

		# --- 2. Direct Link Bar ---
		self.url_layout = QHBoxLayout()
		self.url_input = QLineEdit()
		# Updated Placeholder
		self.url_input.setPlaceholderText("Paste video URL here (YouTube, TikTok, Facebook, X, etc.)...")
		
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
		
		self.status_label = QLabel("Ready")
		self.main_layout.addWidget(self.status_label)

		# تعريف الأزرار
		self.is_paused = False
		self.btn_pause = QPushButton("Pause")
		self.btn_cancel = QPushButton("Cancel")
		self.btn_pause.setVisible(False)
		self.btn_cancel.setVisible(False)

		# إضافة الأزرار بجانب شريط التحميل والعداد
		self.download_layout.addWidget(self.progress_bar)
		self.download_layout.addWidget(self.download_label)
		self.download_layout.addWidget(self.btn_pause)
		self.download_layout.addWidget(self.btn_cancel)
		self.main_layout.addLayout(self.download_layout)
		
		# ربط الأزرار بالدوال
		self.btn_pause.clicked.connect(self.toggle_pause)
		self.btn_cancel.clicked.connect(self.stop_download)

		# --- 5. Buttons Logic ---
		self.search_button.clicked.connect(self.handle_search)
		self.search_input.returnPressed.connect(self.handle_search)
		self.play_url_button.clicked.connect(self.handle_play_link)
		self.url_button.clicked.connect(self.handle_direct_link)
		self.results_list.itemClicked.connect(self.on_item_clicked)
		
	# أضف هذه الدوال هنا
	def toggle_pause(self):
		if not hasattr(self, 'dl_thread'): 
			return
			
		# لو شغال → أوقفه
		if not self.is_paused:
			if hasattr(self.dl_thread, 'process'):
				psutil.Process(self.dl_thread.process.pid).terminate()
			
			self.btn_pause.setText("Resume")
			self.status_label.setText("⏸️ Download Paused")
			self.is_paused = True
		
		# لو متوقف → نعيد تشغيل التحميل
		else:
			url = self.url_input.text().strip()
			selected_quality = self.quality_combo.currentText()
			save_path = os.path.expanduser("~/Downloads")

			self.dl_thread = DownloadThread(url, save_path, selected_quality)
			self.dl_thread.progress_update.connect(self.update_progress)
			self.dl_thread.start()

			self.btn_pause.setText("Pause")
			self.status_label.setText("▶️ Download Resumed")
			self.is_paused = False

	def stop_download(self):
		if hasattr(self, 'dl_thread') and hasattr(self.dl_thread, 'process'):
			psutil.Process(self.dl_thread.process.pid).terminate()
		
		# حذف الملفات الجزئية
		for f in os.listdir(os.path.expanduser("~/Downloads")):
			if f.endswith(".part"):
				try: os.remove(os.path.join(os.path.expanduser("~/Downloads"), f))
				except: pass

		self.progress_bar.setVisible(False)
		self.btn_pause.setVisible(False)
		self.btn_cancel.setVisible(False)
		self.download_label.setText("")
		self.status_label.setText("❌ Download Cancelled")
		self.is_paused = False
		self.btn_pause.setText("Pause")



		

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
		if not url:
			return

		selected_quality = self.quality_combo.currentText()
		self.status_label.setText(f"Streaming: {url}")

		try:
			stream_url, fmt = self.engine.get_stream_url(url, selected_quality)
			ok, msg = self.player.play(stream_url, format_string=fmt)

			if not ok:
				self.status_label.setText(f"❌ Player error: {msg}")
		except Exception as e:
			self.status_label.setText(f"❌ Stream failed: {str(e)}")


	def handle_direct_link(self):
		url = self.url_input.text().strip()
		# السطر السحري: قراءة الجودة المختارة (مثلاً "144p" أو "Audio Only")
		selected_quality = self.quality_combo.currentText() 
		save_path = os.path.expanduser("~/Downloads")
		
		if url:
			# --- إظهار العداد والأزرار عند بدء التحميل ---
			self.progress_bar.setVisible(True)
			self.btn_pause.setVisible(True)
			self.btn_cancel.setVisible(True)
			self.download_label.setVisible(True)
			
			# نمرر selected_quality هنا كعامل ثالث
			self.dl_thread = DownloadThread(url, save_path, selected_quality)
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
			
	def show_help(self):
		QMessageBox.information(self, "Help", 
			"1. Paste link or search for video.\n"
			"2. Select quality (e.g., 144p for slow internet).\n"
			"3. Click 'Play' to stream or 'Download' to save.\n"
			"4. Downloads will resume automatically if interrupted.")

	def show_about(self):
		QMessageBox.about(self, "About Helwan Stream", 
			"Helwan Stream v1.0\n"
			"Part of Helwan Linux Project.\n"
			"Focused on speed and low-resource consumption.\n"
			"Built with love for the community.")

	def get_selected_quality(self):
		return self.quality_combo.currentText()
