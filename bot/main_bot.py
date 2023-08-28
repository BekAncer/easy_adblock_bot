import telebot
import re


TOKEN = "your_token"
bot = telebot.TeleBot(TOKEN)
txt_path = 'adblockwords.txt'
warnings = {}


with open(txt_path, 'r') as file:
    ad_block_word_list = file.readlines()
ad_block_words = [line.strip() for line in ad_block_word_list]
print(ad_block_words)


@bot.message_handler(commands=['info'])
def start(message):
    bot.send_message(message.chat.id, "Приветствую, это бот антирекламы."
                                      "При нарушений он выдает 1 предупреждение, 3 предупреждения = кик")
    bot.send_message(message.chat.id, "Для добавления нового триггер слова введите '/addword'")


@bot.message_handler(func=lambda message: len(re.findall(r'\b\w+\b', message.text)) >= 3 and any(
    re.search(pattern, message.text, re.IGNORECASE) for pattern in ad_block_words))
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(chat_id, user_id)

    if member.status == "administrator" or member.status == "creator":
        bot.send_message(chat_id, 'Sigma')
    else:
        bot.delete_message(chat_id, message.message_id)
        if user_id in warnings:
            if warnings[user_id] < 2:
                warnings[user_id] += 1
                bot.send_message(message.chat.id, f'Пользователю @{user_id} выдано {warnings[user_id]}/3 предупреждений')
            else:
                bot.kick_chat_member(chat_id, user_id)
                bot.send_message(message.chat.id,f'пользователь @{user_id} был кикнут в связи с 3 нарушениями')
        else:
            warnings[user_id] = 1
            bot.send_message(message.chat.id,f'Пользователю @{user_id} выдано 1/3 предупреждений')


@bot.message_handler(commands=['addword'])
def add_word(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(chat_id, user_id)

    if member.status == "administrator" or member.status == "creator":
        msg = bot.send_message(chat_id, "Введите триггер слово, ответом на это сообщение:")
        bot.register_next_step_handler(msg, process_new_word)
    else:
        bot.send_message(chat_id, "у вас нет прав на добавления слов триггеров")


def process_new_word(message):
    new_word = message.text.strip()

    if new_word:
        with open(txt_path, 'a') as file:
            file.write('\n' + new_word)
        with open(txt_path, 'r') as file:
            refreshed_list = file.readlines()
        global ad_block_words
        ad_block_words = [line.strip() for line in refreshed_list]
        bot.send_message(message.chat.id, f"Слово '{new_word}' было добавлено в триггер лист")
    else:
        bot.send_message(message.chat.id, "Недействительное слово. Введите новое:")


if __name__ == '__main__':
    bot.infinity_polling()
    
