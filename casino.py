import telebot
import sqlite3
from random import randint
from telebot import types
import time
import sys

sys.set_int_max_str_digits(0)

bot = telebot.TeleBot('...') # Токен бота

db = sqlite3.connect('casino.db',check_same_thread=False)
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users(
            login TEXT,
            cash BIGINT,
            houses BIGINT
)""")
db.commit

@bot.message_handler(commands=['start'])
def start(message):
    # bot.delete_message(message.chat.id, message.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='🎰Играть🎰')
    btn2 = types.KeyboardButton(text='💰Баланс💰')
    btn3 = types.KeyboardButton(text='🗒️Правила🗒️')
    btn4 = types.KeyboardButton(text='🏠Дома🏠')
    markup.add(btn1)
    markup.add(btn2, btn4)
    markup.add(btn3)
    bot.send_message(message.chat.id, text= '🎰 Добро пожаловать в казино! 🎰',reply_markup=markup)
    user_login = int(message.from_user.id)
    sql.execute(f"SELECT login FROM users WHERE login = '{user_login}'")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?, ?, ?)", (user_login, 1000, 1))
        db.commit()
    else:
        pass
@bot.message_handler(content_types='text')
def balance(message):
    if message.text == '💰Баланс💰':
        # bot.delete_message(message.chat.id, message.id)
        user_login = int(message.from_user.id)
        for i in sql.execute(f"SELECT cash FROM users WHERE login = '{user_login}'"):
            balance = i[0]
            bot.send_message(message.from_user.id, text=(f'💰Ваш баланс: {balance}$ 💰'))
    elif message.text == '🗒️Правила🗒️':
        bot.send_message(message.chat.id, text='<b>🎰Крутите слоты и выигрывайте деньги!🎰</b>\n(если балланс меньше 0, обратитесь в поддержку)\n<b>🏠На заработанные деньги вы можете купить себе дом, или продать если не хватает денег🏠</b>',parse_mode='HTML')
        # bot.delete_message(message.chat.id, message.id)
    elif message.text == '🎰Играть🎰':
        # bot.delete_message(message.chat.id, message.id)
        user_login = int(message.from_user.id)
        for i in sql.execute(f"SELECT cash FROM users WHERE login = '{user_login}'"):
            balance = i[0]
        if balance < 1 :
            bot.send_message(message.chat.id, text='❗️У вас недостаточно средств❗️')
        else:
            dice = bot.send_dice(message.chat.id, emoji='🎰').dice.value
            time.sleep(2)
            if dice > 50:
                if dice == 64:
                    bot.send_message(message.chat.id, text='💰Джекпот! Вы выиграли 10000$!💰')
                    sql.execute(f'UPDATE users SET cash = {10000 + balance} WHERE login ="{user_login}"')
                    db.commit()
                else:
                    bot.send_message(message.chat.id, text=f'💵Вы выиграли 100$!💵')
                    sql.execute(f'UPDATE users SET cash = {100 + balance} WHERE login ="{user_login}"')
                    db.commit()
            else:
                if dice == 1:
                    bot.send_message(message.chat.id, text='Вы ничего не выйграли')
                elif dice == 43:
                    bot.send_message(message.chat.id, text='💵Вы выиграли 500$!💵')
                    sql.execute(f'UPDATE users SET cash = {500 + balance} WHERE login ="{user_login}"')
                    db.commit()
                elif dice == 22:
                    bot.send_message(message.chat.id, text='💵Вы выиграли 500$!💵')
                    sql.execute(f'UPDATE users SET cash = {500 + balance} WHERE login ="{user_login}"')
                    db.commit()
                else:
                    bot.send_message(message.chat.id, text='💸Вы проиграли 100$💸')
                    sql.execute(f'UPDATE users SET cash = {balance - 100} WHERE login ="{user_login}"')
                    db.commit()
    elif message.text == '🏠Дома🏠':
        a = types.ReplyKeyboardRemove()
        user_login = int(message.from_user.id)
        sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'")
        housemany = sql.fetchone()[0]
        if housemany == 1:
            bot.send_message(message.chat.id, text='🏠У вас 1 дом🏠')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
            btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
            btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
            markup.add(btn1, btn2)
            markup.add(btn3)
            bot.send_message(message.chat.id, text='Что желаете сделать?',reply_markup=markup)
            # bot.register_next_step_handler(message, callback='sell')
        else:
            n = housemany
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.send_message(message.chat.id, text=f'🏠У вас {n} домов🏠')
            btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
            btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
            btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
            markup.add(btn1, btn2)
            markup.add(btn3)
            bot.send_message(message.chat.id, text='Что желаете сделать?',reply_markup=markup)
    elif message.text == "🏠Продать дом🏠":
        a = types.ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, text='⬇️Укажите колличество домов⬇️\n(стоимость 1 дома - 10000$)\n(Чтобы выйти введите 0)', reply_markup=a)
        bot.register_next_step_handler(msg, callback=sell)
    elif message.text == '🏠Купить дом🏠':
        a = types.ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, text='⬇️Укажите колличество домов⬇️\n(стоимость 1 дома - 10000$)\n(Чтобы выйти введите 0)', reply_markup=a)
        bot.register_next_step_handler(msg, callback=buy)
    elif message.text == '📝Вернуться в меню📝':
        # bot.delete_message(message.chat.id, message.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text='🎰Играть🎰')
        btn2 = types.KeyboardButton(text='💰Баланс💰')
        btn3 = types.KeyboardButton(text='🗒️Правила🗒️')
        btn4 = types.KeyboardButton(text='🏠Дома🏠')
        markup.add(btn1)
        markup.add(btn2, btn4)
        markup.add(btn3)
        bot.send_message(message.chat.id, text= '🎰 Добро пожаловать в казино! 🎰',reply_markup=markup)
    else:
        start(message)
@bot.callback_query_handler(func= lambda call: call.data =='sell')
def sell(call):
    # message = bot.message_handler(content_types=['text'])
    # call = int(call)
    message = int(call.text)
    user_login = int(call.from_user.id)
    # print(call.text)
    sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'")
    housemany = int(sql.fetchone()[0])
    if message == 0:
        for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                houses = i[0]
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
                btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
                btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
                markup.add(btn1, btn2)
                markup.add(btn3)
                bot.send_message(call.chat.id, text=f'🏠У вас {houses} домов🏠',reply_markup=markup)
                bot.send_message(call.chat.id, text='Что желаете сделать?')
    else:
        if housemany >= message:
            for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                houses = i[0]
                for i in sql.execute(f"SELECT cash FROM users WHERE login = '{user_login}'"):
                    balance = i[0]
                    money = int(call.text) * 10000
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
                    btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
                    btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
                    markup.add(btn1, btn2)
                    markup.add(btn3)
                    bot.send_message(call.chat.id, text='🏠Дом продан!🏠\nДеньги зачислены на счёт', reply_markup=markup)
                    sql.execute(f'UPDATE users SET houses = {houses - message} WHERE login ="{user_login}"')
                    sql.execute(f'UPDATE users SET cash = {balance + money} WHERE login ="{user_login}"')
                    db.commit()
                    for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                            houses = i[0]
                            bot.send_message(call.chat.id, text=f'🏠Теперь у вас {houses} домов🏠')
        elif housemany == 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
            btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
            btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
            markup.add(btn1, btn2)
            markup.add(btn3)
            bot.send_message(call.chat.id, text='🏠У вас нет домов🏠',reply_markup=markup)
        else:
            for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                houses = i[0]
                if houses == 1:
                    msg = bot.send_message(call.chat.id, text=f'❗️Указано неверное колличество домов❗️\n🏠У вас 1 дом🏠\n(Чтобы выйти введите 0)')
                else:
                    msg = bot.send_message(call.chat.id, text=f'❗️Указано неверное колличество домов❗️\n🏠У вас {houses} домов🏠\n(Чтобы выйти введите 0)')
                    bot.register_next_step_handler(msg, callback=sell)

@bot.callback_query_handler(func=lambda call: call.data =='buy')
def buy(call):
    user_login = int(call.from_user.id)
    buyhouse = 10000 * int(call.text)
    message = int(call.text)
    for i in sql.execute(f"SELECT cash FROM users WHERE login = '{user_login}'"):
            balance = i[0]
            # print(balance)
            # print(buyhouse)
            if message == 0:
                for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                        houses = i[0]
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
                        btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
                        btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
                        markup.add(btn1, btn2)
                        markup.add(btn3)
                        bot.send_message(call.chat.id, text=f'🏠У вас {houses} домов🏠',reply_markup=markup)
                        bot.send_message(call.chat.id, text='Что желаете сделать?')
                
            else:
                if balance >= buyhouse:
                    for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                        houses = i[0]
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton(text='🏠Продать дом🏠')
                        btn2 = types.KeyboardButton(text='🏠Купить дом🏠')
                        btn3 = types.KeyboardButton(text='📝Вернуться в меню📝')
                        markup.add(btn1, btn2)
                        markup.add(btn3)
                        bot.send_message(call.chat.id, text='🔑Вот ваши ключи!🔑',reply_markup=markup)
                        sql.execute(f'UPDATE users SET houses = {houses + message} WHERE login ="{user_login}"')
                        sql.execute(f'UPDATE users SET cash = {balance - buyhouse} WHERE login ="{user_login}"')
                        db.commit()
                        for i in sql.execute(f"SELECT houses FROM users WHERE login = '{user_login}'"):
                            houses = i[0]
                            bot.send_message(call.chat.id, text=f'🏠Теперь у вас {houses} домов🏠')
                else:
                    msg = bot.send_message(call.chat.id, text='❗️Недостаточно средств❗️\n ❗️Повторите попытку❗️\n(Чтобы выйти введите 0)')
                    bot.register_next_step_handler(msg, callback=buy)

bot.infinity_polling()