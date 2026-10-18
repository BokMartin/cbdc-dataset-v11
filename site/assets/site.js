/* CBDC Dataset v11 — shared site script: sidebar, mock banner, map page, features page. No build step. */
(function () {
  var NAV = [["index.html", "Home"], ["map.html", "Map"], ["features.html", "Features & types"], ["method.html", "Method & progress"], ["data.html", "Data"], ["about.html", "About"]];
  var here = location.pathname.split("/").pop() || "index.html";
  var side = document.querySelector("aside.side");
  if (side) {
    side.innerHTML = '<a class="brand" href="index.html">CBDC <span>Dataset</span></a><div class="side-tag">v11 · work in progress</div><nav class="main">' +
      NAV.map(function (n) { return '<a href="' + n[0] + '"' + (n[0] === here ? ' class="current"' : "") + ">" + n[1] + "</a>"; }).join("") +
      '</nav><div class="side-foot"><strong>Cite as</strong>Bok, M. &amp; Stroukal, D. (2026). <em>Institutional Determinants of Privacy Design in Central Bank Digital Currencies</em>. Working paper, cbdcdataset.org.</div>';
  }
  window.CBDC = { NAV: NAV };

  window.CBDC.load = function (cb) {
    fetch("assets/data.json").then(function (r) { return r.json(); }).then(function (D) {
      var b = document.getElementById("mock-banner");
      if (b && D.mock) b.innerHTML = "<strong>Mock data</strong>" + D.mock_note + " Development profiles (real, verified quotes): " +
        D.jurisdictions.filter(function (j) { return !j.mock; }).map(function (j) { return j.name; }).join(", ") + ". As of " + D.as_of + ", contract " + D.contract + ".";
      cb(D);
    });
  };

  // ---------- colour schemes ----------
  var TYPE_COL = { A0: "#a8402f", A1: "#d98a6a", B0: "#1f5c45", B1: "#7fb39a", C0: "#2c4f7c", C1: "#8aa7c9" };
  var STATUS_COL = { LIVE: "#1f5c45", PILOT: "#5c8f73", PREPARATION: "#9a7418", EXPLORATION: "#d9c38a", PAUSED: "#b8b0a0", DISCONTINUED: "#8a8275", BANNED: "#a8402f", NONE: "#e6e0d2", NA: "#e6e0d2", UNRESEARCHED: "#efe9dc" };
  var YES_NO = { yes: "#1f5c45", no: "#a8402f" };
  var F12_COL = { conventional_centralised: "#2c4f7c", permissioned_DLT: "#9a7418", permissionless_DLT: "#a8402f", hybrid: "#7fb39a", undecided: "#d9c38a" };
  var F3_COL = { via_PSP: "#1f5c45", via_CB: "#a8402f", via_both: "#9a7418", none_stated: "#d9c38a" };
  var UNKNOWN = "#e6e0d2", NOCORE = "#f3efe6";
  window.CBDC.schemes = {
    type: { label: "Architecture type (F1 × F2 × F4)", col: function (j, s) { return TYPE_COL[s.type] || UNKNOWN; }, legend: Object.keys(TYPE_COL).map(function (k) { return [k, TYPE_COL[k]]; }).concat([["undetermined (?)", UNKNOWN]]) },
    y1: { label: "Y₁ — central bank cannot link online transactions (F1 = no)", col: function (j, s) { return YES_NO[{ no: "yes", yes: "no" }[s.cells.F1]] || UNKNOWN; }, legend: [["Y₁ = 1 (F1 no)", YES_NO.yes], ["Y₁ = 0 (F1 yes)", YES_NO.no], ["undetermined", UNKNOWN]] },
    f7: { label: "F7 — low-identification route exists", col: function (j, s) { return YES_NO[s.cells.F7] || UNKNOWN; }, legend: [["yes", YES_NO.yes], ["no", YES_NO.no], ["n/d", UNKNOWN]] },
    f3: { label: "F3 — documented lawful-access route", col: function (j, s) { return F3_COL[s.cells.F3] || UNKNOWN; }, legend: Object.keys(F3_COL).map(function (k) { return [k, F3_COL[k]]; }).concat([["n/d", UNKNOWN]]) },
    f12: { label: "F12 — ledger technology", col: function (j, s) { return F12_COL[s.cells.F12] || UNKNOWN; }, legend: Object.keys(F12_COL).map(function (k) { return [k, F12_COL[k]]; }).concat([["n/d", UNKNOWN]]) },
    status: { label: "Official project status (Oct 2026)", col: function (j) { return STATUS_COL[j.status] || UNKNOWN; }, legend: Object.keys(STATUS_COL).slice(0, 8).map(function (k) { return [k, STATUS_COL[k]]; }) },
    objective: { label: "Declared financial-inclusion objective (F11)", col: function (j) { return j.cells.F11 && j.cells.F11.value.financial_inclusion ? "#1f5c45" : "#d9c38a"; }, legend: [["declared", "#1f5c45"], ["not documented", "#d9c38a"]] }
  };

  // snapshot of a jurisdiction as of a year: last history entry with year <= Y, else null
  window.CBDC.asOf = function (j, year) {
    var s = null; (j.history || []).forEach(function (h) { if (h.year <= year) s = h; }); return s;
  };

  window.CBDC.panel = function (j, year, D) {
    var el = document.getElementById("panel"); if (!el) return;
    if (!j) { el.innerHTML = '<h3>Click a country</h3><div class="sub">Hover for the type; click to pin the profile. Use the year slider to see how the documented design changed.</div>'; return; }
    var s = window.CBDC.asOf(j, year); var cur = j.cells;
    var tag = j.mock ? '<span class="tag mock">mock</span>' : '<span class="tag dev">development · verified quotes</span>';
    var rows = "";
    var F = { F1: "F1 CB can link online tx", F2: "F2 PSP can link", F3: "F3 lawful-access route", F4: "F4 private offline", F7: "F7 low-ID route", F8: "F8 onboarding ID", F9: "F9 targeted re-identification", F10: "F10 programmable restrictions", F12: "F12 ledger technology" };
    Object.keys(F).forEach(function (k) {
      var c = cur[k] || {}; var v = s && s.cells ? (s.cells[k] || "n/d") : c.value;
      var ev = (s && s.year === (j.years[j.years.length - 1] || year)) ? (c.evidence_state ? " · " + c.evidence_state : "") + (c.claim_status ? " · " + c.claim_status : "") : " · earlier snapshot";
      var q = (!j.mock && c.quote && (!s || s.year === j.years[j.years.length - 1])) ? '<div style="color:var(--muted);font-size:0.76rem;margin-top:2px">doc ' + c.doc + " p." + c.page + ': “' + String(c.quote).slice(0, 160) + (String(c.quote).length > 160 ? "…" : "") + '”</div>' : "";
      rows += "<tr><td>" + F[k] + "</td><td><b>" + v + "</b><span style='color:var(--muted)'>" + ev + "</span>" + q + "</td></tr>";
    });
    var obj = cur.F11 ? Object.keys(cur.F11.value).filter(function (o) { return cur.F11.value[o]; }).map(function (o) { return o.replace(/_/g, " "); }).join(", ") : "";
    rows += "<tr><td>F11 declared objectives</td><td>" + (obj || "none documented") + (cur.F11 && cur.F11.primary_status ? " <span style='color:var(--muted)'>· " + cur.F11.primary_status + "</span>" : "") + "</td></tr>";
    var tl = (j.history || []).map(function (h) { return '<span class="step"' + (h.year === (s && s.year) ? ' style="border-color:var(--green);font-weight:600"' : "") + ">" + h.year + " · " + h.type + "</span>"; }).join("");
    el.innerHTML = "<h3>" + j.name + tag + "</h3><div class='sub'>" + (j.project_name ? j.project_name + " · " : "") + "status " + j.status + (j.status_date ? " (" + j.status_date.slice(0, 7) + ")" : "") + " · " + j.docs.length + " core documents " + (j.years.length ? j.years[0] + "–" + j.years[j.years.length - 1] : "") + "</div>" +
      "<div style='margin:6px 0 10px'>Type as of " + year + ": <b style='font-family:var(--serif);font-size:1.3rem'>" + (s ? s.type : "—") + "</b> &nbsp; current: <b>" + j.type + "</b> &nbsp; Y₁ " + (j.y1 === null ? "—" : j.y1) + " · Y₃ " + (j.y3 === null ? "—" : j.y3) + "</div>" +
      "<table>" + rows + "</table><div class='timeline'><div style='color:var(--muted);margin-bottom:3px'>Documented trajectory (type per document year" + (j.mock ? ", mock" : ", derived") + "):</div>" + tl + "</div>" +
      "<div style='margin-top:10px;color:var(--muted)'>Documents: " + j.docs.map(function (d) { return (d.url ? '<a href="' + d.url + '">' : "") + d.year + " " + d.verdict + (d.url ? "</a>" : ""); }).join(" · ") + "</div>";
  };

  window.CBDC.drawMap = function (D) {
    var svg = d3.select("#cbdc-map"), W = 960, H = 480, year = 2026, scheme = "type", pinned = null;
    var byId = {}; D.jurisdictions.forEach(function (j) { if (j.map_id) byId[j.map_id] = j; (j.member_ids || []).forEach(function (m) { if (m && !byId[m]) byId[m] = j; }); });
    var sel = document.getElementById("scheme"); Object.keys(window.CBDC.schemes).forEach(function (k) { var o = document.createElement("option"); o.value = k; o.textContent = window.CBDC.schemes[k].label; sel.appendChild(o); });
    var years = []; D.jurisdictions.forEach(function (j) { j.years.forEach(function (y) { if (years.indexOf(y) < 0) years.push(y); }); }); years.sort();
    var slider = document.getElementById("year"); slider.min = Math.max(2018, years[0]); slider.max = 2026; slider.value = 2026;
    function legend() { var S = window.CBDC.schemes[scheme]; document.getElementById("legend").innerHTML = S.legend.map(function (l) { return "<span><i style='background:" + l[1] + "'></i>" + l[0] + "</span>"; }).join("") + "<span><i style='background:" + NOCORE + "'></i>no core document</span>"; }
    function colour(f) { var j = byId[String(+f.id)]; if (!j) return NOCORE; var s = window.CBDC.asOf(j, year); if (!s) return NOCORE; return window.CBDC.schemes[scheme].col(j, s); }
    d3.json("assets/vendor/countries-50m.json").then(function (topo) {
      var geo = topojson.feature(topo, topo.objects.countries).features.filter(function (f) { return f.id !== "010"; });
      var proj = d3.geoNaturalEarth1().fitSize([W, H], { type: "FeatureCollection", features: geo }), path = d3.geoPath(proj);
      var paths = svg.selectAll("path").data(geo).join("path").attr("d", path).attr("class", function (f) { return "country" + (byId[String(+f.id)] ? "" : " nocore"); })
        .on("mouseenter", function (e, f) { if (pinned) return; window.CBDC.panel(byId[String(+f.id)], year, D); })
        .on("click", function (e, f) { var j = byId[String(+f.id)]; if (!j) return; pinned = j; paths.classed("pinned", false); d3.select(this).classed("pinned", true).raise(); window.CBDC.panel(j, year, D); });
      function render() { paths.attr("fill", colour); document.getElementById("year-label").textContent = year; legend(); if (pinned) window.CBDC.panel(pinned, year, D); }
      slider.oninput = function () { year = +this.value; render(); };
      sel.onchange = function () { scheme = this.value; render(); };
      document.getElementById("unpin").onclick = function () { pinned = null; paths.classed("pinned", false); window.CBDC.panel(null); };
      var play = document.getElementById("play"), t = null;
      play.onclick = function () { if (t) { clearInterval(t); t = null; play.textContent = "▶ play"; return; } play.textContent = "■ stop"; year = +slider.min; t = setInterval(function () { year++; if (year > 2026) { clearInterval(t); t = null; play.textContent = "▶ play"; year = 2026; } slider.value = year; render(); }, 900); };
      render(); window.CBDC.panel(null);
      // counts table under the map
      var ct = document.getElementById("counts"); if (ct) { var c = {}; D.jurisdictions.forEach(function (j) { c[j.type] = (c[j.type] || 0) + 1; }); ct.innerHTML = Object.keys(c).sort().map(function (k) { return "<span class='step'>" + k + ": " + c[k] + "</span>"; }).join(" "); }
    });
  };

  window.CBDC.featuresTable = function (D) {
    var el = document.getElementById("ftable"); if (!el) return;
    el.innerHTML = "<tr><th>Cell</th><th>Question (contract §4)</th><th>Values</th><th>Decisive qualifiers</th><th>Traps</th></tr>" + D.features.map(function (f) {
      var reserved = /reserved/.test(f.traps);
      return "<tr" + (reserved ? " style='color:var(--muted)'" : "") + "><td>" + f.id + "<br><span style='font-weight:400;color:var(--muted)'>" + f.name + "</span></td><td>" + f.question + "</td><td>" + f.values + "</td><td>" + f.qualifiers + "</td><td>" + f.traps + "</td></tr>";
    }).join("");
    var tc = document.getElementById("type-counts"); if (tc) { var c = {}; D.jurisdictions.forEach(function (j) { c[j.type] = (c[j.type] || 0) + 1; }); ["A0", "A1", "B0", "B1", "C0", "C1"].forEach(function (k) { var e = document.getElementById("n-" + k); if (e) e.textContent = (c[k] || 0) + (D.mock ? " (mock)" : ""); }); var o = Object.keys(c).filter(function (k) { return ["A0", "A1", "B0", "B1", "C0", "C1"].indexOf(k) < 0; }).map(function (k) { return k + ": " + c[k]; }).join(", "); tc.textContent = o ? "Partial / undetermined: " + o : ""; }
  };
})();
