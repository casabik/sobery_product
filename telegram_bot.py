import telebot
from requests import get
from configuration.config import  bot_token
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import statistics
import os
import threading

bot = telebot.TeleBot(bot_token)
matplotlib.use('Agg')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет, Я могу помочь тебе найти комментарий в группе Вконтакте паблика Сибур! Напиши любой текст, и я найду подходящий комментарий!")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    query = message.text  
    answer = get("http://127.0.0.1:8000/get_comments/", params = {'user_text': query}).json()
    if answer['message'] == "Not found":  
        bot.send_message(message.chat.id, "К сожалению таких комментариев нет(")
    else:
        data = answer['comments']
        moods_list = []
        for com in data:
            mood_answer = get("http://127.0.0.1:8000/get_mood", params = {'id': com['comment_id']}).json()
            if mood_answer['mood'] is None:
                continue
            else:
                moods_list = np.concatenate([moods_list, mood_answer['mood']])
        
        moods_list = list(moods_list)
        moods_list = [int(i) for i in moods_list]
        average = statistics.mean(moods_list)
        median = statistics.median(moods_list)
        mode = statistics.mode(moods_list)
        plt.figure(figsize=(8, 6))

        plt.hist(moods_list, bins=10, color="red", edgecolor="black")
        plt.title("Гистограмма 1")
        plt.xlabel("Комметарий")
        plt.ylabel("Частота настроения")
        plt.savefig("hist1.png")
        plt.clf()
        percentages = [(moods_list.count(i) / len(moods_list)) * 100 for i in range(1, 11)]
        plt.bar(range(1, 11), percentages)
        plt.xlabel('Настроение')
        plt.ylabel('Процент')
        plt.title('Процентное часто встречаемости настроения')
        plt.savefig("hist2.png")
        media = [telebot.types.InputMediaPhoto(open("hist1.png", "rb")),
                telebot.types.InputMediaPhoto(open("hist2.png", "rb"))]
        bot.send_media_group(message.chat.id, media)
        bot.send_message(message.chat.id, f"Количвесто комментариев: " + str(len(moods_list)) +  '\nСреднее значение: ' + str(average) + '\n' + 'Медианное значение: ' + str(median) + '\n' + 'Мода: ' + str(mode) + "\n\nПример комметария:  " + str(data[0]['text']))
        os.remove("hist1.png")
        os.remove("hist2.png")
        plt.clf() 
bot.infinity_polling(none_stop=True)

