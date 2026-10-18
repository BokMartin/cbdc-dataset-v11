/* CBDC Dataset v11 — shared site script (no build step). Sidebar, data loading, map with year slider and modes,
   distribution-over-time chart, project panel, profiles table, feature table, paper figures. */
(function () {
  var NAV = [["index.html", "Home"], ["map.html", "Map"], ["profiles.html", "Country profiles"], ["features.html", "Features & types"], ["paper.html", "Paper"],
             ["pipeline.html", "Pipeline"], ["method.html", "Method & progress"], ["data.html", "Data"], ["contribute.html", "Contribute"], ["about.html", "About"]];
  var here = location.pathname.split("/").pop() || "index.html";
  var side = document.querySelector("aside.side");
  if (side) side.innerHTML = '<a class="brand" href="index.html">CBDC <span>Dataset</span></a><div class="side-tag">Open research data · v11</div><nav class="main">' +
    NAV.map(function (n) { return '<a href="' + n[0] + '"' + (n[0] === here ? ' class="current"' : "") + ">" + n[1] + "</a>"; }).join("") +
    '</nav><div class="side-foot"><strong>Cite as</strong>Bok, M. &amp; Stroukal, D. (2026). <em>Institutional Determinants of Privacy Design in Central Bank Digital Currencies</em>. Working paper, cbdcdataset.org.</div>';

  var C = window.CBDC = {};
  C.load = function (cb) {
    fetch("assets/data.json").then(function (r) { return r.json(); }).then(function (D) {
      D.byCode = {}; D.projects.forEach(function (p) { D.byCode[p.code] = p; });
      var b = document.getElementById("mock-banner");
      if (b && D.mock) b.innerHTML = "<strong>Mock-up</strong>" + D.mock_note + " Real, verified: " + D.projects.filter(function (p) { return !p.mock; }).map(function (p) { return p.name; }).join(", ") + ". Contract " + D.contract.replace("MEASUREMENT_CONTRACT_", "").replace(/_/g, " ") + ".";
      cb(D);
    });
  };
  C.esc = function (s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); };

  // ---------- palettes (validated with the dataviz palette checker, light surface #fffdf8) ----------
  var TYPE = { A0: "#9c3a26", A1: "#e07a4a", B0: "#167a4f", B1: "#5cbf8a", C0: "#2a5fb0", C1: "#6fa0e8" };
  var OBJC = { payment_modernisation: "#1f8a5c", financial_inclusion: "#d59a1f", monetary_sovereignty_transmission: "#2f6fc0", cash_substitute_resilience: "#b5452f", aml_cft_tax_enforcement: "#9a5fd6", innovation_competitiveness: "#1fa5a5", several_joint: "#6f6a5e", unranked: "#b8b0a0", conflict: "#4a4640" };
  var STATUSC = { LIVE: "#167a4f", PILOT: "#5cbf8a", PREPARATION: "#d59a1f", EXPLORATION: "#e8cf8a", PAUSED: "#b8b0a0", DISCONTINUED: "#7a736a", BANNED: "#9c3a26", NONE: "#dcd5c6" };
  var YES = "#167a4f", NO = "#9c3a26", PARTIAL = "#c9c2b2", UNKNOWN = "#e6e0d2", NOPROJ = "#f3efe6", NA = "#d8d2c4";
  var F3C = { via_PSP: "#167a4f", via_CB: "#9c3a26", via_both: "#d59a1f", none_stated: "#6fa0e8" };
  var F12C = { conventional_centralised: "#2a5fb0", permissioned_DLT: "#d59a1f", permissionless_DLT: "#9c3a26", hybrid: "#5cbf8a", undecided: "#b8b0a0" };
  C.OBJ_LABEL = { payment_modernisation: "Payment modernisation", financial_inclusion: "Financial inclusion", monetary_sovereignty_transmission: "Monetary sovereignty / transmission", cash_substitute_resilience: "Cash substitute & resilience", aml_cft_tax_enforcement: "AML / CFT / tax enforcement", innovation_competitiveness: "Innovation & competitiveness", several_joint: "Several, jointly", unranked: "Declared, unranked", conflict: "Conflicting statements", "n/d": "Not documented" };
  C.TYPE_LABEL = { A0: "A0 · CB can link · no private offline", A1: "A1 · CB can link · private offline", B0: "B0 · only PSP can link · no private offline", B1: "B1 · only PSP can link · private offline", C0: "C0 · nobody routinely · no private offline", C1: "C1 · nobody routinely · private offline" };
  C.FLABEL = { F1: "F1 Central bank can link online payments", F2: "F2 PSP can link online payments", F3: "F3 Documented lawful-access route", F4: "F4 Private offline mode adopted", F7: "F7 Low-identification route", F8: "F8 Verified identity at onboarding", F9: "F9 Targeted re-identification possible", F10: "F10 State-imposed programmable restrictions", F12: "F12 Ledger technology" };
  function yn(v) { return v === "yes" ? YES : v === "no" ? NO : UNKNOWN; }
  function typeCol(t) { return TYPE[t] || (t && t !== "n.a." && t.indexOf("?") >= 0 ? PARTIAL : UNKNOWN); }
  C.colors = { TYPE: TYPE, OBJC: OBJC, STATUSC: STATUSC, YES: YES, NO: NO, PARTIAL: PARTIAL, UNKNOWN: UNKNOWN, F3C: F3C, F12C: F12C };

  // modes: key -> {label, value(p, snap) -> category, col(category), legend [[cat,label,col]]}
  function fmode(f, cols, order) {
    return { label: C.FLABEL[f], value: function (p, s) { return s.cells[f]; }, col: function (v) { return cols[v] || UNKNOWN; },
             legend: order.map(function (v) { return [v, v.replace(/_/g, " "), cols[v]]; }).concat([["n/d", "not documented", UNKNOWN]]) };
  }
  C.modes = {
    type: { label: "Architecture type (F1 × F2 × F4) — six categories", value: function (p, s) { return s.type; }, col: typeCol,
            legend: Object.keys(TYPE).map(function (k) { return [k, C.TYPE_LABEL[k], TYPE[k]]; }).concat([["partial", "partial type (one cell undetermined)", PARTIAL], ["?", "undetermined", UNKNOWN]]) },
    primary: { label: "Primary declared objective (F11, Layer 2)", value: function (p, s) { return s.primary; }, col: function (v) { return OBJC[v] || UNKNOWN; },
               legend: ["payment_modernisation", "financial_inclusion", "monetary_sovereignty_transmission", "cash_substitute_resilience", "aml_cft_tax_enforcement", "innovation_competitiveness", "several_joint", "unranked"].map(function (k) { return [k, C.OBJ_LABEL[k], OBJC[k]]; }).concat([["n/d", "not documented", UNKNOWN]]) },
    y1: { label: "Y₁ — central bank separated from transaction identity (F1 = no)", value: function (p, s) { return s.cells.F1 === "no" ? "1" : s.cells.F1 === "yes" ? "0" : "n/d"; }, col: function (v) { return v === "1" ? YES : v === "0" ? NO : UNKNOWN; },
          legend: [["1", "Y₁ = 1 — CB cannot routinely link", YES], ["0", "Y₁ = 0 — CB can link", NO], ["n/d", "undetermined", UNKNOWN]] },
    status: { label: "Official project status (Oct 2026)", value: function (p) { return p.status; }, col: function (v) { return STATUSC[v] || UNKNOWN; }, legend: Object.keys(STATUSC).map(function (k) { return [k, k, STATUSC[k]]; }), static: true },
    F1: fmode("F1", { yes: NO, no: YES }, ["yes", "no"]), F2: fmode("F2", { yes: NO, no: YES }, ["yes", "no"]), F3: fmode("F3", F3C, ["via_PSP", "via_CB", "via_both", "none_stated"]),
    F4: fmode("F4", { yes: YES, no: NO }, ["yes", "no"]), F7: fmode("F7", { yes: YES, no: NO }, ["yes", "no"]), F8: fmode("F8", { yes: NO, no: YES }, ["yes", "no"]),
    F9: fmode("F9", { yes: NO, no: YES }, ["yes", "no"]), F10: fmode("F10", { yes: NO, no: YES }, ["yes", "no"]), F12: fmode("F12", F12C, ["conventional_centralised", "permissioned_DLT", "permissionless_DLT", "hybrid", "undecided"])
  };
  // F modes: green = more privacy-protective pole, red = less; stated in legend
  ["F1", "F2", "F8", "F9", "F10"].forEach(function (f) { C.modes[f].legend[0][1] = "yes (less private)"; C.modes[f].legend[1][1] = "no (more private)"; });
  ["F4", "F7"].forEach(function (f) { C.modes[f].legend[0][1] = "yes (more private)"; C.modes[f].legend[1][1] = "no"; });

  C.asOf = function (p, year) { var s = null; (p.history || []).forEach(function (h) { if (h.year <= year) s = h; }); return s; };

  // ---------- project panel ----------
  C.panel = function (p, year, D, el) {
    el = el || document.getElementById("panel"); if (!el) return;
    if (!p) { el.innerHTML = '<h3>Select a project</h3><div class="sub">Hover a country for a quick read, click to pin its full profile. Drag the year to see the documented design as of that year; the chart below the map shows how the categories shift.</div>'; return; }
    if (!p.cells) { el.innerHTML = "<h3>" + C.esc(p.name) + "</h3><div class='sub'>" + (p.project_name ? C.esc(p.project_name) + " · " : "") + "status " + p.status + "</div><p>Outside the retail matrix: " + (p.status === "BANNED" ? "statutory restriction on a retail CBDC (dated); no design cells are coded." : p.status === "NONE" ? "wholesale-only or no retail project; documents are kept in the registry for completeness." : "no retail design documented.") + "</p><div class='sub'>Documents: " + p.docs.map(function (d) { return (d.url ? '<a href="' + d.url + '">' : "") + d.year + (d.url ? "</a>" : ""); }).join(" · ") + "</div>"; return; }
    var s = C.asOf(p, year); var lastYear = p.years[p.years.length - 1]; var isCurrent = !s || s.year === lastYear;
    var tag = p.mock ? '<span class="tag mock">mock values</span>' : '<span class="tag dev">real · verified quotes</span>';
    var rows = "";
    ["F1", "F2", "F4", "F7", "F8", "F9", "F10", "F3", "F12"].forEach(function (k) {
      var c = p.cells[k] || {}; var v = s ? (s.cells[k] || "n/d") : c.value;
      var meta = isCurrent ? [c.evidence_state, c.claim_status, c.derivation === "inferred" ? "inferred" : ""].filter(Boolean).join(" · ") : (s.claim_status && s.claim_status[k] ? s.claim_status[k] + " · snapshot " + s.year : "snapshot " + s.year);
      var src = "";
      if (isCurrent && v !== "n/d" && (c.doc_title || c.doc_id)) {
        src = '<div class="src">' + (c.doc_url ? '<a href="' + c.doc_url + '">' : "") + C.esc(c.doc_title || c.doc_id) + (c.doc_url ? "</a>" : "") + (c.doc_year ? " (" + c.doc_year + ")" : "") + (c.page ? ", p. " + c.page : "") +
              (c.quote ? ' — “' + C.esc(String(c.quote).slice(0, 220)) + (String(c.quote).length > 220 ? "…" : "") + '”' : (p.mock ? " — <i>quote: pipeline output</i>" : "")) + (c.quote_verified ? ' <span class="tag dev">' + c.quote_verified.replace(/_/g, " ") + "</span>" : "") + "</div>";
      }
      rows += '<tr><td><a class="def" href="features.html#' + k + '" title="definition">' + C.FLABEL[k] + "</a></td><td><b>" + C.esc(v) + '</b><span class="meta"> · ' + meta + "</span>" + src + "</td></tr>";
    });
    var f11 = s ? s.f11 : p.cells.F11; var flags = f11.flags || {};
    var obj = Object.keys(flags).filter(function (o) { return flags[o]; }).map(function (o) { return C.OBJ_LABEL[o]; }).join(", ");
    rows += '<tr><td><a class="def" href="features.html#F11">F11 Declared objectives</a></td><td>' + (obj || "none documented") + '<span class="meta"> · ' + (f11.primary_status || "n/d") + (f11.primary_objectives ? " → <b>" + C.OBJ_LABEL[f11.primary_objectives] || f11.primary_objectives : "") + "</b></span>" +
            (isCurrent && p.cells.F11.doc_title ? '<div class="src">' + C.esc(p.cells.F11.doc_title) + (p.cells.F11.doc_year ? " (" + p.cells.F11.doc_year + ")" : "") + (p.cells.F11.page ? ", p. " + p.cells.F11.page : "") + (p.cells.F11.quote ? ' — “' + C.esc(String(p.cells.F11.quote).slice(0, 200)) + '”' : "") + "</div>" : "") + "</td></tr>";
    var tl = (p.history || []).map(function (h) { return '<span class="step' + (s && h.year === s.year ? " on" : "") + '" title="' + C.esc((h.changes || []).join("; ")) + '">' + h.year + " · <b>" + h.type + "</b>" + (h.primary && h.primary !== "n/d" ? " · " + (C.OBJ_LABEL[h.primary] || h.primary).split(" ")[0].toLowerCase() : "") + "</span>"; }).join("");
    var ch = s && s.changes && s.changes.length ? "<div class='meta' style='margin-top:6px'>Changes documented in " + s.year + ": " + C.esc(s.changes.slice(0, 6).join("; ")) + (s.changes.length > 6 ? " …" : "") + "</div>" : "";
    el.innerHTML = "<h3>" + C.esc(p.name) + tag + "</h3><div class='sub'>" + (p.project_name ? C.esc(p.project_name) + " · " : "") + "status " + p.status + (p.pause_kind ? " (" + C.esc(p.pause_kind) + ")" : "") + (p.status_date ? " · " + p.status_date.slice(0, 7) : "") + " · " + p.docs.length + " documents " + (p.years.length ? p.years[0] + "–" + lastYear : "") + (p.members.length > 1 ? " · one project, " + p.members.length + " member states" : "") + "</div>" +
      "<div class='typeline'>Type as of " + year + ": <b style='color:" + typeCol(s ? s.type : p.type) + "'>" + (s ? s.type : "—") + "</b>" + (isCurrent ? "" : " <span class='meta'>(current " + p.type + ")</span>") + " &nbsp;·&nbsp; Y₁ " + (p.y1 === null ? "—" : p.y1) + " · Y₃ " + (p.y3 === null ? "—" : p.y3) + "</div>" +
      "<table>" + rows + "</table><div class='timeline'><div class='meta'>Documented trajectory — type · primary objective per document year" + (p.mock ? " (mock)" : "") + ":</div>" + tl + ch + "</div>" +
      "<div class='meta' style='margin-top:10px'>Documents (" + p.docs.length + "): " + p.docs.map(function (d) { return (d.url ? '<a href="' + d.url + '" title="' + C.esc(d.title) + '">' : "<span title='" + C.esc(d.title) + "'>") + d.year + (d.verdict ? " " + d.verdict[0] : "") + (d.url ? "</a>" : "</span>"); }).join(" · ") + "</div>" +
      (p.status_source ? "<div class='meta'>Status source: <a href='" + p.status_source + "'>link</a></div>" : "");
  };

  // ---------- distribution over time (stacked bars) ----------
  C.timeChart = function (D, modeKey, year, container) {
    var mode = C.modes[modeKey]; var el = d3.select(container); el.selectAll("*").remove();
    var years = D.years, cats = mode.legend.map(function (l) { return l[0]; });
    var data = years.map(function (y) { var row = { year: y }; cats.forEach(function (c) { row[c] = 0; }); row.partial = 0;
      D.projects.forEach(function (p) { if (!p.cells) return; var s = C.asOf(p, y); if (!s) return; var v = mode.static ? mode.value(p) : mode.value(p, s); if (cats.indexOf(v) < 0) v = (modeKey === "type" && v && v.indexOf("?") >= 0) ? "partial" : "n/d"; if (row[v] === undefined) row[v] = 0; row[v]++; });
      return row; });
    var W = el.node().clientWidth || 640, H = 170, m = { t: 8, r: 8, b: 22, l: 28 };
    var svg = el.append("svg").attr("viewBox", "0 0 " + W + " " + H).attr("width", "100%");
    var x = d3.scaleBand().domain(years).range([m.l, W - m.r]).paddingInner(0.25), yMax = d3.max(data, function (r) { return cats.reduce(function (a, c) { return a + (r[c] || 0); }, 0); }) || 1;
    var y = d3.scaleLinear().domain([0, yMax]).range([H - m.b, m.t]);
    var stack = d3.stack().keys(cats)(data);
    svg.append("g").selectAll("g").data(stack).join("g").attr("fill", function (d) { return mode.col(d.key); })
      .selectAll("rect").data(function (d) { return d.map(function (v) { v.key = d.key; return v; }); }).join("rect")
      .attr("x", function (d) { return x(d.data.year); }).attr("width", x.bandwidth()).attr("y", function (d) { return y(d[1]) + 1; }).attr("height", function (d) { return Math.max(0, y(d[0]) - y(d[1]) - 1); })
      .attr("opacity", function (d) { return d.data.year === year ? 1 : 0.75; })
      .append("title").text(function (d) { return d.data.year + " · " + (C.TYPE_LABEL[d.key] || C.OBJ_LABEL[d.key] || d.key) + ": " + (d[1] - d[0]) + " projects"; });
    svg.append("g").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).tickSize(0)).call(function (g) { g.select(".domain").attr("stroke", "#d9d2c2"); g.selectAll("text").attr("font-size", 10).attr("fill", "#6f6a5e").attr("font-family", "sans-serif"); });
    svg.append("g").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).ticks(4).tickSize(-(W - m.l - m.r))).call(function (g) { g.select(".domain").remove(); g.selectAll("line").attr("stroke", "#eee8db"); g.selectAll("text").attr("font-size", 10).attr("fill", "#6f6a5e").attr("font-family", "sans-serif"); });
    svg.append("rect").attr("x", x(year) - 3).attr("y", m.t - 4).attr("width", x.bandwidth() + 6).attr("height", H - m.b - m.t + 6).attr("fill", "none").attr("stroke", "#23211b").attr("stroke-width", 1).attr("rx", 3);
  };

  // ---------- map ----------
  C.drawMap = function (D) {
    var svg = d3.select("#cbdc-map"), W = 960, H = 470, year = 2026, modeKey = "type", pinned = null;
    var byId = {}; D.projects.forEach(function (p) { p.map_ids.forEach(function (i) { if (!byId[i] || p.members.length === 1) byId[i] = p; }); });
    var sel = document.getElementById("mode"); Object.keys(C.modes).forEach(function (k) { var o = document.createElement("option"); o.value = k; o.textContent = C.modes[k].label; sel.appendChild(o); });
    var slider = document.getElementById("year"); slider.min = D.years[0]; slider.max = D.years[D.years.length - 1]; slider.value = year;
    var q = new URLSearchParams(location.search); if (q.get("mode") && C.modes[q.get("mode")]) { modeKey = q.get("mode"); sel.value = modeKey; }
    function legend() { document.getElementById("legend").innerHTML = C.modes[modeKey].legend.map(function (l) { return "<span><i style='background:" + l[2] + "'></i>" + l[1] + "</span>"; }).join("") + "<span><i style='background:" + NA + "'></i>no retail project / n.a.</span><span><i style='background:" + NOPROJ + "'></i>no document in the registry</span>"; }
    function colour(f) { var p = byId[String(+f.id)]; if (!p) return NOPROJ; if (!p.cells) return NA; var s = C.asOf(p, year); if (!s) return NOPROJ; var m = C.modes[modeKey]; return m.col(m.static ? m.value(p) : m.value(p, s)); }
    d3.json("assets/vendor/countries-50m.json").then(function (topo) {
      var geo = topojson.feature(topo, topo.objects.countries).features.filter(function (f) { return f.id !== "010"; });
      var proj = d3.geoNaturalEarth1().fitSize([W, H], { type: "FeatureCollection", features: geo }), path = d3.geoPath(proj);
      svg.append("path").attr("d", path(topojson.mesh(topo, topo.objects.countries, function (a, b) { return a !== b; }))).attr("fill", "none").attr("stroke", "#fffdf8").attr("stroke-width", 0.4);
      var paths = svg.selectAll("path.country").data(geo).join("path").attr("class", function (f) { return "country" + (byId[String(+f.id)] ? "" : " nocore"); }).attr("d", path)
        .on("mouseenter", function (e, f) { if (pinned) return; C.panel(byId[String(+f.id)], year, D); })
        .on("click", function (e, f) { var p = byId[String(+f.id)]; if (!p) return; pinned = p; paths.classed("pinned", function (g) { return byId[String(+g.id)] === p; }); C.panel(p, year, D); history.replaceState(null, "", "?project=" + p.code + "&mode=" + modeKey); });
      svg.append("path").attr("d", path(topojson.mesh(topo, topo.objects.countries, function (a, b) { return a !== b; }))).attr("fill", "none").attr("stroke", "#fffdf8").attr("stroke-width", 0.5).attr("pointer-events", "none");
      function render() { paths.attr("fill", colour); document.getElementById("year-label").textContent = year; legend(); C.timeChart(D, modeKey, year, "#timechart"); document.getElementById("chart-title").textContent = "Projects by " + C.modes[modeKey].label.split(" (")[0].toLowerCase() + ", " + D.years[0] + "–" + D.years[D.years.length - 1] + " (as documented at each year)"; if (pinned) C.panel(pinned, year, D); counts(); }
      function counts() { var c = {}; D.projects.forEach(function (p) { if (!p.cells) return; var s = C.asOf(p, year); if (!s) return; var m = C.modes[modeKey]; var v = m.static ? m.value(p) : m.value(p, s); c[v] = (c[v] || 0) + 1; });
        document.getElementById("counts").innerHTML = Object.keys(c).sort().map(function (k) { return "<span class='step'><i style='background:" + C.modes[modeKey].col(k) + "'></i>" + k + " <b>" + c[k] + "</b></span>"; }).join(" "); }
      slider.oninput = function () { year = +this.value; render(); };
      sel.onchange = function () { modeKey = this.value; render(); history.replaceState(null, "", "?" + (pinned ? "project=" + pinned.code + "&" : "") + "mode=" + modeKey); };
      document.getElementById("unpin").onclick = function () { pinned = null; paths.classed("pinned", false); C.panel(null); history.replaceState(null, "", location.pathname); };
      var play = document.getElementById("play"), t = null;
      play.onclick = function () { if (t) { clearInterval(t); t = null; play.textContent = "▶ play"; return; } play.textContent = "■ stop"; year = +slider.min; t = setInterval(function () { year++; if (year > +slider.max) { clearInterval(t); t = null; play.textContent = "▶ play"; year = +slider.max; } slider.value = year; render(); }, 800); };
      var pre = q.get("project"); if (pre && D.byCode[pre]) { pinned = D.byCode[pre]; paths.classed("pinned", function (g) { return byId[String(+g.id)] === pinned; }); }
      render(); C.panel(pinned, year, D);
    });
  };

  // ---------- profiles table ----------
  C.profiles = function (D) {
    var el = document.getElementById("profiles"); if (!el) return;
    var cols = [["name", "Project"], ["status", "Status"], ["type", "Type"], ["y1", "Y₁"], ["y3", "Y₃"], ["F1", "F1"], ["F2", "F2"], ["F4", "F4"], ["F7", "F7"], ["F8", "F8"], ["F9", "F9"], ["F10", "F10"], ["F3", "F3"], ["F12", "F12"], ["primary", "Primary objective"], ["ndocs", "Docs"], ["last", "Last doc"]];
    var rows = D.projects.map(function (p) { var r = { code: p.code, name: p.name, status: p.status, type: p.type, y1: p.y1 === null ? "" : p.y1, y3: p.y3 === null ? "" : p.y3, primary: p.cells ? (C.OBJ_LABEL[p.primary] || p.primary) : "", ndocs: p.docs.length, last: p.years[p.years.length - 1] || "", mock: p.mock };
      ["F1", "F2", "F3", "F4", "F7", "F8", "F9", "F10", "F12"].forEach(function (f) { r[f] = p.cells ? p.cells[f].value : ""; }); return r; });
    var sortKey = "name", asc = true;
    function draw() {
      rows.sort(function (a, b) { var x = a[sortKey], y = b[sortKey]; if (x === "" && y !== "") return 1; if (y === "" && x !== "") return -1; return (x > y ? 1 : x < y ? -1 : 0) * (asc ? 1 : -1); });
      el.innerHTML = "<thead><tr>" + cols.map(function (c) { return "<th data-k='" + c[0] + "'" + (c[0] === sortKey ? " class='sorted'" : "") + ">" + c[1] + (c[0] === sortKey ? (asc ? " ↑" : " ↓") : "") + "</th>"; }).join("") + "</tr></thead><tbody>" +
        rows.map(function (r) { return "<tr><td><a href='map.html?project=" + r.code + "'>" + C.esc(r.name) + "</a>" + (r.mock ? "" : " <span class='tag dev'>real</span>") + "</td><td><i class='sw' style='background:" + (STATUSC[r.status] || UNKNOWN) + "'></i>" + r.status + "</td><td><b style='color:" + typeCol(r.type) + "'>" + r.type + "</b></td>" +
          ["y1", "y3", "F1", "F2", "F4", "F7", "F8", "F9", "F10", "F3", "F12"].map(function (k) { return "<td>" + C.esc(r[k]).replace(/_/g, " ") + "</td>"; }).join("") + "<td>" + C.esc(r.primary) + "</td><td>" + r.ndocs + "</td><td>" + r.last + "</td></tr>"; }).join("") + "</tbody>";
      el.querySelectorAll("th").forEach(function (th) { th.onclick = function () { var k = th.dataset.k; if (sortKey === k) asc = !asc; else { sortKey = k; asc = true; } draw(); }; });
    }
    draw();
  };

  // ---------- features table & typology counts ----------
  C.featuresTable = function (D) {
    var el = document.getElementById("ftable"); if (el) {
      el.innerHTML = "<tr><th>Cell</th><th>Question (contract §4)</th><th>Values</th><th>Decisive qualifiers</th><th>Traps the coder must avoid</th></tr>" + D.features.map(function (f) {
        var reserved = /reserved/.test(f.traps);
        return "<tr id='" + f.id + "'" + (reserved ? " style='color:var(--muted)'" : "") + "><td>" + f.id + "<br><span style='font-weight:400;color:var(--muted)'>" + f.name + "</span></td><td>" + f.question + "</td><td>" + f.values + "</td><td>" + f.qualifiers + "</td><td>" + f.traps + "</td></tr>";
      }).join("");
    }
    var c = {}; D.projects.forEach(function (p) { c[p.type] = (c[p.type] || 0) + 1; });
    ["A0", "A1", "B0", "B1", "C0", "C1"].forEach(function (k) { var e = document.getElementById("n-" + k); if (e) e.textContent = (c[k] || 0) + " projects"; });
    var tc = document.getElementById("type-counts"); if (tc) tc.textContent = "Partial or undetermined: " + Object.keys(c).filter(function (k) { return ["A0", "A1", "B0", "B1", "C0", "C1", "n.a."].indexOf(k) < 0; }).map(function (k) { return k + " " + c[k]; }).join(", ") + ". Outside the retail matrix (n.a.): " + (c["n.a."] || 0) + ".";
  };

  // ---------- paper figures ----------
  C.crosstab = function (D, container) {
    var el = document.getElementById(container); if (!el) return;
    var types = ["A0", "A1", "B0", "B1", "C0", "C1"], objs = D.objectives;
    var m = {}; types.forEach(function (t) { m[t] = {}; objs.forEach(function (o) { m[t][o] = 0; }); });
    D.projects.forEach(function (p) { if (!p.cells || !m[p.type]) return; objs.forEach(function (o) { if (p.cells.F11.flags[o]) m[p.type][o]++; }); });
    el.innerHTML = "<tr><th>Type</th>" + objs.map(function (o) { return "<th>" + C.OBJ_LABEL[o] + "</th>"; }).join("") + "<th>n</th></tr>" + types.map(function (t) { var n = D.projects.filter(function (p) { return p.type === t; }).length; return "<tr><td><b style='color:" + TYPE[t] + "'>" + t + "</b></td>" + objs.map(function (o) { return "<td>" + (n ? Math.round(100 * m[t][o] / n) + "%" : "—") + "</td>"; }).join("") + "<td>" + n + "</td></tr>"; }).join("");
  };
  C.deltaPlot = function (container) {
    // simulated illustration of the registered estimand: Δ = m(q75) − m(q25) with 95% interval against ±δ (SESOI). Numbers are placeholders.
    var rows = [["H1 informal economy → Y₁", -0.14, -0.31, 0.04], ["H2 liberal democracy → Y₁", 0.22, 0.05, 0.39], ["H3 CB independence (descriptive)", 0.06, -0.12, 0.24], ["Y₃ (secondary) informal economy", -0.09, -0.27, 0.10]];
    var el = d3.select(container); var W = el.node().clientWidth || 640, H = 190, m = { t: 14, r: 20, b: 28, l: 230 };
    var svg = el.append("svg").attr("viewBox", "0 0 " + W + " " + H).attr("width", "100%");
    var x = d3.scaleLinear().domain([-0.5, 0.5]).range([m.l, W - m.r]), y = d3.scaleBand().domain(rows.map(function (r) { return r[0]; })).range([m.t, H - m.b]).padding(0.5);
    svg.append("rect").attr("x", x(-0.2)).attr("width", x(0.2) - x(-0.2)).attr("y", m.t - 6).attr("height", H - m.b - m.t + 6).attr("fill", "#efe9dc");
    svg.append("text").attr("x", x(0)).attr("y", m.t - 2).attr("text-anchor", "middle").attr("font-size", 10).attr("fill", "#6f6a5e").attr("font-family", "sans-serif").text("±δ = 0.20 (working SESOI)");
    svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "#b8b0a0");
    rows.forEach(function (r) { var yy = y(r[0]) + y.bandwidth() / 2;
      svg.append("line").attr("x1", x(r[2])).attr("x2", x(r[3])).attr("y1", yy).attr("y2", yy).attr("stroke", "#23211b").attr("stroke-width", 2);
      svg.append("circle").attr("cx", x(r[1])).attr("cy", yy).attr("r", 5).attr("fill", "#167a4f").attr("stroke", "#fffdf8").attr("stroke-width", 2);
      svg.append("text").attr("x", m.l - 10).attr("y", yy + 4).attr("text-anchor", "end").attr("font-size", 12).attr("fill", "#23211b").attr("font-family", "sans-serif").text(r[0]); });
    svg.append("g").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).ticks(5).tickFormat(d3.format("+.1f"))).call(function (g) { g.select(".domain").attr("stroke", "#d9d2c2"); g.selectAll("text").attr("font-size", 10).attr("fill", "#6f6a5e").attr("font-family", "sans-serif"); });
    svg.append("text").attr("x", (m.l + W - m.r) / 2).attr("y", H - 4).attr("text-anchor", "middle").attr("font-size", 10).attr("fill", "#6f6a5e").attr("font-family", "sans-serif").text("Δ = P(Y=1 | predictor q75) − P(Y=1 | predictor q25), Firth logistic, 95% interval — SIMULATED");
  };
  C.stats = function (D) {
    var set = function (id, v) { var e = document.getElementById(id); if (e) e.textContent = v; };
    var retail = D.projects.filter(function (p) { return p.cells; });
    set("n-proj", D.projects.length); set("n-countries", D.projects.reduce(function (a, p) { return a + p.members.length; }, 0)); set("n-docs", D.projects.reduce(function (a, p) { return a + p.docs.length; }, 0));
    set("n-typed", retail.filter(function (p) { return TYPE[p.type]; }).length); set("n-y1", retail.filter(function (p) { return p.y1 !== null; }).length);
  };
})();
