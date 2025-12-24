import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

candidates = [
    "gemini-2.0-flash-exp",
    "gemini-exp-1206",
    "gemini-2.5-pro",
    "gemini-pro-latest",
    "gemini-2.0-flash-001"
]

print("Searching for a working model (Quota Check)...")

for model_name in candidates:
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello", request_options={"timeout": 10})
        print(f"SUCCESS! [OK]")
        print(f"\n>>> FOUND WORKING MODEL: {model_name} <<<")
        break
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
             print("FAILED [429 Quota Exceeded]")
        elif "404" in error_msg:
             print("FAILED [404 Not Found]")
        else:
             print(f"FAILED [{error_msg[:50]}...]")
    time.sleep(1) # Be nice to the API
