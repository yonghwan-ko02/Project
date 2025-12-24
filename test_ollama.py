import requests
import json

def test_ollama():
    """Ollama API를 통해 모델을 테스트합니다."""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.1:8b-instruct-q4_K_M",
        "prompt": "안녕하세요. 간단한 자기소개를 해주세요.",
        "stream": False
    }
    
    print("Ollama 모델 테스트 시작...")
    print(f"모델: {payload['model']}")
    print(f"질문: {payload['prompt']}\n")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print("응답:")
        print(result.get('response', '응답 없음'))
        print(f"\n생성 시간: {result.get('total_duration', 0) / 1e9:.2f}초")
        print("✅ 테스트 성공!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ollama 서버에 연결할 수 없습니다.")
        print("Ollama 서버가 실행 중인지 확인하세요.")
        print("실행 명령: ollama serve")
        
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_ollama()
