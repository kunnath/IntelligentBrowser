import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent
from browser_use.llm.deepseek.chat import ChatDeepSeek  # Updated to use DeepSeek

# Check for required environment variable
required_env_vars = ['DEEPSEEK_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f'{var} is not set. Please add it to your environment variables.')

task = """
### Sample Browser Automation Task

**Objective:** Navigate to a website, analyze the content, and provide detailed documentation.

**Steps:**
1. Navigate to https://www.dinexora.de
2. Analyze the page structure and content
3. Navigate through main sections of the website
4. Take screenshots of key sections
5. Create detailed analysis report

**Documentation:**
- Take screenshot of homepage and save as "homepage.png"
- Take screenshot of navigation menu and save as "navigation.png"
- Take screenshot of main content areas and save as "content.png"
- Take screenshot of footer and save as "footer.png"
- Save all screenshots to: /Users/kunnath/Projects/useme/browser-use/reports/
- Create a detailed HTML report with embedded screenshots
- Save HTML report as: /Users/kunnath/Projects/useme/browser-use/reports/dinexora_report.html

**Analysis Requirements:**
- Document page structure and layout
- Identify all interactive elements
- Analyze visual design and user experience
- Note technical observations
- Provide comprehensive summary

**Output Files:**
1. HTML report: /Users/kunnath/Projects/useme/browser-use/reports/dinexora_report.html
2. Screenshots: /Users/kunnath/Projects/useme/browser-use/reports/homepage.png, navigation.png, etc.
3. Text summary in the HTML report

**Important:** After completion, tell the user exactly where all files have been saved.
"""


# Updated to use ChatDeepSeek instead of Ollama
agent = Agent(
    task=task,
    llm=ChatDeepSeek(
        model='deepseek-chat',
        api_key=os.getenv('DEEPSEEK_API_KEY')
    )
)

async def main():
    try:
        await agent.run()
        input('Press Enter to close the browser...')
    except Exception as e:
        print(f"Error running agent: {e}")
    except KeyboardInterrupt:
        print("Script interrupted by user")

if __name__ == '__main__':
    asyncio.run(main())