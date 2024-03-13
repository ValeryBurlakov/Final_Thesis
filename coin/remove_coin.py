import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def remove_coin():
    @dp.message_handler(commands=['remove_coin'])
    async def remove(message: types.Message, state: FSMContext):
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
                await state.set_state("waiting_for_collection_remove")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /show_collection: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.callback_query_handler(lambda query: 'select_collection_' in query.data, state="waiting_for_collection_remove")
    async def select_coin_for_removal(query: types.CallbackQuery, state: FSMContext):
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
            await state.set_state("waiting_for_coin_remove")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /show_collection: {e}")
            await query.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.callback_query_handler(lambda query: 'select_coin_' in query.data, state="waiting_for_coin_remove")
    async def remove_selected_coin(query: types.CallbackQuery, state: FSMContext):
        try:
            data = query.data.replace('select_coin_', '').split('_')
            collection_name, coin_name, year, id, coinstate = data[0], data[1], data[2], data[3], data[4]
            # coin_id = query.data.replace('select_coin_', '')
            # print(collection_name, coin_name, year, id, coinstate)
            cursor.execute("DELETE FROM coin WHERE id = %s", (id,))
            mydb.commit()
            await query.message.answer("Монета успешно удалена")
            await state.finish()
        except Exception as e:
            logging.error(f"Ошибка при удалении выбранной монеты: {e}")
            await query.message.answer("Возникла ошибка при удалении монеты. Попробуйте позднее")
            await state.finish()
