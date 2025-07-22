import openai

client = openai.OpenAI(api_key="your api key")

response = client.chat.completions.create(
    model="gpt-4.1-nano-2025-04-14",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain calculus simply."}
    ]
)

print(response.choices[0].message.content)