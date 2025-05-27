## 커밋 메시지 규칙

- 커밋 메시지에 커밋 타입과 내용을 기입해야 합니다.

| 타입     | 설명                                    | 예시                                          |
| -------- | --------------------------------------- | --------------------------------------------- |
| feat     | 새로운 기능 추가                        | `feat: 로그인 API 토큰 발급 로직 추가`        |
| fix      | 버그 수정                               | `fix: 모델 확률 출력 오류 수정`               |
| docs     | 문서 변경                               | `docs: 설치 및 실행 방법 보강`                |
| style    | 코드 포맷·세미콜론·공백 등 스타일 변경  | `style: 버튼 여백 조정`                       |
| refactor | 코드 리팩터링(기능 변경 없이 구조 개선) | `refactor: UserProfile 관계 정리`             |
| perf     | 성능 개선                               | `perf: 캐시 적용으로 응답 속도 향상`          |
| test     | 테스트 코드 추가·수정                   | `test: eye 모델 유닛 테스트 추가`             |
| chore    | 기타 변경(빌드, 설정 파일 등)           | `chore: GitHub Action 워크플로우 추가`        |
| ci       | CI/CD 설정 변경                         | `ci: 도커 이미지 빌드 스크립트 수정`          |
| build    | 빌드 시스템 변경(의존성 업데이트 등)    | `build: drf-simplejwt 최신 버전으로 업데이트` |
| revert   | 이전 커밋 되돌리기                      | `revert: feat: 피드 카드 레이아웃 변경`       |


---

## 1. 브랜치 종류 및 네이밍 규칙

| 브랜치 종류 | 역할                                                                     | 네이밍 예시         |
| ----------- | ------------------------------------------------------------------------ | ------------------- |
| **main**    | 배포 가능한 최종 결과물 (Production)                                     | `main`              |
| **develop** | 다음 버전 개발을 위한 통합 브랜치                                        | `develop`           |
| **feat**    | WBS 또는 기능 명세서 기반으로 한 작업 단위 개발                          | `feat-FD-01`        |
| **bugfix**  | 배포된 기능(또는 develop)에서 발견된 버그 수정                           | `bugfix-FEED-03`    |
| **release** | 다음 배포를 준비 (테스트, 문서·릴리즈 노트 작성 등)                      | `release-v1.2.0`    |
| **hotfix**  | Production(`main`)에서 긴급히 수정할 필요가 있는 경우                    | `hotfix-PROD-123`   |
| **chore**   | 라이브러리 업데이트, 설정 변경, 문서·CI 수정 등 코드 기능 변화 없는 작업 | `chore-deps-update` |

---

## 2. 브랜치 생성/병합 흐름

1. **개발 시작**

   - 모든 기능 개발은 `develop` 브랜치에서 분기
   - 예: `git checkout develop && git checkout -b feat-FD-01`

2. **기능 완료 후 PR**

   - `feat-*`, `bugfix-*` 브랜치는 PR(PR 대상: `develop`)
   - 코드 리뷰 → `develop` 병합


---

## 3. 브랜치 네이밍 가이드라인

- **소문자 + 하이픈(-) 구분**
  예) `feat-user-auth`, `bugfix-feed-crash`
- **작업 코드 포함**
  예) `feat-FD-01`

---

## 4. 추가 팁

- **Protect 설정**: `main`, `develop` 브랜치에 직접 Push 금지
- **Branch Policy**: PR 승인 최소 1명 이상

---

## template 코드 위치

+ **전역템플릿 (BASE_DIR/templates/)**
: base.html, 공통 include 파일(navbar, footer 등)을 두고, 모든 앱 템플릿에서 {% extends "base.html" %} 사용

<br>

+ **앱별 템플릿 (앱이름/templates/앱이름/)**
: APP_DIRS=True 일 때 render(request, "accounts/signup.html", {...}) 처럼 경로를 지정



## .env 예시:

```shell
MYSQL_DATABASE=allready_db
MYSQL_USER=allready_user
MYSQL_PASSWORD=secret_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

## Python / Django / DB 버전

| 항목   | 버전     | 비고                    |
| ------ | -------- | ----------------------- |
| Python | `3.11.9` | pyenv 가상환경          |
| Django | `4.2.x`  | LTS 지원                |
| MySQL  | `8.4.x`  | macOS/Windows 공통 추천 |

## pip 패키지

| 패키지                      | 버전 (권장) | 용도                                 |
| --------------------------- | ----------- | ------------------------------------ |
| `Django`                    | `~=4.2`     | 웹 프레임워크                        |
| `djangorestframework`       | 최신        | REST API 제공                        |
| `django-allauth`            | 최신        | 소셜 로그인·회원관리                 |
| `drf-spectacular`           | 최신        | OpenAPI/Swagger 문서화               |
| `pillow`                    | 최신        | 이미지 처리                          |
| `cloudinary`                | 최신        | 미디어 호스팅                        |
| `django-cloudinary-storage` | 최신        | Cloudinary 스토리지 백엔드           |
| `dj-rest-auth[with_social]` | 최신        | 로그인/로그아웃/회원가입/소셜 로그인 |
| `django-filter`             | 최신        | DRF 쿼리 파라미터 필터링             |
| `django-environ`            | 최신        | `.env` 기반 환경변수 관리            |
| `whitenoise`                | 최신        | 정적 파일 서빙 (배포용)              |
| `mysqlclient`               | 최신        | MySQL 연동 드라이버                  |
| `crispy_forms`              | 최신        | Django 폼 렌더링/레이아웃            |
| `crispy_bootstrap5`         | 최신        | Bootstrap5용 crispy-forms 템플릿팩   |
| `bootstrap5`                | 최신        | Bootstrap5 컴포넌트 지원             |
