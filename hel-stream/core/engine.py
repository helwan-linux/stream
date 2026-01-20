import yt_dlp
import subprocess
import sys
import os
from typing import List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal # استيراد السيجنالز

class UniversalStreamEngine(QObject): # جعل الكلاس يدعم السيجنالز
    # تعريف إشارة تحديث العداد (النسبة، السرعة)
    progress_signal = pyqtSignal(float, str)
    
    def __init__(self):
        super().__init__() # ضروري للـ QObject
        self.ensure_latest_engine()
        
        # إعدادات البحث الافتراضية (سريعة ولا تحمل ملفات)
        self.default_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'extract_flat': True,
            'skip_download': True,
            'socket_timeout': 7,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

    def ensure_latest_engine(self):
        try:
            subprocess.Popen([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    # --- دالة الـ Hook للعداد ---
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # محاولة الحصول على النسبة المئوية بكافة الطرق الممكنة
                percent_str = d.get('_percent_str')
                if percent_str:
                    # تنظيف النص وتحويله لرقم (مثلاً " 50.5%" تبقى 50.5)
                    percent = float(percent_str.replace('%', '').strip())
                else:
                    # حساب يدوي لو النص مش موجود
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    percent = (downloaded / total * 100) if total > 0 else 0.5 # هزة بسيطة للعداد

                speed = d.get('_speed_str', '0KB/s')
                
                # إرسال الإشارة فوراً للواجهة
                self.progress_signal.emit(percent, speed)
                
            except Exception as e:
                # لو حصل أي خطأ، ابعت إشارة "جاري العمل" عشان العداد ما يثبتش
                self.progress_signal.emit(0.1, "Calculating...")
                
        elif d['status'] == 'finished':
            self.progress_signal.emit(100.0, "Done")

    def download_video(self, url: str, path: str):
        """دالة التحميل النهائية - إصلاح القطع وتشغيل العداد"""
        if not os.path.exists(path):
            os.makedirs(path)

        download_opts = {
            # تعديل الفورمات لأضمن صيغة عشان ما يقطعش
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'progress_hooks': [self._progress_hook],
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            # إضافة الهوية عشان السيرفر ما يرفضش الاتصال ويصفر العداد
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
            'noplaylist': True,
            'http_chunk_size': 1048576, # تحميل القطع الصغيرة لضمان الاستقرار
        }
        
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            # مسح الذاكرة المؤقتة لضمان بداية فريش للعداد
            ydl.download([url])

    def search(self, query: str, platform: str = "All") -> List[Dict[str, Any]]:
        # إذا كان المدخل رابطاً مباشراً وليس كلمة بحث
        if query.startswith(('http://', 'https://')):
            return self.get_direct_info(query)

        search_results = []
        mapping = {
            "YouTube": f"ytsearch10:{query}",
            "SoundCloud": f"scsearch10:{query}",
            #"TikTok": f"https://www.tiktok.com/search?q={query}",
            #"TikTok": f"ytsearch5:{query}",
            #"Facebook": f"https://www.facebook.com/search/videos/?q={query}",
            #"Twitter": f"https://twitter.com/search?q={query}&f=video"
        }

        targets = [mapping.get(platform, f"ytsearch10:{query}")] if platform != "All" else list(mapping.values())

        with yt_dlp.YoutubeDL(self.default_opts) as ydl:
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
                                'duration': self._format_duration(entry.get('duration')),
                                'thumbnail': entry.get('thumbnail') or '',
                                'source': entry.get('ie_key', 'Web')
                            })
                except Exception as e:
                    print(f"Engine Warning: Search failed for {target} -> {e}")
                    continue 

        return search_results

    def get_direct_info(self, url: str) -> List[Dict[str, Any]]:
        """لجلب معلومات رابط مباشر ووضعه في قائمة النتائج"""
        try:
            with yt_dlp.YoutubeDL(self.default_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return [{
                    'title': info.get('title', 'Direct Link'),
                    'url': url,
                    'uploader': info.get('uploader', 'Web'),
                    'duration': self._format_duration(info.get('duration')),
                    'thumbnail': info.get('thumbnail', ''),
                    'source': 'Direct'
                }]
        except:
            return []

    def get_available_formats(self, url: str) -> List[Dict[str, str]]:
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                seen_heights = set()
                
                for f in info.get('formats', []):
                    height = f.get('height')
                    if height and height not in seen_heights and f.get('vcodec') != 'none':
                        formats.append({
                            'id': f['format_id'],
                            'res': f"{height}p",
                            'note': f.get('format_note', '')
                        })
                        seen_heights.add(height)
                
                formats.sort(key=lambda x: int(x['res'].replace('p','')), reverse=True)
                return formats
        except:
            return []

    def get_stream_url(self, url: str, requested_quality: str = "best") -> str:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]

        if requested_quality != "best" and requested_quality != "Auto":
            clean_res = requested_quality.replace('p', '')
            fmt = f"bestvideo[height<={clean_res}]+bestaudio/best"
        else:
            fmt = "best"

        for i, ua in enumerate(user_agents):
            try:
                opts = {
                    **self.default_opts,
                    'format': fmt,
                    'user_agent': ua,
                    'socket_timeout': 5,
                }
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    stream_url = info.get('url')
                    if stream_url:
                        return stream_url
            except Exception:
                fmt = "best"
                continue

        return url

    def _format_duration(self, duration: Any) -> str:
        if not duration: return "00:00"
        try:
            if isinstance(duration, str): return duration
            total_seconds = int(duration)
            mins, secs = divmod(total_seconds, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                return f"{hours:02d}:{mins:02d}:{secs:02d}"
            return f"{mins:02d}:{secs:02d}"
        except:
            return "00:00"
