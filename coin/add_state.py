from aiogram import types
from initialization.initialization import mydb, dp, cursor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def add_state():
    @dp.message_handler(commands=['add_state'])
    async def states(message: types.Message):
        # Создаем клавиатуру с вариантами состояния монеты
        keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = [KeyboardButton(text='Отличное'), KeyboardButton(text='Среднее'), KeyboardButton(text='Плохое')]
        keyboard.add(*buttons)

        await message.answer("Выберите состояние монеты:", reply_markup=keyboard)

    @dp.message_handler(lambda message: message.text in ['Отличное', 'Среднее', 'Плохое'])
    async def process_choice(message: types.Message):
        coin_state = message.text
        idi = 3
        val = (coin_state, idi)
        # Ваш код для записи состояния монеты в базу данных MySQL
        sql = "UPDATE coin SET state = %s WHERE id = %s"
        cursor.execute(sql, val)
        mydb.commit()

        await message.answer(f"Вы выбрали состояние {coin_state}. Запись в базу данных прошла успешно.",
                             reply_markup=types.ReplyKeyboardRemove())
