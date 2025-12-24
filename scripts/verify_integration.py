#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 테스트 스크립트 (Integration Test)
실제 Ollama 및 ChromaDB 연동 상태를 점검합니다.

개선사항:
- 성능 메트릭 추가 (응답 시간 측정)
- 상세한 로깅 출력 (타임스탬프 포함)
- ChromaDB 정리 기능
- 임베딩 모델 가용성 확인
"""

import os
import sys
import time
import urllib.request
import shutil
import json
from datetime import datetime

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# 프로젝트 루트 경로를 sys.path에 추가하여 src 모듈을 찾을 수 있게 함
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

try:
    from src.impl.lore_keeper_impl import LoreKeeperImpl
    from src.impl.dungeon_master_impl import DungeonMasterImpl
    from src.impl.game_state_impl import GameStateImpl
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("가상환경이 활성화되어 있는지, 프로젝트 루트 구조가 올바른지 확인해주세요.")
    sys.exit(1)

# 성능 메트릭 저장
performance_metrics = {}

def log_with_timestamp(message):
    """타임스탬프와 함께 로그 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def check_ollama_server():
    """Ollama 서버가 실행 중인지 확인"""
    log_with_timestamp("🔍 1. Ollama 서버 연결 확인 중...")
    url = "http://localhost:11434/"
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            elapsed = time.time() - start_time
            if response.status == 200:
                log_with_timestamp(f"   ✅ Ollama 서버가 실행 중입니다. (응답 시간: {elapsed:.3f}초)")
                performance_metrics['ollama_connection'] = elapsed
                return True
    except Exception as e:
        log_with_timestamp(f"   ❌ Ollama 서버에 연결할 수 없습니다: {e}")
        log_with_timestamp("   💡 터미널에서 `ollama serve`를 실행했는지 확인하세요.")
        return False
    return False

def check_embedding_model():
    """임베딩 모델 가용성 확인"""
    log_with_timestamp("\n🔍 2. 임베딩 모델 가용성 확인 중...")
    
    try:
        # Ollama API를 통해 모델 목록 확인
        url = "http://localhost:11434/api/tags"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = [model['name'] for model in data.get('models', [])]
            
            # nomic-embed-text 모델 확인
            embedding_models = [m for m in models if 'embed' in m.lower()]
            
            if embedding_models:
                log_with_timestamp(f"   ✅ 임베딩 모델 발견: {', '.join(embedding_models)}")
                return True
            else:
                log_with_timestamp("   ⚠️ 임베딩 모델을 찾을 수 없습니다.")
                log_with_timestamp("   💡 `ollama pull nomic-embed-text` 명령어로 모델을 다운로드하세요.")
                return False
    except Exception as e:
        log_with_timestamp(f"   ⚠️ 모델 확인 실패: {e}")
        return False

def test_lore_keeper_integration():
    """LoreKeeper (ChromaDB + Embedding) 통합 테스트"""
    log_with_timestamp("\n📚 3. LoreKeeper (RAG & ChromaDB) 테스트 중...")
    
    test_db_path = os.path.join(project_root, "chroma_db_test")
    test_file_path = os.path.join(project_root, "data", "integration_test.txt")
    
    # 테스트용 데이터 생성
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("콩쥐는 마음씨가 착하고 부지런한 소녀입니다.\n팥쥐는 게으르고 심술궂습니다.")

    try:
        # LoreKeeper 초기화
        log_with_timestamp("   - LoreKeeper 초기화 중...")
        lore_keeper = LoreKeeperImpl()
        
        # 텍스트 파일 로딩
        log_with_timestamp("   - 텍스트 파일 로딩 및 청킹...")
        start_time = time.time()
        lore_keeper.load_book(test_file_path)
        load_time = time.time() - start_time
        performance_metrics['lore_keeper_load'] = load_time
        log_with_timestamp(f"   ⏱️  로딩 완료 ({load_time:.3f}초)")
        
        # 벡터 인덱스 생성
        log_with_timestamp("   - 벡터 인덱스 생성 (임베딩)...")
        start_time = time.time()
        lore_keeper.build_index()
        index_time = time.time() - start_time
        performance_metrics['lore_keeper_index'] = index_time
        log_with_timestamp(f"   ⏱️  인덱싱 완료 ({index_time:.3f}초)")
        
        # 검색 테스트
        log_with_timestamp("   - 검색(Retrieve) 테스트...")
        query = "콩쥐의 성격은?"
        start_time = time.time()
        results = lore_keeper.retrieve(query)
        retrieve_time = time.time() - start_time
        performance_metrics['lore_keeper_retrieve'] = retrieve_time
        
        if results and len(results) > 0:
            log_with_timestamp(f"   ✅ 검색 성공 ({retrieve_time:.3f}초)")
            log_with_timestamp(f"   📝 쿼리: '{query}'")
            log_with_timestamp(f"   📝 결과: '{results[0].strip()}'")
            return True
        else:
            log_with_timestamp("   ⚠️ 검색 결과가 비어있습니다.")
            return False
            
    except Exception as e:
        log_with_timestamp(f"   ❌ LoreKeeper 테스트 실패: {e}")
        import traceback
        log_with_timestamp(f"   상세 오류:\n{traceback.format_exc()}")
        return False
    finally:
        # 테스트 파일 정리
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            log_with_timestamp("   🧹 테스트 파일 정리 완료")

def test_dungeon_master_integration():
    """DungeonMaster (LLM Generation) 통합 테스트"""
    log_with_timestamp("\n🧠 4. DungeonMaster (LLM) 테스트 중...")
    
    try:
        log_with_timestamp("   - DungeonMaster 초기화 중...")
        game_state = GameStateImpl()
        dm = DungeonMasterImpl(game_state=game_state)
        
        log_with_timestamp("   - 스토리 생성 요청 (Llama 3.1)...")
        start_time = time.time()
        response = dm.generate_story(
            user_input="콩쥐는 팥쥐에게 인사를 건넸다.",
            context=["콩쥐는 착하다.", "팥쥐는 심술궂다."]
        )
        generation_time = time.time() - start_time
        performance_metrics['dungeon_master_generate'] = generation_time
        
        if response:
            log_with_timestamp(f"   ✅ 생성 성공 ({generation_time:.3f}초)")
            log_with_timestamp(f"   📝 응답 길이: {len(response)}자")
            log_with_timestamp(f"   📝 응답 미리보기: {response[:80]}...")
            
            # 성능 경고
            if generation_time > 5.0:
                log_with_timestamp(f"   ⚠️  응답 시간이 5초를 초과했습니다 ({generation_time:.3f}초)")
            
            return True
        else:
            log_with_timestamp("   ❌ 응답이 비어있습니다.")
            return False
    except Exception as e:
        log_with_timestamp(f"   ❌ DungeonMaster 테스트 실패: {e}")
        log_with_timestamp("   💡 `ollama pull llama3.1` 명령어로 모델을 다운로드했는지 확인하세요.")
        import traceback
        log_with_timestamp(f"   상세 오류:\n{traceback.format_exc()}")
        return False

def cleanup_test_chromadb():
    """테스트용 ChromaDB 정리"""
    log_with_timestamp("\n🧹 5. ChromaDB 테스트 데이터 정리 중...")
    
    test_db_path = os.path.join(project_root, "chroma_db_test")
    
    try:
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
            log_with_timestamp(f"   ✅ 테스트 DB 삭제 완료: {test_db_path}")
        else:
            log_with_timestamp("   ℹ️  정리할 테스트 DB가 없습니다.")
    except Exception as e:
        log_with_timestamp(f"   ⚠️ DB 정리 실패: {e}")

def print_performance_summary():
    """성능 메트릭 요약 출력"""
    log_with_timestamp("\n📊 성능 메트릭 요약:")
    log_with_timestamp("=" * 60)
    
    for key, value in performance_metrics.items():
        status = "✅" if value < 5.0 else "⚠️"
        log_with_timestamp(f"   {status} {key}: {value:.3f}초")
    
    total_time = sum(performance_metrics.values())
    log_with_timestamp(f"\n   📈 총 실행 시간: {total_time:.3f}초")
    log_with_timestamp("=" * 60)

def main():
    print("=" * 60)
    print("🚀 전래동화 리부트: 통합 테스트 (Integration Test)")
    print("=" * 60)
    
    overall_start = time.time()
    
    # 1. Ollama 서버 확인
    if not check_ollama_server():
        sys.exit(1)
    
    # 2. 임베딩 모델 확인
    check_embedding_model()
    
    # 3. LoreKeeper 테스트
    lk_result = test_lore_keeper_integration()
    
    # 4. DungeonMaster 테스트
    dm_result = test_dungeon_master_integration()
    
    # 5. ChromaDB 정리
    cleanup_test_chromadb()
    
    # 6. 성능 요약
    print_performance_summary()
    
    # 최종 결과
    overall_time = time.time() - overall_start
    print("\n" + "=" * 60)
    if lk_result and dm_result:
        log_with_timestamp("🎉 모든 통합 테스트를 통과했습니다! 시스템이 정상 작동합니다.")
    else:
        log_with_timestamp("⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
    log_with_timestamp(f"⏱️  전체 테스트 실행 시간: {overall_time:.3f}초")
    print("=" * 60)

if __name__ == "__main__":
    main()