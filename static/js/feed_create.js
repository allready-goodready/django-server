// static/js/feed_create.js

// 작성 모달 닫기
document.getElementById("close_create_modal_x")?.addEventListener("click", () => {
  document.getElementById("modal_create_feed").style.display = "none";
  document.body.style.overflowY = "visible";
});

let currentCreateIndex = 0; // feed_create용 이미지 인덱스

// 크롭한 이미지를 id=input_image에 가져오는 함수
window.insertCroppedImage = function () {
    const inputImageContainer = document.getElementById("input_image");
    
    // 전역 변수에서 가져옴
    const croppedImages = window.croppedList;

    if (!croppedImages || croppedImages.length === 0 || !inputImageContainer) return;
    
    const aspect = sessionStorage.getItem("croppedAspect") || "4/5"; 
    inputImageContainer.innerHTML = "";  // 초기화

    if (aspect) {
      inputImageContainer.style.aspectRatio = `${aspect}`;
    }

    // 이미지 보여주는 함수 따로 정의
  function showImage(index) {
    inputImageContainer.innerHTML = "";  // 초기화
    const img = document.createElement("img");
    img.src = croppedImages[index];
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "contain";
    inputImageContainer.appendChild(img);

    // 좌우 화살표 추가
    if (croppedImages.length > 1) {
      const leftArrow = document.createElement("button");
      leftArrow.innerHTML = "&#10094;";
      leftArrow.className = "arrow left";
      leftArrow.onclick = () => {
        if (currentCreateIndex > 0) {
          currentCreateIndex--;
          showImage(currentCreateIndex);
        }
      };

      const rightArrow = document.createElement("button");
      rightArrow.innerHTML = "&#10095;";
      rightArrow.className = "arrow right";
      rightArrow.onclick = () => {
        if (currentCreateIndex < croppedImages.length - 1) {
          currentCreateIndex++;
          showImage(currentCreateIndex);
        }
      };

      inputImageContainer.appendChild(leftArrow);
      inputImageContainer.appendChild(rightArrow);
    }
  }

  currentCreateIndex = 0;
  showImage(currentCreateIndex);
};

// feed_create 모달 열기 함수 (전역 등록)
function openCreateModal() {
  const createModal = document.getElementById("modal_create_feed");

  if (!createModal) return;

  createModal.style.top = window.pageYOffset + "px";
  createModal.style.display = "flex";
  createModal.style.opacity = "1";
  createModal.style.pointerEvents = "auto";
  

  const innerWindow = createModal.querySelector(".create_modal_window");
  if (innerWindow) {
    innerWindow.style.opacity = "1";
    innerWindow.style.pointerEvents = "auto";
  }

  document.body.style.overflowY = "hidden";

  // 이미지 미리보기 넣기
  window.insertCroppedImage();
}

// 전역 등록
window.openCreateModal = openCreateModal;

// 작성 모달 → 크롭 모달로 돌아가기
document.getElementById('close_create_modal')?.addEventListener('click', function () {
    document.getElementById('modal_create_feed').style.display = 'none';
    document.getElementById('modal_crop_feed').style.display = 'flex';
});


// 글자 수 카운팅
const contentInput = document.getElementById("input_caption");
const countDisplay = document.getElementById("content_count");

contentInput?.addEventListener("input", () => {
    const content = contentInput.value;
    if (content.length > 200) {
        contentInput.value = content.substring(0, 200);
    }
    countDisplay.textContent = contentInput.value.length;
});


window.addEventListener("DOMContentLoaded", () => {
  // 여행지 검색 아이콘 클릭
  const placeIcon = document.getElementById("place_search_icon");
  placeIcon?.addEventListener("click", function () {
    const searchModal = document.getElementById("search_place_modal"); 
    if (searchModal) {
      searchModal.style.display = "flex";
      document.body.style.overflowY = "hidden";
    }

    // 유저 정보 렌더링

    // 로그인한 사용자 정보를 불러와서 프로필에 반영
    // const username = "{{ request.user.username }}";  // 템플릿에서 넘기는 경우
    // const profileImageUrl = "{{ request.user.profile.image.url }}";  // 예: 사용자 프로필 사진 경로

    // document.getElementById("input_user_id").textContent = username;
    // document.getElementById("input_profile_image").src = profileImageUrl;
  });

  // 모달 바깥 클릭 시 닫기
  window.addEventListener("click", function (e) {
    const searchModal = document.getElementById("search_place_modal");
    if (e.target === searchModal) {
      searchModal.style.display = "none";
      document.body.style.overflowY = "visible";
    }
  });

  // 닫기 버튼(x) 클릭 시 검색 모달 닫기
  const closeBtn = document.getElementById("close_search_modal");
  closeBtn?.addEventListener("click", () => {
    const searchModal = document.getElementById("search_place_modal");
    if (searchModal) {
      searchModal.style.display = "none";
      document.body.style.overflowY = "visible";
    }
  });
});


// 공유하기 버튼을 눌렀을 때
document.getElementById("button_write_feed")?.addEventListener("click", async function (e) {
    e.preventDefault();     // a태그의 기본 동작 막기

    const formData = new FormData();

    const place = document.getElementById("input_place")?.value;
    const lat = document.getElementById("input_lat")?.value;
    const lng = document.getElementById("input_lng")?.value;
    const caption = document.getElementById("input_caption")?.value;

    // 장소나 캡션을 작성하지 않으면 등록 불가
    if (!place || !caption) {
      alert("여행지와 캡션을 모두 입력해주세요.");
      return;
    }

    // 캡션 유효성 검사 : 한글 자음 모음 따로 쓰기도 가능
    const captionPattern = /^[\u3131-\u318E\uAC00-\uD7A3a-zA-Z0-9\s.,!?()\[\]{}'"~:;\-]*$/;

    if (!captionPattern.test(caption)) {
      alert("⚠️ 캡션에는 한글, 영어, 공백, 문장부호(.,!?()[]{}'\"~:;-)만 입력할 수 있어요.");
      return;
    }

    formData.append("place", place);
    formData.append("caption", caption);
    if (lat)    formData.append("lat", lat);
    if (lng)    formData.append("lon", lng);

    // 확인용 로그
    console.log("lat in formData:", formData.get("lat"));
    console.log("lon in formData:", formData.get("lon"));

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    const base64Images = window.croppedList || []; 

    base64Images.forEach((base64Image, idx) => {
      if (!base64Image) return;

      const byteString = atob(base64Image.split(",")[1]);
      const mimeString = base64Image.split(",")[0].split(":")[1].split(";")[0];

      const ab = new ArrayBuffer(byteString.length);
      const ia = new Uint8Array(ab);
      for (let i = 0; i < byteString.length; i++) {
          ia[i] = byteString.charCodeAt(i);
      }

      const blob = new Blob([ab], { type: mimeString });
      const file = new File([blob], `image_${idx + 1}.jpg`, { type: mimeString });

      formData.append("images", file);  // 서버에서 getlist('images')로 받을 수 있도록
    });


    try {
        const response = await fetch('/feed/api/create/', {
          method: "POST",
          body: formData,
          credentials: 'include',
        });

        if (response.ok) {
        alert("업로드 완료");

        // 모달 닫기
        document.getElementById("modal_create_feed").style.display = "none";

        // 화면 새로고침 or 목록 갱신 등 추가 작업 가능
        location.reload();
        } else {
        const err = await response.json();
        alert("등록 실패: " + (err.detail || "오류가 발생했습니다."));
        }
    } catch (error) {
        console.error("업로드 중 오류:", error);
        console.log("place:", place);
        console.log("lat:", lat);
        console.log("lng:", lng);
        console.log("caption:", caption);
        console.log("images:", formData.getAll("images"));
        alert("서버와의 통신 중 오류가 발생했습니다.");
    }
});



