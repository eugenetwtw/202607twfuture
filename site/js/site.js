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
})();
