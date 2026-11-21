/* CBDC privacy dataset: shared site script. Header, footer, theme, data loading, labels, link builders.
   No build step, no third-party requests: the page talks to nothing but its own files until a visitor clicks
   an outbound link (issuer, Internet Archive, translation service). */
(function () {
  "use strict";
  var S = (window.SITE = {});
  var NAV = [["index.html", "Home"], ["map.html", "Map"], ["documents.html", "Documents"], ["method.html", "Method"], ["data.html", "Data & reuse"], ["about.html", "About"]];
  var here = location.pathname.split("/").pop() || "index.html";

  // theme: follows the system, a visitor may override it (kept only in their browser)
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  var saved = store("theme");
  if (saved === "light" || saved === "dark") document.documentElement.setAttribute("data-theme", saved);
  S.store = store;

  var header = document.querySelector("header.site");
  if (header) {
    header.innerHTML = '<a class="skip" href="#main">Skip to content</a><div class="in"><a class="brand" href="index.html">CBDC <span>privacy</span> dataset</a>' +
      '<nav class="main" aria-label="Main">' + NAV.map(function (n) { return '<a href="' + n[0] + '"' + (n[0] === here ? ' aria-current="page"' : "") + ">" + n[1] + "</a>"; }).join("") + "</nav>" +
      '<button class="theme-btn" type="button" aria-label="Switch colour theme">◐</button></div>';
    header.querySelector(".theme-btn").addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next); store("theme", next);
      document.dispatchEvent(new Event("themechange"));
    });
  }
  var footer = document.querySelector("footer.site");
  if (footer) footer.innerHTML = '<div class="in"><div><strong>Bok, M. &amp; Stroukal, D. (2026).</strong> CBDC privacy dataset (in development). Prague University of Economics and Business.</div>' +
    '<div>Data and documentation CC BY 4.0 · code MIT · source on <a href="https://github.com/BokMartin/cbdc-dataset-v11">GitHub</a>. Official documents are not redistributed: every row links to its issuer.</div>' +
    '<div>No cookies, no analytics, no third-party scripts.</div></div>';

  S.esc = function (s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); };
  S.fmt = function (n) { return n == null ? "" : Number(n).toLocaleString("en-GB"); };
  S.get = function (f) { return fetch(f).then(function (r) { if (!r.ok) throw new Error(f + " " + r.status); return r.json(); }); };

  S.CAT = {
    evidence: { label: "Evidence", long: "Evidence: an official document of the competent body that the measurement reads" },
    inclined: { label: "Inclined", long: "Inclined: an official document the authors lean towards (joint or wholesale work of the competent body); read as a separate layer that can support, never establish, a finding" },
    companion: { label: "Companion", long: "Companion: cited for status, timeline or legal state, never measured" },
    dropped: { label: "Not used", long: "Not used: does not meet the source rule (another issuer, off topic, no bearing on design or status)" },
    wholesale: { label: "Wholesale", long: "Wholesale only: outside the retail frame" },
    candidate: { label: "Candidate", long: "Candidate: found after the collection, awaiting an author's decision" }
  };
  S.CAT_ORDER = ["evidence", "inclined", "companion", "dropped", "wholesale", "candidate"];
  S.STATUS = {
    LIVE: ["Live", "#1b7f5b"], PILOT: ["Pilot", "#4aa37c"], PREPARATION: ["Preparation", "#2f74b5"], EXPLORATION: ["Exploration", "#8fb7dd"],
    PAUSED: ["Paused", "#d39b3a"], DISCONTINUED: ["Discontinued", "#b5523b"], UNRESEARCHED: ["Status not yet checked", "#b9b4a8"],
    NONE: ["No retail project", "#cfcabe"], BANNED: ["Retail CBDC barred by law", "#7d5a8c"], NA: ["Not applicable", "#cfcabe"]
  };
  S.BY = { author: "decided by an author", model: "model proposal, not yet confirmed by an author" };
  S.lang = function (code, meta) { return code ? (meta.languages[code] || code) : "unknown"; };

  // outbound links: nothing is hosted here
  S.archive = function (u) { return "https://web.archive.org/web/" + u; };
  S.targetLang = function () {
    var t = store("tl"); if (t) return t;
    var n = (navigator.language || "en").slice(0, 2).toLowerCase(); return n || "en";
  };
  S.googlePage = function (u, tl) { return "https://translate.google.com/translate?sl=auto&tl=" + encodeURIComponent(tl) + "&u=" + encodeURIComponent(u); };
  S.googleDocs = function (tl) { return "https://translate.google.com/?sl=auto&tl=" + encodeURIComponent(tl) + "&op=docs"; };
  S.deeplDocs = "https://www.deepl.com/translator/files";
})();
