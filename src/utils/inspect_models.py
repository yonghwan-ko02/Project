import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

models_to_check = [
    "models/gemini-flash-latest",
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash-lite-preview-02-05",
    "models/gemini-1.5-flash"
]

print(f"{'Model Name':<45} | {'Display Name':<30} | {'Version':<10}")
print("-" * 90)

for m_name in models_to_check:
    try:
        model_info = genai.get_model(m_name)
        print(f"{m_name:<45} | {model_info.display_name:<30} | {model_info.version:<10}")
    except Exception as e:
        print(f"{m_name:<45} | NOT FOUND / ERROR")
