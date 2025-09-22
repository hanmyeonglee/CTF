(function () {
  // DOM elements
  const deliveryAddressEl = document.getElementById("delivery-address");
  const homeBtn = document.getElementById("home-btn");

  async function loadDefaultAddress() {
    if (!deliveryAddressEl) return;

    try {
      // Wait for window.api and window.me to be available
      if (!window.api) {
        window.addEventListener("apiReady", loadDefaultAddress, { once: true });
        return;
      }

      if (!window.me) {
        window.addEventListener("userReady", loadDefaultAddress, {
          once: true,
        });
        return;
      }

      let address = null;

      const orderId = window.__ORDER_ID__;
      const buyerId = window.__PRODUCT_BUYER_ID__;
      const cacheSettings = window.__CACHE_SETTINGS__;

      const cacheKey = `cachedOrderDetail`;

      if (
        cacheSettings &&
        cacheSettings.cache &&
        document.cookie.includes(`${cacheKey}=`)
      ) {
        if (!cacheSettings.refresh) {
          const cachedAddress = JSON.parse(
            atob(document.cookie.split(`${cacheKey}=`)[1])
          );

          updateAddressDisplay(cachedAddress);
          return;
        }
      }

      if (window.me && window.me.role === "admin") {
        address = await window.api.get(`address/${orderId}/${buyerId}`);
      } else {
        address = await window.api.get("address");
      }

      if (cacheSettings && cacheSettings.cache) {
        const stringifiedData = btoa(JSON.stringify(address));

        document.cookie = `${cacheKey}=${stringifiedData}; path=${location.pathname}`;
      }

      updateAddressDisplay(address);
    } catch (error) {
      console.error("Failed to load default address:", error);
      deliveryAddressEl.innerHTML =
        '<div class="loading-placeholder">기본 주소를 불러올 수 없습니다.</div>';
    }
  }

  function updateAddressDisplay(address) {
    if (!address || Object.keys(address).length === 0) {
      deliveryAddressEl.innerHTML =
        '<div class="loading-placeholder">배송 주소 정보가 없습니다.</div>';
      return;
    }

    const countryName = getCountryName(address.country);

    deliveryAddressEl.innerHTML = `
      <div class="address-info">
        <div class="address-row">
          <div class="address-label">주소</div>
          <div class="address-value">${address.address || ""}</div>
        </div>
        <div class="address-row">
          <div class="address-label">우편번호</div>
          <div class="address-value">${address.postalCode || ""}</div>
        </div>
        <div class="address-row">
          <div class="address-label">국가</div>
          <div class="address-value">${countryName}</div>
        </div>
      </div>
    `;
  }

  function getCountryName(countryCode) {
    const countryNames = {
      KR: "대한민국",
      US: "미국",
      JP: "일본",
      CN: "중국",
    };

    if (countryNames[countryCode] === undefined) {
      return "지원되지 않는 국가";
    }

    return countryNames[countryCode] || "등록되지 않음";
  }

  // Check if user is seller and setup seller actions
  function checkSellerAndSetupActions() {
    if (window.me) {
      if (
        window.me.id === window.__PRODUCT_SELLER_ID__ &&
        window.me.role === "admin"
      ) {
        setupSellerActions();
      }
    } else if (window.api) {
      // Fetch user info directly if window.me is not available
      window.api
        .get("me/profile")
        .then((me) => {
          if (
            me &&
            me.id === window.__PRODUCT_SELLER_ID__ &&
            me.role === "admin"
          ) {
            setupSellerActions();
          }
        })
        .catch(() => {
          // User not logged in or error, do nothing
        });
    }
  }

  // Try to setup seller actions
  checkSellerAndSetupActions();

  // Wait for user info if not available
  if (!window.me) {
    window.addEventListener("userReady", checkSellerAndSetupActions, {
      once: true,
    });
  }

  let isSellerActionsSetup = false;

  // Setup seller action buttons
  function setupSellerActions() {
    if (isSellerActionsSetup) return;

    const sellerActions = document.getElementById("seller-actions");
    const approveBtn = document.getElementById("approve-btn");
    const cancelBtn = document.getElementById("cancel-btn");

    if (!sellerActions) return;

    // Show seller actions
    sellerActions.style.display = "flex";

    // Show/hide buttons based on order status
    if (approveBtn && cancelBtn) {
      if (window.__ORDER_STATUS__ === "PENDING") {
        // PENDING status - show both buttons
        approveBtn.style.display = "block";
        cancelBtn.style.display = "block";
      } else {
        // Already approved or other status - hide approve button
        approveBtn.style.display = "none";
        cancelBtn.style.display = "block";
      }

      // Remove existing event listeners to prevent duplicates
      approveBtn.onclick = null;
      cancelBtn.onclick = null;

      // Add event listeners
      approveBtn.onclick = () => handleOrderAction("approve");
      cancelBtn.onclick = () => handleOrderAction("cancel");

      isSellerActionsSetup = true;
    }
  }

  let isProcessingAction = false;

  // Handle order actions (approve/cancel)
  async function handleOrderAction(action) {
    if (isProcessingAction) return;

    const orderId = window.__ORDER_ID__;
    const productId = window.__PRODUCT_ID__;

    if (!orderId || !productId) {
      alert("주문 정보를 찾을 수 없습니다.");
      return;
    }

    const actionText = action === "approve" ? "승인" : "취소";

    const button =
      action === "approve"
        ? document.getElementById("approve-btn")
        : document.getElementById("cancel-btn");

    try {
      isProcessingAction = true;

      // Disable button during request
      if (button) {
        button.disabled = true;
        button.textContent = `${actionText} 중...`;
      }

      // Determine new status
      const newStatus = action === "approve" ? "PAID" : "CANCELLED";

      // Check if window.api is available
      if (!window.api) {
        throw new Error("API가 로드되지 않았습니다.");
      }

      // API call to update order status
      await window.api.put(`products/${productId}/orders/${orderId}/status`, {
        body: { status: newStatus },
      });

      // Show success message and reload
      alert(`주문이 성공적으로 ${actionText}되었습니다.`);
      window.location.reload();
    } catch (error) {
      console.error("Order action error:", error);
      alert(`오류가 발생했습니다: ${error.message || "알 수 없는 오류"}`);

      // Re-enable button
      if (button) {
        button.disabled = false;
        button.textContent = action === "approve" ? "주문 승인" : "주문 취소";
      }
    } finally {
      isProcessingAction = false;
    }
  }

  // Event listeners
  if (homeBtn) {
    homeBtn.addEventListener("click", () => {
      window.location.href = "/";
    });
  }

  // Initialize - load default address only if needed
  loadDefaultAddress();
})();
