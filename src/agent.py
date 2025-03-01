from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Initialize OpenAI model
llm = ChatOpenAI(model="gpt-4o")

async def main():
    agent = Agent(
        task="Go to Hiring Cafe (https://hiring.cafe) and extract job listings, including job titles, companies, and application links.",
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())