# Maintainer: Saeed Badrelden <helwanlinux@gmail.com>
pkgname=hel-stream
pkgver=1.0.0
pkgrel=1
pkgdesc="High-performance multimedia streaming engine for Helwan Linux."
arch=('any')
url="https://github.com/helwan-linux/stream"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-requests' 'python-pillow' 'yt-dlp' 'mpv' 'aria2' 'ffmpeg')
source=("git+https://github.com/helwan-linux/stream.git")
md5sums=('SKIP')

package() {
  # 1. الدخول لمجلد المستودع اللي جيت هاب عمله Clone
  cd "$srcdir/stream"

  # 2. الدخول لمجلد المشروع الفعلي اللي إنت مصممه
  # إحنا محتاجين الملفات اللي جوه hel-stream/
  local _app_dir="hel-stream"

  install -dm755 "$pkgdir/usr/share/hel-stream"

  # 3. نسخ المحتويات من داخل مجلد hel-stream بالظبط كما في الهيكل اللي بعته
  cp -r "$_app_dir/core" "$pkgdir/usr/share/hel-stream/"
  cp -r "$_app_dir/ui" "$pkgdir/usr/share/hel-stream/"
  cp -r "$_app_dir/assets" "$pkgdir/usr/share/hel-stream/"
  cp -r "$_app_dir/utils" "$pkgdir/usr/share/hel-stream/"
  cp "$_app_dir/main.py" "$pkgdir/usr/share/hel-stream/"
  cp "$_app_dir/config.json" "$pkgdir/usr/share/hel-stream/"
  cp "$_app_dir/requirements.txt" "$pkgdir/usr/share/hel-stream/"

  # 4. إعداد ملف التشغيل (Binary Launcher)
  install -dm755 "$pkgdir/usr/bin"
  echo -e "#!/bin/bash\ncd /usr/share/hel-stream\npython main.py \"\$@\"" > "$pkgdir/usr/bin/hel-stream"
  chmod +x "$pkgdir/usr/bin/hel-stream"

  # 5. تثبيت ملف الـ Desktop والأيقونة
  if [ -f "$_app_dir/hel-stream.desktop" ]; then
    install -Dm644 "$_app_dir/hel-stream.desktop" "$pkgdir/usr/share/applications/hel-stream.desktop"
  fi
  
  # تثبيت الأيقونة في مسار النظام ليراها ملف الـ Desktop
  install -Dm644 "$_app_dir/assets/icons/stream.png" "$pkgdir/usr/share/pixmaps/hel-stream.png"
}
