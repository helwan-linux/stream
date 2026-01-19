import yt_dlp
import subprocess
import sys

class UniversalStreamEngine:
    def __init__(self):
        # محاولة تحديث المحرك في الخلفية عند كل تشغيل لضمان تخطي الحظر
        self.ensure_latest_engine()
        
        self.ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'nocheckcertificate': True, 
            'socket_timeout': 7,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

    def ensure_latest_engine(self):
        """تحديث مكتبة yt-dlp برمجياً لضمان استمرارية العمل"""
        try:
            subprocess.Popen([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    def search(self, query, platform="All"):
        search_results = []
        mapping = {
            "YouTube": f"ytsearch10:{query}",
            "SoundCloud": f"scsearch10:{query}",
            "TikTok": f"https://www.tiktok.com/search?q={query}",
            "Facebook": f"https://www.facebook.com/search/videos/?q={query}",
            "Twitter": f"https://twitter.com/search?q={query}&f=video"
        }

        if platform == "All":
            targets = list(mapping.values())
        else:
            targets = [mapping.get(platform, f"ytsearch10:{query}")]

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            for target in targets:
                try:
                    info = ydl.extract_info(target, download=False)
                    if info and 'entries' in info:
                        for entry in info['entries']:
                            if not entry: continue
                            search_results.append({
                                'title': entry.get('title') or 'No Title',
                                'url': entry.get('url') or entry.get('webpage_url'),
                                'uploader': entry.get('uploader') or entry.get('channel') or 'Unknown Source',
                                'duration': self.clean_duration(entry.get('duration')),
                                'thumbnail': entry.get('thumbnail') or '',
                                'source': entry.get('ie_key', 'Web')
                            })
                except Exception as e:
                    print(f"Connection Error with {target}: {e}")
                    continue 

        return search_results

    def clean_duration(self, duration):
        if not duration: return "00:00"
        try:
            if isinstance(duration, str): return duration
            mins, secs = divmod(int(duration), 60)
            return f"{mins:02d}:{secs:02d}"
        except: return "00:00"

    def get_stream_url(self, url):
        try:
            with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True, 'nocheckcertificate': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url', url)
        except:
            return url
