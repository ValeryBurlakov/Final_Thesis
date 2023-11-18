from aiogram import types
from aiogram.dispatcher import FSMContext
from initialization.initialization import mydb, dp, cursor

def add_photo():
    @dp.message_handler(commands=['add_photo'])
    async def add(message: types.Message, state: FSMContext):
        await message.answer(f'пришлите фото')
        await state.set_state("test_add_photo")  # переход в следующее состояние


    @dp.message_handler(state="test_add_photo", content_types=types.ContentType.PHOTO)
    async def process_photo(message: types.Message):
        # Получаем объект изображения
        photo = message.photo[-1]
        file_id = photo.file_id
        file_path = f'/home/valery/Photo_coin/{file_id}.jpg'

        # Сохраняем изображение на сервере
        await photo.download(destination=file_path)

        # Открываем файл и считываем его содержимое в бинарном виде
        with open(file_path, 'rb') as f:
            data = f.read()

        # Записываем данные изображения в базу данных
        cursor.execute("INSERT INTO photos (image, pathfile) VALUES (%s, %s)", (data, file_path))
        mydb.commit()

        await message.reply("Изображение успешно сохранено!")
