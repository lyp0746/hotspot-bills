#!/usr/bin/env bash
# 一键构建：书稿转换 -> 插图/封面 -> 印刷版 PDF -> 电子阅读版 PDF -> EPUB -> Markdown
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f .env.build ] && . ./.env.build
PY="${PYTHON:-python}"


echo "== 1/5 插图与封面 =="
"$PY" analysis/make_figures.py
"$PY" analysis/make_cover.py

echo "== 2/5 印刷版（正式书稿版式）=="
"$PY" build_book.py --pdf

echo "== 3/5 电子阅读版 =="
"$PY" build_book.py --ereader --pdf

echo "== 4/5 EPUB 3 =="
"$PY" build_epub.py

echo "== 5/5 Markdown =="
"$PY" build_markdown.py

echo
echo "完成。产物："
ls -lh output/*.pdf output/*.epub output/*.html output/markdown/book.md 2>/dev/null || true
