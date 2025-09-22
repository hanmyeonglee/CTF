(function () {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHome);
  } else {
    initHome();
  }

  function initHome() {
    const grid = document.getElementById("featured-grid");
    if (!grid) return;

    // Pagination state
    let currentPage = 1;
    const itemsPerPage = 8;
    let totalItems = 0;
    let allProductElements = [];

    // Pagination elements
    const paginationContainer = document.getElementById("pagination-container");
    const paginationPages = document.getElementById("pagination-pages");
    const paginationInfo = document.getElementById("pagination-info");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    // Get all product cards from server-rendered HTML
    function getAllProductsFromDOM() {
      return Array.from(grid.querySelectorAll(".product-card"));
    }

    // Initialize pagination
    function initializePagination() {
      allProductElements = getAllProductsFromDOM();
      totalItems = allProductElements.length;

      // Setup buy button event listeners
      setupBuyButtonListeners();

      if (totalItems <= itemsPerPage) {
        // No need for pagination if items fit on one page
        return;
      }

      showCurrentPageItems();
      renderPagination();
      setupPaginationEvents();
      paginationContainer.style.display = "flex";
    }

    // Setup buy button event listeners
    function setupBuyButtonListeners() {
      allProductElements.forEach((card) => {
        const buyBtn = card.querySelector(".add-btn");
        if (buyBtn) {
          buyBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            const productId = buyBtn.getAttribute("data-id");
            if (productId) {
              window.location.href = `/products/${productId}/checkout?quantity=1`;
            }
          });
        }
      });
    }

    // Show items for current page
    function showCurrentPageItems() {
      // Hide all items
      allProductElements.forEach((item) => {
        item.style.display = "none";
      });

      // Show items for current page
      const startIndex = (currentPage - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;

      for (
        let i = startIndex;
        i < endIndex && i < allProductElements.length;
        i++
      ) {
        allProductElements[i].style.display = "flex";
      }
    }

    // Render pagination
    function renderPagination() {
      const totalPages = Math.ceil(totalItems / itemsPerPage);

      // Update navigation buttons
      prevBtn.disabled = currentPage === 1;
      nextBtn.disabled = currentPage === totalPages;

      // Clear existing page numbers
      paginationPages.innerHTML = "";

      // Generate page numbers with ellipsis logic
      const maxVisiblePages = 5;
      let startPage = Math.max(
        1,
        currentPage - Math.floor(maxVisiblePages / 2)
      );
      let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

      // Adjust start page if we're near the end
      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }

      // Add first page and ellipsis if needed
      if (startPage > 1) {
        addPageButton(1);
        if (startPage > 2) {
          addEllipsis();
        }
      }

      // Add visible page numbers
      for (let i = startPage; i <= endPage; i++) {
        addPageButton(i);
      }

      // Add ellipsis and last page if needed
      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          addEllipsis();
        }
        addPageButton(totalPages);
      }

      // Update info text
      const startItem = (currentPage - 1) * itemsPerPage + 1;
      const endItem = Math.min(currentPage * itemsPerPage, totalItems);
      paginationInfo.textContent = `${startItem}-${endItem} / 총 ${totalItems}개 상품`;
    }

    // Add page button
    function addPageButton(pageNum) {
      const button = document.createElement("button");
      button.className = `pagination-page ${
        pageNum === currentPage ? "active" : ""
      }`;
      button.textContent = pageNum;
      button.addEventListener("click", () => goToPage(pageNum));
      paginationPages.appendChild(button);
    }

    // Add ellipsis
    function addEllipsis() {
      const ellipsis = document.createElement("span");
      ellipsis.className = "pagination-ellipsis";
      ellipsis.textContent = "...";
      paginationPages.appendChild(ellipsis);
    }

    // Go to specific page
    function goToPage(pageNum) {
      const totalPages = Math.ceil(totalItems / itemsPerPage);
      if (pageNum < 1 || pageNum > totalPages || pageNum === currentPage)
        return;

      currentPage = pageNum;
      showCurrentPageItems();
      renderPagination();

      // Smooth scroll to top of product grid
      grid.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // Setup pagination event listeners
    function setupPaginationEvents() {
      prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
          goToPage(currentPage - 1);
        }
      });

      nextBtn.addEventListener("click", () => {
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        if (currentPage < totalPages) {
          goToPage(currentPage + 1);
        }
      });
    }

    // Add seller product add button
    function addSellerProductButton() {
      // Wait for window.me to be available or fetch user info directly
      function checkUserAndAddButton() {
        if (window.me) {
          if (window.me.role === "admin") {
            createProductAddButton();
          }
        }
      }

      function createProductAddButton() {
        // Find the card container that wraps the product grid
        const cardContainer = grid.closest(".card");
        if (cardContainer) {
          // Check if button already exists
          if (cardContainer.querySelector(".product-add-btn")) {
            return;
          }

          // Make the card container relatively positioned for absolute positioning
          cardContainer.style.position = "relative";

          const productAddBtn = document.createElement("button");
          productAddBtn.className = "product-add-btn";
          productAddBtn.textContent = "상품 추가";
          productAddBtn.addEventListener("click", () => {
            if (window.ProductModal) {
              window.ProductModal.show("add");
            }
          });

          // Add button to the card container (not the grid)
          cardContainer.appendChild(productAddBtn);
        }
      }

      // Try immediately, then retry after a short delay if needed
      checkUserAndAddButton();

      // Wait for user info if not available
      if (!window.me) {
        window.addEventListener("userReady", checkUserAndAddButton, {
          once: true,
        });
      }
    }

    // Start the application
    initializePagination();
    addSellerProductButton();
  }
})();
