import gspread as gs
import telebot
from telebot import types as ttp


# connecting to GoogleSheets
gs = gs.service_account(filename='../first_stuff/credentials.json')
sh = gs.open_by_key('1Q9bY3Vlc-He5eyyaZYllSE1h7XjRbduN2wR1zm4v31k')
worksheet = sh.sheet1
new_book = []

# making dict for searching by authors
authors = worksheet.col_values(2)
ids = worksheet.col_values(1)
aut_and_id = dict(zip(ids, authors))


# bot
bot = telebot.TeleBot('5862500583:AAFLMRZNlGi6aZ28c1LqmV9xpMG5mSmLQ9Q')


# bot greeting and work start
@bot.message_handler(commands=['start'])
def start(message):
    mess = f"Привет, <b>{message.from_user.first_name}</b>. \n Этот бот предназначен для подготовки к сочинениям по русскому языку и литературе. \n С его помощью вы можете найти краткие пересказы на интересующие вас произведения, вспомнить главных героев, а также посмотреть, какие проблемы расскрываются. \n  Также вы можете добавить прочитанное вами произведение" \
           f"\n Кнопка <b>/search</b> переведёт вас на поиск нужного вам произведения. \n Кнопка <b>/add_new_book</b> позволит вам добавить новое произведение. \n Кнопка <b>/back</b> позволит вам вернуться в главное меню"
    markup = ttp.ReplyKeyboardMarkup(row_width=2)
    button1 = ttp.KeyboardButton(text='/search')
    button2 = ttp.KeyboardButton(text='/add_new_book')
    markup.add(button1, button2)

    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


# adding to GS
@bot.message_handler(commands=['add_new_book'])
def add_new_book(message):
    # keyboard
    markup = ttp.ReplyKeyboardMarkup(row_width=2)
    button1 = ttp.KeyboardButton(text='/search')
    button2 = ttp.KeyboardButton(text='/add_new_book')
    back = ttp.KeyboardButton(text='/back')
    markup.add(button1, button2, back)

    mess1 = "Для того, чтобы добавить новое произведение вы должны знать формат заполнения. Он содержит: \n 1) Автор (пример: А.С.Пушкин) \n 2) Жанр произведения (роман\проза\стихотоворение\...) \n 3) Название (примеры: Капитанская дочка\Дубровский\...) \n 4) Главные герои (пример: Пётр Гринёв, Мария, ... ) \n 5) Проблемы произведения (нравственный выбор," \
            "подвиг во имя любви, ...) \n 6) Ссылка на краткий пересказ (желательно, чтобы это были ресурсы briefly.ru / litrekon.ru / obrazovaka.ru) \n Если вы хотите вернуться в меню, напишите /start"
    bot.send_message(message.chat.id, mess1, reply_markup=markup)
    sent = bot.send_message(message.chat.id, 'Введите параметры произведения (<b>каждый на новой стороке!</b>), как указано выше', parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(sent, adding)


def adding(message):
    if message.text != '/start' and message.text != '/back':
        parametrs = message.text
        last_row = int(worksheet.col_values(1)[-1])
        new =[str(last_row + 1)] + parametrs.strip().split()
        print(new)
        worksheet.append_row(new)
        bot.send_message(615893726, f"СООБЩЕНИЕ МОДЕРАТОРУ. \n Была добавлена книга с характеристиками {new}")
        sent = bot.send_message(message.chat.id, 'Книга была успешно добавлена! Спасибо за вклад!')
        bot.register_next_step_handler(sent, start)
    elif message.text == '/back':
        bot.send_message(message.chat.id, 'Добавление книги отменено! Введите /start, чтобы продолжить работу')


@bot.message_handler(commands=['search'])
def searcher(message):
    markup = ttp.ReplyKeyboardMarkup(row_width=2)
    back = ttp.KeyboardButton(text='/back')
    button_auth_search = ttp.KeyboardButton(text='Поиск по автору')
    button_name_search = ttp.KeyboardButton(text='Поиск по названию')
    markup.add(back, button_name_search, button_auth_search)

    mess = 'Выберите вид поиска:'
    bot.send_message(message.chat.id, mess, reply_markup=markup)
    sent = bot.send_message(message.chat.id, 'Если вы нажали на кнопку по ошибке, напишите /start или нажмите /back', reply_markup=markup)
    bot.register_next_step_handler(sent, search_by)


def search_by(message):
    if message.text != '/start' and message.text != '/back':
        if message.text == 'Поиск по автору':
            sent = bot.send_message(message.chat.id, 'Введите искомого автора \n Пример поиска: Л.Н.Толстой <b>без пробелов, соблюдая точки!</b>. Исклюяения: Джордж Оруэлл, Джон Гойн, О.Генри)', parse_mode='html')
            bot.register_next_step_handler(sent, search_by_author)


def search_by_author(message):
    if message.text != '/start' and message.text != '/back':
        value = str(message.text)
        for k, v in aut_and_id.items():
            if v == value:
                print(f"{k} -> {v}")
                bot.send_message(message.chat.id, f"{worksheet.row_values(k)}")


# bot polling
bot.polling(none_stop=True)
