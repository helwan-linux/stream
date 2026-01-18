Helwan Stream (Beta)
The Lightweight, Privacy-Focused Video Engine for Helwan Linux.

Helwan Stream is a high-performance video search and playback utility designed specifically for users who value system resources and privacy. Unlike resource-heavy web browsers, Helwan Stream decouples the video content from the website's bloat, providing a seamless experience even on legacy hardware (e.g., Core 2 Duo, 4GB RAM).

🚀 Key Features
Ultra-Low Resource Usage: Reduces CPU consumption by 40% to 60% compared to viewing in a browser by utilizing the raw power of MPV.

Privacy First: No tracking, no ads, and no JavaScript execution from video platforms. You watch the content, not the trackers.

Multi-Platform Search: Unified search engine for YouTube, Facebook, X (Twitter), and TikTok.

Legacy Hardware Friendly: Optimized for older machines where modern browsers often struggle or crash.

Battery Saver: Extends laptop battery life significantly by using hardware-accelerated decoding.

Smart Downloader: Built-in capability to download video or "Audio Only" to save bandwidth.

🛠 Tech Stack
Language: Python 3

UI Framework: PyQt5 (Native & Lightweight)

Playback Engine: MPV (Direct Hardware Rendering)

Backend Scraper: yt-dlp (Industry Standard)

📥 Installation (Helwan Linux / Arch)
Since the program relies on rolling-release packages, ensure your system is up to date:

Bash

sudo pacman -Syu
sudo pacman -S mpv yt-dlp python-pyqt5
📖 Usage
Launch the application.

Enter your search query in the search bar.

Select your desired platform (YouTube/Facebook/etc.).

Click on a video thumbnail to play instantly in the lightweight MPV player.

⚠️ Disclaimer
Helwan Stream is an independent tool and is not affiliated with any video hosting platform. It is designed to provide a more efficient way to access publicly available content for educational and personal use.
