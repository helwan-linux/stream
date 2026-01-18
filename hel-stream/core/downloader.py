import yt_dlp
import os
from utils.helpers import load_config, clean_filename

class MediaDownloader:
    def __init__(self):
        self.config = load_config()
        self.download_path = self.config.get("download_path", os.path.expanduser("~/Downloads"))

    def download_video(self, video_url, title, progress_hook=None):
        """
        Downloads full video with best quality.
        """
        filename = clean_filename(title)
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.download_path, f'{filename}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
        return self._execute_download(ydl_opts, video_url)

    def extract_audio(self, video_url, title, progress_hook=None):
        """
        Downloads only the audio and converts it to MP3.
        The "Protein-only" mode for saving data.
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
        }
        return self._execute_download(ydl_opts, video_url)

    def _execute_download(self, opts, url):
        """Internal execution with error handling."""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True, "Download completed successfully."
        except Exception as e:
            return False, str(e)
