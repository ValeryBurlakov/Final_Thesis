from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from initialization.initialization import mydb, dp, cursor


# 9. Создаем команду `/show_collection`, чтобы пользователи могли просмотреть свою коллекцию монет:
# def show_collection():
#     @dp.message_handler(commands=['show_collection'])
#     async def show(message: types.Message):
#         reply_markup = types.ReplyKeyboardRemove()
#         user_id = message.from_user.id
#         username = message.from_user.username
#         cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
#         # обработка всего ответа от БД (fetchall)
#         results = cursor.fetchall()
#         rows = [row[0] for row in results]
#         if len(rows) == 0:
#             await message.answer('У вас еще нет коллекций', reply_markup=types.ReplyKeyboardRemove())
#         else:
#             # Отправьте строки в телеграм
#             await message.answer(f'Ваши коллекции:\n' + '\n'.join(rows), reply_markup=types.ReplyKeyboardRemove())

# Define the state for handling collection selection
class CollectionSelectionState(StatesGroup):
    selecting_collection = State()


def show_collection():
    @dp.message_handler(commands=['show_collection'])
    async def show(message: types.Message, state: FSMContext):
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

    @dp.callback_query_handler(lambda query: query.data.startswith('select_collection_'), state="select_collection_")
    async def select_collection(query: types.CallbackQuery, state: FSMContext):
        collection_name = query.data.replace('select_collection_', '')
        # user_id = query.from_user.id
        cursor.execute("SELECT _description FROM coin WHERE collection_name = %s", (collection_name,))
        results = cursor.fetchall()
        coins_list = [row[0] for row in results]

        if len(coins_list) == 0:
            await query.answer("В этой коллекции еще нет монет")
        else:
            # вывод монет списком
            # coins_message = f'Монеты в коллекции {collection_name}:\n'
            # for coin_name in coins_list:
            #     coins_message += f"- {coin_name}\n"
            # await query.message.answer(coins_message)
            # вывод монет кнопками
            keyboards = types.InlineKeyboardMarkup()
            for coin in coins_list:
                callback_data = f"select_coin_{coin}"
                keyboards.add(types.InlineKeyboardButton(coin, callback_data=callback_data))
            await query.message.answer('Выберите монету:', reply_markup=keyboards)

        await state.set_state("selecting_collection")

    @dp.callback_query_handler(lambda query: query.data.startswith('select_coin_'), state="selecting_collection")
    async def select_coin(query: types.CallbackQuery, state: FSMContext):
        coin_name = query.data.replace('select_coin_', '')
        cursor.execute("SELECT image, pathfile FROM photos WHERE coin_name = %s", (coin_name,))
        result = cursor.fetchone()
        if result:
            image_blob, pathfile = result
            # Convert the image_blob to a format suitable for sending in a message
            # Send the image along with any additional details
            await query.message.answer_photo(photo=image_blob, caption=f"Фото монеты {coin_name}")
        else:
            await query.answer(f"для монеты {coin_name} фото нет")

