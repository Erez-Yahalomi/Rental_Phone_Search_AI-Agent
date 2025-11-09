import openai
from config.settings import settings

openai.api_key = settings.OPENAI_API_KEY

def summarize_conversation(listing, answers: dict) -> str:
    """
    Use GPT-4 to summarize the conversation answers into a concise paragraph.
    """
    prompt = f"""
Summarize the following rental inquiry conversation into a short paragraph.
Do not list the questions. Focus only on the answers and key insights.

Listing: {listing.get('title') or listing.get('address') or 'Rental'}
Answers:
{answers}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a summarization assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=300
    )
    return response.choices[0].message["content"].strip()
