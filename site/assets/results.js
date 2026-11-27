/* Privacy index page. Reads assets/results.json (scripts/site/build_results_site.py). Rows by tier and name, never by value. */
(function () {
  "use strict";
  var S = window.SITE, $ = function (id) { return document.getElementById(id); };
  var CELL = {
    F1: "Central bank can link online payments to a person", F2: "Intermediary can link online payments to a person",
    F3: "Lawful access route", F4: "Private offline payments available", F7: "Low-identity route",
    F8: "Identity required at onboarding", F9: "Targeted re-identification possible", F10: "Programmable restrictions"
  };
  var VERDICT = { holds: "holds", fails: "does not hold", inconclusive: "inconclusive" };
  var AGREE = { all3: "all three agree", partial: "one or two give a value, none contradicts", conflict: "models disagree", none: "no model gives a value" };
  function pct(x) { return x == null ? "–" : Math.round(100 * x) + "%"; }
  function yn(b) { return b ? "yes" : "no"; }

  S.get("assets/results.json").then(function (R) {
    S.prelim(R.meta); S.provenance(R.meta);
    var rule = "prov";

    function hyp() {
      var H = R.hypothesis;
      if (!H.prov) {  /* no verdict written: core projects withheld or the combination rule undecided */
        var shown = R.projects.filter(function (p) { return H.shown.indexOf(p.id) >= 0; });
        $("hyp").innerHTML = '<div class="card"><div class="small muted">Verdict</div><div class="verdict v-inconclusive">not yet given</div>' +
          "<p class='small'>" + S.esc(H.reason) + "</p>" +
          "<p class='small'>Core projects: " + H.n + ". Withheld until the authors' verification: " + H.withheld.length + (H.withheld.length ? " (" + H.withheld.map(function (c) { var p = R.projects.filter(function (x) { return x.id === c; })[0]; return S.esc(p ? p.name : c); }).join(", ") + ")" : "") + ". " +
          "Shown: " + (shown.length ? shown.map(function (p) { return S.esc(p.name) + " (meets both at L · U, " + (rule === "prov" ? "provisional" : "strict") + ": " + yn(p.talk.h[rule][0]) + " · " + yn(p.talk.h[rule][1]) + ")"; }).join("; ") : "none") + ".</p></div>";
        return;
      }
      $("hyp").innerHTML = ["prov", "strict"].map(function (k) {
        var h = R.hypothesis[k], n = h.n;
        return '<div class="card' + (k === rule ? " on" : "") + '"><div class="small muted">' + (k === "prov" ? "Provisional reading" : "Strict reading") + "</div>" +
          '<div class="verdict v-' + h.verdict + '">' + VERDICT[h.verdict] + "</div>" +
          '<div class="lu" role="img" aria-label="L ' + h.L + ", U " + h.U + ' of ' + n + '"><span class="lu-range" style="left:' + (100 * h.L / n) + "%;width:" + (100 * (h.U - h.L) / n) + '%"></span><span class="lu-maj" style="left:' + (100 * 8.5 / n) + '%"><i>9 of ' + n + "</i></span>" +
          '<span class="lu-tick" style="left:' + (100 * h.L / n) + '%">L ' + h.L + '</span><span class="lu-tick" style="left:' + (100 * h.U / n) + '%">U ' + h.U + "</span></div>" +
          '<div class="lu-axis"><span>0</span><span>' + n + " core projects</span></div></div>";
      }).join("");
    }

    /* At a glance: every project in blocks by tier, one coloured square per cell (like the results PDF of 24 Nov). */
    var GCOLS = ["F1", "F2", "F4", "F7", "F8", "F9", "F10", "F3"];
    var GHEAD = { F1: "Central bank sees who pays", F2: "Intermediary sees who pays", F4: "Private offline mode", F7: "Low-identity route", F8: "ID needed to open a wallet", F9: "Re-identification process", F10: "Programmable restrictions", F3: "Lawful access route" };
    var PROT = { F1: "no", F2: "no", F4: "yes", F7: "yes", F8: "no", F9: "no", F10: "no" };
    function gcell(p, f) {
      var c = p.cells[f], v = c[rule], n = 0;
      if (c.agree === "conflict") return '<td><span class="gc g-conf" title="' + S.esc(f + ": the models disagree") + '">≠</span></td>';
      if (!v) return '<td><span class="gc g-un" title="' + S.esc(f + ": no value" + (rule === "strict" && c.prov ? " in the strict reading" : "")) + '">·</span></td>';
      S.MODELS.forEach(function (m) { if (c.models[m[0]].v === v) n++; });
      var cls = f === "F3" ? "g-cat" : (v === PROT[f] ? "g-pro" : "g-non") + (n === 3 ? "3" : "");
      return '<td><span class="gc ' + cls + '" title="' + S.esc(f + ": " + (S.VAL[v] || v) + ", " + n + " of 3 models") + '">' + S.esc(S.VAL[v] || v) + "<sup>" + n + "/3</sup></span></td>";
    }
    function glance() {
      var head = "<thead><tr><th scope='col' class='gp'>Project</th>" + GCOLS.map(function (f) { return "<th scope='col'><b>" + f + "</b><span>" + GHEAD[f] + "</span></th>"; }).join("") +
        "<th scope='col'><b>Index</b><span>7 cells, " + (rule === "prov" ? "provisional" : "strict") + "</span></th><th scope='col'><b>Legal basis</b><span>of the CBDC</span></th></tr></thead>";
      $("glance").innerHTML = ["T1", "T2", "T3"].map(function (t) {
        var ps = rows.filter(function (p) { return p.tier === t; });
        if (!ps.length) return "";
        var body = ps.map(function (p) {
          var name = "<th scope='row' class='gp'>" + S.esc(p.name) + "</th>";
          if (p.masked) return "<tr class='gmask'>" + name + "<td colspan='" + (GCOLS.length + 1) + "'><span class='gc g-mask'>withheld until the authors' verification</span></td><td class='glb' title='Legal basis of the CBDC: being collected'>pending</td></tr>";
          return '<tr tabindex="0" data-id="' + S.esc(p.id) + '">' + name + GCOLS.map(function (f) { return gcell(p, f); }).join("") +
            "<td class='gix'>" + S.ivbar(p.index[rule], "thin") + "</td><td class='glb' title='Legal basis of the CBDC: being collected'>pending</td></tr>";
        }).join("");
        return "<section class='card glance'><h3>" + S.esc(S.TIERLABEL[t] || t) + " <span class='small muted'>" + ps.length + " projects</span></h3><div class='scroll-x'><table class='gtable'><colgroup><col class='c-p'>" + GCOLS.map(function () { return "<col>"; }).join("") + "<col class='c-ix'><col class='c-lb'></colgroup>" + head + "<tbody>" + body + "</tbody></table></div></section>";
      }).join("") + "<p class='small muted'>Click a project for the quotation behind each square. The superscript counts the models that give the value shown. The legal basis of each CBDC (ordinary law, constitution or other) is being collected and will appear in the last column.</p>";
    }
    var rows = R.projects.slice().sort(function (a, b) { return a.tier.localeCompare(b.tier) || a.name.localeCompare(b.name); });
    function paint() {
      var f = $("tier-filter").value, last = "";
      document.querySelector("#rtable tbody").innerHTML = rows.filter(function (p) {
        return f === "all" || (f === "core" ? (p.tier === "T1" || p.tier === "T2") : p.tier === f);
      }).map(function (p) {
        var t = p.talk, head = "", ix = p.index;
        if (p.tier !== last) { last = p.tier; head = '<tr class="grp"><th colspan="9" scope="rowgroup">' + S.esc(S.TIERLABEL[p.tier] || p.tier) + "</th></tr>"; }
        if (p.masked) return head + '<tr class="masked" id="p-' + S.esc(p.id) + '"><td><b>' + S.esc(p.name) + "</b><div class='small muted'>" + S.esc(p.tier) + "</div></td><td colspan='8' class='muted small'>Withheld until the authors' verification. The authors are checking the cells of this project against the sources without seeing the models' answers, so no model value is published yet.</td></tr>";
        var models = S.MODELS.map(function (m) { return "<div class='mrow'><span class='small muted'>" + m[1] + "</span>" + S.ivbar(ix.models[m[0]], "thin") + "</div>"; }).join("");
        var h = t && (p.tier === "T1" || p.tier === "T2") ? yn(t.h[rule][0]) + " · " + yn(t.h[rule][1]) : "<span class='muted'>–</span>";
        return head + '<tr tabindex="0" data-id="' + S.esc(p.id) + '" id="p-' + S.esc(p.id) + '">' +
          "<td><b>" + S.esc(p.name) + "</b><div class='small muted'>" + S.esc(p.tier) + (p.tier === "T3" ? " · exploratory" : "") + "</div></td>" +
          "<td class='ivc'>" + S.ivbar(ix[rule]) + "<div class='small muted'>" + ix["det_" + rule] + " of 7 cells determined</div></td>" +
          "<td class='ivc'>" + (rule === "prov" ? S.ivbar(ix.prov4, "thin") : "<span class='muted small'>provisional only</span>") + "</td>" +
          "<td class='ivc'>" + models + "</td>" +
          "<td>" + S.esc(S.VAL[p.f3[rule]] || p.f3[rule] || "–") + "</td>" +
          "<td class='n'>" + (t ? t.per100[0].toFixed(1) + (t.per100[1] !== t.per100[0] ? "–" + t.per100[1].toFixed(1) : "") + "<div class='small muted'>" + t.pubs + " publications</div>" : "–") + "</td>" +
          "<td class='n'>" + (t ? pct(t.mech) + " · " + pct(t.dec) : "–") + "</td>" +
          "<td class='n'>" + (t ? (t.gap[0] === t.gap[1] ? t.gap[0] : t.gap[0] + "–" + t.gap[1]) + " of 6" : "–") + "</td>" +
          "<td>" + h + "</td></tr>";
      }).join("");
    }
    $("rule").addEventListener("change", function () { rule = this.value; hyp(); glance(); paint(); });
    $("glance").addEventListener("click", function (e) { var tr = e.target.closest("tr[data-id]"); if (tr) detail(tr.getAttribute("data-id")); });
    $("glance").addEventListener("keydown", function (e) { var tr = e.target.closest("tr[data-id]"); if (tr && e.key === "Enter") detail(tr.getAttribute("data-id")); });
    $("tier-filter").addEventListener("change", paint);
    var tb = document.querySelector("#rtable tbody");
    tb.addEventListener("click", function (e) { var tr = e.target.closest("tr[data-id]"); if (tr) detail(tr.getAttribute("data-id")); });
    tb.addEventListener("keydown", function (e) { var tr = e.target.closest("tr[data-id]"); if (tr && e.key === "Enter") detail(tr.getAttribute("data-id")); });

    function detail(id) {
      var p = R.projects.filter(function (x) { return x.id === id; })[0]; if (!p || p.masked) return;
      var cells = ["F1", "F2", "F4", "F7", "F8", "F9", "F10", "F3"].map(function (f) {
        var c = p.cells[f];
        var ms = S.MODELS.map(function (m) {
          var x = c.models[m[0]];
          var st = [x.ds, x.is].filter(function (s) { return s && s !== "untested_or_unreported"; }).join(", ");
          return "<div class='mcell'><b>" + m[1] + ":</b> " + (x.v ? S.esc(S.VAL[x.v] || x.v) : "<span class='muted'>" + S.esc((x.ur || "no value").replace(/_/g, " ")) + "</span>") +
            (st ? " <span class='small muted'>(" + S.esc(st) + ")</span>" : "") +
            (x.q ? "<blockquote>“" + S.esc(x.q) + "”</blockquote><div class='small'>" + S.docLink(x.doc) + "</div>" : (x.doc ? "<div class='small'>" + S.docLink(x.doc) + "</div>" : "")) + "</div>";
        }).join("");
        return "<tr><th scope='row'><b>" + f + "</b><div class='small muted'>" + S.esc(CELL[f]) + "</div></th><td><b>" + S.esc(S.VAL[c.prov] || c.prov || "–") + "</b> / " + S.esc(S.VAL[c.strict] || c.strict || "–") + "<div class='small muted'>" + AGREE[c.agree] + "</div></td><td>" + ms + "</td></tr>";
      }).join("");
      var d = $("detail");
      d.hidden = false;
      d.innerHTML = "<h2 style='margin-top:0'>" + S.esc(p.name) + " <span class='small muted'>" + S.esc(S.TIERLABEL[p.tier] || p.tier) + "</span></h2>" +
        "<p class='small'>Index, provisional " + S.ivbar(p.index.prov) + " · strict " + S.ivbar(p.index.strict) + ". <a href='cells.html#" + S.esc(p.id) + "'>How the cells developed document by document</a> · <a href='documents.html#project=" + S.esc(p.id) + "'>documents</a> · <a href='map.html#" + S.esc(p.id) + "'>map</a>.</p>" +
        "<div class='scroll-x'><table class='ptable cells'><thead><tr><th>Cell</th><th>Provisional / strict</th><th>The three models, with the quotation each value rests on</th></tr></thead><tbody>" + cells + "</tbody></table></div>" +
        "<p class='small muted'>Quotations are short extracts (at most " + R.meta.quote_max + " characters) from the official documents; the link opens the issuer's own copy at the page.</p>";
      d.scrollIntoView({ behavior: "smooth", block: "start" });
      history.replaceState(null, "", "#" + p.id);
    }
    hyp(); glance(); paint();
    function fromHash() {
      var start = location.hash.slice(1);
      var p = R.projects.filter(function (x) { return x.id === start; })[0];
      if (p && p.masked) { var row = $("p-" + p.id); if (row) row.scrollIntoView({ block: "center" }); return; }
      if (p) { if (p.tier === "T3" && $("tier-filter").value === "core") { $("tier-filter").value = "all"; paint(); } detail(start); }
    }
    window.addEventListener("hashchange", fromHash);
    fromHash();
  }).catch(function (e) { $("hyp").textContent = "The results could not be loaded (" + e.message + ")."; });
})();
