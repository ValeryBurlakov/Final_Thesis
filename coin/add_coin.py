import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from initialization.initialization import mydb, dp, cursor

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


# 7. Создаем команду `/add_coin`, чтобы пользователи могли добавлять монеты в свою коллекцию:
def add_coin_():
    @dp.message_handler(commands=['add_coin'])
    async def add_coin(message: types.Message, state: FSMContext):
        try:
            logging.info(f"Пользователь {message.from_user.username} выбрал команду /add_coin")
            user_id = message.from_user.id
            await message.answer("Введите название монеты:")
            await state.set_state("waiting_for_coin_name")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /add_coin: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.message_handler(state="waiting_for_coin_name")
    async def process_coin_name(message: types.Message, state: FSMContext):
        try:
            user_id = message.from_user.id
            coin_name = message.text
            # позволяет использовать переменные в других хендлерах
            await state.update_data(coin_name=coin_name)
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
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /add_coin: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.message_handler(state="waiting_for_collection")
    async def process_collection_name(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            coin_name = data.get('coin_name')
            collection_name = message.text  # Получаем название коллекции из команды
            cursor.execute("SELECT MAX(id) FROM coin")  # получили id нашей новой монеты из базы
            id_our_coin = cursor.fetchone()
            await state.update_data(id_coin=id_our_coin)
            cursor.execute("UPDATE coin SET collection_name = %s WHERE id = %s", (collection_name, id_our_coin[0]))
            mydb.commit()  # сохранили изменения
            cursor.execute("SELECT id from collection WHERE collection_name = %s", [collection_name])
            id_collection = cursor.fetchone()
            await state.update_data(id_collection=id_collection)
            cursor.execute("UPDATE coin SET collection_id = %s WHERE id = %s", (id_collection[0], id_our_coin[0]))
            mydb.commit()
            # Insert coin into photos table
            cursor.execute("INSERT INTO photos (coin_name, coin_id) VALUES (%s, %s)", (coin_name, id_our_coin[0],))
            mydb.commit()
            cursor.execute("SELECT _year FROM coin WHERE id = %s", id_our_coin)  # получили id нашей новой монеты из базы
            coin_year = cursor.fetchone()
            # позволяет использовать переменные в других хендлерах
            await state.update_data(collection_name=collection_name)
            await message.answer(f"Введите год монеты:", reply_markup=types.ReplyKeyboardRemove())
            await state.set_state("waiting_year")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /add_coin: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.message_handler(state="waiting_year")
    async def process_add_year(message: types.Message, state: FSMContext):
        try:
            coin_year = message.text  # Получаем year монеты из команды

            cursor.execute("SELECT MAX(id) FROM coin")  # получили id нашей новой монеты из базы
            id_our_coin = cursor.fetchone()
            await state.update_data(id_coin=id_our_coin)
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
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /add_coin: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.message_handler(state="add_state")
    async def states(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            coin_name = data.get('coin_name')
            id_collection = data.get('id_collection')
            coin_state = message.text
            collection_name = message.text  # Получаем year монеты из команды
            cursor.execute("SELECT MAX(id) FROM coin")  # получили id нашей новой монеты из базы
            id_our_coin = cursor.fetchone()
            cursor.execute("UPDATE coin SET state = %s WHERE id = %s", (collection_name, id_our_coin[0]))
            mydb.commit()  # сохранили изменения
            # update_query = "UPDATE photos SET coin_id = %s WHERE coin_name = %s"
            # cursor.execute(update_query, (id_our_coin[0], coin_name))
            update_query = "UPDATE photos SET coin_id = %s, collection_id = %s WHERE coin_name = %s"
            cursor.execute(update_query, (id_our_coin[0], id_collection[0], coin_name))
            mydb.commit()

            await message.answer(f"Вы выбрали состояние {coin_state}. Запись в базу данных прошла успешно.",
                                 reply_markup=types.ReplyKeyboardRemove())
            await message.answer(f'пришлите фото')
            await state.set_state("add_photo")  # переход в следующее состояние
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /add_coin: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.message_handler(state="add_photo", content_types=types.ContentType.PHOTO)
    async def process_photo(message: types.Message, state: FSMContext):
        try:
            # используем переменную collection_name из другого хендлера
            data = await state.get_data()
            collection_name = data.get('collection_name')
            coin_name = data.get('coin_name')
            coin_id = data.get('id_coin')
            # Получаем объект изображения
            photo = message.photo[-1]
            file_id = photo.file_id
            user_id = message.from_user.id
            # file_path = f'/home/valery/Photo_coin/{file_id}.jpg'
            file_path = f'/home/valery/Photo_coin/{user_id}/{collection_name}/{file_id}.jpg'
            # Сохраняем изображение на сервере
            await photo.download(destination_file=file_path)
            # Открываем файл и считываем его содержимое в бинарном виде
            with open(file_path, 'rb') as f:
                data = f.read()

            # Записываем данные изображения в базу данных
            update_query = "UPDATE photos SET image = %s, pathfile = %s WHERE coin_id = %s"
            cursor.execute(update_query, (data, file_path, coin_id[0]))
            mydb.commit()


            cursor.execute(
                "SELECT _description FROM coin WHERE id = (SELECT MAX(id) FROM coin)")  # получили id нашей новой монеты из базы
            coin_name = cursor.fetchone()
            await message.answer(f"Монета {coin_name[0]} добавлена в коллекцию.")
            await message.reply("Изображение успешно сохранено!")
            logging.info(f"команда /add_coin отработана")
            await state.finish()  # закончили с добавлением
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /add_coin: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()
