function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

function checkHealth() {
  fetch("/api/health-check")
    .then((response) => {
      if (!response.ok) throw new Error("Response was not OK");
    })
    .then(() => {
      const elem = document.getElementById("health-check-state");

      if (elem) {
        elem.classList.remove("text-red-700");
        elem.classList.add("text-green-700");
        elem.innerText = "Healthy";
      }
    })
    .catch(() => {
      const elem = document.getElementById("health-check-state");

      if (elem) {
        elem.classList.remove("text-green-700");
        elem.classList.add("text-red-700");
        elem.innerText = "Unhealthy";
      }
    });
}

function checkSession() {
  const sessionId = getCookie("id");

  if (sessionId) {
    const elem = document.getElementById("session-id");
    if (elem) elem.innerText = sessionId;
  }
}

function checkUptime() {
  fetch("/api/monitor/uptime")
    .then((response) => {
      if (!response.ok) throw new Error("Response was not OK");
      return response.text();
    })
    .then((resp) => {
      const elem = document.getElementById("uptime");
      if (elem) elem.innerText = resp;
    });
}

function checkIdletime() {
  fetch("/api/monitor/idle-time")
    .then((response) => {
      if (!response.ok) throw new Error("Response was not OK");
      return response.text();
    })
    .then((resp) => {
      const elem = document.getElementById("idle-time");
      if (elem) elem.innerText = resp;
    });
}

function checkCpuUsage() {
  fetch("/api/monitor/cpu")
    .then((response) => {
      if (!response.ok) throw new Error("Response was not OK");
      return response.text();
    })
    .then((resp) => {
      const usage = parseFloat(resp).toFixed(2);
      const elem = document.getElementById("cpu-usage");
      if (elem) elem.innerText = `${usage} %`;
    });
}

function checkMemUsage() {
  fetch("/api/monitor/mem")
    .then((response) => {
      if (!response.ok) throw new Error("Response was not OK");
      return response.text();
    })
    .then((resp) => {
      const usage = parseFloat(resp).toFixed(2);
      const elem = document.getElementById("mem-usage");
      if (elem) elem.innerText = `${usage} %`;
    });
}

function checkLogs() {
  fetch("/api/logs")
    .then((response) => {
      if (!response.ok) throw new Error("Response was not OK");
      return response.text();
    })
    .then((resp) => {
      if (resp.length > 0) {
        const elem = document.getElementById("logs");
        if (elem) elem.innerText = resp;
      }
    });
}

function check() {
  checkHealth();
  checkSession();
  checkUptime();
  checkIdletime();
  checkCpuUsage();
  checkMemUsage();
  checkLogs();
}

check();

let intervalId = setInterval(check, 1000);
setTimeout(() => {
  clearInterval(intervalId);
  setInterval(check, 60000);
}, 10000);
