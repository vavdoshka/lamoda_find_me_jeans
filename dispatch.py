import telepot
from config import TOKEN, CHAT_ID

def dispatch_to_telegram_chat(msg_list):
    bot = telepot.Bot(TOKEN)
    bot.sendMessage("Hello Here What I found Today")
    for msg in msg_list:
        bot.sendMessage(CHAT_ID, msg)
    bot.sendMessage("See you")
