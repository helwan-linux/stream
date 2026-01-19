# 📄 Helwan Linux Stream

**The Ultimate Multimedia Streaming & Downloading Engine for Helwan Linux.**

---

## 🌟 Overview

**Helwan Stream** is a high-performance, multi-platform media tool designed to provide a seamless experience for searching, streaming, and downloading content from various sources like **YouTube**, **SoundCloud**, and more.

Built with **Python** and **PyQt5**, it focuses on **speed**, **stability**, and **Silent Recovery** for broken streams.

---

## 🚀 Key Features

* **Universal Search**
  Unified search engine for YouTube, SoundCloud, TikTok, and more.

* **Silent Recovery**
  Multi-layered connection logic with User-Agent rotation to bypass blocks.

* **Quality Control**
  Dynamic resolution selection (1080p, 720p, 480p, etc.).

* **High-Speed Downloads**
  Powered by `aria2c` for maximum bandwidth utilization.

* **Minimalist UI**
  Clean, dark-themed interface built with custom QSS.

* **Dependency Shield**
  Automatic system check for required tools on startup.

---

## 📁 Project Structure

```
📁 hel-stream/
├── 📁 assets/           # Application icons and branding
├── 📄 config.json       # User settings and preferences
├── 📁 core/             # Business logic (Engine, Player, Downloader)
├── 📄 hel-stream.desktop # Linux desktop entry
├── 📄 main.py           # Application entry point
├── 📄 requirements.txt  # Python dependencies
├── 📁 ui/               # GUI components and styling (QSS)
├── 📁 utils/            # Logging and helper functions
└── 📄 PKGBUILD          # Arch Linux package build configuration
```

---

## 🛠️ Installation (Arch Linux)

### 1️⃣ System Dependencies

The app requires **mpv**, **ffmpeg**, and **aria2**. Install them using `pacman`:

```bash
sudo pacman -S --needed python-pyqt5 mpv python-requests yt-dlp python-pillow aria2 ffmpeg
```

### 2️⃣ Python Requirements

Install the required Python libraries from the project root:

```bash
pip install -r requirements.txt --break-system-packages
```

### 3️⃣ Build & Install via PKGBUILD

To install it as a native Arch Linux package:

```bash
makepkg -si
```

---

## 🖥️ Usage

Launch the application from the desktop menu or via terminal:

```bash
hel-stream
```

Or manually:

```bash
python main.py
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch:

   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch:

   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

Developed with ❤️ by the **Helwan Linux Team**
**Maintained by:** *Saeed Badrelden*
