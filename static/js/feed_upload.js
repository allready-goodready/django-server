// static/js/feed_upload.js

const uploadModal = document.getElementById("modal_upload_feed");
const openUploadBtn = document.getElementById("open_feed_create_modal");
const imageInput = document.getElementById("image_input");
const imageUploadBtn = document.getElementById("next_feed_step");
const nextBtn = document.getElementById("select_img");
const uploadText = document.getElementById("upload_text");
const previewWrapper = document.getElementById("preview_wrapper");

let selectedImages = [];  // 파일 객체 보관용
let imageURLs = [];   // dataURL 목록, sessionStorage에 저장
let currentIndex = 0;
let uploadModalActive = false;

// 업로드 모달 닫기
document.getElementById("close_upload_modal_x")?.addEventListener("click", () => {
  document.getElementById("modal_upload_feed").style.display = "none";
  document.body.style.overflowY = "visible";
});


// 업로드 모달 열기
openUploadBtn?.addEventListener("click", () => {
  // 모든 모달 닫기
  document.getElementById("modal_crop_feed").style.display = "none";
  document.getElementById("modal_create_feed").style.display = "none";
  
  // 초기화
  selectedImages = [];
  imageList = [];
  croppedList = [];
  imageURLs = [];
  currentCropIndex = 0;
  sessionStorage.removeItem("uploadedImageList");
  // create 모달 값도 초기화
  document.getElementById("input_caption").value = "";
  document.getElementById("input_place").value = "";
  document.getElementById("input_lat").value = "";
  document.getElementById("input_lng").value = "";
  document.getElementById("content_count").textContent = "0";
  document.getElementById("place_input").value = "";  // 장소 검색도 초기화

  nextBtn.style.display = "none";
  uploadText.style.display = "block";
  imageUploadBtn.style.display = "inline";
  previewWrapper.classList.add("d-none");
  previewWrapper.innerHTML = "";

  // 모달 열기
  uploadModal.style.top = window.pageYOffset + "px";
  uploadModal.style.display = "flex";
  document.body.style.overflowY = "hidden";
  

  sessionStorage.removeItem("uploadedImageList");
  sessionStorage.removeItem("croppedAspect");
  
  uploadModalActive = true;
});

// "사진 선택" 버튼 → input 열기
imageUploadBtn?.addEventListener("click", () => {
  imageInput.click();
});

// 파일 선택 시
imageInput?.addEventListener("change", async (e) => {
  const files = Array.from(e.target.files);

  for (const file of files) {
    if (selectedImages.length >= 5) {
      alert("이미지는 최대 5장까지 첨부할 수 있습니다.");
      break;
    }
    selectedImages.push(file);
  }

  imageURLs = await Promise.all(selectedImages.map(file => readFileAsDataURL(file)));

  if (imageURLs.length > 0) {
    sessionStorage.setItem("uploadedImageList", JSON.stringify(imageURLs));

    nextBtn.style.display = "inline";
    uploadText.style.display = "none";
    imageUploadBtn.style.display = "none";
    previewWrapper.classList.remove("d-none");

    currentIndex = 0;
    updateImagePreview();
  }

  imageInput.value = "";
});

// File → dataURL 변환 함수
function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.onerror = e => reject(e);
    reader.readAsDataURL(file);
  });
}

// 이미지 미리보기 업데이트
function updateImagePreview() {
  previewWrapper.innerHTML = "";

  const container = document.createElement("div");
  container.className = "image-box position-relative";

  const img = document.createElement("img");
  img.src = imageURLs[currentIndex];
  img.className = "preview-img"; 

  // 삭제 버튼 추가
  const deleteBtn = document.createElement("span");
  deleteBtn.textContent = "×";
  deleteBtn.className = "delete-button";

  deleteBtn.addEventListener("click", () => {
    if (imageURLs.length === 1) {
      // 마지막 이미지면 초기화
      selectedImages = [];
      imageURLs = [];
      previewWrapper.classList.add("d-none");
      nextBtn.style.display = "none";
      uploadText.style.display = "block";
      imageUploadBtn.style.display = "inline";
    } else {
      selectedImages.splice(currentIndex, 1);
      imageURLs.splice(currentIndex, 1);
      if (currentIndex >= imageURLs.length) currentIndex--;
      
    }

    sessionStorage.setItem("uploadedImageList", JSON.stringify(imageURLs));
    updateImagePreview();
  });
  
  // 좌우 화살표
  if (imageURLs.length > 1) {
    const leftArrow = document.createElement("button");
    leftArrow.innerHTML = "&#10094;";
    leftArrow.className = "arrow left";
    leftArrow.addEventListener("click", () => {
      if (currentIndex > 0) {
        currentIndex--;
        updateImagePreview();
      }
    });

    const rightArrow = document.createElement("button");
    rightArrow.innerHTML = "&#10095;";
    rightArrow.className = "arrow right";
    rightArrow.addEventListener("click", () => {
      if (currentIndex < imageURLs.length - 1) {
        currentIndex++;
        updateImagePreview();
      }
    });

    container.appendChild(leftArrow);
    container.appendChild(rightArrow);
  }

  // + 버튼 (모든 이미지에)
  const plusBtn = document.createElement("button");
  plusBtn.textContent = "+";
  plusBtn.className = "add-button";
  plusBtn.addEventListener("click", () => imageInput.click());

  container.appendChild(img);
  container.appendChild(deleteBtn)
  container.appendChild(plusBtn);

  previewWrapper.appendChild(container);
}

// 다음 → 크롭 모달로
nextBtn?.addEventListener("click", () => {
  uploadModal.style.display = "none";
  window.openCropModal(); // 크롭 모달 열기 함수는 전역에 정의된 상태
});

