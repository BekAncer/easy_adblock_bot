import telebot
import re


TOKEN = "your_token"
bot = telebot.TeleBot(TOKEN)
txt_path1 = 'adblockwords.txt'
txt_path2 = 'adminmembers.txt'


with open(txt_path1, 'r') as file:  # прочитывает все слова в документе adblockwords.txt
    ad_block_word_list = file.readlines()
ad_block_words = [line.strip() for line in ad_block_word_list]


with open(txt_path2, 'r') as file:  # прочитывает все слова в документе adminmembers.txt
    admin_list = file.readlines()
admins = [line.strip() for line in admin_list]
print(admins)

warnings = {}


# _______________________________|команда информаций|______________________
@bot.message_handler(commands=['info'])
def start(message):
    bot.send_message(message.chat.id, "Приветствую, это бот антирекламы."
                                      "При нарушений он выдает 1 предупреждение, 3 предупреждения = кик")
    bot.send_message(message.chat.id, "Для добавления нового триггер слова введите '/addword'")
# _________________________________________________________________________


# ______________________________|проверка на триггеры|_____________________
@bot.message_handler(func=lambda message: len(re.findall(r'\b\w+\b', message.text)) >= 3 and any(re.search(pattern, message.text, re.IGNORECASE) for pattern in ad_block_words))
def handle_message(message):  # проверка на триггер слова
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = bot.get_chat_member(chat_id, user_id).user.username

    if username in admins:
        bot.send_message(chat_id, 'Good')
    else:
        bot.delete_message(chat_id, message.message_id)
        if user_id in warnings:
            if warnings[user_id] < 2:
                warnings[user_id] += 1
                bot.send_message(message.chat.id, f'Пользователю @{username}'
                                                  f' выдано {warnings[user_id]}/3 предупреждений')
            else:
                bot.kick_chat_member(chat_id, user_id)
                bot.send_message(message.chat.id, f'пользователь @{username} был кикнут в связи с 3 нарушениями')
        else:
            warnings[user_id] = 1
            bot.send_message(message.chat.id, f'Пользователю @{username} выдано 1/3 предупреждений')
# _________________________________________________________________________


# _____________________________|команда новое слово|______________________________________
@bot.message_handler(commands=['add_word'])
def add_word(message):  # добавление нового слова
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = bot.get_chat_member(chat_id, user_id).user.username

    if username in admins:
        msg = bot.send_message(chat_id, "Введите триггер слово, ответом на это сообщение:")
        bot.register_next_step_handler(msg, process_new_word)
    else:
        bot.send_message(chat_id, "у вас нет прав на добавления слов триггеров")


def process_new_word(message):  # обработка файла adblockwords
    new_word = message.text.strip()

    if new_word:
        with open(txt_path1, 'a') as file1:
            file1.write('\n' + new_word)
        with open(txt_path1, 'r') as file2:
            refreshed_list = file2.readlines()
        global ad_block_words
        ad_block_words = [line.strip() for line in refreshed_list]
        bot.send_message(message.chat.id, f"Слово '{new_word}' было добавлено в триггер лист")
    else:
        bot.send_message(message.chat.id, "Недействительное слово. Введите новое:")
# _________________________________________________________________________


# __________________________|команда нового админа|________________________
@bot.message_handler(commands=['add_admin'])
def add_word(message):  # добавление нового слова
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = bot.get_chat_member(chat_id, user_id).user.username

    if username in admins:
        msg = bot.send_message(chat_id, "Введите username, ответом на это сообщение:")
        bot.register_next_step_handler(msg, process_new_admin)
    else:
        bot.send_message(chat_id, "у вас нет прав на добавления слов триггеров")


def process_new_admin(message):  # обработка файла adminmembers
    global admins
    new_admin = message.text.strip()[1:]
    print(new_admin)

    if new_admin:
        if new_admin in admins:
            bot.send_message(message.chat.id, "Пользователь уже есть в списке")
        else:
            with open(txt_path2, 'a') as file1:
                file1.write('\n' + new_admin)
            with open(txt_path2, 'r') as file2:
                refreshed_list = file2.readlines()
            admins = [line.strip() for line in refreshed_list]
            bot.send_message(message.chat.id, f"Новый админ '{new_admin}' был добавлен в список")
# _________________________________________________________________________


if __name__ == '__main__':
    bot.infinity_polling()
