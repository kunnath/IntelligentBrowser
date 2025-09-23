#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["browser-use", "python-dotenv"]
# ///

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
from browser_use import Agent
from browser_use.llm.deepseek.chat import ChatDeepSeek  # Updated to use DeepSeek

# Check for required environment variable
required_env_vars = ['DEEPSEEK_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f'{var} is not set. Please add it to your environment variables.')

logger = logging.getLogger(__name__)

async def main():
    try:
        agent = Agent(
            task="""
            Objective: Navigate to the following URL, what is on page 3?
            URL:  https://docs.house.gov/meetings/GO/GO00/20220929/115171/HHRG-117-GO00-20220929-SD010.pdf
            
            Instructions:
            1. Navigate to the PDF URL
            2. Wait for the PDF to load
            3. Navigate to page 3 (you might need to scroll or use page navigation)
            4. Extract and summarize the content on page 3
            5. Provide a detailed summary of what you find on page 3
            """,
            llm=ChatDeepSeek(
                model='deepseek-chat',
                api_key=os.getenv('DEEPSEEK_API_KEY')
            ),
        )
        
        result = await agent.run()
        logger.info("Agent execution completed")
        logger.info(f"Result: {result}")
        
        print("\n" + "="*50)
        print("EXTRACTION COMPLETED")
        print("="*50)
        print(f"Result: {result}")
        
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        print(f"Error: {e}")
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        print("Script interrupted by user")

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
