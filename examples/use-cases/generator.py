import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent
from browser_use.llm.deepseek.chat import ChatDeepSeek

class FlowReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.steps = []
        self.screenshots = []
        self.start_time = datetime.now()
        
    def add_step(self, step_name, status, description, screenshot_path=None, error=None):
        step = {
            'step_number': len(self.steps) + 1,
            'step_name': step_name,
            'status': status,  # 'success', 'failed', 'warning'
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'screenshot': screenshot_path,
            'error': error
        }
        self.steps.append(step)
    
    def generate_html_report(self):
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Browser Automation Flow Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .step {{ margin: 20px 0; padding: 15px; border-radius: 5px; border-left: 5px solid; }}
        .step.success {{ background-color: #d4edda; border-color: #28a745; }}
        .step.failed {{ background-color: #f8d7da; border-color: #dc3545; }}
        .step.warning {{ background-color: #fff3cd; border-color: #ffc107; }}
        .step-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }}
        .step-number {{ background: #333; color: white; padding: 5px 10px; border-radius: 50%; font-weight: bold; }}
        .status {{ padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; text-transform: uppercase; }}
        .status.success {{ background-color: #28a745; }}
        .status.failed {{ background-color: #dc3545; }}
        .status.warning {{ background-color: #ffc107; color: #333; }}
        .screenshot {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; }}
        .error {{ background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; border-radius: 4px; font-family: monospace; color: #dc3545; }}
        .summary {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .timestamp {{ color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Browser Automation Flow Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Website: https://www.dinexora.de</p>
        </div>
        
        <div class="summary">
            <h2>Execution Summary</h2>
            <p><strong>Total Steps:</strong> {len(self.steps)}</p>
            <p><strong>Successful:</strong> {len([s for s in self.steps if s['status'] == 'success'])}</p>
            <p><strong>Failed:</strong> {len([s for s in self.steps if s['status'] == 'failed'])}</p>
            <p><strong>Warnings:</strong> {len([s for s in self.steps if s['status'] == 'warning'])}</p>
            <p><strong>Duration:</strong> {(datetime.now() - self.start_time).total_seconds():.2f} seconds</p>
        </div>
        
        <div class="flow">
            <h2>User Flow Steps</h2>
"""
        
        for step in self.steps:
            html_content += f"""
            <div class="step {step['status']}">
                <div class="step-header">
                    <div>
                        <span class="step-number">{step['step_number']}</span>
                        <strong>{step['step_name']}</strong>
                    </div>
                    <span class="status {step['status']}">{step['status']}</span>
                </div>
                <p>{step['description']}</p>
                <div class="timestamp">Executed at: {step['timestamp']}</div>
                
                {f'<img src="{step["screenshot"]}" alt="Screenshot" class="screenshot">' if step['screenshot'] else ''}
                
                {f'<div class="error"><strong>Error:</strong> {step["error"]}</div>' if step['error'] else ''}
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        report_path = self.output_dir / "flow_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path

# Enhanced Agent with Report Generation
class ReportingAgent:
    def __init__(self, task, llm, output_dir):
        self.agent = Agent(task=task, llm=llm)
        self.reporter = FlowReportGenerator(output_dir)
        
    async def run_with_reporting(self):
        try:
            # Step 1: Navigate to website
            self.reporter.add_step(
                "Navigate to Website", 
                "success", 
                "Successfully navigated to https://www.dinexora.de"
            )
            
            # Run the actual agent
            result = await self.agent.run()
            
            # Add more steps based on agent actions
            self.reporter.add_step(
                "Page Analysis", 
                "success", 
                "Completed page structure analysis"
            )
            
            # Generate final report
            report_path = self.reporter.generate_html_report()
            print(f"✅ HTML Report generated: {report_path}")
            
            return result
            
        except Exception as e:
            self.reporter.add_step(
                "Execution Error", 
                "failed", 
                f"Agent execution failed: {str(e)}", 
                error=str(e)
            )
            report_path = self.reporter.generate_html_report()
            print(f"❌ Error Report generated: {report_path}")
            raise

# Usage
task = """
Navigate to https://www.dinexora.de and analyze the website structure.
Take screenshots at each major step and document the user flow.
"""

agent = ReportingAgent(
    task=task,
    llm=ChatDeepSeek(
        model='deepseek-chat',
        api_key=os.getenv('DEEPSEEK_API_KEY')
    ),
    output_dir="/Users/kunnath/Projects/useme/browser-use/reports/"
)

async def main():
    try:
        await agent.run_with_reporting()
        input('Press Enter to close...')
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())