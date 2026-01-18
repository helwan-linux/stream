import yt_dlp
import os

class StreamEngine:
    def __init__(self):
        self.ydl_opts = {
            # تم تعديل التنسيق لضمان جلب أفضل جودة فيديو وصوت مدمجين
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            # 'extract_flat' تم ضبطه ليسمح بجلب البيانات الأساسية دون إبطاء المحرك
            'extract_flat': 'in_playlist', 
            'skip_download': True,
            # إضافة User-Agent لتبدو الأداة كمتصفح حقيقي وتتجنب الحظر
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query, max_results=10):
        results = []
        
        # ميزة المستكشف المحلي 
        if os.path.isdir(query):
            try:
                files = [f for f in os.listdir(query) if f.endswith(('.mp4', '.mkv', '.mp3', '.flv'))]
                for f in files[:max_results]:
                    results.append({
                        'title': f,
                        'url': os.path.abspath(os.path.join(query, f)),
                        'thumbnail': "local_icon", # يمكنك وضع مسار أيقونة ثابتة هنا
                        'duration': "Local",
                        'uploader': "Local Disk",
                    })
                return results
            except Exception as e:
                print(f"Local Scan Error: {e}")

        # تحسين صياغة البحث 
        search_query = query if query.startswith(('http://', 'https://')) else f"ytsearch{max_results}:{query}"
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # التحقق من نوع الرابط لضمان معالجة الإدخال بشكل صحيح
                info = ydl.extract_info(search_query, download=False)
                
                if not info:
                    return []

                entries = info.get('entries', [info])

                for entry in entries:
                    if entry:
                        # استخراج الرابط بذكاء (يحاول جلب الرابط المباشر أولاً ثم صفحة الويب) 
                        video_url = entry.get('url') or entry.get('webpage_url')
                        
                        # في بعض الأحيان ytsearch يعيد id فقط، نقوم بصناعة الرابط
                        if entry.get('ie_key') == 'Youtube' and not video_url.startswith('http'):
                            video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"

                        results.append({
                            'title': entry.get('title', 'Unknown Title'),
                            'url': video_url,
                            'thumbnail': entry.get('thumbnail', ''),
                            'duration': self._format_duration(entry.get('duration')),
                            'uploader': entry.get('uploader', 'Unknown Source'),
                        })
        except Exception as e:
            print(f"Search Error: {e}")
            
        return results

    def _format_duration(self, seconds):
        """تحويل الثواني إلى تنسيق (دقيقة:ثانية)"""
        if not seconds or not isinstance(seconds, int): return "00:00"
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def get_stream_url(self, url):
        """جلب رابط البث المباشر النهائي للـ MPV """
        # نستخدم خيار --get-url بشكل برمجي لسرعة الاستجابة
        with yt_dlp.YoutubeDL({'quiet': True, 'format': 'best'}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info.get('url', url)
            except:
                return url
