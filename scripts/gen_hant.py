#!/usr/bin/env python3
"""由简体页生成繁体页：index.html → zh-hant/index.html，privacy.html → zh-hant/privacy.html。

依赖：pip install opencc-python-reimplemented
用法：python3 scripts/gen_hant.py（在仓库根目录执行）
简体页是唯一的源文件，繁体页不要手改，改完简体后重新运行本脚本即可。
"""
import re
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://trxglobal.github.io"
cc = OpenCC("s2tw")

# OpenCC 只做字形转换，以下是港台常用词汇的修正
WORDS = {
    "登錄": "登入",
    "賬": "帳",
    "充值": "儲值",
    "域名": "網域",
    "信息": "資訊",
    "程序化": "程式化",
    "默認": "預設",
    "數據": "資料",
    "接口": "介面",
    "郵箱": "電子郵件",
    "搜索": "搜尋",
}

# 语言切换器里的「简体中文」必须保持简体
KEEP = ["简体中文"]


def convert(src: str) -> str:
    placeholders = {}
    for i, word in enumerate(KEEP):
        key = f"\x00KEEP{i}\x00"
        placeholders[key] = word
        src = src.replace(word, key)
    out = cc.convert(src)
    for a, b in WORDS.items():
        out = out.replace(a, b)
    for key, word in placeholders.items():
        out = out.replace(key, word)
    return out


def localize(html: str, page: str) -> str:
    html = html.replace('<html lang="zh-CN">', '<html lang="zh-Hant">')
    html = html.replace('content="zh_CN"', 'content="zh_TW"')
    # canonical 与 og:url 指向繁体页自身
    html = re.sub(
        r'(<link rel="canonical" href=")[^"]*(")',
        rf"\g<1>{BASE}/zh-hant/{'' if page == 'index.html' else page}\g<2>",
        html,
    )
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{BASE}/zh-hant/\g<2>", html)
    # 站内链接：首页与隐私政策改到 /zh-hant/ 下
    html = html.replace('href="/"', 'href="/zh-hant/"').replace('href="/privacy.html"', 'href="/zh-hant/privacy.html"')
    # 语言切换器的链接要保留原目标；上一步把简体入口也改掉了，这里还原
    html = html.replace('href="/zh-hant/" hreflang="zh-CN"', 'href="/" hreflang="zh-CN"')
    # 当前语言标记从简体移到繁体
    html = html.replace(' lang="zh-CN" aria-current="page"', ' lang="zh-CN"')
    html = html.replace('hreflang="zh-Hant" lang="zh-Hant">', 'hreflang="zh-Hant" lang="zh-Hant" aria-current="page">')
    html = html.replace('<span class="lbl">简体中文</span>', '<span class="lbl">繁體中文</span>')
    return html


def main():
    out_dir = ROOT / "zh-hant"
    out_dir.mkdir(exist_ok=True)
    for page in ["index.html", "privacy.html"]:
        src = ROOT / page
        if not src.exists():
            continue
        html = localize(convert(src.read_text(encoding="utf-8")), page)
        (out_dir / page).write_text(html, encoding="utf-8")
        print(f"生成 zh-hant/{page}")


if __name__ == "__main__":
    main()
