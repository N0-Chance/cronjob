from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# Initialize OpenAI model
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o")
llm = ChatOpenAI(model=AGENT_MODEL)

async def main():
    agent = Agent(
        task="Go this specific jon application page and scrape all data, including all text and form fields: https://job-boards.greenhouse.io/chime/jobs/7860805002?gh_jid=7860805002",
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())