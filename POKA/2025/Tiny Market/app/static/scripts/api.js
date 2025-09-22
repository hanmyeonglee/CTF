(function () {
  function getBaseUrl() {
    return location.origin + "/gateway/";
  }

  function buildUrl(path, query) {
    const base = getBaseUrl();
    const url = new URL(path, base);
    if (query && typeof query === "object") {
      Object.entries(query).forEach(([k, v]) => {
        if (v == null) return;
        url.searchParams.set(k, String(v));
      });
    }
    return url.toString();
  }

  async function request(method, path, options) {
    const { query, body, headers, isFormData } = options || {};
    const controller = new AbortController();
    const timeoutMs = (window.ENV && window.ENV.REQUEST_TIMEOUT_MS) || 8000;
    const timeoutId = setTimeout(() => controller.abort("timeout"), timeoutMs);

    const finalHeaders = Object.assign(
      { Accept: "application/json; charset=utf-8" },
      headers || {}
    );

    const apiKey = sessionStorage.getItem("apiKey");
    const gatewayKey = localStorage.getItem("gateway_key");

    if (body && !isFormData && !finalHeaders["Content-Type"])
      finalHeaders["Content-Type"] = "application/json; charset=utf-8";

    if (apiKey) finalHeaders["X-API-Key"] = apiKey;
    if (gatewayKey) finalHeaders["X-Gateway-Key"] = gatewayKey;

    let response;
    try {
      response = await fetch(buildUrl(path, query), {
        method,
        headers: finalHeaders,
        body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
        signal: controller.signal,
        credentials: "include",
      });
    } finally {
      clearTimeout(timeoutId);
    }

    const responseText = await response.text();
    let data = {};
    try {
      data = responseText ? JSON.parse(responseText) : {};
    } catch (parseError) {
      console.warn(
        "JSON Parsing Error:",
        parseError,
        "Response:",
        responseText
      );
      data = {};
    }

    // handle api response error
    if (data.error) {
      const error = new Error("Request failed");
      error.status = 400;
      error.statusText = data.error;
      error.data = null;
      throw error;
    }

    if (!response.ok) {
      const error = new Error("Request failed");
      error.status = response.status;
      error.statusText = response.statusText;
      error.data = data;
      throw error;
    }
    return data;
  }

  window.api = {
    get: (path, opts) => request("GET", path, opts),
    post: (path, opts) => request("POST", path, opts),
    put: (path, opts) => request("PUT", path, opts),
    patch: (path, opts) => request("PATCH", path, opts),
    delete: (path, opts) => request("DELETE", path, opts),
    buildUrl,
  };

  // Notify that API is ready
  window.dispatchEvent(new CustomEvent("apiReady"));
  console.log("API module loaded and ready");
})();
