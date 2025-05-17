from openai import OpenAI
from django.conf import settings

def generate_real_estate_summary(df, query):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        sample_data = df.head(5).to_dict()
        print("Sending to OpenAI:", sample_data)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a real estate analysis assistant."
                },
                {
                    "role": "user", 
                    "content": f"Analyze this real estate data and provide a concise summary: {sample_data} for the query: '{query}'"
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )

        print("OpenAI Response:", response)

        # Safety check for response content
        if response and hasattr(response, "choices") and len(response.choices) > 0:
            return response.choices[0].message.content
        
        return "AI analysis failed: No response content."

    except Exception as e:
        print("OpenAI Error:", e)
        return "AI summary generation failed."
