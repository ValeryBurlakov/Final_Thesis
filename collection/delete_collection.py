import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def delete_collection():
    @dp.message_handler(commands=['delete_collection'])
    async def delete(message: types.Message, state: FSMContext):
        try:
            logging.info(f"Пользователь {message.from_user.username} выбрал команду /delete_collection")
            user_id = message.from_user.id
            # Get the collections owned by the user
            cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
            collection_names = [name[0] for name in cursor.fetchall()]
            if not collection_names:
                await message.answer("У вас нет коллекций для удаления.")
                return
            # Create the inline keyboard markup with the collection names
            keyboard = types.InlineKeyboardMarkup()
            for name in collection_names:
                button = types.InlineKeyboardButton(text=name, callback_data=f"delete_{name}")
                keyboard.add(button)
            keyboard.add(types.InlineKeyboardButton(text="Отмена", callback_data="cancel_delete"))
            await message.answer("Выберите коллекцию для удаления:", reply_markup=keyboard)
            await state.set_state("waiting_delete_collection")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /delete_collection: {e}")
            await message.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.callback_query_handler(lambda query: query.data.startswith('delete_'), state="waiting_delete_collection")
    async def process_delete_collection(callback_query: types.CallbackQuery, state: FSMContext):
        try:
            user_id = callback_query.from_user.id
            collection_name = callback_query.data.split('_')[1]
            cursor.execute("SELECT id FROM collection WHERE collection_name = %s", (collection_name,))
            collection_id = cursor.fetchone()
            cursor.execute("DELETE FROM collection WHERE user_id = %s AND collection_name = %s",
                           (user_id, collection_name))
            cursor.execute("DELETE FROM coin WHERE collection_id = %s", (collection_id[0],))
            cursor.execute("DELETE FROM photos WHERE collection_id = %s", (collection_id[0],))
            mydb.commit()
            logging.info(f"команда /delete_collection отработана")
            await state.finish()
            await callback_query.answer()
            await callback_query.message.answer(f"Коллекция {collection_name} удалена.",
                                                reply_markup=types.ReplyKeyboardRemove())
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /delete_collection: {e}")
            await callback_query.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()

    @dp.callback_query_handler(lambda query: query.data == 'cancel_delete', state="waiting_delete_collection")
    async def cancel_delete(callback_query: types.CallbackQuery, state: FSMContext):
        try:
            logging.info(f"команда /show_collection отменена")
            await state.finish()
            await callback_query.answer()
            await callback_query.message.answer("Операция отменена.")
        except Exception as e:
            logging.error(f"Ошибка в обработке команды /delete_collection: {e}")
            await callback_query.answer(f"Возникла ошибка при обработке команды. Попробуйте позднее")
            await state.finish()
