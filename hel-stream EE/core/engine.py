import yt_dlp
import subprocess
import sys

class UniversalStreamEngine:
    def __init__(self):
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

    # --- التعديل الجديد: جلب الجودات المتاحة ---
    def get_available_formats(self, url):
        """تجلب قائمة بالجودات المتاحة للفيديو (مثلاً: 1080p, 720p...)"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                seen_heights = set()
                
                # ترتيب الجودات من الأعلى للأقل
                for f in info.get('formats', []):
                    height = f.get('height')
                    # نفلتر الجودات عشان ميبقاش فيه تكرار وناخد اللي فيها فيديو وصوت
                    if height and height not in seen_heights and f.get('vcodec') != 'none':
                        formats.append({
                            'id': f['format_id'],
                            'res': f"{height}p",
                            'note': f.get('format_note', '')
                        })
                        seen_heights.add(height)
                
                # ترتيب القائمة تنازلياً حسب الرقم (مثلاً 1080 ثم 720)
                formats.sort(key=lambda x: int(x['res'].replace('p','')), reverse=True)
                return formats
        except:
            return []

    # --- التعديل الجديد: طلب البث بجودة محددة ---
    def get_stream_url(self, url, requested_quality="best"):
        """
        نظام التعافي الصامت: المحاولة أكثر من مرة بتغيير الهوية والجودة لضمان التشغيل.
        """
        # قائمة بالهويات المختلفة (User-Agents) للمناورة
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

        # تحديد صيغة الجودة
        fmt = f"bestvideo[height<={requested_quality[:-1]}]+bestaudio/best" if requested_quality != "Auto" else "best"

        for i, ua in enumerate(user_agents):
            try:
                opts = {
                    'format': fmt,
                    'quiet': True,
                    'nocheckcertificate': True,
                    'user_agent': ua,
                    'socket_timeout': 5, # تقليل وقت الانتظار عشان البرنامج ميهنجش
                }
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    res_url = info.get('url')
                    if res_url:
                        return res_url
            except Exception as e:
                print(f"Attempt {i+1} failed for {url}, trying next User-Agent...")
                # في المحاولة الأخيرة، نتنازل عن الجودة ونطلب أي حاجة شغالة
                fmt = "best" 
                continue

        # إذا فشل كل شيء، نرجع الرابط الأصلي لعل المشغل (MPV) يقدر يتعامل معاه بطريقته
        return url
