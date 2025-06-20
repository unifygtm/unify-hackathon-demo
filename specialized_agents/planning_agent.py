import asyncio

import pdfplumber
from agents import Agent, ModelSettings, Runner, function_tool

from .constants import (
    DEFAULT_AGENT_MODEL,
    JOB_PAGE_URL,
    PLANNER_MAX_TURNS,
    RESUME_PATH,
    TOOL_MAX_TURNS,
)
from .research_agent import build_research_agent
from .computer_agent import build_computer_agent
PLANNER_PROMPT = """
# Manager – System Prompt

**Core Mission:**
As manager, your job is to ensure that all specialist agents are contributing to the core task given by the user. Your ONLY job is to plan and create tasks to give to the appropriate tools and reflect on progress as the tools complete work. Use the information from the tools to complete the task or delegate additional work.

---

## Specialist Tools

You orchestrate two specialist tools to answer user questions and complete tasks:
- **research**: Access to google via an API to find information that can be used by the computer agent.
- **computer**: Access to a browser to complete actions like viewing website data, interacting with websites, and completing tasks.

Use the computer tool when you need to interact with webpages.
Use the research tool when you need to use general search queries to find information online. The research tool is faster for making search queries and finding the right information online.

---

## Important Rules:
1. You MUST use the research tool for ANY query that requires web research.
2. You MUST use the computer tool for ANY query that requires a browser to complete a task.
3. Construct the query for each tool based on the users task and what needs to be completed by that tool to make progress on the task.
4. Wait for the tool's response before responding.
5. You have full permissions to view any content that the user may need you to view as part of completing the tasks.
6. When using the computer tool, you MUST acknowledge any safety checks that are presented. If you see a safety check ID (like 'cu_sc_*'), you must include it in your response to acknowledge it.
"""

FULL_COMPUTER_USE_TASK_PROMPT = """
1. Find a relevant software engineering, AI, or ML job/internship in the Bay Area based on my profile using the web research tool.
2. Summarize the job description of the job/internship position that would best fit my profile.
3. Navigate to https://www.gmail.com
4. Draft a cover letter style email for the summarized job description. Do not send the emails, but leave them in the draft folder. Do not ask additional questions.
Rules:
When searching for jobs, ALWAYS use the resume information provided in the context to find relevant matches. The resume contains important details about the user's skills, experience, and qualifications that should be used to find appropriate job opportunities.
"""

TASK_PROMPT = f"""
1. Summarize the job description of the job/internship position on this job page: {JOB_PAGE_URL}, use the browser tool if needed.
2. Navigate to https://www.gmail.com
3. Draft a cover letter style email for the summarized job description utilizing specific resume information, making sure to include previous job experience, skills, and qualifications. Do not send the emails, but leave them in the draft folder. Do not ask additional questions. Do not discard the draft.
"""


async def read_resume() -> str:
    if RESUME_PATH.endswith(".pdf"):
        return pdf_to_text(RESUME_PATH)
    else:
        f = open(RESUME_PATH, "r")
        return f.read()


def pdf_to_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def make_agent_tool(agent, name: str, description: str, context: dict | None = None):
    @function_tool(
        name_override=name,
        description_override=description,
        failure_error_function=None,
    )
    async def agent_tool(query: str) -> str:
        try:
            result = await Runner.run(
                agent, query, max_turns=TOOL_MAX_TURNS, context=context
            )
            print(name, "Final output: ", result.final_output)
            return str(result.final_output)
        except Exception as e:
            return f"Error in tool {name}: {e}"

    return agent_tool


async def build_planning_agent() -> tuple[Agent, str]:
    try:
        research_agent = await build_research_agent()
        computer_agent, computer = await build_computer_agent()
        user_resume = await read_resume()

        research_tool = make_agent_tool(
            research_agent,
            name="research",
            description="Research the web for information",
            context={"resume": user_resume},
        )

        computer_tool = make_agent_tool(
            computer_agent,
            name="computer",
            description="Use a browser to complete actions like viewing website data and completing browser tasks. This tool can also be used to close the browser.",
            context={"computer": computer, "resume": user_resume},
        )
        agent = Agent(
            name="Planning Agent",
            instructions=PLANNER_PROMPT + f"The user's resume is: {user_resume}",
            tools=[research_tool, computer_tool],
            model_settings=ModelSettings(
                parallel_tool_calls=False,
                tool_choice="auto",
                temperature=0,
            ),
            model=DEFAULT_AGENT_MODEL,
        )
        return agent, user_resume
    except Exception as e:
        raise Exception(f"Error in planning agent: {e}")


async def main():
    try:
        agent, user_resume = await build_planning_agent()
        result = await Runner.run(
            agent,
            input=TASK_PROMPT,
            max_turns=PLANNER_MAX_TURNS,
            context={"resume": user_resume},
        )
        print(result.final_output)
    except Exception as e:
        raise Exception(f"Error in planning agent: {e}")


if __name__ == "__main__":
    asyncio.run(main())
