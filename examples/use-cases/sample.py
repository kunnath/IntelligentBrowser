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

**Objective:** Navigate to a website, analyze the content, and provide a detailed description with comprehensive documentation.

**Steps:**
1. Navigate to https://www.dinexora.de
2. Analyze the page structure and content
3. Navigate through main sections of the website
4. Identify key elements on the page
5. Describe the layout and visual elements
6. Take multiple screenshots during navigation
7. Save all findings to a structured report

**Requirements:**
- Be thorough in your analysis
- Describe both textual content and visual elements
- Note any interactive elements or forms
- Provide a summary of the page's purpose
- Document the navigation flow with screenshots
- Take screenshots at each major step
- Save screenshots with descriptive filenames
- Create a detailed text report with findings

**Documentation Strategy:**
- Take screenshot of homepage
- Take screenshot of main navigation menu
- Take screenshot of key content sections
- Take screenshot of footer/contact information
- Save each screenshot with timestamp and description
- Record all observations in a structured format

**Output Requirements:**
1. Multiple screenshots saved to /Users/kunnath/Projects/useme/browser-use/screenshots/
2. Detailed text report saved as report.txt
3. Create an HTML report that can be converted to PDF
4. Include all screenshots in the HTML report with captions
5. Generate final PDF from the HTML report

**Report Structure:**
- Website Overview
- Navigation Analysis
- Content Analysis (with embedded screenshots)
- Interactive Elements Found
- Technical Observations
- Visual Design Analysis
- User Experience Notes
- Summary and Conclusions

**File Organization:**
- Save all files to: /Users/kunnath/Projects/useme/browser-use/reports/dinexora_analysis/
- Screenshots: screenshots/
- Text report: analysis_report.txt
- HTML report: analysis_report.html
- Final PDF: analysis_report.pdf

Note: Since PDF cannot contain actual video, use multiple sequential screenshots to show the navigation flow instead.
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