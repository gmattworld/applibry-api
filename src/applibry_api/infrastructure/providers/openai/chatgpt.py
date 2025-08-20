from openai import OpenAI

from decouple import config

client = OpenAI(
    api_key=config("OPENAI_API_KEY"),
    # project=config("ORGANIZATION_ID"),
    # organization=config("PROJECT_ID"),
)

def get_content_summary(content: str) -> str:
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize this article in not longer than 250 characters \n {content}"}]
    )
    return chat_completion.choices[0].message.content

