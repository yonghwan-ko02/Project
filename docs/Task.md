# Project Task List: 전래동화 리부트 (콩쥐의 선택)

## Phase 1: 환경 설정 및 기초 공사 (Environment & Foundation)
.- [x] **프로젝트 초기화**
    - [x] Python 가상환경 설정 (`venv`)
    - [x] 필수 라이브러리 설치 (`langchain`, `chromadb`, `ollama` 등)
    - [x] `requirements.txt` 작성
- [x] **Ollama 연동 테스트**
    - [x] Llama-3.1-8b-instruct 모델 로컬 구동 확인
    - [x] Python에서 Ollama API 호출 테스트 (LangChain 연동)

## Phase 2: 데이터 엔지니어링 (Data Engineering - LoreKeeper)
**SOLID & TDD 적용: Interface -> Test -> Implement**

- [x] **LoreKeeper 설계 및 테스트 준비**
    - [x] `LoreKeeper` 인터페이스(Abstract Base Class) 정의 (DIP)
    - [x] `MockLoreKeeper` 작성 (테스트용 의존성)
    - [x] Test Scaffold 구축 (`unittest` or `pytest`)
- [x] **기능 구현 (TDD Cycle)**
    - [x] `load_book()`: 텍스트 파일 로딩 및 청킹
        - [x] Test: 파일 로드 및 청크 분할 검증
        - [x] Implement: 로직 구현
    - [x] `build_index()`: ChromaDB 인덱스 생성
        - [x] Test: 임베딩 생성 및 저장 확인 (Mock DB 활용)
        - [x] Implement: ChromaDB 연동
    - [x] `retrieve()`: 쿼리 기반 검색 (RAG)
        - [x] Test: 검색 결과 관련성 검증
        - [x] Implement: 검색 로직

## Phase 3: AI 엔진 구현 (AI Engine - DungeonMaster)
**SOLID & TDD 적용: Interface -> Test -> Implement**

- [x] **DungeonMaster 설계 및 테스트 준비**
    - [x] `DungeonMaster` 인터페이스 정의
    - [x] `MockLLM` 설정 (Ollama 호출 없이 로직 테스트)
- [x] **기능 구현 (TDD Cycle)**
    - [x] 시스템 프롬프트 관리 모듈 구현
    - [x] `generate_story()`: 스토리 생성
        - [x] Test: 입력(Context + Query)에 따른 프롬프트 구성 검증
        - [x] Implement: LLM 호출 및 응답 처리
    - [x] **인과관계 처리 로직** (비틀기 분기)
        - [x] Test: 선택지(Choice)에 따른 상태(State) 변경 로직 테스트
        - [x] Test: 상태 조건(Condition)에 따른 스토리 분기 검증
        - [x] Implement: `GameState` 클래스 및 상태 전이(State Transition) 로직
        - [x] Implement: 원작 vs 리부트 엔딩 결정 알고리즘

## Phase 4: 게임 시스템 구축 (Game System - GameLoop)
**SOLID & TDD 적용: UI와 로직 분리 (SRP)**

- [x] **GameLoop 설계**
    - [x] `InputProvider` / `OutputDisplay` 인터페이스 정의 (UI 의존성 분리)
    - [x] `GameLoop` 클래스 설계 (Core Logic only)
- [x] **기능 구현 (TDD Cycle)**
    - [x] 메인 루프 (Loop)
        - [x] Test: 게임 턴 진행 및 종료 조건 테스트 (Mock IO 사용)
        - [x] Implement: 상태 머신(State Machine) 구현
    - [x] **메모리 관리 (Memory Management)**
        - [x] Test: 대화 히스토리 관리 및 요약 트리거 테스트
        - [x] Implement: `buffer_memory` 및 `summary` 로직

## Phase 5: 인터페이스 및 통합 (Interface & Integration)
**UI Implementation (Manual Verification Only - No Automated Tests)**

- [x] **CLI UI 구현 (Rich Library)**
    - [x] `RichOutputDisplay` 구현 (OutputDisplay 인터페이스 상속) [Manual Test]
    - [x] `QuestionaryInputProvider` 구현 (InputProvider 인터페이스 상속) [Manual Test]
- [x] **통합 테스트 (Integration)**
    - [x] 실제 Ollama 및 ChromaDB 연동 테스트
        - [x] `verify_integration.py` 스크립트 개선 (성능 메트릭, 로깅, 정리 기능)
        - [x] E2E 시나리오 테스트 파일 생성 (`test_e2e_scenarios.py`)
        - [x] 필요한 Ollama 모델 다운로드 (llama3.1, nomic-embed-text)
        - [x] 모든 통합 테스트 실행 및 검증
    - [x] 엔드투엔드(E2E) 시나리오 플레이

## Phase 6: 폴리싱 (Polish) & 확장 (Expansion)
- [x] **로그 및 데이터 저장 시스템**
    - [x] `Logger` 클래스 구현 (Singleton 패턴)
        - [x] 사용자 입력/AI 응답 쌍을 JSONL 포맷으로 저장
        - [x] 세션별 로그 파일 분리 (Timestamp 기반 네이밍)
- [x] **예외 처리 및 안정성 (Robustness)**
    - [x] Ollama 연결 실패 시 재시도(Retry) 로직
    - [x] ChromaDB 로드 실패 시 Fallback (메모리 전용 모드 등)
    - [x] 비정상적인 사용자 입력 핸들링 (빈 문자열, 욕설 필터링 등)
- [ ] **사용자 편의성 (UX)**
    - [x] 로딩 인디케이터 (Spinner) 추가 (Story Generation 중)
    - [x] `help`, `restart`, `save`, `load` 등 메타 커맨드 구현
    - [ ] 자동 오프닝(프롤로그) 구현 (게임 시작 시 상황 묘사)
- [x] **웹 인터페이스 (Web UI)**
    - [x] FastAPI 백엔드 구축 (`web_server.py`)
    - [x] WebSocket 실시간 통신 구현
    - [x] 반응형 웹 페이지 (`web/index.html`)
- [x] **플랫폼 호환성 (Compatibility)**
    - [x] Windows UTF-8 인코딩 문제 해결 (`run_game.py`, `.env`)
    - [x] 서버 실행 스크립트 단일화
- [x] **콘텐츠 확장**
    - [x] `story.txt` 전체 텍스트 확보 및 검수
    - [x] 캐릭터 페르소나(System Prompt) 고도화
        - [x] `persona_variants.py` 모듈 생성 (PersonaManager)
        - [x] 5가지 페르소나 정의 (classic, dialect, cynical, modern, poetic)
        - [x] DungeonMaster에 페르소나 지원 통합
        - [x] GameLoop에 `persona` 메타 커맨드 추가
        - [x] 게임 시작 시 페르소나 선택 UI 추가
