(function () {
  function initCheckout() {
    // Wait for API module to be available
    if (!window.api) {
      window.addEventListener("apiReady", initCheckout, { once: true });
      return;
    }

    const productId = window.__PRODUCT_ID__;

    // DOM elements
    const quantityInput = document.getElementById("quantity");
    const quantityIncreaseBtn = document.getElementById("quantity-increase");
    const quantityDecreaseBtn = document.getElementById("quantity-decrease");
    const stockInfo = document.getElementById("stock-info");
    const buyerNoteInput = document.getElementById("buyer-note");

    // Address elements
    const useDefaultAddressRadio = document.getElementById(
      "use-default-address"
    );
    const useCustomAddressRadio = document.getElementById("use-custom-address");
    const customAddressForm = document.getElementById("custom-address-form");

    // Summary elements
    const productTotalSpan = document.getElementById("product-total");
    const totalAmountSpan = document.getElementById("total-amount");
    const myBalanceSpan = document.getElementById("my-balance");
    const remainingBalanceSpan = document.getElementById("remaining-balance");
    const remainingBalanceRow = document.getElementById(
      "remaining-balance-row"
    );

    // Action elements
    const placeOrderBtn = document.getElementById("place-order-btn");

    // Get data from server-rendered template
    const productPrice =
      parseInt(productTotalSpan?.textContent.replace(/\D/g, "")) || 0;
    const userBalance =
      parseInt(myBalanceSpan?.textContent.replace(/\D/g, "")) || 0;
    const stockText = stockInfo?.textContent || "";
    const stockMatch = /\d+/.exec(stockText);
    const maxStock =
      stockText.includes("재고") && !stockText.includes("충분")
        ? parseInt(stockMatch?.[0]) || 99
        : 99;

    // State
    let isLoading = false;
    let isPlacingOrder = false;

    // Get quantity from URL parameters
    function getQuantityFromURL() {
      const urlParams = new URLSearchParams(window.location.search);
      const quantity = parseInt(urlParams.get("quantity")) || 1;
      return Math.max(1, quantity);
    }

    // Update quantity controls
    function updateQuantityControls() {
      if (!quantityInput) return;

      const quantity = parseInt(quantityInput.value) || 1;

      // Update quantity buttons
      if (quantityDecreaseBtn) {
        quantityDecreaseBtn.disabled = quantity <= 1;
      }

      if (quantityIncreaseBtn) {
        quantityIncreaseBtn.disabled =
          quantity >= maxStock || stockText.includes("품절");
      }

      // Update summary
      updateSummary();
    }

    // Update summary (dynamic calculation)
    function updateSummary() {
      const quantity = parseInt(quantityInput.value) || 1;
      const productTotal = productPrice * quantity;
      const totalAmount = productTotal; // No shipping fee
      const remainingBalance = userBalance - totalAmount;

      // Update amounts
      if (productTotalSpan) {
        productTotalSpan.textContent = formatCurrency(productTotal);
      }

      if (totalAmountSpan) {
        totalAmountSpan.textContent = formatCurrency(totalAmount);
      }

      if (remainingBalanceSpan) {
        remainingBalanceSpan.textContent = formatCurrency(remainingBalance);
        remainingBalanceSpan.className = `value ${
          remainingBalance >= 0 ? "sufficient" : "insufficient"
        }`;
      }

      // Update order button state
      updateOrderButtonState(remainingBalance, totalAmount);
    }

    // Update order button state
    function updateOrderButtonState(remainingBalance, totalAmount) {
      if (!placeOrderBtn) return;

      if (remainingBalance < 0) {
        placeOrderBtn.disabled = true;
        placeOrderBtn.textContent = "잔액 부족";
        showInsufficientBalanceWarning(totalAmount - userBalance);
      } else {
        placeOrderBtn.disabled = false;
        placeOrderBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        주문하기
      `;
        hideInsufficientBalanceWarning();
      }
    }

    // Show/hide insufficient balance warning
    function showInsufficientBalanceWarning(shortfall) {
      let warningDiv = document.querySelector(".insufficient-balance");
      if (!warningDiv) {
        warningDiv = document.createElement("div");
        warningDiv.className = "insufficient-balance";
        remainingBalanceRow.parentNode.appendChild(warningDiv);
      }
      warningDiv.textContent = `잔액이 ${formatCurrency(
        shortfall
      )} 부족합니다.`;
    }

    function hideInsufficientBalanceWarning() {
      const warningDiv = document.querySelector(".insufficient-balance");
      if (warningDiv) {
        warningDiv.remove();
      }
    }

    // Place order
    async function placeOrder() {
      if (isLoading || isPlacingOrder) return;

      const quantity = parseInt(quantityInput.value) || 1;
      const totalAmount = productPrice * quantity;

      // Check balance
      if (userBalance < totalAmount) {
        alert("잔액이 부족합니다.");
        return;
      }

      try {
        isLoading = true;
        isPlacingOrder = true;
        placeOrderBtn.disabled = true;
        placeOrderBtn.textContent = "주문 처리 중...";

        const orderData = {
          quantity: quantity,
          buyerNote: buyerNoteInput.value || "",
          paymentMethod: "ACCOUNT_BALANCE",
          paymentDetailedId: `pay_${Date.now()}`,
        };

        const response = await window.api.post(
          `products/${encodeURIComponent(productId)}/orders`,
          {
            body: orderData,
          }
        );

        const orderResult = response;

        // Redirect to order detail
        setTimeout(() => {
          window.location.href = `/products/${productId}/orders/${orderResult.id}`;
        }, 1000);
      } catch (error) {
        console.error("Order failed:", error);
        alert("주문에 실패했습니다.");
      } finally {
        isLoading = false;
        isPlacingOrder = false;
        placeOrderBtn.disabled = false;
      }
    }

    // Utility functions
    function formatCurrency(amount) {
      return new Intl.NumberFormat("ko-KR").format(amount) + "원";
    }

    // Event listeners
    function setupEventListeners() {
      // Quantity controls
      if (quantityIncreaseBtn) {
        quantityIncreaseBtn.addEventListener("click", () => {
          const currentValue = parseInt(quantityInput.value) || 1;

          if (currentValue < maxStock && !stockText.includes("품절")) {
            quantityInput.value = currentValue + 1;
            updateQuantityControls();
          }
        });
      }

      if (quantityDecreaseBtn) {
        quantityDecreaseBtn.addEventListener("click", () => {
          const currentValue = parseInt(quantityInput.value) || 1;

          if (currentValue > 1) {
            quantityInput.value = currentValue - 1;
            updateQuantityControls();
          }
        });
      }

      if (quantityInput) {
        quantityInput.addEventListener("input", () => {
          const value = parseInt(quantityInput.value) || 1;

          if (value < 1) {
            quantityInput.value = 1;
          } else if (value > maxStock) {
            quantityInput.value = maxStock;
          }

          updateQuantityControls();
        });
      }

      // Address option toggle
      if (useDefaultAddressRadio && useCustomAddressRadio) {
        useDefaultAddressRadio.addEventListener("change", () => {
          if (useDefaultAddressRadio.checked) {
            customAddressForm.style.display = "none";
          }
        });

        useCustomAddressRadio.addEventListener("change", () => {
          if (useCustomAddressRadio.checked) {
            customAddressForm.style.display = "block";
          }
        });
      }

      // Place order
      if (placeOrderBtn) {
        placeOrderBtn.addEventListener("click", placeOrder);
      }
    }

    // Initialize the page
    function init() {
      // Set initial quantity from URL parameter
      const initialQuantity = getQuantityFromURL();
      if (quantityInput) {
        quantityInput.value = initialQuantity;
      }

      setupEventListeners();
      updateQuantityControls();
    }

    // Start the application
    init();
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCheckout);
  } else {
    initCheckout();
  }
})();
