# TRX Global · TRON 能量租赁引导页

面向 Google Ads 投放的落地页，把流量引导至 [TRXAPI](https://www.trxapi.io/) 注册 / 登录。纯静态站点，由 GitHub Pages 直接托管。

| 语言 | 地址 |
|---|---|
| 简体中文 | https://trxglobal.github.io/ |
| 繁體中文 | https://trxglobal.github.io/zh-hant/ |
| English | https://trxglobal.github.io/en/ |

## 文件结构

- `index.html` / `privacy.html`：简体中文（繁体页的源文件）
- `zh-hant/`：繁体中文，由脚本生成，**不要手改**
- `en/`：英文，单独维护
- `assets/style.css`、`assets/main.js`：共用样式与脚本

## 修改简体后同步繁体

```bash
pip install opencc-python-reimplemented
python3 scripts/gen_hant.py
```

## 接入 Google Ads 转化跟踪

编辑 `assets/main.js` 顶部的 `CONFIG`：

```js
adsId: "AW-XXXXXXXXX",       // 转化 ID
registerLabel: "xxxxxxxx",   // 「点击注册」转化标签
loginLabel: "xxxxxxxx"       // 「点击登录」转化标签（可留空）
```

留空时不会加载任何 Google 脚本。所有带 `data-out` 属性的链接，都会自动附加来源参数（`gclid`、`utm_*`）后再跳转到 trxapi.io。
