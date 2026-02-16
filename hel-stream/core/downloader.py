import yt_dlp
import os
from utils.helpers import load_config, clean_filename

class MediaDownloader:
	def __init__(self):
		# تحميل الإعدادات من الملف لضمان استخدام المسارات المخصصة
		self.config = load_config()
		self.download_path = self.config.get("download_path", os.path.expanduser("~/Downloads"))

	def download_video(self, video_url, title, progress_hook=None, quality="720p"):
		"""
		تنزيل الفيديو بالجودة المختارة مع دعم استكمال التحميل والسرعة القصوى.
		"""
		filename = clean_filename(title)
		
		# 1. التحقق من خيار "صوت فقط"
		if quality.lower() in ["audio only", "audio", "sound"]:
			return self.extract_audio(video_url, title, progress_hook)

		# 2. بناء معيار اختيار الجودة بشكل ديناميكي
		if quality == "Auto":
			format_selector = 'bestvideo+bestaudio/best'
		else:
			# تنظيف النص لضمان الحصول على الرقم (مثل 480 بدلاً من 480p)
			res = quality.replace('p', '')
			format_selector = f'bestvideo[height<={res}]+bestaudio/best'

		ydl_opts = {
			'format': format_selector,
			'continuedl': True,  # تفعيل ميزة استكمال التحميل في حالة الانقطاع
			'outtmpl': os.path.join(self.download_path, f'{filename}.%(ext)s'),
			'quiet': True,
			'no_warnings': True,
			'progress_hooks': [progress_hook] if progress_hook else [],
			
			# استخدام aria2c لتسريع التحميل عبر تعدد الاتصالات
			'external_downloader': 'aria2c',
			'external_downloader_args': [
				'-x', '16', '-s', '16', '-k', '1M'
			],
		}
		return self._execute_download(ydl_opts, video_url)

	def extract_audio(self, video_url, title, progress_hook=None):
		"""
		تحميل الصوت فقط وتحويله إلى صيغة MP3 بأعلى جودة.
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
			'continuedl': True,
			'quiet': True,
			'no_warnings': True,
			'progress_hooks': [progress_hook] if progress_hook else [],
			'external_downloader': 'aria2c',
			'external_downloader_args': ['-x', '16', '-s', '16'],
		}
		return self._execute_download(ydl_opts, video_url)

	def _execute_download(self, opts, url):
		"""تنفيذ التحميل مع معالجة الأخطاء التلقائية."""
		try:
			with yt_dlp.YoutubeDL(opts) as ydl:
				ydl.download([url])
			return True, "Download completed successfully."
		except Exception as e:
			# حل ذكي: إذا لم يتوفر aria2c في النظام، يتم التراجع للمحرك الافتراضي تلقائياً
			if "aria2c" in str(e).lower():
				opts.pop('external_downloader', None)
				opts.pop('external_downloader_args', None)
				try:
					with yt_dlp.YoutubeDL(opts) as ydl:
						ydl.download([url])
					return True, "Download completed (aria2c missing, used default)."
				except Exception as fallback_e:
					return False, str(fallback_e)
			return False, str(e)
