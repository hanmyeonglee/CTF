(function () {
  function initProfile() {
    // Wait for API module to be available
    if (!window.api) {
      window.addEventListener("apiReady", initProfile, { once: true });
      return;
    }

    // DOM elements
    const profileAvatar = document.getElementById("profile-avatar");
    const profileName = document.getElementById("profile-name");
    const profileEmail = document.getElementById("profile-email");
    const profileRole = document.getElementById("profile-role");
    const profileBalance = document.getElementById("profile-balance");

    // Detail elements
    const detailEmail = document.getElementById("detail-email");
    const detailName = document.getElementById("detail-name");
    const detailRole = document.getElementById("detail-role");
    const detailCreated = document.getElementById("detail-created");

    // Address elements
    const addressDetails = document.getElementById("address-details");

    // Modal elements
    const editProfileModal = document.getElementById("edit-profile-modal");
    const editProfileBtn = document.getElementById("edit-profile-btn");
    const editModalClose = document.getElementById("edit-modal-close");
    const cancelEditBtn = document.getElementById("cancel-edit");
    const saveEditBtn = document.getElementById("save-edit");

    // Send referral code elements
    const sendReferralCodeBtn = document.getElementById(
      "send-referral-code-btn"
    );
    const sendReferralModal = document.getElementById("send-referral-modal");
    const sendReferralModalClose = document.getElementById(
      "send-referral-modal-close"
    );
    const sendReferralModalCancel = document.getElementById(
      "send-referral-modal-cancel"
    );
    const sendReferralForm = document.getElementById("send-referral-form");
    const targetUserIdInput = document.getElementById("target-user-id");
    const sendReferralSubmit = document.getElementById("send-referral-submit");

    // Register referral code elements
    const registerReferralCodeBtn = document.getElementById(
      "register-referral-code-btn"
    );
    const registerReferralModal = document.getElementById(
      "register-referral-modal"
    );
    const registerReferralModalClose = document.getElementById(
      "register-referral-modal-close"
    );
    const registerReferralModalCancel = document.getElementById(
      "register-referral-modal-cancel"
    );
    const registerReferralForm = document.getElementById(
      "register-referral-form"
    );
    const referralCodeInput = document.getElementById("referral-code-input");
    const registerReferralSubmit = document.getElementById(
      "register-referral-submit"
    );

    // Form elements
    const editNameInput = document.getElementById("edit-name");
    const editProfileImageInput = document.getElementById("edit-profile-image");
    const selectImageBtn = document.getElementById("select-image-btn");
    const currentImagePreview = document.getElementById(
      "current-image-preview"
    );
    const editAddressFullInput = document.getElementById("edit-address-full");
    const editAddressPostalInput = document.getElementById(
      "edit-address-postal"
    );
    const editAddressCountrySelect = document.getElementById(
      "edit-address-country"
    );

    // State
    let currentProfile = null;
    let isLoading = false;
    let isSavingProfile = false;
    let isSendingReferral = false;
    let isRegisteringReferral = false;

    function readProfileFromDOM() {
      const name = profileName?.textContent?.trim() || "";
      const email = profileEmail?.textContent?.trim() || "";
      const roleEl = profileRole;
      const role = roleEl
        ? ["user", "admin"].find((r) => roleEl.classList.contains(r)) ||
          roleEl.textContent?.trim() ||
          "user"
        : "user";

      let amount = 0;
      let currency = "KRW";
      if (profileBalance && profileBalance.textContent) {
        const digits = profileBalance.textContent.replace(/[^0-9]/g, "");
        amount = digits ? parseInt(digits, 10) : 0;
      }

      let profileImageUrl = "";
      if (profileAvatar) {
        const bg = window.getComputedStyle(profileAvatar).backgroundImage;
        const match =
          bg && bg.startsWith("url(")
            ? bg.match(/url\(["']?(.*?)["']?\)/)
            : null;
        profileImageUrl = (match && match[1]) || "";
      }

      if (!profileImageUrl || profileImageUrl === "NONE") {
        profileImageUrl = "/static/assets/default-profile.png";
      }

      const createdAt = detailCreated?.textContent?.trim() || "";

      let addrAddress = "";
      let addrPostal = "";
      let addrCountryText = "";
      const addrRoot = addressDetails;
      if (addrRoot) {
        const rows = addrRoot.querySelectorAll(".address-row");
        rows.forEach((row) => {
          const label = row
            .querySelector(".address-label")
            ?.textContent?.trim();
          const value =
            row.querySelector(".address-value")?.textContent?.trim() || "";
          if (label === "주소") addrAddress = value;
          if (label === "우편번호") addrPostal = value;
          if (label === "국가") addrCountryText = value;
        });
      }

      const address = {
        address: addrAddress,
        postalCode: addrPostal,
        country: getCountryCode(addrCountryText) || "KR",
      };

      return {
        id: "",
        name,
        email,
        role,
        amount,
        currency,
        profileImageUrl,
        createdAt,
        address,
      };
    }

    function loadProfileFromTemplate() {
      try {
        setLoading(true);
        currentProfile = readProfileFromDOM();
      } finally {
        setLoading(false);
      }
    }

    async function saveProfile() {
      if (isLoading || isSavingProfile) return;

      try {
        isSavingProfile = true;
        setLoading(true);

        const profilePayload = {
          name: editNameInput?.value || "",
          profileImageUrl: currentProfile?.profileImageUrl || "",
          dateOfBirth: "NONE",
          phone: "NONE",
        };

        const addressPayload = {
          address: editAddressFullInput?.value || "",
          postalCode: editAddressPostalInput?.value || "",
          country: editAddressCountrySelect?.value || "KR",
        };

        await window.api.put("me/profile", { body: profilePayload });
        await window.api.post("address", { body: addressPayload });

        currentProfile = {
          ...currentProfile,
          name: profilePayload.name,
          profileImageUrl: profilePayload.profileImageUrl,
          address: {
            ...(currentProfile.address || {}),
            ...addressPayload,
          },
        };

        updateProfileDisplay(currentProfile);
        closeEditModal();
        showSuccess("프로필이 성공적으로 업데이트되었습니다.");
      } catch (error) {
        console.error("Failed to save profile:", error);
        showError("프로필 저장에 실패했습니다.");
      } finally {
        setLoading(false);
      }
    }

    async function uploadImage(file) {
      const formData = new FormData();
      formData.append("image", file, "profile.jpg");

      try {
        const response = await fetch("/uploads", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.status}`);
        }

        const result = await response.json();
        return result.url || result.path;
      } catch (error) {
        console.error("Image upload error:", error);
        throw new Error("이미지 업로드에 실패했습니다.");
      }
    }

    // UI update functions
    function updateProfileDisplay(profile) {
      // Header section
      if (profileName) profileName.textContent = profile.name || "사용자";
      if (profileEmail) profileEmail.textContent = profile.email || "";
      if (profileRole) {
        profileRole.textContent = getRoleDisplayName(profile.role);
        profileRole.className = `profile-role ${profile.role}`;
      }
      if (profileBalance) {
        profileBalance.textContent = formatCurrency(
          profile.amount,
          profile.currency
        );
      }

      // Profile avatar
      if (profileAvatar && profile.profileImageUrl) {
        profileAvatar.style.backgroundImage = `url(${profile.profileImageUrl})`;
        profileAvatar.classList.add("has-image");
      }

      // Detail section
      if (detailEmail) detailEmail.textContent = profile.email || "";
      if (detailName) detailName.textContent = profile.name || "";
      if (detailRole) detailRole.textContent = getRoleDisplayName(profile.role);
      if (detailCreated)
        detailCreated.textContent = formatDate(profile.createdAt);

      // Address section
      updateAddressDisplay(profile.address);
    }

    function updateAddressDisplay(address) {
      if (!addressDetails) return;

      if (!address || Object.keys(address).length === 0) {
        addressDetails.innerHTML =
          '<div class="address-loading">등록된 주소가 없습니다.</div>';
        return;
      }

      const countryName = getCountryName(address.country);

      addressDetails.innerHTML = `
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

    // Image upload handling
    async function handleImageSelect(event) {
      const file = event.target.files[0];
      if (!file) return;

      // Validate file type
      if (!file.type.startsWith("image/")) {
        showError("이미지 파일만 업로드 가능합니다.");
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        showError("파일 크기는 10MB 이하여야 합니다.");
        return;
      }

      try {
        setLoading(true);
        const url = await uploadImage(file);

        if (url) {
          currentProfile.profileImageUrl = url;

          if (currentImagePreview) {
            currentImagePreview.style.backgroundImage = `url(${url})`;
            currentImagePreview.classList.add("has-image");
          }
        }
      } catch (error) {
        console.error("Failed to upload image:", error);
        showError("이미지 업로드에 실패했습니다.");
      } finally {
        setLoading(false);
      }
    }

    // Modal functions
    function openEditModal() {
      if (!currentProfile) return;

      // Populate form with current data
      if (editNameInput) editNameInput.value = currentProfile.name || "";

      // Update current image preview
      if (currentImagePreview && currentProfile.profileImageUrl) {
        currentImagePreview.style.backgroundImage = `url(${currentProfile.profileImageUrl})`;
        currentImagePreview.classList.add("has-image");
      } else if (currentImagePreview) {
        currentImagePreview.style.backgroundImage = "";
        currentImagePreview.classList.remove("has-image");
      }

      if (currentProfile.address) {
        if (editAddressFullInput)
          editAddressFullInput.value =
            currentProfile.address.address != "등록되지 않음"
              ? currentProfile.address.address
              : "";
        if (editAddressPostalInput)
          editAddressPostalInput.value =
            currentProfile.address.postalCode != "등록되지 않음"
              ? currentProfile.address.postalCode
              : "";
        if (editAddressCountrySelect)
          editAddressCountrySelect.value =
            currentProfile.address.country || "KR";
      }

      editProfileModal.classList.add("active");
      document.body.style.overflow = "hidden";
    }

    function closeEditModal() {
      editProfileModal.classList.remove("active");
      document.body.style.overflow = "";
    }

    // Utility functions
    function getRoleDisplayName(role) {
      const roleNames = {
        user: "사용자",
        admin: "관리자",
      };
      return roleNames[role] || role;
    }

    function formatCurrency(amount, currency = "KRW") {
      if (amount == null) return "₩0";

      return new Intl.NumberFormat("ko-KR", {
        style: "currency",
        currency: currency,
      }).format(amount);
    }

    function formatDate(dateString) {
      if (!dateString) return "";

      try {
        const date = new Date(dateString);
        return date.toLocaleDateString("ko-KR");
      } catch {
        return "";
      }
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

    function getCountryCode(text) {
      if (!text) return "";
      const normalized = String(text).trim();
      const map = {
        대한민국: "KR",
        미국: "US",
        일본: "JP",
        중국: "CN",
        KR: "KR",
        US: "US",
        JP: "JP",
        CN: "CN",
      };
      return map[normalized] || "";
    }

    function setLoading(loading) {
      isLoading = loading;
      document.body.classList.toggle("loading", loading);
    }

    function showError(message) {
      alert(message);
    }

    function showSuccess(message) {
      alert(message);
    }

    // Event listeners
    function setupEventListeners() {
      // Edit profile modal
      editProfileBtn?.addEventListener("click", openEditModal);
      editModalClose?.addEventListener("click", closeEditModal);
      cancelEditBtn?.addEventListener("click", closeEditModal);
      saveEditBtn?.addEventListener("click", saveProfile);

      // Image upload
      if (selectImageBtn && editProfileImageInput) {
        selectImageBtn.addEventListener("click", () => {
          editProfileImageInput.click();
        });
        editProfileImageInput.addEventListener("change", handleImageSelect);
      }

      // Close modal when clicking outside
      editProfileModal?.addEventListener("click", (e) => {
        if (e.target === editProfileModal) {
          closeEditModal();
        }
      });

      // Keyboard shortcuts
      document.addEventListener("keydown", (e) => {
        if (
          e.key === "Escape" &&
          editProfileModal?.classList.contains("active")
        ) {
          closeEditModal();
        }
      });
    }

    // Send referral code functionality
    function showSendReferralModal() {
      if (sendReferralModal) {
        sendReferralModal.classList.add("show");
        document.body.style.overflow = "hidden";

        // Focus on input
        setTimeout(() => targetUserIdInput?.focus(), 100);
      }
    }

    function closeSendReferralModal() {
      if (sendReferralModal) {
        sendReferralModal.classList.remove("show");
        document.body.style.overflow = "";

        // Reset form
        if (sendReferralForm) {
          sendReferralForm.reset();
        }
      }
    }

    async function sendReferralCode(formData) {
      if (isSendingReferral) return;

      const targetUserId = formData.get("targetUserId");

      if (!targetUserId || targetUserId.trim().length === 0) {
        alert("사용자 ID를 입력해주세요.");
        return;
      }

      try {
        isSendingReferral = true;
        const referralResponse = await window.api.get("me/referral-code/send", {
          query: {
            uid: targetUserId,
          },
        });

        if (!referralResponse) {
          alert("추천인 코드를 불러올 수 없습니다.");
          return;
        }

        if (referralResponse) {
          closeSendReferralModal();
          alert(`${targetUserId} 사용자에게 추천인 코드가 전송되었습니다!`);
        }
      } catch (error) {
        console.error("Failed to send referral code:", error);

        if (error.status === 404) {
          alert("존재하지 않는 사용자 ID입니다.");
        } else if (error.status === 409) {
          alert("이미 추천인 코드를 사용한 사용자입니다.");
        } else {
          alert("추천인 코드 전송에 실패했습니다. 다시 시도해주세요.");
        }
      } finally {
        isSendingReferral = false;
      }
    }

    // Setup send referral code event listeners
    function setupSendReferralCodeListener() {
      if (sendReferralCodeBtn) {
        sendReferralCodeBtn.addEventListener("click", showSendReferralModal);
      }

      if (sendReferralModalClose) {
        sendReferralModalClose.addEventListener(
          "click",
          closeSendReferralModal
        );
      }

      if (sendReferralModalCancel) {
        sendReferralModalCancel.addEventListener(
          "click",
          closeSendReferralModal
        );
      }

      if (sendReferralForm) {
        sendReferralForm.addEventListener("submit", async (e) => {
          e.preventDefault();

          const submitButton = sendReferralSubmit;
          const originalText = submitButton?.textContent;

          try {
            if (submitButton) {
              submitButton.disabled = true;
              submitButton.textContent = "전송 중...";
            }

            const formData = new FormData(sendReferralForm);
            await sendReferralCode(formData);
          } catch (error) {
            console.error("Form submission error:", error);
          } finally {
            if (submitButton && originalText) {
              submitButton.disabled = false;
              submitButton.textContent = originalText;
            }
          }
        });
      }

      // Close modal when clicking outside
      if (sendReferralModal) {
        sendReferralModal.addEventListener("click", (e) => {
          if (e.target === sendReferralModal) {
            closeSendReferralModal();
          }
        });
      }

      // Close modal with Escape key
      document.addEventListener("keydown", (e) => {
        if (
          e.key === "Escape" &&
          sendReferralModal?.classList.contains("show")
        ) {
          closeSendReferralModal();
        }
        if (
          e.key === "Escape" &&
          registerReferralModal?.classList.contains("show")
        ) {
          closeRegisterReferralModal();
        }
      });
    }

    // Register referral code functionality
    function showRegisterReferralModal() {
      if (registerReferralModal) {
        registerReferralModal.classList.add("show");
        document.body.style.overflow = "hidden";

        // Focus on input
        setTimeout(() => referralCodeInput?.focus(), 100);
      }
    }

    function closeRegisterReferralModal() {
      if (registerReferralModal) {
        registerReferralModal.classList.remove("show");
        document.body.style.overflow = "";

        // Reset form
        if (registerReferralForm) {
          registerReferralForm.reset();
        }
      }
    }

    async function registerReferralCode(formData) {
      if (isRegisteringReferral) return;

      const referralCode = formData.get("referralCode");

      if (!referralCode || referralCode.trim().length === 0) {
        alert("추천인 코드를 입력해주세요.");
        return;
      }

      try {
        isRegisteringReferral = true;
        const response = await window.api.post("referrals/redeem", {
          body: { code: referralCode },
        });

        if (response.success) {
          closeRegisterReferralModal();
          alert(
            `${response.message}\n💰 ${response.reward}원이 지급되었습니다!`
          );
          window.location.reload();
        }
      } catch (error) {
        console.error("Failed to register referral code:", error);

        if (error.status === 404) {
          alert("존재하지 않는 추천인 코드입니다.");
        } else if (error.status === 409) {
          alert("이미 사용된 추천인 코드이거나 중복 등록입니다.");
        } else {
          alert("추천인 코드 등록에 실패했습니다. 다시 시도해주세요.");
        }
      } finally {
        isRegisteringReferral = false;
      }
    }

    // Setup register referral code event listeners
    function setupRegisterReferralCodeListener() {
      if (registerReferralCodeBtn) {
        registerReferralCodeBtn.addEventListener(
          "click",
          showRegisterReferralModal
        );
      }

      if (registerReferralModalClose) {
        registerReferralModalClose.addEventListener(
          "click",
          closeRegisterReferralModal
        );
      }

      if (registerReferralModalCancel) {
        registerReferralModalCancel.addEventListener(
          "click",
          closeRegisterReferralModal
        );
      }

      if (registerReferralForm) {
        registerReferralForm.addEventListener("submit", async (e) => {
          e.preventDefault();

          const submitButton = registerReferralSubmit;
          const originalText = submitButton?.textContent;

          try {
            if (submitButton) {
              submitButton.disabled = true;
              submitButton.textContent = "등록 중...";
            }

            const formData = new FormData(registerReferralForm);
            await registerReferralCode(formData);
          } catch (error) {
            console.error("Form submission error:", error);
          } finally {
            if (submitButton && originalText) {
              submitButton.disabled = false;
              submitButton.textContent = originalText;
            }
          }
        });
      }

      // Close modal when clicking outside
      if (registerReferralModal) {
        registerReferralModal.addEventListener("click", (e) => {
          if (e.target === registerReferralModal) {
            closeRegisterReferralModal();
          }
        });
      }

      // Auto-format referral code input
      if (referralCodeInput) {
        referralCodeInput.addEventListener("input", (e) => {
          let value = e.target.value.toUpperCase().replace(/[^A-Z0-9-]/g, "");
          e.target.value = value;
        });
      }
    }

    // Initialize the page
    function init() {
      loadProfileFromTemplate();
      setupEventListeners();
      setupSendReferralCodeListener();
      setupRegisterReferralCodeListener();
    }

    // Start the application
    init();
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProfile);
  } else {
    initProfile();
  }
})();
