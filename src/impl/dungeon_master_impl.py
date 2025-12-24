import os
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.dungeon_master import DungeonMaster
from src.core.game_state import GameState
from src.impl.persona_variants import get_persona_manager
from dotenv import load_dotenv

load_dotenv()

class DungeonMasterImpl(DungeonMaster):
    def __init__(self, model_name: str = "gemini-2.5-flash", game_state: Optional[GameState] = None, persona_type: str = "classic"):
        # gemini-2.5-flash 사용 (검증된 작동 모델)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
            
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0.4,
            google_api_key=api_key
        )
        self.persona_manager = get_persona_manager()
        self.current_persona = persona_type
        self.system_prompt = self.persona_manager.get_persona(persona_type)
        self.game_state = game_state
        print(f"[INFO] DungeonMaster initialized with {model_name}")
        
        # Memory Management
        self.conversation_history: List[dict] = []  # Short-term memory (Exact turns)
        self.long_term_memory: str = "아직 기록된 킨 역사가 없습니다." # Long-term memory (Summary)

    def set_system_prompt(self, prompt: str) -> None:
        """시스템 프롬프트를 직접 설정 (커스텀 프롬프트용)"""
        self.system_prompt = prompt
        self.current_persona = "custom"
    
    def set_persona(self, persona_type: str) -> None:
        """
        페르소나 타입을 설정하고 시스템 프롬프트 업데이트
        
        Args:
            persona_type: 페르소나 타입 (classic, dialect, cynical, modern, poetic)
        
        Raises:
            ValueError: 유효하지 않은 페르소나 타입인 경우
        """
        self.system_prompt = self.persona_manager.get_persona(persona_type)
        self.current_persona = persona_type
    
    def get_current_persona(self) -> str:
        """현재 설정된 페르소나 타입 반환"""
        return self.current_persona
    
    def list_available_personas(self) -> list:
        """사용 가능한 페르소나 목록 반환"""
        return self.persona_manager.list_personas()
    
    def get_persona_description(self, persona_type: str = None) -> str:
        """페르소나 설명 반환 (타입 미지정 시 현재 페르소나)"""
        target_persona = persona_type if persona_type else self.current_persona
        if target_persona == "custom":
            return "🎨 커스텀 - 사용자 정의 프롬프트"
        return self.persona_manager.get_persona_description(target_persona)

    def generate_story(self, user_input: str, context: List[str]) -> str:
        # 1. Memory Management (Summarize if too long)
        if len(self.conversation_history) > 5:
            self._summarize_old_memories()

        # Context formatting
        context_str = "\n".join(context) if context else "원작 콩쥐팥쥐 이야기를 참고하세요."
        
        # Add game state information if available
        state_info = ""
        scene_info = ""
        if self.game_state:
            ending = self.game_state.determine_ending()
            score = self.game_state.get_reboot_score()
            
            # Scene State Retrieving
            scene_state = self.game_state.get_scene()
            current_chapter = scene_state.get("chapter", "chapter_1_house")
            
            state_info = f"\n\n[게임 상태] 리부트 점수: {score}/100, 현재 경로: {ending.value}"
            scene_info = f"\n[현재 챕터 상황]: {current_chapter}\n이 챕터의 갈등(과제)을 해결하면 다음 챕터로 진행됩니다."

        # Add conversation history context
        history_str = ""
        
        # 1. Long-term Memory (Summary of past events)
        if self.long_term_memory and self.long_term_memory != "아직 기록된 역사가 없습니다.":
            history_str += f"\n\n[지난 이야기 요약]\n{self.long_term_memory}\n"
        
        # 2. Short-term Memory (Recent detailed turns)
        if self.conversation_history:
            history_str += "\n[최근 대화]\n"
            for turn in self.conversation_history:
                history_str += f"플레이어: {turn['user']}\n던전마스터: {turn['ai']}\n"
        
        # Construct messages
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""배경 지식:
{context_str}
{state_info}
{scene_info}
{history_str}

플레이어의 행동: {user_input}

위 정보를 바탕으로 이야기를 계속 이어가세요.
주의사항:
1. 캐릭터 이름은 반드시 원작(콩쥐, 팥쥐, 새어머니 등)을 정확히 따르세요. '콕쥐' 같은 오타를 내지 마세요.
2. 문맥에 맞지 않는 뜬금없는 단어(공룡, 현대 물건 등)를 사용하지 마세요.
3. 한국어 문장을 자연스럽게 구사하세요.
4. **답변 마지막에는 반드시 플레이어가 선택할 수 있는 3가지 행동 예시를 제시하세요.** (번호 매기기 1, 2, 3)
5. **[중요] 하이브리드 스토리 로직 (Strict Problems, Open Solutions)**:
   - **문제의 절대성**: '밑 빠진 독', '섞인 곡식' 등 물리적 제약은 절대적입니다. 단순한 의지만으로는 해결되지 않습니다. (예: "그냥 물을 붓는다" -> "물이 다 샌다" -> 실패)
   - **해결의 유연성**: 
     A. **창의적 해결(Reboot)**: 플레이어가 타당한 물리적 해결책(예: "진흙이나 지푸라기로 구멍을 막는다", "체로 곡식을 거른다")을 제시하면 **성공**으로 처리하고, '똑똑한 콩쥐' 루트로 이야기를 전개하세요.
     B. **고전적 해결(Classic)**: 플레이어가 포기하거나, 실패를 반복하거나, 도움을 요청하면 원작의 조력자(두꺼비, 참새, 선녀)가 등장하여 도와주는 이벤트를 발생시키세요.
6. **[장면 전환 시스템]**:
   - 플레이어의 행동으로 인해 현재 챕터의 갈등이 해소되었다면(과제 완료, 탈출, 등) 답변 맨 마지막에 `[SCENE_RESOLVED]` 태그를 붙이세요.
   - 이 태그는 프로그램이 감지하여 다음 챕터로 넘기는 용도입니다.

답변은 한국어로 하고, 생동감 있게 서술하세요.""")
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        # Check for Scene Resolution Tag
        if "[SCENE_RESOLVED]" in content:
            print(f"[DungeonMaster] Scene Resolution Detected!")
            # Remove tag from display
            content = content.replace("[SCENE_RESOLVED]", "").strip()
            
            # Update State (Transitions)
            if self.game_state:
                # Chapter 1 -> Chapter 2
                current = self.game_state.get_scene().get("chapter")
                if current == "chapter_1_house":
                    self.game_state.update_scene("chapter_2_road", "resolved")
                    content += "\n\n✨ [시스템] 과제를 마치고 집을 나섭니다! 다음 챕터로 이동합니다..."

        # Record in conversation history
        self.conversation_history.append({
            "user": user_input,
            "ai": content
        })
        
        return content

    def _summarize_old_memories(self):
        """오래된 대화 내용을 요약하여 장기 기억으로 이관"""
        # 가장 오래된 2개의 턴을 추출
        old_turns = self.conversation_history[:2]
        self.conversation_history = self.conversation_history[2:]
        
        turns_text = ""
        for turn in old_turns:
            turns_text += f"Play: {turn['user']}\nDM: {turn['ai']}\n"
            
        print(f"[Memory] Summarizing {len(old_turns)} old turns...")
        
        summary_prompt = f"""
현재까지의 이야기 요약:
{self.long_term_memory}

새로 추가된 대화 내용:
{turns_text}

지시사항:
위 '새로 추가된 대화 내용'을 '현재까지의 이야기 요약'에 자연스럽게 통합하여 업데이트된 요약문을 작성하세요.
- 주요 사건, 결정, 아이템 획득 여부를 중심으로 간략히 요약하세요.
- 3문장 이내로 작성하세요.
- 한국어로 작성하세요.
"""
        try:
            summary_response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            self.long_term_memory = summary_response.content
            print(f"[Memory] Summary Updated: {self.long_term_memory}")
        except Exception as e:
            print(f"[Memory] Summarization Failed: {e}")
            # 실패 시 그냥 롤백하지 않고 로그만 남김 (데이터는 날아가지만 치명적이지 않음)

    def generate_prologue(self, context: List[str]) -> str:
        """게임 시작 시 프롤로그 반환 (고정된 상황)"""
        # 사용자 요청: 매번 생성하는 대신 고정된 상황 사용 (속도 및 일관성)
        prologue_text = """[전래동화 리부트: 콩쥐의 선택]

옛날 어느 마을에 마음씨 착한 콩쥐가 살고 있었습니다. 하지만 콩쥐의 어머니가 돌아가시고, 아버지가 새어머니를 맞이하면서 콩쥐의 고된 나날이 시작되었습니다. 새어머니에게는 심술궂은 딸 팥쥐가 있었는데, 두 모녀는 콩쥐를 미워하며 온갖 구박을 일삼았습니다.

어느 날, 마을 원님 댁에서 큰 잔치가 열린다는 소식이 들려왔습니다. 곱게 차려입은 새어머니와 팥쥐는 잔치에 갈 채비를 마쳤습니다. 콩쥐도 잔치에 가고 싶은 마음에 조심스럽게 물었지만, 새어머니는 코웃음을 치며 말했습니다.

"너도 잔치에 가고 싶으냐? 좋다, 하지만 내가 시키는 일을 다 끝내야만 갈 수 있다."

새어머니는 마당에 놓인 큰 독과 쌓여있는 일감을 가리켰습니다.

"첫째, 저 밑 빠진 독에 물을 가득 채워라.
둘째, 저 겨와 쌀을 섞어 놓은 것을 모두 골라내어라.
셋째, 저 삼 한 바구니를 모두 삼아서 베를 짜거라.
우리가 돌아올 때까지 이 일을 다 끝내면, 그때 잔치에 오거라."

새어머니와 팥쥐는 깔깔거리며 대문을 나섰고, 텅 빈 마당에는 절망적인 표정의 콩쥐만 홀로 남겨졌습니다. 눈앞에는 깨진 독과 산더미 같은 일감이 놓여 있습니다.

이때, 콩쥐는 어떻게 해야 할까요?

1. 밑 빠진 독에 물을 채우기 시작한다.
2. 너무 힘들어 포기하고 주저앉아 운다.
3. 새어머니가 시킨 일을 무시하고 몰래 잔치로 향한다."""

        # Record prologue in history
        self.conversation_history.append({
            "user": "[System: Game Start]",
            "ai": prologue_text
        })
        
        return prologue_text
