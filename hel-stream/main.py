import sys
import os
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# الآن الاستيراد سيعمل بنجاح حتى بعد التثبيت
import ctypes
import shutil
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMenu, QComboBox, QMessageBox 
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QProcess 
from PyQt5.QtGui import QIcon 

# استيراد المكونات
from ui.window import MainWindow 
from ui.components import VideoCard 
from core.engine import UniversalStreamEngine as StreamEngine 
from core.player import PlayerManager 

# استيراد ملف توفير الموارد
from resource_saver import apply_engine_saver, apply_ui_saver


try:
	from core.downloader import MediaDownloader
except ImportError:
	MediaDownloader = None

# --- Fix Taskbar Icon for Windows ---
def fix_taskbar_icon():
	try:
		app_id = 'helwan.linux.stream.v1' 
		if sys.platform == 'win32':
			ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
	except:
		pass

# --- Background Workers ---
class SearchWorker(QThread):
	results_found = pyqtSignal(list)
	status_msg = pyqtSignal(str)

	def __init__(self, query, platform="All"):
		super().__init__()
		self.query = query
		self.platform = platform
		self.engine = StreamEngine()

	def run(self):
		try:
			self.status_msg.emit(f"Searching for: {self.query}...")
			results = self.engine.search(self.query, platform=self.platform)
			self.results_found.emit(results)
		except Exception as e:
			self.status_msg.emit(f"Search Error: {str(e)}")
			self.results_found.emit([])

class StreamWorker(QThread):
	stream_ready = pyqtSignal(str, str) 
	status_msg = pyqtSignal(str)

	def __init__(self, url, quality, engine):
		super().__init__()
		self.url = url
		self.quality = quality
		self.engine = engine

	def run(self):
		try:
			self.status_msg.emit(f"Preparing {self.quality} stream...")
			stream_url = self.engine.get_stream_url(self.url, requested_quality=self.quality)
			self.stream_ready.emit(stream_url, self.quality)
		except Exception as e:
			self.status_msg.emit(f"Stream Error: {str(e)}")

class DownloadWorker(QThread):
	progress_signal = pyqtSignal(int)
	finished_signal = pyqtSignal(bool, str)

	def __init__(self, url, title, mode="video", quality="720p"):
		super().__init__()
		self.url = url
		self.title = title
		self.mode = mode
		self.quality = quality
		if MediaDownloader:
			self.downloader = MediaDownloader()

	def progress_hook(self, d):
		if d['status'] == 'downloading':
			p = d.get('_percent_str', '0%').replace('%','')
			try:
				self.progress_signal.emit(int(float(p)))
			except: pass

	def run(self):
		if not MediaDownloader:
			self.finished_signal.emit(False, "Downloader module missing")
			return
		if self.mode == "audio":
			success, msg = self.downloader.extract_audio(self.url, self.title, self.progress_hook)
		else:
			success, msg = self.downloader.download_video(self.url, self.title, self.progress_hook, quality=self.quality)
		self.finished_signal.emit(success, msg)

class HelwanStreamApp(MainWindow):
	def __init__(self):
		super().__init__()
		
		# Dependency check before initialization
		self.check_dependencies()
		
		self.player_manager = PlayerManager()
		#self.engine = StreamEngine()
		self.engine = apply_engine_saver(StreamEngine())
		apply_ui_saver(self)
		self.current_player_process = None 

		icon_path = os.path.join("assets", "icons", "stream.png")
		if os.path.exists(icon_path):
			self.setWindowIcon(QIcon(icon_path))
		
		if not hasattr(self, 'platform_selector'):
			self.platform_selector = QComboBox()
			self.platform_selector.addItems(["All", "YouTube", "SoundCloud"])
			try: self.search_layout.insertWidget(1, self.platform_selector)
			except: pass
		
		self.search_button.clicked.connect(self.run_search)
		self.search_input.returnPressed.connect(self.run_search)
		self.results_list.customContextMenuRequested.connect(self.show_results_menu)
		self.playlist_list.customContextMenuRequested.connect(self.show_playlist_menu)
		self.status_label.setText("Helwan Stream Ready | Minimalist Experience")

	def check_dependencies(self):
		"""Check for required CLI tools: mpv, aria2c, ffmpeg"""
		essentials = {
			'mpv': 'Required for Video Playback',
			'aria2c': 'Required for High-Speed Downloads',
			'ffmpeg': 'Required for Audio Extraction'
		}
		missing = [f"• {tool} ({reason})" for tool, reason in essentials.items() if not shutil.which(tool)]
		
		if missing:
			msg = QMessageBox(self)
			msg.setIcon(QMessageBox.Warning)
			msg.setWindowTitle("System Check | Helwan Stream")
			msg.setText("Missing system dependencies:")
			msg.setInformativeText("\n".join(missing))
			copy_btn = msg.addButton("Copy Install Command", QMessageBox.ActionRole)
			msg.addButton(QMessageBox.Ok)
			msg.exec_()
			if msg.clickedButton() == copy_btn:
				QApplication.clipboard().setText("sudo pacman -S mpv aria2 ffmpeg")

	def run_search(self):
		query = self.search_input.text()
		if not query: return
		self.results_list.clear()
		self.worker = SearchWorker(query, self.platform_selector.currentText())
		self.worker.status_msg.connect(self.status_label.setText)
		self.worker.results_found.connect(self.display_results)
		self.worker.start()

	def display_results(self, results):
		if not results:
			self.status_label.setText("No results found.")
			return
		for res in results:
			item = QListWidgetItem(self.results_list)
			card = VideoCard(res['title'], res['uploader'], res['duration'], res['thumbnail'])
			item.setSizeHint(card.sizeHint())
			item.setData(Qt.UserRole, res['url'])
			self.results_list.addItem(item)
			self.results_list.setItemWidget(item, card)
		self.status_label.setText(f"Found {len(results)} items.")

	def show_results_menu(self, pos):
		item = self.results_list.itemAt(pos)
		if not item: return
		menu = QMenu()
		add_queue = menu.addAction("Add to Playlist")
		play_now = menu.addAction("Play Now")
		download = menu.addAction("Download Video")
		
		action = menu.exec_(self.results_list.mapToGlobal(pos))
		if action == add_queue: self.add_to_playlist(item)
		elif action == play_now: self.start_playback(item)
		elif action == download: 
			quality = self.quality_combo.currentText()
			self.start_download(item.data(Qt.UserRole), "Video", "video", quality)

	def start_playback(self, item):
		url = item.data(Qt.UserRole)
		selected_quality = self.quality_combo.currentText()
		self.status_label.setText("Preparing secure stream connection...")
		
		self.st_worker = StreamWorker(url, selected_quality, self.engine)
		self.st_worker.status_msg.connect(self.status_label.setText)
		self.st_worker.stream_ready.connect(self.launch_mpv_player)
		self.st_worker.start()

	def launch_mpv_player(self, stream_url, quality):
		player_bin = self.player_manager.find_available_player()
		if player_bin:
			if self.current_player_process: 
				self.current_player_process.terminate()
				self.current_player_process.waitForFinished(1000)
			self.current_player_process = QProcess()
			self.current_player_process.finished.connect(self.on_player_finished)
			self.current_player_process.start(player_bin, [stream_url])
			self.status_label.setText(f"Streaming: {quality}")

	def start_download(self, url, title, mode, quality):
		self.progress_bar.setVisible(True)
		self.status_label.setText(f"Downloading {quality}...")
		self.dl_worker = DownloadWorker(url, title, mode, quality)
		self.dl_worker.progress_signal.connect(self.progress_bar.setValue)
		self.dl_worker.finished_signal.connect(lambda s, m: self.progress_bar.setVisible(False))
		self.dl_worker.start()

	def on_player_finished(self):
		if self.playlist_list.count() > 0:
			next_item = self.playlist_list.takeItem(0)
			self.start_playback(next_item)
		else:
			self.status_label.setText("Playlist finished.")

	def show_playlist_menu(self, pos):
		item = self.playlist_list.itemAt(pos)
		if not item: return
		menu = QMenu()
		remove = menu.addAction("Remove Item")
		action = menu.exec_(self.playlist_list.mapToGlobal(pos))
		if action == remove: self.playlist_list.takeItem(self.playlist_list.row(item))

	def add_to_playlist(self, search_item):
		url = search_item.data(Qt.UserRole)
		card = self.results_list.itemWidget(search_item)
		item = QListWidgetItem(self.playlist_list)
		new_card = VideoCard(card.title_label.text(), "In Queue", "", "")
		item.setSizeHint(new_card.sizeHint())
		item.setData(Qt.UserRole, url)
		self.playlist_list.addItem(item)
		self.playlist_list.setItemWidget(item, new_card)

if __name__ == "__main__":
	fix_taskbar_icon()
	app = QApplication(sys.argv)
	
	# Load Styles and Icons
	icon_path = os.path.join("assets", "icons", "stream.png")
	if os.path.exists(icon_path):
		app.setWindowIcon(QIcon(icon_path))
	
	try:
		if os.path.exists("ui/style.qss"):
			with open("ui/style.qss", "r", encoding="utf-8") as f:
				app.setStyleSheet(f.read())
	except: pass

	window = HelwanStreamApp()
	window.show()
	sys.exit(app.exec_())


