// Side rail: a fixed, collapsible list of the page's sections that stays on the left while scrolling.
// Home page: About, Experience, Skills, Projects, Contact. Project pages: the page's own section headings.
(function () {
  var isHome = !!document.querySelector(".hero.container");
  var items = [];

  if (isHome) {
    [["top", "Top"], ["about", "About"], ["experience", "Experience"], ["skills", "Skills"],
     ["projects", "Projects"], ["contact", "Contact"]].forEach(function (p) {
      var el = document.getElementById(p[0]);
      if (el) items.push({ id: p[0], label: p[1], el: el });
    });
  } else {
    var header = document.querySelector(".project-header") || document.querySelector("main h1");
    if (header) {
      if (!header.id) header.id = "overview";
      items.push({ id: header.id, label: "Overview", el: header });
    }
    var n = 0;
    document.querySelectorAll("main .study-section > h2, main .overview, main #live-demo > h2").forEach(function (h) {
      var target = h.classList && h.classList.contains("overview") ? h : (h.closest("section") || h);
      var label = h.classList && h.classList.contains("overview") ? "Summary" : h.textContent.trim();
      if (!label) return;
      if (!target.id) target.id = "sec-" + (++n);
      items.push({ id: target.id, label: label.length > 28 ? label.slice(0, 26) + "…" : label, el: target });
    });
  }
  if (items.length < 3) return;

  var store = { get: function () { try { return localStorage.getItem("railOpen"); } catch (e) { return null; } },
                set: function (v) { try { localStorage.setItem("railOpen", v); } catch (e) {} } };

  var rail = document.createElement("nav");
  rail.className = "rail";
  rail.setAttribute("aria-label", "On this page");
  var toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "rail-toggle";
  toggle.innerHTML = '<span class="rail-chev" aria-hidden="true"></span><span class="rail-title">On this page</span>';
  var list = document.createElement("ol");
  list.id = "rail-list";
  toggle.setAttribute("aria-controls", "rail-list");
  items.forEach(function (it) {
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = "#" + it.id;
    a.innerHTML = '<span class="rail-dot" aria-hidden="true"></span><span class="rail-label"></span>';
    a.querySelector(".rail-label").textContent = it.label;
    a.title = it.label;
    li.appendChild(a);
    list.appendChild(li);
    it.a = a;
  });
  if (!isHome) {
    var li = document.createElement("li");
    li.className = "rail-back";
    var slug = (location.pathname.split("/").pop() || "").replace(/\.html$/, "");
    li.innerHTML = '<a href="../index.html#' + (slug ? "p-" + slug : "projects") + '"><span class="rail-dot" aria-hidden="true">←</span><span class="rail-label">All projects</span></a>';
    list.appendChild(li);
  }
  rail.appendChild(toggle);
  rail.appendChild(list);
  document.body.appendChild(rail);

  var compact = window.matchMedia("(max-width: 1259px)");
  function setOpen(open, remember) {
    rail.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Collapse section menu" : "Expand section menu");
    if (remember) store.set(open ? "1" : "0");
  }
  setOpen(!compact.matches && store.get() === "1", false);
  toggle.addEventListener("click", function () { setOpen(!rail.classList.contains("open"), true); });
  list.addEventListener("click", function (e) {
    if (e.target.closest("a") && compact.matches) setOpen(false, false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && rail.classList.contains("open") && compact.matches) { setOpen(false, false); toggle.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (compact.matches && rail.classList.contains("open") && !rail.contains(e.target)) setOpen(false, false);
  });

  var ticking = false;
  function update() {
    ticking = false;
    var vh = window.innerHeight, y = window.scrollY;
    rail.classList.toggle("shown", y > vh * 0.45);
    var current = 0;
    items.forEach(function (it, i) { if (it.el.getBoundingClientRect().top < vh * 0.35) current = i; });
    if (y + vh >= document.documentElement.scrollHeight - 4) current = items.length - 1;
    items.forEach(function (it, i) {
      it.a.classList.toggle("active", i === current);
      if (i === current) it.a.setAttribute("aria-current", "location"); else it.a.removeAttribute("aria-current");
    });
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  window.addEventListener("resize", update);
  update();
})();
