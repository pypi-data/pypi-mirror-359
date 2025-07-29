# w-train-utils-mlflow-triton-plugin

MLflow plugin for Triton Inference Server with secure Python function execution

## 빠른 시작

### 1. 환경 설정

```sh
# UV 설치 (이미 설치되어 있지 않은 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 클론 및 의존성 설치
git clone https://github.com/hbjs/w-train-utils-mlflow-triton-plugin
cd w-train-utils-mlflow-triton-plugin
uv sync  # 가상환경 자동 생성 및 개발 의존성 설치
```

### 2. 필수 환경 변수

```sh
export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export MLFLOW_TRACKING_URI=http://localhost:5001
export AWS_ACCESS_KEY_ID=minio
export AWS_SECRET_ACCESS_KEY=miniostorage
export TRITON_URL=http://localhost:8001
export TRITON_MODEL_REPO=s3://http://localhost:9000/triton
```

### 3. 기본 사용법

```sh
# 코드 품질 검사
uv run poe format    # 코드 포맷팅
uv run poe check     # 린팅 + 타입 체크
uv run poe test      # 테스트 실행

# 버전 확인
uv run poe version
```

## 개발 가이드

### 개발 환경

```sh
# 개발 의존성 포함 설치
uv sync

# 프로덕션 의존성만 설치
uv sync --no-dev

# 의존성 업데이트
uv lock --upgrade
```

### 코드 품질 관리

```sh
# 코드 포맷팅
uv run poe format

# 린팅 + 타입 체크
uv run poe check

# CI 파이프라인 (검사 + 테스트)
uv run poe ci
```

### 테스트

```sh
# 기본 테스트
uv run poe test

# 커버리지 포함
uv run poe test-cov

# 특정 Python 버전 테스트
uv run poe test-py39
uv run poe test-py310
uv run poe test-py312

# 모든 Python 버전 테스트
uv run poe test-all
```

## 버전 관리 및 배포

### 개발-릴리즈 사이클

```mermaid
graph LR
    A[안정 버전 0.0.15] --> B[버전 증가 poe version-patch]
    B --> C[다음 버전 0.0.16]
    C --> D[개발 시작 poe dev-start]
    D --> E[개발 버전 0.0.16.dev0]
    E --> F[개발/테스트 변경사항 작업]
    F --> G{개발 버전 배포 필요?}
    G -->|Yes| H[개발 배포 poe dev-publish]
    H --> I[PyPI poe publish]
    I --> F
    G -->|No| J[개발 완료 poe dev-finish]
    J --> K[릴리즈 준비 0.0.16]
    K --> L[최종 테스트 poe ci-all-versions]
    L --> M[빌드 poe build]
    M --> N[PyPI 배포 poe publish]
    N --> A
```

### 개발 버전 워크플로우

개발 버전은 **다음 릴리즈**를 위한 활발한 개발이 진행되는 단계입니다.

#### 1. 다음 버전 준비

```sh
# 먼저 버전을 올립니다
poe version-patch   # 0.0.15 -> 0.0.16
# 또는
poe version-minor   # 0.0.15 -> 0.1.0
# 또는
poe version-major   # 0.0.15 -> 1.0.0
```

#### 2. 개발 모드 시작

```sh
poe dev-start       # 0.0.16 -> 0.0.16.dev0
```

#### 3. 개발 및 테스트

```sh
# 코드 변경 후 검증
poe check           # 린팅 + 타입 체크
poe test            # 단위 테스트
poe test-all        # 모든 Python 버전 테스트
```

#### 4. 개발 버전 배포 (선택사항)

개발 버전 배포는 다음과 같은 경우에만 권장됩니다:

- 다른 프로젝트에서 테스트가 필요한 경우
- 특정 사용자에게 사전 배포가 필요한 경우

```sh
poe dev-publish     # CI 테스트 및 빌드
poe publish         # PyPI에 배포 (예: 0.0.16.dev0)
```

> **주의**:
>
> - PyPI에 업로드된 버전은 삭제할 수 없습니다
> - `pip install package`는 개발 버전을 무시합니다
> - 개발 버전 설치: `pip install package==0.0.16.dev0`

#### 5. 정식 릴리즈

```sh
poe dev-finish      # 0.0.16.dev0 -> 0.0.16
poe ci-all-versions # 모든 Python 버전 최종 테스트
poe build           # 패키지 빌드
poe publish         # PyPI에 정식 배포
```

### 릴리즈 워크플로우

릴리즈 명령은 자동으로 다음을 수행합니다:

- 빌드 아티팩트 정리
- 버전 업데이트
- **모든 Python 버전 CI 테스트** (3.9, 3.10, 3.12)
- 패키지 빌드 및 검증

```sh
# 패치 릴리즈 (버그 수정)
poe release-patch

# 마이너 릴리즈 (새 기능)
poe release-minor

# 메이저 릴리즈 (호환성 변경)
poe release-major

# 긴급 패치 (현재 Python만)
poe release-patch-quick
```

### PyPI 배포

#### 배포 설정

```sh
# ~/.pypirc 파일 설정
[pypi]
  username = __token__
  password = <your-pypi-token>
```

#### 배포 명령어

```sh
# PyPI에 배포
poe publish
```

## 예시 시나리오

### 간단한 버그 수정

```sh
# 개발 버전 없이 바로 패치
poe release-patch-quick  # 현재 Python 버전만 테스트
poe publish
```

### 일반적인 기능 개발

```sh
# 1. 다음 버전 결정 및 개발 시작
poe version-minor   # 0.0.15 -> 0.1.0
poe dev-start       # 0.1.0 -> 0.1.0.dev0

# 2. 개발 진행
# ... 코드 변경 ...
poe test-all        # 모든 Python 버전 테스트

# 3. 개발 완료 및 릴리즈
poe dev-finish      # 0.1.0.dev0 -> 0.1.0
poe build           # 패키지 빌드
poe publish         # PyPI에 배포
```

### 대규모 변경 (알파/베타 테스트 필요 시)

```sh
# 1. 다음 메이저 버전 준비
poe version-major   # 0.0.16 -> 1.0.0
poe dev-start       # 1.0.0 -> 1.0.0.dev0

# 2. 알파 테스트 (선택사항)
poe version-alpha   # 1.0.0.dev0 -> 1.0.0a1
poe build && poe publish

# 3. 베타 테스트 (선택사항)
poe version-beta    # 1.0.0a1 -> 1.0.0b1
poe build && poe publish

# 4. 정식 릴리즈
poe version-release # 1.0.0b1 -> 1.0.0
poe ci-all-versions # 전체 테스트
poe build && poe publish
```

> 더 자세한 버전 관리 가이드는 [VERSIONING.md](VERSIONING.md)를 참조하세요.

## 참고 사항

### 환경 변수 상세

| 환경변수               | 설명                   | 예시                    |
| ---------------------- | ---------------------- | ----------------------- |
| MLFLOW_S3_ENDPOINT_URL | MinIO 엔드포인트 URL   | `http://localhost:9000` |
| MLFLOW_TRACKING_URI    | MLflow 트래킹 서버 URI | `http://localhost:5001` |
| AWS_ACCESS_KEY_ID      | AWS/MinIO 액세스 키    | `minio`                 |
| AWS_SECRET_ACCESS_KEY  | AWS/MinIO 시크릿 키    | `miniostorage`          |
| TRITON_URL             | Triton gRPC 엔드포인트 | `http://localhost:8001` |
| TRITON_MODEL_REPO      | Triton 모델 저장소 URL | `s3://bucket/models`    |

### Triton Inference Server 실행

```sh
docker run --rm -p8000:8000 -p8001:8001 -p8002:8002 \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    nvcr.io/nvidia/tritonserver:24.01-py3 \
    tritonserver --model-repository=$TRITON_MODEL_REPO \
    --model-control-mode=explicit \
    --log-verbose=1
```

### Python 버전 관리

```sh
# 지원 Python 버전 설치
poe install-pythons

# 특정 버전 테스트
poe test-py39
poe test-py310
poe test-py312
```
