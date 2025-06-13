// static/js/feed_list.js

function getCurrentPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get("page")) || 1;
    
    return isNaN(page) ? 1 : page;
}

function updateQueryParam(param, value, urlParams) {
    const updated = new URLSearchParams(urlParams);
    updated.set(param, value);
    return '?' + updated.toString();
}

document.addEventListener("DOMContentLoaded", function () {
    const paginationContainer = document.getElementById("pagination");
    const feedContainer = document.querySelector(".row");  // 카드들이 들어있는 div

    // 현재 페이지 번호 가져오기
    const currentPage = getCurrentPage();
    
    const urlParams = new URLSearchParams(window.location.search);
    const pageSize = parseInt(urlParams.get("page_size")) || 12;

    const queryString = urlParams.toString();  // 쿼리 전체 추출
    const apiUrl = `/feed/api/feeds/?${queryString}`;

    // 현재 페이지 번호 기반 API 요청
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            const totalFeeds = data.count;
            const perPage = isNaN(pageSize) ? 12 : pageSize;
            const totalPages = Math.ceil(totalFeeds / perPage);

            // 피드 목록 렌더링
            feedContainer.innerHTML = "";

            if (!data.results || !Array.isArray(data.results)) {
                console.error("피드 목록을 불러올 수 없습니다.");
                return;
            }

            data.results.forEach(feed => {
                const col = document.createElement("div");
                col.classList.add("col");
                col.innerHTML = `
                    <div class="feed-item position-relative">
                        <div class="image-box">
                            <a href="#">
                                <img src="${feed.images[0]}" class="feed-img" alt="피드 이미지">
                                <div class="feed-overlay d-flex flex-column justify-content-between">
                                    <div class="overlay-top d-flex justify-content-between align-items-start">
                                        <div class="d-flex align-items-center">
                                            <img src="/static/images/user.jpg" class="profile-img me-2" alt="프로필">
                                            <div class="username"> ${feed.user.username} </div>
                                        </div>
                                        <img src="/static/images/bookmark.png" class="bookmark-icon" alt="북마크">
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
        `       ;
                feedContainer.appendChild(col);
            });

            // 페이지네이션 렌더링
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
        
    // // 모달 열기 함수
    // function openFeedDetailModal(feedId) {
    //     const modal = document.getElementById("modal_detail_feed");

    //     fetch(`/api/feed/${feedId}/`)
    //         .then(res => res.json())
    //         .then(data => {
    //             document.getElementById("detail_image").innerHTML = `
    //                 <img src="${data.images[0]}" class="feed-img" style="width: 100%;">
    //             `;
    //             document.getElementById("input_user_id").textContent = data.user.username;
    //             document.getElementById("detail_caption").textContent = data.caption;
    //             document.getElementById("detail_place").innerHTML = `여행지: <span class="fw-bold">${data.place}</span>`;
                
    //             modal.style.display = "flex";
    //             document.body.style.overflow = "hidden";
    //         })
    //         .catch(err => {
    //             console.error("피드 상세 로드 실패:", err);
    //         });
    // }

    // // 모달 닫기 버튼
    // document.getElementById("close_create_modal_x")?.addEventListener("click", () => {
    //     document.getElementById("modal_detail_feed").style.display = "none";
    //     document.body.style.overflowY = "visible";
    // });

    // // 동적으로 생성된 카드에 이벤트 위임
    // document.addEventListener("click", function (e) {
    //     if (e.target.closest(".open-detail-modal")) {
    //         e.preventDefault();
    //         const id = e.target.closest(".open-detail-modal").dataset.id;
    //         openFeedDetailModal(id);
    //     }
    // });

    // 예시: 피드 카드 클릭 시 detail 모달 띄우기
    document.addEventListener("click", function (e) {
    const target = e.target.closest(".feed-item");  // 카드 전체

    if (target) {
        // 모달 열기
        const modal = document.getElementById("modal_detail_feed");
        if (modal) {
        modal.style.top = window.pageYOffset + "px";
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";  // 스크롤 잠금

        // 테스트용 더미 데이터 넣기
        document.getElementById("detail_image").innerHTML = `
            <img src="/static/images/1.png" ">
        `;
        document.getElementById("input_user_id").textContent = "sample_user";
        document.getElementById("detail_caption").textContent = "이건 테스트 캡션입니다.";
        document.querySelector("#detail_place span").textContent = "대한민국 서울";
        }
    }
    });

    document.getElementById("close_create_modal_x")?.addEventListener("click", function () {
        document.getElementById("modal_detail_feed").style.display = "none";
        document.body.style.overflowY = "visible";
    });    
});
