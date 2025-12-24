import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("No API Key found")
    exit(1)

print("Testing LangChain with gemini-2.5-flash...")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4,
        google_api_key=api_key
    )
    response = llm.invoke([HumanMessage(content="Hello, is 2.5 flash working via LangChain?")])
    print(f"SUCCESS! Response: {response.content}")
except Exception as e:
    print(f"FAILED: {e}")
