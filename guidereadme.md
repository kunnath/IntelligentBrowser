# Browser-Use Shopping Example - Complete User Guide

## 🛍️ Overview

This guide will walk you through setting up and running the shopping automation example using Browser-Use. You'll learn how to automate e-commerce tasks like searching for products, adding items to cart, and completing purchases using natural language commands.

## 📋 What You'll Learn

- How to set up the Browser-Use environment
- Running the shopping automation example
- Understanding the execution flow
- Customizing shopping tasks
- Troubleshooting common issues

## 🔧 Prerequisites

Before starting, ensure you have:
- **Python 3.9+** installed
- **Git** for cloning the repository
- **API Key** for OpenAI, Anthropic, or AWS Bedrock
- **Internet connection** for browser automation

## 🚀 Step-by-Step Setup Guide

### Step 1: Navigate to Project Directory
```bash
cd /Users/kunnath/Projects/useme
```
### Step 2: Set Up Python Virtual Environment
```bash
python3 -m venv .venv
```
### Step 3: Activate Virtual Environment
```bash
source .venv/bin/activate
```
### Step 4: Install Required Packages
```bash
pip install -r requirements.txt
```
### Step 5: Set Up Environment Variables
```bash
export OPENAI_API_KEY='your-api-key'
export ANTHROPIC_API_KEY='your-api-key'
export AWS_BEDROCK_API_KEY='your-api-key'
export ADEEPSEEK_API_KEY='your-api-key'
```
### Step 6: Run the Shopping Automation Example
```bash
python examples/shopping.py
```

## 📂 File Structure

- `/Users/kunnath/Projects/useme/`
  - `.venv/` - Python virtual environment
  - `examples/` - Contains shopping automation example
  - `requirements.txt` - Python dependencies
  - `README.md` - This guide

## 🛠️ Customization

To customize shopping tasks, modify the `shopping.py` script in the `examples` folder. You can change product search queries, specify shopping sites, and adjust automation steps.

## 🚧 Troubleshooting

- **Issue:** Browser automation fails to start.
  - **Solution:** Ensure you have the latest version of Chrome and ChromeDriver installed.
- **Issue:** API key authentication errors.
  - **Solution:** Double-check your API keys and ensure they have the necessary permissions.

## 📈 Performance Tips

- For faster execution, use headless browser mode.
- Limit the number of concurrent browser instances to avoid overwhelming your system.

## 🔮 Next Steps

- Explore advanced Browser-Use features for more complex automation.
- Integrate with other tools and APIs for a complete e-commerce solution.


Happy automating!

# Check if virtual environment exists
ls -la .venv/

# If it doesn't exist, create it
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install browser-use package
cd browser-use
pip install -e .

# Install Playwright browsers
playwright install chromium

# Create environment file
cp .env.example .env

# Edit the .env file (use your preferred editor)
nano .env

# Choose ONE of the following:

ADEEPSEEK_API_KEY= sk-your-openai-key-here
# OR
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
# OR
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Test if everything is installed correctly
python -c "import browser_use; print('Browser-Use installed successfully!')"

Understanding the Execution Flow
Phase 1: Initialization

[INFO] Initializing Browser-Use Agent
[INFO] Loading LLM model
[INFO] Starting browser session
[INFO] Setting up DOM observer

Phase 2: Task Execution

[INFO] Processing task: "Search for laptop on Amazon"
[INFO] Navigating to amazon.com
[INFO] Locating search box
[INFO] Typing search query: "laptop"
[INFO] Clicking search button

Phase 3: Product Interaction

[INFO] Analyzing search results
[INFO] Selecting product: "MacBook Pro 14-inch"
[INFO] Adding to cart
[INFO] Proceeding to checkout

Phase 4: Completion

[INFO] Task completed successfully
[INFO] Browser session closed

# Edit the shopping.py file or create your own script
import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI

async def shop_for_item():
    llm = ChatOpenAI(model="gpt-4")
    
    agent = Agent(
        task="Go to Amazon and search for 'wireless headphones' under $100",
        llm=llm,
        headless=False  # Set to True to run in background
    )
    
    result = await agent.run()
    return result

# Run the function
asyncio.run(shop_for_item())


async def compare_prices():
    llm = ChatOpenAI(model="gpt-4")
    
    agent = Agent(
        task="Search for 'iPhone 15' on both Amazon and Best Buy, compare prices",
        llm=llm
    )
    
    result = await agent.run()
    return result


    async def specific_shopping():
    llm = ChatOpenAI(model="gpt-4")
    
    agent = Agent(
        task="""
        Go to Target.com and:
        1. Search for 'gaming mouse'
        2. Filter by price range $20-$50
        3. Sort by customer ratings
        4. Add the highest-rated mouse to cart
        """,
        llm=llm
    )
    
    result = await agent.run()
    return result


    # Modify browser behavior
agent = Agent(
    task="Your shopping task",
    llm=llm,
    browser_config={
        "headless": False,          # Show browser window
        "viewport": {
            "width": 1920,
            "height": 1080
        },
        "timeout": 30000,           # 30 second timeout
        "user_agent": "Mozilla/5.0..." # Custom user agent
    }
)


# Control execution behavior
agent = Agent(
    task="Your task",
    llm=llm,
    max_actions=50,        # Maximum actions to perform
    action_delay=1000,     # Delay between actions (ms)
    enable_recording=True  # Record browser session
)

# Solution: Install Playwright browsers
cd browser-use
playwright install chromium

# Solution: Check your .env file
cat browser-use/.env | grep API_KEY

# Make sure the key is valid and properly formatted
export OPENAI_API_KEY=your-key-here

# Solution: Fix file permissions
chmod +x /Users/kunnath/Projects/useme/.venv/bin/python

# Solution: Add error handling and timeouts
agent = Agent(
    task="Your task",
    llm=llm,
    timeout=60000,  # Increase timeout
    headless=True   # Use headless mode for stability
)

# Run with debug logging
DEBUG=1 .venv/bin/python browser-use/examples/use-cases/shopping.py

agent = Agent(task="...", llm=llm, headless=True)

agent = Agent(
    task="...", 
    llm=llm, 
    timeout=15000  # Shorter timeout for faster execution
)


# Process multiple items in one session
task = """
Search for these items and add to cart:
1. Wireless mouse
2. Keyboard
3. Monitor stand
"""

import logging
logging.basicConfig(level=logging.INFO)

# Your agent code here

async def save_shopping_results():
    result = await agent.run()
    
    # Save results to file
    with open('shopping_results.txt', 'w') as f:
        f.write(str(result))
    
    return result


    # Simple search
"Search for 'coffee maker' on Amazon"

# Price comparison
"Find the cheapest wireless charger under $25"

# Category browsing
"Browse electronics section and find trending items"


# Filtered search
"Search for laptops under $800 with SSD storage"

# Multiple criteria
"Find running shoes, size 10, under $100, with good reviews"

# Cart management
"Add 3 different phone cases to cart, then remove the most expensive one"

# Multi-site comparison
"Compare iPhone prices on Amazon, Best Buy, and Apple Store"

# Complex workflows
"Search for gaming setup (monitor, keyboard, mouse), compare prices, add best deals to cart"

# Conditional logic
"If MacBook Pro is on sale for more than 10% off, add to cart, otherwise check refurbished options"