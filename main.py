# mysql-connector-python-8.1.0 protobuf-4.21.12
# Импорт необходимых модулей в файл Python:
from aiogram.utils import executor
from coin.add_coin import add_coin_
from coin.add_photo import add_photo
from coin.add_state import add_state
from bot.command_help import _help
from bot.command_start import start_
from collection.create_collection import create_collection
from collection.delete_collection import delete_collection
from initialization.initialization import mydb, dp, cursor
from coin.remove_coin import remove_coin
from collection.show_collection import show_collection
import logging

logging.basicConfig(filename='restart.log', level=logging.INFO, format='%(asctime)s - %(message)s')

logging.info('Приложение было перезапущено')

start_(cursor, mydb)
add_coin_()
create_collection()
delete_collection()
add_photo()
# add_state()
remove_coin()
_help()
show_collection()

# Запуск бота:
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
