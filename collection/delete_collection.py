from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor


def delete_collection():
    @dp.message_handler(commands=['delete_collection'])
    async def delete(message: types.Message, state: FSMContext):
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
