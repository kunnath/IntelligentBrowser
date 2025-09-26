from browser_use.browser.events import BrowserEvent
from browser_use.agent.views import ActionResult

class FlowLogger:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.actions = []
        
    def log_action(self, action_type, status, details, screenshot=None):
        self.actions.append({
            'action': action_type,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'screenshot': screenshot
        })
    
    def generate_report(self):
        # Similar HTML generation as above
        pass

# Integrate with agent
agent = Agent(task=task, llm=llm)
logger = FlowLogger("/Users/kunnath/Projects/useme/browser-use/reports/")

# Override agent methods to capture actions
original_run = agent.run
async def logged_run():
    try:
        result = await original_run()
        logger.log_action("Agent Execution", "success", "Completed successfully")
        return result
    except Exception as e:
        logger.log_action("Agent Execution", "failed", f"Error: {str(e)}")
        raise
    finally:
        logger.generate_report()

agent.run = logged_run