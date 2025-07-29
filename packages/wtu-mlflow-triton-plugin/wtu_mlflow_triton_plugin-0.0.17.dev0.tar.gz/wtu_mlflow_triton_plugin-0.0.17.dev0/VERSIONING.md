# 버전 관리 가이드

## 버전 체계

이 프로젝트는 [PEP 440](https://peps.python.org/pep-0440/)와 [Semantic Versioning](https://semver.org/)을 따릅니다.

### 버전 형식

```
MAJOR.MINOR.PATCH[.devN|aN|bN|rcN]
```

- **MAJOR**: 하위 호환성이 없는 API 변경
- **MINOR**: 하위 호환성을 유지하면서 기능 추가
- **PATCH**: 하위 호환성을 유지하면서 버그 수정
- **dev**: 개발 버전 (예: 1.2.0.dev0)
- **a**: 알파 버전 (예: 1.2.0a1)
- **b**: 베타 버전 (예: 1.2.0b1)
- **rc**: 릴리즈 후보 (예: 1.2.0rc1)

## 릴리즈 사이클

### 1. 개발 버전 (Development)

```sh
poe dev-start  # X.Y.Z -> X.Y.Z.dev0
```

- 활발한 개발이 진행되는 단계
- 기능이 자주 변경될 수 있음
- PyPI에 배포 가능하지만 권장하지 않음

### 2. 알파 버전 (Alpha) - 선택사항

```sh
poe version-alpha  # X.Y.Z.dev0 -> X.Y.Za1
```

- 주요 기능이 구현되었지만 불안정할 수 있음
- 내부 테스트 용도
- 공개 배포는 권장하지 않음

### 3. 베타 버전 (Beta) - 선택사항

```sh
poe version-beta  # X.Y.Za1 -> X.Y.Zb1
```

- 기능 동결 (Feature Freeze)
- 버그 수정에 집중
- 제한된 사용자 대상 테스트

### 4. 릴리즈 후보 (RC) - 선택사항

```sh
poe version-rc  # X.Y.Zb1 -> X.Y.Zrc1
```

- 최종 릴리즈 직전 단계
- 치명적인 버그만 수정

### 5. 정식 릴리즈

```sh
poe release-patch/minor/major  # 정식 버전 릴리즈
```

## 권장 워크플로우

### 간단한 버그 수정

```sh
# 바로 패치 릴리즈
poe release-patch-quick  # X.Y.Z -> X.Y.(Z+1)
poe publish
```

### 새 기능 개발

```sh
# 1. 개발 시작
poe dev-start           # 1.2.0 -> 1.2.0.dev0

# 2. 개발 및 테스트
poe test-all           # 모든 Python 버전 테스트

# 3. (선택) 개발 버전 배포
poe dev-publish
poe publish            # PyPI에 1.2.0.dev0 배포

# 4. 개발 완료
poe dev-finish         # 1.2.0.dev0 -> 1.2.0

# 5. 정식 릴리즈
poe release-minor      # 1.2.0 -> 1.3.0
poe publish
```

### 대규모 변경 (알파/베타 사용)

```sh
# 1. 개발 버전
poe dev-start          # 2.0.0 -> 2.0.0.dev0

# 2. 알파 릴리즈
poe version-alpha      # 2.0.0.dev0 -> 2.0.0a1
poe build && poe publish

# 3. 베타 릴리즈
poe version-beta       # 2.0.0a1 -> 2.0.0b1
poe build && poe publish

# 4. RC 릴리즈
poe version-rc         # 2.0.0b1 -> 2.0.0rc1
poe build && poe publish

# 5. 정식 릴리즈
poe version-release    # 2.0.0rc1 -> 2.0.0
poe release-major      # 전체 테스트 및 빌드
poe publish
```

## 주의사항

1. **PyPI는 버전 삭제 불가**: 한번 업로드된 버전은 삭제할 수 없음
2. **개발 버전 배포는 신중히**: 개발 버전도 영구 기록됨
3. **pip 기본 동작**: `pip install`은 프리릴리즈를 무시함
   - 설치하려면: `pip install package==1.2.0.dev0`
   - 또는: `pip install --pre package`

## 버전 확인

```sh
# 현재 버전 확인
poe version

# 설치 가능한 버전 확인
pip index versions wtu-mlflow-triton-plugin
```