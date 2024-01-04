from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from initialization.initialization import mydb, dp, cursor


# 7. Создаем команду `/add_coin`, чтобы пользователи могли добавлять монеты в свою коллекцию:
def add_coin_():
    @dp.message_handler(commands=['add_coin'])
    async def add_coin(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        await message.answer("Введите название монеты:")
        await state.set_state("waiting_for_coin_name")

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
        cursor.execute("SELECT id from collection WHERE collection_name = %s", [collection_name])
        id_collection = cursor.fetchone()
        cursor.execute("UPDATE coin SET collection_id = %s WHERE id = %s", (id_collection[0], id_our_coin[0]))
        mydb.commit()
        cursor.execute("SELECT _year FROM coin WHERE id = %s", id_our_coin)  # получили id нашей новой монеты из базы
        coin_year = cursor.fetchone()
        # позволяет использовать переменные в других хендлерах
        await state.update_data(collection_name=collection_name)
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
        cursor.execute("SELECT _description FROM coin WHERE id = %s",
                       id_our_coin)  # получили id нашей новой монеты из базы
        coin_name = cursor.fetchone()
        # await message.answer("Выберите состояние монеты:")
        keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = [KeyboardButton(text='Отличное'), KeyboardButton(text='Среднее'), KeyboardButton(text='Плохое')]
        keyboard.add(*buttons)
        await message.answer("Выберите состояние монеты:", reply_markup=keyboard)
        await state.set_state("add_state")

    @dp.message_handler(state="add_state")
    async def states(message: types.Message, state: FSMContext):
        coin_state = message.text
        collection_name = message.text  # Получаем year монеты из команды
        cursor.execute("SELECT MAX(id) FROM coin")  # получили id нашей новой монеты из базы
        id_our_coin = cursor.fetchone()
        cursor.execute("UPDATE coin SET state = %s WHERE id = %s", (collection_name, id_our_coin[0]))
        mydb.commit()  # сохранили изменения

        await message.answer(f"Вы выбрали состояние {coin_state}. Запись в базу данных прошла успешно.",
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f'пришлите фото')
        await state.set_state("add_photo")  # переход в следующее состояние

    @dp.message_handler(state="add_photo", content_types=types.ContentType.PHOTO)
    async def process_photo(message: types.Message, state: FSMContext):
        # используем переменную collection_name из другого хендлера
        data = await state.get_data()
        collection_name = data.get('collection_name')
        # Получаем объект изображения
        photo = message.photo[-1]
        file_id = photo.file_id
        user_id = message.from_user.id
        # file_path = f'/home/valery/Photo_coin/{file_id}.jpg'
        file_path = f'/home/valery/Photo_coin/{user_id}/{collection_name}/{file_id}.jpg'
        # Сохраняем изображение на сервере
        await photo.download(destination=file_path)
        # Открываем файл и считываем его содержимое в бинарном виде
        with open(file_path, 'rb') as f:
            data = f.read()

        # Записываем данные изображения в базу данных
        cursor.execute("INSERT INTO photos (image, pathfile) VALUES (%s, %s)", (data, file_path))
        mydb.commit()
        await state.finish()  # закончили с добавлением
        cursor.execute(
            "SELECT _description FROM coin WHERE id = (SELECT MAX(id) FROM coin)")  # получили id нашей новой монеты из базы
        coin_name = cursor.fetchone()
        await message.answer(f"Монета {coin_name[0]} добавлена в коллекцию.")
        await message.reply("Изображение успешно сохранено!")
