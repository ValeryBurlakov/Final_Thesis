import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from initialization.initialization import mydb, dp, cursor

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def show_collection():
    @dp.message_handler(commands=['show_collection'])
    async def show(message: types.Message, state: FSMContext):
        logging.info(f"Пользователь {message.from_user.username} выбрал команду /show_collection")
        await message.answer("Show_collection", reply_markup=types.ReplyKeyboardRemove())
        try:
            user_id = message.from_user.id
            cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            rows = [row[0] for row in results]
            if len(rows) == 0:
                await message.answer('У вас еще нет коллекций')
            else:
                keyboard = types.InlineKeyboardMarkup()
                for collection_name in rows:
                    callback_data = f"select_collection_{collection_name}"
                    keyboard.add(types.InlineKeyboardButton(collection_name, callback_data=callback_data))
                await message.answer('Выберите коллекцию:', reply_markup=keyboard)
                await state.set_state("select_collection_")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /show_collection: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.callback_query_handler(lambda query: query.data.startswith('select_collection_'), state="select_collection_")
    async def select_collection(query: types.CallbackQuery, state: FSMContext):
        try:
            collection_name = query.data.replace('select_collection_', '')
            # cursor.execute("SELECT _description, _year FROM coin WHERE collection_name = %s", (collection_name,))
            cursor.execute("SELECT _description, _year, id, state FROM coin WHERE collection_name = %s",
                           (collection_name,))
            results = cursor.fetchall()
            coins_list = [(row[0], row[1], row[2], row[3]) for row in results]
            if len(coins_list) == 0:
                await query.answer("В этой коллекции еще нет монет")
            else:
                keyboards = types.InlineKeyboardMarkup()
                for coin, year, id, coinstate in coins_list:
                    callback_data = f"select_coin_{collection_name}_{coin}_{year}_{id}_{coinstate}"
                    keyboards.add(types.InlineKeyboardButton(f"{coin} ({year})", callback_data=callback_data))
                await query.message.answer('Выберите монету:', reply_markup=keyboards)
            await state.set_state("selecting_collection")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /show_collection: {e}")
            await query.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.callback_query_handler(lambda query: query.data.startswith('select_coin_'), state="selecting_collection")
    async def select_coin(query: types.CallbackQuery, state: FSMContext):
        try:
            data = query.data.replace('select_coin_', '').split('_')
            collection_name, coin_name, year, id, coinstate = data[0], data[1], data[2], data[3], data[4]
            # cursor.execute("SELECT image, pathfile FROM photos WHERE coin_name = %s AND _year = %s", (coin_name, year,))
            # cursor.execute("SELECT image, pathfile FROM photos WHERE coin_name = %s", (coin_name,))
            cursor.execute("SELECT image, pathfile FROM photos WHERE id = %s", (id,))
            result = cursor.fetchone()
            if result:
                image_blob, pathfile = result
                await query.message.answer_photo(photo=image_blob,
                                                 caption=f"Фото монеты: {coin_name}. Состояние: {coinstate}")
            else:
                await query.answer(f"для монеты {coin_name} фото нет")
            logging.info(f"команда /show_collection отработана")

            # await state.finish()  # закончили
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /show_collection: {e}")
            await query.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")

        await state.finish()
