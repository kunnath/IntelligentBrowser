"""
Enhanced Job Finder with LinkedIn Authentication - Reads CV, extracts latest job role, and searches LinkedIn
"""
import asyncio
import csv
import logging
import os
import sys
import re
from pathlib import Path
from typing import Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from PyPDF2 import PdfReader
from browser_use import ActionResult, Agent, Tools
from browser_use.llm.deepseek.chat import ChatDeepSeek
from browser_use.browser import BrowserProfile, BrowserSession

# Check required environment variables
required_env_vars = ['DEEPSEEK_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f'{var} is not set. Please add it to your environment variables.')

# LinkedIn credentials
LINKEDIN_EMAIL = "kunnathsreelesh@gmail.com"
LINKEDIN_PASSWORD = "Adi!!2023"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CV file path
CV_PATH = Path(__file__).parent.parent.parent / 'cv.pdf'

tools = Tools()

class Job(BaseModel):
    title: str
    link: str
    company: str
    fit_score: float
    location: str | None = None
    salary: str | None = None

class CVInfo(BaseModel):
    latest_job_title: str
    experience_years: int
    key_skills: List[str]
    industries: List[str]

def extract_cv_info() -> CVInfo:
    """Extract key information from CV PDF"""
    try:
        if not CV_PATH.exists():
            logger.error(f"CV file not found at {CV_PATH}")
            return CVInfo(
                latest_job_title="Software Developer",
                experience_years=3,
                key_skills=["Python", "Machine Learning"],
                industries=["Technology"]
            )
        
        reader = PdfReader(str(CV_PATH))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        logger.info(f"Extracted {len(text)} characters from CV")
        
        # Extract latest job title (look for common patterns)
        job_patterns = [
            r'(?i)(software\s+engineer|data\s+scientist|machine\s+learning\s+engineer|full\s+stack\s+developer|backend\s+developer|frontend\s+developer|devops\s+engineer|product\s+manager|project\s+manager)',
            r'(?i)(senior\s+\w+\s+\w+|lead\s+\w+|principal\s+\w+)',
            r'(?i)(analyst|consultant|specialist|coordinator|manager|director)'
        ]
        
        latest_job = "Software Developer"  # default
        for pattern in job_patterns:
            matches = re.findall(pattern, text)
            if matches:
                latest_job = matches[0].title()
                break
        
        # Extract experience years
        exp_pattern = r'(?i)(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)'
        exp_matches = re.findall(exp_pattern, text)
        experience_years = int(exp_matches[0]) if exp_matches else 3
        
        # Extract skills
        skill_patterns = [
            r'(?i)python|javascript|java|c\+\+|react|node\.js|sql|mongodb|aws|docker|kubernetes',
            r'(?i)machine\s+learning|data\s+science|artificial\s+intelligence|deep\s+learning',
            r'(?i)agile|scrum|git|ci/cd|devops'
        ]
        
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend([match.title() for match in matches])
        
        skills = list(set(skills))[:10]  # Remove duplicates and limit
        
        return CVInfo(
            latest_job_title=latest_job,
            experience_years=experience_years,
            key_skills=skills if skills else ["Python", "Software Development"],
            industries=["Technology", "Software"]
        )
        
    except Exception as e:
        logger.error(f"Error reading CV: {e}")
        return CVInfo(
            latest_job_title="Software Developer",
            experience_years=3,
            key_skills=["Python", "Machine Learning"],
            industries=["Technology"]
        )

@tools.action('Read and analyze CV to extract latest job role and skills')
def read_and_analyze_cv():
    try:
        cv_info = extract_cv_info()
        analysis = f"""
        CV Analysis Results:
        - Latest Job Title: {cv_info.latest_job_title}
        - Years of Experience: {cv_info.experience_years}
        - Key Skills: {', '.join(cv_info.key_skills)}
        - Industries: {', '.join(cv_info.industries)}
        """
        logger.info(f"CV Analysis completed: {cv_info.latest_job_title}")
        return ActionResult(extracted_content=analysis, include_in_memory=True)
    except Exception as e:
        logger.error(f'Error analyzing CV: {e}')
        fallback_analysis = """
        CV Analysis Results (Fallback):
        - Latest Job Title: Software Developer
        - Years of Experience: 3
        - Key Skills: Python, Machine Learning, Data Science
        - Industries: Technology, Software
        """
        return ActionResult(extracted_content=fallback_analysis, include_in_memory=True)

@tools.action('Login to LinkedIn with provided credentials')
async def login_to_linkedin(browser_session: BrowserSession):
    """
    Login to LinkedIn using the configured email and password credentials.
    This function navigates to LinkedIn login page and authenticates the user.
    """
    try:
        logger.info("🔐 Starting LinkedIn login process...")
        
        # Navigate to LinkedIn login page
        logger.info("📍 Navigating to LinkedIn login page...")
        await browser_session.goto("https://www.linkedin.com/login")
        await browser_session.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # Give page time to fully load
        
        # Fill email field
        logger.info("📧 Attempting to fill email field...")
        email_selectors = [
            '#email-or-phone',
            'input[id="email-or-phone"]',
            'input[name="session_key"]',
            'input[id="username"]',
            '#session_key',
            'input[type="email"]'
        ]
        
        email_filled = False
        for i, selector in enumerate(email_selectors):
            try:
                logger.info(f"Trying email selector {i+1}/{len(email_selectors)}: {selector}")
                await browser_session.page.wait_for_selector(selector, timeout=5000)
                await browser_session.fill(selector, LINKEDIN_EMAIL)
                email_filled = True
                logger.info(f"✅ Email filled successfully with selector: {selector}")
                break
            except Exception as e:
                logger.debug(f"❌ Email selector {selector} failed: {e}")
                continue
        
        if not email_filled:
            error_msg = "Could not find or fill email input field"
            logger.error(error_msg)
            return ActionResult(error=error_msg, include_in_memory=True)
        
        # Fill password field
        logger.info("🔒 Attempting to fill password field...")
        password_selectors = [
            '#password',
            'input[id="password"]',
            'input[name="session_password"]',
            '#session_password',
            'input[type="password"]'
        ]
        
        password_filled = False
        for i, selector in enumerate(password_selectors):
            try:
                logger.info(f"Trying password selector {i+1}/{len(password_selectors)}: {selector}")
                await browser_session.page.wait_for_selector(selector, timeout=5000)
                await browser_session.fill(selector, LINKEDIN_PASSWORD)
                password_filled = True
                logger.info(f"✅ Password filled successfully with selector: {selector}")
                break
            except Exception as e:
                logger.debug(f"❌ Password selector {selector} failed: {e}")
                continue
        
        if not password_filled:
            error_msg = "Could not find or fill password input field"
            logger.error(error_msg)
            return ActionResult(error=error_msg, include_in_memory=True)
        
        # Click login button
        logger.info("🖱️ Attempting to click login button...")
        login_selectors = [
            'button[type="submit"]',
            'button[data-id="sign-in-form__submit-btn"]',
            '.btn__primary--large',
            'input[type="submit"]',
            'button.btn__primary--large',
            '[data-litms-control-urn="login-submit"]'
        ]
        
        login_clicked = False
        for i, selector in enumerate(login_selectors):
            try:
                logger.info(f"Trying login button selector {i+1}/{len(login_selectors)}: {selector}")
                await browser_session.page.wait_for_selector(selector, timeout=5000)
                await browser_session.click(selector)
                login_clicked = True
                logger.info(f"✅ Login button clicked with selector: {selector}")
                break
            except Exception as e:
                logger.debug(f"❌ Login button selector {selector} failed: {e}")
                continue
        
        if not login_clicked:
            error_msg = "Could not find or click login button"
            logger.error(error_msg)
            return ActionResult(error=error_msg, include_in_memory=True)
        
        # Wait for login to complete
        logger.info("⏳ Waiting for login to complete...")
        await browser_session.wait_for_load_state("networkidle")
        await asyncio.sleep(5)  # Increased wait time
        
        # Check if login was successful
        current_url = browser_session.page.url
        logger.info(f"Current URL after login attempt: {current_url}")
        
        if "feed" in current_url or "linkedin.com/in/" in current_url or ("linkedin.com" in current_url and "login" not in current_url):
            success_msg = "🎉 LinkedIn login successful!"
            logger.info(success_msg)
            return ActionResult(
                extracted_content=success_msg,
                include_in_memory=True
            )
        else:
            # Handle potential issues
            if "challenge" in current_url or "checkpoint" in current_url:
                error_msg = "LinkedIn requires additional verification (2FA/CAPTCHA). Please complete manually."
                logger.warning(error_msg)
                return ActionResult(error=error_msg, include_in_memory=True)
            elif "login" in current_url:
                error_msg = "Login failed - still on login page. Please check credentials."
                logger.error(error_msg)
                return ActionResult(error=error_msg, include_in_memory=True)
            else:
                error_msg = f"Unexpected page after login: {current_url}"
                logger.error(error_msg)
                return ActionResult(error=error_msg, include_in_memory=True)
                
    except Exception as e:
        error_msg = f"LinkedIn login failed with exception: {str(e)}"
        logger.error(error_msg)
        return ActionResult(error=error_msg, include_in_memory=True)

@tools.action('Save jobs to CSV file with fit score', param_model=Job)
def save_jobs(job: Job):
    try:
        file_exists = os.path.exists('jobs.csv')
        with open('jobs.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Title', 'Company', 'Link', 'Salary', 'Location', 'Fit Score'])
            writer.writerow([job.title, job.company, job.link, job.salary, job.location, job.fit_score])
        logger.info(f'Saved job: {job.title} at {job.company} (Fit Score: {job.fit_score})')
        return 'Successfully saved job to CSV file'
    except Exception as e:
        logger.error(f'Error saving job: {e}')
        return f'Error saving job: {e}'

@tools.action('Read saved jobs from CSV file')
def read_saved_jobs():
    try:
        if os.path.exists('jobs.csv'):
            with open('jobs.csv', 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f'Read jobs file with {len(content)} characters')
            return content
        else:
            return "No jobs file found yet"
    except Exception as e:
        logger.error(f'Error reading jobs file: {e}')
        return f'Error reading jobs file: {e}'

@tools.action('Upload CV file to job application form')
async def upload_cv_file(index: int, browser_session: BrowserSession):
    try:
        cv_path = str(CV_PATH.absolute())
        if not CV_PATH.exists():
            return ActionResult(error=f'CV file not found at {cv_path}')
        
        dom_element = await browser_session.get_element_by_index(index)
        if dom_element is None:
            return ActionResult(error=f'No element found at index {index}')
        
        if not browser_session.is_file_input(dom_element):
            return ActionResult(error=f'Element at index {index} is not a file upload element')
        
        from browser_use.browser.events import UploadFileEvent
        event = browser_session.event_bus.dispatch(UploadFileEvent(node=dom_element, file_path=cv_path))
        await event
        await event.event_result(raise_if_any=True, raise_if_none=False)
        
        msg = f'Successfully uploaded CV file to index {index}'
        logger.info(msg)
        return ActionResult(extracted_content=msg)
        
    except Exception as e:
        logger.error(f'Error uploading CV: {str(e)}')
        return ActionResult(error=f'Failed to upload CV to index {index}: {str(e)}')

async def create_browser_session():
    """Create browser session with better error handling"""
    try:
        return BrowserSession(
            browser_profile=BrowserProfile(
                executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                disable_security=True,
                user_data_dir='~/.config/browseruse/profiles/linkedin_session',  # Separate profile for LinkedIn
            )
        )
    except Exception as e:
        logger.error(f'Error creating browser session: {e}')
        return BrowserSession()

async def main():
    browser_session = None
    try:
        # First extract CV information
        logger.info("Analyzing CV to extract job information...")
        cv_info = extract_cv_info()
        logger.info(f"Latest job role identified: {cv_info.latest_job_title}")
        
        browser_session = await create_browser_session()
        
        # Create the main task with LinkedIn login
        task = f"""
        You are a professional job finder and applier. Follow these steps IN ORDER:
        
        1. First, call read_and_analyze_cv() to understand my background and latest job role
        
        2. Call login_to_linkedin() to authenticate with LinkedIn using the provided credentials
        
        3. After successful login, navigate to LinkedIn Jobs (https://www.linkedin.com/jobs/search/)
        
        4. Search for jobs similar to my latest role: "{cv_info.latest_job_title}"
           - Use the search box to enter job title
           - You can also search by skills: {', '.join(cv_info.key_skills[:3])}
        
        5. Browse through job listings and find 3-5 relevant positions
        
        6. For each job, evaluate the fit based on:
           - Job title similarity to my latest role: {cv_info.latest_job_title}
           - Required skills match with my skills: {', '.join(cv_info.key_skills)}
           - Experience level requirements vs my {cv_info.experience_years} years
           - Company reputation and growth potential
        
        7. Save the best matching jobs using save_jobs() function with fit scores (1-10)
        
        8. If you encounter any login issues or verification prompts, try to handle them or report the specific error
        
        Important: Make sure to login first before searching for jobs. LinkedIn requires authentication.
        Focus on finding quality matches rather than quantity.
        """
        
        # Use DeepSeek model
        model = ChatDeepSeek(
            model='deepseek-chat',
            api_key=os.getenv('DEEPSEEK_API_KEY')
        )
        
        logger.info(f'Creating agent with LinkedIn authentication for job search: {cv_info.latest_job_title}')
        agent = Agent(
            task=task,
            llm=model,
            tools=tools,
            browser_session=browser_session,
            max_actions_per_step=5,  # Increased for login process
            max_retries=3
        )
        
        logger.info('Starting LinkedIn job search with authentication...')
        await agent.run()
        logger.info('Job search completed successfully')
        
        # Show results
        logger.info('Reading saved jobs...')
        saved_jobs = read_saved_jobs()
        print("\n" + "="*50)
        print("FOUND JOBS FROM LINKEDIN:")
        print("="*50)
        print(saved_jobs)
        
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
