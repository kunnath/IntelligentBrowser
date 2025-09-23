# Goal: Checks for available visa appointment slots on the Greece MFA website.

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from browser_use.llm.deepseek.chat import ChatDeepSeek  # Updated to use DeepSeek
from browser_use.agent.service import Agent
from browser_use.tools.service import Tools

# Updated to use DeepSeek instead of OpenAI
required_env_vars = ['DEEPSEEK_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f'{var} is not set. Please add it to your environment variables.')

tools = Tools()

class WebpageInfo(BaseModel):
    """Model for webpage link."""
    link: str = 'https://appointment.mfa.gr/en/reservations/aero/ireland-grcon-dub/'

@tools.action('Go to the webpage', param_model=WebpageInfo)
def go_to_webpage(webpage_info: WebpageInfo):
    """Returns the webpage link."""
    return webpage_info.link

async def main():
    """Main function to execute the agent task."""
    try:
        task = (
            'Go to the Greece MFA webpage via the link I provided you. '
            'Check the visa appointment dates. If there is no available date in this month, check the next month. '
            'If there is no available date in both months, tell me there is no available date. '
            'Be thorough in checking all available appointment slots and provide detailed information about what you find.'
        )
        
        # Updated to use ChatDeepSeek instead of ChatOpenAI
        model = ChatDeepSeek(
            model='deepseek-chat',
            api_key=os.getenv('DEEPSEEK_API_KEY')
        )
        
        agent = Agent(task, model, tools=tools, use_vision=True)
        
        print("Starting appointment check...")
        print("Checking Greece MFA visa appointment availability...")
        
        result = await agent.run()
        
        print("\n" + "="*60)
        print("APPOINTMENT CHECK COMPLETED")
        print("="*60)
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error running agent: {e}")
    except KeyboardInterrupt:
        print("Script interrupted by user")

if __name__ == '__main__':
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
