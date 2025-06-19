// static/js/feed_list.js
// 나중에 프로필 이미지 부분 백엔드에서 받아오기 

// 현재 URL에서 'page' 쿼리 파라미터를 가져오는 함수
function getCurrentPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get("page")) || 1;
    return isNaN(page) ? 1 : page;
}

// 쿼리 파라미터를 수정해서 새로운 URL 쿼리 문자열을 반환하는 함수
function updateQueryParam(param, value, urlParams) {
    const updated = new URLSearchParams(urlParams);
    updated.set(param, value);
    return '?' + updated.toString();
}

// 북마크가 변경된 피드 ID를 기록할 Set
const updatedBookmarks = new Set();

document.addEventListener("DOMContentLoaded", function () {
    const paginationContainer = document.getElementById("pagination");
    const feedContainer = document.querySelector(".row");

    const currentPage = getCurrentPage();
    const urlParams = new URLSearchParams(window.location.search);
    const pageSize = parseInt(urlParams.get("page_size")) || 12;
    const apiUrl = `/feed/api/feeds/?${urlParams.toString()}`;

    // 피드 목록 API 요청
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            const totalFeeds = data.count;
            const perPage = isNaN(pageSize) ? 12 : pageSize;
            const totalPages = Math.ceil(totalFeeds / perPage);
            feedContainer.innerHTML = "";

            if (!data.results || !Array.isArray(data.results)) {
                console.error("피드 목록을 불러올 수 없습니다.");
                return;
            }

            // 각 피드를 카드 형태로 DOM에 추가
            data.results.forEach(feed => {
                const col = document.createElement("div");
                col.classList.add("col");

                // 북마크 상태에 따른 아이콘 스타일 설정
                const isBookmarked = feed.is_bookmarked;
                const bookmarkIconClass = isBookmarked ? "material-icons" : "material-icons-outlined";
                const bookmarkIconText = isBookmarked ? "bookmark" : "bookmark_border";
                const bookmarkColor = isBookmarked ? "#4169E1" : "black";

                // 피드 카드 HTML 구성
                col.innerHTML = `
                    <div class="feed-item position-relative" data-id="${feed.id}">
                        <div class="image-box">
                            <a href="#">
                                <img src="${feed.images[0]}" class="feed-img" alt="피드 이미지">
                                <div class="feed-overlay d-flex flex-column justify-content-between">
                                    <div class="overlay-top d-flex justify-content-between align-items-start">
                                        <div class="d-flex align-items-center">
                                            <img src="/static/images/user.jpg" class="profile-img me-2" alt="프로필">
                                            <div class="username"> ${feed.user.username} </div>
                                        </div>
                                        <span class="bookmark-icon ${bookmarkIconClass}" 
                                            style="position: absolute; top: 10px; right: 10px; z-index: 10; font-size: 28px; color:${bookmarkColor}">
                                            ${bookmarkIconText}
                                        </span>
                                    </div>
                                    <div class="location fw-semibold mt-1">
                                        # ${feed.place}
                                    </div>
                                    <p class="caption mt-auto">
                                        ${feed.caption.substring(0, 60)}
                                    </p>
                                </div>
                            </a>
                        </div>
                    </div>
                `;

                // 북마크 상태 갱신 (hover 시 서버에서 최신 정보 확인)
                col.addEventListener("mouseenter", async () => {
                    const feedId = col.querySelector(".feed-item").dataset.id;
                    const bookmarkBtn = col.querySelector(".bookmark-icon");

                    // 서버에서 최신 북마크 상태 조회
                    try {
                        const res = await fetch(`/feed/api/${feedId}/`);
                        const data = await res.json();

                        if (data.is_bookmarked) {
                            bookmarkBtn.textContent = "bookmark";
                            bookmarkBtn.classList.remove("material-icons-outlined");
                            bookmarkBtn.classList.add("material-icons");
                            bookmarkBtn.style.color = "#4169E1";
                        }
                        else {
                            bookmarkBtn.textContent = "bookmark_border";
                            bookmarkBtn.classList.remove("material-icons");
                            bookmarkBtn.classList.add("material-icons-outlined");
                            bookmarkBtn.style.color = "black";
                        }
                    }
                    catch (err) {
                        console.error("북마크 상태 갱신 실패:", err);
                    }
                });

                feedContainer.appendChild(col);

                // 북마크 아이콘 클릭 이벤트 (상세 모달 방지 + 토글 기능)
                const bookmarkBtn = col.querySelector(".bookmark-icon");
                bookmarkBtn.addEventListener("click", (e) => {
                    e.preventDefault();     // a 태그의 기본 동작 막기
                    e.stopPropagation();  // 카드 클릭 이벤트 방지 (상세 모달 방지)
                    const feedId = col.querySelector(".feed-item").dataset.id;
                    toggleBookmark(feedId, bookmarkBtn);  // 북마크 토글 함수 호출 (bookmark.js에서 정의)
                });
            });

            // 페이지네이션
            const pageGroupSize = 5;
            const currentGroup = Math.floor((currentPage - 1) / pageGroupSize);
            const startPage = currentGroup * pageGroupSize + 1;
            let endPage = startPage + pageGroupSize - 1;
            if (endPage > totalPages) endPage = totalPages;

            paginationContainer.innerHTML = "";

            if (startPage > 1) {
                const preLi = document.createElement("li");
                preLi.classList.add("page-item");
                const preLink = document.createElement("a");
                preLink.classList.add("page-link");
                preLink.href = updateQueryParam('page', startPage - 1, urlParams);
                preLink.textContent = "Previous";
                preLi.appendChild(preLink);
                paginationContainer.appendChild(preLi);
            }

            for (let i = startPage; i <= endPage; i++) {
                const li = document.createElement("li");
                li.classList.add("page-item");
                if (i === currentPage) li.classList.add("active");
                const link = document.createElement("a");
                link.classList.add("page-link");
                link.href = updateQueryParam('page', i, urlParams);
                link.textContent = i;
                li.appendChild(link);
                paginationContainer.appendChild(li);
            }

            if (endPage < totalPages) {
                const nextLi = document.createElement("li");
                nextLi.classList.add("page-item");
                const nextLink = document.createElement("a");
                nextLink.classList.add("page-link");
                nextLink.href = updateQueryParam('page', endPage + 1, urlParams);
                nextLink.textContent = "Next";
                nextLi.appendChild(nextLink);
                paginationContainer.appendChild(nextLi);
            }
        })
        .catch(error => {
            console.error("페이지네이션 에러:", error);
        });

    // 카드 클릭 시 상세 모달 열기
    document.addEventListener("click", function (e) {
        const target = e.target.closest(".feed-item");
        if (target && !e.target.classList.contains("bookmark-icon")) {
            e.preventDefault();
            const feedId = target.dataset.id;
            window.openFeedDetailModal(feedId);
        }
    });
});
