/* Results page: the privacy index with its interval, the PET profile and talk beside the index, by tier.
   Reads assets/results.json (scripts/site/build_results_data.py) and assets/projects.json for names.
   Rows are listed by tier and name, never sorted by a value (no league table, index spec §6). */
(function () {
  "use strict";
  var S = window.SITE, $ = function (id) { return document.getElementById(id); };
  var CELL = {
    F1: "Central bank can link online payments to a person", F2: "Intermediary can link online payments to a person",
    F4: "Private offline payments available", F7: "Low-identity route (anonymous holding and paying)",
    F8: "Identity required at onboarding", F9: "Targeted re-identification possible", F10: "Programmable restrictions"
  };
  var F3 = { via_psp: "via the intermediary", via_cb: "via the central bank", via_both: "via both", none_stated: "none stated", undetermined: "not determined" };
  var TIER = { T1: "T1 · core", T2: "T2 · core", T3: "T3 · exploratory, often unfinished CBDC research" };
  var VERDICT = { holds: "holds", fails: "does not hold", inconclusive: "inconclusive" };
  var RUNG = ["not stated", "considered", "tested", "endorsed", "operational"];
  function pct(x) { return x == null ? "–" : Math.round(100 * x) + "%"; }
  function num(x, d) { return x == null ? "–" : Number(x).toFixed(d == null ? 2 : d); }
  function pet(code) { return code.replace(/^other:/, "other: ").replace(/_/g, " "); }

  function bar(iv, cls) {
    var lo = 100 * iv[0], hi = 100 * iv[1];
    return '<span class="ivbar ' + (cls || "") + '" role="img" aria-label="from ' + num(iv[0]) + " to " + num(iv[1]) + '">' +
      '<span class="iv" style="left:' + lo + "%;width:" + Math.max(hi - lo, 1.2) + '%"></span></span>' +
      '<span class="ivnum">' + num(iv[0]) + "–" + num(iv[1]) + "</span>";
  }

  Promise.all([S.get("assets/results.json"), S.get("assets/projects.json").catch(function () { return { projects: [] }; })]).then(function (r) {
    var R = r[0], names = {};
    r[1].projects.forEach(function (p) { names[p.code] = p.name; });
    var name = function (id) { return names[id] || id; };

    if (R.mock) {
      var b = $("mock-banner");
      b.hidden = false;
      b.innerHTML = "<strong>Test data.</strong> Every number on this page is invented (projects MOCK01 to MOCK44) to try out the page before the real results exist. Nothing here is a result.";
      document.title = "TEST DATA · " + document.title;
    }
    $("as-of").innerHTML = (R.mock ? "<strong>Test data, not a result.</strong> " : "") + "Run <code>" + S.esc(R.label) + "</code>, " + R.projects.length + " projects. Inputs and their SHA-256 are listed in <a href='assets/results.json' download>results.json</a>.";

    // hypothesis
    var H = R.hypothesis, n = H.n_core, maj = R.definitions.majority;
    var scale = function (k) { return (100 * k / n) + "%"; };
    $("hyp").innerHTML =
      '<div class="hyp-head"><div><div class="small muted">Verdict' + (R.mock ? " (test data)" : "") + '</div><div class="verdict v-' + H.verdict + '">' + VERDICT[H.verdict] + "</div></div>" +
      '<div class="stat"><b>' + H.L + "</b><span>core projects meet both at the least favourable reading (L)</span></div>" +
      '<div class="stat"><b>' + H.U + "</b><span>at the most favourable reading (U)</span></div></div>" +
      '<div class="lu" role="img" aria-label="L ' + H.L + ", U " + H.U + ", majority " + maj + " of " + n + '">' +
      '<span class="lu-range" style="left:' + scale(H.L) + ";width:" + scale(H.U - H.L) + '"></span>' +
      '<span class="lu-maj" style="left:' + scale(maj - 0.5) + '"><i>majority: ' + maj + " of " + n + "</i></span>" +
      '<span class="lu-tick" style="left:' + scale(H.L) + '">L</span><span class="lu-tick" style="left:' + scale(H.U) + '">U</span></div>' +
      '<div class="lu-axis"><span>0</span><span>' + n + "</span></div>" +
      '<p class="small muted" style="margin:10px 0 0">Holds if L ≥ ' + maj + ", fails if U ≤ " + (maj - 1) + ", inconclusive if the two readings straddle the majority. Least favourable reading: an undetermined cell counts as committed and a sentence without a majority label as not relevant; most favourable: the reverse.</p>";

    // tiers
    $("tiers").innerHTML = Object.keys(R.by_tier).map(function (t) {
      var x = R.by_tier[t];
      return '<div class="card tier t-' + t + '"><h3>' + S.esc(TIER[t] || t) + "</h3>" +
        '<div class="small muted">' + x.n + " projects</div>" +
        '<div class="tier-iv">' + bar([x.stated_lower_mean, x.stated_upper_mean]) + '</div><div class="small muted">mean lower and upper bound of the index</div>' +
        '<p class="small" style="margin:8px 0 0">' + num(x.committed_mean, 1) + " of 7 cells committed on average · PETs named by " + x.with_pet + " of " + x.n + "</p></div>";
    }).join("");

    // table
    var rows = R.projects.slice().sort(function (a, b) { return a.tier.localeCompare(b.tier) || name(a.id).localeCompare(name(b.id)); });
    function paint() {
      var f = $("tier-filter").value, last = "";
      var html = rows.filter(function (p) { return f === "all" || (f === "core" ? p.core : p.tier === f); }).map(function (p) {
        var t = p.talk, head = "";
        if (p.tier !== last) { last = p.tier; head = '<tr class="grp"><th colspan="9" scope="rowgroup">' + S.esc(TIER[p.tier] || p.tier) + "</th></tr>"; }
        return head + '<tr tabindex="0" data-id="' + S.esc(p.id) + '">' +
          "<td><b>" + S.esc(name(p.id)) + "</b><div class='small muted'>" + S.esc(p.tier) + (p.tier === "T3" ? " · exploratory" : "") + "</div></td>" +
          "<td class='ivc'>" + bar(p.index.stated) + "<div class='small muted'>" + p.index.determined + " of " + p.index.of + " cells determined</div></td>" +
          "<td class='ivc'>" + bar(p.index.core4, "thin") + "</td>" +
          "<td>" + S.esc(F3[p.f3] || p.f3) + "</td>" +
          "<td class='n'>" + p.axis2.committed + "</td>" +
          "<td>" + (p.pet.length ? p.pet.map(function (c) { return "<span class='pet'>" + S.esc(pet(c)) + "</span>"; }).join(" ") : "<span class='muted'>none named</span>") + "</td>" +
          "<td class='n'>" + num(t.per_100, 1) + (t.per_100_ci95 ? "<div class='small muted'>" + num(t.per_100_ci95[0], 1) + " to " + num(t.per_100_ci95[1], 1) + "</div>" : "") + "</td>" +
          "<td class='n'>" + pct(t.mechanism_share) + " · " + pct(t.decision_share) + "</td>" +
          "<td class='n'>" + (t.gap[0] === t.gap[1] ? t.gap[0] : t.gap[0] + " to " + t.gap[1]) + " of " + t.aspects + "</td></tr>";
      }).join("");
      document.querySelector("#rtable tbody").innerHTML = html;
    }
    $("tier-filter").addEventListener("change", paint);
    document.querySelector("#rtable tbody").addEventListener("click", function (e) { var tr = e.target.closest("tr[data-id]"); if (tr) detail(tr.getAttribute("data-id")); });
    document.querySelector("#rtable tbody").addEventListener("keydown", function (e) { var tr = e.target.closest("tr[data-id]"); if (tr && e.key === "Enter") detail(tr.getAttribute("data-id")); });
    paint();

    function detail(id) {
      var p = R.projects.filter(function (x) { return x.id === id; })[0]; if (!p) return;
      var c = p.index.components, h = p.hypothesis;
      var cells = R.definitions.index_cells.map(function (f) {
        var v = c[f], r = p.axis2.rungs[f] || 0;
        return "<tr><td><b>" + f + "</b> " + S.esc(CELL[f] || "") + "</td><td>" + (v === 1 ? "more privacy" : v === 0 ? "less privacy" : "<span class='muted'>open (0 to 1)</span>") + "</td><td>" + RUNG[r] + "</td></tr>";
      }).join("");
      var hyp = h ? "<h3>Hypothesis, this project</h3><table class='ptable'><thead><tr><th>Reading</th><th>Much talk</th><th>Few commitments</th><th>Both</th></tr></thead><tbody>" +
        ["lower", "upper"].map(function (k) {
          var x = h[k]; return "<tr><td>" + (k === "lower" ? "least favourable (L)" : "most favourable (U)") + "</td><td>" + (x.much_talk ? "yes" : "no") + " <span class='small muted'>(" + num(x.relevant_per_100, 1) + " per 100)</span></td><td>" + (x.few_commitments ? "yes" : "no") + " <span class='small muted'>(" + x.commitments_counted + " of 4)</span></td><td><b>" + (x.meets_both ? "yes" : "no") + "</b></td></tr>";
        }).join("") + "</tbody></table>" : "<p class='small muted'>Exploratory tier: not part of the hypothesis.</p>";
      var d = $("detail");
      d.hidden = false;
      d.innerHTML = "<h2 style='margin-top:0'>" + S.esc(name(p.id)) + " <span class='small muted'>" + S.esc(TIER[p.tier] || p.tier) + "</span></h2>" +
        (R.mock ? "<p class='mock-inline'>Test data, invented.</p>" : "") +
        "<div class='scroll-x'><table class='ptable'><thead><tr><th>Cell</th><th>Stated design</th><th>Status</th></tr></thead><tbody>" + cells + "</tbody></table></div>" +
        "<p class='small'>Index " + num(p.index.stated[0]) + " to " + num(p.index.stated[1]) + "; committed cells only: " + num(p.index.admissible[0]) + " to " + num(p.index.admissible[1]) + ". Lawful access route: " + S.esc(F3[p.f3] || p.f3) + ".</p>" +
        "<p class='small'>Talk: " + S.fmt(p.talk.own_relevant_units) + " own-voice relevant units of " + S.fmt(p.talk.eligible_units) + " eligible, in " + p.talk.own_voice_publications + " publications; " + p.talk.aspects_talked + " of " + p.talk.aspects + " aspects with a design cell talked about" +
        (p.talk.talk_only_aspects.length ? "; also " + p.talk.talk_only_aspects.map(function (a) { return a.toLowerCase().replace(/_/g, " "); }).join(", ") : "") + ".</p>" + hyp;
      d.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // PET profile
    var pc = R.pet_counts, keys = Object.keys(pc).sort(function (a, b) { return pc[b] - pc[a] || a.localeCompare(b); });
    $("pets").innerHTML = keys.length ? keys.map(function (k) { return "<span class='chip'>" + S.esc(pet(k)) + " <span class='n'>" + pc[k] + "</span></span>"; }).join("") : "<span class='muted'>No technique named yet.</span>";
  }).catch(function (e) {
    $("as-of").textContent = "The results could not be loaded (" + e.message + ").";
  });
})();
