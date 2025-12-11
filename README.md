### 📂 Project Structure
이 프로젝트는 FastAPI를 기반으로 구축되었으며, 모듈화된 아키텍처를 따릅니다. 각 디렉터리와 파일의 역할은 다음과 같습니다.

```

.
├── faiss_index/                     # FAISS 벡터 DB 인덱스 저장 디렉터리 (index.faiss, index.pkl)
├── r.py                             # 간단한 요청 테스트 / 실험용 스크립트
├── requirements.txt                 # 프로젝트 의존성 패키지 목록
└── src/                             # 메인 애플리케이션 소스 코드
    ├── core/                        # 프로젝트 설정 및 환경 변수 관리
    │   └── config.py                # .env 로드, 로깅 설정, 전역 환경 변수를 정의하는 설정 모듈
    │
    ├── embedding/                   # RAG 및 생성 모델에 사용하는 JSON 기반 정적 데이터
    │   ├── answer_patterns.json     # 답변 구조/패턴 데이터
    │   ├── answer_templates.json    # 기본 답변 템플릿
    │   ├── answer_templates_plus.json # 확장 템플릿(고급 버전)
    │   ├── company_values.json      # 기업별 핵심 가치관 데이터
    │   ├── competency_rubrics.json  # 역량 평가 기준(루브릭)
    │   └── question_templates.json  # 면접 질문 템플릿
    │
    ├── faiss_index/                 # (서비스용) 임베딩 인덱스 저장 폴더
    │   ├── index.faiss              # 벡터 DB 인덱스 파일
    │   └── index.pkl                # 인덱스 메타데이터
    │
    ├── main.py                      # FastAPI 애플리케이션 진입점 (라우터 등록 및 서비스 시작)
    │
    ├── routers/                     # API 엔드포인트 라우팅 (Controller 역할)
    │   ├── interview.py             # 면접 질문 생성 API
    │   ├── feedback.py              # 답변 피드백 생성 API
    │   ├── search.py                # RAG 검색 API
    │   └── tip.py                   # 면접 팁/가이드 생성 API
    │
    ├── schemas/                     # 요청/응답 데이터 구조 정의 (Pydantic DTO)
    │   ├── feedback.py              # 피드백 API 스키마
    │   ├── gen_question_models.py   # 질문 생성 API 스키마
    │   └── gen_tip_models.py        # 팁 생성 API 스키마
    │
    └── services/                    # 핵심 비즈니스 로직 처리(Service Layer)
        ├── ai_service.py            # OpenAI GPT 호출 및 프롬프트 구성 로직
        ├── gen_service.py           # 면접 질문 생성 로직
        ├── rag_service.py           # FAISS 기반 검색/임베딩 조회 처리
        ├── tip_service.py           # 면접 팁 및 조언 생성 로직
        └── utils.py                 # 공통 유틸 함수 (전처리, 파일 로드 등)

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


1️⃣ 가상환경(venv) 생성 및 활성화프로젝트 루트 디렉터리로 이동한 후, 독립적인 파이썬 실행 환경을 구성합니다.
```
Bash# 프로젝트 폴더로 이동
cd C:\Users\...\jobmate-ai
```
가상환경 생성
```
Bash
python -m venv venv
```
가상환경 활성화OS명령어

Windows
```
.\venv\Scripts\activate
```
Mac
```
/Linuxsource venv/bin/activate
```
💡 터미널 프롬프트 앞에 (venv)가 표시되면 활성화 성공입니다.

2️⃣ 라이브러리 설치필요한 Python 패키지들을 설치합니다.
```
Bash
pip install -r requirements.txt
```
3️⃣ 환경 설정 및 데이터 준비서버 실행 전, 아래 파일들이 올바른 위치에 있는지 확인해주세요.
```
📂 필수 파일 구조Plaintextjobmate-ai/
├── .env                      # OpenAI API Key 설정
├── src/
│   ├── main.py               # 실행 파일
│   └── embedding/            # 데이터 폴더
│       ├── question_templates.json
│       ├── answer_patterns.json
│       ├── competency_rubrics.json
│       ├── answer_templates
|       └── company_values.json
└── ...
```
4️⃣ 서버 실행Uvicorn을 사용하여 FastAPI 서버를 실행합니다.
```
Bash
# (venv) 활성화 상태에서 실행
uvicorn src.main:app --reload --port 8001
```
5️⃣ API 테스트 (Swagger UI)브라우저를 열고 아래 주소로 접속하여 API를 테스트할 수 있습니다.

👉 접속 URL: http://127.0.0.1:8001/docs
테스트 방법

POST /structured-feedback 엔드포인트 클릭
Try it out 버튼 클릭아래 Request Body 입력 후 Execute 클릭📝 

Request Body 예시
```
JSON{
  "company": "{company_name} (혹은 공백 가능)",
  "job_family": "IT",
  "question": "최근에 경험한 프로젝트 중에서 가장 인상 깊었던 경험을 말해 주세요.",
  "answer": "네, 4인 팀으로 진행했던 졸업 프로젝트에서 한 팀원이 개인 사정을 이유로 맡은 파트의 진행이 계속 늦어졌던 경험이 있습니다. (Situation) 마감 기한은 다가오는데 핵심 기능 구현이 지연되면서 프로젝트 전체에 차질이 생길 수 있는 위기 상황이었습니다. (Task) 저는 프로젝트를 성공적으로 완수하기 위해 이 문제를 해결해야 한다고 생각했습니다. 단순히 그 팀원을 비난하기보다는, 함께 해결책을 찾는 것이 중요하다고 판단했습니다. (Action) 먼저, 그 팀원과 따로 만나 이야기를 나누며 어려움을 들어주었습니다. 알고 보니, 해당 파트에 대한 기술적 이해도가 부족해 어디서부터 시작해야 할지 막막함을 느끼고 있었습니다. 그래서 저는 제가 먼저 관련 기술 자료를 리서치하여 정리해주고, 매일 30분씩 '페어 프로그래밍'을 하자고 제안했습니다. 함께 코드를 보며 막히는 부분을 같이 해결하고, 제가 아는 부분을 설명해주며 진행을 도왔습니다. (Result) 그 결과, 팀원은 다시 의욕을 되찾아 본인의 역할을 완수할 수 있었고, 저희 팀은 프로젝트를 성공적으로 마감하여 우수한 성적을 거둘 수 있었습니다. 이 경험을 통해 동료의 어려움에 공감하고 실질적인 도움을 통해 함께 문제를 해결하는 협업의 중요성을 배울 수 있었습니다."
}

```
