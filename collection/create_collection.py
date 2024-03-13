# создание коллекции юзера
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def create_collection():
    @dp.message_handler(commands=['create_collection'])
    async def create(message: types.Message, state: FSMContext):
        try:
            logging.info(f"Пользователь {message.from_user.username} выбрал команду /create_collection")
            user_id = message.from_user.id

            # Проверяем количество коллекций пользователя
            cursor.execute("SELECT COUNT(*) FROM collection WHERE user_id = %s", (user_id,))
            collection_count = cursor.fetchone()[0]

            if collection_count >= 3:
                await message.answer(
                    "Вы больше не можете иметь коллекций. Пожалуйста, удалите текущие перед добавлением новой.")
                return

            await message.answer("Создаем коллекцию. Введите название:", reply_markup=types.ReplyKeyboardRemove())
            await state.set_state("waiting_create_collection")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /create_collection: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.message_handler(state="waiting_create_collection")
    async def process_collection_name(message: types.Message, state: FSMContext):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            collection_name = message.text  # Получаем название коллекции из команды

            cursor.execute("INSERT INTO collection (collection_name, user_id) VALUES (%s, %s)", (collection_name, user_id))

            mydb.commit()
            logging.info(f"команда /create_collection отработана")
            await state.finish()
            await message.answer(f"коллекция {collection_name} добавлена к юзеру @{username}.")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /create_collection: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()


# @dp.message_handler(commands=['create_collection'])
# async def add_coin(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#
#     await message.answer("Создаем коллекцию")
#     await state.set_state("waiting_create_collection")