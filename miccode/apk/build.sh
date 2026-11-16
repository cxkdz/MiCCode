#!/usr/bin/env bash
# 手工构建 MiCCode.apk —— 不用 Gradle，直接调 aapt2 / javac / d8 / apksigner
set -u

BT="/d/AndroidStudio/build-tools/34.0.0"
D8BT="/d/AndroidStudio/build-tools/37.0.0"   # 老版 d8 在 JDK 21 上会 NPE，用新的
PLATFORM="/d/AndroidStudio/platforms/android-34/android.jar"
JBR="/c/Program Files/Android/Android Studio/jbr/bin"
export JAVA_HOME="C:/Program Files/Android/Android Studio/jbr"

cd "$(dirname "$0")" || exit 1

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
fail() { printf '\033[31m✗ %s\033[0m\n' "$1"; exit 1; }

rm -rf build MiCCode.apk assets
mkdir -p build/gen build/classes build/dex || fail "建目录失败"

step "0/7 打包前端资源到 assets（无服务也能编辑）"
mkdir -p assets/www/vendor || fail "创建 assets 失败"
cp ../index.html ../symbols.json ../manifest.json \
   ../icon-192.png ../icon-512.png ../favicon-32.png assets/www/ || fail "拷贝前端文件失败"
cp ../vendor/* assets/www/vendor/ || fail "拷贝 vendor 失败"
echo "  assets/www: $(ls assets/www | wc -l) 个文件 + vendor/"

step "1/7 编译资源 (aapt2 compile)"
"$BT/aapt2.exe" compile --dir res -o build/res.zip || fail "资源编译失败"

step "2/7 生成 APK 骨架 + R.java (aapt2 link)"
"$BT/aapt2.exe" link \
  -o build/base.apk \
  -I "$PLATFORM" \
  --manifest AndroidManifest.xml \
  --auto-add-overlay \
  -A assets \
  -R build/res.zip \
  --java build/gen \
  --min-sdk-version 21 \
  --target-sdk-version 34 \
  || fail "链接失败"

step "3/7 编译 Java (javac)"
"$JBR/javac.exe" -source 8 -target 8 -nowarn \
  -classpath "$PLATFORM" \
  -d build/classes \
  build/gen/com/miccode/app/R.java \
  src/com/miccode/app/MainActivity.java 2>&1 | grep -v "^警告\|^warning\|bootstrap" || true
[ -f build/classes/com/miccode/app/MainActivity.class ] || fail "javac 没有产出 class"

step "4/7 转 dex (d8)"
"$D8BT/d8.bat" --lib "$PLATFORM" --min-api 24 --output build/dex \
  build/classes/com/miccode/app/*.class || fail "d8 失败"
[ -f build/dex/classes.dex ] || fail "没有生成 classes.dex"

step "5/7 把 dex 塞进 APK（重建 zip 而不是追加，避免 header mismatch）"
python - <<'PY' || fail "打包 dex 失败"
import zipfile
src = zipfile.ZipFile("build/base.apk")
dst = zipfile.ZipFile("build/unsigned.apk", "w", zipfile.ZIP_DEFLATED)
n = 0
for item in src.infolist():
    # 用原来的 ZipInfo 写，保留每个条目自己的压缩方式
    # （resources.arsc 必须保持不压缩，Android 11+ 会校验）
    dst.writestr(item, src.read(item.filename))
    n += 1
src.close()
dst.write("build/dex/classes.dex", "classes.dex")
dst.close()
print("  重建完成：%d 个原有条目 + classes.dex" % n)
PY

step "6/7 对齐 (zipalign)"
"$BT/zipalign.exe" -f 4 build/unsigned.apk build/aligned.apk || fail "zipalign 失败"

step "7/7 签名 (apksigner)"
if [ ! -f miccode.keystore ]; then
  echo "  生成签名密钥…"
  "$JBR/keytool.exe" -genkeypair -v \
    -keystore miccode.keystore -alias miccode \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass miccode2026 -keypass miccode2026 \
    -dname "CN=MiCCode, OU=Personal, O=MiCCode, L=CN, ST=CN, C=CN" \
    >/dev/null 2>&1 || fail "生成 keystore 失败"
fi

"$BT/apksigner.bat" sign \
  --ks miccode.keystore \
  --ks-pass pass:miccode2026 \
  --key-pass pass:miccode2026 \
  --min-sdk-version 21 \
  --v1-signing-enabled true \
  --v2-signing-enabled true \
  --v3-signing-enabled true \
  --out MiCCode.apk build/aligned.apk || fail "签名失败"

"$BT/apksigner.bat" verify --print-certs MiCCode.apk 2>&1 | head -4

SIZE=$(stat -c%s MiCCode.apk)
awk -v s="$SIZE" 'BEGIN { printf "\n\033[32m✓ 构建成功\033[0m  MiCCode.apk  (%.0f KB)\n", s/1024 }'
