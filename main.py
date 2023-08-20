# mysql-connector-python-8.1.0 protobuf-4.21.12

# 3. Импортируем необходимые модули в файл Python:

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import mysql.connector
from config import TOKEN2, PASSWORD, HOST, USER, DATABASE

# 4. Создаем соединение с базой данных в вашем файле Python:

mydb = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

# 5. Создаем экземпляры классов `Bot`, `Dispatcher` и `mysql.connector.Cursor` в файле Python:

storage = MemoryStorage()
bot = Bot(token=TOKEN2)
dp = Dispatcher(bot, storage=storage)
cursor = mydb.cursor()


# 6. Создаем команду `/start`, чтобы бот мог приветствовать пользователей и добавлять их в базу данных:

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверка наличия пользователя в базе данных
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
    count = cursor.fetchone()[0]

    if count > 0:
        # Пользователь уже существует, выполняется обновление его записи
        cursor.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
    else:
        # Пользователь не существует, выполняется вставка новой записи
        cursor.execute("INSERT INTO users (id, username, coin_collection) VALUES (%s, %s, %s)", (user_id, username, ""))

    mydb.commit()
    await message.reply("Привет! Ты зарегистрирован. '/help' - справка"
                        "")


# 7. Создаем команду `/add_coin`, чтобы пользователи могли добавлять монеты в свою коллекцию:


# @dp.message_handler(commands=['add_coin'])
# async def add_coin(message: types.Message):
#     user_id = message.from_user.id
#     coin_name = message.text[10:]  # Получаем название монеты из команды
#     cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
#     result = cursor.fetchone()
#     if result is not None:
#         coin_collection = result[0]
#     else:
#         coin_collection = ""
#     coin_collection += coin_name + ","
#     cursor.execute("UPDATE users SET coin_collection = %s WHERE id = %s", (coin_collection, user_id))
#     mydb.commit()
#     await message.reply(f"Монета {coin_name} добавлена в коллекцию.")


@dp.message_handler(commands=['add_coin'])
async def add_coin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer("Введите название монеты:")
    await state.set_state("waiting_for_coin_name")


# @dp.message_handler(state="waiting_for_coin_name")
# async def process_coin_name(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     coin_name = message.text  # Получаем название монеты из команды
#     cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
#     result = cursor.fetchone()
#     if result is not None:
#         coin_collection = result[0]
#     else:
#         coin_collection = ""
#     coin_collection += coin_name + ","
#     cursor.execute("UPDATE users SET coin_collection = %s WHERE id = %s", (coin_collection, user_id))
#     mydb.commit()
#     await state.finish()
#     await message.answer(f"Монета {coin_name} добавлена в коллекцию.")
@dp.message_handler(state="waiting_for_coin_name")
async def process_coin_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    coin_name = message.text  # Получаем название монеты из команды

    cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

    if result is not None:
        coin_collection = result[0]
    else:
        coin_collection = ","

    if coin_collection is not None:
        coin_collection += coin_name + ","
    else:
        coin_collection = coin_name + ","

    cursor.execute("UPDATE users SET coin_collection = %s WHERE id = %s", (coin_collection, user_id))
    mydb.commit()

    await state.finish()
    await message.answer(f"Монета {coin_name} добавлена в коллекцию.")


# 8. Создаем команду `/remove_coin`, чтобы пользователи могли удалять монеты из своей коллекции:

@dp.message_handler(commands=['remove_coin'])
async def remove_coin(message: types.Message):
    user_id = message.from_user.id
    coin_name = message.text[13:]  # Получаем название монеты из команды
    cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result is not None:
        coin_collection = result[0]
        coin_collection = coin_collection.replace(coin_name + ",", "")
        cursor.execute("UPDATE users SET coin_collection = %s WHERE id = %s", (coin_collection, user_id))
        mydb.commit()
        await message.reply(f"Монета {coin_name} удалена из коллекции.")
    else:
        await message.reply("Коллекция пуста.")


@dp.message_handler(commands=['help'])
async def on_help_command(message: types.Message):
    help_text = "список доступных команд:\n\n" \
                "/start - запуск бота\n" \
                "/help - справка\n" \
                "/add_coin - добавить монету\n" \
                "/remove_coin - удалить монету\n" \
                "/show_collection - показать коллекцию\n"
    await message.answer(help_text)


# dp.register_message_handler(on_help_command, commands="help") # обработчик команды в диспетчер??
# 9. Создаем команду `/show_collection`, чтобы пользователи могли просмотреть свою коллекцию монет:


@dp.message_handler(commands=['show_collection'])
async def show_collection(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result is not None:
        coin_collection = result[0]
        coins = coin_collection.split(",")
        coins.remove("")
        if len(coins) > 0:
            collection = "\n".join(coins)
            await message.reply(f"Коллекция:\n{collection}")
        else:
            await message.reply("Коллекция пуста.")
    else:
        await message.reply("Коллекция пуста.")


# 10. Запуск бота:

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
