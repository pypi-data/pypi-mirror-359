import asyncio
from browser_use import Agent, Controller
from langchain_openai import  ChatOpenAI
from tc_localagent.browser_context import launch_browser_context

class AgentRunner:
    def __init__(self, browser_context_config, controller=None, on_new_step=None, on_agent_done=None, file_paths=None):
        self.browser_context_config = browser_context_config
        self.controller = controller or Controller()
        self.on_new_step = on_new_step
        self.on_agent_done = on_agent_done
        self.file_paths = file_paths

    async def run_agent(self, prompt: str, browser_context_config: dict = None):
        # Use request-provided context if given, otherwise fall back to CLI config
        context_config = browser_context_config or self.browser_context_config

        # Launch the browser context based on this config
        browser_context = await launch_browser_context(context_config)
        page = await browser_context.new_page()
        await page.goto("https://yupp.ai")
        agent = Agent(
            task=prompt,
            use_vision=False,
            llm=ChatOpenAI(model="gpt-4o-mini"),
            controller=self.controller,
            page=page,
            register_new_step_callback=self.on_new_step,
            register_done_callback=self.on_agent_done,
            available_file_paths=(self.file_paths if self.file_paths and len(self.file_paths) > 0 else None)
        )

        result = await agent.run()

        await browser_context.close()
        return result