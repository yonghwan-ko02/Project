from typing import List, Dict, Any
from src.core.io import InputProvider, OutputDisplay
from src.core.lore_keeper import LoreKeeper
from src.core.dungeon_master import DungeonMaster
from src.core.game_state import GameState
from src.utils.logger import Logger

class GameLoop:
    def __init__(self, 
                 input_provider: InputProvider, 
                 output_display: OutputDisplay, 
                 lore_keeper: LoreKeeper, 
                 dungeon_master: DungeonMaster,
                 game_state: GameState,
                 enable_logging: bool = True):
        self.input_provider = input_provider
        self.output_display = output_display
        self.lore_keeper = lore_keeper
        self.dungeon_master = dungeon_master
        self.game_state = game_state
        self.history: List[Dict[str, str]] = []
        self.turn_count = 0
        self.enable_logging = enable_logging
        
        # Initialize logger
        if self.enable_logging:
            self.logger = Logger()
            self.output_display.display_system(f"📝 세션 로그: {self.logger.get_session_file()}")

    def run(self):
        self.output_display.display_system("🎭 전래동화 리부트: 콩쥐의 선택에 오신 것을 환영합니다!")
        
        # Display current persona
        persona_desc = self.dungeon_master.get_persona_description()
        self.output_display.display_system(f"현재 페르소나: {persona_desc}")
        
        self.output_display.display_system("메타 명령어: 'help', 'status', 'persona', 'restart', 'quit'")
        self.output_display.display_system("-" * 50)
        
        # Start Prologue
        self._start_prologue()
        
        while True:
            user_input = self.input_provider.get_input("당신의 선택")
            
            if not user_input:
                continue
                
            # Handle meta commands
            if user_input.lower() == 'quit':
                self.output_display.display_system("게임을 종료합니다. 안녕히 가세요!")
                break
            elif user_input.lower() == 'help':
                self._show_help()
                continue
            elif user_input.lower() == 'status':
                self._show_status()
                continue
            elif user_input.lower() == 'restart':
                self._restart_game()
                continue
            elif user_input.lower().startswith('persona'):
                self._handle_persona_command(user_input)
                continue
            
            # Analyze user input for choice tracking
            self._analyze_and_record_choice(user_input)
            
            # RAG Retrieval
            try:
                context = self.lore_keeper.retrieve(user_input)
            except Exception as e:
                self.output_display.display_system(f"⚠️ 지식 검색 실패: {e}")
                context = []
            
            # AI Generation with loading indicator
            self.output_display.display_system("🤔 던전 마스터가 생각 중...")
            try:
                story_segment = self.dungeon_master.generate_story(user_input, context)
            except Exception as e:
                self.output_display.display_system(f"❌ 스토리 생성 실패: {e}")
                self.output_display.display_system("Ollama가 실행 중인지 확인해주세요.")
                continue
            
            # Display Output
            self.output_display.display(story_segment)
            
            # Update History
            self.history.append({"user": user_input, "ai": story_segment})
            self.turn_count += 1
            
            # Log the turn
            if self.enable_logging:
                metadata = {
                    "turn": self.turn_count,
                    "reboot_score": self.game_state.get_reboot_score(),
                    "ending_type": self.game_state.determine_ending().value
                }
                self.logger.log_turn(user_input, story_segment, metadata)
            
            # Memory management: summarize if history is too long
            if len(self.history) > 10:
                self._summarize_history()
            
        self.output_display.display_system("Game Over.")
    
    def _show_help(self):
        """Display help information"""
        help_text = """
📖 **도움말**

**게임 방법:**
- 자유롭게 행동을 입력하세요 (예: "두꺼비를 도와준다", "밑 빠진 독을 거부한다")
- 당신의 선택에 따라 이야기가 달라집니다

**메타 명령어:**
- `help`: 이 도움말 표시
- `status`: 현재 게임 상태 확인
- `persona`: 페르소나 목록 보기
- `persona <type>`: 페르소나 변경 (classic, dialect, cynical, modern, poetic)
- `restart`: 게임 재시작
- `quit`: 게임 종료

**팁:**
- 원작을 따르면 ORIGINAL 엔딩
- 원작과 다른 선택을 하면 REBOOT 엔딩
- 리부트 점수가 60 이상이면 완전히 새로운 이야기!
        """
        self.output_display.display_system(help_text)
    
    def _show_status(self):
        """Display current game status"""
        status = self.game_state.get_state_summary()
        persona_desc = self.dungeon_master.get_persona_description()
        self.output_display.display_system(
            f"\n📊 **게임 상태**\n{status}\n턴 수: {self.turn_count}\n현재 페르소나: {persona_desc}"
        )
    
    def _restart_game(self):
        """Restart the game"""
        self.history.clear()
        self.turn_count = 0
        # Note: GameState should be recreated by caller, this just clears local state
        self.output_display.display_system("🔄 게임을 재시작하려면 프로그램을 다시 실행해주세요.")
    
    def _handle_persona_command(self, command: str):
        """
        Handle persona meta command
        Usage: 
            - 'persona' : Show available personas
            - 'persona <type>' : Switch to specified persona
        """
        parts = command.split()
        
        if len(parts) == 1:
            # Show available personas
            personas = self.dungeon_master.list_available_personas()
            self.output_display.display_system("\n🎭 **사용 가능한 페르소나:**")
            for persona in personas:
                desc = self.dungeon_master.get_persona_description(persona)
                self.output_display.display_system(f"  - {persona}: {desc}")
            self.output_display.display_system("\n사용법: persona <type> (예: persona dialect)")
        
        elif len(parts) == 2:
            # Switch persona
            persona_type = parts[1].lower()
            try:
                old_persona = self.dungeon_master.get_current_persona()
                self.dungeon_master.set_persona(persona_type)
                new_desc = self.dungeon_master.get_persona_description()
                self.output_display.display_system(
                    f"✨ 페르소나가 변경되었습니다: {old_persona} → {persona_type}\n{new_desc}"
                )
            except ValueError as e:
                self.output_display.display_system(f"❌ 오류: {e}")
        else:
            self.output_display.display_system("❌ 잘못된 명령어 형식입니다. 'persona' 또는 'persona <type>'을 사용하세요.")
    
    def _analyze_and_record_choice(self, user_input: str):
        """
        Analyze user input and record significant choices in GameState.
        This is a simple keyword-based analysis.
        """
        user_input_lower = user_input.lower()
        
        # Check for reboot indicators
        if any(word in user_input_lower for word in ["거부", "거절", "싫어", "안 해", "안해"]):
            if "독" in user_input_lower or "물" in user_input_lower:
                self.game_state.record_choice("refused_impossible_task", True)
            elif "두꺼비" in user_input_lower:
                self.game_state.record_choice("rejected_toad_help", True)
            elif "잔치" in user_input_lower or "결혼" in user_input_lower:
                self.game_state.record_choice("refused_marriage", True)
        
        if any(word in user_input_lower for word in ["대항", "맞서", "항의", "따지"]):
            if "새어머니" in user_input_lower or "계모" in user_input_lower:
                self.game_state.record_choice("confronted_stepmother", True)
        
        if any(word in user_input_lower for word in ["도와", "돕", "협력"]):
            if "팥쥐" in user_input_lower:
                self.game_state.record_choice("helped_patjwi", True)
        
        if any(word in user_input_lower for word in ["떠나", "도망", "탈출"]):
            self.game_state.record_choice("left_home_early", True)
    
    def _summarize_history(self):
        """
        Summarize conversation history to manage context window.
        For now, just keep the last 5 turns.
        """
        if len(self.history) > 5:
            self.history = self.history[-5:]
            self.output_display.display_system("💾 대화 내역이 요약되었습니다.")

    def _start_prologue(self):
        """
        Generate and display the game prologue (intro scene).
        Uses fixed text for instant start.
        """
        self.output_display.display_system("🎬 프롤로그 실행 중...")
        
        try:
            # We assume dungeon_master has generate_prologue method now
            if hasattr(self.dungeon_master, 'generate_prologue'):
                prologue = self.dungeon_master.generate_prologue([])
            else:
                # Fallback
                prologue = self.dungeon_master.generate_story("이야기의 시작", [])
            
            self.output_display.display(f"\n{prologue}\n")
            
            # Log it
            if self.enable_logging:
                self.logger.log_turn("[System: Prologue]", prologue, {"type": "prologue"})
                
        except Exception as e:
            self.output_display.display_system(f"❌ 프롤로그 생성 실패: {e}")

