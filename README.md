### 📂 Project Structure
이 프로젝트는 FastAPI를 기반으로 구축되었으며, 모듈화된 아키텍처를 따릅니다. 각 디렉터리와 파일의 역할은 다음과 같습니다.

```

.
├── faiss_index/             # FAISS 벡터 DB 인덱스 저장소 (생성된 .faiss, .pkl 파일)
├── r.py                     # 간단한 요청 테스트 또는 실행 스크립트
├── requirements.txt         # 프로젝트 의존성 패키지 목록
└── src/                     # 소스 코드 메인 디렉터리
    ├── core/                # 프로젝트 설정 및 환경 변수 관리
    │   └── config.py        # .env 로드, 로깅 설정, 전역 상수 정의
    │
    ├── embedding/           # RAG(검색 증강 생성)를 위한 원본 데이터 (JSON)
    │   ├── answer_patterns.json    # 답변 구조 패턴 데이터
    │   ├── company_values.json     # 기업별 인재상 데이터
    │   ├── competency_rubrics.json # 역량 평가 루브릭
    │   └── question_templates.json # 면접 질문 템플릿
    │
    ├── faiss_index/         # (백업/참조용) 임베딩 인덱스 폴더
    ├── main.py              # 애플리케이션 진입점 (FastAPI App 실행)
    │
    ├── routers/             # API 엔드포인트 라우팅 (Controller 역할)
    │   ├── feedback.py      # 면접 피드백 생성 관련 API
    │   └── search.py        # 질문/답변 검색 및 조회 API
    │
    ├── schemas/             # Pydantic 데이터 모델 (DTO)
    │   └── feedback.py      # 요청(Request) 및 응답(Response) 데이터 구조 정의
    │
    └── services/            # 비즈니스 로직 처리 (Service Layer)
        ├── ai_service.py    # OpenAI GPT API 호출 및 프롬프트 엔지니어링 로직
        ├── rag_service.py   # FAISS 벡터 검색 및 데이터 검색 로직
        └── utils.py         # 데이터 로드 등 공통 유틸리티 함수

```
### 🏗 Architecture Details
이 프로젝트는 기능별로 명확하게 모듈이 분리되어 있습니다.

1. src/core (Configuration)
config.py: 환경 변수(OPENAI_API_KEY 등), 파일 경로(BASE_DIR, DATA_DIR), 로깅 설정, OpenAI 클라이언트 인스턴스 생성 등을 담당합니다. 모든 설정값은 이곳에서 중앙 관리됩니다.

2. src/schemas (Data Validation)
feedback.py: 클라이언트와 서버 간에 주고받는 데이터의 형태를 정의합니다. Pydantic을 사용하여 데이터 유효성 검사를 수행하며, API 문서(Swagger UI) 자동 생성의 기준이 됩니다. (예: StructuredFeedbackRequest)

3. src/routers (API Layer)
실질적인 URL 엔드포인트가 정의되는 곳입니다. 비즈니스 로직을 직접 포함하지 않고, 요청을 받아 Service 계층으로 전달한 뒤 결과를 반환하는 역할을 합니다.

feedback.py: /structured-feedback 등 AI 피드백 관련 라우터.

search.py: /search-documents, /random-questions 등 검색 관련 라우터.

4. src/services (Business Logic)
프로젝트의 핵심 로직이 구현된 계층입니다.

rag_service.py: LangChain과 FAISS를 사용하여 벡터 DB를 구축하고, 질문에 가장 적합한 문서를 검색하는 RAG 로직을 수행합니다.

ai_service.py: 검색된 컨텍스트와 사용자 입력을 바탕으로 최적의 프롬프트를 구성하고, GPT 모델을 호출하여 응답을 생성합니다.

utils.py: JSON 파일 로딩, 데이터 전처리 등 보조적인 기능을 수행합니다.

5. src/embedding (Data Source)
RAG 시스템이 참조하는 지식 베이스(Knowledge Base)입니다. 기업 인재상, 면접 질문 예시, 답변 패턴 등이 JSON 형태로 저장되어 있으며, 서버 시작 시 이 데이터들이 임베딩되어 벡터 DB로 변환됩니다.

### 🚀 Getting Started
환경 변수 설정 .env 파일을 루트 디렉터리에 생성하고 API 키를 입력합니다.

```
Bash

OPENAI_API_KEY=sk-proj-...
패키지 설치

Bash
```

pip install -r requirements.txt
서버 실행

Bash

uvicorn src.main:app --reload
