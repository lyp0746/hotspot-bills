# -*- coding: utf-8 -*-
"""create_github_release.py — 单一 release、单一 tag，承载全部发布产物。

模型
----
本仓库采用**一个 release、一个 tag**：tag 形如 ``<prefix>-<YYYY-MM-DD>``（日期作后缀），
一个 release 承载全部读者面产物（印刷版/电子阅读版 PDF、EPUB、HTML、Markdown、封面、文档）。
若需“一个产物一个 tag”，改用 ``create_github_release_per_artifact.py``。

用法
----
    python scripts/create_github_release.py --date 2026-10-14
    python scripts/create_github_release.py --date 2026-10-14 --draft
    python scripts/create_github_release.py --list
    python scripts/create_github_release.py --verify
"""
import argparse
import os
import subprocess
import sys
import time

import requests

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = os.environ.get("GIT_BIN", r"D:\Git\cmd\git.exe")

REPO_DEFAULT = "lyp0746/hotspot-bills"
BOOK = "热点的账单"

# (源文件, GitHub 资产名) —— 一个 release 的资产清单
ASSETS = [
    ("release/hotspot-bills-print.pdf", "hotspot-bills-print.pdf"),
    ("release/hotspot-bills-ereader.pdf", "hotspot-bills-ereader.pdf"),
    ("release/mind-forks.epub", "mind-forks.epub"),
    ("release/mind-forks.html", "mind-forks.html"),
    ("release/hotspot-bills-ereader.html", "hotspot-bills-ereader.html"),
    ("release/mind-forks.md", "mind-forks.md"),
    ("release/hotspot-bills-markdown.zip", "hotspot-bills-markdown.zip"),
    ("release/cover.svg", "cover.svg"),
    ("release/README.md", "README.md"),
    ("release/修订说明.md", "REVISION-NOTES.md"),
    ("release/数据缺口清单.md", "DATA-GAPS.md"),
    ("release/欢迎补充数据.md", "CONTRIBUTING-DATA.md"),
]


def get_token():
    out = subprocess.run(
        [GIT, "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    for line in out.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):].strip()
    raise SystemExit("未能从 git credential helper 取得 token")


def api(tok, method, url, extra_headers=None, **kw):
    headers = {
        "Authorization": f"token {tok}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "capacity-cascade-release"}
    if extra_headers:
        headers.update(extra_headers)
    return requests.request(method, url, headers=headers, timeout=180, **kw)


def release_body():
    return ("《热点的账单：从无意识到可观察——心理学流派的六次划线》发布产物（本 release 承载全部格式）：\n"
            "- 印刷版 PDF（A4）、电子阅读版 PDF（B5）\n"
            "- EPUB 3、网页版 HTML、电子阅读 HTML、合并 Markdown、分文件 Markdown（zip）\n"
            "- 封面 SVG、读者说明、修订说明、数据缺口、开放贡献指南\n\n"
            "内容许可 CC BY 4.0；代码许可 MIT。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--date", default="", help="版本日期，如 2026-10-14")
    ap.add_argument("--tag-prefix", default="edition")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--prerelease", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    if args.list or (not args.date and not args.verify):
        print("单一 release 模型；资产清单：")
        for src, dst in ASSETS:
            exists = "√" if os.path.exists(os.path.join(HERE, src)) else "×"
            print(f"  [{exists}] {dst:34s} <- {src}")
        return
    if args.verify and not args.date:
        raise SystemExit("--verify 需要 --date <YYYY-MM-DD>（指定要校验的 tag）")

    tag = f"{args.tag_prefix}-{args.date}"
    tok = get_token()
    base = f"https://api.github.com/repos/{args.repo}"
    name = f"{BOOK} · {args.date}"

    if args.verify:
        r = api(tok, "GET", f"{base}/releases/tags/{tag}")
        if r.status_code != 200:
            print(f"[缺 release] {tag}")
            sys.exit(1)
        rel = r.json()
        have = {a["name"] for a in rel.get("assets", [])}
        missing = [d for _, d in ASSETS if d not in have]
        print(f"release {tag}: {len(have)} 个资产；缺失 {missing or '无'}")
        sys.exit(0 if not missing else 1)

    r = api(tok, "GET", f"{base}/releases/tags/{tag}")
    if r.status_code == 200:
        rel = r.json()
        print(f"[reuse] release {tag} id={rel['id']}")
    else:
        r = api(tok, "POST", f"{base}/releases",
                json={"tag_name": tag, "name": name, "body": release_body(),
                      "draft": args.draft, "prerelease": args.prerelease,
                      "make_latest": "true"})
        if r.status_code not in (200, 201):
            raise SystemExit(f"创建 release 失败：{r.status_code} {r.text[:300]}")
        rel = r.json()
        print(f"[new] release {tag} id={rel['id']} (Latest)")

    have = {a["name"] for a in rel.get("assets", [])}
    for src, dst in ASSETS:
        if dst in have:
            print(f"  [have] {dst}")
            continue
        p = os.path.join(HERE, src)
        if not os.path.exists(p):
            print(f"  [skip] 缺文件 {src}")
            continue
        with open(p, "rb") as fh:
            data = fh.read()
        up = None
        for attempt in range(4):
            try:
                up = api(tok, "POST",
                         f"https://uploads.github.com/repos/{args.repo}/releases/{rel['id']}/assets",
                         params={"name": dst}, data=data,
                         extra_headers={"Content-Type": "application/octet-stream"})
                break
            except requests.exceptions.RequestException as e:
                print(f"  [retry {attempt+1}/4] {dst}（{type(e).__name__}）")
                time.sleep(3 * (attempt + 1))
        if up is None:
            print(f"  [FAIL] {dst} 上传失败（网络）")
            continue
        print(f"  [{'ok' if up.status_code in (200,201) else 'FAIL'}] {dst}"
              + ("" if up.status_code in (200, 201) else f" {up.status_code} {up.text[:200]}"))
    print("release 页面：", rel.get("html_url"))


if __name__ == "__main__":
    main()
