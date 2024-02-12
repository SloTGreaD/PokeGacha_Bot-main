import telebot
from telebot import types
import random
import functions
import sqlite3
import logging
# Загрузка токена из переменных окружения
bot = telebot.TeleBot("6831587612:AAEUQ4m30-Pajetdnw0AwZ4omaNmzVkc-4o")

found_pokemon = []

helpinfo = """
<b>Помощь по использованию бота:</b>

/start - Начать поиск покемона
/help - Вывести это сообщение справки
/go - Попробовать поймать покемона
/keepgoing - Продолжить поиски
/skip - Пропустить и попробовать еще раз
/retry - Повторить попытку

<b>Дополнительные команды:</b>
/help - Вывести это сообщение справки

<b>Обратите внимание:</b>
- После каждой успешной или неудачной попытки поиска вам будут предоставлены соответствующие опции.
- Удачи в поисках покемонов!
"""

class PokemonBot:


    def __init__(self):
        # Словарь для хранения состояний пользователей
        self.states = {}
        # Создаем таблицу для спойманных покемонов
        conn = sqlite3.connect('pokedex.sql')
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS captured_pokemons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        found_pokemon VARCHAR(50),
        captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

    def capture_pokemon(self, user_id, found_pokemon):
        conn = sqlite3.connect('pokedex.sql')
        cur = conn.cursor()
        cur.execute("INSERT INTO captured_pokemons (user_id, found_pokemon) VALUES (?, ?)", (user_id, found_pokemon))
        conn.commit()
        conn.close()

    def start(self, message):
        
        conn = sqlite3.connect('pokedex.sql')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(50))')
        conn.commit()
        conn.close()
        # Приветственное сообщение при старте
        bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name}")
        self.show_go_buttons(message.chat.id)

    def handle_go_callback(self, call):
        chat_id = call.message.chat.id

        # Обработка нажатия кнопок "Go", "Keep going", "Skip"
        if call.data in ['go', 'keepgoing', 'skip']:
            
            if call.data in ['keepgoing', 'skip']:
                bot.delete_message(call.message.chat.id, call.message.message_id) 
                found_pokemon.clear()     # удаляет сообщение в котором было нажато "keepgoing"
            if random.choice([True, False]):
                self.states[chat_id] = 'choose_catch_or_skip'
                self.show_catch_or_skip_buttons(chat_id, call.message.message_id)
                found_pokemon.clear()
            else:
                self.states[chat_id] = 'choose_find_or_skip'
                self.back_to_start(chat_id, call.message.message_id)
                found_pokemon.clear()



        # Обработка нажатия кнопок "Catch", "Retry"
        elif call.data in ['catch', 'retry']:
            if call.data == 'retry':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                
            
            if random.choice([True, False]):
                self.states[chat_id] = 'choose_captured_or_retry'
                self.show_captured_or_retry_buttons(chat_id, call.message.message_id)
                
            else:
                self.states[chat_id] = 'choose_find_or_skip'
                self.show_captured_or_not_buttons(chat_id, call.message.message_id)

        # Обработка нажатия кнопки "Captured"
        elif call.data == 'captured':
            bot.send_message(chat_id, "Вы успешно поймали покемона!")
            self.capture_pokemon(call.message.chat.id, f"{found_pokemon[0]}")
        elif call.data == 'pokedex':
            self.show_pokedex(chat_id, call.message.message_id)
            
            

    def callback_handler(self, call):
        # Обработка команды "help"
        if call.data == 'help':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, helpinfo)

    def show_go_buttons(self, chat_id):
        # Отправка кнопки "Go" для начала поиска покемона
        markup = types.InlineKeyboardMarkup()

        button_go = types.InlineKeyboardButton('Go', callback_data='go')
        markup.add(button_go)

        bot.send_message(chat_id, "Press 'Go' to start searching for a Pokemon:", reply_markup=markup)

    def back_to_start(self, chat_id, message_id):
        # Возвращение к начальному состоянию после неудачной попытки
        markup = types.InlineKeyboardMarkup()
        button_back = types.InlineKeyboardButton('Keep going', callback_data='keepgoing')
        markup.add(button_back)
        bot.send_message(chat_id, 'You did not find anything', reply_markup=markup)
        #bot.delete_message(chat_id, message_id)


    def show_pokedex(self, chat_id):
        conn = sqlite3.connect('pokedex.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM captured_pokemons')
        info = cur.fetchall()
        pokedex = ''
        for el in info:
            # Убедитесь, что здесь правильно форматируете строку, например:
            pokedex += f"Pokemon: {el[0]}, Captured At: {el[1]}\n"
        cur.close()
        conn.close()

        # Проверка на пустую строку 'pokedex' перед отправкой
        if pokedex.strip() == '':
            bot.send_message(chat_id, "No Pokemons have been captured yet.")
        else:
            bot.send_message(chat_id, pokedex)



    def show_catch_or_skip_buttons(self, chat_id, message_id):
        # Отображение кнопок "Try to Catch" и "Skip" после успешной попытки
        markup = types.InlineKeyboardMarkup()
        button_catch = types.InlineKeyboardButton('Try to Catch', callback_data='catch')
        button_skip = types.InlineKeyboardButton('Skip', callback_data='skip')
        markup.add(button_catch, button_skip)

        # Отображение случайного покемона с весами
        chosen_pokemon = functions.pokemon_catch() #функция с вероятностями выпадения покемонов в файле functions.py
        pokemon_image = f'image/{chosen_pokemon.lower()}.png'
        with open(pokemon_image, 'rb') as pokemon_photo:
            found_pokemon.append(chosen_pokemon)
            sent_message = bot.send_photo(chat_id, pokemon_photo, caption=f"You found a {found_pokemon}! What would you like to do?", reply_markup=markup)
            self.states[chat_id] = {'message_id': sent_message.message_id, 'state': 'choose_catch_or_skip'}
            
            

    def show_captured_or_retry_buttons(self, chat_id, message_id):
        # Отображение кнопки "Keep going" после успешного захвата
        markup = types.InlineKeyboardMarkup()
        button_go = types.InlineKeyboardButton('Keep going', callback_data='go')
        markup.add(button_go)
        bot.send_message(chat_id, "You captured a Pokemon!", reply_markup=markup)
        
        #bot.delete_message(chat_id, message_id)

    def show_captured_or_not_buttons(self, chat_id, message_id):
        # Отображение кнопки "Try again" после неудачной попытки захвата
        markup = types.InlineKeyboardMarkup()
        button_try_again = types.InlineKeyboardButton('Try again', callback_data='retry')
        markup.add(button_try_again)
        bot.send_message(chat_id, 'Bad luck', reply_markup=markup)
        #bot.delete_message(chat_id, message_id)

    def run(self):
        # Запуск бота в режиме бесконечного опроса
        bot.infinity_polling()

# Если файл запущен напрямую (а не импортирован как модуль)
if __name__ == "__main__":
    # Создание экземпляра класса PokemonBot
    pokemon_bot = PokemonBot()

    # Обработчики сообщений и колбеков
    @bot.message_handler(commands=['start'])
    def start_wrapper(message):
        pokemon_bot.start(message)

    @bot.message_handler(commands=['pokedex'])
    def deploy_pokedex(message):
        chat_id = message.chat.id
        pokemon_bot.show_pokedex(chat_id)
        
    @bot.callback_query_handler(func=lambda call: call.data in ['go', 'keepgoing', 'skip', 'retry', 'catch'])
    def handle_go_callback_wrapper(call):
        markup = types.InlineKeyboardMarkup()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        pokemon_bot.handle_go_callback(call)
        

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler_wrapper(call):
        markup = types.InlineKeyboardMarkup()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        pokemon_bot.callback_handler(call)

    # Запуск бота
    pokemon_bot.run()
