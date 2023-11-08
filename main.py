# mysql-connector-python-8.1.0 protobuf-4.21.12

# 3. Импортируем необходимые модули в файл Python:

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.builtin import CommandStart
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
# также можно использовать: commands=['start']
@dp.message_handler(CommandStart())
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


# @dp.message_handler(state="waiting_for_coin_name")
# async def process_coin_name(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     coin_name = message.text  # Получаем название монеты из команды
#
#     cursor.execute("SELECT coin_collection FROM users WHERE id = %s", (user_id,))
#     result = cursor.fetchone()
#
#     cursor.execute("INSERT INTO coin (_description, collection_id) VALUES (%s, %s)", (coin_name, user_id))
#     mydb.commit()
#     await message.answer(f'{coin_name}\n  Введите год монеты:')
#     # await state.finish()
#     await state.set_state("waiting_year")  # переход в следующее состояние
@dp.message_handler(state="waiting_for_coin_name")
async def process_coin_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    coin_name = message.text

    # Retrieve collections related to the user
    cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
    collection = cursor.fetchall()
    cursor.execute("INSERT INTO coin (_description) VALUES (%s)", (coin_name,))
    mydb.commit()

    # Create reply keyboard markup with collections
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for collection in collection:
        keyboard.add(types.KeyboardButton(text=collection[0]))

    await message.answer(f"Выберите в какую коллекцию добавить монету:", reply_markup=keyboard)
    await state.set_state("waiting_for_collection")


@dp.message_handler(state="waiting_for_collection")
async def process_coin_name(message: types.Message, state: FSMContext):
    collection_name = message.text  # Получаем year монеты из команды
    cursor.execute("SELECT MAX(id) FROM coin")  # получили id нашей новой монеты из базы
    id_our_coin = cursor.fetchone()
    cursor.execute("UPDATE coin SET collection_name = %s WHERE id = %s", (collection_name, id_our_coin[0]))
    mydb.commit()  # сохранили изменения
    cursor.execute("SELECT _year FROM coin WHERE id = %s", id_our_coin)  # получили id нашей новой монеты из базы
    coin_year = cursor.fetchone()
    await message.answer(f"Введите год монеты:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("waiting_year")


@dp.message_handler(state="waiting_year")
async def process_coin_name(message: types.Message, state: FSMContext):
    coin_year = message.text  # Получаем year монеты из команды

    cursor.execute("SELECT MAX(id) FROM coin")  # получили id нашей новой монеты из базы
    id_our_coin = cursor.fetchone()
    cursor.execute("UPDATE coin SET _year = %s WHERE id = %s", (coin_year, id_our_coin[0]))
    # 0 индекс так как результат fetchone это множество
    mydb.commit()  # сохранили изменения
    cursor.execute("SELECT _description FROM coin WHERE id = %s", id_our_coin)  # получили id нашей новой монеты из базы
    coin_name = cursor.fetchone()

    await state.finish()  # закончили с добавлением

    await message.answer(f"Монета {coin_name[0]} добавлена в коллекцию.")


# ===================================================================

# создание коллекции юзера


# @dp.message_handler(commands=['create_collection'])
# async def add_coin(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#
#     await message.answer("Создаем коллекцию")
#     await state.set_state("waiting_create_collection")
@dp.message_handler(commands=['create_collection'])
async def add_coin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверяем количество коллекций пользователя
    cursor.execute("SELECT COUNT(*) FROM collection WHERE user_id = %s", (user_id,))
    collection_count = cursor.fetchone()[0]

    if collection_count >= 3:
        await message.answer(
            "Вы больше не можете иметь коллекций. Пожалуйста, удалите текущие перед добавлением новой.")
        return

    await message.answer("Создаем коллекцию. Введите названиеЖ:", reply_markup=types.ReplyKeyboardRemove())
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


# =========================удаление коллекции======================================
@dp.message_handler(commands=['delete_collection'])
async def delete_collection(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Get the collections owned by the user
    cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
    collection_names = [name[0] for name in cursor.fetchall()]

    if not collection_names:
        await message.answer("У вас нет коллекций для удаления.")
        return

    # Create the keyboard markup with the collection names
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in collection_names])
    keyboard.add(types.KeyboardButton("Отмена"))

    await message.answer("Выберите коллекцию для удаления:", reply_markup=keyboard)
    await state.set_state("waiting_delete_collection")


@dp.message_handler(state="waiting_delete_collection")
async def process_delete_collection(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    collection_name = message.text

    if collection_name == "Отмена":
        await state.finish()
        await message.answer("Операция отменена.")
        return

    cursor.execute("DELETE FROM collection WHERE user_id = %s AND collection_name = %s", (user_id, collection_name))
    cursor.execute("DELETE FROM coin WHERE collection_name = %s", (collection_name,))
    mydb.commit()

    await state.finish()
    await message.answer(f"Коллекция {collection_name} удалена.", reply_markup=types.ReplyKeyboardRemove())


# ===============================================================


@dp.message_handler(commands=['add_photo'])
async def add_coin(message: types.Message, state: FSMContext):
    await message.answer(f'пришлите фото')
    await state.set_state("test_add_photo")  # переход в следующее состояние


@dp.message_handler(state="test_add_photo", content_types=types.ContentType.PHOTO)
async def process_photo(message: types.Message):
    # Получаем объект изображения
    photo = message.photo[-1]
    file_id = photo.file_id
    file_path = f'/home/valery/Photo_coin/{file_id}.jpg'

    # Сохраняем изображение на сервере
    await photo.download(destination=file_path)

    # Открываем файл и считываем его содержимое в бинарном виде
    with open(file_path, 'rb') as f:
        data = f.read()

    # Записываем данные изображения в базу данных
    cursor.execute("INSERT INTO photos (image, pathfile) VALUES (%s, %s)", (data, file_path))
    mydb.commit()

    await message.reply("Изображение успешно сохранено!")


@dp.message_handler(commands=['add_state'])
async def states(message: types.Message):
    # Создаем клавиатуру с вариантами состояния монеты
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [KeyboardButton(text='Отличное'), KeyboardButton(text='Среднее'), KeyboardButton(text='Плохое')]
    keyboard.add(*buttons)

    await message.answer("Выберите состояние монеты:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ['Отличное', 'Среднее', 'Плохое'])
async def process_choice(message: types.Message):
    coin_state = message.text
    idi = 3
    val = (coin_state, idi)
    # Ваш код для записи состояния монеты в базу данных MySQL
    sql = "UPDATE coin SET state = %s WHERE id = %s"
    cursor.execute(sql, val)
    mydb.commit()

    await message.answer(f"Вы выбрали состояние {coin_state}. Запись в базу данных прошла успешно.",
                         reply_markup=types.ReplyKeyboardRemove())


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


# @dp.message_handler(commands=['help'])
# async def on_help_command(message: types.Message):
#     help_text = "список доступных команд:\n\n" \
#                 "/start - запуск бота\n" \
#                 "/help - справка\n" \
#                 "/create_collection - создать коллекцию\n" \
#                 "/delete_collection - удалить коллекцию\n" \
#                 "/add_coin - добавить монету\n" \
#                 "/remove_coin - удалить монету\n" \
#                 "/add_photo - тест добавления монеты\n" \
#                 "/show_collection - показать коллекцию\n"
#
#     await message.answer(help_text)
@dp.message_handler(commands=['help'])
async def on_help_command(message: types.Message):
    help_text = "список доступных команд:\n\n" \
                "/start - запуск бота\n" \
                "/help - справка\n" \
                "/create_collection - создать коллекцию\n" \
                "/delete_collection - удалить коллекцию\n" \
                "/add_coin - добавить монету\n" \
                "/remove_coin - удалить монету\n" \
                "/add_photo - тест добавления монеты\n" \
                "/show_collection - показать коллекцию\n"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/start", "/help", "/create_collection", "/delete_collection",
               "/add_coin", "/remove_coin", "/add_photo", "/show_collection"]
    keyboard.add(*buttons)

    await message.answer(help_text, reply_markup=keyboard)


# dp.register_message_handler(on_help_command, commands="help") # обработчик команды в диспетчер??
# 9. Создаем команду `/show_collection`, чтобы пользователи могли просмотреть свою коллекцию монет:


@dp.message_handler(commands=['show_collection'])
async def show_collection(message: types.Message):
    reply_markup = types.ReplyKeyboardRemove()
    user_id = message.from_user.id
    username = message.from_user.username
    cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
    # обработка всего ответа от БД (fetchall)
    results = cursor.fetchall()
    rows = [row[0] for row in results]
    if len(rows) == 0:
        await message.answer('У вас еще нет коллекций', reply_markup=types.ReplyKeyboardRemove())
    else:
        # Отправьте строки в телеграм
        await message.answer(f'Ваши коллекции:\n' + '\n'.join(rows), reply_markup=types.ReplyKeyboardRemove())


# 10. Запуск бота:

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
