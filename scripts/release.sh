#!/usr/bin/env bash
# 组装可发布交付包（仅读者可见内容）。BASE 可覆盖。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f .env.build ] && . ./.env.build
PY="${PYTHON:-python}"
BASE="${BASE:-hotspot-bills}"

echo "== 构建最新产物 =="
bash scripts/build.sh >/dev/null

REL="$ROOT/release"
rm -rf "$REL"; mkdir -p "$REL"
copy() { if [ -f "$1" ]; then cp "$1" "$2"; echo "  + $(basename "$2")"; fi; }

copy output/book.pdf          "$REL/$BASE-print.pdf"
copy output/book-ereader.pdf  "$REL/$BASE-ereader.pdf"
copy output/book.epub         "$REL/$BASE.epub"
copy output/book.html         "$REL/$BASE.html"
copy output/book-ereader.html "$REL/$BASE-ereader.html"
copy output/markdown/book.md  "$REL/$BASE.md"
copy assets/svg/cover.svg     "$REL/cover.svg"
if [ -d output/markdown ]; then
  mkdir -p "$REL/$BASE-markdown"; cp -r output/markdown/. "$REL/$BASE-markdown/"
  "$PY" - "release/$BASE-markdown.zip" "output/markdown" <<'PY'
import os, sys, zipfile
out, src = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(src):
        for f in files:
            p = os.path.join(root, f); z.write(p, os.path.relpath(p, src))
PY
  echo "  + $BASE-markdown.zip"
fi
copy README.md              "$REL/README.md"
copy docs/RELEASE-NOTES.md   "$REL/修订说明.md"
copy docs/DATA-GAPS.md       "$REL/数据缺口清单.md"
copy docs/OPEN-CONTRIBUTION.md "$REL/欢迎补充数据.md"

cat > "$REL/MANIFEST.txt" <<EOF
$BASE — 发布包清单
==================
$BASE-print.pdf    印刷版 PDF
$BASE-ereader.pdf  电子阅读版 PDF
$BASE.epub         EPUB 3
$BASE.html         网页版
$BASE.md           合并 Markdown
$BASE-markdown/    分文件 Markdown（含 assets）
cover.svg          封面
数据来源与口径.md   数据来源、采集方式与局限
明确不包含：analysis/ 脚本、data/ 原始数据、source/ 源文件、*.py。
EOF

# 清单自检：把目录中未列出的文件补进 MANIFEST（避免清单与实物不一致）
REL_PY="$REL"
if command -v wslpath >/dev/null 2>&1; then REL_PY="$(wslpath -w "$REL")"; fi
"$PY" - "$REL_PY" <<'PY'
import os, sys
rel = sys.argv[1]
mf = os.path.join(rel, "MANIFEST.txt")
text = open(mf, encoding="utf-8").read()
missing = [f for f in sorted(os.listdir(rel)) if f != "MANIFEST.txt" and f not in text]
if missing:
    with open(mf, "a", encoding="utf-8") as f:
        f.write("\n（自动补充：以下文件亦在本包内）\n")
        for m in missing:
            f.write("%-30s %s\n" % (m, "见文件本身"))
PY

BAD=$(find "$REL" -type f \( -name '*.py' -o -name '*.json' -o -name '*.xlsx' -o -name '*.csv' \) || true)
[ -n "$BAD" ] && { echo "ERROR: 发布包含非发布内容："; echo "$BAD"; exit 1; }
echo "== release/ 已生成 =="; ls -lh "$REL"
