// Motion layer for the portfolio: scroll reveals, hero entrance, count-up stats,
// word-by-word headings, timeline progress, sticky nav with scroll spy.
// Presentation only: no text or links are changed.
(function () {
  var root = document.documentElement;
  window.__motionReady = true;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasIO = "IntersectionObserver" in window;
  if (!root.classList.contains("motion") || !hasIO) { root.classList.remove("motion"); return; }

  var isHome = !!document.querySelector(".hero.container");

  // ---------- Reveal targets ----------
  var groups = isHome ? [
    ".section-head", ".panel", ".timeline li", ".awards", ".skill", ".group-title",
    ".projects > .project", ".callout", ".credits-block"
  ] : [
    ".project-header > *", ".hero-media", ".facts > div", ".stat-strip > div", ".overview article",
    ".study-section > h2", ".study-section > p", ".study-section > figure", ".study-section > .compare > div",
    ".steps li", ".labs > .lab", ".gallery > figure", ".document-card", ".study-section > .buttons",
    ".study-section > .table-scroll", ".study-section > .split > *", ".card", ".source-note", ".note",
    ".project-return", "main > figure", "main > .buttons"
  ];
  var seen = new Set();
  var targets = [];
  groups.forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (el) {
      if (seen.has(el)) return;
      // Skip anything nested in an element that already reveals, so motion never doubles up.
      for (var p = el.parentElement; p; p = p.parentElement) { if (seen.has(p)) return; }
      seen.add(el); targets.push(el);
    });
  });

  // Hero entrance on the home page: staggered on load.
  if (isHome) {
    var hero = document.querySelector(".hero.container");
    var heroParts = Array.prototype.slice.call(hero.querySelectorAll(":scope > div:first-child > *"));
    var portrait = hero.querySelector(".portrait");
    if (portrait) heroParts.push(portrait);
    heroParts.forEach(function (el, i) {
      el.classList.add("rv"); el.style.setProperty("--rv-delay", (80 + i * 90) + "ms");
    });
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      heroParts.forEach(function (el) { el.classList.add("rv-in"); });
    }); });
  }

  targets.forEach(function (el) { el.classList.add("rv"); if (reduce) el.classList.add("rv-fade"); });

  // Stagger elements that enter the viewport in the same frame.
  var batch = [], scheduled = false;
  function flush() {
    scheduled = false;
    batch.sort(function (a, b) {
      var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
      return (ra.top - rb.top) || (ra.left - rb.left);
    });
    batch.forEach(function (el, i) {
      el.style.setProperty("--rv-delay", Math.min(i * 70, 420) + "ms");
      el.classList.add("rv-in");
      el.addEventListener("transitionend", function done(e) {
        if (e.target !== el) return;
        el.style.removeProperty("--rv-delay");
        el.removeEventListener("transitionend", done);
      });
    });
    batch = [];
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      batch.push(e.target);
    });
    if (batch.length && !scheduled) { scheduled = true; requestAnimationFrame(flush); }
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  targets.forEach(function (el) { io.observe(el); });
  // Anything the reader has already scrolled past (fast scroll, anchor jump, layout shift) is shown at once.
  function revealPassed() {
    targets.forEach(function (el) {
      if (el.classList.contains("rv-in")) return;
      if (el.getBoundingClientRect().bottom < 0) { io.unobserve(el); el.classList.add("rv-in"); }
    });
  }

  // ---------- Count-up for whole-number stats (final text is identical) ----------
  if (!reduce) {
    document.querySelectorAll(".stat-strip strong").forEach(function (el) {
      var text = el.textContent;
      var m = text.match(/^(\D*?)(\d{1,3}(?:,\d{3})+|\d+)(\D*)$/);
      if (!m || /\d/.test(m[1] + m[3])) return;
      var target = parseInt(m[2].replace(/,/g, ""), 10);
      if (!(target > 1)) return;
      var useComma = m[2].indexOf(",") > -1;
      var fmt = function (n) { return useComma ? n.toLocaleString("en-US") : String(n); };
      var cardIO = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return;
        cardIO.disconnect();
        var t0 = performance.now(), dur = 1100;
        (function tick(t) {
          var k = Math.min(1, (t - t0) / dur);
          var eased = 1 - Math.pow(1 - k, 3);
          el.textContent = m[1] + fmt(Math.round(target * eased)) + m[3];
          if (k < 1) requestAnimationFrame(tick); else el.textContent = text;
        })(t0);
      }, { threshold: 0.6 });
      cardIO.observe(el);
    });
  }

  // ---------- Letter-by-letter reveal for the contact heading ----------
  document.querySelectorAll(".callout h2").forEach(function (h) {
    if (h.children.length) return;
    var text = h.textContent.trim();
    var words = text.split(/\s+/);
    h.setAttribute("aria-label", text);
    h.textContent = "";
    var letters = [];
    words.forEach(function (w, i) {
      var ws = document.createElement("span");   // keeps each word on one line
      ws.className = "w"; ws.setAttribute("aria-hidden", "true");
      Array.from(w).forEach(function (ch) {
        var l = document.createElement("span");
        l.className = "l"; l.textContent = ch;
        ws.appendChild(l); letters.push(l);
      });
      h.appendChild(ws);
      if (i < words.length - 1) h.appendChild(document.createTextNode(" "));
    });
    h.classList.add("rw");
    // Once the heading is fully in view (and its card has faded in), letters light up one after another.
    // Time-based, so it never depends on how far the page can scroll.
    var started = false;
    var hio = new IntersectionObserver(function (es) {
      if (started || !es[0].isIntersecting) return;
      started = true; hio.disconnect();
      letters.forEach(function (l, i) {
        setTimeout(function () { l.classList.add("on"); }, 400 + i * 45);
      });
    }, { threshold: 1, rootMargin: "0px 0px -15% 0px" });
    hio.observe(h);
  });

  // ---------- Scroll-linked pieces (rAF throttled) ----------
  var bar = document.createElement("div");
  bar.className = "scroll-progress"; bar.setAttribute("aria-hidden", "true");
  document.body.appendChild(bar);
  var timeline = document.querySelector(".timeline");
  var nav = isHome ? document.querySelector("header.nav") : null;
  if (nav) nav.classList.add("nav-sticky");
  var links = nav ? Array.prototype.slice.call(nav.querySelectorAll('.navlinks a[href^="#"]')) : [];
  var sections = links.map(function (a) { return document.querySelector(a.getAttribute("href")); });

  var ticking = false;
  function update() {
    ticking = false;
    var y = window.scrollY, vh = window.innerHeight;
    var max = document.documentElement.scrollHeight - vh;
    bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, y / max) : 0) + ")";
    if (nav) nav.classList.toggle("stuck", y > 20);
    revealPassed();
    if (timeline) {
      var r = timeline.getBoundingClientRect();
      var p = (vh * 0.7 - r.top) / r.height;
      timeline.style.setProperty("--tl", Math.max(0, Math.min(1, p)).toFixed(3));
    }
    if (links.length) {
      var current = -1;
      sections.forEach(function (s, i) { if (s && s.getBoundingClientRect().top < vh * 0.35) current = i; });
      if (y + vh >= document.documentElement.scrollHeight - 4) current = sections.length - 1;
      links.forEach(function (a, i) { a.classList.toggle("active", i === current); });
    }
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  window.addEventListener("resize", update);
  update();
})();
