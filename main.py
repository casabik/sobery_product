from data.config import bot_token
from telebot import types
import telebot
import random
import csv
import g4f


bot = telebot.TeleBot(bot_token)    


def check_users_amount(chat_id):
    amount = bot.get_chat_member_count(chat_id)
    if amount > 3 and amount < 8:
        return True
    else: 
        return False



def prepare_case():
    with open("data\game_data.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        key_words = next(reader)
        key_words = key_words[1:]
        key_words = random.sample(key_words, 2)
        key_words_str = ', '.join(key_words)
        print(key_words_str)
    message = f'Придумай задачу для программмиста, которыя бы имела бы следующие воства задач: {key_words_str}.' 
    request = [{"role": "user", "content": message}]
    try:
        case = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=request,
        )
        return [key_words, case]
    except Exception as e:
        print(e)
        print("Извините, произошла ошибка.")
        return None
    

@bot.callback_query_handler(func=lambda callback: True)
def button1(callback):
    if callback.data == 'Начать':
        chat_id = callback.message.chat.id
        if not check_users_amount(chat_id):
            bot.send_message(chat_id, 'Извините, вас слишком много или слишком мало для этой игры. В чате должно быть от трех до 6 участников для комфортной игры(')
        else:
            response = prepare_case()
            while True:
                if response is None:
                    response = prepare_case()
                    continue
                else:
                    break
            case = response[0]
            task_properties = response[1]
            bot.send_message(chat_id, f'Ребята, давайте начнем!\n\nВашей задачей будет:\n\n{task_properties}')



@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Начать', callback_data='Начать')
    markup.add(item1)
    bot.reply_to(message, "Привет! Я бот, который поможет вам поиграть в нашу игру 'Собери Продукт'!. Нажми на кнопку внизу, чтобы начать игру.", reply_markup=markup)



bot.infinity_polling(none_stop=True)

