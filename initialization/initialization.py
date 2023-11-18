from initialization.bot_instance import create_bot_and_dispatcher
from initialization.connection_database import create_connection


# 4. Создаем соединение с базой данных в вашем файле Python:
mydb = create_connection()
# 5. Создаем экземпляры классов `Bot`, `Dispatcher` и `mysql.connector.Cursor` в файле Python:
bot, dp = create_bot_and_dispatcher()
# создали объект курсора для взаимодействия с базой данных
cursor = mydb.cursor()
