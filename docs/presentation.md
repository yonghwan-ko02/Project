---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
style: |
  section {
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
  }
  h1 {
    color: #2c3e50;
  }
  h2 {
    color: #e67e22;
  }
  strong {
    color: #e74c3c;
  }

---

# 전래동화 리부트
## 콩쥐의 선택

### Product Requirements Document Overview

---

## 1. 프로젝트 개요 (Overview)

### 🎯 목표 (Goal)
*   **전래동화 《콩쥐팥쥐》 기반 텍스트 어드벤처 게임**
*   주인공 '콩쥐'가 되어 원작과 다른 선택을 통해 **새로운 결말** 창조
*   사용자의 상상력에 따라 전개가 변화하는 **인터랙티브 스토리텔링**

### 💡 핵심 컨셉 (Concept)
*   **"밑 빠진 독에 물 붓기를 거부한다면?"**
*   원작의 권선징악 구조 비틀기 (Twist)
*   원작 캐릭터 페르소나 유지 + 사용자 자유도 부여

---

## 2. 제약 조건 (Constraints)

### 💻 로컬 환경 (Local Environment)
*   인터넷 연결 없이 **개인 노트북(Local Host)**에서 완벽 구동

### 💸 비용 0원 (Zero Cost)
*   서버 비용/API 사용료 **Zero**
*   100% 오픈소스 및 로컬 모델 사용

### 🛠️ 유지보수 최소화 (Minimal Maintenance)
*   복잡한 DB 관리 없이 **파일 기반 구조** 지향

---

## 3. 기술 스택 (Tech Stack)

| 구분 | 도구 (Tool) | 선정 이유 |
| :--- | :--- | :--- |
| **LLM** | **Ollama** (Llama-3.1-8b) | 로컬 구동 가능, 비용 0원, 준수한 한국어 성능 |
| **Vector DB** | **ChromaDB** | 파일 기반 임베딩 DB, 유지보수 용이 |
| **Framework** | **LangChain** | LLM 연동 및 RAG 파이프라인 표준 |
| **UI** | **Python Terminal** | 텍스트 생성 집중, GUI 리소스 배제 |

---

## 4. 데이터 구조 (Data Structure)

### 📚 원본 데이터 (Source)
*   저작권 만료된 《콩쥐팥쥐》 원문 텍스트 (`.txt`)

### 🗂️ 벡터 DB 스키마 (Metadata)
*   `source`: 출처 (예: "콩쥐팥쥐")
*   `type`: `event`, `persona`, `background`
*   `character`: 관련 등장인물 (예: `["팥쥐엄마", "콩쥐"]`)
*   `emotion`: 텍스트 감정 (예: `unfair`, `sad`)

> **RAG 전략**: 캐릭터 등장 시 `type: persona`로 검색하여 일관된 말투 유지

---

## 5. 핵심 기능 (Functional Requirements)

### 🧙‍♂️ LoreKeeper (지식 관리자)
*   데이터 로딩 및 청킹(Chunking)
*   임베딩 및 ChromaDB 저장
*   RAG 검색 수행

### 🎲 DungeonMaster (게임 마스터 AI)
*   스토리 텔링 및 인과관계 처리
*   **TRPG 마스터** 페르소나 롤플레잉

### 🎮 GameLoop (메인 실행기)
*   턴제 텍스트 I/O 처리
*   **Context Window 관리**: 최근 3턴 유지 + 이전 대화 요약

---

## 6. 사용자 흐름 (User Flow)

1.  **초기화 (Init)**: DB 로딩 (최초 임베딩)
2.  **오프닝**: "밑 빠진 독에 물 붓기" 씬 (두꺼비 등장)
3.  **입력 (Input)**: 사용자 행동 선택/입력 (예: "두꺼비를 발로 찬다")
4.  **처리 (Process)**:
    *   (LoreKeeper) 캐릭터 성격 검색
    *   (DungeonMaster) 상황 판단 및 스토리 생성
5.  **출력 (Output)**: 결과 및 다음 위기 제시
6.  **반복**: 엔딩까지 Loop

---

## 7. 기대 효과

*   ✅ **로컬 LLM 기반 인터랙티브 스토리텔링 기술 검증**
*   📊 **플레이어 성향 데이터 확보** (순종적 vs 반항적)

---

# 감사합니다
## Q & A
