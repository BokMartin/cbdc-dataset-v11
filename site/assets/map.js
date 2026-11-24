/* Map page: D3 + TopoJSON, world geometry vendored (Natural Earth 1:50m via world-atlas). Reads site/assets/projects.json
   and site/assets/documents.json. Shows corpus facts and official status only; never a measurement result. */
(function () {
  "use strict";
  var S = window.SITE, $ = function (id) { return document.getElementById(id); };
  var W = 960, H = 500;
  var DOC_BINS = [[0, 0, "none yet"], [1, 2, "1 to 2"], [3, 4, "3 to 4"], [5, 7, "5 to 7 (T2 level)"], [8, 999, "8 or more (T1 level)"]];
  var DOC_COL = ["#e9e5da", "#c6dbef", "#85b6da", "#3d88c2", "#0f4d85"];
  // analysis tiers of 17 Nov 2026: T1 and T2 are the 16 core projects, T3 is exploratory (Registration A §1, ADR-012 D1)
  var TIER = { T1: ["T1 · core", "#0f4d85"], T2: ["T2 · core", "#3d88c2"], T3: ["T3 · exploratory, often unfinished CBDC research", "#e3b45c"] };
  S.tierLabel = function (t) { return (TIER[t] || [t])[0]; };

  Promise.all([S.get("assets/projects.json"), S.get("assets/documents.json"), S.get("assets/vendor/countries-50m.json")])
    .then(function (r) { init(r[0], r[1], r[2]); })
    .catch(function (e) { $("panel").innerHTML = "<p>Could not load the map (" + S.esc(e.message) + ").</p>"; });

  function init(PP, DD, world) {
    var meta = PP.meta, projects = PP.projects, docs = DD.documents;
    var P = {}, byGeo = {};
    projects.forEach(function (p) { P[p.code] = p; p.geo.forEach(function (g) { byGeo[g] = p; }); });
    var frame = projects.filter(function (p) { return p.frame; });
    $("as-of").innerHTML = "<strong>Corpus as of " + meta.as_of + "; official status as documented up to " + meta.status_as_of + ".</strong> No measurement result is shown: the coding of the documents has not been run yet.";

    var years = [];
    frame.forEach(function (p) { Object.keys(p.ev_by_year).forEach(function (y) { years.push(+y); }); });
    var y0 = Math.min.apply(null, years), y1 = Math.max.apply(null, years);
    $("year").min = y0; $("year").max = y1; $("year").value = y1; $("year-out").textContent = y1;
    var FIRST = d3.scaleSequential(d3.interpolateYlGnBu).domain([y1 + 1, y0 - 2]);

    var state = { mode: "status", year: y1, sel: null };
    var h = new URLSearchParams(location.search);
    if (h.get("mode")) state.mode = h.get("mode");
    $("mode").value = state.mode;

    function pubsUpTo(p, y) { var n = 0; Object.keys(p.ev_by_year).forEach(function (k) { if (+k <= y) n += p.ev_by_year[k]; }); return n; }
    function bin(n) { for (var i = 0; i < DOC_BINS.length; i++) if (n >= DOC_BINS[i][0] && n <= DOC_BINS[i][1]) return i; return 0; }
    function colour(p) {
      if (state.mode === "status") return (S.STATUS[p.status] || S.STATUS.NA)[1];
      if (state.mode === "docs") return DOC_COL[bin(pubsUpTo(p, state.year))];
      if (state.mode === "tier") return (TIER[p.tier] || TIER.T3)[1];
      return p.ev_years.length ? FIRST(p.ev_years[0]) : DOC_COL[0];
    }
    function label(p) {
      if (state.mode === "status") return (S.STATUS[p.status] || S.STATUS.NA)[0];
      if (state.mode === "docs") { var n = pubsUpTo(p, state.year); return n + " evidence publication" + (n === 1 ? "" : "s") + " up to " + state.year; }
      if (state.mode === "tier") return S.tierLabel(p.tier);
      return p.ev_years.length ? "first evidence publication " + p.ev_years[0] : "no evidence publication";
    }

    // geometry
    var countries = topojson.feature(world, world.objects.countries).features.filter(function (f) { return f.id !== "010"; });
    var proj = d3.geoEqualEarth().fitExtent([[8, 8], [W - 8, H - 8]], { type: "FeatureCollection", features: countries });
    var path = d3.geoPath(proj);
    var svg = d3.select("#map"), g = svg.append("g");
    var outGeo = {}; projects.forEach(function (p) { if (!p.frame) p.geo.forEach(function (x) { outGeo[x] = 1; }); });

    g.append("g").selectAll("path").data(countries.filter(function (f) { return !(byGeo[f.id] && byGeo[f.id].frame); })).join("path")
      .attr("class", function (f) { return "land" + (outGeo[f.id] ? " out" : ""); }).attr("d", path)
      .append("title").text(function (f) { var p = byGeo[f.id]; return f.properties.name + (p ? ": documents held, outside the frame" : ""); });
    var inFrame = countries.filter(function (f) { return byGeo[f.id] && byGeo[f.id].frame; });
    var shapes = g.append("g").selectAll("path").data(inFrame).join("path").attr("class", "proj").attr("d", path)
      .attr("tabindex", -1);
    // small territories as markers (projected area below a threshold), one marker per project
    var small = {};
    inFrame.forEach(function (f) { var p = byGeo[f.id]; if (p.code !== "EU" && path.area(f) < 30) small[p.code] = f; });
    var markers = g.append("g").selectAll("circle").data(Object.keys(small).map(function (c) { return { p: P[c], f: small[c] }; })).join("circle")
      .attr("class", "marker").attr("r", 5).attr("cx", function (d) { return path.centroid(d.f)[0]; }).attr("cy", function (d) { return path.centroid(d.f)[1]; });

    var tip = $("tip"), box = document.querySelector(".map-box");
    function over(ev, p) {
      shapes.classed("hl", function (f) { return byGeo[f.id] === p; });
      var r = box.getBoundingClientRect();
      tip.innerHTML = "<b>" + S.esc(p.name) + "</b> · " + S.esc(label(p)); tip.style.left = (ev.clientX - r.left) + "px"; tip.style.top = (ev.clientY - r.top) + "px"; tip.style.opacity = 1;
    }
    function out() { shapes.classed("hl", false); tip.style.opacity = 0; }
    shapes.on("mousemove", function (ev, f) { over(ev, byGeo[f.id]); }).on("mouseleave", out).on("click", function (ev, f) { select(byGeo[f.id].code); });
    markers.on("mousemove", function (ev, d) { over(ev, d.p); }).on("mouseleave", out).on("click", function (ev, d) { select(d.p.code); });

    var zoom = d3.zoom().scaleExtent([1, 12]).translateExtent([[0, 0], [W, H]]).on("zoom", function (ev) {
      g.attr("transform", ev.transform);
      markers.attr("r", 5 / Math.sqrt(ev.transform.k)).style("stroke-width", 0.8 / ev.transform.k);
      shapes.style("stroke-width", null);
    });
    svg.call(zoom);
    $("zin").onclick = function () { svg.transition().call(zoom.scaleBy, 1.6); };
    $("zout").onclick = function () { svg.transition().call(zoom.scaleBy, 1 / 1.6); };
    $("zreset").onclick = function () { svg.transition().call(zoom.transform, d3.zoomIdentity); };

    function paint() {
      shapes.attr("fill", function (f) { return colour(byGeo[f.id]); }).classed("sel", function (f) { return state.sel && byGeo[f.id].code === state.sel; });
      markers.attr("fill", function (d) { return colour(d.p); }).classed("sel", function (d) { return d.p.code === state.sel; });
      $("yr-box").style.visibility = state.mode === "docs" ? "visible" : "hidden";
      legend();
    }
    function legend() {
      var items;
      if (state.mode === "status") {
        var seen = {}; frame.forEach(function (p) { seen[p.status] = (seen[p.status] || 0) + 1; });
        items = meta.status_order.filter(function (s) { return seen[s]; }).map(function (s) { return [S.STATUS[s][1], S.STATUS[s][0] + " (" + seen[s] + ")"]; });
      } else if (state.mode === "docs") {
        var cnt = DOC_BINS.map(function () { return 0; }); frame.forEach(function (p) { cnt[bin(pubsUpTo(p, state.year))]++; });
        items = DOC_BINS.map(function (b, i) { return [DOC_COL[i], b[2] + " (" + cnt[i] + ")"]; });
      } else if (state.mode === "tier") {
        items = ["T1", "T2", "T3"].map(function (t) { return [TIER[t][1], TIER[t][0] + " (" + frame.filter(function (p) { return p.tier === t; }).length + ")"]; });
      } else {
        items = [y0, Math.round((y0 + y1) / 2), y1].map(function (y) { return [FIRST(y), String(y)]; }).concat([[DOC_COL[0], "none"]]);
      }
      $("legend").innerHTML = items.map(function (i) { return '<span><i style="background:' + i[0] + '"></i>' + S.esc(i[1]) + "</span>"; }).join("") +
        '<span><i style="background:var(--land-out)"></i>outside the frame, documents held</span>';
    }

    // panel
    function select(code) {
      state.sel = code; paint(); panel(P[code]);
      history.replaceState(null, "", "#" + code + (state.mode !== "status" ? "" : ""));
      if (window.innerWidth < 980) $("panel").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function panel(p) {
      if (!p) {
        var n = {}, pubs = 0;
        frame.forEach(function (q) { Object.keys(q.n).forEach(function (k) { n[k] = (n[k] || 0) + q.n[k]; }); pubs += q.pubs; });
        $("panel").innerHTML = "<h2>44 projects</h2><div class='sub'>Click a country or a row of the table below.</div>" +
          "<p><b>" + pubs + "</b> evidence publications, <b>" + n.companion + "</b> companions and <b>" + ((n.dropped || 0) + (n.wholesale || 0)) + "</b> documents not used, for the projects in the frame.</p>" +
          "<p><a class='btn sm' href='documents.html'>Browse all documents</a></p>";
        return;
      }
      var mine = docs.filter(function (d) { return d.p === p.code; });
      var ev = mine.filter(function (d) { return d.c === "evidence" && !d.same; }).sort(function (a, b) { return (b.y || 0) - (a.y || 0); });
      var st = S.STATUS[p.status] || S.STATUS.NA;
      var max = Math.max.apply(null, S.CAT_ORDER.map(function (c) { return p.n[c]; }).concat([1]));
      var bars = S.CAT_ORDER.map(function (c) {
        return '<div class="bar"><span>' + S.CAT[c].label + '</span><span class="track"><span class="fill b-' + c + '" style="display:block;width:' + (100 * p.n[c] / max) + '%;background:currentColor"></span></span><span class="v">' + p.n[c] + "</span></div>";
      }).join("");
      var ys = []; for (var y = y0; y <= y1; y++) ys.push(y);
      var mx = Math.max.apply(null, ys.map(function (y) { return p.ev_by_year[y] || 0; }).concat([1]));
      var spark = p.frame ? '<div class="small muted">Evidence publications by year</div><div class="spark" aria-hidden="true">' + ys.map(function (y) { return '<i style="height:' + (100 * (p.ev_by_year[y] || 0) / mx) + '%" title="' + y + ": " + (p.ev_by_year[y] || 0) + '"></i>'; }).join("") + '</div><div class="spark-x"><span>' + y0 + "</span><span>" + y1 + "</span></div>" : "";
      var en = p.frame && p.pubs ? '<p class="small" style="margin-top:12px">English text for measurement: ' + Object.keys(p.english).filter(function (k) { return p.english[k]; }).map(function (k) { return p.english[k] + " " + k; }).join(", ") + ".</p>" : "";
      $("panel").innerHTML = "<h2>" + S.esc(p.name) + "</h2><div class='sub'>" + (p.project_name ? S.esc(p.project_name) + " · " : "") + (p.frame ? "tier " + S.esc(S.tierLabel(p.tier)) : "outside the frame") + "</div>" +
        '<p><span class="dot" style="background:' + st[1] + '"></span> <b>' + S.esc(st[0]) + "</b>" + (p.status_date ? " as of " + S.esc(p.status_date) : "") +
        (p.status_url ? ' · <a href="' + S.esc(p.status_url) + '" target="_blank" rel="noopener">source ↗</a>' : "") + "</p>" +
        (p.members.length ? "<p class='small muted'>One project for " + p.members.length + " member states; documents of the ECB and of national central banks of the euro area belong to it.</p>" : "") +
        bars + spark + en +
        (ev.length ? "<h3>Evidence publications</h3><ul class='plain doclist'>" + ev.slice(0, 8).map(function (d) {
          return "<li><span class='muted'>" + (d.y || "n.d.") + "</span> " + (d.u ? '<a href="' + S.esc(d.u) + '" target="_blank" rel="noopener">' + S.esc(d.t) + "</a>" : S.esc(d.t)) + "</li>";
        }).join("") + "</ul>" : "") +
        "<p style='margin-top:12px'><a class='btn sm' href='documents.html#project=" + p.code + "'>All " + mine.length + " documents of " + S.esc(p.name) + "</a></p>";
    }

    // table
    var rows = frame.slice().sort(function (a, b) { return a.name.localeCompare(b.name); });
    d3.select("#ptable tbody").selectAll("tr").data(rows).join("tr").attr("tabindex", 0)
      .html(function (p) {
        var st = S.STATUS[p.status] || S.STATUS.NA;
        return "<td><b>" + S.esc(p.name) + "</b>" + (p.project_name ? "<div class='small muted'>" + S.esc(p.project_name) + "</div>" : "") + "</td>" +
          '<td><span class="dot" style="background:' + st[1] + '"></span> ' + S.esc(st[0]) + "</td><td>" + S.esc(p.tier) + (p.tier === "T3" ? "<div class='small muted'>exploratory</div>" : "") + "</td>" +
          '<td class="n">' + p.pubs + "</td><td>" + (p.ev_years.length ? p.ev_years[0] + (p.ev_years[1] !== p.ev_years[0] ? " to " + p.ev_years[1] : "") : "") + "</td>" +
          '<td class="n">' + p.n.companion + '</td><td class="n">' + ((p.n.dropped || 0) + (p.n.wholesale || 0)) + "</td>";
      })
      .on("click", function (ev, p) { select(p.code); window.scrollTo({ top: 0, behavior: "smooth" }); })
      .on("keydown", function (ev, p) { if (ev.key === "Enter") select(p.code); });

    $("mode").addEventListener("change", function () { state.mode = this.value; paint(); });
    $("year").addEventListener("input", function () { state.year = +this.value; $("year-out").textContent = state.year; paint(); });
    var timer = null;
    $("play").addEventListener("click", function () {
      if (timer) { clearInterval(timer); timer = null; this.textContent = "▶"; return; }
      var b = this; b.textContent = "❚❚"; state.year = y0 - 1;
      timer = setInterval(function () {
        state.year++; $("year").value = state.year; $("year-out").textContent = state.year; paint();
        if (state.year >= y1) { clearInterval(timer); timer = null; b.textContent = "▶"; }
      }, 700);
    });
    paint();
    var start = location.hash.slice(1);
    if (P[start]) select(start); else panel(null);
  }
})();
