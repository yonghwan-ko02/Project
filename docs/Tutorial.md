# 전래동화 리부트 (콩쥐의 선택) 제작 튜토리얼

이 문서는 "콩쥐의 선택" 텍스트 어드벤처 게임을 바닥부터 완성까지 만드는 전체 과정을 안내합니다.

---

## 1. 개요 (Overview)

프로젝트 기획 및 설계 단계에서 작성된 `docs` 폴더 내 주요 문서들에 대한 설명입니다.

*   **`Ideation.md`**: 프로젝트의 초기 아이디어 브레인스토밍 문서입니다. (핵심 컨셉: 밑 빠진 독 거부하기)
*   **`PRD.md` (Product Requirements Document)**: 아이디어를 구체화하여 제품의 목표, 제약 조건, 기능 요구사항을 정의한 명세서입니다.
*   **`TechStack.md`**: 프로젝트에 사용될 프로그래밍 언어, 라이브러리, 툴 등 기술적 기반을 정의한 문서입니다.
*   **`Task.md`**: 개발 단계를 Phase별로 나누고 세부 할 일을 정리한 작업 목록(Backlog)입니다.
*   **`presentation.md`**: 프로젝트 소개를 위한 발표 자료(Marp 포맷)입니다.

---

## 2. 사전 준비 (Prerequisites)

개발 시작 전, 로컬 환경에 다음 도구들이 설치되어 있는지 확인해주세요.

### 필수 소프트웨어
1.  **Python 3.10 이상**: [python.org](https://www.python.org/)에서 설치.
2.  **Git & GitHub CLI**: 버전 관리 및 이슈 트래킹을 위해 필요.
3.  **VS Code**: 권장 코드 편집기. ([Marp for VS Code Extension](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) 설치 권장)
4.  **Ollama**: 로컬 LLM 구동기. [ollama.com](https://ollama.com/)에서 다운로드.

### 모델 준비
터미널에서 다음 명령어로 사용할 AI 모델을 다운로드합니다.
```bash
ollama run llama3.1
# 또는 한국어 성능이 튜닝된 모델 (예: EEVE-Korean 등) 사용 가능
# 메모리 절약을 위해 텍스트 임베딩 모델도 필요할 수 있음
ollama pull nomic-embed-text
```

---

## 3. 최종 프로젝트 구조 (Project Structure)

개발이 완료되었을 때 예상되는 프로젝트 폴더 구조입니다.

```text
Project/
├── .venv/                  # Python 가상환경 (Git 제외)
├── data/
│   └── story.txt           # 콩쥐팥쥐 원본 텍스트 파일
├── docs/                   # 기획 및 설계 문서 (상기 참조)
├── src/                    # 소스 코드
│   ├── __init__.py
│   ├── lore_keeper.py      # RAG & ChromaDB 관리 클래스
│   ├── dungeon_master.py   # 스토리 생성 및 AI 로직 클래스
│   └── game_loop.py        # 게임 진행 및 UI/UX 클래스
├── main.py                 # 프로그램 진입점 (Entry Point)
├── requirements.txt        # 의존성 라이브러리 목록
└── README.md               # 프로젝트 메인 설명
```

---

## 4. 단계별 제작 가이드 (Step-by-Step)

`docs/Task.md`의 흐름에 따라 순차적으로 진행합니다.

### Step 1: 환경 설정 (Setup)
*   프로젝트 폴더 생성 및 Git 초기화 (`git init`)
*   Python 가상환경 생성 (`python -m venv .venv`) 및 활성화
*   필수 패키지 설치 (`langchain`, `chromadb`, `rich` 등)

### Step 2: 데이터 준비 (LoreKeeper 구현)
*   저작권 만료된 콩쥐팥쥐 텍스트 확보 (`data/story.txt`)
*   텍스트를 문단 단위로 자르고(Chunking), ChromaDB에 저장하는 로직 구현
*   테스트: 특정 키워드(예: "두꺼비")로 관련 문장이 잘 검색되는지 확인

### Step 3: AI 엔진 구축 (DungeonMaster 구현)
*   LangChain과 Ollama 연결
*   시스템 프롬프트 작성: "당신은 TRPG 마스터입니다..."
*   RAG 결합: 사용자 입력 + 검색된 원작 내용 -> 새로운 스토리 생성

### Step 4: 게임 루프 완성 (GameLoop & UI)
*   `rich` 라이브러리를 활용하여 터미널 화면 꾸미기
*   게임의 시작(오프닝)부터 종료(엔딩)까지의 순환 구조(While Loop) 만들기
*   대화 히스토리 관리 (메모리) 기능 추가

### Step 5: 마무리 (Polish)
*   버그 수정 및 프롬프트 개선 (캐릭터 말투 교정 등)
*   `README.md` 작성 및 최종 코드 커밋
