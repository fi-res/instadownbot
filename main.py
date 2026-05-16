from asyncio import run, CancelledError
from os import getenv

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout

from lib import download, reply

load_dotenv()

session = AiohttpSession(timeout=120)
bot = Bot(getenv('TOKEN', ''), session=session)
dp = Dispatcher()


@dp.message(F.text.startswith('https://www.instagram.com/'))
@dp.message(F.text.startswith('https://instagram.com/'))
async def process(message: Message):
    assert message.text

    print('process message', message.text)
    load_message = await message.answer('Загрузка...')

    res = download(message.text)
    await load_message.delete()
    if res is not None:
        await message.reply(f'Ошибка загрузки: {res}')
        return

    await reply(message)

async def main():
    print('start polling')
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        run(main())
    except (KeyboardInterrupt, CancelledError):
        print('bot stop (cancelled by user)')