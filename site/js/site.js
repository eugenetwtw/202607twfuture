(function () {
  function flashButton(btn, message) {
    if (!btn) return;
    var original = btn.textContent;
    btn.textContent = message;
    btn.disabled = true;
    setTimeout(function () {
      btn.textContent = original;
      btn.disabled = false;
    }, 1600);
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand("copy");
        document.body.removeChild(ta);
        if (ok) resolve();
        else reject(new Error("copy failed"));
      } catch (e) {
        reject(e);
      }
    });
  }

  function getComposeText(box) {
    var ta = box.querySelector("[data-compose-text]");
    return ta ? ta.value : "";
  }

  function openShare(network, text, url) {
    var encodedUrl = encodeURIComponent(url);
    var encodedText = encodeURIComponent(text);
    var href = "";
    if (network === "facebook") {
      href = "https://www.facebook.com/sharer/sharer.php?u=" + encodedUrl;
    } else if (network === "x") {
      href =
        "https://twitter.com/intent/tweet?text=" +
        encodedText +
        "&url=" +
        encodedUrl;
    } else if (network === "line") {
      href =
        "https://social-plugins.line.me/lineit/share?url=" +
        encodedUrl +
        "&text=" +
        encodedText;
    } else if (network === "threads") {
      href =
        "https://www.threads.net/intent/post?text=" +
        encodeURIComponent(text + "\n\n" + url);
    }
    if (href) {
      window.open(href, "_blank", "noopener,noreferrer,width=640,height=640");
    }
  }

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

  // Compose / publish box
  document.querySelectorAll("[data-compose-box]").forEach(function (box) {
    var msgText =
      box.getAttribute("data-msg-copied-text") ||
      (document.documentElement.lang === "en" ? "Text copied" : "已複製文案");
    var msgLink =
      box.getAttribute("data-msg-copied-link") ||
      (document.documentElement.lang === "en" ? "Link copied" : "已複製連結");

    // Append live URL into draft once (avoid duplicating on rebuild)
    var ta = box.querySelector("[data-compose-text]");
    if (ta && ta.value.indexOf(location.href) === -1) {
      ta.value = ta.value.replace(/\s*$/, "") + "\n\n" + location.href;
    }

    var copyTextBtn = box.querySelector("[data-copy-text]");
    if (copyTextBtn) {
      copyTextBtn.addEventListener("click", function () {
        copyText(getComposeText(box))
          .then(function () {
            flashButton(copyTextBtn, msgText);
          })
          .catch(function () {
            window.prompt("Text", getComposeText(box));
          });
      });
    }

    var copyUrlBtn = box.querySelector("[data-copy-url]");
    if (copyUrlBtn) {
      copyUrlBtn.addEventListener("click", function () {
        copyText(location.href)
          .then(function () {
            flashButton(copyUrlBtn, msgLink);
          })
          .catch(function () {
            window.prompt("URL", location.href);
          });
      });
    }

    var nativeBtn = box.querySelector("[data-share-native]");
    if (nativeBtn && navigator.share) {
      nativeBtn.hidden = false;
      nativeBtn.addEventListener("click", function () {
        var text = getComposeText(box);
        navigator
          .share({
            title: document.title,
            text: text,
            url: location.href,
          })
          .catch(function () {});
      });
    }

    box.querySelectorAll("[data-share]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openShare(
          btn.getAttribute("data-share"),
          getComposeText(box),
          location.href
        );
      });
    });
  });

  // Standalone copy-url buttons (if any remain outside compose box)
  document.querySelectorAll("[data-copy-url]").forEach(function (btn) {
    if (btn.closest("[data-compose-box]")) return;
    btn.addEventListener("click", function () {
      var url = location.href;
      var done = function () {
        var original = btn.textContent;
        btn.textContent =
          document.documentElement.lang === "en" ? "Copied" : "已複製連結";
        setTimeout(function () {
          btn.textContent = original;
        }, 1600);
      };
      copyText(url).then(done).catch(function () {
        window.prompt("URL", url);
      });
    });
  });

  // Gallery lightbox + slideshow
  (function initGallery() {
    var dataEl = document.getElementById("gallery-data");
    var lb = document.querySelector("[data-gallery-lightbox]");
    if (!dataEl || !lb) return;

    var items = [];
    try {
      items = JSON.parse(dataEl.textContent || "[]");
    } catch (e) {
      return;
    }
    if (!items.length) return;

    var index = 0;
    var playing = false;
    var timer = null;
    var INTERVAL_MS = 4500;

    var imgEl = lb.querySelector("[data-gallery-img]");
    var capEl = lb.querySelector("[data-gallery-caption]");
    var idxEl = lb.querySelector("[data-gallery-index]");
    var totalEl = lb.querySelector("[data-gallery-total]");
    var playBtn = lb.querySelector("[data-gallery-play]");
    var labelPlay = lb.getAttribute("data-label-play") || "Play";
    var labelPause = lb.getAttribute("data-label-pause") || "Pause";

    if (totalEl) totalEl.textContent = String(items.length);

    function stopPlay() {
      playing = false;
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      if (playBtn) playBtn.textContent = labelPlay;
    }

    function startPlay() {
      playing = true;
      if (playBtn) playBtn.textContent = labelPause;
      if (timer) clearInterval(timer);
      timer = setInterval(function () {
        show((index + 1) % items.length);
      }, INTERVAL_MS);
    }

    function show(i) {
      index = (i + items.length) % items.length;
      var item = items[index];
      if (imgEl) {
        imgEl.src = item.src;
        imgEl.alt = (item.caption || "").slice(0, 120);
      }
      if (capEl) capEl.textContent = item.caption || "";
      if (idxEl) idxEl.textContent = String(index + 1);
    }

    function open(i) {
      show(i);
      lb.hidden = false;
      document.body.classList.add("lb-open");
      // focus close for a11y
      var closeBtn = lb.querySelector(".lb__close");
      if (closeBtn) closeBtn.focus();
    }

    function close() {
      stopPlay();
      lb.hidden = true;
      document.body.classList.remove("lb-open");
      if (imgEl) imgEl.removeAttribute("src");
    }

    document.querySelectorAll("[data-gallery-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var i = parseInt(btn.getAttribute("data-gallery-open"), 10) || 0;
        open(i);
      });
    });

    lb.querySelectorAll("[data-gallery-close]").forEach(function (el) {
      el.addEventListener("click", close);
    });

    var prev = lb.querySelector("[data-gallery-prev]");
    var next = lb.querySelector("[data-gallery-next]");
    if (prev) {
      prev.addEventListener("click", function (e) {
        e.stopPropagation();
        show(index - 1);
      });
    }
    if (next) {
      next.addEventListener("click", function (e) {
        e.stopPropagation();
        show(index + 1);
      });
    }
    if (playBtn) {
      playBtn.addEventListener("click", function () {
        if (playing) stopPlay();
        else startPlay();
      });
    }

    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") {
        e.preventDefault();
        close();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        show(index - 1);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        show(index + 1);
      } else if (e.key === " " || e.key === "Spacebar") {
        // space toggles autoplay when lightbox open
        if (e.target && e.target.tagName === "BUTTON") return;
        e.preventDefault();
        if (playing) stopPlay();
        else startPlay();
      }
    });

    // touch swipe
    var touchX = null;
    var stage = lb.querySelector(".lb__stage");
    if (stage) {
      stage.addEventListener(
        "touchstart",
        function (e) {
          if (e.changedTouches && e.changedTouches[0]) {
            touchX = e.changedTouches[0].clientX;
          }
        },
        { passive: true }
      );
      stage.addEventListener(
        "touchend",
        function (e) {
          if (touchX == null || !e.changedTouches || !e.changedTouches[0]) return;
          var dx = e.changedTouches[0].clientX - touchX;
          touchX = null;
          if (Math.abs(dx) < 40) return;
          if (dx > 0) show(index - 1);
          else show(index + 1);
        },
        { passive: true }
      );
    }
  })();
})();
