(function () {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProductDetail);
  } else {
    initProductDetail();
  }

  function initProductDetail() {
    const productId = window.__PRODUCT_ID__;

    // DOM elements
    const quantityEl = document.getElementById("quantity");
    const quantityIncreaseEl = document.getElementById("quantity-increase");
    const quantityDecreaseEl = document.getElementById("quantity-decrease");
    const buyBtn = document.getElementById("buy-now");
    const totalPriceEl = document.getElementById("total-price");
    const stockInfoEl = document.getElementById("stock-info");

    if (!productId) return;

    // Get product data from template (passed from server)
    const productPrice =
      parseInt(
        document
          .getElementById("detail-product-price")
          ?.textContent.replace(/\D/g, "")
      ) || 0;
    const stockText = stockInfoEl?.textContent || "";
    const stockMatch = /\d+/.exec(stockText);
    const maxStock =
      stockText.includes("재고") && !stockText.includes("충분")
        ? parseInt(stockMatch?.[0]) || 99
        : 99;

    // Quantity controls
    function updateQuantityControls() {
      if (!quantityEl) return;

      const quantity = parseInt(quantityEl.value) || 1;

      // Update quantity buttons
      if (quantityDecreaseEl) {
        quantityDecreaseEl.disabled = quantity <= 1;
      }

      if (quantityIncreaseEl) {
        quantityIncreaseEl.disabled =
          quantity >= maxStock || stockText.includes("품절");
      }

      // Update total price
      updateTotalPrice();
    }

    function updateTotalPrice() {
      if (!totalPriceEl || !quantityEl) return;

      const quantity = parseInt(quantityEl.value) || 1;
      const total = productPrice * quantity;
      totalPriceEl.textContent = new Intl.NumberFormat("ko-KR", {
        style: "currency",
        currency: "KRW",
      }).format(total);
    }

    // Image gallery functionality
    function setupImageGallery() {
      const mainImage = document.getElementById("product-main-image");
      const thumbnails = document.querySelectorAll(".thumbnail-image");

      thumbnails.forEach((thumbnail) => {
        thumbnail.addEventListener("click", () => {
          const imageUrl = thumbnail.style.backgroundImage.slice(5, -2); // Extract URL from style

          if (mainImage) {
            mainImage.style.backgroundImage = `url(${imageUrl})`;
            mainImage.classList.add("has-image");
          }

          // Update active thumbnail
          thumbnails.forEach((t) => t.classList.remove("active"));
          thumbnail.classList.add("active");
        });
      });
    }

    // Event listeners
    function setupEventListeners() {
      // Quantity controls
      if (quantityIncreaseEl) {
        quantityIncreaseEl.addEventListener("click", () => {
          const currentValue = parseInt(quantityEl.value) || 1;

          if (currentValue < maxStock && !stockText.includes("품절")) {
            quantityEl.value = currentValue + 1;
            updateQuantityControls();
          }
        });
      }

      if (quantityDecreaseEl) {
        quantityDecreaseEl.addEventListener("click", () => {
          const currentValue = parseInt(quantityEl.value) || 1;

          if (currentValue > 1) {
            quantityEl.value = currentValue - 1;
            updateQuantityControls();
          }
        });
      }

      if (quantityEl) {
        quantityEl.addEventListener("input", () => {
          const value = parseInt(quantityEl.value) || 1;

          if (value < 1) {
            quantityEl.value = 1;
          } else if (value > maxStock) {
            quantityEl.value = maxStock;
          }

          updateQuantityControls();
        });
      }

      // Buy now button
      if (buyBtn) {
        buyBtn.addEventListener("click", () => {
          const quantity = parseInt(quantityEl?.value) || 1;
          window.location.href = `/products/${productId}/checkout?quantity=${quantity}`;
        });
      }
    }

    function checkProductSeller() {
      // Wait for window.me to be available or fetch user info directly
      function checkUserAndShowSellerControls() {
        if (window.me) {
          if (
            window.me.id === window.__PRODUCT_SELLER_ID__ &&
            window.me.role === "admin"
          ) {
            showSellerControls();
          }
        }
      }

      function showSellerControls() {
        // Hide quantity selector
        const quantitySelector = document.querySelector(".quantity-selector");
        if (quantitySelector) {
          quantitySelector.style.display = "none";
        }

        // Hide buy button
        if (buyBtn) {
          buyBtn.style.display = "none";
        }

        // Hide total price section
        const totalPriceSection = document.querySelector(".total-price");
        if (totalPriceSection) {
          totalPriceSection.style.display = "none";
        }

        // Create and add edit button in the action buttons section
        const actionButtons = document.querySelector(".action-buttons");
        if (actionButtons) {
          const editBtn = document.createElement("button");
          editBtn.className = "btn btn-edit";
          editBtn.innerHTML = `
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
            상품 수정
          `;

          const orderManageBtn = document.createElement("button");
          orderManageBtn.className = "btn btn-order-manage";
          orderManageBtn.innerHTML = `
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>
            </svg>
            주문 내역 관리`;

          // Add click animation
          editBtn.addEventListener("click", (e) => {
            // Add ripple effect
            const ripple = document.createElement("span");
            const rect = editBtn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
              position: absolute;
              width: ${size}px;
              height: ${size}px;
              left: ${x}px;
              top: ${y}px;
              background: rgba(255, 255, 255, 0.3);
              border-radius: 50%;
              transform: scale(0);
              animation: ripple 0.6s linear;
              pointer-events: none;
            `;

            editBtn.appendChild(ripple);

            // Remove ripple after animation
            setTimeout(() => ripple.remove(), 600);

            // Open modal after animation
            setTimeout(() => {
              if (window.ProductModal && window.product) {
                window.ProductModal.show("edit", window.product);
              }
            }, 200);
          });

          // Add click animation
          orderManageBtn.addEventListener("click", (e) => {
            // Add ripple effect
            const ripple = document.createElement("span");
            const rect = orderManageBtn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
              position: absolute;
              width: ${size}px;
              height: ${size}px;
              left: ${x}px;
              top: ${y}px;
              background: rgba(255, 255, 255, 0.3);
              border-radius: 50%;
              transform: scale(0);
              animation: ripple 0.6s linear;
              pointer-events: none;
            `;

            orderManageBtn.appendChild(ripple);

            // Remove ripple after animation
            setTimeout(() => ripple.remove(), 600);

            // Navigate after animation
            setTimeout(() => {
              window.location.href = `/products/${productId}/orders`;
            }, 200);
          });

          // Replace the buy button with edit button
          actionButtons.appendChild(editBtn);
          actionButtons.appendChild(orderManageBtn);

          // Ripple animation is now defined in product_detail.css
        }
      }

      // Try immediately, then retry after a short delay if needed
      checkUserAndShowSellerControls();

      // Wait for user info if not available
      if (!window.me) {
        window.addEventListener("userReady", checkUserAndShowSellerControls, {
          once: true,
        });
      }
    }

    // Initialize
    function init() {
      setupEventListeners();
      setupImageGallery();
      updateQuantityControls();
      checkProductSeller();
    }

    // Function to refresh product detail
    window.refreshProductList = function () {
      window.location.reload();
    };

    // Start the application
    init();
  }
})();
