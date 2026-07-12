(function () {
  // Cluster filters on home
  var filters = document.getElementById("cluster-filters");
  var grid = document.getElementById("issue-grid");
  if (filters && grid) {
    filters.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-filter]");
      if (!btn) return;
      var key = btn.getAttribute("data-filter");
      filters.querySelectorAll(".chip").forEach(function (c) {
        c.classList.toggle("is-active", c === btn);
      });
      grid.querySelectorAll(".issue-card").forEach(function (card) {
        var cluster = card.getAttribute("data-cluster");
        var show = key === "all" || cluster === key;
        card.style.display = show ? "" : "none";
      });
    });
  }

  // Copy page URL
  document.querySelectorAll("[data-copy-url]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var url = location.href;
      var done = function () {
        var original = btn.textContent;
        btn.textContent = document.documentElement.lang === "en" ? "Copied" : "已複製連結";
        setTimeout(function () {
          btn.textContent = original;
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done).catch(function () {
          window.prompt("URL", url);
        });
      } else {
        window.prompt("URL", url);
      }
    });
  });
})();
