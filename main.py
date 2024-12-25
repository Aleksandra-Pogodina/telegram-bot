import telebot
from bot import TestBot
import config

TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)

test_bot_instance = TestBot(bot)
test_bot_instance.start()

bot.polling(none_stop=True)