// Minimal, dependency-free tab switching for the cleanvibe site.
(function () {
  var tabs = document.querySelectorAll(".tab");
  var panels = document.querySelectorAll(".panel");

  function activate(name) {
    tabs.forEach(function (t) {
      var on = t.dataset.tab === name;
      t.classList.toggle("is-active", on);
      t.setAttribute("aria-selected", on ? "true" : "false");
    });
    panels.forEach(function (p) {
      p.classList.toggle("is-active", p.id === name);
    });
    if (history.replaceState) history.replaceState(null, "", "#" + name);
  }

  tabs.forEach(function (t) {
    t.addEventListener("click", function () { activate(t.dataset.tab); });
  });

  // "Pick a tab" cards on the overview panel.
  document.querySelectorAll("[data-goto]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      activate(a.dataset.goto);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  // Honour an incoming #hash so links/refreshes land on the right tab.
  var initial = (location.hash || "").replace("#", "");
  if (initial && document.getElementById(initial)) activate(initial);
})();
