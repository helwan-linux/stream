import yt_dlp
import os
from utils.helpers import load_config, clean_filename

class MediaDownloader:
    def __init__(self):
        self.config = load_config()
        self.download_path = self.config.get("download_path", os.path.expanduser("~/Downloads"))

    # تعديل الدالة لتقبل الجودة (quality)
    def download_video(self, video_url, title, progress_hook=None, quality="720p"):
        """
        تنزيل الفيديو بالجودة المختارة مع تفعيل السرعة القصوى.
        """
        filename = clean_filename(title)
        
        # تحويل الجودة النصية لشرط برمجي يفهمه yt-dlp
        # لو المستخدم اختار 1080p مثلاً، البرنامج هيجيب أحسن فيديو ميزيدش عن 1080p
        format_selector = f'bestvideo[height<={quality[:-1]}]+bestaudio/best' if quality != "Auto" else 'bestvideo+bestaudio/best'

        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(self.download_path, f'{filename}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook] if progress_hook else [],
            
            # --- ميزة الإبهار: تفعيل التحميل المتعدد (Multi-connection) ---
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '-x', '16', # فتح 16 اتصال بالسيرفر في نفس الوقت
                '-s', '16', # تقسيم الملف لـ 16 قطعة
                '-k', '1M'  # أقل حجم للقطعة 1 ميجا لضمان كفاءة التقسيم
            ],
        }
        return self._execute_download(ydl_opts, video_url)

    def extract_audio(self, video_url, title, progress_hook=None):
        """
        تحميل الصوت فقط بأعلى جودة MP3.
        """
        filename = clean_filename(title)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.download_path, f'{filename}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook] if progress_hook else [],
            # حتى في الصوت بنفعل السرعة القصوى
            'external_downloader': 'aria2c',
            'external_downloader_args': ['-x', '16', '-s', '16'],
        }
        return self._execute_download(ydl_opts, video_url)

    def _execute_download(self, opts, url):
        """Internal execution with error handling."""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True, "Download completed successfully."
        except Exception as e:
            # لو aria2c مش متطبب عند المستخدم، البرنامج هيرجع يحمل بالطريقة العادية تلقائياً
            if "aria2c" in str(e):
                opts.pop('external_downloader', None)
                opts.pop('external_downloader_args', None)
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                return True, "Download completed (aria2c missing, used default)."
            return False, str(e)
