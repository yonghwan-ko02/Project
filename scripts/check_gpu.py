#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama GPU 사용 확인 및 최적화 스크립트
"""

import urllib.request
import json
import sys
import subprocess

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_gpu_status():
    """nvidia-smi로 GPU 상태 확인"""
    print("🔍 GPU 상태 확인 중...\n")
    
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            info = result.stdout.strip().split(', ')
            print(f"📊 GPU 정보:")
            print(f"  이름: {info[0]}")
            print(f"  총 VRAM: {info[1]}")
            print(f"  사용 중: {info[2]}")
            print(f"  여유: {info[3]}")
            print(f"  사용률: {info[4]}")
            
            # VRAM 여유 공간 확인
            free_mb = int(info[3].replace(' MiB', ''))
            if free_mb < 1000:
                print(f"\n⚠️ VRAM 여유 공간이 부족합니다 ({free_mb}MB)")
                print("  다른 프로그램을 종료하거나 Ollama를 재시작하세요.")
                return False
            else:
                print(f"\n✅ VRAM 여유 공간 충분: {free_mb}MB")
                return True
        else:
            print("⚠️ nvidia-smi 실행 실패")
            return False
            
    except FileNotFoundError:
        print("❌ nvidia-smi를 찾을 수 없습니다. NVIDIA 드라이버가 설치되어 있는지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ GPU 상태 확인 실패: {e}")
        return False

def check_ollama_gpu():
    """Ollama가 GPU를 사용하는지 확인"""
    print("\n🔍 Ollama GPU 사용 확인 중...\n")
    
    try:
        # 간단한 테스트 생성 요청
        url = "http://localhost:11434/api/generate"
        data = json.dumps({
            "model": "llama3.1:8b-instruct-q4_K_M",
            "prompt": "Hello",
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print("📝 테스트 생성 요청 중...")
        import time
        start = time.time()
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            elapsed = time.time() - start
            
            print(f"✅ 응답 시간: {elapsed:.2f}초")
            
            # GPU 사용 여부 판단 (GPU 사용 시 훨씬 빠름)
            if elapsed < 5:
                print("🎮 GPU 가속이 활성화되어 있습니다!")
                return True
            elif elapsed < 15:
                print("⚠️ GPU를 사용하고 있지만 느립니다. VRAM 부족 가능성이 있습니다.")
                return True
            else:
                print("❌ CPU로 실행 중인 것 같습니다. 매우 느립니다.")
                return False
                
    except urllib.error.URLError:
        print("❌ Ollama 서버에 연결할 수 없습니다.")
        return False
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def get_optimization_tips():
    """최적화 팁 제공"""
    print("\n" + "="*60)
    print("💡 성능 최적화 팁")
    print("="*60)
    print("""
1. VRAM 확보:
   - Chrome, Slack 등 GPU 사용 프로그램 종료
   - 불필요한 백그라운드 프로그램 종료

2. Ollama 재시작:
   - 작업 관리자에서 Ollama 프로세스 종료
   - Ollama 다시 시작

3. 모델 언로드:
   - 사용하지 않는 모델 언로드하여 VRAM 확보

4. 더 작은 모델 사용:
   - llama3.1:3b (더 작고 빠름)
   - 대신 품질은 약간 낮아질 수 있음

5. 환경 변수 설정 (이미 적용되어 있을 가능성 높음):
   - OLLAMA_GPU_LAYERS=999 (모든 레이어를 GPU에)
   - OLLAMA_NUM_GPU=1
""")

def main():
    print("🚀 Ollama GPU 최적화 도구")
    print("="*60)
    
    # 1. GPU 상태 확인
    gpu_ok = check_gpu_status()
    
    # 2. Ollama GPU 사용 확인
    ollama_gpu = check_ollama_gpu()
    
    # 3. 결과 및 권장사항
    print("\n" + "="*60)
    print("📊 최종 결과")
    print("="*60)
    
    if gpu_ok and ollama_gpu:
        print("✅ GPU 가속이 정상적으로 작동하고 있습니다!")
        print("   게임 실행 시 빠른 응답을 기대할 수 있습니다.")
    elif ollama_gpu:
        print("⚠️ GPU를 사용하고 있지만 VRAM이 부족할 수 있습니다.")
        print("   다른 프로그램을 종료하면 성능이 향상됩니다.")
    else:
        print("❌ GPU 가속이 제대로 작동하지 않습니다.")
        print("   아래 최적화 팁을 참고하세요.")
    
    # 4. 최적화 팁
    if not (gpu_ok and ollama_gpu):
        get_optimization_tips()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
