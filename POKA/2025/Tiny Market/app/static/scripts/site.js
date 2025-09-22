(function () {
  function initSite() {
    // Wait for API module to be available
    if (!window.api) {
      window.addEventListener("apiReady", initSite, { once: true });
      return;
    }

    const yearEl = document.getElementById("year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());

    const current = window.location.pathname.replace(/\/$/, "") || "/";
    document.querySelectorAll("nav.nav a[data-nav]").forEach((a) => {
      const href = (a.getAttribute("href") || "").replace(/\/$/, "") || "/";
      if (href === current) a.classList.add("active");
    });

    try {
      const authGroup = document.getElementById("nav-auth");
      const userGroup = document.getElementById("nav-user");

      window.api
        .get("me/profile")
        .then((me) => {
          authGroup.classList.add("hidden");
          userGroup.classList.remove("hidden");

          const nameEl = document.getElementById("nav-username");
          const avatarEl = document.getElementById("nav-avatar");

          window.me = me;

          // Notify that user info is ready
          window.dispatchEvent(new CustomEvent("userReady"));

          if (nameEl && me && me.name) nameEl.textContent = me.name;
          if (avatarEl && me && me.profileImageUrl)
            avatarEl.src =
              me.profileImageUrl == "NONE"
                ? "/static/assets/default-profile.png"
                : me.profileImageUrl;
        })
        .catch((e) => {
          if (e.status === 401 && e.statusText === "SESSION_EXPIRED") {
            window.location.href = "/login";
          }
        });
    } catch (_) {}
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSite);
  } else {
    initSite();
  }
})();
