import os
import sys

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    # 콘솔 코드 페이지를 UTF-8로 설정
    os.system('chcp 65001 > nul')

# Add project root to path ensuring modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.impl.lore_keeper_impl import LoreKeeperImpl
from src.impl.dungeon_master_impl import DungeonMasterImpl
from src.impl.game_loop import GameLoop
from src.impl.game_state_impl import GameStateImpl
from src.ui.cli import RichOutputDisplay, ConsoleInputProvider

def main():
    output_display = RichOutputDisplay()
    input_provider = ConsoleInputProvider()
    
    try:
        # 1. Persona Selection
        output_display.display_system("\n🎭 페르소나를 선택하세요:")
        output_display.display_system("1. 📖 classic - 따뜻하고 교육적인 전통 스타일")
        output_display.display_system("2. 🗣️ dialect - 경상도 방언으로 생동감 있는 스타일")
        output_display.display_system("3. 🌑 cynical - 어둡고 풍자적인 현대적 해석")
        output_display.display_system("4. 💻 modern - 현대 언어와 문화 참조")
        output_display.display_system("5. ✨ poetic - 서정적이고 문학적인 표현")
        output_display.display_system("\n번호를 입력하거나 Enter를 눌러 기본값(classic) 사용:")
        
        persona_choice = input_provider.get_input("")
        persona_map = {
            "1": "classic",
            "2": "dialect",
            "3": "cynical",
            "4": "modern",
            "5": "poetic",
            "": "classic"
        }
        selected_persona = persona_map.get(persona_choice, "classic")
        
        # 2. Initialize Components with selected persona
        output_display.display_system(f"✅ {selected_persona} 페르소나가 선택되었습니다!")
        game_state = GameStateImpl()
        lore_keeper = LoreKeeperImpl()
        dungeon_master = DungeonMasterImpl(game_state=game_state, persona_type=selected_persona)
        
        # 3. Data Loading (MVP: Load the default story file)
        story_path = os.path.join(os.path.dirname(__file__), 'data', 'story.txt')
        if os.path.exists(story_path):
            output_display.display_system(f"📚 스토리 로딩 중: {story_path}")
            lore_keeper.load_book(story_path)
            output_display.display_system("🔍 벡터 인덱스 생성 중... (Ollama 임베딩 모델 필요)")
            lore_keeper.build_index()
            output_display.display_system("✅ 지식 베이스 준비 완료!")
        else:
            output_display.display_system("⚠️ Warning: story.txt not found. Starting with empty knowledge.")

        # 3. Setup AI Persona
        system_prompt = """당신은 '전래동화 리부트: 콩쥐의 선택'의 던전 마스터입니다.

**역할:**
- 콩쥐팥쥐 이야기를 배경으로 플레이어의 선택에 따라 이야기를 이끌어갑니다
- 플레이어가 원작과 다른 선택을 하면, 그에 맞는 새로운 전개를 만들어냅니다
- 캐릭터의 성격은 원작을 유지하되, 스토리는 플레이어의 선택을 존중합니다

**스타일:**
- 생동감 있고 몰입감 있는 서술
- 한국 전래동화 특유의 따뜻하면서도 교훈적인 톤
- 플레이어의 행동에 대한 자연스러운 반응과 결과 제시

**중요:**
- 답변은 항상 한국어로 작성
- 너무 길지 않게 (200-300자 정도)
- 플레이어에게 다음 선택의 여지를 남겨둘 것"""
        
        dungeon_master.set_system_prompt(system_prompt)

        # 4. Initialize Game Loop
        game = GameLoop(input_provider, output_display, lore_keeper, dungeon_master, game_state)
        
        # 5. Run
        game.run()
        
    except KeyboardInterrupt:
        output_display.display_system("\n\n⚠️ 게임이 중단되었습니다.")
    except Exception as e:
        output_display.display_system(f"\n\n❌ 오류 발생: {e}")
        output_display.display_system("\n**문제 해결:**")
        output_display.display_system("1. Ollama가 실행 중인지 확인: `ollama serve`")
        output_display.display_system("2. 필요한 모델이 설치되었는지 확인:")
        output_display.display_system("   - `ollama pull llama3.1`")
        output_display.display_system("   - `ollama pull nomic-embed-text`")
        output_display.display_system("3. 의존성이 설치되었는지 확인: `pip install -r requirements.txt`")
        raise

if __name__ == "__main__":
    main()

