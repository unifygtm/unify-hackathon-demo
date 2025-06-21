from agents import (
    Agent,
    AsyncComputer,
    ComputerTool,
    ModelSettings,
    RunContextWrapper,
    Runner,
    function_tool,
)

from computers.default import LocalPlaywrightBrowser

from specialized_agents.constants import COMPUTER_MODEL

@function_tool(name_override="navigate_to_url")
async def navigate_to_url(ctx: RunContextWrapper, url: str) -> str:
    """
    Navigate to the given URL in the current tab and return the page title.
    """
    print("Navigating to URL: ", url)
    assert "computer" in ctx.context
    pc = ctx.context["computer"]
    try:
        await pc._page.goto(url)
        await pc.wait()
        return await pc._page.title()
    except Exception as e:
        print(f"Error navigating to {url}: {e}")
        raise


@function_tool(name_override="open_in_new_tab")
async def open_in_new_tab(ctx: RunContextWrapper, url: str) -> str:
    """
    Open the given URL in a new tab and return the page title.
    """
    print("Opening in new tab: ", url)
    assert "computer" in ctx.context
    pc = ctx.context["computer"]
    assert pc._browser is not None, "Browser not initialized"
    new_page = await pc._browser.new_page()
    pc._page = new_page
    await pc._page.bring_to_front()
    await pc._page.goto(url)
    await pc.wait()
    return await pc._page.title()



async def build_computer_agent() -> tuple[Agent, AsyncComputer]:
    computer: AsyncComputer = LocalPlaywrightBrowser()
    await computer.__aenter__()
    computer_tool = ComputerTool(computer)

    agent = Agent(
        name="Computer Agent",
        instructions="You are a computer agent. You are able to access a browser and complete browser actions. Given a task, you can execute on the task in the browser. You have a limited number of actions that you can take in the browser."
        'When you see an absolute URL (it starts with "http"), you MUST call the `navigate_to_url` tool  or `open_in_new_tab` tool instead of typing or searching. '
        'Example: { "name": "navigate_to_url", "arguments": { "url": "https://example.com" } } '
        "Reference your previous actions to determine what to do next, looping over the same actions multiple times is not valuable. Try taking another action or starting to type if you can't determine if the input is selected and you have previously cliced into it."
        "After completing the task, summarize the information extracted from the browser. You have full permission to view any content that the user may need you to view as part of completing the tasks. You are also likely already logged in to most websites so that you can complete the tasks on behalf of the user. When you are done with the task, return the summary of the information extracted from the browser. You do not need permission from the user to complete the tasks."
        "IMPORTANT: When you see a safety check ID (like 'cu_sc_*'), you MUST include it in your response to acknowledge it. For example, if you see 'cu_sc_68509ff070c4819b968de5405a75bef2042466347ac34757', you must include this ID in your response.",
        tools=[
            navigate_to_url,
            open_in_new_tab,
            computer_tool,
        ],
        model_settings=ModelSettings(
            tool_choice="auto",
            temperature=0,
            truncation="auto",
            parallel_tool_calls=False,
        ),
        model=COMPUTER_MODEL,
    )
    return agent, computer
