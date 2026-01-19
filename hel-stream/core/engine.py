import yt_dlp
import subprocess
import sys
from typing import List, Dict, Any

class UniversalStreamEngine:
    def __init__(self):
        # Update yt-dlp automatically on startup
        self.ensure_latest_engine()
        
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
        """Attempts to update the yt-dlp core to bypass recent platform blocks."""
        try:
            subprocess.Popen([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    def search(self, query: str, platform: str = "All") -> List[Dict[str, Any]]:
        """Search across multiple media platforms."""
        search_results = []
        mapping = {
            "YouTube": f"ytsearch10:{query}",
            "SoundCloud": f"scsearch10:{query}",
            "TikTok": f"https://www.tiktok.com/search?q={query}",
            "Facebook": f"https://www.facebook.com/search/videos/?q={query}",
            "Twitter": f"https://twitter.com/search?q={query}&f=video"
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

    def get_available_formats(self, url: str) -> List[Dict[str, str]]:
        """Retrieves a list of available video resolutions (e.g., 1080p, 720p)."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                seen_heights = set()
                
                for f in info.get('formats', []):
                    height = f.get('height')
                    # Filter for unique resolutions that contain video
                    if height and height not in seen_heights and f.get('vcodec') != 'none':
                        formats.append({
                            'id': f['format_id'],
                            'res': f"{height}p",
                            'note': f.get('format_note', '')
                        })
                        seen_heights.add(height)
                
                # Sort descending (Highest resolution first)
                formats.sort(key=lambda x: int(x['res'].replace('p','')), reverse=True)
                return formats
        except:
            return []

    def get_stream_url(self, url: str, requested_quality: str = "best") -> str:
        """
        Silent Recovery System: Rotates User-Agents and falls back 
        to lower qualities if the primary stream fails to resolve.
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]

        # Convert simple quality string to yt-dlp format selector
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
                # On failure, try next User-Agent and fallback to generic 'best'
                fmt = "best"
                continue

        return url

    def _format_duration(self, duration: Any) -> str:
        """Converts seconds into MM:SS or HH:MM:SS format."""
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
