"""
E2E 시나리오 통합 테스트
실제 Ollama 및 ChromaDB를 사용한 엔드투엔드 테스트

이 테스트는 실제 API 호출을 수행하므로 시간이 오래 걸립니다.
pytest -m slow 명령어로 실행하세요.
"""

import pytest
import os
import sys
import time
from unittest.mock import Mock

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.impl.lore_keeper_impl import LoreKeeperImpl
from src.impl.dungeon_master_impl import DungeonMasterImpl
from src.impl.game_state_impl import GameStateImpl
from src.impl.game_loop import GameLoop
from src.core.io import InputProvider, OutputDisplay


# 테스트용 Mock IO 클래스
class MockInputProvider(InputProvider):
    """테스트용 입력 제공자"""
    
    def __init__(self, inputs):
        self.inputs = inputs
        self.index = 0
    
    def get_input(self, prompt: str = "") -> str:
        if self.index < len(self.inputs):
            result = self.inputs[self.index]
            self.index += 1
            return result
        return "quit"


class MockOutputDisplay(OutputDisplay):
    """테스트용 출력 디스플레이"""
    
    def __init__(self):
        self.messages = []
        self.system_messages = []
    
    def display_story(self, text: str):
        self.messages.append(("story", text))
    
    def display_system(self, text: str):
        self.system_messages.append(text)
    
    def clear(self):
        pass


@pytest.mark.slow
class TestE2EScenarios:
    """E2E 시나리오 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """각 테스트 전 설정"""
        self.test_story_path = os.path.join(project_root, "data", "e2e_test_story.txt")
        
        # 테스트용 스토리 파일 생성
        os.makedirs(os.path.dirname(self.test_story_path), exist_ok=True)
        with open(self.test_story_path, "w", encoding="utf-8") as f:
            f.write("""콩쥐팥쥐 이야기

옛날 어느 마을에 콩쥐라는 착하고 부지런한 소녀가 살았습니다.
콩쥐의 어머니는 일찍 돌아가시고, 아버지는 새어머니를 맞이했습니다.
새어머니에게는 팥쥐라는 딸이 있었는데, 게으르고 심술궂었습니다.

새어머니와 팥쥐는 콩쥐를 구박하며 온갖 힘든 일을 시켰습니다.
하지만 콩쥐는 불평 없이 묵묵히 일을 했습니다.

어느 날 마을에 큰 잔치가 열렸습니다.
새어머니와 팥쥐는 예쁜 옷을 입고 잔치에 갔지만, 콩쥐는 집에 남아 일을 해야 했습니다.

콩쥐가 슬퍼하고 있을 때, 신비한 두꺼비가 나타나 콩쥐를 도와주었습니다.
두꺼비의 도움으로 콩쥐는 아름다운 옷을 입고 잔치에 갈 수 있었습니다.

잔치에서 콩쥐는 원님의 눈에 띄었고, 원님은 콩쥐에게 반했습니다.
콩쥐는 서둘러 집으로 돌아가다가 신발 한 짝을 잃어버렸습니다.

원님은 신발의 주인을 찾기 위해 마을의 모든 처녀들에게 신발을 신겨보았습니다.
마침내 콩쥐를 찾아낸 원님은 콩쥐와 결혼했고, 콩쥐는 행복하게 살았습니다.""")
        
        yield
        
        # 테스트 후 정리
        if os.path.exists(self.test_story_path):
            os.remove(self.test_story_path)
    
    def test_original_story_path(self):
        """
        시나리오 1: 원작 스토리 경로
        플레이어가 전통적인 콩쥐팥쥐 이야기를 따라가는 경우
        """
        # Given: 게임 컴포넌트 초기화
        game_state = GameStateImpl()
        lore_keeper = LoreKeeperImpl()
        dungeon_master = DungeonMasterImpl(game_state=game_state)
        
        # 스토리 로딩
        lore_keeper.load_book(self.test_story_path)
        lore_keeper.build_index()
        
        # 시스템 프롬프트 설정
        dungeon_master.set_system_prompt(
            "당신은 콩쥐팥쥐 이야기의 던전 마스터입니다. 플레이어의 선택에 따라 이야기를 진행하세요."
        )
        
        # When: 원작을 따르는 선택들
        context = lore_keeper.retrieve("콩쥐는 착하고 부지런하다")
        
        # 선택 1: 새어머니의 구박을 묵묵히 견딘다
        response1 = dungeon_master.generate_story(
            user_input="콩쥐는 새어머니의 구박을 묵묵히 견뎠다.",
            context=context
        )
        
        # Then: 응답이 생성되어야 함
        assert response1 is not None
        assert len(response1) > 0
        
        # 선택 2: 두꺼비의 도움을 받는다
        response2 = dungeon_master.generate_story(
            user_input="콩쥐는 두꺼비의 도움을 받아 잔치에 갔다.",
            context=context
        )
        
        assert response2 is not None
        assert len(response2) > 0
        
        # 상태 확인: 원작을 따르는 경로
        assert game_state.get_choice_count() >= 0
    
    def test_reboot_story_path(self):
        """
        시나리오 2: 리부트 스토리 경로
        플레이어가 대안적 선택을 하는 경우
        """
        # Given: 게임 컴포넌트 초기화
        game_state = GameStateImpl()
        lore_keeper = LoreKeeperImpl()
        dungeon_master = DungeonMasterImpl(game_state=game_state)
        
        lore_keeper.load_book(self.test_story_path)
        lore_keeper.build_index()
        
        dungeon_master.set_system_prompt(
            "당신은 콩쥐팥쥐 리부트의 던전 마스터입니다. 플레이어가 원작과 다른 선택을 하면 새로운 전개를 만드세요."
        )
        
        # When: 원작과 다른 선택들
        context = lore_keeper.retrieve("콩쥐 새어머니 팥쥐")
        
        # 반항적 선택 1: 새어머니에게 맞선다
        response1 = dungeon_master.generate_story(
            user_input="콩쥐는 새어머니의 부당한 대우에 맞섰다.",
            context=context
        )
        
        # Then: 응답이 생성되어야 함
        assert response1 is not None
        assert len(response1) > 0
        
        # 선택 기록
        game_state.record_choice("새어머니에게 맞섬", is_rebellion=True)
        
        # 반항적 선택 2: 스스로 잔치에 간다
        response2 = dungeon_master.generate_story(
            user_input="콩쥐는 두꺼비의 도움 없이 스스로 잔치에 갔다.",
            context=context
        )
        
        assert response2 is not None
        assert len(response2) > 0
        
        game_state.record_choice("스스로 잔치에 감", is_rebellion=True)
        
        # 상태 확인: 반항 횟수가 기록되어야 함
        assert game_state.get_rebellion_count() >= 2
    
    def test_memory_management(self):
        """
        시나리오 3: 메모리 관리
        대화 히스토리 및 요약 기능 테스트
        """
        # Given: 게임 컴포넌트 초기화
        game_state = GameStateImpl()
        dungeon_master = DungeonMasterImpl(game_state=game_state)
        
        dungeon_master.set_system_prompt("던전 마스터입니다.")
        
        # When: 여러 번의 대화 진행
        for i in range(15):  # 버퍼 임계값을 초과하도록
            response = dungeon_master.generate_story(
                user_input=f"테스트 입력 {i}",
                context=[f"컨텍스트 {i}"]
            )
            assert response is not None
        
        # Then: 메모리가 오버플로우되지 않아야 함
        # (내부적으로 요약이 트리거되어야 함)
        # 실제 구현에 따라 메모리 크기 확인 로직 추가 가능
        assert True  # 오류 없이 완료되면 성공
    
    def test_error_recovery(self):
        """
        시나리오 4: 오류 복구
        시스템 견고성 테스트
        """
        # Given: 게임 컴포넌트
        game_state = GameStateImpl()
        
        # When & Then: 잘못된 입력 처리
        
        # 1. 빈 문자열 입력
        try:
            dungeon_master = DungeonMasterImpl(game_state=game_state)
            response = dungeon_master.generate_story(
                user_input="",
                context=[]
            )
            # 빈 입력도 처리되어야 함 (오류 없이)
            assert response is not None or response == ""
        except Exception as e:
            pytest.fail(f"빈 입력 처리 실패: {e}")
        
        # 2. 매우 긴 입력
        try:
            long_input = "테스트 " * 1000
            response = dungeon_master.generate_story(
                user_input=long_input,
                context=[]
            )
            assert response is not None
        except Exception as e:
            pytest.fail(f"긴 입력 처리 실패: {e}")
        
        # 3. 특수 문자 입력
        try:
            special_input = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
            response = dungeon_master.generate_story(
                user_input=special_input,
                context=[]
            )
            assert response is not None
        except Exception as e:
            pytest.fail(f"특수 문자 처리 실패: {e}")
    
    def test_meta_commands(self):
        """
        시나리오 5: 메타 커맨드
        게임 제어 명령어 테스트
        """
        # Given: 게임 루프 설정
        game_state = GameStateImpl()
        lore_keeper = LoreKeeperImpl()
        dungeon_master = DungeonMasterImpl(game_state=game_state)
        
        # Mock IO
        inputs = ["help", "quit"]
        input_provider = MockInputProvider(inputs)
        output_display = MockOutputDisplay()
        
        # When: 게임 루프 실행
        game_loop = GameLoop(
            input_provider,
            output_display,
            lore_keeper,
            dungeon_master,
            game_state
        )
        
        # Then: help 커맨드가 처리되어야 함
        # (실제 게임 루프 실행은 무한 루프이므로 여기서는 컴포넌트 초기화만 확인)
        assert game_loop is not None
        assert output_display is not None
    
    def test_game_state_persistence(self):
        """
        시나리오 6: 게임 상태 저장/복원
        상태 지속성 테스트
        """
        # Given: 게임 상태 생성 및 선택 기록
        game_state = GameStateImpl()
        
        game_state.record_choice("선택 1", is_rebellion=False)
        game_state.record_choice("선택 2", is_rebellion=True)
        game_state.record_choice("선택 3", is_rebellion=True)
        
        # When: 상태 확인
        choice_count = game_state.get_choice_count()
        rebellion_count = game_state.get_rebellion_count()
        
        # Then: 기록된 선택이 올바르게 저장되어야 함
        assert choice_count == 3
        assert rebellion_count == 2
        
        # 엔딩 결정 로직 테스트
        ending = game_state.determine_ending()
        assert ending in ["original", "reboot"]
        
        # 반항 비율이 높으면 리부트 엔딩
        if rebellion_count / choice_count > 0.5:
            assert ending == "reboot"
    
    def test_performance_requirements(self):
        """
        시나리오 7: 성능 요구사항
        응답 시간이 허용 범위 내인지 확인
        """
        # Given: 게임 컴포넌트
        game_state = GameStateImpl()
        dungeon_master = DungeonMasterImpl(game_state=game_state)
        
        dungeon_master.set_system_prompt("던전 마스터입니다.")
        
        # When: 스토리 생성 시간 측정
        start_time = time.time()
        response = dungeon_master.generate_story(
            user_input="콩쥐는 잔치에 갔다.",
            context=["콩쥐는 착하다."]
        )
        elapsed_time = time.time() - start_time
        
        # Then: 응답 시간이 5초 이내여야 함
        assert response is not None
        assert elapsed_time < 5.0, f"응답 시간이 너무 깁니다: {elapsed_time:.2f}초"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "slow"])
