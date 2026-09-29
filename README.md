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
- `assets/style.css`、`assets/main.js`：共用样式与脚本的**源文件**，构建时内联进每个页面
- `assets/flags/`：语言切换器用的国旗（来自 [flag-icons](https://github.com/lipis/flag-icons)，MIT 许可）
- `scripts/build.py`：渲染语言切换器、内联样式与脚本、由简体生成繁体

## 修改页面后重新构建

```bash
pip install opencc-python-reimplemented
python3 scripts/build.py
```

语言切换器仿 PhotonPay 按地区分组，地区与语言的对应关系在 `scripts/build.py` 的 `REGIONS` 中配置。页面里 `<!-- lsw -->…<!-- /lsw -->` 之间的内容由脚本生成，不要手改。

## 接入 Google Ads 转化跟踪

编辑 `assets/main.js` 顶部的 `CONFIG`：

```js
adsId: "AW-XXXXXXXXX",       // 转化 ID
registerLabel: "xxxxxxxx",   // 「点击注册」转化标签
loginLabel: "xxxxxxxx",      // 「点击登录」转化标签（可留空）
contactLabel: "xxxxxxxx"     // 「点击联系渠道」转化标签（可留空）
```

留空时不会加载任何 Google 脚本。所有带 `data-out` 属性的链接，都会自动附加来源参数（`gclid`、`utm_*`）后再跳转到 trxapi.io。

## 为什么样式和脚本是内联的

GitHub Pages 对 HTML 和静态资源各缓存 10 分钟，而且不认 `?v=` 版本参数。外链资源时，访客可能拿到旧 HTML 配新 CSS，页面就会错乱。内联之后，每个页面自带与之匹配的样式和脚本，不会再出现这种情况。

**改完 `assets/` 下任何文件后，都要运行 `python3 scripts/build.py` 再提交。**
