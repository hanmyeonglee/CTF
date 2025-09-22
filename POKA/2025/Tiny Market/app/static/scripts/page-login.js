(function () {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLogin);
  } else {
    initLogin();
  }

  function initLogin() {
    const form = document.getElementById("login-form");
    const status = document.getElementById("status");
    if (!form || !status) return;

    // Wait for API module to be available
    if (!window.api) {
      window.addEventListener("apiReady", initLogin, { once: true });
      return;
    }

    let isLoggingIn = false;

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();

      if (isLoggingIn) return;

      const email = /** @type {HTMLInputElement} */ (
        document.getElementById("email")
      ).value;
      const password = /** @type {HTMLInputElement} */ (
        document.getElementById("password")
      ).value;

      try {
        isLoggingIn = true;
        status.textContent = "로그인 진행 중...";

        const data = await window.api.post("auth/login", {
          body: {
            email: email,
            password: password,
          },
        });

        if (data && data.apiKey) {
          try {
            const sessionResponse = await fetch("/auth/session", {
              method: "POST",
              headers: {
                "Content-Type": "application/json; charset=utf-8",
                Accept: "application/json; charset=utf-8",
              },
              credentials: "include",
              body: JSON.stringify({ apiKey: data.apiKey }),
            });

            const sessionData = await sessionResponse.json();

            sessionStorage.setItem("apiKey", data.apiKey);

            // Store gateway key in localStorage
            if (sessionData.gateway_key) {
              localStorage.setItem("gateway_key", sessionData.gateway_key);
            }
          } catch (_) {}

          status.textContent = "로그인에 성공하였습니다.";
          window.location.href = "/";
        } else {
          status.textContent = "로그인에 실패하였습니다.";
        }
      } catch (e) {
        status.textContent = `실패: ${e.status || ""}`;
      } finally {
        isLoggingIn = false;
      }
    });
  }
})();
