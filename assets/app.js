/* AI Engineering course: progress, reading settings, sync between devices, search, quizzes,
   mobile navigation, resume reading and offline support. No dependencies. */
(function () {
  "use strict";

  var KEY = "aie-progress-v1";
  var PREFS_KEY = "aie-prefs";
  var LAST_KEY = "aie-last";
  var docEl = document.documentElement;
  var body = document.body;
  var root = body.getAttribute("data-root") || "";
  var pageId = body.getAttribute("data-page") || "";
  var COURSE = window.COURSE || { lessons: [] };
  var mobile = window.matchMedia("(max-width: 900px)");

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function readJSON(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || "null") || fallback; } catch (e) { return fallback; }
  }
  function writeJSON(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* private mode: keep in memory */ }
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // ------------------------------------------------------------ toast
  var toastTimer = null;
  function toast(msg, actionLabel, action) {
    var t = $(".toast");
    if (!t) { t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); body.appendChild(t); }
    t.innerHTML = "<span>" + esc(msg) + "</span>";
    if (actionLabel) {
      var b = document.createElement("button");
      b.type = "button"; b.textContent = actionLabel;
      b.addEventListener("click", function () { t.hidden = true; action(); });
      t.appendChild(b);
    }
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.hidden = true; }, actionLabel ? 9000 : 3500);
  }

  // ------------------------------------------------------------ progress
  var progress = readJSON(KEY, {});
  function save() { writeJSON(KEY, progress); }
  function doneCount(slug, n) {
    var c = 0;
    for (var i = 0; i < n; i++) if (progress[slug + ":" + i]) c++;
    return c;
  }

  function refresh() {
    $all("input[data-session]").forEach(function (cb) {
      cb.checked = !!progress[cb.getAttribute("data-session")];
      var row = cb.closest(".day-row");
      if (row) row.classList.toggle("is-done", cb.checked);
    });
    $all("[data-lesson][data-sessions]").forEach(function (el) {
      var n = +el.getAttribute("data-sessions");
      var f = n ? doneCount(el.getAttribute("data-lesson"), n) / n : 0;
      el.style.setProperty("--frac", f.toFixed(3));
      if (el.tagName === "A" && el.closest(".course-map")) el.setAttribute("title", Math.round(f * 100) + "% of sessions done");
    });
    $all(".complete-btn").forEach(function (btn) {
      var slug = btn.getAttribute("data-complete"), n = +btn.getAttribute("data-sessions");
      var all = doneCount(slug, n) === n;
      btn.classList.toggle("is-done", all);
      btn.textContent = all ? "Lesson complete. Clear its sessions" : "Mark all sessions done";
    });
    var total = 0, done = 0, next = null;
    COURSE.lessons.forEach(function (l) {
      total += l.sessions;
      var d = doneCount(l.slug, l.sessions);
      done += d;
      if (!next && d < l.sessions) next = l;
    });
    var pt = document.getElementById("progress-text");
    if (pt) pt.textContent = done + " of " + total + " sessions done" + (done ? " (" + Math.round((100 * done) / total) + "%)" : "");
    var cont = document.getElementById("continue-link");
    if (cont && COURSE.lessons.length) {
      if (done === 0) cont.textContent = "Start lesson 00";
      else if (next) { cont.href = root + next.href; cont.textContent = "Continue with lesson " + next.id; }
      else { cont.href = root + COURSE.lessons[COURSE.lessons.length - 1].href; cont.textContent = "Course complete. Revisit the capstones"; }
    }
  }

  document.addEventListener("change", function (e) {
    var t = e.target;
    if (t && t.matches && t.matches("input[data-session]")) {
      var k = t.getAttribute("data-session");
      if (t.checked) progress[k] = 1; else delete progress[k];
      save();
      refresh();
    }
  });
  $all(".complete-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var slug = btn.getAttribute("data-complete"), n = +btn.getAttribute("data-sessions");
      var all = doneCount(slug, n) === n;
      for (var i = 0; i < n; i++) { if (all) delete progress[slug + ":" + i]; else progress[slug + ":" + i] = 1; }
      save();
      refresh();
    });
  });

  // ------------------------------------------------------------ sync between devices
  // A sync code lists, for each lesson with ticks, its slug and a hex bitmask of done sessions.
  function syncCode() {
    var parts = [];
    COURSE.lessons.forEach(function (l) {
      var mask = 0;
      for (var i = 0; i < l.sessions; i++) if (progress[l.slug + ":" + i]) mask |= 1 << i;
      if (mask) parts.push(l.slug + "." + mask.toString(16));
    });
    return parts.join("~");
  }
  function siteBase() {
    if (/^https?:$/.test(location.protocol)) {
      var a = document.createElement("a");
      a.href = root + "index.html";
      return a.href.replace(/index\.html$/, "");
    }
    return COURSE.site_url || "";
  }
  function syncLink() { return siteBase() + "index.html#sync=" + syncCode(); }
  function importSync(code) {
    var added = 0;
    code.split("~").forEach(function (part) {
      var m = /^([a-z0-9-]+)\.([0-9a-f]+)$/.exec(part);
      if (!m) return;
      var mask = parseInt(m[2], 16);
      for (var i = 0; i < 31; i++) {
        if (mask & (1 << i) && !progress[m[1] + ":" + i]) { progress[m[1] + ":" + i] = 1; added++; }
      }
    });
    save();
    refresh();
    return added;
  }
  var hashSync = /^#sync=(.*)$/.exec(location.hash);
  if (hashSync) {
    var n = importSync(decodeURIComponent(hashSync[1]));
    try { history.replaceState(null, "", location.pathname + location.search); } catch (e) { /* ignore */ }
    setTimeout(function () { toast(n ? "Added " + n + " ticked session" + (n === 1 ? "" : "s") + " from your other device." : "Your progress here was already up to date."); }, 300);
  }

  // ------------------------------------------------------------ reading settings
  var prefs = readJSON(PREFS_KEY, null);
  if (!prefs) {
    prefs = {};
    try { var old = localStorage.getItem("aie-theme"); if (old) prefs.theme = old; } catch (e) { /* ignore */ }
  }
  function applyPrefs() {
    if (prefs.theme && prefs.theme !== "auto") docEl.setAttribute("data-theme", prefs.theme); else docEl.removeAttribute("data-theme");
    if (prefs.size && prefs.size !== "m") docEl.setAttribute("data-size", prefs.size); else docEl.removeAttribute("data-size");
    if (prefs.font === "sans") docEl.setAttribute("data-font", "sans"); else docEl.removeAttribute("data-font");
    $all(".seg-ctl").forEach(function (ctl) {
      var key = ctl.getAttribute("data-pref");
      var val = prefs[key] || { theme: "auto", size: "m", font: "serif" }[key];
      $all("button", ctl).forEach(function (b) { b.setAttribute("aria-pressed", b.value === val ? "true" : "false"); });
    });
  }
  applyPrefs();
  $all(".seg-ctl button").forEach(function (b) {
    b.addEventListener("click", function () {
      prefs[b.parentNode.getAttribute("data-pref")] = b.value;
      writeJSON(PREFS_KEY, prefs);
      applyPrefs();
    });
  });

  var dialog = $("dialog.settings");
  function openSettings() {
    if (!dialog) return;
    var input = $(".sync-link", dialog);
    if (input) input.value = syncLink();
    if (dialog.showModal) dialog.showModal(); else dialog.setAttribute("open", "");
  }
  $all(".settings-toggle, .open-settings").forEach(function (b) { b.addEventListener("click", openSettings); });
  if (dialog) {
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
    var copyBtn = $(".sync-copy", dialog), shareBtn = $(".sync-share", dialog), linkInput = $(".sync-link", dialog);
    if (copyBtn) copyBtn.addEventListener("click", function () {
      copyText(linkInput.value, function (ok) { copyBtn.textContent = ok ? "Copied" : "Select and copy"; setTimeout(function () { copyBtn.textContent = "Copy"; }, 1600); });
    });
    if (shareBtn && navigator.share) {
      shareBtn.hidden = false;
      shareBtn.addEventListener("click", function () {
        navigator.share({ title: "My AI Engineering progress", url: linkInput.value }).catch(function () { /* cancelled */ });
      });
    }
    if (linkInput) linkInput.addEventListener("focus", function () { linkInput.select(); });
  }

  // ------------------------------------------------------------ mobile course map
  var navBtn = $(".nav-toggle"), map = $(".course-map"), scrim = $(".scrim");
  function setNav(open) {
    body.classList.toggle("nav-open", open);
    if (navBtn) navBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (scrim) scrim.hidden = !open;
    if (open && map) { var cur = $('a[aria-current="page"]', map) || $("a", map); if (cur) cur.focus({ preventScroll: true }); }
  }
  if (navBtn) navBtn.addEventListener("click", function () { setNav(!body.classList.contains("nav-open")); });
  if (scrim) scrim.addEventListener("click", function () { setNav(false); });
  if (map) map.addEventListener("click", function (e) { if (e.target.closest("a")) setNav(false); });
  var curLink = map && $('a[aria-current="page"]', map);
  if (curLink) map.scrollTop = Math.max(0, curLink.offsetTop - map.clientHeight / 3);

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (body.classList.contains("nav-open")) { setNav(false); if (navBtn) navBtn.focus(); }
    if (body.classList.contains("search-open")) closeSearch();
    if (sheet && !sheet.hidden) setSheet(false);
  });

  // ------------------------------------------------------------ copy and wrap buttons on code
  function copyText(text, done) {
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(true); } catch (e) { done(false); }
      body.removeChild(ta);
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    else fallback();
  }
  $all(".highlight").forEach(function (block) {
    var head = $(".code-head", block), pre = $("pre", block);
    if (!head || !pre) return;
    if (pre.scrollWidth > pre.clientWidth + 4) {
      var wrap = document.createElement("button");
      wrap.type = "button"; wrap.className = "code-btn"; wrap.textContent = "Wrap";
      wrap.setAttribute("aria-pressed", "false");
      wrap.setAttribute("aria-label", "Wrap long lines");
      wrap.addEventListener("click", function () {
        var on = block.classList.toggle("is-wrapped");
        wrap.setAttribute("aria-pressed", on ? "true" : "false");
      });
      head.appendChild(wrap);
    }
    if (block.classList.contains("is-output")) return;
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "code-btn"; btn.textContent = "Copy";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    btn.addEventListener("click", function () {
      copyText(($("code", pre) || pre).innerText.replace(/\n$/, ""), function (ok) {
        btn.textContent = ok ? "Copied" : "Press Ctrl+C";
        setTimeout(function () { btn.textContent = "Copy"; }, 1600);
      });
    });
    head.appendChild(btn);
  });

  // ------------------------------------------------------------ diagrams: scroll and enlarge on phones
  $all(".prose figure.fig").forEach(function (fig) {
    var svg = $("svg.diagram", fig);
    if (!svg) return;
    var box = document.createElement("div");
    box.className = "fig-scroll";
    svg.parentNode.insertBefore(box, svg);
    box.appendChild(svg);
    var b = document.createElement("button");
    b.type = "button"; b.className = "btn-small fig-zoom"; b.textContent = "Enlarge diagram";
    b.addEventListener("click", function () {
      var d = document.createElement("dialog");
      d.className = "zoom";
      d.innerHTML = '<div class="zoom-head"><span>Scroll or pinch to explore. Turn your phone sideways for more room.</span><button type="button" class="btn-small">Close</button></div><div class="zoom-body"></div>';
      $(".zoom-body", d).appendChild(svg.cloneNode(true));
      var lesson = fig.closest(".lesson");
      if (lesson) d.setAttribute("style", lesson.getAttribute("style"));
      body.appendChild(d);
      $("button", d).addEventListener("click", function () { d.close(); });
      d.addEventListener("close", function () { d.remove(); });
      d.showModal();
    });
    var cap = $("figcaption", fig);
    fig.insertBefore(b, cap || null);
  });

  // ------------------------------------------------------------ quizzes
  $all("[data-quiz]").forEach(function (quiz) {
    var qs = $all("[data-q]", quiz), score = $(".quiz-score", quiz), answered = 0, right = 0;
    qs.forEach(function (q) {
      var opts = $all(".quiz-opt", q);
      opts.forEach(function (opt) {
        opt.addEventListener("click", function () {
          if (q.getAttribute("data-done")) return;
          q.setAttribute("data-done", "1");
          var ok = opt.getAttribute("data-correct") === "1";
          answered++;
          if (ok) right++;
          opts.forEach(function (o) { o.disabled = true; if (o.getAttribute("data-correct") === "1") o.classList.add("is-correct"); });
          if (!ok) opt.classList.add("is-wrong");
          var ex = $(".quiz-expl", q);
          if (ex && ex.innerHTML.trim()) ex.hidden = false;
          if (score && answered === qs.length) {
            score.textContent = "You got " + right + " of " + qs.length + "." +
              (right === qs.length ? " Solid." : " Reread the sections behind the ones you missed, then move on.");
          }
        });
      });
    });
  });

  // ------------------------------------------------------------ contents, reading position, lesson bar
  var heads = $all(".prose h2[id], .prose h3[id]");
  var tocLinks = $all(".toc a, .toc-sheet-list a");
  var sectionLabel = $(".lb-section");
  var lessonSlug = $("article.lesson") ? $("article.lesson").getAttribute("data-lesson") : null;
  var article = $("article.lesson .prose");
  var sheet = $("#toc-sheet"), sheetBtn = $(".lb-toc");
  function setSheet(open) {
    if (!sheet) return;
    sheet.hidden = !open;
    if (sheetBtn) sheetBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { var act = $(".toc-sheet-list a.is-active", sheet); if (act) act.scrollIntoView({ block: "center" }); }
  }
  if (sheetBtn) sheetBtn.addEventListener("click", function () { setSheet(sheet.hidden); });
  if (sheet) sheet.addEventListener("click", function (e) { if (e.target === sheet || e.target.closest("a")) setSheet(false); });

  function currentHeading() {
    var line = (mobile.matches ? 80 : 120), cur = null;
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top < line) cur = heads[i]; else break;
    }
    return cur;
  }
  var lastSaved = 0;
  function onScrollWork() {
    var h = currentHeading();
    tocLinks.forEach(function (a) { a.classList.toggle("is-active", !!h && a.getAttribute("href") === "#" + h.id); });
    if (sectionLabel) sectionLabel.textContent = h ? h.textContent.replace(/#$/, "") : sectionLabel.getAttribute("data-default") || sectionLabel.textContent;
    if (article) {
      var r = article.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.6;
      var pct = Math.min(1, Math.max(0, -r.top / Math.max(1, total)));
      docEl.style.setProperty("--read", pct.toFixed(3));
      var now = Date.now();
      if (lessonSlug && now - lastSaved > 1500 && pct > 0.02) {
        lastSaved = now;
        var lessonInfo = COURSE.lessons.filter(function (l) { return l.slug === lessonSlug; })[0];
        var all = readJSON(LAST_KEY, {});
        all.positions = all.positions || {};
        all.positions[lessonSlug] = { y: Math.round(window.scrollY), pct: pct, id: h ? h.id : "" };
        all.latest = { slug: lessonSlug, href: lessonInfo ? lessonInfo.href : "", id: h ? h.id : "", section: h ? h.textContent.replace(/#$/, "") : "",
                       title: lessonInfo ? lessonInfo.id + " " + lessonInfo.short : "", pct: pct, t: now };
        writeJSON(LAST_KEY, all);
      }
    }
  }
  if (sectionLabel) sectionLabel.setAttribute("data-default", sectionLabel.textContent);

  var lastY = window.scrollY, ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.scrollY;
      if (mobile.matches && !body.classList.contains("nav-open") && !body.classList.contains("search-open")) {
        if (y > lastY + 6 && y > 240) body.classList.add("is-scrolling-down");
        else if (y < lastY - 6 || y < 120) body.classList.remove("is-scrolling-down");
      } else body.classList.remove("is-scrolling-down");
      lastY = y;
      onScrollWork();
    });
  }, { passive: true });
  onScrollWork();

  // resume where you stopped
  var lastData = readJSON(LAST_KEY, {});
  if (lessonSlug && !location.hash && lastData.positions && lastData.positions[lessonSlug]) {
    var pos = lastData.positions[lessonSlug];
    var resume = $(".resume");
    if (resume && pos.pct > 0.08 && pos.pct < 0.97) {
      resume.hidden = false;
      $(".resume-btn", resume).addEventListener("click", function () {
        var target = pos.id && document.getElementById(pos.id);
        if (target) target.scrollIntoView(); else window.scrollTo(0, pos.y);
        resume.hidden = true;
      });
    }
  }
  var resumeHome = $(".resume-home");
  if (resumeHome && lastData.latest && lastData.latest.href) {
    var L = lastData.latest, link = $("a", resumeHome);
    link.href = root + L.href + (L.id ? "#" + L.id : "");
    link.textContent = "Pick up where you stopped reading: " + L.title + (L.section ? ", " + L.section : "");
    resumeHome.hidden = false;
  }

  // ------------------------------------------------------------ search (index loads on first use)
  var input = document.getElementById("search-input");
  var box = $(".search-results");
  var docs = null, loading = false, pendingQuery = null;
  function loadIndex(cb) {
    if (docs) return cb();
    pendingQuery = cb;
    if (loading) return;
    loading = true;
    var s = document.createElement("script");
    s.src = root + "assets/search-index.js?v=" + (COURSE.version || "");
    s.onload = function () {
      docs = (window.COURSE_SEARCH || []).map(function (d) {
        return { h: d.h, p: d.p, s: d.s, t: d.t, lp: (d.p || "").toLowerCase(), ls: (d.s || "").toLowerCase(), lt: (d.t || "").toLowerCase() };
      });
      if (pendingQuery) pendingQuery();
    };
    s.onerror = function () { loading = false; if (box) { box.innerHTML = '<div class="r-empty">Search could not load. Check your connection.</div>'; box.hidden = false; } };
    document.head.appendChild(s);
  }
  function count(hay, needle) {
    var n = 0, i = hay.indexOf(needle);
    while (i !== -1 && n < 50) { n++; i = hay.indexOf(needle, i + needle.length); }
    return n;
  }
  function snippet(d, terms) {
    var i = d.lt.indexOf(terms[0]);
    if (i < 0) return esc(d.t.slice(0, 140)) + (d.t.length > 140 ? "…" : "");
    var start = Math.max(0, i - 60);
    var out = esc((start ? "…" : "") + d.t.slice(start, start + 170) + "…");
    terms.forEach(function (t) {
      if (t.length < 2) return;
      out = out.replace(new RegExp("(" + esc(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    });
    return out;
  }
  var active = -1;
  function render(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) { box.hidden = true; return; }
    var results = [];
    docs.forEach(function (d) {
      var score = 0;
      for (var k = 0; k < terms.length; k++) {
        var c = count(d.ls, terms[k]) * 8 + count(d.lp, terms[k]) * 4 + count(d.lt, terms[k]);
        if (!c) return;
        score += c;
      }
      results.push({ d: d, score: score });
    });
    results.sort(function (a, b) { return b.score - a.score; });
    results = results.slice(0, 12);
    active = -1;
    box.innerHTML = results.length ? results.map(function (r) {
      var d = r.d;
      return '<a href="' + esc(root + d.h) + '"><span class="r-title">' + esc(d.s || d.p) + "</span>" +
        (d.s ? '<span class="r-page">' + esc(d.p) + "</span>" : "") + '<span class="r-snip">' + snippet(d, terms) + "</span></a>";
    }).join("") : '<div class="r-empty">No matches for “' + esc(q) + '”. Try a shorter word, such as “rag” or “loss”.</div>';
    box.hidden = false;
  }
  function openSearch() { body.classList.add("search-open"); body.classList.remove("is-scrolling-down"); if (input) input.focus(); }
  function closeSearch() { body.classList.remove("search-open"); if (box) box.hidden = true; if (input) input.blur(); }
  var searchToggle = $(".search-toggle"), searchClose = $(".search-close");
  if (searchToggle) searchToggle.addEventListener("click", openSearch);
  if (searchClose) searchClose.addEventListener("click", closeSearch);
  if (input && box) {
    var timer = null;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { var q = input.value.trim(); loadIndex(function () { render(q); }); }, 80);
    });
    input.addEventListener("focus", function () { loadIndex(function () { if (input.value.trim()) render(input.value.trim()); }); });
    input.addEventListener("keydown", function (e) {
      var links = $all("a", box);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        if (!links.length) return;
        e.preventDefault();
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
        links.forEach(function (a, i) { a.classList.toggle("is-active", i === active); });
        links[active].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        var target = links[active >= 0 ? active : 0];
        if (target) { e.preventDefault(); window.location.href = target.href; }
      }
    });
    box.addEventListener("click", function (e) { if (e.target.closest("a")) closeSearch(); });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".search") && !e.target.closest(".search-toggle")) { box.hidden = true; if (mobile.matches) body.classList.remove("search-open"); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input && !/INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || "")) {
        e.preventDefault();
        openSearch();
      }
    });
  }

  // ------------------------------------------------------------ glossary filter
  var gFilter = $(".g-filter");
  if (gFilter) {
    gFilter.addEventListener("input", function () {
      var q = gFilter.value.trim().toLowerCase(), any = false;
      $all(".g-letter").forEach(function (sec) {
        var shown = 0;
        $all(".g-entry", sec).forEach(function (en) {
          var hit = !q || en.textContent.toLowerCase().indexOf(q) !== -1;
          en.hidden = !hit;
          if (hit) shown++;
        });
        sec.hidden = !shown;
        if (shown) any = true;
      });
      var empty = $(".g-empty");
      if (empty) empty.hidden = any;
    });
  }

  // ------------------------------------------------------------ offline reading (only when served over http/https)
  if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
    navigator.serviceWorker.register(root + "sw.js").then(function (reg) {
      var section = $(".settings .offline"), allBtn = $(".offline-all"), status = $(".offline-status");
      if (!section) return;
      section.hidden = false;
      allBtn.addEventListener("click", function () {
        var sw = reg.active || navigator.serviceWorker.controller;
        if (!sw) { status.textContent = "Offline support is still starting. Try again in a moment."; return; }
        allBtn.disabled = true;
        status.textContent = "Saving lessons…";
        sw.postMessage({ type: "cache-all" });
      });
      navigator.serviceWorker.addEventListener("message", function (e) {
        if (!e.data || e.data.type !== "cache-progress") return;
        status.textContent = e.data.done < e.data.total ? "Saving lessons… " + e.data.done + " of " + e.data.total
          : "Every lesson is saved on this device. You can read without a connection.";
        if (e.data.done >= e.data.total) allBtn.disabled = false;
      });
    }).catch(function () { /* offline support is optional */ });
  }

  // ------------------------------------------------------------ go
  refresh();
  if (body.classList.contains("is-loading")) {
    requestAnimationFrame(function () { requestAnimationFrame(function () { body.classList.remove("is-loading"); }); });
  }
})();
