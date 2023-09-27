# mysql-connector-python-8.1.0 protobuf-4.21.12

# 3. Импортируем необходимые модули в файл Python:

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import mysql.connector
from config import TOKEN2, PASSWORD, HOST, USER, DATABASE
# import json

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


@dp.message_handler(commands=['add_coin'])
async def add_coin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer("Введите название монеты:")
    await state.set_state("waiting_for_coin_name")


@dp.message_handler(state="waiting_for_coin_name")
async def process_coin_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    coin_name = message.text  # Получаем название монеты из команды

    cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

    cursor.execute("INSERT INTO coin (_description, collection_id) VALUES (%s, %s)", (coin_name, user_id))
    mydb.commit()
    await message.answer(f'{coin_name}\n  Введите год монеты:')
    # await state.finish()
    await state.set_state("waiting_year") # переход в следующее состояние



@dp.message_handler(state="waiting_year")
async def process_coin_name(message: types.Message, state: FSMContext):
    coin_year = message.text  # Получаем year монеты из команды

    cursor.execute("SELECT MAX(id) FROM coin") # получили id нашей новой монеты из базы
    id_our_coin = cursor.fetchone()
    cursor.execute("UPDATE coin SET _year = %s WHERE id = %s", (coin_year, id_our_coin[0]))
    # 0 индекс так как результат fetchone это множество
    mydb.commit() # сохранили изменения
    cursor.execute("SELECT _description FROM coin WHERE id = %s", id_our_coin)  # получили id нашей новой монеты из базы
    coin_name = cursor.fetchone()

    await state.finish() # закончили с добавлением 

    await message.answer(f"Монета {coin_name[0]} добавлена в коллекцию.")

# ===================================================================

# создание коллекции юзера


@dp.message_handler(commands=['create_collection'])
async def add_coin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer("Создаем коллекцию")
    await state.set_state("waiting_create_collection")


@dp.message_handler(state="waiting_create_collection")
async def process_coin_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    collection_name = message.text  # Получаем название коллекции из команды

    cursor.execute("INSERT INTO collection (collection_name, user_id) VALUES (%s, %s)", (collection_name, user_id))

    mydb.commit()

    await state.finish()
    await message.answer(f"коллекция {collection_name} добавлена к юзеру @{username}.")
# ===============================================================


# @dp.message_handler(state="waiting_for_coin_photo", content_types=types.ContentType.PHOTO)
# async def process_coin_photo(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     coin_name = (await state.get_data())['coin_name']
#     photo_id = message.photo[-1].file_id  # Get the ID of the last (largest) photo sent by the user
#
#     # Save the photo ID in the photos table associated with the coin
#     cursor.execute("INSERT INTO photos (coin_id, photo_id) VALUES (NULL, %s)",
#                    (photo_id,))
#     coin_id = cursor.lastrowid
#     mydb.commit()
#
#     # Add the coin to the coin collection
#     cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
#     result = cursor.fetchone()
#
#     if result is not None:
#         coin_collection = result[0]
#     else:
#         coin_collection = ","
#
#     if coin_collection is not None:
#         coin_collection += coin_name + ","
#     else:
#         coin_collection = coin_name + ","
#
#     cursor.execute("UPDATE users SET coin_collection = %s WHERE id = %s", (coin_collection, user_id))
#     mydb.commit()
#
#     await state.finish()
#     await message.answer(f"Монета {coin_name} добавлена в коллекцию.")


# 8. Создаем команду `/remove_coin`, чтобы пользователи могли удалять монеты из своей коллекции:


@dp.message_handler(commands=['remove_coin'])
async def remove_coin(message: types.Message, state: FSMContext):
    # user_id = message.from_user.id
    await message.answer("Введите название монеты для удаления:")
    await state.set_state("waiting_for_coin_name_remove")


@dp.message_handler(state="waiting_for_coin_name_remove")
async def process_coin_name_remove(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    coin_name = message.text  # Получаем название монеты для удаления

    cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

    if result is not None:
        coin_collection = result[0]
    else:
        coin_collection = ""

    if coin_name in coin_collection:
        coin_collection = coin_collection.replace(coin_name + ",", "")
        cursor.execute("UPDATE users SET coin_collection = %s WHERE id = %s", (coin_collection, user_id))
        mydb.commit()
        await state.finish()
        await message.answer(f"Монета {coin_name} удалена из коллекции.")
    else:
        await state.finish()
        await message.answer(f"Монеты {coin_name} нет в коллекции.")


@dp.message_handler(commands=['help'])
async def on_help_command(message: types.Message):
    help_text = "список доступных команд:\n\n" \
                "/start - запуск бота\n" \
                "/help - справка\n" \
                "/create_collection - создать коллекцию\n"\
                "/add_coin - добавить монету\n" \
                "/remove_coin - удалить монету\n" \
                "/show_collection - показать коллекцию\n"
    await message.answer(help_text)


# dp.register_message_handler(on_help_command, commands="help") # обработчик команды в диспетчер??
# 9. Создаем команду `/show_collection`, чтобы пользователи могли просмотреть свою коллекцию монет:


@dp.message_handler(commands=['show_collection'])
async def show_collection(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
    # обработка всего ответа от БД (fetchall)
    results = cursor.fetchall()
    rows = [row[0] for row in results]
    if len(rows) == 0:
        await message.answer('У вас еще нет коллекций')
    else:
        # Отправьте строки в телеграм
        await message.answer('Ваши коллекции:\n' + '\n'.join(rows))


# 10. Запуск бота:

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
