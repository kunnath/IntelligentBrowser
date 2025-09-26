import asyncio
import os
import requests
from dotenv import load_dotenv
from browser_use import Agent

class DeepSeekOllamaLLM:
    def __init__(self, model="deepseek-r1:8b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    async def ainvoke(self, messages):
        # Convert messages to a simple prompt
        prompt = ""
        if isinstance(messages, list):
            for msg in messages:
                if hasattr(msg, 'content'):
                    prompt += msg.content + "\n"
                elif isinstance(msg, dict):
                    prompt += msg.get('content', str(msg)) + "\n"
                else:
                    prompt += str(msg) + "\n"
        else:
            prompt = str(messages)
        
        # Call Ollama API directly
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from Ollama')
            else:
                return f"Error from Ollama: {response.status_code}"
                
        except Exception as e:
            return f"Failed to connect to Ollama: {e}"

async def main():
    # Load environment variables
    load_dotenv("/Users/kunnath/Projects/useme/browser-use/.env")
    
    # Get DeepSeek key for any needed authentication
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        print(f"✅ DeepSeek key loaded: {deepseek_key[:8]}...")
    
    print("🚀 Testing browser-use with custom DeepSeek-Ollama integration...")
    print("Make sure 'ollama serve' is running in another terminal")
    
    # Test Ollama connection first
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Ollama is running. Available models: {len(models.get('models', []))}")
            
            # Check if deepseek-r1:8b is available
            model_names = [m['name'] for m in models.get('models', [])]
            if 'deepseek-r1:8b' in model_names:
                print("✅ deepseek-r1:8b model found")
            else:
                print("❌ deepseek-r1:8b model not found. Available models:", model_names)
                return
        else:
            print("❌ Ollama is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure to run 'ollama serve' in another terminal")
        return
    
    # Create custom Ollama LLM with DeepSeek model
    llm = DeepSeekOllamaLLM("deepseek-r1:8b")
    
    # Test the LLM first
    test_response = await llm.ainvoke("Hello, are you working? Please respond briefly.")
    print(f"🧠 LLM test response: {test_response[:100]}...")
    
    # Create agent with custom LLM
    agent = Agent(
        task="Navigate to https://example.com and describe what you see",
        llm=llm,
        use_vision=False,
        browser_config={
            "headless": False,
            "viewport_size": {"width": 1280, "height": 720}
        }
    )
    
    try:
        result = await agent.run()
        print("✅ Success with DeepSeek-Ollama integration!")
        print("Result:", result)
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())