import logging

from aiogram import types
from initialization.initialization import mydb, dp, cursor

logging.basicConfig(filename='logging_collection.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def _help():
    @dp.message_handler(commands=['help'])
    async def on_help_command(message: types.Message):
        logging.info(f"Пользователь {message.from_user.username} выбрал команду /help")
        help_text = "список доступных команд:\n\n" \
                    "/start - запуск бота\n" \
                    "/help - справка\n" \
                    "/create_collection - создать коллекцию\n" \
                    "/delete_collection - удалить коллекцию\n" \
                    "/add_coin - добавить монету\n" \
                    "/remove_coin - удалить монету\n" \
                    "/show_collection - показать коллекцию\n"

        # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # buttons = ["/start", "/help", "/create_collection", "/delete_collection",
        #            "/add_coin", "/remove_coin", "/show_collection"]
        # keyboard.add(*buttons)

        # await message.answer(help_text, reply_markup=keyboard)

        await message.answer(help_text)
        logging.info(f"команда /help отработана")

