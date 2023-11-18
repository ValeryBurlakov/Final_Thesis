from aiogram import types
from initialization.initialization import mydb, dp, cursor

# 9. Создаем команду `/show_collection`, чтобы пользователи могли просмотреть свою коллекцию монет:
def show_collection():
    @dp.message_handler(commands=['show_collection'])
    async def show(message: types.Message):
        reply_markup = types.ReplyKeyboardRemove()
        user_id = message.from_user.id
        username = message.from_user.username
        cursor.execute("SELECT collection_name FROM collection WHERE user_id = %s", (user_id,))
        # обработка всего ответа от БД (fetchall)
        results = cursor.fetchall()
        rows = [row[0] for row in results]
        if len(rows) == 0:
            await message.answer('У вас еще нет коллекций', reply_markup=types.ReplyKeyboardRemove())
        else:
            # Отправьте строки в телеграм
            await message.answer(f'Ваши коллекции:\n' + '\n'.join(rows), reply_markup=types.ReplyKeyboardRemove())
