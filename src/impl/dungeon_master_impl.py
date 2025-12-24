from typing import List, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.dungeon_master import DungeonMaster
from src.core.game_state import GameState
from src.impl.persona_variants import get_persona_manager

class DungeonMasterImpl(DungeonMaster):
    def __init__(self, model_name: str = "llama3.1:8b-instruct-q4_K_M", game_state: Optional[GameState] = None, persona_type: str = "classic"):
        self.llm = ChatOllama(model=model_name, temperature=0.7)
        self.persona_manager = get_persona_manager()
        self.current_persona = persona_type
        self.system_prompt = self.persona_manager.get_persona(persona_type)
        self.game_state = game_state
        self.conversation_history: List[dict] = []

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
        # Context formatting
        context_str = "\n".join(context) if context else "원작 콩쥐팥쥐 이야기를 참고하세요."
        
        # Add game state information if available
        state_info = ""
        if self.game_state:
            ending = self.game_state.determine_ending()
            score = self.game_state.get_reboot_score()
            state_info = f"\n\n[게임 상태] 리부트 점수: {score}/100, 현재 경로: {ending.value}"
        
        # Add conversation history context (last 3 turns)
        history_str = ""
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]
            history_str = "\n\n[최근 대화 내역]\n"
            for turn in recent_history:
                history_str += f"플레이어: {turn['user']}\n던전마스터: {turn['ai']}\n"
        
        # Construct messages
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""배경 지식:
{context_str}
{state_info}
{history_str}

플레이어의 행동: {user_input}

위 정보를 바탕으로 이야기를 계속 이어가세요. 플레이어의 선택을 존중하되, 캐릭터의 성격은 원작을 유지하세요.
답변은 한국어로 하고, 생동감 있게 서술하세요.""")
        ]
        
        response = self.llm.invoke(messages)
        
        # Record in conversation history
        self.conversation_history.append({
            "user": user_input,
            "ai": response.content
        })
        
        return response.content
