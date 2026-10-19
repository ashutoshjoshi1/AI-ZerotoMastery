/* AI Engineering course: progress tracking, quizzes, search, theme, copy buttons. */
(function () {
  "use strict";

  var KEY = "aie-progress-v1";
  var THEME_KEY = "aie-theme";
  var body = document.body;
  var root = body.getAttribute("data-root") || "";
  var COURSE = window.COURSE || { lessons: [], search: [] };

  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  // ------------------------------------------------------------ storage
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; }
  }
  function save(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* private mode: keep in memory */ }
  }
  var progress = load();

  function doneCount(slug, n) {
    var c = 0;
    for (var i = 0; i < n; i++) if (progress[slug + ":" + i]) c++;
    return c;
  }
  function fraction(slug, n) { return n ? doneCount(slug, n) / n : 0; }

  // ------------------------------------------------------------ progress UI
  function refresh() {
    $all("input[data-session]").forEach(function (cb) {
      cb.checked = !!progress[cb.getAttribute("data-session")];
      var row = cb.closest("tr");
      if (row) row.classList.toggle("is-done", cb.checked);
    });
    $all("[data-lesson][data-sessions]").forEach(function (el) {
      var f = fraction(el.getAttribute("data-lesson"), +el.getAttribute("data-sessions"));
      el.style.setProperty("--frac", f.toFixed(3));
      if (el.tagName === "A" && el.closest(".course-map")) {
        el.setAttribute("title", Math.round(f * 100) + "% of sessions done");
      }
    });
    $all(".complete-btn").forEach(function (btn) {
      var slug = btn.getAttribute("data-complete");
      var n = +btn.getAttribute("data-sessions");
      var all = doneCount(slug, n) === n;
      btn.classList.toggle("is-done", all);
      btn.textContent = all ? "Lesson complete. Clear its sessions" : "Mark all sessions done";
    });
    // home page totals + continue link
    var total = 0, done = 0, next = null;
    COURSE.lessons.forEach(function (l) {
      total += l.sessions;
      var d = doneCount(l.slug, l.sessions);
      done += d;
      if (!next && d < l.sessions) next = l;
    });
    var pt = document.getElementById("progress-text");
    if (pt) {
      pt.textContent = done + " of " + total + " sessions done" + (done ? " (" + Math.round((100 * done) / total) + "%)" : "");
    }
    var cont = document.getElementById("continue-link");
    if (cont) {
      if (done === 0) {
        cont.textContent = "Start lesson 00";
      } else if (next) {
        cont.href = root + next.href;
        cont.textContent = "Continue with lesson " + next.id;
      } else {
        cont.href = root + COURSE.lessons[COURSE.lessons.length - 1].href;
        cont.textContent = "Course complete. Revisit the capstones";
      }
    }
  }

  document.addEventListener("change", function (e) {
    var t = e.target;
    if (t && t.matches && t.matches("input[data-session]")) {
      var k = t.getAttribute("data-session");
      if (t.checked) progress[k] = 1; else delete progress[k];
      save(progress);
      refresh();
    }
  });

  $all(".complete-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var slug = btn.getAttribute("data-complete");
      var n = +btn.getAttribute("data-sessions");
      var all = doneCount(slug, n) === n;
      for (var i = 0; i < n; i++) {
        if (all) delete progress[slug + ":" + i]; else progress[slug + ":" + i] = 1;
      }
      save(progress);
      refresh();
    });
  });

  // ------------------------------------------------------------ theme
  var themeBtn = document.querySelector(".theme-toggle");
  function currentTheme() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* ignore */ }
    });
  }

  // ------------------------------------------------------------ mobile course map
  var navBtn = document.querySelector(".nav-toggle");
  if (navBtn) {
    navBtn.addEventListener("click", function () {
      var open = body.classList.toggle("nav-open");
      navBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && body.classList.contains("nav-open")) {
        body.classList.remove("nav-open");
        navBtn.setAttribute("aria-expanded", "false");
        navBtn.focus();
      }
    });
    var map = document.querySelector(".course-map");
    if (map) {
      map.addEventListener("click", function (e) {
        if (e.target.closest("a")) body.classList.remove("nav-open");
      });
    }
  }
  var cur = document.querySelector('.course-map a[aria-current="page"]');
  if (cur && cur.scrollIntoView) {
    var mapEl = document.querySelector(".course-map");
    if (mapEl) mapEl.scrollTop = Math.max(0, cur.offsetTop - mapEl.clientHeight / 3);
  }

  // ------------------------------------------------------------ copy buttons
  function copyText(text, done) {
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(true); } catch (e) { done(false); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    } else {
      fallback();
    }
  }
  $all(".highlight").forEach(function (block) {
    var pre = block.querySelector("pre");
    if (!pre) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "Copy";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    btn.addEventListener("click", function () {
      var code = pre.querySelector("code") || pre;
      copyText(code.innerText.replace(/\n$/, ""), function (ok) {
        btn.textContent = ok ? "Copied" : "Press Ctrl+C";
        btn.classList.add("is-done");
        setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("is-done"); }, 1600);
      });
    });
    block.appendChild(btn);
  });

  // ------------------------------------------------------------ quizzes
  $all("[data-quiz]").forEach(function (quiz) {
    var qs = $all("[data-q]", quiz);
    var score = quiz.querySelector(".quiz-score");
    var answered = 0, right = 0;
    qs.forEach(function (q) {
      var opts = $all(".quiz-opt", q);
      opts.forEach(function (opt) {
        opt.addEventListener("click", function () {
          if (q.getAttribute("data-done")) return;
          q.setAttribute("data-done", "1");
          var ok = opt.getAttribute("data-correct") === "1";
          answered++;
          if (ok) right++;
          opts.forEach(function (o) {
            o.disabled = true;
            if (o.getAttribute("data-correct") === "1") o.classList.add("is-correct");
          });
          if (!ok) opt.classList.add("is-wrong");
          var ex = q.querySelector(".quiz-expl");
          if (ex && ex.innerHTML.trim()) ex.hidden = false;
          if (score && answered === qs.length) {
            score.textContent = "You got " + right + " of " + qs.length + "." +
              (right === qs.length ? " Solid." : " Reread the sections behind the ones you missed, then move on.");
          }
        });
      });
    });
  });

  // ------------------------------------------------------------ wrap wide tables
  $all(".prose table").forEach(function (t) {
    if (t.parentElement.classList.contains("table-wrap") || t.classList.contains("schedule")) return;
    var w = document.createElement("div");
    w.className = "table-wrap";
    t.parentNode.insertBefore(w, t);
    w.appendChild(t);
  });

  // ------------------------------------------------------------ table of contents highlight
  var tocLinks = $all(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[decodeURIComponent(a.getAttribute("href").slice(1))] = a; });
    var heads = $all(".prose h2[id], .prose h3[id]").filter(function (h) { return byId[h.id]; });
    var visible = {};
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
      var active = null;
      for (var i = 0; i < heads.length; i++) {
        if (visible[heads[i].id]) { active = heads[i]; break; }
      }
      if (!active) {
        for (var j = heads.length - 1; j >= 0; j--) {
          if (heads[j].getBoundingClientRect().top < 120) { active = heads[j]; break; }
        }
      }
      tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
      if (active && byId[active.id]) byId[active.id].classList.add("is-active");
    }, { rootMargin: "-70px 0px -60% 0px" });
    heads.forEach(function (h) { obs.observe(h); });
  }

  // ------------------------------------------------------------ search
  var input = document.getElementById("search-input");
  var box = document.querySelector(".search-results");
  var docs = null;
  function prepare() {
    if (docs) return;
    docs = (COURSE.search || []).map(function (d) {
      return { h: d.h, p: d.p, s: d.s, t: d.t, lp: (d.p || "").toLowerCase(), ls: (d.s || "").toLowerCase(), lt: (d.t || "").toLowerCase() };
    });
  }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function count(hay, needle) {
    var n = 0, i = hay.indexOf(needle);
    while (i !== -1 && n < 50) { n++; i = hay.indexOf(needle, i + needle.length); }
    return n;
  }
  function snippet(d, terms) {
    var i = d.lt.indexOf(terms[0]);
    if (i < 0) return esc(d.t.slice(0, 140)) + (d.t.length > 140 ? "…" : "");
    var start = Math.max(0, i - 60);
    var s = (start ? "…" : "") + d.t.slice(start, start + 170) + "…";
    var out = esc(s);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      var re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }
  var active = -1;
  function render(q) {
    prepare();
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) { box.hidden = true; return; }
    var results = [];
    docs.forEach(function (d) {
      var score = 0;
      for (var k = 0; k < terms.length; k++) {
        var t = terms[k];
        var c = count(d.ls, t) * 8 + count(d.lp, t) * 4 + count(d.lt, t);
        if (!c) return;
        score += c;
      }
      results.push({ d: d, score: score });
    });
    results.sort(function (a, b) { return b.score - a.score; });
    results = results.slice(0, 10);
    active = -1;
    if (!results.length) {
      box.innerHTML = '<div class="r-empty">No matches for “' + esc(q) + '”. Try a shorter word, such as “rag” or “loss”.</div>';
    } else {
      box.innerHTML = results.map(function (r) {
        var d = r.d;
        return '<a href="' + esc(root + d.h) + '"><span class="r-title">' + esc(d.s || d.p) + '</span>' +
          (d.s ? '<span class="r-page">' + esc(d.p) + "</span>" : "") +
          '<span class="r-snip">' + snippet(d, terms) + "</span></a>";
      }).join("");
    }
    box.hidden = false;
  }
  if (input && box) {
    var timer = null;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { render(input.value.trim()); }, 80);
    });
    input.addEventListener("focus", function () { if (input.value.trim()) render(input.value.trim()); });
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
      } else if (e.key === "Escape") {
        box.hidden = true;
        input.blur();
      }
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".search")) box.hidden = true;
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input &&
          !/INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || "")) {
        e.preventDefault();
        input.focus();
      }
    });
  }

  // ------------------------------------------------------------ go
  refresh();
  if (body.classList.contains("is-loading")) {
    requestAnimationFrame(function () { requestAnimationFrame(function () { body.classList.remove("is-loading"); }); });
  }
})();
