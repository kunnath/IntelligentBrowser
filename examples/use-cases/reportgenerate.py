import asyncio
import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent
from browser_use.llm.deepseek.chat import ChatDeepSeek

class DetailedWorkflowReportGenerator:
    def __init__(self, output_dir, agent_data_dir=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.agent_data_dir = agent_data_dir
        self.workflow_steps = []
        self.navigation_history = []
        self.execution_files = []
        self.start_time = datetime.now()
        
    def find_agent_data_directory(self):
        """Find the latest browser-use agent data directory"""
        if self.agent_data_dir and Path(self.agent_data_dir).exists():
            return Path(self.agent_data_dir)
        
        # Search for agent directories in multiple locations
        search_patterns = [
            "/var/folders/*/T/browser_use_agent_*",
            "/tmp/browser_use_agent_*",
            str(self.output_dir.parent / "browser_use_agent_*"),
            str(Path.home() / "Downloads" / "browser_use_agent_*"),
            "/Users/*/Projects/useme/browser-use/browser_use_agent_*"
        ]
        
        all_dirs = []
        for pattern in search_patterns:
            all_dirs.extend(glob.glob(pattern))
        
        if all_dirs:
            latest_dir = max(all_dirs, key=os.path.getctime)
            print(f"🔍 Found agent data directory: {latest_dir}")
            return Path(latest_dir)
        
        return None
    
    def add_workflow_step(self, step_type, action, url=None, element=None, status="success", 
                         screenshot=None, timestamp=None, description="", error=None):
        """Add detailed workflow step with navigation context"""
        step = {
            'step_number': len(self.workflow_steps) + 1,
            'step_type': step_type,  # 'navigation', 'interaction', 'analysis', 'capture'
            'action': action,        # 'navigate_to', 'click', 'fill', 'scroll', 'analyze'
            'url': url,
            'element': element,
            'status': status,
            'description': description,
            'screenshot': screenshot,
            'timestamp': timestamp or datetime.now().isoformat(),
            'error': error
        }
        self.workflow_steps.append(step)
        
        # Track navigation history
        if step_type == 'navigation' and url:
            self.navigation_history.append({
                'url': url,
                'timestamp': step['timestamp'],
                'step_number': step['step_number']
            })
    
    def scan_execution_files(self, agent_dir):
        """Scan for execution report files and categorize them"""
        files_data = {
            'execution_reports': [],
            'analysis_reports': [],
            'screenshots': [],
            'logs': [],
            'other_files': []
        }
        
        if not agent_dir or not agent_dir.exists():
            return files_data
        
        # Categorize files by their purpose
        for file_path in agent_dir.rglob('*'):
            if file_path.is_file():
                file_info = {
                    'name': file_path.name,
                    'path': str(file_path),
                    'relative_path': str(file_path.relative_to(agent_dir)),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    'content_preview': self.get_file_preview(file_path)
                }
                
                # Categorize files based on naming patterns
                filename_lower = file_path.name.lower()
                
                if 'execution' in filename_lower or 'workflow' in filename_lower:
                    files_data['execution_reports'].append(file_info)
                elif filename_lower.endswith('.md') and any(keyword in filename_lower for keyword in 
                    ['website_structure', 'analysis', 'content', 'report', 'summary']):
                    files_data['analysis_reports'].append(file_info)
                elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    files_data['screenshots'].append(file_info)
                elif file_path.suffix.lower() in ['.log', '.txt']:
                    files_data['logs'].append(file_info)
                else:
                    files_data['other_files'].append(file_info)
        
        return files_data
    
    def get_file_preview(self, file_path, max_length=500):
        """Get a preview of file content"""
        try:
            if file_path.suffix.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > max_length:
                        return content[:max_length] + "..."
                    return content
            elif file_path.suffix.lower() in ['.txt', '.log']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')[:10]  # First 10 lines
                    return '\n'.join(lines) + ("..." if len(lines) >= 10 else "")
        except Exception as e:
            return f"Preview unavailable: {str(e)}"
        return "Binary file - no preview available"
    
    def generate_enhanced_workflow_report(self):
        """Generate comprehensive workflow report with navigation steps and linked files"""
        
        agent_dir = self.find_agent_data_directory()
        files_data = self.scan_execution_files(agent_dir) if agent_dir else {}
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detailed Workflow & Execution Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }}
        .container {{ max-width: 1600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        
        .nav-tabs {{ display: flex; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
        .nav-tab {{ flex: 1; padding: 15px; text-align: center; cursor: pointer; border: none; background: transparent; font-weight: 500; transition: all 0.3s; }}
        .nav-tab:hover {{ background: #e9ecef; }}
        .nav-tab.active {{ background: white; border-bottom: 3px solid #667eea; color: #667eea; }}
        
        .tab-content {{ display: none; padding: 30px; }}
        .tab-content.active {{ display: block; }}
        
        .workflow-step {{ margin: 20px 0; border: 1px solid #e9ecef; border-radius: 8px; overflow: hidden; background: white; }}
        .step-header {{ padding: 15px 20px; background: #f8f9fa; display: flex; justify-content: space-between; align-items: center; }}
        .step-number {{ background: #667eea; color: white; padding: 8px 12px; border-radius: 50%; font-weight: bold; min-width: 30px; text-align: center; }}
        .step-details {{ flex: 1; margin-left: 15px; }}
        .step-title {{ font-weight: 600; margin: 0; color: #2c3e50; }}
        .step-meta {{ font-size: 0.9em; color: #6c757d; margin: 5px 0 0 0; }}
        .step-status {{ padding: 6px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 500; text-transform: uppercase; }}
        .status-success {{ background: #d4edda; color: #155724; }}
        .status-failed {{ background: #f8d7da; color: #721c24; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        
        .step-content {{ padding: 20px; }}
        .step-screenshot {{ max-width: 100%; border-radius: 6px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .step-error {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 6px; color: #721c24; }}
        
        .navigation-flow {{ margin: 20px 0; }}
        .nav-item {{ display: flex; align-items: center; margin: 10px 0; padding: 15px; background: #f8f9fa; border-radius: 6px; }}
        .nav-arrow {{ margin: 0 15px; color: #667eea; font-size: 1.2em; }}
        
        .file-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .file-card {{ border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; background: #f8f9fa; }}
        .file-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .file-title {{ font-weight: 600; color: #2c3e50; }}
        .file-type {{ background: #667eea; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
        .file-link {{ color: #667eea; text-decoration: none; font-weight: 500; }}
        .file-link:hover {{ text-decoration: underline; }}
        .file-preview {{ background: white; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; font-family: 'Courier New', monospace; font-size: 0.9em; max-height: 200px; overflow-y: auto; }}
        
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-number {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .summary-label {{ font-size: 0.9em; opacity: 0.9; }}
        
        .timeline {{ position: relative; padding-left: 30px; }}
        .timeline-item {{ position: relative; margin: 20px 0; }}
        .timeline-item::before {{ content: ''; position: absolute; left: -35px; top: 10px; width: 10px; height: 10px; border-radius: 50%; background: #667eea; }}
        .timeline-item::after {{ content: ''; position: absolute; left: -31px; top: 20px; width: 2px; height: calc(100% + 20px); background: #e9ecef; }}
        .timeline-item:last-child::after {{ display: none; }}
    </style>
    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Detailed Workflow & Execution Report</h1>
            <p>Website Analysis: https://www.dinexora.de</p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            {f'<p>Agent Data: {agent_dir}</p>' if agent_dir else ''}
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('overview')">Overview</button>
            <button class="nav-tab" onclick="showTab('workflow')">Workflow Steps</button>
            <button class="nav-tab" onclick="showTab('navigation')">Navigation Flow</button>
            <button class="nav-tab" onclick="showTab('reports')">Execution Reports</button>
            <button class="nav-tab" onclick="showTab('screenshots')">Screenshots</button>
        </div>
        
        <div id="overview" class="tab-content active">
            <h2>Execution Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-number">{len(self.workflow_steps)}</div>
                    <div class="summary-label">Total Steps</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{len([s for s in self.workflow_steps if s['status'] == 'success'])}</div>
                    <div class="summary-label">Successful</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{len([s for s in self.workflow_steps if s['status'] == 'failed'])}</div>
                    <div class="summary-label">Failed</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{len(self.navigation_history)}</div>
                    <div class="summary-label">Page Visits</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{sum(len(files) for files in files_data.values()) if files_data else 0}</div>
                    <div class="summary-label">Generated Files</div>
                </div>
            </div>
            
            <h3>Navigation History</h3>
            <div class="navigation-flow">
"""
        
        # Add navigation timeline
        for i, nav in enumerate(self.navigation_history):
            html_content += f"""
                <div class="nav-item">
                    <strong>Step {nav['step_number']}</strong>
                    <span class="nav-arrow">→</span>
                    <code>{nav['url']}</code>
                    <span style="margin-left: auto; color: #6c757d; font-size: 0.9em;">{nav['timestamp']}</span>
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
        <div id="workflow" class="tab-content">
            <h2>Detailed Workflow Steps</h2>
            <div class="timeline">
"""
        
        # Add detailed workflow steps
        for step in self.workflow_steps:
            status_class = f"status-{step['status']}"
            html_content += f"""
                <div class="timeline-item">
                    <div class="workflow-step">
                        <div class="step-header">
                            <div style="display: flex; align-items: center;">
                                <div class="step-number">{step['step_number']}</div>
                                <div class="step-details">
                                    <h4 class="step-title">{step['action'].replace('_', ' ').title()}</h4>
                                    <p class="step-meta">
                                        Type: {step['step_type'].title()} | 
                                        Time: {step['timestamp']}
                                        {f" | URL: {step['url']}" if step['url'] else ""}
                                        {f" | Element: {step['element']}" if step['element'] else ""}
                                    </p>
                                </div>
                            </div>
                            <div class="step-status {status_class}">{step['status']}</div>
                        </div>
                        <div class="step-content">
                            <p>{step['description']}</p>
                            {f'<img src="file://{step["screenshot"]}" alt="Screenshot" class="step-screenshot">' if step['screenshot'] else ''}
                            {f'<div class="step-error"><strong>Error:</strong> {step["error"]}</div>' if step['error'] else ''}
                        </div>
                    </div>
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
        <div id="navigation" class="tab-content">
            <h2>Navigation Flow Analysis</h2>
            <p>Complete navigation path during the workflow execution:</p>
"""
        
        # Enhanced navigation flow with more details
        for i, nav in enumerate(self.navigation_history):
            related_steps = [s for s in self.workflow_steps if s.get('url') == nav['url']]
            html_content += f"""
            <div class="workflow-step">
                <div class="step-header">
                    <div class="step-details">
                        <h4 class="step-title">Navigation #{i+1}: {nav['url']}</h4>
                        <p class="step-meta">Timestamp: {nav['timestamp']} | Related to Step {nav['step_number']}</p>
                    </div>
                </div>
                <div class="step-content">
                    <p><strong>Actions performed on this page:</strong></p>
                    <ul>
"""
            for related_step in related_steps:
                html_content += f"<li>{related_step['action'].replace('_', ' ').title()}: {related_step['description']}</li>"
            
            html_content += """
                    </ul>
                </div>
            </div>
"""
        
        html_content += """
        </div>
        
        <div id="reports" class="tab-content">
            <h2>Execution Reports & Analysis Files</h2>
"""
        
        # Add execution reports with enhanced linking
        if files_data:
            for category, files in files_data.items():
                if files and category in ['execution_reports', 'analysis_reports']:
                    html_content += f"""
            <h3>{category.replace('_', ' ').title()} ({len(files)} files)</h3>
            <div class="file-grid">
"""
                    for file_info in files:
                        html_content += f"""
                <div class="file-card">
                    <div class="file-header">
                        <div class="file-title">{file_info['name']}</div>
                        <div class="file-type">{file_info['name'].split('.')[-1].upper()}</div>
                    </div>
                    <p><strong>Path:</strong> {file_info['relative_path']}</p>
                    <p><strong>Size:</strong> {file_info['size']} bytes | <strong>Modified:</strong> {file_info['modified']}</p>
                    <p><a href="file://{file_info['path']}" class="file-link" target="_blank">📄 Open Full Report</a></p>
                    
                    <h5>Content Preview:</h5>
                    <div class="file-preview">{file_info['content_preview']}</div>
                </div>
"""
                    html_content += "</div>"
        
        html_content += """
        </div>
        
        <div id="screenshots" class="tab-content">
            <h2>Screenshots Gallery</h2>
            <div class="file-grid">
"""
        
        # Add screenshots
        if files_data.get('screenshots'):
            for screenshot in files_data['screenshots']:
                html_content += f"""
                <div class="file-card">
                    <div class="file-header">
                        <div class="file-title">{screenshot['name']}</div>
                        <div class="file-type">IMG</div>
                    </div>
                    <img src="file://{screenshot['path']}" alt="{screenshot['name']}" class="step-screenshot">
                    <p><a href="file://{screenshot['path']}" class="file-link" target="_blank">🖼️ Open Full Size</a></p>
                    <p><strong>Modified:</strong> {screenshot['modified']}</p>
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
    </div>
</body>
</html>
"""
        
        report_path = self.output_dir / "flow_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Enhanced Workflow Report generated: {report_path}")
        if agent_dir:
            print(f"📁 Linked to agent directory: {agent_dir}")
            total_files = sum(len(files) for files in files_data.values())
            print(f"🔗 Integrated {total_files} execution files")
        
        return report_path

# Enhanced Workflow Tracking Agent
class WorkflowTrackingAgent:
    def __init__(self, task, llm, output_dir):
        self.agent = Agent(task=task, llm=llm)
        self.reporter = DetailedWorkflowReportGenerator(output_dir)
        
    async def run_with_workflow_tracking(self):
        try:
            # Track detailed workflow steps
            self.reporter.add_workflow_step(
                step_type="initialization",
                action="initialize_agent",
                description="Browser automation agent initialized successfully",
                status="success"
            )
            
            self.reporter.add_workflow_step(
                step_type="navigation",
                action="navigate_to",
                url="https://www.dinexora.de",
                description="Navigating to target website for analysis",
                status="success"
            )
            
            self.reporter.add_workflow_step(
                step_type="analysis",
                action="analyze_page_structure",
                description="Analyzing page structure, content, and interactive elements",
                status="success"
            )
            
            # Run the actual agent
            result = await self.agent.run()
            
            self.reporter.add_workflow_step(
                step_type="completion",
                action="generate_reports",
                description="Analysis completed, generating comprehensive reports",
                status="success"
            )
            
            # Generate the enhanced workflow report
            report_path = self.reporter.generate_enhanced_workflow_report()
            
            return result, report_path
            
        except Exception as e:
            self.reporter.add_workflow_step(
                step_type="error",
                action="handle_exception",
                description=f"Workflow execution failed: {str(e)}",
                status="failed",
                error=str(e)
            )
            report_path = self.reporter.generate_enhanced_workflow_report()
            raise

# Usage
task = """
Navigate to https://www.dinexora.de and perform comprehensive website analysis.
Document each navigation step, interaction, and analysis phase.
Generate detailed execution reports and capture screenshots at key points.
"""

agent = WorkflowTrackingAgent(
    task=task,
    llm=ChatDeepSeek(
        model='deepseek-chat',
        api_key=os.getenv('DEEPSEEK_API_KEY')
    ),
    output_dir="/Users/kunnath/Projects/useme/browser-use/reports/"
)

async def main():
    try:
        result, report_path = await agent.run_with_workflow_tracking()
        print(f"\n🎉 Workflow Report Complete!")
        print(f"📊 Report Location: {report_path}")
        print(f"🔗 All execution files linked and accessible")
        input('Press Enter to close...')
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())