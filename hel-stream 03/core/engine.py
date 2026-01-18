import yt_dlp

class UniversalStreamEngine:
    def __init__(self):
        # إعدادات متقدمة لتجاوز حجب الاتصال وفشل الـ DNS
        self.ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'nocheckcertificate': True, 
            'socket_timeout': 7,
            # استخدام User-Agent لمتصفح حقيقي لتجنب حظر المواقع
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

    def search(self, query, platform="All"):
        search_results = []
        mapping = {
            "YouTube": f"ytsearch10:{query}",
            "SoundCloud": f"scsearch10:{query}",
            "TikTok": f"https://www.tiktok.com/search?q={query}",
            "Facebook": f"https://www.facebook.com/search/videos/?q={query}",
            "Twitter": f"https://twitter.com/search?q={query}&f=video"
        }

        # تحديد المواقع المطلوبة
        if platform == "All":
            targets = list(mapping.values())
        else:
            targets = [mapping.get(platform, f"ytsearch10:{query}")]

        # تنفيذ البحث باستخدام YoutubeDL
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            for target in targets:
                try:
                    # استخراج البيانات - قمنا بوضعها داخل try لكي لا ينهار البحث إذا فشل موقع واحد
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
                    # طباعة الخطأ في الكونسول للمطورة لكن استكمال البحث في باقي المواقع
                    print(f"Connection Error with {target}: {e}")
                    continue 

        return search_results

    def clean_duration(self, duration):
        """تحويل الثواني إلى تنسيق وقت مفهوم للـ UI"""
        if not duration: return "00:00"
        try:
            if isinstance(duration, str): return duration
            mins, secs = divmod(int(duration), 60)
            return f"{mins:02d}:{secs:02d}"
        except: return "00:00"

    def get_stream_url(self, url):
        """جلب رابط البث المباشر للمشغل"""
        try:
            with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True, 'nocheckcertificate': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url', url)
        except:
            return url
