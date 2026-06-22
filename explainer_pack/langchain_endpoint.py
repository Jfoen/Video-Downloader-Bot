import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from chunking_prompt_module import split_into_chunks

load_dotenv()


def build_prompt(content: dict) -> str:
    with open("prompt.txt", "r", encoding="utf-8") as f:
        return (
            f.read()
            .replace("{transcribed_text}", str(content["video_text"]))
            .replace("{video_title}", str(content["video_title"]))
            .replace("{additional_description}", str(content["video_description"]))
        )


async def generate_summary(content: dict) -> str:
    instruction = build_prompt(content)

    chunks = split_into_chunks(instruction, max_tokens=2000)

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEP_SEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        temperature=0,
    )

    responses = []

    for chunk in chunks:
        result = await llm.ainvoke([
            SystemMessage(content="You are summary-bot"),
            HumanMessage(content=chunk),
        ])
        responses.append(result.content)

    final_summary = " ".join(responses)

    return final_summary




