import asyncio
import os
import sys

# Add the parent directories to Python path for importing browser_use
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent
from openai import AsyncOpenAI
from typing import Any, Dict, List, Optional, Union

# Check for required environment variable
required_env_vars = ['DEEPSEEK_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f'{var} is not set. Please add it to your environment variables.')

class ChatDeepSeek:
    """
    Custom DeepSeek LLM wrapper compatible with Browser-Use
    """
    def __init__(self, model: str = "deepseek-chat", api_key: str = None, **kwargs):
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com/v1"
        )
        
        # Set all required attributes for Browser-Use compatibility
        self.model = model
        self.provider = "deepseek"
        self.model_name = model
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 4000)
        
        # Additional attributes that might be checked
        self._model = model
        self._provider = "deepseek"
        self._model_name = model
        self._temperature = self.temperature
        self._max_tokens = self.max_tokens

    def _convert_messages_to_openai_format(self, messages: Any) -> List[Dict[str, str]]:
        """
        Convert various message formats to OpenAI format
        """
        try:
            openai_messages = []
            
            # Handle string input
            if isinstance(messages, str):
                return [{"role": "user", "content": messages}]
            
            # Handle list input
            if isinstance(messages, list):
                for msg in messages:
                    try:
                        # Handle Pydantic models or objects with attributes
                        if hasattr(msg, 'content'):
                            content = str(msg.content)
                            
                            # Determine role
                            if hasattr(msg, 'type'):
                                role_map = {
                                    "human": "user",
                                    "user": "user",
                                    "assistant": "assistant",
                                    "ai": "assistant",
                                    "system": "system"
                                }
                                role = role_map.get(str(msg.type).lower(), "user")
                            elif hasattr(msg, 'role'):
                                role = str(msg.role)
                            else:
                                role = "user"
                            
                            openai_messages.append({"role": role, "content": content})
                        
                        # Handle dictionary format
                        elif isinstance(msg, dict):
                            if 'role' in msg and 'content' in msg:
                                openai_messages.append({
                                    "role": str(msg['role']),
                                    "content": str(msg['content'])
                                })
                            else:
                                openai_messages.append({"role": "user", "content": str(msg)})
                        
                        # Handle string or other types
                        else:
                            openai_messages.append({"role": "user", "content": str(msg)})
                            
                    except Exception as e:
                        print(f"Warning: Failed to process message {msg}: {e}")
                        # Fallback: convert to string
                        openai_messages.append({"role": "user", "content": str(msg)})
                
                return openai_messages
            
            # Handle single object (not list)
            if hasattr(messages, 'content'):
                content = str(messages.content)
                role = "user"
                
                if hasattr(messages, 'type'):
                    role_map = {
                        "human": "user",
                        "user": "user",
                        "assistant": "assistant",
                        "ai": "assistant",
                        "system": "system"
                    }
                    role = role_map.get(str(messages.type).lower(), "user")
                elif hasattr(messages, 'role'):
                    role = str(messages.role)
                
                return [{"role": role, "content": content}]
            
            # Fallback: convert anything else to string
            return [{"role": "user", "content": str(messages)}]
            
        except Exception as e:
            print(f"Error converting messages: {e}")
            # Ultimate fallback
            return [{"role": "user", "content": str(messages)}]

    async def ainvoke(self, messages: Any, config: Optional[Dict] = None, **kwargs) -> str:
        """
        Async invoke method required by Browser-Use
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = self._convert_messages_to_openai_format(messages)
            
            # Merge config into kwargs if provided
            if config:
                kwargs.update(config)
            
            # Filter kwargs to only include valid OpenAI parameters
            valid_params = {
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
                'top_p': kwargs.get('top_p'),
                'frequency_penalty': kwargs.get('frequency_penalty'),
                'presence_penalty': kwargs.get('presence_penalty'),
                'stop': kwargs.get('stop')
            }
            
            # Remove None values
            api_params = {k: v for k, v in valid_params.items() if v is not None}
            
            # Make API call to DeepSeek
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                **api_params
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ DeepSeek API error: {e}")
            print(f"❌ Messages type: {type(messages)}")
            print(f"❌ Messages content: {messages}")
            raise

    def invoke(self, messages: Any, config: Optional[Dict] = None, **kwargs) -> str:
        """
        Synchronous invoke method
        """
        return asyncio.run(self.ainvoke(messages, config, **kwargs))

    async def agenerate(self, messages: List[List[Any]], **kwargs) -> Any:
        """
        Additional method that might be called by Browser-Use
        """
        results = []
        for message_list in messages:
            result = await self.ainvoke(message_list, **kwargs)
            results.append(result)
        return results

    def generate(self, messages: List[List[Any]], **kwargs) -> Any:
        """
        Synchronous generate method
        """
        return asyncio.run(self.agenerate(messages, **kwargs))

    def __getattr__(self, name: str) -> Any:
        """
        Handle any missing attributes that Browser-Use might look for
        """
        attribute_map = {
            "provider": "deepseek",
            "_provider": "deepseek",
            "model": self.model,
            "_model": self.model,
            "model_name": self.model,
            "_model_name": self.model,
            "temperature": self.temperature,
            "_temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "_max_tokens": self.max_tokens,
            "streaming": False,
            "_streaming": False,
            "callbacks": None,
            "_callbacks": None,
            "metadata": {},
            "_metadata": {},
            "tags": [],
            "_tags": []
        }
        return attribute_map.get(name, None)

    def dict(self) -> Dict[str, Any]:
        """
        Return dictionary representation
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

task = """
### Prompt for Shopping Agent – Migros Online Grocery Order

**Objective:** Visit [Migros Online](https://www.migros.ch/), search for the required grocery items, add them to the cart, select an appropriate delivery window, and complete the checkout process using TWINT.

**Important:** 
- Make sure that you don't buy more than it's needed for each article.
- After your search, if you click the "+" button, it adds the item to the basket.
- If you open the basket sidewindow menu, you can close it by clicking the X button on the top right. This will help you navigate easier.

---

### Step 1: Navigate to the Website
- Open [Migros Online](https://www.migros.ch/).
- You should be logged in as maya sreelesh

---

### Step 2: Add Items to the Basket

#### Shopping List:

**Meat & Dairy:**
- Beef Minced meat (1 kg)
- Gruyère cheese (grated preferably)
- 2 liters full-fat milk
- Butter (cheapest available)

**Vegetables:**
- Carrots (1kg pack)
- Celery
- Leeks (1 piece)
- 1 kg potatoes

At this stage, check the basket on the top right (indicates the price) and check if you bought the right items.

**Fruits:**
- 2 lemons
- Oranges (for snacking)

**Pantry Items:**
- Lasagna sheets
- Tahini
- Tomato paste (below CHF2)
- Black pepper refill (not with the mill)
- 2x 1L Oatly Barista (oat milk)
- 1 pack of eggs (10 egg package)

#### Ingredients I already have (DO NOT purchase):
- Olive oil, garlic, canned tomatoes, dried oregano, bay leaves, salt, chili flakes, flour, nutmeg, cumin.

---

### Step 3: Handling Unavailable Items
- If an item is **out of stock**, find the best alternative.
- Use the following recipe contexts to choose substitutions:
  - **Pasta Bolognese & Lasagna:** Minced meat, tomato paste, lasagna sheets, milk (for béchamel), Gruyère cheese.
  - **Hummus:** Tahini, chickpeas, lemon juice, olive oil.
  - **Chickpea Curry Soup:** Chickpeas, leeks, curry, lemons.
  - **Crispy Slow-Cooked Pork Belly with Vegetables:** Potatoes, butter.
- Example substitutions:
  - If Gruyère cheese is unavailable, select another semi-hard cheese.
  - If Tahini is unavailable, a sesame-based alternative may work.

---

### Step 4: Adjusting for Minimum Order Requirement
- If the total order **is below CHF 99**, add **a liquid soap refill** to reach the minimum. If it's still not enough, you can buy some bread, dark chocolate.
- At this step, check if you have bought MORE items than needed. If the price is more than CHF200, you MUST remove items.
- If an item is not available, choose an alternative.
- If an age verification is needed, remove alcoholic products, we haven't verified yet.

---

### Step 5: Select Delivery Window
- Choose a **delivery window within the current week**. It's ok to pay up to CHF2 for the window selection.
- Preferably select a slot within the workweek.

---

### Step 6: Checkout
- Proceed to checkout.
- Select **TWINT** as the payment method.
- Check out.
- If it's needed the username is: maya.sreelesh@gmail.com
- And the password is: Password23

---

### Step 7: Confirm Order & Output Summary
- Once the order is placed, output a summary including:
  - **Final list of items purchased** (including any substitutions).
  - **Total cost**.
  - **Chosen delivery time**.

**Important:** Ensure efficiency and accuracy throughout the process.
"""

async def test_deepseek_connection():
    """
    Test DeepSeek connection before running the main task
    """
    try:
        llm = ChatDeepSeek(api_key=os.getenv('DEEPSEEK_API_KEY'))
        
        # Test with simple string
        test1 = await llm.ainvoke("Hello, can you respond with 'Ready for shopping'?")
        print(f"✅ String test: {test1}")
        
        # Test with list format
        test2 = await llm.ainvoke([{"role": "user", "content": "Say 'Test successful'"}])
        print(f"✅ List test: {test2}")
        
        return llm
    except Exception as e:
        print(f"❌ DeepSeek connection test failed: {e}")
        return None

async def main():
    try:
        print("🛒 Starting Migros Online Shopping with DeepSeek...")
        print("=" * 60)
        print(f"🎯 Target website: https://www.migros.ch/")
        print("👤 User: maya sreelesh")
        print("💳 Payment: TWINT")
        print("-" * 60)
        
        # Test DeepSeek connection first
        print("🧠 Testing DeepSeek connection...")
        llm = await test_deepseek_connection()
        if not llm:
            print("❌ DeepSeek connection failed. Exiting...")
            return
        
        # Create the agent
        agent = Agent(
            task=task,
            llm=llm,
            headless=False,  # Show browser for debugging
            max_actions=300,  # Increase for complex shopping task
            action_delay=3000,  # 3 second delay between actions for stability
        )
        
        result = await agent.run()
        
        print("\n" + "=" * 60)
        print("✅ Shopping task completed!")
        print(f"📊 Final result: {result}")
        
        input('Press Enter to close the browser...')
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("⏹️ Script interrupted by user")

if __name__ == '__main__':
    print("🇨🇭 Migros Online Shopping Bot with DeepSeek")
    print("=" * 50)
    
    # Verify environment setup
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ DEEPSEEK_API_KEY not found!")
        print("Please add it to your .env file:")
        print("DEEPSEEK_API_KEY=your_deepseek_api_key_here")
        exit(1)
    
    print("✅ DeepSeek API key found")
    print("▶️ Starting shopping automation...")
    
    asyncio.run(main())
