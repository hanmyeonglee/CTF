(function () {
  // DOM elements
  const notificationBtn = document.getElementById("notification-btn");
  const notificationDropdown = document.getElementById("notification-dropdown");
  const notificationBadge = document.getElementById("notification-badge");
  const notificationList = document.getElementById("notification-list");
  const markAllReadBtn = document.getElementById("mark-all-read");

  let notifications = [];
  let isDropdownOpen = false;
  let isMarkingAllRead = false;

  // Initialize notifications
  function init() {
    if (!notificationBtn) return;

    setupEventListeners();

    // Setup notification polling when user info is available
    if (window.me) {
      loadNotifications();
      // Poll for new notifications every 30 seconds
      setInterval(loadNotifications, 30000);
    } else {
      // Wait for user info and then setup polling
      window.addEventListener(
        "userReady",
        () => {
          loadNotifications();
          setInterval(loadNotifications, 30000);
        },
        { once: true }
      );
    }
  }

  // Setup event listeners
  function setupEventListeners() {
    if (notificationBtn) {
      notificationBtn.addEventListener("click", toggleDropdown);
    }

    if (markAllReadBtn) {
      markAllReadBtn.addEventListener("click", markAllAsRead);
    }

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (
        !notificationBtn?.contains(e.target) &&
        !notificationDropdown?.contains(e.target)
      ) {
        closeDropdown();
      }
    });

    // Handle notification item clicks
    if (notificationList) {
      notificationList.addEventListener("click", handleNotificationClick);
    }
  }

  // Toggle dropdown visibility
  function toggleDropdown() {
    if (isDropdownOpen) {
      closeDropdown();
    } else {
      openDropdown();
    }
  }

  // Open dropdown
  function openDropdown() {
    if (!notificationDropdown) return;

    isDropdownOpen = true;
    notificationDropdown.classList.add("show");
    loadNotifications(); // Refresh notifications when opening
  }

  // Close dropdown
  function closeDropdown() {
    if (!notificationDropdown) return;

    isDropdownOpen = false;
    notificationDropdown.classList.remove("show");
  }

  // Load notifications
  async function loadNotifications() {
    try {
      const response = await window.api.get("notifications");
      if (response && response.data) {
        notifications = response.data;
        updateNotificationBadge();
        renderNotifications();
      }
    } catch (error) {
      console.error("Failed to load notifications:", error);
      renderErrorState();
    }
  }

  // Update notification badge
  function updateNotificationBadge() {
    if (!notificationBadge) return;

    const unreadCount = notifications.filter((n) => !n.read).length;

    if (unreadCount > 0) {
      notificationBadge.textContent =
        unreadCount > 99 ? "99+" : unreadCount.toString();
      notificationBadge.style.display = "flex";
    } else {
      notificationBadge.style.display = "none";
    }
  }

  // Render notifications
  function renderNotifications() {
    if (!notificationList) return;

    if (notifications.length === 0) {
      notificationList.innerHTML = `
        <div class="notification-empty">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" style="color: var(--muted); margin-bottom: 8px;">
            <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
          </svg>
          <p>새로운 알림이 없습니다</p>
        </div>
      `;
      return;
    }

    const notificationItems = notifications
      .map(
        (notification) => `
      <div class="notification-item ${
        !notification.read ? "unread" : "read"
      }" data-id="${notification.id}">
        <div class="notification-title">${escapeHtml(notification.title)}</div>
        <div class="notification-message">${escapeHtml(
          notification.message
        )}</div>
        <div class="notification-time">${formatTime(
          notification.createdAt
        )}</div>
        ${
          notification.read
            ? '<div class="notification-read-indicator">읽음</div>'
            : ""
        }
      </div>
    `
      )
      .join("");

    notificationList.innerHTML = notificationItems;
  }

  // Render error state
  function renderErrorState() {
    if (!notificationList) return;

    const errorDiv = document.createElement("div");
    errorDiv.className = "notification-empty";

    const errorText = document.createElement("p");
    errorText.textContent = "알림을 불러오는데 실패했습니다";

    const retryBtn = document.createElement("button");
    retryBtn.textContent = "다시 시도";
    retryBtn.style.cssText =
      "margin-top: 8px; padding: 4px 8px; background: var(--link); color: white; border: none; border-radius: 4px; cursor: pointer;";
    retryBtn.addEventListener("click", () =>
      window.notifications.loadNotifications()
    );

    errorDiv.appendChild(errorText);
    errorDiv.appendChild(retryBtn);
    notificationList.innerHTML = "";
    notificationList.appendChild(errorDiv);
  }

  // Handle notification item click
  async function handleNotificationClick(e) {
    const notificationItem = e.target.closest(".notification-item");
    if (!notificationItem) return;

    const notificationId = notificationItem.dataset.id;
    const notification = notifications.find((n) => n.id === notificationId);

    if (!notification) return;

    // Mark as read if unread
    if (!notification.read) {
      notification.read = true;
      notificationItem.classList.remove("unread");
      updateNotificationBadge();

      try {
        await window.api.patch(`notifications/${notificationId}`, {
          body: { read: true },
        });
      } catch (error) {
        console.error("Failed to mark notification as read:", error);
      }
    }

    // Handle notification type-specific actions
    handleNotificationAction(notification);
  }

  // Handle notification-specific actions
  function handleNotificationAction(notification) {
    switch (notification.type) {
      case "order.updated":
        // Extract order ID from message or use a different approach
        const orderMatch = notification.message.match(/ord_\w+/);
        if (orderMatch) {
          const orderId = orderMatch[0];
          // Navigate to order detail - you might need to adjust this URL
          window.location.href = `/orders/${orderId}`;
        }
        break;
      default:
        // Default action - just close dropdown
        closeDropdown();
        break;
    }
  }

  // Mark all notifications as read
  async function markAllAsRead() {
    if (isMarkingAllRead) return;

    const unreadNotifications = notifications.filter((n) => !n.read);

    if (unreadNotifications.length === 0) return;

    try {
      isMarkingAllRead = true;
      const promises = unreadNotifications.map((notification) =>
        window.api.patch(`notifications/${notification.id}`, {
          body: { read: true },
        })
      );
      await Promise.all(promises);

      renderNotifications();
      updateNotificationBadge();
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error);
      alert("알림을 읽음 처리하는데 실패했습니다.");
    } finally {
      isMarkingAllRead = false;
    }
  }

  // Utility functions
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "방금 전";
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;

    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
    });
  }

  // Export functions for global access
  window.notifications = {
    init,
    loadNotifications,
    toggleDropdown,
    closeDropdown,
  };
  // Auto-initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      setTimeout(init, 100); // Small delay to ensure site.js has run
    });
  } else {
    setTimeout(init, 100);
  }
})();
