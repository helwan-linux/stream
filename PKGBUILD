# Maintainer: Saeed Badrelden <helwanlinux@gmail.com>
pkgname=hel-stream
pkgver=1.0.0
pkgrel=1
pkgdesc="High-performance multimedia streaming engine for Helwan Linux."
arch=('any')
url="https://github.com/helwan-linux/stream"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-requests' 'python-pillow' 'yt-dlp' 'mpv' 'aria2' 'ffmpeg')

# بنستخدم $SRCDEST عشان نجيب الملفات اللي الـ Action عمل لها Checkout فعلاً
source=("${pkgname}::git+file://$GITHUB_WORKSPACE")
md5sums=('SKIP')

pkgver() {
  # بنعدل هنا عشان يدخل المجلد اللي اتعمل له Clone فعلياً
  cd "$srcdir/${pkgname}"
  printf "1.0.0"
}

package() {
  # الدخول للمجلد اللي فيه الكود
  cd "$srcdir/${pkgname}"
  
  install -dm755 "$pkgdir/usr/share/${pkgname}"
  
  # نسخ الملفات - تأكد إن المجلدات دي موجودة في جذر المستودع عندك
  cp -r core ui assets utils main.py requirements.txt "$pkgdir/usr/share/${pkgname}/"
  
  install -dm755 "$pkgdir/usr/bin"
  echo -e "#!/bin/bash\ncd /usr/share/${pkgname}\npython main.py \"\$@\"" > "$pkgdir/usr/bin/${pkgname}"
  chmod +x "$pkgdir/usr/bin/${pkgname}"

  # البحث عن ملف الـ Desktop في الجذر
  if [ -f "hel-stream.desktop" ]; then
    install -Dm644 "hel-stream.desktop" "$pkgdir/usr/share/applications/hel-stream.desktop"
  fi
}
