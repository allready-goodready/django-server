// static/js/feed_detail.js


// 피드 상세 모달 열기 함수
window.openFeedDetailModal = function (feedId) {
    const modal = document.getElementById("modal_detail_feed");


    // 0. 작성 모달이 있다면 닫기
    const uploadModal = document.getElementById("modal_upload_feed");
    if (uploadModal) uploadModal.style.display = "none";
    
    const cropModal = document.getElementById("modal_crop_feed");
    if (cropModal) cropModal.style.display = "none";

    const createModal = document.getElementById("modal_create_feed");
    if (createModal) createModal.style.display = "none";

    // 1. 상세 모달 열기 
    modal.style.top = "50%";
    modal.style.transform = "translateY(-50%)";
    modal.style.display = "flex";
    document.body.style.overflow = "hidden";

    // 2. fetch 요청으로 피드 상세 데이터 불러오기
    fetch(`/feed/api/${feedId}/`)
        .then(res => res.json())
        .then(data => {
            // 프로필 이미지가 있다면 넣고 없으면 기본 이미지
            const profileImg = document.getElementById("detail_profile_image");
            if (data.user.profile_image) {
                profileImg.src = data.user.profile_image;
            } else {
                profileImg.src = "/static/images/user.jpg";
            }

            // 사용자명, 캡션, 장소 삽입
            document.getElementById("detail_user_id").textContent = data.user.username;
            document.getElementById("detail_caption").textContent = data.caption;
            document.querySelector("#detail_place span").textContent = data.place;

            // 슬라이더용 변수
            window.feedImages = data.images;   // 이미지 배열 저장
            window.currentImageIndex = 0;      // 현재 보여주는 이미지의 인덱스

            // 이미지 렌더링 함수
            function renderSliderImage() {
                const container = document.getElementById("detail_image");
                const totalImages = window.feedImages.length;
                const currentImage = window.feedImages[window.currentImageIndex];

                let prevBtn = '';
                let nextBtn = '';

                if (totalImages > 1 && window.currentImageIndex > 0) {
                    prevBtn = `<button id="prevBtn" class="detail-arrow left">&#10094;</button>`;
                }

                if (totalImages > 1 && window.currentImageIndex < totalImages - 1) {
                    nextBtn = `<button id="nextBtn" class="detail-arrow right">&#10095;</button>`;
                }

                // 이미지와 버튼들 덮어쓰기
                container.innerHTML = `
                    <div class="slider-container" style="position: relative;">
                        <img src="${currentImage}" class="feed-img" style="width: 100%;">
                        ${prevBtn}
                        ${nextBtn}
                    </div>
                `;

                // 버튼 이벤트 연결
                if (totalImages > 1) {
                    const prev = document.getElementById("prevBtn");
                    const next = document.getElementById("nextBtn");

                    if (prev) {
                        prev.addEventListener("click", () => {
                            if (window.currentImageIndex > 0) {
                                window.currentImageIndex--;
                                renderSliderImage();
                            }
                        });
                    }

                    if (next) {
                        next.addEventListener("click", () => {
                            if (window.currentImageIndex < totalImages - 1) {
                                window.currentImageIndex++;
                                renderSliderImage();
                            }
                        });
                    }
                }
            }

            renderSliderImage();
        })
        .catch(err => {
            console.error("피드 상세 로드 실패:", err);
        });
}

// 상세 모달 닫기
document.getElementById("close_detail_modal_x")?.addEventListener("click", function () {
    document.getElementById("modal_detail_feed").style.display = "none";
    document.body.style.overflowY = "visible";
});

