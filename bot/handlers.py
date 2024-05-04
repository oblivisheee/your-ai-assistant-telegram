from telebot import types
from openai import OpenAI
import config
import api
import requests
import base64
import telebot
import os
class Assistant:
    def __init__(self):
        self.client_llm = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=f"{config.NVIDIA_KEY}"
        )
        self.client_image = OpenAI(base_url='https://api.naga.ac/v1', api_key=config.NAGA_AI_API)
        self.session_1 = requests.Session()

    def start(self, bot, message):
        bot.send_message(message.chat.id, 'Ваш ИИ ассистент приветствует вас!', )
    def image_request(self, bot, message):
        if message.photo:
            file_id = message.photo[0].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            answer = self.request_with_image(base64.b64encode(downloaded_file).decode(), message.text)
            if answer == "bad_size":
                bot.send_message(message.chat.id, "Image is too big.")
                return
            bot.send_message(message.chat.id, answer)
    def request(self, bot: telebot.TeleBot, message):
        if message.text.startswith('/generate'):
            self.request_generate_image(bot, message)
        else:
            answer = self.request_text(message.text)
            bot.send_message(message.chat.id, answer)
            
    def request_text(self, prompt: str):
        return api.get_completion(prompt, self.client_llm)

    def request_with_image(self, image, prompt):
        return api.get_completion_with_image(image, prompt)

    def request_generate_image(self, bot, message):
        prompt = message.text[9:]
        user_id = message.from_user.id
        print(f"#{user_id}@{message.from_user.username}: {prompt}")
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, 'Generating your image...')
        
        image_url = api.generate_image(prompt, self.client_image)
        if image_url is None:
            print(f'Error occurred while processing the prompt from user #{user_id}@{message.from_user.username}. The error could be due to NSFW content or an issue with the API.')
            bot.send_message(message.chat.id, 'Something went wrong, possibly, that was an NSFW alert, or problem with API, try again please.')
            return
        
        image_path = os.path.join(os.getcwd(), f'{user_id}-image.jpg')
        api.save_image(image_url, image_path)
        bot.send_chat_action(message.chat.id, 'upload_photo')
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove(image_path)
        bot.send_message(message.chat.id, 'Your image has been generated!')