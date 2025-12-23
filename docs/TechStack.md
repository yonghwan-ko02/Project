# Technology Stack (기술 스택)

## 1. Core Framework vs Language
*   **Language:** Python 3.10+
    *   **선정 이유:** 방대한 AI/ML 생태계, LangChain과의 최고의 호환성, 빠른 프로토타이핑 가능.
    *   **권장 버전:** 3.11 (성능 향상 및 안정성)

*   **Virtual Environment:** `venv` (Standard Library)
    *   **선정 이유:** 외부 의존성 없는 Python 표준 도구. 프로젝트의 "비용 0원" 및 "유지보수 최소화" 철학에 부합.

## 2. AI Engine (Local LLM)
*   **Modeling Engine:** **Ollama**
    *   **역할:** 로컬 환경에서 LLM을 실행하고 관리하는 서버/런타임.
    *   **선정 이유:** Docker나 복잡한 설정 없이 CLI 명령어로 모델 설치/실행 가능. REST API 제공으로 연동 용이.
    *   **Target Model:** `llama3.1:8b-instruct-q4_K_M` (또는 동급의 한국어 튜닝 모델)
        *   8B 파라미터: 일반 소비자용 노트북(8~16GB RAM)에서 구동 가능한 마지노선.

## 3. RAG Pipeline (LlamaIndex vs LangChain)
*   **Framework:** **LangChain**
    *   **선정 이유:** 단순 챗봇을 넘어선 "Agentic Workflow"(게임 로직, 메모리 관리, 툴 사용) 구현에 가장 적합한 표준 프레임워크.
    *   **핵심 모듈:**
        *   `langchain-core`: 기본 입출력 추상화
        *   `langchain-community`: 다양한 서드파티 통합
        *   `langchain-ollama`: Ollama 전용 커넥터

*   **Vector Database:** **ChromaDB**
    *   **선정 이유:**
        *   **Serverless:** 별도 DB 프로세스 설치 없이 로컬 파일(`sqlite` 기반)로 데이터 저장.
        *   **Python Native:** `pip install chromadb` 만으로 설치 끝.
    *   **역할:** 콩쥐팥쥐 원문 및 페르소나 데이터의 임베딩 저장소.

## 4. User Interface (CLI)
*   **Library:** **Rich**
    *   **선정 이유:** 밋밋한 터미널 텍스트를 "게임"처럼 보이게 만드는 스타일링 라이브러리.
    *   **활용:**
        *   내레이션 vs 대사 구분 (색상)
        *   진행 상황 바 (Progress Bar)
        *   마크다운 렌더링 (테이블, 강조 등)

*   **Input Handling:** **Questionary** (Optional)
    *   **선정 이유:** 화살표 키로 선택지 선택 등 직관적인 입력 UX 제공.

## 5. Development Tools
*   **Version Control:** Git + GitHub
*   **IDE:** VS Code
*   **Linting/Formatting:** Black, Flake8 (코드 품질 유지)

---

## 6. Dependencies (`requirements.txt` Preview)

```text
langchain
langchain-community
langchain-ollama
chromadb
rich
```
