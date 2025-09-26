import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent

async def main():
    # Load environment variables
    load_dotenv("/Users/kunnath/Projects/useme/browser-use/.env")
    
    # Clear any OpenAI environment variables to force Ollama usage
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    if "OPENAI_BASE_URL" in os.environ:
        del os.environ["OPENAI_BASE_URL"]
    
    # Set Ollama-specific environment variables
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = "deepseek-r1:8b"
    
    print("🔧 Configuring agent to use local Ollama model...")
    
    # Create agent with explicit Ollama configuration
    agent = Agent(
        task="""
        Please help me automate a Google search:
        1. Go to https://google.com
        2. Accept any cookie banners if they appear
        3. Type 'browser automation test' in the search box
        4. Press Enter to search
        5. Take a screenshot of the search results
        6. Describe what you see on the page
        """,
        # Force Ollama provider
        llm_provider="ollama",
        llm_model="deepseek-r1:8b", 
        llm_base_url="http://localhost:11434",
        use_vision=False,
        browser_config={
            "headless": False,
            "viewport_size": {"width": 1280, "height": 720}
        }
    )
    
    print("🚀 Starting browser automation with local Ollama model...")
    result = await agent.run()
    print("\n=== Task Completed ===")
    print("Result:", result)
    
    return result

if __name__ == "__main__":
    # Make sure Ollama is running first
    print("🔍 Make sure Ollama is running: ollama serve")
    print("🔍 Test your model: ollama run deepseek-r1:8b 'Hello'")
    
    asyncio.run(main())