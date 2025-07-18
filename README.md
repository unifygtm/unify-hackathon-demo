# Unify Berkeley Hackathon

This repository uses the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) to build a small multi-agent system that can help you conduct research and draft cold emails for jobs and internships. We've set this up to use your existing Chrome browser with current logins, so if you don't have Chrome please install Chrome and login to your Google / Gmail account.

The goal of this workshop is to draft and send a cold email to us (we'll give an email address) using this Agent system to conduct research on the job posting, customize it with context about you from your resume, and then email us using the Computer Agent via Gmail in your browser.

May the best cold AI generated email win :)

## Quick Start

Install a few prerequisites on your computer:

1. [uv](https://docs.astral.sh/uv/getting-started/installation/)

2. [Google Chrome](https://www.google.com/chrome/)

Log in to your Gmail account in Chrome if you're not already logged in.

Next, configure your agent:

1. Copy the `.env.example` file to create a new `.env` in the root of the repo. Fill in the OpenAI API Key that we'll provide during the workshop.
2. Update `RESUME_PATH` at `specialized_agents/constants.py` as needed.
3. Adjust the job posting you want to apply for in the `constants.py` file.

Next install the Python dependencies and then run the shell script and python script for the Agents:

```bash
# Install dependencies
uv sync

# Install Playwright Chromium dependency
uv run playwright install

# If you want to run your local Chrome, run the bash script
./start_chrome_debug.sh

# Run the Agents
uv run -m specialized_agents.planning_agent
```

After you get a sense for how it will work, we encourage you to jump in and adjust the prompts to craft a perfect cold email to us (the stock prompts will draft a pretty mediocre cold email).

## Details

The agent connects to your existing Chrome browser via Chrome DevTools Protocol (CDP):

1. `start_chrome_debug.sh` starts Chrome with remote debugging enabled on port 9222
2. Agent automatically connects to your existing Chrome session
3. All your current tabs, logins, and extensions remain intact
4. If connection fails, falls back to launching Playwright browser


## Environment

Required:
```env
OPENAI_API_KEY=your_key_here
```

Optional:
```env
CHROME_DEBUG_PORT=9222  # Change debug port if needed
```

## Troubleshooting

- Chrome must be running with remote debugging enabled
- Default debug port is 9222 - change if port is in use
- If connection fails, agent falls back to Playwright browser (if you need to use Playwright, you'll need to login to Gmail on playwright as well)
