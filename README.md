# 🎭# 🎮 전래동화 리부트: 콩쥐의 선택 (Kongjwi's Reboot)

[![Play Now](https://img.shields.io/badge/Play_Game-Render-blue?style=for-the-badge&logo=render)](https://ai-interactive-game.onrender.com/)

> **"항아리에 물을 붓지 마라. 깨어라."**
> AI와 함께 써내려가는 신개념 인터랙티브 텍스트 어드벤처 게임

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-success)](https://yonghwan-ko02.github.io/Project/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_1.5_Flash-4285F4.svg)](https://deepmind.google/technologies/gemini/)

---

## 📖 프로젝트 소개

**콩쥐의 선택**은 누구나 알고 있는 전래동화 《콩쥐팥쥐》를 완전히 새롭게 경험할 수 있는 인터랙티브 스토리텔링 게임입니다.

### 🎯 핵심 컨셉

- **원작을 비틀다**: 원작의 권선징악 구조를 거부하고 새로운 선택을 할 수 있습니다
- **AI 기반 스토리텔링**: 로컬 LLM이 당신의 선택에 따라 실시간으로 새로운 이야기를 생성합니다
- **캐릭터 일관성 유지**: 원작 캐릭터의 성격은 유지하되, 스토리는 완전히 달라집니다

### ✨ 특징

- ☁️ **클라우드 실행**: Google Gemini API를 사용하여 저사양 기기에서도 쾌적하게 플레이
- 🏠 **로컬 모드 지원**: Ollama를 사용하여 인터넷 없이 내 컴퓨터의 성능으로도 실행 가능
- 💰 **비용 0원**: Google의 무료 티어(Free Tier)를 사용하여 비용 부담 없음
- 🎮 **무한한 가능성**: 당신의 선택에 따라 매번 다른 결말
- 🧠 **RAG 기술**: 원작 지식을 활용한 일관성 있는 스토리텔링

---

## 🚀 빠른 시작

### 사전 요구사항

- **Python 3.10 이상**
- **Google Gemini API Key** ([발급받기](https://aistudio.google.com/app/apikey))
- (선택) 로컬 모드 사용 시: **Ollama**

### 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/yonghwan-ko02/Project.git
cd Project

# 2. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정 (.env 파일 생성)
# .env 파일을 만들고 아래 내용을 추가하세요:
# GOOGLE_API_KEY=your_api_key_here

# 5. 게임 실행
python web_server.py
```

브라우저에서 `http://localhost:8001`에 접속하여 플레이하세요.

---

## 🏗️ 프로젝트 구조

```
Project/
├── .github/
│   └── workflows/
│       └── marp-to-pages.yml    # GitHub Pages 자동 배포
├── data/
│   └── story.txt                # 콩쥐팥쥐 원본 텍스트
├── docs/                        # 📚 프로젝트 문서
│   ├── Ideation.md              # 초기 아이디어
│   ├── PRD.md                   # 제품 요구사항 명세서
│   ├── TechStack.md             # 기술 스택 설명
│   ├── Task.md                  # 개발 작업 목록
│   ├── Tutorial.md              # 제작 튜토리얼
│   ├── presentation.md          # 프로젝트 발표 자료
│   └── GitHub-Actions-설명.md   # CI/CD 워크플로우 설명
├── src/                         # 💻 소스 코드
│   ├── lore_keeper.py           # RAG & ChromaDB 관리
│   ├── dungeon_master.py        # AI 스토리 생성 엔진
│   └── game_loop.py             # 게임 진행 로직
├── main.py                      # 프로그램 진입점
├── requirements.txt             # Python 의존성
└── README.md                    # 이 문서
```

---

## 🛠️ 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **언어** | Python 3.10+ | AI/ML 생태계 최적화 |
| **LLM** | Google Gemini (1.5 Flash) | 빠르고 정확한 클라우드 AI 모델 (Free Tier) |
| **RAG** | LangChain | AI 워크플로우 구축 프레임워크 |
| **Vector DB** | ChromaDB | 서버리스 임베딩 데이터베이스 |
| **Web** | FastAPI + HTML/JS | 반응형 웹 인터페이스 |

자세한 내용은 [TechStack.md](docs/TechStack.md)를 참고하세요.

---

## 🎮 게임 플레이

### 게임 흐름

1. **오프닝**: 익숙한 "밑 빠진 독에 물 붓기" 장면에서 시작
2. **선택의 순간**: 원작대로 따를 것인가, 거부할 것인가?
3. **AI 반응**: 당신의 선택에 따라 AI가 새로운 스토리 생성
4. **결말**: 원작과 완전히 다른 엔딩을 경험

### 예시 시나리오

```
[내레이션] 두꺼비가 밑 빠진 독을 고쳐주겠다고 합니다.

당신의 선택은?
1. 두꺼비를 도와준다 (원작)
2. 두꺼비를 무시한다
3. 직접 입력: _____

> 두꺼비를 발로 찬다

[AI 생성] 두꺼비는 놀라 도망갑니다. 
은혜를 갚을 기회를 잃은 두꺼비는 다시 돌아오지 않았습니다...
```

---

## 📚 문서

- **[PRD.md](docs/PRD.md)**: 제품 요구사항 명세서 - 프로젝트의 목표와 기능 정의
- **[Tutorial.md](docs/Tutorial.md)**: 단계별 제작 가이드
- **[Task.md](docs/Task.md)**: 개발 작업 목록 및 진행 상황
- **[GitHub Actions 설명](docs/GitHub-Actions-설명.md)**: CI/CD 워크플로우 이해하기

---

## 🧩 핵심 모듈

### 1. LoreKeeper (지식 관리자)
- 원작 텍스트를 벡터 DB에 저장
- 게임 상황에 맞는 원작 정보 검색 (RAG)
- 캐릭터 페르소나 일관성 유지

### 2. DungeonMaster (게임 마스터 AI)
- 사용자 입력 + 원작 지식 → 새로운 스토리 생성
- 인과관계 처리 및 캐릭터 성격 유지
- TRPG 마스터 역할 수행

### 3. GameLoop (메인 실행기)
- 턴제 텍스트 입출력 처리
- 대화 히스토리 관리 (메모리)
- 컨텍스트 윈도우 최적화

---

## 🎯 개발 로드맵

- [x] 프로젝트 기획 및 문서화
- [x] GitHub 저장소 설정
- [x] GitHub Pages 자동 배포 설정
- [x] 데이터 준비 (story.txt - 120줄, 8개 챕터)
- [x] LoreKeeper 구현 (RAG with retry logic & fallback)
- [x] DungeonMaster 구현 (AI 엔진 with GameState integration)
- [x] GameState 구현 (선택 추적 및 분기 로직)
- [x] GameLoop 구현 (UI/UX with meta commands)
- [x] Logger 구현 (세션 기록)
- [x] 테스트 및 버그 수정 (20/20 tests passing)
- [ ] 실제 Ollama 통합 테스트
- [ ] 최종 배포

**현재 진행 상황**: Phase 6 완료, 통합 테스트 대기 중

자세한 작업 내역은 [Walkthrough](file:///C:/Users/WIN/.gemini/antigravity/brain/8ccb637d-b225-40c7-bc91-563f33b9db26/walkthrough.md)를 참고하세요.

---

## 🆕 새로운 기능

### GameState 시스템
- 플레이어 선택 자동 추적
- 리부트 점수 계산 (0-100)
- 3가지 엔딩 타입 (ORIGINAL/REBOOT/NEUTRAL)

### 메타 명령어
- `help`: 도움말 표시
- `status`: 현재 게임 상태 확인
- `restart`: 게임 재시작
- `quit`: 게임 종료

### 고급 기능
- **에러 처리**: Ollama 연결 실패 시 재시도 (exponential backoff)
- **Fallback 모드**: Vector DB 실패 시 키워드 검색
- **세션 로깅**: JSONL 형식으로 게임 기록 저장
- **Rich UI**: 컬러풀한 터미널 출력 및 로딩 스피너

---

## 🤝 기여하기

이 프로젝트는 학습 목적으로 제작되었습니다. 기여를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 말

- **Ollama**: 로컬 LLM 실행 환경 제공
- **LangChain**: RAG 파이프라인 구축 프레임워크
- **ChromaDB**: 서버리스 벡터 데이터베이스
- **전래동화 《콩쥐팥쥐》**: 영감의 원천

---

## 📧 연락처

프로젝트 관련 문의: [GitHub Issues](https://github.com/yonghwan-ko02/Project/issues)

---

<div align="center">

**Made with ❤️ and 🤖 AI**

[Documentation](docs/) · [Report Bug](https://github.com/yonghwan-ko02/Project/issues) · [Request Feature](https://github.com/yonghwan-ko02/Project/issues)

</div>
