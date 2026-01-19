# Maintainer: Saeed Badrelden <helwanlinux@gmail.com>
pkgname=hel-stream
pkgver=1.0.0
pkgrel=1
pkgdesc="High-performance multimedia streaming engine for Helwan Linux."
arch=('any')
url="https://github.com/helwan-linux/stream"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-requests' 'python-pillow' 'yt-dlp' 'mpv' 'aria2' 'ffmpeg')
# السحب مباشرة من الرابط العام
source=("git+https://github.com/helwan-linux/stream.git")
md5sums=('SKIP')

package() {
  # المجلد اللي جيت هاب هينزله هيكون اسمه stream (اسم الـ Repo)
  cd "$srcdir/stream"
  
  install -dm755 "$pkgdir/usr/share/hel-stream"
  
  # نسخ كل محتويات المشروع للمجلد الهدف
  cp -r core ui assets utils main.py requirements.txt "$pkgdir/usr/share/hel-stream/"
  
  install -dm755 "$pkgdir/usr/bin"
  echo -e "#!/bin/bash\ncd /usr/share/hel-stream\npython main.py \"\$@\"" > "$pkgdir/usr/bin/hel-stream"
  chmod +x "$pkgdir/usr/bin/hel-stream"

  if [ -f "hel-stream.desktop" ]; then
    install -Dm644 "hel-stream.desktop" "$pkgdir/usr/share/applications/hel-stream.desktop"
  fi
}
