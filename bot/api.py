from openai import OpenAI
import requests
import base64
import config


def get_completion(prompt: str, client: OpenAI):
    completion = client.chat.completions.create(
        model="meta/llama3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        top_p=1,
        max_tokens=1024,
    )
    
    return completion.choices[0].message.content


def get_completion_with_image(image_b64: str, prompt: str):
    invoke_url = "https://ai.api.nvidia.com/v1/vlm/nvidia/neva-22b"
    stream = False

    

    headers = {
        "Authorization": f"Bearer {config.NVIDIA_KEY}",
        "Accept": "text/event-stream" if stream else "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": f'{prompt} <img src="data:image/png;base64,{image_b64}" />'
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.20,
        "top_p": 0.70,
        "seed": 0,
        "stream": stream
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']



def generate_image(prompt, client: OpenAI):
    response = client.images.generate(
        model="sdxl",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

def save_image(url, path):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)