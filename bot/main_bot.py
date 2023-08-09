import telebot
import re


TOKEN = "5913351179:AAFT7Ldsf_6WsEzZOhHS4kxhZDTmlauw0I0"
bot = telebot.TeleBot(TOKEN)

adblockwords = [
    'Big city lights',
    'Faces KBTU',
    'Codemode',
    'Codeye',
    'Altron academy'
]
warnings = {}


@bot.message_handler(commands=['info'])
def start(message):
    bot.send_message(message.chat.id, "Приветствую, это бот антирекламы."
                                      "При нарушений он выдает 1 предупреждение, 3 предупреждения = кик")
    bot.send_message(message.chat.id, "Для добавления нового триггер слова введите '/addword'")



@bot.message_handler(func=lambda message: len(re.findall(r'\b\w+\b', message.text)) >= 3 and any(
    re.search(pattern, message.text, re.IGNORECASE) for pattern in adblockwords))
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    member = bot.get_chat_member(chat_id, user_id)

    if member.status == "administrator" or member.status == "creator":
        bot.send_message(chat_id, 'Sigma')
    else:
        if user_id in warnings:
            warnings[user_id] += 1
        else:
            warnings[user_id] = 1


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
        adblockwords.append(new_word)
        bot.send_message(message.chat.id, f"Слово '{new_word}' было добавлено в триггер лист")
    else:
        bot.send_message(message.chat.id, "Недействительное слово. Введите новое:")


if __name__ == '__main__':
    bot.infinity_polling()
