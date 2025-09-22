(function () {
  const productId = window.__PRODUCT_ID__;
  const ordersData = window.__ORDERS_DATA__ || [];

  // DOM elements
  const statusFilter = document.getElementById("status-filter");
  const paymentFilter = document.getElementById("payment-filter");
  const dateFilter = document.getElementById("date-filter");
  const ordersTable = document.getElementById("orders-table");
  const ordersTbody = document.getElementById("orders-tbody");
  const emptyState = document.getElementById("empty-state");
  const exportBtn = document.getElementById("export-btn");
  const refreshBtn = document.getElementById("refresh-btn");

  let filteredOrders = [...ordersData];

  // Initialize page
  function init() {
    setupEventListeners();
    applyFilters();
  }

  // Setup event listeners
  function setupEventListeners() {
    // Filter events
    if (statusFilter) {
      statusFilter.addEventListener("change", applyFilters);
    }
    if (paymentFilter) {
      paymentFilter.addEventListener("change", applyFilters);
    }
    if (dateFilter) {
      dateFilter.addEventListener("change", applyFilters);
    }

    // Action button events
    if (ordersTbody) {
      ordersTbody.addEventListener("click", handleActionClick);
    }

    // Export and refresh
    if (exportBtn) {
      exportBtn.addEventListener("click", exportOrders);
    }
    if (refreshBtn) {
      refreshBtn.addEventListener("click", refreshOrders);
    }
  }

  // Apply filters
  function applyFilters() {
    const statusValue = statusFilter?.value || "";
    const paymentValue = paymentFilter?.value || "";
    const dateValue = dateFilter?.value || "";

    filteredOrders = ordersData.filter((order) => {
      // Status filter
      if (statusValue && order.status !== statusValue) {
        return false;
      }

      // Payment filter
      if (paymentValue && order.paymentMethod !== paymentValue) {
        return false;
      }

      // Date filter
      if (dateValue) {
        const orderDate = new Date(order.createdAt);
        const now = new Date();
        const diffTime = now - orderDate;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        switch (dateValue) {
          case "today":
            if (diffDays > 1) return false;
            break;
          case "week":
            if (diffDays > 7) return false;
            break;
          case "month":
            if (diffDays > 30) return false;
            break;
        }
      }

      return true;
    });

    updateTable();
    updateStats();
  }

  // Update table display
  function updateTable() {
    if (!ordersTbody || !ordersTable || !emptyState) return;

    if (filteredOrders.length === 0) {
      ordersTable.style.display = "none";
      emptyState.style.display = "block";
      return;
    }

    ordersTable.style.display = "table";
    emptyState.style.display = "none";

    // Show/hide rows based on filter
    const allRows = ordersTbody.querySelectorAll(".order-row");
    allRows.forEach((row) => {
      const orderId = row.dataset.orderId;
      const shouldShow = filteredOrders.some((order) => order.id === orderId);
      row.style.display = shouldShow ? "" : "none";
    });
  }

  // Update statistics
  function updateStats() {
    const totalOrdersEl = document.getElementById("total-orders");
    const pendingOrdersEl = document.getElementById("pending-orders");
    const completedOrdersEl = document.getElementById("completed-orders");

    if (totalOrdersEl) {
      totalOrdersEl.textContent = filteredOrders.length;
    }
    if (pendingOrdersEl) {
      pendingOrdersEl.textContent = filteredOrders.filter(
        (o) => o.status === "PENDING"
      ).length;
    }
    if (completedOrdersEl) {
      completedOrdersEl.textContent = filteredOrders.filter(
        (o) => o.status === "PAID"
      ).length;
    }
  }

  // Handle action button clicks
  function handleActionClick(e) {
    const target = e.target;
    if (!target.classList.contains("btn-detail")) return;

    const orderId = target.dataset.orderId;
    if (!orderId) return;

    // Navigate to order detail
    window.location.href = `/products/${productId}/orders/${orderId}`;
  }

  // Export orders to CSV
  function exportOrders() {
    const csvContent = [
      [
        "주문번호",
        "구매자",
        "수량",
        "금액",
        "결제방식",
        "상태",
        "주문일시",
      ].join(","),
      ...filteredOrders.map((order) =>
        [
          order.id,
          order.buyer.name,
          order.quantity,
          order.amount,
          order.paymentMethod,
          order.status,
          order.createdAt,
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `orders_${productId}_${new Date().toISOString().split("T")[0]}.csv`
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // Refresh orders
  function refreshOrders() {
    window.location.reload();
  }

  // Start the application
  init();
})();
