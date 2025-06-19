# Unify Berkeley Hackathon

This repository uses the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) to build a small multi-agent system that can help you conduct research and draft cold emails for jobs and internships. We've set this up to use your existing Chrome browser with current logins, so if you don't have Chrome please install Chrome and login to your Google / Gmail account.

The goal of this workshop is to draft and send a cold email to us (we'll give an email address) using this Agent system to conduct research on the job posting, customize it with context about you from your resume, and then email us using the Computer Agent via Gmail in your browser.

May the best cold AI generated email win :)

## Quick Start
To get started you'll need to:
- update the `.env` file with an OpenAI API Key that we'll provide
- update the `resume.txt` or `resume.pdf` files with your own resume
- adjust the job posting you want to apply for in the `constants.py` file

After setting up the following, install the dependencies and then run the shell script and python script for the Agents. After you get a sense for how it will work, we encourage you to jump in and adjust the prompts to craft a perfect cold email to us (the stock prompts will draft a pretty mediocre cold email).

```bash
# Install dependencies
uv sync

# If you want to run your local Chrome, run the bash script
./start_chrome_debug.sh

# To run the Agents
uv run -m specialized_agents.planning_agent
```

## Details

The agent connects to your existing Chrome browser via Chrome DevTools Protocol (CDP):

1. Start Chrome with remote debugging enabled on port 9222
2. Agent automatically connects to your existing Chrome session
3. All your current tabs, logins, and extensions remain intact
4. If connection fails, falls back to launching Playwright browser

## Chrome Debug Port

### macOS/Linux:
```bash
# Find Chrome path
which google-chrome || which chrome

# Start Chrome with debug port
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```

### Windows:
```bash
# Start Chrome with debug port (adjust path as needed)
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

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
