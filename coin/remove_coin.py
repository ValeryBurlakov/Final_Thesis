from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor


# 8. Создаем команду `/remove_coin`, чтобы пользователи могли удалять монеты из своей коллекции:
def remove_coin():
    @dp.message_handler(commands=['remove_coin'])
    async def remove(message: types.Message, state: FSMContext):
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
