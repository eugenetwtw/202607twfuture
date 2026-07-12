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

  // Gallery lightbox + slideshow (photo mode vs video mode)
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
    var slideMode = "photo"; // "photo" | "video"
    var playing = false;
    var playTimer = null;
    var MIN_SEC = 2;
    var MAX_SEC = 30;
    var DEFAULT_SEC = 5;
    var STORAGE_KEY = "twfuture-gallery-delay-sec";
    var intervalSec = DEFAULT_SEC;
    var remainSec = intervalSec;

    var imgEl = lb.querySelector("[data-gallery-img]");
    var clipEl = lb.querySelector("[data-gallery-clip]");
    var ytEl = lb.querySelector("[data-gallery-video]");
    var stillPane = lb.querySelector("[data-gallery-still-pane]");
    var clipPane = lb.querySelector("[data-gallery-clip-pane]");
    var capEl = lb.querySelector("[data-gallery-caption]");
    var idxEl = lb.querySelector("[data-gallery-index]");
    var totalEl = lb.querySelector("[data-gallery-total]");
    var modeLabel = lb.querySelector("[data-gallery-mode-label]");
    var playBtn = lb.querySelector("[data-gallery-play]");
    var countdownEl = lb.querySelector("[data-gallery-countdown]");
    var delayLabel = lb.querySelector("[data-gallery-delay-label]");
    var delayDec = lb.querySelector("[data-gallery-delay-dec]");
    var delayInc = lb.querySelector("[data-gallery-delay-inc]");
    var fsBtn = lb.querySelector("[data-gallery-fullscreen]");
    var extLink = lb.querySelector("[data-gallery-extlink]");
    var panel = lb.querySelector("[data-gallery-panel]") || lb;
    var labelOpenLink = lb.getAttribute("data-label-open-link") || "Open link";
    var labelPlay = lb.getAttribute("data-label-play") || "Play";
    var labelPause = lb.getAttribute("data-label-pause") || "Pause";
    var labelFs = lb.getAttribute("data-label-fs") || "Fullscreen";
    var labelFsExit = lb.getAttribute("data-label-fs-exit") || "Exit fullscreen";
    var labelModePhoto = lb.getAttribute("data-label-mode-photo") || "Photos";
    var labelModeVideo = lb.getAttribute("data-label-mode-video") || "Clips";
    var docLang = document.documentElement.lang || "";
    var isZh = docLang.indexOf("zh") === 0;
    var isJa = docLang.indexOf("ja") === 0;
    var useSecSuffix = isZh || isJa;

    function photoPool() {
      var out = [];
      for (var i = 0; i < items.length; i++) {
        if (!items[i].youtube_id) out.push(i);
      }
      return out.length ? out : items.map(function (_, i) { return i; });
    }

    function videoPool() {
      var out = [];
      for (var i = 0; i < items.length; i++) {
        if (items[i].clip && !items[i].youtube_id) out.push(i);
      }
      return out;
    }

    function activePool() {
      if (slideMode === "video") {
        var v = videoPool();
        return v.length ? v : photoPool();
      }
      return photoPool();
    }

    function poolPos(pool) {
      var p = pool.indexOf(index);
      return p < 0 ? 0 : p;
    }

    function clampSec(n) {
      n = parseInt(n, 10);
      if (isNaN(n)) return DEFAULT_SEC;
      if (n < MIN_SEC) return MIN_SEC;
      if (n > MAX_SEC) return MAX_SEC;
      return n;
    }

    function loadInterval() {
      try {
        var raw = localStorage.getItem(STORAGE_KEY);
        if (raw != null) intervalSec = clampSec(raw);
      } catch (e) {
        intervalSec = DEFAULT_SEC;
      }
      remainSec = intervalSec;
    }

    function saveInterval() {
      try {
        localStorage.setItem(STORAGE_KEY, String(intervalSec));
      } catch (e) {}
    }

    function formatSec(sec) {
      return useSecSuffix ? sec + " 秒" : sec + "s";
    }

    function renderDelayControls() {
      if (delayLabel) delayLabel.textContent = formatSec(intervalSec);
      if (delayDec) delayDec.disabled = intervalSec <= MIN_SEC;
      if (delayInc) delayInc.disabled = intervalSec >= MAX_SEC;
    }

    function setIntervalSec(next) {
      intervalSec = clampSec(next);
      saveInterval();
      renderDelayControls();
      if (playing) armPlayTimer();
      else {
        remainSec = intervalSec;
        renderCountdown();
      }
    }

    function formatCountdown(sec) {
      if (isJa) return "次 " + sec + " 秒";
      if (isZh) return "下張 " + sec + " 秒";
      return "next " + sec + "s";
    }

    function renderCountdown() {
      if (!countdownEl) return;
      if (!playing) {
        countdownEl.hidden = true;
        countdownEl.textContent = "";
        return;
      }
      countdownEl.hidden = false;
      countdownEl.textContent = formatCountdown(remainSec);
    }

    function clearPlayTimer() {
      if (playTimer) {
        clearInterval(playTimer);
        playTimer = null;
      }
    }

    function armPlayTimer() {
      clearPlayTimer();
      remainSec = intervalSec;
      renderCountdown();
      playTimer = setInterval(function () {
        remainSec -= 1;
        if (remainSec <= 0) {
          step(1);
          remainSec = intervalSec;
        }
        renderCountdown();
      }, 1000);
    }

    function stopPlay() {
      playing = false;
      clearPlayTimer();
      remainSec = intervalSec;
      renderCountdown();
      if (playBtn) playBtn.textContent = labelPlay;
    }

    function startPlay() {
      playing = true;
      if (playBtn) playBtn.textContent = labelPause;
      armPlayTimer();
    }

    function fsElement() {
      return (
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.msFullscreenElement ||
        null
      );
    }

    function isFs() {
      var el = fsElement();
      return !!(el && (el === panel || el === lb || panel.contains(el)));
    }

    function updateFsButton() {
      if (!fsBtn) return;
      fsBtn.textContent = isFs() ? labelFsExit : labelFs;
    }

    function requestFs(el) {
      if (el.requestFullscreen) return el.requestFullscreen();
      if (el.webkitRequestFullscreen) return el.webkitRequestFullscreen();
      if (el.msRequestFullscreen) return el.msRequestFullscreen();
      return Promise.reject(new Error("fullscreen unsupported"));
    }

    function exitFs() {
      if (document.exitFullscreen) return document.exitFullscreen();
      if (document.webkitExitFullscreen) return document.webkitExitFullscreen();
      if (document.msExitFullscreen) return document.msExitFullscreen();
      return Promise.resolve();
    }

    function toggleFullscreen() {
      var p = isFs() ? exitFs() : requestFs(panel);
      if (p && typeof p.then === "function") {
        p.then(updateFsButton).catch(updateFsButton);
      } else updateFsButton();
    }

    function clearMedia() {
      if (ytEl) {
        ytEl.innerHTML = "";
        ytEl.hidden = true;
      }
      if (clipEl) {
        try {
          clipEl.pause();
        } catch (e) {}
        clipEl.removeAttribute("src");
        clipEl.load();
      }
      if (clipPane) clipPane.hidden = true;
      if (stillPane) stillPane.hidden = false;
    }

    function setMode(mode, opts) {
      opts = opts || {};
      var next = mode === "video" ? "video" : "photo";
      var changed = next !== slideMode;
      slideMode = next;
      if (modeLabel) {
        modeLabel.textContent =
          slideMode === "video" ? labelModeVideo : labelModePhoto;
      }
      lb.setAttribute("data-slide-mode", slideMode);
      if (stillPane) {
        stillPane.classList.toggle("is-active-mode", slideMode === "photo");
      }
      if (clipPane) {
        clipPane.classList.toggle("is-active-mode", slideMode === "video");
      }
      // Refresh counter / media behavior for the active pool
      if (opts.refresh !== false && !lb.hidden) {
        var pool = activePool();
        if (slideMode === "video" && pool.length && pool.indexOf(index) < 0) {
          index = pool[0];
        }
        show(index, {
          userOpen: slideMode === "video",
          restartTimer: playing || !!opts.restartTimer,
        });
      }
      return changed;
    }

    function show(i, opts) {
      opts = opts || {};
      index = (i + items.length) % items.length;
      var item = items[index] || {};
      var yt = item.youtube_id || "";
      var clip = item.clip || "";
      var pool = activePool();
      // If current item is outside the active pool, snap to nearest in-pool item
      if (pool.length && pool.indexOf(index) < 0) {
        index = pool[0];
        item = items[index] || {};
        yt = item.youtube_id || "";
        clip = item.clip || "";
      }

      clearMedia();

      if (yt && ytEl) {
        // YouTube tiles stay standalone (not part of photo/video dual stack)
        if (stillPane) stillPane.hidden = true;
        if (clipPane) clipPane.hidden = true;
        ytEl.hidden = false;
        ytEl.innerHTML =
          '<iframe src="https://www.youtube.com/embed/' +
          encodeURIComponent(yt) +
          '?rel=0&modestbranding=1&autoplay=0" title="YouTube" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>';
      } else {
        if (stillPane) stillPane.hidden = false;
        if (imgEl) {
          imgEl.src = item.src || item.poster || "";
          imgEl.alt = (item.caption || "").slice(0, 120);
        }
        if (clip && clipEl && clipPane) {
          clipPane.hidden = false;
          clipEl.poster = item.src || "";
          if (clipEl.getAttribute("src") !== clip) {
            clipEl.src = clip;
            clipEl.load();
          }
          // Autoplay clip only while in video slideshow mode
          if (slideMode === "video" && (opts.userOpen || playing)) {
            var p = clipEl.play();
            if (p && typeof p.catch === "function") p.catch(function () {});
          } else {
            try {
              clipEl.pause();
            } catch (e2) {}
          }
        } else if (clipPane) {
          clipPane.hidden = true;
        }
      }

      if (capEl) capEl.textContent = item.caption || "";
      // counter within active pool
      if (idxEl) idxEl.textContent = String(poolPos(pool) + 1);
      if (totalEl) totalEl.textContent = String(pool.length);
      if (modeLabel) {
        modeLabel.textContent =
          slideMode === "video" ? labelModeVideo : labelModePhoto;
      }
      if (stillPane) {
        stillPane.classList.toggle("is-active-mode", slideMode === "photo");
      }
      if (clipPane) {
        clipPane.classList.toggle(
          "is-active-mode",
          slideMode === "video" && !clipPane.hidden
        );
      }

      if (extLink) {
        if (item.link && !yt) {
          extLink.hidden = false;
          extLink.href = item.link;
          extLink.textContent = labelOpenLink;
        } else if (yt) {
          extLink.hidden = false;
          extLink.href =
            item.link || "https://www.youtube.com/watch?v=" + yt;
          extLink.textContent = "YouTube";
        } else {
          extLink.hidden = true;
          extLink.removeAttribute("href");
        }
      }

      if (playing && opts.restartTimer) armPlayTimer();
    }

    function step(dir) {
      var pool = activePool();
      if (!pool.length) return;
      var pos = poolPos(pool);
      pos = (pos + dir + pool.length) % pool.length;
      show(pool[pos], {
        restartTimer: true,
        userOpen: slideMode === "video",
      });
    }

    function open(i, mode) {
      // Photo thumb → photo pool; clip thumb → video pool
      setMode(mode === "video" ? "video" : "photo", { refresh: false });
      show(i, { userOpen: true });
      lb.hidden = false;
      lb.removeAttribute("hidden");
      document.body.classList.add("lb-open");
      updateFsButton();
      var closeBtn = lb.querySelector(".lb__close");
      if (closeBtn) closeBtn.focus();
    }

    function closeLightbox(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      stopPlay();
      try {
        if (isFs()) {
          var p = exitFs();
          if (p && typeof p.catch === "function") p.catch(function () {});
        }
      } catch (err) {}
      clearMedia();
      lb.hidden = true;
      lb.setAttribute("hidden", "");
      document.body.classList.remove("lb-open");
      if (imgEl) imgEl.removeAttribute("src");
      updateFsButton();
    }

    loadInterval();
    renderDelayControls();
    setMode("photo");

    document.querySelectorAll("[data-gallery-open]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        var i = parseInt(btn.getAttribute("data-gallery-open"), 10) || 0;
        // Clicking the clip badge (or a clip-marked thumb) can enter video mode
        var wantVideo = false;
        if (e.target && e.target.closest) {
          if (e.target.closest(".gallery-thumb__badge--clip")) wantVideo = true;
        }
        if (
          !wantVideo &&
          btn.classList.contains("gallery-thumb--clip") &&
          e.shiftKey
        ) {
          wantVideo = true;
        }
        // Default: open in photo mode (top still). Video mode via badge or
        // by clicking the bottom clip once the lightbox is open.
        open(i, wantVideo ? "video" : "photo");
      });
    });

    lb.querySelectorAll("[data-gallery-close]").forEach(function (el) {
      el.addEventListener("click", closeLightbox);
    });

    var prev = lb.querySelector("[data-gallery-prev]");
    var next = lb.querySelector("[data-gallery-next]");
    if (prev) {
      prev.addEventListener("click", function (e) {
        e.stopPropagation();
        step(-1);
      });
    }
    if (next) {
      next.addEventListener("click", function (e) {
        e.stopPropagation();
        step(1);
      });
    }
    if (playBtn) {
      playBtn.addEventListener("click", function () {
        if (playing) stopPlay();
        else startPlay();
      });
    }
    if (fsBtn) {
      fsBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleFullscreen();
      });
    }
    if (delayDec) {
      delayDec.addEventListener("click", function (e) {
        e.stopPropagation();
        setIntervalSec(intervalSec - 1);
      });
    }
    if (delayInc) {
      delayInc.addEventListener("click", function (e) {
        e.stopPropagation();
        setIntervalSec(intervalSec + 1);
      });
    }

    // Click photo pane → photo slideshow mode (carousel only photos)
    if (stillPane) {
      stillPane.addEventListener("click", function (e) {
        if (e.target && e.target.closest("a,button")) return;
        if (slideMode === "photo") return;
        setMode("photo");
        if (clipEl) {
          try {
            clipEl.pause();
          } catch (err) {}
        }
      });
    }
    // Click / play video pane → video slideshow mode (carousel only clips)
    if (clipPane) {
      clipPane.addEventListener("click", function (e) {
        // Let native video controls work; still switch mode
        if (slideMode === "video") return;
        setMode("video");
      });
    }
    if (clipEl) {
      clipEl.addEventListener("play", function () {
        if (slideMode === "video") return;
        setMode("video", { refresh: false });
        // Update counter only
        var pool = activePool();
        if (idxEl) idxEl.textContent = String(poolPos(pool) + 1);
        if (totalEl) totalEl.textContent = String(pool.length);
        if (modeLabel) modeLabel.textContent = labelModeVideo;
        if (stillPane) stillPane.classList.remove("is-active-mode");
        if (clipPane) clipPane.classList.add("is-active-mode");
        lb.setAttribute("data-slide-mode", "video");
      });
    }

    document.addEventListener("fullscreenchange", updateFsButton);
    document.addEventListener("webkitfullscreenchange", updateFsButton);

    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") {
        if (isFs()) return;
        e.preventDefault();
        closeLightbox(e);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        step(-1);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        step(1);
      } else if (e.key === "f" || e.key === "F") {
        if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA"))
          return;
        e.preventDefault();
        toggleFullscreen();
      } else if (e.key === " " || e.key === "Spacebar") {
        if (e.target && e.target.tagName === "BUTTON") return;
        if (e.target && e.target.tagName === "VIDEO") return;
        e.preventDefault();
        if (playing) stopPlay();
        else startPlay();
      }
    });

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
          if (dx > 0) step(-1);
          else step(1);
        },
        { passive: true }
      );
    }
  })();

})();
