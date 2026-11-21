/* Documents page: filter, sort and link every document of site/assets/documents.json. State lives in the URL hash. */
(function () {
  "use strict";
  var S = window.SITE, $ = function (id) { return document.getElementById(id); };
  var PAGE = 60;
  var TL = [["en", "English"], ["cs", "Czech"], ["de", "German"], ["fr", "French"], ["es", "Spanish"], ["it", "Italian"], ["pl", "Polish"], ["pt", "Portuguese"], ["zh-CN", "Chinese"], ["ja", "Japanese"], ["ru", "Russian"], ["uk", "Ukrainian"], ["ar", "Arabic"]];

  Promise.all([S.get("assets/documents.json"), S.get("assets/projects.json")]).then(function (r) { init(r[0], r[1]); })
    .catch(function (e) { $("rows").innerHTML = '<tr><td colspan="6" class="empty">Could not load the document list (' + S.esc(e.message) + ").</td></tr>"; });

  function init(DD, PP) {
    var docs = DD.documents, meta = DD.meta, P = {};
    PP.projects.forEach(function (p) { P[p.code] = p; });
    var byId = {}; docs.forEach(function (d) { byId[d.id] = d; });
    $("as-of").innerHTML = "<strong>State of " + meta.as_of + ".</strong> No result of the measurement is shown here: the dataset is still being built and no model has classified the documents yet. This page lists the corpus and the authors' decisions on it.";

    // controls
    var codes = Object.keys(P).sort(function (a, b) { return (P[b].frame - P[a].frame) || P[a].name.localeCompare(P[b].name); });
    var framed = codes.filter(function (c) { return P[c].frame; }), other = codes.filter(function (c) { return !P[c].frame; });
    $("project").innerHTML += '<optgroup label="The 44 projects">' + framed.map(opt).join("") + '</optgroup><optgroup label="Outside the frame">' + other.map(opt).join("") + "</optgroup>";
    function opt(c) { return '<option value="' + c + '">' + S.esc(P[c].name) + " (" + docs.filter(function (d) { return d.p === c; }).length + ")</option>"; }
    var langs = {}; docs.forEach(function (d) { if (d.l) langs[d.l] = (langs[d.l] || 0) + 1; });
    $("lang").innerHTML += Object.keys(langs).sort(function (a, b) { return langs[b] - langs[a]; }).map(function (l) { return '<option value="' + l + '">' + S.esc(S.lang(l, meta)) + " (" + langs[l] + ")</option>"; }).join("");
    var kinds = {}; docs.forEach(function (d) { if (d.k) kinds[d.k] = (kinds[d.k] || 0) + 1; });
    $("kind").innerHTML += Object.keys(kinds).sort().map(function (k) { return '<option value="' + S.esc(k) + '">' + S.esc(k) + " (" + kinds[k] + ")</option>"; }).join("");
    var tl = S.targetLang(); if (!TL.some(function (x) { return x[0] === tl; })) TL.unshift([tl, tl]);
    $("tl").innerHTML = TL.map(function (x) { return '<option value="' + x[0] + '"' + (x[0] === tl ? " selected" : "") + ">" + x[1] + "</option>"; }).join("");
    $("legend").innerHTML = S.CAT_ORDER.map(function (c) { var t = S.CAT[c].long.split(": "); return '<dt><span class="badge b-' + c + '">' + S.CAT[c].label + "</span></dt><dd>" + S.esc(t[1]) + "</dd>"; }).join("") +
      '<dt><span class="badge b-evidence">Evidence · borderline</span></dt><dd>Evidence the authors kept although it sits near the edge of the rule (for example, staff research that may corroborate but never establish).</dd>';

    var count = {}; docs.forEach(function (d) { count[d.c] = (count[d.c] || 0) + 1; });
    $("cats").innerHTML = S.CAT_ORDER.map(function (c) { return '<button type="button" class="chip" data-c="' + c + '" aria-pressed="false" title="' + S.esc(S.CAT[c].long) + '"><span class="badge b-' + c + '">' + S.CAT[c].label + '</span><span class="n">' + count[c] + "</span></button>"; }).join("");

    var st = { q: "", project: "", lang: "", en: "", by: "", kind: "", y0: "", y1: "", cats: [], sort: "y", dir: -1, shown: PAGE };
    readHash();
    function readHash() {
      var h = new URLSearchParams(location.hash.slice(1));
      ["q", "project", "lang", "en", "by", "kind", "y0", "y1"].forEach(function (k) { st[k] = h.get(k) || ""; $(k).value = st[k]; });
      st.cats = (h.get("c") || "").split(",").filter(Boolean);
      if (h.get("s")) { st.sort = h.get("s").replace("-", ""); st.dir = h.get("s")[0] === "-" ? -1 : 1; }
    }
    function writeHash() {
      var h = new URLSearchParams();
      ["q", "project", "lang", "en", "by", "kind", "y0", "y1"].forEach(function (k) { if (st[k]) h.set(k, st[k]); });
      if (st.cats.length) h.set("c", st.cats.join(","));
      if (!(st.sort === "y" && st.dir === -1)) h.set("s", (st.dir < 0 ? "-" : "") + st.sort);
      var s = h.toString(); history.replaceState(null, "", s ? "#" + s : location.pathname);
    }
    ["q", "project", "lang", "en", "by", "kind", "y0", "y1"].forEach(function (k) {
      $(k).addEventListener("input", function () { st[k] = $(k).value.trim(); st.shown = PAGE; render(); });
    });
    $("tl").addEventListener("change", function () { tl = $("tl").value; S.store("tl", tl); render(); });
    $("cats").addEventListener("click", function (e) {
      var b = e.target.closest(".chip"); if (!b) return;
      var c = b.getAttribute("data-c"), i = st.cats.indexOf(c);
      if (i < 0) st.cats.push(c); else st.cats.splice(i, 1);
      st.shown = PAGE; render();
    });
    $("reset").addEventListener("click", function () { ["q", "project", "lang", "en", "by", "kind", "y0", "y1"].forEach(function (k) { st[k] = ""; $(k).value = ""; }); st.cats = []; st.shown = PAGE; render(); });
    $("more").addEventListener("click", function () { st.shown += PAGE * 2; render(); });
    document.querySelectorAll("table.docs th[data-k] button").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.parentNode.getAttribute("data-k");
        if (st.sort === k) st.dir = -st.dir; else { st.sort = k; st.dir = k === "y" ? -1 : 1; }
        render();
      });
    });
    window.addEventListener("hashchange", function () { readHash(); render(); });
    document.addEventListener("click", function (e) {
      var m = e.target.closest(".menu > button");
      document.querySelectorAll(".menu-pop").forEach(function (p) { if (!m || p !== m.nextElementSibling) p.hidden = true; });
      if (m) { var pop = m.nextElementSibling; pop.hidden = !pop.hidden; m.setAttribute("aria-expanded", String(!pop.hidden)); }
      var f = e.target.closest("[data-goto]");
      if (f) { e.preventDefault(); location.hash = "q=" + encodeURIComponent(f.getAttribute("data-goto")); }
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") document.querySelectorAll(".menu-pop").forEach(function (p) { p.hidden = true; }); });

    var current = [];
    function match(d) {
      if (st.cats.length && st.cats.indexOf(d.c) < 0) return false;
      if (st.project && d.p !== st.project) return false;
      if (st.lang && d.l !== st.lang) return false;
      if (st.en && d.en !== st.en) return false;
      if (st.by && d.by !== st.by) return false;
      if (st.kind && d.k !== st.kind) return false;
      if (st.y0 && (!d.y || d.y < +st.y0)) return false;
      if (st.y1 && (!d.y || d.y > +st.y1)) return false;
      if (st.q) {
        var hay = (d.t + " " + d.iss + " " + d.id + " " + (P[d.p] ? P[d.p].name : "") + " " + d.k).toLowerCase();
        return st.q.toLowerCase().split(/\s+/).every(function (w) { return hay.indexOf(w) >= 0; });
      }
      return true;
    }
    function key(d) {
      switch (st.sort) {
        case "t": return d.t.toLowerCase();
        case "p": return P[d.p] ? P[d.p].name : d.p;
        case "c": return S.CAT_ORDER.indexOf(d.c) + (d.bl ? 0.5 : 0);
        case "l": return S.lang(d.l, meta);
        default: return d.y || 0;
      }
    }
    function render() {
      writeHash();
      document.querySelectorAll("#cats .chip").forEach(function (b) { b.setAttribute("aria-pressed", String(st.cats.indexOf(b.getAttribute("data-c")) >= 0)); });
      document.querySelectorAll("table.docs th[data-k]").forEach(function (th) {
        if (th.getAttribute("data-k") === st.sort) th.setAttribute("aria-sort", st.dir > 0 ? "ascending" : "descending"); else th.removeAttribute("aria-sort");
      });
      current = docs.filter(match).sort(function (a, b) {
        var x = key(a), y = key(b); if (x < y) return -st.dir; if (x > y) return st.dir;
        return (b.y || 0) - (a.y || 0) || a.t.localeCompare(b.t);
      });
      var pubs = {}; current.forEach(function (d) { if (d.c === "evidence") pubs[d.same || d.id] = 1; });
      $("count").innerHTML = "<strong>" + S.fmt(current.length) + "</strong> of " + S.fmt(docs.length) + " documents" +
        (Object.keys(pubs).length ? " · " + Object.keys(pubs).length + " evidence publications" : "");
      $("rows").innerHTML = current.length ? current.slice(0, st.shown).map(row).join("") : '<tr><td colspan="6" class="empty">No document matches these filters.</td></tr>';
      $("more").hidden = current.length <= st.shown;
      $("more").textContent = "Show more (" + (current.length - st.shown) + " left)";
    }

    function row(d) {
      var p = P[d.p] || { name: d.p };
      var title = d.u ? '<a href="' + S.esc(d.u) + '" target="_blank" rel="noopener">' + S.esc(d.t) + "</a>" : S.esc(d.t);
      var sub = [d.iss, d.k, d.pg ? d.pg + " pages" : ""].filter(Boolean).map(S.esc).join(" · ");
      var links = [];
      if (d.u) {
        links.push('<a href="' + S.esc(d.u) + '" target="_blank" rel="noopener" title="Open the issuer\'s copy">Original ↗</a>');
        links.push('<a href="' + S.esc(S.archive(d.u)) + '" target="_blank" rel="noopener" title="Archived copy at the Internet Archive (Wayback Machine)">Archive</a>');
      } else links.push('<span class="off" title="No public URL recorded; the file is identified by its SHA-256">No link</span>');
      if (d.ue) links.push('<a href="' + S.esc(d.ue) + '" target="_blank" rel="noopener" title="English edition published by the issuer">English edition ↗</a>');
      if (d.tr) links.push('<a href="translation.html?id=' + encodeURIComponent(d.id) + '" title="Our English machine translation, published because the issuer\'s licence allows reuse">English translation</a>');
      if (d.u && d.l && d.l !== "en" && d.l !== tl.slice(0, 2)) links.push(translateMenu(d));
      var extra = "<dl class='kv'><dt>ID</dt><dd class='mono'>" + S.esc(d.id) + "</dd>" +
        (d.sha ? "<dt>SHA-256</dt><dd class='mono'>" + S.esc(d.sha) + "</dd>" : "") +
        (d.ext ? "<dt>File</dt><dd>" + S.esc(d.ext.toUpperCase()) + (d.pg ? ", " + d.pg + " pages" : "") + "</dd>" : "") +
        (d.c === "evidence" ? "<dt>English text</dt><dd>" + S.esc(d.en) + "</dd>" : "") +
        (d.same ? "<dt>Same publication as</dt><dd><a href='#' data-goto='" + S.esc(d.same) + "'>" + S.esc(byId[d.same] ? byId[d.same].t : d.same) + "</a></dd>" : "") +
        (d.role ? "<dt>Companion role</dt><dd>" + S.esc(d.role) + "</dd>" : "") +
        (d.link.length ? "<dt>Linked evidence</dt><dd>" + d.link.map(function (i) { return "<a href='#' data-goto='" + S.esc(i) + "'>" + S.esc(byId[i] ? byId[i].y + " · " + byId[i].t : i) + "</a>"; }).join("<br>") + "</dd>" : "") +
        (d.tf ? "<dt>Title</dt><dd>taken from the file name, to be checked</dd>" : "") +
        (d.tm ? "<dt>Title</dt><dd>read from the document's first pages, not yet checked by an author</dd>" : "") + "</dl>";
      return "<tr>" +
        '<td class="y" data-l="Year">' + (d.y || "n.d.") + "</td>" +
        '<td><div class="dt">' + title + (d.tf ? ' <span class="muted small">(from file name)</span>' : "") + '</div><div class="dm">' + sub + '</div><details class="more"><summary>Details</summary>' + extra + "</details></td>" +
        '<td><a href="map.html#' + d.p + '">' + S.esc(p.name) + "</a></td>" +
        '<td><span class="badge b-' + d.c + '">' + S.CAT[d.c].label + (d.bl ? " · borderline" : "") + '</span><span class="by ' + d.by + '">' + S.BY[d.by] + "</span></td>" +
        '<td class="y" data-l="Language">' + S.esc(S.lang(d.l, meta)) + "</td>" +
        '<td><div class="links">' + links.join("") + "</div></td></tr>";
    }
    function translateMenu(d) {
      var tname = ($("tl").selectedOptions[0] || {}).textContent || tl;
      var page = d.ext === "pdf" || /\.pdf($|\?)/i.test(d.u) ? "" : '<a href="' + S.esc(S.googlePage(d.u, tl)) + '" target="_blank" rel="noopener">Open the page translated (Google Translate)</a>';
      return '<span class="menu"><button type="button" aria-haspopup="true" aria-expanded="false">Translate</button><div class="menu-pop" hidden>' +
        "<p>Into " + S.esc(tname) + ". The translation is made by the service you choose, from the issuer's copy; we send it nothing.</p>" + page +
        '<a href="' + S.esc(S.googleDocs(tl)) + '" target="_blank" rel="noopener">Translate the file in Google Translate (upload the downloaded original)</a>' +
        '<a href="' + S.esc(S.deeplDocs) + '" target="_blank" rel="noopener">Translate the file in DeepL (upload the downloaded original)</a>' +
        "<p>Machine translation can change meaning and strength. Quote the original.</p></div></span>";
    }

    $("dl-filtered").addEventListener("click", function (e) {
      var cols = ["id", "p", "y", "t", "tm", "iss", "k", "c", "bl", "by", "l", "pg", "en", "trf", "u", "ue", "same", "role", "link", "sha"];
      var head = ["id", "project", "year", "title", "title_read_by_model_unchecked", "issuer", "kind", "decision", "borderline", "decided_by", "language", "pages", "english_text", "published_translation", "url", "issuer_english_edition_url", "same_publication_as", "companion_role", "linked_evidence", "sha256"];
      var q = function (v) { v = Array.isArray(v) ? v.join(";") : v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
      var csv = [head.join(",")].concat(current.map(function (d) { return cols.map(function (c) { return q(c === "trf" ? (d.tr ? d.tr.f : "") : d[c]); }).join(","); })).join("\n") + "\n";
      this.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    });
    render();
  }
})();
