from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OpenRouter API Key>",
)

def generate(model):
    completion = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant."
        }, {
            "role": "user",
            "content": "Write a random interesting 500-word essay in English. Do not use markdown formatting. Do not write any title."
        }]
    )

    return completion.choices[0].message.content

for i in range(64):
    with open(f"gpt/{i:02}.txt", 'w') as f:
        f.write(generate("openai/gpt-4o"))

for i in range(64):
    with open(f"qwen/{i:02}.txt", 'w') as f:
        f.write(generate("qwen/qwen-2.5-72b-instruct"))