import telebot
import config
import handlers

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
handler = handlers.Assistant()

@bot.message_handler(commands=['start'])
def start(message):
    handler.start(bot, message)

@bot.message_handler(content_types=['photo'])
def image_request(message):
    handler.image_request(bot, message)

@bot.message_handler(func=lambda message: True)
def check_message(message):
    if message.content_type == 'photo':
        image_request(message)
    else:
        request(message)

def request(message):
    handler.request(bot, message)

bot.polling(non_stop=True)