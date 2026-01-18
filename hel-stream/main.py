import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMenu
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# استدعاء أجزاء نظام "حلوان لينكس"
from ui.window import MainWindow
from ui.components import VideoCard
from core.engine import StreamEngine
from core.player import PlayerManager
from core.downloader import MediaDownloader

# --- حل مشكلة أيقونة التسك بار (Taskbar Icon Fix) ---
def fix_taskbar_icon():
    try:
        # معرف فريد للتطبيق ليتمكن النظام من تمييز أيقونته عن بايثون
        app_id = 'helwan.linux.stream.v1' 
        if sys.platform == 'win32':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception as e:
        print(f"Taskbar fix error: {e}")

class SearchWorker(QThread):
    """خيط مستقل للبحث لمنع تجمد الواجهة"""
    results_found = pyqtSignal(list)
    status_msg = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query
        self.engine = StreamEngine()

    def run(self):
        try:
            self.status_msg.emit(f"Searching for: {self.query}...")
            results = self.engine.search(self.query)
            self.results_found.emit(results)
        except Exception as e:
            self.status_msg.emit(f"Search Error: {str(e)}")
            self.results_found.emit([])

class DownloadWorker(QThread):
    """خيط مستقل للتحميل مع إرسال تحديثات التقدم"""
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url, title, mode="video"):
        super().__init__()
        self.url = url
        self.title = title
        self.mode = mode
        self.downloader = MediaDownloader()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                self.progress_signal.emit(int(float(p)))
            except: pass

    def run(self):
        if self.mode == "audio":
            success, msg = self.downloader.extract_audio(self.url, self.title, self.progress_hook)
        else:
            success, msg = self.downloader.download_video(self.url, self.title, self.progress_hook)
        self.finished_signal.emit(success, msg)

class HelwanStreamApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.player = PlayerManager()
        
        # تعيين الأيقونة للنافذة الرئيسية
        icon_path = os.path.join("assets", "icons", "stream.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.search_button.clicked.connect(self.run_search)
        self.search_input.returnPressed.connect(self.run_search)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        self.status_label.setText("Helwan Stream Ready | الجمال في الصمت")

    def run_search(self):
        query = self.search_input.text()
        if not query: return
        
        self.results_list.clear()
        self.worker = SearchWorker(query)
        self.worker.status_msg.connect(self.status_label.setText)
        self.worker.results_found.connect(self.display_results)
        self.worker.start()

    def display_results(self, results):
        if not results:
            self.status_label.setText("No results found. Check connection.")
            return

        for res in results:
            try:
                item = QListWidgetItem(self.results_list)
                card = VideoCard(
                    title=res['title'],
                    uploader=res['uploader'],
                    duration=res.get('duration', '00:00'),
                    thumbnail_url=res.get('thumbnail', '')
                )
                item.setSizeHint(card.sizeHint())
                item.setData(Qt.UserRole, res['url'])
                self.results_list.addItem(item)
                self.results_list.setItemWidget(item, card)
            except Exception as e:
                print(f"UI Error: {e}")
        
        self.status_label.setText(f"Found {len(results)} items.")

    def show_context_menu(self, pos):
        item = self.results_list.itemAt(pos)
        if not item: return
        
        menu = QMenu()
        play_action = menu.addAction("▶ Play with MPV")
        download_vid = menu.addAction("📥 Download Video")
        download_aud = menu.addAction("🎵 Extract Audio (Protein)")
        
        action = menu.exec_(self.results_list.mapToGlobal(pos))
        url = item.data(Qt.UserRole)
        card_widget = self.results_list.itemWidget(item)
        title = card_widget.title_label.text()

        if action == play_action:
            stream_url = StreamEngine().get_stream_url(url)
            self.player.play(stream_url)
        elif action == download_vid:
            self.start_download(url, title, "video")
        elif action == download_aud:
            self.start_download(url, title, "audio")

    def start_download(self, url, title, mode):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.dl_worker = DownloadWorker(url, title, mode)
        self.dl_worker.progress_signal.connect(self.progress_bar.setValue)
        self.dl_worker.finished_signal.connect(self.on_download_finished)
        self.dl_worker.start()

    def on_download_finished(self, success, msg):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Done!" if success else f"Error: {msg}")

if __name__ == "__main__":
    # تشغيل حل مشكلة التسك بار قبل بدء التطبيق
    fix_taskbar_icon()
    
    app = QApplication(sys.argv)
    
    # تعيين أيقونة التطبيق العامة لضمان ظهورها في التسك بار
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
