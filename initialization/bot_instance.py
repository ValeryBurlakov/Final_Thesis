from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.config import TOKEN2


def create_bot_and_dispatcher():
    storage = MemoryStorage()
    bot = Bot(token=TOKEN2)
    dp = Dispatcher(bot, storage=storage)
    return bot, dp



