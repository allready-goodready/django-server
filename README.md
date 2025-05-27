## 커밋 메시지 규칙

| 타입     | 설명                                    | 예시                                                |
| -------- | --------------------------------------- | --------------------------------------------------- |
| feat     | 새로운 기능 추가                        | `feat(auth): 로그인 API 토큰 발급 로직 추가`        |
| fix      | 버그 수정                               | `fix(prediction): 모델 확률 출력 오류 수정`         |
| docs     | 문서 변경                               | `docs(README): 설치 및 실행 방법 보강`              |
| style    | 코드 포맷·세미콜론·공백 등 스타일 변경  | `style(css): 버튼 여백 조정`                        |
| refactor | 코드 리팩터링(기능 변경 없이 구조 개선) | `refactor(models): UserProfile 관계 정리`           |
| perf     | 성능 개선                               | `perf(api): 캐시 적용으로 응답 속도 향상`           |
| test     | 테스트 코드 추가·수정                   | `test(prediction): eye 모델 유닛 테스트 추가`       |
| chore    | 기타 변경(빌드, 설정 파일 등)           | `chore(ci): GitHub Action 워크플로우 추가`          |
| ci       | CI/CD 설정 변경                         | `ci: 도커 이미지 빌드 스크립트 수정`                |
| build    | 빌드 시스템 변경(의존성 업데이트 등)    | `build(deps): drf-simplejwt 최신 버전으로 업데이트` |
| revert   | 이전 커밋 되돌리기                      | `revert: feat(feed): 피드 카드 레이아웃 변경`       |

## .env 예시:

```shell
MYSQL_DATABASE=allready_db
MYSQL_USER=allready_user
MYSQL_PASSWORD=secret_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```
