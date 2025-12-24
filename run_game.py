import os
import sys
import uvicorn

def reconfigure_encoding():
    """
    현재 프로세스의 표준 입출력을 UTF-8로 강제 재설정합니다.
    """
    if sys.platform == 'win32':
        import codecs
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
            os.system('chcp 65001 > nul')
        except Exception:
            pass

def main():
    # 1. 환경 변수 확인 및 재실행 로직
    # PYTHONIOENCODING이 utf-8로 설정되지 않았다면, 설정 후 재실행합니다.
    # 이렇게 하면 파이썬 인터프리터가 시작될 때부터 UTF-8을 사용하게 됩니다.
    if os.environ.get("PYTHONIOENCODING") != "utf-8":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["PYTHONUTF8"] = "1"
        
        # 현재 스크립트 재실행
        # sys.executable: 파이썬 인터프리터 경로
        # sys.argv: 현재 스크립트 실행 인자
        print("Set encoding to UTF-8 and restart...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return

    # 2. (안전을 위해) 코드 내에서도 스트림 재설정
    reconfigure_encoding()

    # 3. 이제 안전하게 출력 가능
    print("🚀 게임 서버를 시작합니다... (UTF-8 Mode)")

    # 4. 서버 실행
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
