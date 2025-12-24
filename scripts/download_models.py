#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 모델 다운로드 스크립트
API를 통해 필수 모델을 다운로드합니다.
"""

import urllib.request
import json
import sys
import time

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_server():
    """Ollama 서버 연결 확인"""
    try:
        with urllib.request.urlopen("http://localhost:11434/", timeout=5) as response:
            return response.status == 200
    except:
        return False

def pull_model(model_name):
    """
    Ollama API를 통해 모델 다운로드
    
    Args:
        model_name: 다운로드할 모델 이름
    
    Returns:
        bool: 성공 여부
    """
    print(f"\n{'='*60}")
    print(f"📥 {model_name} 모델 다운로드 시작...")
    print(f"{'='*60}")
    
    url = "http://localhost:11434/api/pull"
    data = json.dumps({"name": model_name}).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=None) as response:
            print(f"⏳ 다운로드 중... (시간이 걸릴 수 있습니다)")
            
            # 스트리밍 응답 처리
            for line in response:
                try:
                    status = json.loads(line.decode('utf-8'))
                    
                    # 진행 상황 표시
                    if 'status' in status:
                        status_msg = status['status']
                        
                        # 다운로드 진행률 표시
                        if 'completed' in status and 'total' in status:
                            completed = status['completed']
                            total = status['total']
                            if total > 0:
                                percent = (completed / total) * 100
                                mb_completed = completed / (1024 * 1024)
                                mb_total = total / (1024 * 1024)
                                print(f"   {status_msg}: {mb_completed:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)", end='\r')
                        else:
                            print(f"   {status_msg}")
                    
                    # 완료 확인
                    if status.get('status') == 'success':
                        print(f"\n✅ {model_name} 다운로드 완료!")
                        return True
                        
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"\n⚠️ 상태 파싱 오류: {e}")
                    continue
        
        return True
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP 오류 발생: {e.code} {e.reason}")
        print(f"   상세: {e.read().decode('utf-8', errors='ignore')}")
        return False
        
    except urllib.error.URLError as e:
        print(f"\n❌ 연결 오류: {e.reason}")
        print(f"   Ollama 서버가 실행 중인지 확인하세요.")
        return False
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_model_exists(model_name):
    """모델이 이미 설치되어 있는지 확인"""
    try:
        url = "http://localhost:11434/api/tags"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = [model['name'] for model in data.get('models', [])]
            
            # 부분 일치 확인 (예: llama3.1:8b도 llama3.1로 인식)
            for installed in models:
                if model_name in installed:
                    return True, installed
            return False, None
    except:
        return False, None

def main():
    print("🚀 Ollama 모델 다운로드 도구")
    print("="*60)
    
    # 1. 서버 확인
    print("\n1️⃣ Ollama 서버 연결 확인 중...")
    if not check_server():
        print("❌ Ollama 서버에 연결할 수 없습니다.")
        print("   해결 방법:")
        print("   1. Ollama가 설치되어 있는지 확인")
        print("   2. 터미널에서 'ollama serve' 실행")
        print("   3. http://localhost:11434 접속 확인")
        sys.exit(1)
    
    print("✅ Ollama 서버 연결 성공")
    
    # 2. 필수 모델 목록
    required_models = [
        "llama3.1",
        "nomic-embed-text"
    ]
    
    # 3. 각 모델 다운로드
    results = {}
    
    for model_name in required_models:
        print(f"\n2️⃣ {model_name} 확인 중...")
        
        # 이미 설치되어 있는지 확인
        exists, installed_name = check_model_exists(model_name)
        if exists:
            print(f"✅ {model_name}은(는) 이미 설치되어 있습니다: {installed_name}")
            results[model_name] = True
            continue
        
        # 다운로드 시도
        print(f"📥 {model_name} 다운로드 필요")
        success = pull_model(model_name)
        results[model_name] = success
        
        if not success:
            print(f"\n⚠️ {model_name} 다운로드 실패")
            print(f"   수동으로 다운로드하려면:")
            print(f"   ollama pull {model_name}")
    
    # 4. 최종 결과
    print("\n" + "="*60)
    print("📊 다운로드 결과:")
    print("="*60)
    
    all_success = True
    for model_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {model_name:<20} {status}")
        if not success:
            all_success = False
    
    print("="*60)
    
    if all_success:
        print("\n🎉 모든 모델 다운로드 완료!")
        print("   이제 게임을 실행할 수 있습니다:")
        print("   python main.py")
    else:
        print("\n⚠️ 일부 모델 다운로드 실패")
        print("   실패한 모델을 수동으로 다운로드해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 다운로드를 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
