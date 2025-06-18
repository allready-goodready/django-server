// static/js/feed_crop.js
 
let cropper;
let imageList = [];     // 선택한 원본 이미지 목록
let croppedList = [];  // 크롭된 이미지 목록 (나중에 window.croppedList로 넘김)
let currentCropIndex = 0;   // 현재 크롭 중인 이미지 인덱스

// 크롭 모달 닫기
document.getElementById("close_crop_modal_x")?.addEventListener("click", () => {
  document.getElementById("modal_crop_feed").style.display = "none";
  document.body.style.overflowY = "visible";
});


// 문자열로 된 비율을 숫자로 변경
function parseRatio(str) {
    if (str.includes("/")) {
        const [w, h] = str.split("/").map(Number);
        return w / h;
    }
    return parseFloat(str);
}


// 크롭 모달 열기 (이미지 목록 불러오기)
function openCropModal() {
    const cropModal = document.getElementById("modal_crop_feed");
    const storedList = sessionStorage.getItem("uploadedImageList");

    if (!storedList) return;

    imageList = JSON.parse(storedList);     // 업로드된 이미지 목록 불러옴
    croppedList = new Array(imageList.length).fill(null);   // 크롭 리스트 초기화
    currentCropIndex = 0;

    cropModal.style.top = window.pageYOffset + "px";
    cropModal.style.display = "flex";
    document.body.style.overflowY = "hidden";

    loadCropperImage();     // 첫 이미지 업로드
    setupArrowButtons();    // 좌우 화살표 셋팅
    setupRatioButtons();    // 비율 버튼 셋팅
}

// 외부에서도 접근 가능하도록 전역 함수로 등록
window.openCropModal = openCropModal;


// 현재 인덱스의 이미지를 Cropper에 load
function loadCropperImage() {
    const imageElement = document.getElementById("crop_target_image");
    if (cropper) cropper.destroy();

    imageElement.src = imageList[currentCropIndex];     // 해당 인덱스의 이미지

    imageElement.onload = function () {
        cropper = new Cropper(imageElement, {
            aspectRatio: 4 / 5,
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
            background: false,
            dragMode: 'none',
            movable: false,
            zoomable: false,
            cropBoxResizable: true,
        });

        // 비율 버튼 active 상태 유지
        const activeBtn = document.querySelector(".ratio_buttons .active");
        if (activeBtn) {
            const ratioStr = activeBtn.dataset.ratio;
            cropper.setAspectRatio(parseRatio(ratioStr));
            sessionStorage.setItem("croppedAspect", ratioStr);
        }
    };
}

// 좌우 화살표 버튼
function setupArrowButtons() {
    const container = document.querySelector(".crop_modal_content");

    container.querySelectorAll(".crop-arrow").forEach(el => el.remove());

    const leftArrow = document.createElement("button");
    leftArrow.innerHTML = "&#10094;";
    leftArrow.className = "arrow left";
    leftArrow.addEventListener("click", () => {
        saveCurrentCrop();  // 현재 이미지 저장
        if (currentCropIndex > 0) {
            currentCropIndex--;     // 이전 이미지로 이동
            loadCropperImage();
        }
    });

    const rightArrow = document.createElement("button");
    rightArrow.innerHTML = "&#10095;";
    rightArrow.className = "arrow right";
    rightArrow.addEventListener("click", () => {
        saveCurrentCrop();  // 현재 이미지 저장
        if (currentCropIndex < imageList.length - 1) {
            currentCropIndex++;     // 다음 이미지로 이동
            loadCropperImage();
        }
    });

    container.appendChild(leftArrow);
    container.appendChild(rightArrow);
}

// 비율 선택 버튼
function setupRatioButtons() {
    document.querySelectorAll(".ratio_buttons button").forEach(button => {
        if (!button.dataset.bound) {
            button.addEventListener("click", function () {
                const ratioStr = this.dataset.ratio;
                const ratioNum = parseRatio(ratioStr);

                cropper.setAspectRatio(ratioNum);
                sessionStorage.setItem("croppedAspect", ratioStr);

                // 버튼 active 상태 토글
                document.querySelectorAll(".ratio_buttons button")
                    .forEach(btn => btn.classList.remove("active"));
                this.classList.add("active");
            });
            button.dataset.bound = "true";      // 중복 바인딩 방지
        }
    });
}


// 현재 이미지 크롭 결과 저장
function saveCurrentCrop() {
  if (!cropper) return false;

  let croppedCanvas = cropper.getCroppedCanvas();

  // 크롭 영역이 너무 작거나 없는 경우
  if (!croppedCanvas || croppedCanvas.width === 0 || croppedCanvas.height === 0) {
    console.log("사용자가 크롭을 건드리지 않음 → 4:5로 자동 크롭");

    // 원본 이미지에서 4:5 중심 비율로 자동 자르기
    const imageData = cropper.getImageData();
    const naturalWidth = imageData.naturalWidth;
    const naturalHeight = imageData.naturalHeight;

    const targetRatio = 4 / 5;
    let cropWidth = naturalWidth;
    let cropHeight = Math.round(cropWidth / targetRatio);

    if (cropHeight > naturalHeight) {
      cropHeight = naturalHeight;
      cropWidth = Math.round(cropHeight * targetRatio);
    }

    const startX = Math.round((naturalWidth - cropWidth) / 2);
    const startY = Math.round((naturalHeight - cropHeight) / 2);

    cropper.setCropBoxData({
      left: startX,
      top: startY,
      width: cropWidth,
      height: cropHeight,
    });

    // 다시 캔버스 생성
    croppedCanvas = cropper.getCroppedCanvas();
  }

  const croppedImage = croppedCanvas.toDataURL("image/png");
  croppedList[currentCropIndex] = croppedImage;
  return true;
}


// 뒤로 가기 버튼 눌러서 feed_upload 모달로 이동 (사진 첨부)
document.getElementById("close_crop_modal")?.addEventListener("click", function () {
    document.getElementById("modal_crop_feed").style.display = "none";
    document.getElementById("modal_upload_feed").style.display = "flex";
    document.body.style.overflowY = "hidden";
});

// '다음' 버튼 클릭하면 feed_create 모달로 이동 (내용 작성)
const toCreateBtn = document.getElementById("apply_crop");

toCreateBtn?.addEventListener("click", () => {
    const success = saveCurrentCrop();  // 마지막 이미지도 저장
    if (!success) return; // 크롭 안 했으면 이후 로직 중단

    // 하나라도 크롭 안 된 이미지가 있으면 에러
    const isAllCropped = croppedList.every((item) => item !== null);
    if (!isAllCropped) {
        alert("모든 사진을 크롭해주세요!");
        return;
    }

    console.log("croppedList : ", croppedList)
    window.croppedList = [...croppedList];      // sessionStorage 대신 전역 변수로 넘김

    // 모달 전환
    uploadModalActive = false;      // 모달 전환 전 이벤트 충돌 방지
    
    document.getElementById("modal_crop_feed").style.display = "none";
    document.getElementById("modal_upload_feed").style.display = "none"; // 혹시 켜져 있으면

    window.openCreateModal();
});

// cropper 관련 상태 초기화 함수 (upload.js에서 호출할 수 있게 export)
window.resetCropper = function () {
  if (cropper) {
    cropper.destroy();
    cropper = null;
  }
  imageList = [];
  croppedList = [];
  currentCropIndex = 0;
};

