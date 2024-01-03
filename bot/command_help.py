from aiogram import types
from initialization.initialization import mydb, dp, cursor


# @dp.message_handler(commands=['help'])
# async def on_help_command(message: types.Message):
#     help_text = "список доступных команд:\n\n" \
#                 "/start - запуск бота\n" \
#                 "/help - справка\n" \
#                 "/create_collection - создать коллекцию\n" \
#                 "/delete_collection - удалить коллекцию\n" \
#                 "/add_coin - добавить монету\n" \
#                 "/remove_coin - удалить монету\n" \
#                 "/add_photo - тест добавления монеты\n" \
#                 "/show_collection - показать коллекцию\n"
#
#     await message.answer(help_text)

def _help():
    @dp.message_handler(commands=['help'])
    async def on_help_command(message: types.Message):
        help_text = "список доступных команд:\n\n" \
                    "/start - запуск бота\n" \
                    "/help - справка\n" \
                    "/create_collection - создать коллекцию\n" \
                    "/delete_collection - удалить коллекцию\n" \
                    "/add_coin - добавить монету\n" \
                    "/remove_coin - удалить монету\n" \
                    "/add_photo - тест добавления монеты\n" \
                    "/show_collection - показать коллекцию\n"

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["/start", "/help", "/create_collection", "/delete_collection",
                   "/add_coin", "/remove_coin", "/add_photo", "/show_collection"]
        keyboard.add(*buttons)

        await message.answer(help_text, reply_markup=keyboard)

# dp.register_message_handler(on_help_command, commands="help") # обработчик команды в диспетчер??
