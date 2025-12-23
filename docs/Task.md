# Project Task List: 전래동화 리부트 (콩쥐의 선택)

## Phase 1: 환경 설정 및 기초 공사 (Environment & Foundation)
- [ ] **프로젝트 초기화**
    - [ ] Python 가상환경 설정 (`venv`)
    - [ ] 필수 라이브러리 설치 (`langchain`, `chromadb`, `ollama` 등)
    - [ ] `requirements.txt` 작성
- [ ] **Ollama 연동 테스트**
    - [ ] Llama-3.1-8b-instruct 모델 로컬 구동 확인
    - [ ] Python에서 Ollama API 호출 테스트 (LangChain 연동)

## Phase 2: 데이터 엔지니어링 (Data Engineering - LoreKeeper)
- [ ] **원본 데이터 준비**
    - [ ] `data/story.txt` : 콩쥐팥쥐 원문 텍스트 확보 및 정제
- [ ] **LoreKeeper 클래스 구현**
    - [ ] `load_book()`: 텍스트 파일 로딩 및 청킹(Chunking) 로직 구현
    - [ ] `build_index()`: ChromaDB 인덱스 생성 및 저장 (임베딩)
    - [ ] `retrieve()`: 쿼리 기반 문맥 검색(RAG) 기능 구현
    - [ ] 메타데이터 필터링 테스트 (캐릭터, 감정 등)

## Phase 3: AI 엔진 구현 (AI Engine - DungeonMaster)
- [ ] **DungeonMaster 클래스 구현**
    - [ ] 시스템 프롬프트(System Prompt) 설계 ("TRPG 마스터" 페르소나)
    - [ ] `generate_story()`: 사용자 입력 + RAG 결과 기반 스토리 생성
    - [ ] **인과관계 처리 로직** 구현 (원작 vs 비틀기 분기 처리)
- [ ] **프롬프트 엔지니어링**
    - [ ] 캐릭터 성격 유지를 위한 퓨샷(Few-shot) 예제 구성

## Phase 4: 게임 시스템 구축 (Game System - GameLoop)
- [ ] **GameLoop 클래스 구현**
    - [ ] 메인 루프 (Input -> Process -> Output)
    - [ ] **메모리 관리 (Memory Management)**
        - [ ] 최근 3턴 대화 유지 (`buffer_memory`)
        - [ ] 오래된 대화 요약 (`summary_memory`) 및 프롬프트 주입
- [ ] **인터페이스 (UI)**
    - [ ] 터미널 입출력 포맷팅 (색상, 구분선 등 가독성 개선)

## Phase 5: 통합 테스트 및 폴리싱 (Integration & Polish)
- [ ] **시나리오 테스트**
    - [ ] 오프닝 ~ 엔딩 플레이 테스트
    - [ ] 원작 파괴 선택지 시나리오 검증 (예: 두꺼비 발로 차기)
- [ ] **로그 시스템** (추후 확장을 위한 기반)
    - [ ] 사용자 선택 로그 파일 저장 기능
