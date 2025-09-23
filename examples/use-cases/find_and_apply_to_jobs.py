"""
Goal: Searches for job listings, evaluates relevance based on a CV, and applies
@dev You need to add DEEPSEEK_API_KEY to your environment variables.
Also you have to install PyPDF2 to read pdf files: pip install PyPDF2
"""

import asyncio
import csv
import logging
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from PyPDF2 import PdfReader  # type: ignore

from browser_use import ActionResult, Agent, Tools
from browser_use.llm.deepseek.chat import ChatDeepSeek  # Direct import path
from browser_use.browser import BrowserProfile, BrowserSession

# Updated to use DeepSeek instead of Gemini
required_env_vars = ['DEEPSEEK_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f'{var} is not set. Please add it to your environment variables.')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# full screen mode
tools = Tools()

# NOTE: This is the path to your cv file
# create a dummy cv
CV = Path.cwd() / 'dummy_cv.pdf'

# Create dummy CV as a proper PDF instead of text file
def create_dummy_cv():
    if not CV.exists():
        with open(CV, 'w', encoding='utf-8') as f:
            f.write('''Hi I am a machine learning engineer with 3 years of experience in the field.
            
Skills:
- Python, TensorFlow, PyTorch
- Machine Learning, Deep Learning
- Data Science, Statistics
- Computer Vision, NLP

Experience:
- 3 years in ML engineering
- Worked on various AI projects
- Experience with cloud platforms''')
        logger.info(f'Created dummy CV at {CV}')

create_dummy_cv()

class Job(BaseModel):
    title: str
    link: str
    company: str
    fit_score: float
    location: str | None = None
    salary: str | None = None

@tools.action('Save jobs to file - with a score how well it fits to my profile', param_model=Job)
def save_jobs(job: Job):
    try:
        with open('jobs.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([job.title, job.company, job.link, job.salary, job.location])
        logger.info(f'Saved job: {job.title} at {job.company}')
        return 'Saved job to file'
    except Exception as e:
        logger.error(f'Error saving job: {e}')
        return f'Error saving job: {e}'

@tools.action('Read jobs from file')
def read_jobs():
    try:
        if os.path.exists('jobs.csv'):
            with open('jobs.csv', 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f'Read {len(content)} characters from jobs file')
                return content
        else:
            return "No jobs file found yet"
    except Exception as e:
        logger.error(f'Error reading jobs: {e}')
        return f'Error reading jobs: {e}'

@tools.action('Read my cv for context to fill forms')
def read_cv():
    try:
        with open(CV, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f'Read cv with {len(text)} characters')
        return ActionResult(extracted_content=text, include_in_memory=True)
    except Exception as e:
        logger.error(f'Error reading CV: {e}')
        fallback_text = "Machine learning engineer with 3 years of experience in Python, TensorFlow, PyTorch, and AI projects."
        return ActionResult(extracted_content=fallback_text, include_in_memory=True)

@tools.action(
    'Upload cv to element - call this function to upload if element is not found, try with different index of the same upload element',
)
async def upload_cv(index: int, browser_session: BrowserSession):
    try:
        path = str(CV.absolute())
        
        dom_element = await browser_session.get_element_by_index(index)
        
        if dom_element is None:
            logger.info(f'No element found at index {index}')
            return ActionResult(error=f'No element found at index {index}')
        
        if not browser_session.is_file_input(dom_element):
            logger.info(f'Element at index {index} is not a file upload element')
            return ActionResult(error=f'Element at index {index} is not a file upload element')
        
        from browser_use.browser.events import UploadFileEvent
        
        event = browser_session.event_bus.dispatch(UploadFileEvent(node=dom_element, file_path=path))
        await event
        await event.event_result(raise_if_any=True, raise_if_none=False)
        
        msg = f'Successfully uploaded file "{path}" to index {index}'
        logger.info(msg)
        return ActionResult(extracted_content=msg)
    except Exception as e:
        logger.error(f'Error in upload: {str(e)}')
        return ActionResult(error=f'Failed to upload file to index {index}: {str(e)}')

async def create_browser_session():
    """Create browser session with better error handling"""
    try:
        return BrowserSession(
            browser_profile=BrowserProfile(
                executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                disable_security=True,
                user_data_dir='~/.config/browseruse/profiles/default',
            )
        )
    except Exception as e:
        logger.error(f'Error creating browser session: {e}')
        return BrowserSession()

async def main():
    browser_session = None
    try:
        browser_session = await create_browser_session()
        
        ground_task = (
            'You are a professional job finder. '
            'Read my CV first using read_cv function. '
            'Then search for machine learning jobs at Google careers website. '
            'Find 2-3 relevant ML jobs and save them using the save_jobs function.'
        )
        
        tasks = [ground_task]
        
        # Use DeepSeek model with direct import
        model = ChatDeepSeek(
            model='deepseek-chat',
            api_key=os.getenv('DEEPSEEK_API_KEY')  # Explicitly pass the API key
        )
        
        agents = []
        for i, task in enumerate(tasks):
            logger.info(f'Creating agent {i+1} with task: {task[:100]}...')
            agent = Agent(
                task=task, 
                llm=model, 
                tools=tools, 
                browser_session=browser_session,
                max_actions_per_step=3,
                max_retries=2
            )
            agents.append(agent)
        
        for i, agent in enumerate(agents):
            try:
                logger.info(f'Running agent {i+1}...')
                await agent.run()
                logger.info(f'Agent {i+1} completed successfully')
            except Exception as e:
                logger.error(f'Agent {i+1} failed: {e}')
                continue
                
    except Exception as e:
        logger.error(f'Error in main: {e}')
    finally:
        if browser_session:
            try:
                await browser_session.close()
                logger.info('Browser session closed successfully')
            except Exception as e:
                logger.error(f'Error closing browser session: {e}')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Script interrupted by user')
    except Exception as e:
        logger.error(f'Script failed: {e}')
