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
		تنزيل الفيديو بالجودة المختارة أو الصوت فقط مع تفعيل السرعة القصوى.
		"""
		filename = clean_filename(title)
		
		# 1. التحقق إذا كان الاختيار هو "صوت فقط" 
		if quality.lower() in ["audio only", "audio", "sound"]:

			# توجيه العملية فوراً لدالة استخراج الصوت الموجودة بالفعل في الكلاس 
			return self.extract_audio(video_url, title, progress_hook)

		# 2. بناء معيار اختيار الجودة (Format Selector)
		# نستخدم المنطق الجديد ليدعم الجودات المنخفضة (144 و 240) بشكل سليم 
		if quality == "Auto":
			format_selector = 'bestvideo+bestaudio/best'
		else:
			# تنظيف النص من حرف 'p' لضمان بقاء الرقم فقط (مثل 144)
			res = quality.replace('p', '')
			# نطلب فيديو لا يتعدى الارتفاع المطلوب + أفضل صوت متاح 
			format_selector = f'bestvideo[height<={res}]+bestaudio/best'

		ydl_opts = {
			'format': format_selector,
			'continuedl': True,  # <-- أضف هذا السطر هنا لتفعيل استكمال التحميل
			'outtmpl': os.path.join(self.download_path, f'{filename}.%(ext)s'),
			'quiet': True,
			'no_warnings': True,
			'progress_hooks': [progress_hook] if progress_hook else [],
			
			# ميزة الإبهار (aria2c) تظل كما هي لضمان السرعة 
			'external_downloader': 'aria2c',
			'external_downloader_args': [
				'-x', '16', '-s', '16', '-k', '1M'
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
