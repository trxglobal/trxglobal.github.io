/*
 * 落地页脚本：
 * 1. 把广告带来的 gclid / utm_* 等参数透传到 trxapi.io 的外链上，方便在目标站做来源归因；
 * 2. 点击注册 / 登录 / 联系渠道时上报 Google Ads 转化（需在下方 CONFIG 填入转化标签）。
 * gtag.js 由 scripts/build.py 写在每个页面 <head> 最前面（ID 见 build.py 的 GTAG_ID），这里只负责上报事件。
 */
(function () {
  var CONFIG = {
    // Google Ads 转化 ID，须与 build.py 的 GTAG_ID 一致
    adsId: "AW-18481729310",
    // 转化标签，在 Google Ads「目标 → 转化」里创建后获得，形如 "AbCdEfGhIjKlMn"
    registerLabel: "",
    loginLabel: "",
    // 点击任一联系渠道（Telegram / WhatsApp / 在线客服等）的转化标签，可留空
    contactLabel: ""
  };

  // 语言切换：点击按钮展开（触屏设备）；点击页面其他位置或按 Esc 收起
  var lsw = document.querySelector(".lsw");
  if (lsw) {
    var btn = lsw.querySelector(".lsw-btn");
    var setOpen = function (open) {
      lsw.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    };
    btn.addEventListener("click", function () { setOpen(!lsw.classList.contains("open")); });
    document.addEventListener("click", function (e) { if (!lsw.contains(e.target)) setOpen(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setOpen(false); });

    // 同一语言可能属于多个地区（如 English 对应香港 / 美国 / 英国 / 加拿大），
    // 记住访客选的地区，下次打开时按钮显示对应国旗，并高亮该地区下的当前语言
    var REGION_KEY = "trxg_region";
    var pageLang = lsw.getAttribute("data-lang");
    lsw.addEventListener("click", function (e) {
      var link = e.target.closest("a[data-region]");
      var row = e.target.closest("li[data-region]");
      if (!link && row) link = row.querySelector("a[data-region]"); // 点整行等同于点该地区第一个语言
      if (!link) return;
      try { localStorage.setItem(REGION_KEY, link.getAttribute("data-region")); } catch (err) {}
      if (link !== e.target) location.href = link.href;
    });
    var saved = null;
    try { saved = localStorage.getItem(REGION_KEY); } catch (err) {}
    var match = saved && lsw.querySelector('a[data-region="' + saved + '"][lang="' + pageLang + '"]');
    if (match) {
      var cur = lsw.querySelector(".rl a.on");
      if (cur) { cur.classList.remove("on"); cur.removeAttribute("aria-current"); }
      match.classList.add("on");
      match.setAttribute("aria-current", "page");
      btn.querySelector(".flag").src = "/assets/flags/" + saved + ".svg";
    }
  }

  var PASS_KEYS = ["gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
  var STORE_KEY = "trxg_attr";

  // 读取本次落地参数；没有则沿用本次会话里第一次落地时记下的参数
  var params = {};
  var qs = new URLSearchParams(location.search);
  PASS_KEYS.forEach(function (k) { if (qs.get(k)) params[k] = qs.get(k); });
  try {
    if (Object.keys(params).length) sessionStorage.setItem(STORE_KEY, JSON.stringify(params));
    else params = JSON.parse(sessionStorage.getItem(STORE_KEY) || "{}");
  } catch (e) { /* 隐私模式下 sessionStorage 可能不可用，忽略即可 */ }

  // 未投放广告的自然流量也打上来源，便于在 trxapi.io 后台区分
  if (!params.utm_source) {
    params.utm_source = "trxglobal";
    params.utm_medium = params.gclid ? "cpc" : "referral";
  }

  document.querySelectorAll("a[data-out]").forEach(function (a) {
    var url = new URL(a.href);
    Object.keys(params).forEach(function (k) {
      if (!url.searchParams.has(k)) url.searchParams.set(k, params[k]);
    });
    a.href = url.toString();
  });

  if (!CONFIG.adsId || typeof window.gtag !== "function") return;

  document.addEventListener("click", function (e) {
    var c = e.target.closest && e.target.closest("a[data-contact]");
    if (c) {
      // 联系渠道都在新标签页打开，直接上报即可，不影响跳转
      if (CONFIG.contactLabel) gtag("event", "conversion", { send_to: CONFIG.adsId + "/" + CONFIG.contactLabel });
      return;
    }
    var a = e.target.closest && e.target.closest("a[data-out]");
    if (!a) return;
    var label = a.dataset.out === "register" ? CONFIG.registerLabel : CONFIG.loginLabel;
    if (!label) return;
    // 新标签页打开时不阻塞跳转；同页跳转则等上报完成（最多 800ms）
    var href = a.href;
    var sameTab = a.target !== "_blank" && !e.metaKey && !e.ctrlKey;
    var done = false;
    var go = function () { if (!done) { done = true; if (sameTab) location.href = href; } };
    if (sameTab) e.preventDefault();
    gtag("event", "conversion", { send_to: CONFIG.adsId + "/" + label, event_callback: go });
    if (sameTab) setTimeout(go, 800);
  });
})();
