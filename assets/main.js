/*
 * 落地页脚本：
 * 1. 把广告带来的 gclid / utm_* 等参数透传到 trxapi.io 的外链上，方便在目标站做来源归因；
 * 2. 点击注册 / 登录按钮时上报 Google Ads 转化（需在下方 CONFIG 填入转化 ID 与标签）。
 */
(function () {
  var CONFIG = {
    // Google Ads 转化 ID，形如 "AW-123456789"；留空则不加载 gtag
    adsId: "",
    // 转化标签，在 Google Ads「目标 → 转化」里创建后获得，形如 "AbCdEfGhIjKlMn"
    registerLabel: "",
    loginLabel: ""
  };

  // 语言下拉：点击页面其他位置或按 Esc 时收起
  document.addEventListener("click", function (e) {
    document.querySelectorAll("details.lsw[open]").forEach(function (d) {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") document.querySelectorAll("details.lsw[open]").forEach(function (d) { d.removeAttribute("open"); });
  });

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

  if (!CONFIG.adsId) return;

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + CONFIG.adsId;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  gtag("js", new Date());
  gtag("config", CONFIG.adsId);

  document.addEventListener("click", function (e) {
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
