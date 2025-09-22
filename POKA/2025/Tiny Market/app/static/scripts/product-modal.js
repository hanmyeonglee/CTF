(function () {
  function initProductModal() {
    // Wait for API module to be available
    if (!window.api) {
      window.addEventListener("apiReady", initProductModal, { once: true });
      return;
    }

    // Modal elements
    const modal = document.getElementById("product-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalClose = document.getElementById("modal-close");
    const modalCancel = document.getElementById("modal-cancel");
    const productForm = document.getElementById("product-form");
    const modalSubmit = document.getElementById("modal-submit");

    // Form elements
    const productName = document.getElementById("modal-product-name");
    const productPrice = document.getElementById("modal-product-price");
    const productStock = document.getElementById("modal-product-stock");
    const productDescription = document.getElementById(
      "modal-product-description"
    );
    const productHidden = document.getElementById("modal-product-hidden");
    const productImages = document.getElementById("modal-product-images");
    const fileUploadArea = document.getElementById("modal-file-upload-area");
    const imagePreviews = document.getElementById("modal-image-previews");
    const fileUploadContent = fileUploadArea?.querySelector(
      ".file-upload-content"
    );

    // Category elements
    const categorySelect = document.getElementById("modal-category-select");
    const addCategoryBtn = document.getElementById("modal-add-category-btn");
    const selectedCategoriesEl = document.getElementById(
      "modal-selected-categories"
    );

    let currentMode = "add"; // "add" or "edit"
    let currentProductId = null;
    let selectedFiles = []; // Array to store multiple files
    let existingImages = []; // Array to store existing image URLs for edit mode
    let selectedCategories = []; // Array to store selected categories
    let isSubmittingProduct = false;

    // Modal management
    const ProductModal = {
      show: function (mode = "add", productData = null) {
        currentMode = mode;
        currentProductId = productData?.id || null;

        // Update modal title and submit button
        modalTitle.textContent = mode === "add" ? "상품 추가" : "상품 수정";
        modalSubmit.textContent = mode === "add" ? "추가" : "수정";

        // Reset form
        this.resetForm();

        // Fill form with existing data for edit mode
        if (mode === "edit" && productData) {
          this.fillForm(productData);
        }

        // setup hidden checkbox
        this.setupHiddenCheckbox(mode);

        // Show modal
        modal.classList.add("show");
        document.body.style.overflow = "hidden";

        // Focus first input
        setTimeout(() => productName?.focus(), 100);
      },

      hide: function () {
        modal.classList.remove("show");
        document.body.style.overflow = "";
        this.resetForm();
        currentMode = "add";
        currentProductId = null;
      },

      resetForm: function () {
        productForm?.reset();
        selectedFiles = [];
        existingImages = [];
        selectedCategories = [];
        this.updateImagePreviews();
        this.updateCategoriesDisplay();
        if (fileUploadContent) {
          fileUploadContent.style.display = "block";
        }

        // setup hidden checkbox
        if (productHidden) {
          const hiddenContainer = productHidden.closest(".form-group");
          if (hiddenContainer) {
            productHidden.disabled = false;
            hiddenContainer.style.opacity = "1";

            // remove disabled hint
            const disabledHint =
              hiddenContainer.querySelector(".disabled-hint");
            if (disabledHint) {
              disabledHint.remove();
            }
          }
        }
      },

      fillForm: function (productData) {
        if (productName) productName.value = productData.name || "";
        if (productPrice) productPrice.value = productData.price || "";
        if (productStock) productStock.value = productData.stock || "";
        if (productDescription)
          productDescription.value = productData.description || "";
        if (productHidden) productHidden.checked = productData.hidden || false;

        // Handle existing images
        existingImages = [];
        if (productData.imageUrl) {
          // Single image (legacy support)
          existingImages.push(productData.imageUrl);
        } else if (
          productData.imageUrls &&
          Array.isArray(productData.imageUrls)
        ) {
          // Multiple images
          existingImages = [...productData.imageUrls];
        } else if (productData.images && Array.isArray(productData.images)) {
          // Multiple images (alternative structure)
          existingImages = [...productData.images];
        }

        // Handle existing categories
        selectedCategories = [];
        if (productData.categories && Array.isArray(productData.categories)) {
          selectedCategories = [...productData.categories];
        }

        this.updateImagePreviews();
        this.updateCategoriesDisplay();
      },

      setupHiddenCheckbox: function (mode) {
        if (!productHidden) return;

        const hiddenContainer = productHidden.closest(".form-group");
        if (!hiddenContainer) return;

        if (mode === "add") {
          // add mode: enable checkbox
          productHidden.disabled = false;
          hiddenContainer.style.display = "block";
          hiddenContainer.style.opacity = "1";

          // remove disabled hint
          const disabledHint = hiddenContainer.querySelector(".disabled-hint");
          if (disabledHint) {
            disabledHint.remove();
          }
        } else if (mode === "edit") {
          // edit mode: disable checkbox
          productHidden.disabled = true;
          hiddenContainer.style.opacity = "0.5";

          // add disabled hint
          let disabledHint = hiddenContainer.querySelector(".disabled-hint");
          if (!disabledHint) {
            disabledHint = document.createElement("div");
            disabledHint.className = "disabled-hint";
            disabledHint.style.cssText =
              "font-size: 12px; color: var(--muted); margin-top: 4px;";
            disabledHint.textContent =
              "상품 수정 시에는 숨기기 설정을 변경할 수 없습니다";
            hiddenContainer.appendChild(disabledHint);
          }
        }
      },

      updateImagePreviews: function () {
        if (!imagePreviews) return;

        imagePreviews.innerHTML = "";
        const allImages = [...existingImages, ...selectedFiles];

        if (allImages.length === 0) {
          if (fileUploadContent) {
            fileUploadContent.style.display = "block";
          }
          return;
        }

        if (fileUploadContent) {
          fileUploadContent.style.display = "none";
        }

        allImages.forEach((item, index) => {
          const previewItem = document.createElement("div");
          previewItem.className = "image-preview-item";
          if (index === 0) previewItem.classList.add("main");

          const img = document.createElement("img");

          if (typeof item === "string") {
            // Existing image URL
            img.src = item;
            img.alt = "상품 이미지";
          } else {
            // New file
            const reader = new FileReader();
            reader.onload = (e) => {
              img.src = e.target.result;
            };
            reader.readAsDataURL(item);
            img.alt = "새 이미지";
          }

          const removeBtn = document.createElement("button");
          removeBtn.className = "image-preview-remove";
          removeBtn.innerHTML = "×";
          removeBtn.type = "button";
          removeBtn.addEventListener("click", () => {
            if (typeof item === "string") {
              // Remove from existing images
              existingImages = existingImages.filter((url) => url !== item);
            } else {
              // Remove from selected files
              selectedFiles = selectedFiles.filter((file) => file !== item);
            }
            this.updateImagePreviews();
          });

          if (index === 0) {
            const mainLabel = document.createElement("div");
            mainLabel.className = "image-preview-main";
            mainLabel.textContent = "대표";
            previewItem.appendChild(mainLabel);
          }

          previewItem.appendChild(img);
          previewItem.appendChild(removeBtn);
          imagePreviews.appendChild(previewItem);
        });
      },

      updateCategoriesDisplay: function () {
        if (!selectedCategoriesEl) return;

        selectedCategoriesEl.innerHTML = "";

        selectedCategories.forEach((category) => {
          const categoryTag = document.createElement("div");
          categoryTag.className = "category-tag";

          const categoryText = document.createElement("span");
          categoryText.textContent = category;

          const removeBtn = document.createElement("button");
          removeBtn.className = "category-tag-remove";
          removeBtn.innerHTML = "×";
          removeBtn.type = "button";
          removeBtn.addEventListener("click", () => {
            selectedCategories = selectedCategories.filter(
              (c) => c !== category
            );
            this.updateCategoriesDisplay();
          });

          categoryTag.appendChild(categoryText);
          categoryTag.appendChild(removeBtn);
          selectedCategoriesEl.appendChild(categoryTag);
        });
      },

      submit: async function (formData) {
        if (isSubmittingProduct) return;

        try {
          isSubmittingProduct = true;
          let result;
          const submitData = {
            name: formData.get("name"),
            price: parseInt(formData.get("price")),
            stock: parseInt(formData.get("stock")),
            currency: "KRW",
            description: formData.get("description"),
            categories: selectedCategories,
            imageUrl: [],
            hidden: productHidden ? productHidden.checked : false,
          };

          // Handle multiple image uploads
          const imageUrl = [...existingImages]; // Keep existing images

          if (selectedFiles.length > 0) {
            for (const file of selectedFiles) {
              const imageFormData = new FormData();
              imageFormData.append("image", file);

              const imageResponse = await fetch("/uploads", {
                method: "POST",
                body: imageFormData,
              });

              if (imageResponse.ok) {
                const imageResult = await imageResponse.json();
                if (imageResult && imageResult.url) {
                  imageUrl.push(imageResult.url);
                }
              } else {
                console.error(
                  "Image upload failed:",
                  await imageResponse.text()
                );
              }
            }
          }

          // Set images in submit data
          if (imageUrl.length > 0) {
            submitData.imageUrl = imageUrl;
          }

          if (currentMode === "add") {
            result = await window.api.post("products", {
              body: submitData,
            });
          } else {
            result = await window.api.patch(`products/${currentProductId}`, {
              body: submitData,
            });
          }

          // Success - hide modal and refresh product list
          this.hide();

          // Trigger product list refresh if function exists
          if (window.refreshProductList) {
            window.refreshProductList();
          } else {
            // Fallback - reload page
            window.location.reload();
          }

          return result;
        } catch (error) {
          console.error("Product save error:", error);
          throw error;
        } finally {
          isSubmittingProduct = false;
        }
      },
    };

    // Event listeners
    if (modalClose) {
      modalClose.addEventListener("click", () => ProductModal.hide());
    }

    if (modalCancel) {
      modalCancel.addEventListener("click", () => ProductModal.hide());
    }

    // Close modal when clicking outside
    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          ProductModal.hide();
        }
      });
    }

    // Handle form submission
    if (productForm) {
      productForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitButton = modalSubmit;
        const originalText = submitButton.textContent;

        try {
          submitButton.textContent = "저장 중...";
          submitButton.disabled = true;

          const formData = new FormData(productForm);
          await ProductModal.submit(formData);
        } catch (error) {
          alert(`오류가 발생했습니다: ${error.message || "알 수 없는 오류"}`);
        } finally {
          submitButton.textContent = originalText;
          submitButton.disabled = false;
        }
      });
    }

    // File upload handling
    if (fileUploadArea && productImages) {
      // Click to upload
      fileUploadArea.addEventListener("click", () => {
        productImages.click();
      });

      // File input change
      productImages.addEventListener("change", (e) => {
        const files = Array.from(e.target.files);
        handleMultipleFileSelect(files);
      });

      // Drag and drop
      fileUploadArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        fileUploadArea.classList.add("dragover");
      });

      fileUploadArea.addEventListener("dragleave", (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove("dragover");
      });

      fileUploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove("dragover");

        const files = Array.from(e.dataTransfer.files).filter((file) =>
          file.type.startsWith("image/")
        );
        if (files.length > 0) {
          handleMultipleFileSelect(files);
        }
      });
    }

    function handleMultipleFileSelect(files) {
      // Add new files to existing selection
      selectedFiles.push(...files);

      // Update previews
      ProductModal.updateImagePreviews();
    }

    // Category management
    if (addCategoryBtn && categorySelect) {
      addCategoryBtn.addEventListener("click", () => {
        const selectedValue = categorySelect.value;
        if (selectedValue && !selectedCategories.includes(selectedValue)) {
          selectedCategories.push(selectedValue);
          ProductModal.updateCategoriesDisplay();
          categorySelect.value = ""; // Reset select
        }
      });

      // Also allow adding category by pressing Enter
      categorySelect.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          addCategoryBtn.click();
        }
      });
    }

    // Close modal with Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("show")) {
        ProductModal.hide();
      }
    });

    // Export to global scope
    window.ProductModal = ProductModal;
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProductModal);
  } else {
    initProductModal();
  }
})();
