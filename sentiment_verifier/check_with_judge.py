import OpenAI
from sentiment_constants import SENTIMENT_JUDGE_MODEL_ID, CLIENT_BASE_URL

def check_sentiment_with_judge(prompt):
    client = OpenAI(
            base_url=CLIENT_BASE_URL,
            api_key=API_KEY,
    )
    response = client.chat.completions.create(
                    model=SENTIMENT_JUDGE_MODEL_ID,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                )

    response_message = response.choices[0].message
    if response_message.content:
        return response_message.content
    else:
        return None
       