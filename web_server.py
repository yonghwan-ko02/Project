#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 UI용 FastAPI 백엔드
"""

import os
import sys

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.system('chcp 65001 > nul')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.impl.lore_keeper_impl import LoreKeeperImpl
from src.impl.dungeon_master_impl import DungeonMasterImpl
from src.impl.game_state_impl import GameStateImpl

app = FastAPI(title="전래동화 리부트")

# 게임 세션 저장
game_sessions = {}

class GameSession:
    def __init__(self, persona_type: str = "classic"):
        self.game_state = GameStateImpl()
        self.lore_keeper = LoreKeeperImpl()
        self.dungeon_master = DungeonMasterImpl(
            game_state=self.game_state,
            persona_type=persona_type
        )
        self.history = []
        self.turn_count = 0
        self.initialized = False
    
    async def initialize(self):
        """게임 초기화"""
        if not self.initialized:
            # 스토리 로딩
            story_path = os.path.join(os.path.dirname(__file__), 'data', 'story.txt')
            if os.path.exists(story_path):
                self.lore_keeper.load_book(story_path)
                self.lore_keeper.build_index()
            self.initialized = True
    
    async def process_input(self, user_input: str) -> dict:
        """사용자 입력 처리"""
        # 메타 커맨드 처리
        if user_input.lower() == 'help':
            return {
                "type": "system",
                "message": self._get_help_text()
            }
        elif user_input.lower() == 'status':
            return {
                "type": "system",
                "message": self._get_status()
            }
        elif user_input.lower().startswith('persona'):
            return await self._handle_persona_command(user_input)
        
        # 일반 게임 입력 처리
        try:
            # RAG 검색
            context = self.lore_keeper.retrieve(user_input)
            
            # AI 스토리 생성
            story_segment = self.dungeon_master.generate_story(user_input, context)
            
            # 히스토리 저장
            self.history.append({"user": user_input, "ai": story_segment})
            self.turn_count += 1
            
            # 선택 분석 및 기록
            self._analyze_and_record_choice(user_input)
            
            return {
                "type": "story",
                "message": story_segment,
                "turn": self.turn_count
            }
        except Exception as e:
            return {
                "type": "error",
                "message": f"오류 발생: {str(e)}"
            }
    
    def _get_help_text(self) -> str:
        return """
**도움말**

**게임 방법:**
- 자유롭게 행동을 입력하세요
- 당신의 선택에 따라 이야기가 달라집니다

**메타 명령어:**
- help: 이 도움말 표시
- status: 현재 게임 상태 확인
- persona: 페르소나 목록 보기
- persona <type>: 페르소나 변경

**팁:**
- 원작을 따르면 ORIGINAL 엔딩
- 원작과 다른 선택을 하면 REBOOT 엔딩
"""
    
    def _get_status(self) -> str:
        status = self.game_state.get_state_summary()
        persona_desc = self.dungeon_master.get_persona_description()
        return f"""
**게임 상태**

{status}

턴 수: {self.turn_count}
현재 페르소나: {persona_desc}
"""
    
    async def _handle_persona_command(self, command: str) -> dict:
        parts = command.split()
        
        if len(parts) == 1:
            personas = self.dungeon_master.list_available_personas()
            message = "**사용 가능한 페르소나:**\n\n"
            for persona in personas:
                desc = self.dungeon_master.get_persona_description(persona)
                message += f"- {persona}: {desc}\n"
            message += "\n사용법: persona <type> (예: persona dialect)"
            return {"type": "system", "message": message}
        
        elif len(parts) == 2:
            persona_type = parts[1].lower()
            try:
                old_persona = self.dungeon_master.get_current_persona()
                self.dungeon_master.set_persona(persona_type)
                new_desc = self.dungeon_master.get_persona_description()
                return {
                    "type": "system",
                    "message": f"페르소나가 변경되었습니다: {old_persona} → {persona_type}\n{new_desc}"
                }
            except ValueError as e:
                return {"type": "error", "message": str(e)}
        
        return {"type": "error", "message": "잘못된 명령어 형식입니다."}
    
    def _analyze_and_record_choice(self, user_input: str):
        """선택 분석 및 기록"""
        user_input_lower = user_input.lower()
        
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


@app.get("/")
async def read_root():
    """메인 페이지"""
    return FileResponse("web/index.html")


@app.get("/api/personas")
async def get_personas():
    """사용 가능한 페르소나 목록"""
    dm = DungeonMasterImpl()
    personas = dm.list_available_personas()
    return {
        "personas": [
            {
                "id": p,
                "name": p,
                "description": dm.get_persona_description(p)
            }
            for p in personas
        ]
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 엔드포인트"""
    await websocket.accept()
    
    try:
        # 세션 초기화
        if session_id not in game_sessions:
            # 첫 메시지로 페르소나 받기
            data = await websocket.receive_json()
            persona_type = data.get("persona", "classic")
            
            game_sessions[session_id] = GameSession(persona_type)
            await game_sessions[session_id].initialize()
            
            # 환영 메시지
            await websocket.send_json({
                "type": "system",
                "message": f"🎭 전래동화 리부트: 콩쥐의 선택에 오신 것을 환영합니다!\n\n페르소나: {game_sessions[session_id].dungeon_master.get_persona_description()}\n\n이야기를 시작하려면 행동을 입력하세요."
            })
        
        session = game_sessions[session_id]
        
        # 메시지 루프
        while True:
            data = await websocket.receive_json()
            user_input = data.get("message", "")
            
            if not user_input:
                continue
            
            # 사용자 메시지 에코
            await websocket.send_json({
                "type": "user",
                "message": user_input
            })
            
            # 처리 중 표시
            await websocket.send_json({
                "type": "thinking",
                "message": "🤔 던전 마스터가 생각 중..."
            })
            
            # 입력 처리
            response = await session.process_input(user_input)
            
            # 응답 전송
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        if session_id in game_sessions:
            del game_sessions[session_id]
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"오류 발생: {str(e)}"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
