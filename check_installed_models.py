import urllib.request
import json

url = "http://localhost:11434/api/tags"
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    models = data.get('models', [])
    
    print("Installed models:")
    for model in models:
        print(f"  - {model['name']}")
