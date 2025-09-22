(function () {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRegister);
  } else {
    initRegister();
  }

  function initRegister() {
    const form = document.getElementById("register-form");
    const status = document.getElementById("status");
    if (!form || !status) {
      console.error("Register form elements not found");
      return;
    }

    // Wait for API module to be available
    if (!window.api) {
      window.addEventListener("apiReady", initRegister, { once: true });
      return;
    }

    let isRegistering = false;

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();

      status.textContent = "회원가입 진행 중...";

      const email = /** @type {HTMLInputElement} */ (
        document.getElementById("email")
      ).value;
      const name = /** @type {HTMLInputElement} */ (
        document.getElementById("name")
      ).value;
      const password = /** @type {HTMLInputElement} */ (
        document.getElementById("password")
      ).value;
      const rePassword = /** @type {HTMLInputElement} */ (
        document.getElementById("re-password")
      ).value;

      if (password !== rePassword) {
        status.textContent = "비밀번호가 일치하지 않습니다.";
        return;
      }

      try {
        isRegistering = true;

        const data = await window.api.post("auth/register", {
          body: {
            email: email,
            password: password,
            name: name,
          },
        });

        if (data) {
          status.textContent = "회원가입에 성공하였습니다.";
          window.location.href = "/login";
        } else {
          status.textContent = "회원가입에 실패하였습니다.";
        }
      } catch (e) {
        console.error("Registration error:", e);
        status.textContent = `실패: ${
          e.status || e.message || "알 수 없는 오류"
        }`;
      } finally {
        isRegistering = false;
      }
    });
  }
})();
