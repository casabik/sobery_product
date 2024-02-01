from data.config import bot_token
from telebot import types
import telebot
import random
import csv
import g4f


bot = telebot.TeleBot(bot_token)    

rounds_count = 0
people_round = 0
case = []
sum_people_count = {}

def get_table_data(title):
    result = 0
    with open("data\game_data.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        titles = next(reader)
        indexes = [titles.index(c) for c in case]

        for row in reader:
            if row[0] == title:
                for c in indexes:
                    result += int(row[c])
                    break
    return result




def get_channel_users(chat_id):
    members_count = bot.get_chat_members_count(chat_id)
    member_list =  []
    for i in range(members_count):
        try:
            member = bot.get_chat_member(chat_id, i)
            print(member)
            member_list.append(member.user.username)
        except Exception as e:
            print("Error getting member", i, ":", str(e))
    return member_list 
            
    



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
        deal = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=request,
        )
        return [key_words, deal]
    except Exception as e:
        print(e)
        print("Извините, произошла ошибка.")
        return None
    
def check_text_csv(text):
    with open("data\game_data.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if row[0] == text:
                return True
        return False
    

@bot.callback_query_handler(func=lambda callback: True)
def button1(callback):
    global case
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
    people_in_chat = get_channel_users(message.chat.id)
    for people in people_in_chat:
        sum_people_count[people] = 0
    print(sum_people_count)
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Начать', callback_data='Начать')
    markup.add(item1)
    bot.reply_to(message, "Привет! Я бот, который поможет вам поиграть в нашу игру 'Собери Продукт'!. Нажми на кнопку внизу, чтобы начать игру.", reply_markup=markup)



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global rounds_count, people_round, sum_people_count
    chat_id = message.chat.id
    username = message.from_user.username
    text = message.text
    if check_text_csv(text):
        sum = get_table_data(text)
        sum_people_count[username] += sum
        people_round += 1
        if people_round == 6: 
            rounds_count += 1
            people_round == 0
            people_in_chat = get_channel_users(message.chat.id)
            table = ""
            for man in people_in_chat:
                table += f"{man}: {sum_people_count[man]}\n"
            bot.send_message(chat_id, f'Результаты:\n\n{table}')
    else:
        bot.send_message(chat_id, f'Вы ввели несущствующую технологию()')


bot.infinity_polling(none_stop=True)

