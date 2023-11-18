from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor

# 7. Создаем команду `/add_coin`, чтобы пользователи могли добавлять монеты в свою коллекцию:
def add_coin_():
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
        cursor.execute("SELECT _description FROM coin WHERE id = %s",
                       id_our_coin)  # получили id нашей новой монеты из базы
        coin_name = cursor.fetchone()

        await state.finish()  # закончили с добавлением

        await message.answer(f"Монета {coin_name[0]} добавлена в коллекцию.")
