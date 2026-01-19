# Maintainer: Saeed Badrelden <helwanlinux@gmail.com>
pkgname=hel-stream
_pkgname=hel-stream
pkgver=1.0.0.r0.g$(git rev-parse --short HEAD 2>/dev/null || echo "0")
pkgrel=1
pkgdesc="High-performance multimedia streaming and downloading engine for Helwan Linux."
arch=('any')
url="https://github.com/helwan-linux/stream"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-requests' 'python-pillow' 'yt-dlp' 'mpv' 'aria2' 'ffmpeg')
makedepends=('git')
provides=("$_pkgname")
conflicts=("$_pkgname")
source=("git+https://github.com/helwan-linux/stream.git")
md5sums=('SKIP')

pkgver() {
  cd "$_pkgname"
  git describe --long --tags | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
  cd "$srcdir/$_pkgname"

  # إنشاء المجلدات اللازمة في النظام
  install -dm755 "$pkgdir/usr/share/$_pkgname"
  install -dm755 "$pkgdir/usr/bin"

  # نسخ ملفات المشروع بالكامل (core, ui, assets, utils) 
  cp -r core ui assets utils main.py config.json requirements.txt "$pkgdir/usr/share/$_pkgname/"

  # إنشاء سكربت التشغيل في /usr/bin
  echo -e "#!/bin/bash\npython /usr/share/$_pkgname/main.py \"\$@\"" > "$pkgdir/usr/bin/$_pkgname"
  chmod +x "$pkgdir/usr/bin/$_pkgname"

  # تثبيت ملف الـ Desktop والأيقونة
  install -Dm644 "hel-stream.desktop" "$pkgdir/usr/share/applications/hel-stream.desktop"
  install -Dm644 "assets/icons/stream.png" "$pkgdir/usr/share/pixmaps/hel-stream.png"
}
