#!/usr/bin/env python3
"""站点构建脚本（在仓库根目录执行：python3 scripts/build.py）

1. 把语言切换器渲染进 index.html、en/index.html（替换 <!-- lsw --> 与 <!-- /lsw --> 之间的内容）；
2. 由简体页生成繁体页：index.html → zh-hant/index.html，privacy.html → zh-hant/privacy.html。

依赖：pip install opencc-python-reimplemented
简体页是繁体页唯一的源文件，繁体页不要手改；改完简体或切换器后重新运行本脚本即可。
"""
import re
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://trxglobal.github.io"
cc = OpenCC("s2tw")

# ── 语言切换器（仿 PhotonPay：按地区分组，圆形国旗 + 地区名 + 可选语言）──

LANG_PATH = {"zh-CN": "/", "zh-Hant": "/zh-hant/", "en": "/en/"}
LANG_NAME = {"zh-CN": "简体中文", "zh-Hant": "繁體中文", "en": "English"}
REGIONS = [
    ("hk", "Hong Kong SAR", ["en", "zh-CN", "zh-Hant"]),
    ("us", "United States", ["en"]),
    ("gb", "United Kingdom", ["en"]),
    ("ca", "Canada", ["en"]),
    ("cn", "Chinese Mainland", ["zh-CN"]),
]
# 没有记住地区时，各语言页默认显示的地区；访客在下拉里选过地区后由 main.js 按记忆切换
DEFAULT_REGION = {"zh-CN": "cn", "zh-Hant": "hk", "en": "us"}
ARIA = {"zh-CN": "切换语言", "zh-Hant": "切換語言", "en": "Change language"}
CHEVRON = '<svg class="c" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'


def flag(code: str) -> str:
    return f'<img class="flag" src="/assets/flags/{code}.svg" alt="" width="24" height="24">'


def render_switcher(lang: str) -> str:
    region = DEFAULT_REGION[lang]
    rows = []
    for code, name, langs in REGIONS:
        tags = '<i></i>'.join(
            f'<a href="{LANG_PATH[l]}" hreflang="{l}" lang="{l}" data-region="{code}"'
            + (' class="on" aria-current="page"' if (code, l) == (region, lang) else "")
            + f">{LANG_NAME[l]}</a>"
            for l in langs
        )
        rows.append(
            f'<li data-region="{code}">{flag(code)}<div><div class="rn">{name}</div><div class="rl">{tags}</div></div></li>'
        )
    return (
        f'<div class="lsw" data-lang="{lang}">'
        f'<button class="lsw-btn" type="button" aria-haspopup="true" aria-expanded="false" aria-label="{ARIA[lang]}">'
        f'{flag(region)}<span class="lbl">{LANG_NAME[lang]}</span>{CHEVRON}</button>'
        f'<div class="lsw-pop"><ul>{"".join(rows)}</ul></div></div>'
    )


def inject_switcher(html: str, lang: str) -> str:
    return re.sub(r"<!-- lsw -->.*?<!-- /lsw -->", lambda _: f"<!-- lsw -->{render_switcher(lang)}<!-- /lsw -->", html, flags=re.S)


# ── 简体 → 繁体 ──

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
    "聯繫": "聯絡",
    "在線": "線上",
}

# 页脚语言链接里的「简体中文」必须保持简体
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
    # 页脚语言链接要保留原目标；上一步把简体入口也改掉了，这里还原，并把当前语言标记移到繁体
    html = html.replace('href="/zh-hant/" hreflang="zh-CN"', 'href="/" hreflang="zh-CN"')
    html = html.replace(' lang="zh-CN" aria-current="page"', ' lang="zh-CN"')
    html = html.replace('hreflang="zh-Hant" lang="zh-Hant">', 'hreflang="zh-Hant" lang="zh-Hant" aria-current="page">')
    # 切换器在转换之后重新渲染，避免地区名、语言名被转换
    return inject_switcher(html, "zh-Hant")


def main():
    for page, lang in [("index.html", "zh-CN"), ("en/index.html", "en")]:
        path = ROOT / page
        path.write_text(inject_switcher(path.read_text(encoding="utf-8"), lang), encoding="utf-8")
        print(f"更新切换器 {page}")

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
