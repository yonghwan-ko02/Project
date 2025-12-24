import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("No API Key found")
    exit(1)

genai.configure(api_key=api_key)

print("Searching for a working model...")
working_model = None

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            model_name = m.name
            # Clean up model name if needed (remove 'models/')
            clean_name = model_name.replace("models/", "")
            
            print(f"Testing {clean_name}...", end=" ")
            try:
                model = genai.GenerativeModel(clean_name)
                response = model.generate_content("Hello")
                print(f"SUCCESS! [OK]")
                working_model = clean_name
                break
            except Exception as e:
                print(f"FAILED [X] ({str(e)[:50]}...)")
                
    if working_model:
        print(f"\nFOUND WORKING MODEL: {working_model}")
    else:
        print("\nNO WORKING MODELS FOUND.")

except Exception as e:
    print(f"Fatal error: {e}")
