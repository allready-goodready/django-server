// static/js/bookmark.js
// 북마크 기능은 feed_detail 상세 모달과 feed_list hover 두 곳에서 사용되므로 별도 파일로 분리함


// CSRF 토큰 가져오기
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      // csrftoken 이름에 해당하는 쿠키 값을 추출
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let isProcessing = false;

// 북마크 토글 함수: 북마크 상태를 서버에 요청하고 아이콘 상태를 변경함
function toggleBookmark(feedId, iconElement) {
  if (isProcessing) return;  // 중복 요청 방지
    isProcessing = true;

  fetch(`/feed/api/${feedId}/bookmark/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    },
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("서버 오류 발생");
      }
      return response.json();
    })
    .then(data => {
      if (data.is_bookmarked) {
        // 북마크 추가 → 실선 아이콘 + 파란색
        iconElement.textContent = "bookmark";
        iconElement.classList.remove("material-icons-outlined");
        iconElement.classList.add("material-icons");
        iconElement.style.setProperty("color", "#4169E1", "important");
      } 
      
      else {
        // 북마크 해제 → 테두리 아이콘 + 검정색
        iconElement.textContent = "bookmark_border";
        iconElement.classList.remove("material-icons");
        iconElement.classList.add("material-icons-outlined");
        iconElement.style.color = "black";
      }
    })
    .catch(error => {
      console.error('북마크 처리 중 오류 발생:', error);
    })
    .finally(() => {
      isProcessing = false;  // 여기서 처리 완료 후 초기화
    });
}