import logging

from aiogram.dispatcher.filters import CommandStart
from aiogram import types

from initialization.initialization import dp
# Создаем команду `/start`, чтобы бот мог приветствовать пользователей и добавлять их в базу данных:
# также можно использовать: commands=['start']

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def start_(cursor, mydb):
    @dp.message_handler(CommandStart())
    async def start(message: types.Message):
        logging.info(f"Пользователь {message.from_user.username} выбрал команду /show_collection")
        user_id = message.from_user.id
        username = message.from_user.username
        await message.answer("Start", reply_markup=types.ReplyKeyboardRemove())
        # Проверка наличия пользователя в базе данных
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Пользователь уже существует, выполняется обновление его записи
            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        else:
            # Пользователь не существует, выполняется вставка новой записи
            cursor.execute("INSERT INTO users (id, username, coin_collection) VALUES (%s, %s, %s)",
                           (user_id, username, ""))

        mydb.commit()
        await message.reply("Привет! Ты зарегистрирован. '/help' - справка"
                            "")
        logging.info(f"команда /start отработана")