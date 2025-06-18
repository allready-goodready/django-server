// static/js/feed_detail.js

// CSRF 토큰 가져오기
function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return "";
}

// 좋아요 버튼 초기화 + 클릭 이벤트 등록
function initLikeButton(feedId, isLiked, likeCount) {
    const oldBtn = document.getElementById("like-button");
    if (!oldBtn || !feedId) return;

    const likeBtn = oldBtn.cloneNode(true);  // 기존 버튼 복제
    oldBtn.replaceWith(likeBtn);             // 교체해서 이벤트 초기화 방지

    likeBtn.setAttribute("data-feed-id", feedId);

    // 초기 하트 상태 설정
    if (isLiked) {
        likeBtn.textContent = "favorite";
        likeBtn.classList.remove("material-icons-outlined");
        likeBtn.classList.add("material-icons");
        likeBtn.style.color = "red";
    } else {
        likeBtn.textContent = "favorite_border";
        likeBtn.classList.remove("material-icons");
        likeBtn.classList.add("material-icons-outlined");
        likeBtn.style.color = "black";
    }

    // 초기 좋아요 개수 표시
    const countSpan = document.getElementById("like-count");
    if (countSpan) {
        if (likeCount > 0) {
            countSpan.textContent = likeCount;
            countSpan.style.display = "inline";
        } else {
            countSpan.style.display = "none";
        }
    }

    // 클릭 이벤트 등록
    likeBtn.addEventListener("click", () => {
        fetch(`/feed/api/${feedId}/like/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json",
            },
        })
        .then(res => res.json())
        .then(data => {
            // 하트 상태 업데이트
            if (data.is_liked) {
                likeBtn.textContent = "favorite";
                likeBtn.classList.remove("material-icons-outlined");
                likeBtn.classList.add("material-icons");
                likeBtn.style.color = "red";
            } else {
                likeBtn.textContent = "favorite_border";
                likeBtn.classList.remove("material-icons");
                likeBtn.classList.add("material-icons-outlined");
                likeBtn.style.color = "black";
            }

            // 좋아요 수 업데이트
            if (countSpan) {
                if (data.like_count > 0) {
                    countSpan.textContent = data.like_count;
                    countSpan.style.display = "inline";
                } else {
                    countSpan.style.display = "none";
                }
            }
        })
        .catch(err => {
            console.error("좋아요 요청 실패", err);
        });
    });
}

// 피드 상세 모달 열기
window.openFeedDetailModal = function (feedId) {
    const modal = document.getElementById("modal_detail_feed");

    // 0. 다른 모달 닫기
    ["modal_upload_feed", "modal_crop_feed", "modal_create_feed"].forEach(id => {
        const m = document.getElementById(id);
        if (m) m.style.display = "none";
    });

    // 1. 모달 열기
    modal.style.top = "50%";
    modal.style.transform = "translateY(-50%)";
    modal.style.display = "flex";
    document.body.style.overflow = "hidden";

    // 2. 피드 상세 데이터 가져오기
    fetch(`/feed/api/${feedId}/`)
        .then(res => res.json())
        .then(data => {
            // 작성자, 내용, 장소
            document.getElementById("detail_profile_image").src = data.user.profile_image || "/static/images/user.jpg";
            document.getElementById("detail_user_id").textContent = data.user.username;
            document.getElementById("detail_caption").textContent = data.caption;
            document.querySelector("#detail_place span").textContent = data.place;

            // 좋아요 버튼/수 초기화
            initLikeButton(feedId, data.is_liked, data.like_count);

            // 이미지 슬라이더 설정
            window.feedImages = data.images;
            window.currentImageIndex = 0;

            function renderSliderImage() {
                const container = document.getElementById("detail_image");
                const totalImages = window.feedImages.length;
                const currentImage = window.feedImages[window.currentImageIndex];

                let prevBtn = '';
                let nextBtn = '';

                if (totalImages > 1 && window.currentImageIndex > 0)
                    prevBtn = `<button id="prevBtn" class="detail-arrow left">&#10094;</button>`;
                if (totalImages > 1 && window.currentImageIndex < totalImages - 1)
                    nextBtn = `<button id="nextBtn" class="detail-arrow right">&#10095;</button>`;

                container.innerHTML = `
                    <div class="slider-container" style="position: relative;">
                        <img src="${currentImage}" class="feed-img" style="width: 100%;">
                        ${prevBtn}
                        ${nextBtn}
                    </div>
                `;

                // 화살표 이벤트 등록
                document.getElementById("prevBtn")?.addEventListener("click", () => {
                    if (window.currentImageIndex > 0) {
                        window.currentImageIndex--;
                        renderSliderImage();
                    }
                });

                document.getElementById("nextBtn")?.addEventListener("click", () => {
                    if (window.currentImageIndex < totalImages - 1) {
                        window.currentImageIndex++;
                        renderSliderImage();
                    }
                });
            }

            renderSliderImage();
        })
        .catch(err => {
            console.error("피드 상세 로드 실패:", err);
        });
};

// 모달 닫기
document.getElementById("close_detail_modal_x")?.addEventListener("click", function () {
    document.getElementById("modal_detail_feed").style.display = "none";
    document.body.style.overflowY = "visible";
});
