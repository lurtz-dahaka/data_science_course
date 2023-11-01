import asyncio
import logging
import sys
import json

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold, hlink

with open('//Users/egor/Documents/data_science_course/project_7/credentials.txt',
          'r', encoding='utf-8-sig') as psw:
    TOKEN = psw.read().rstrip()

dp = Dispatcher()
bot = Bot(token=TOKEN, parse_mode='html')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

    button = InlineKeyboardButton(text="Get Best Deals", callback_data='get_best_deals')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer("Welcome to the Car Ad Bot!\n"
                        "This bot can daily send best car ads from Nettiauto.com.\n"
                        "Click the button below to get today's best car deals:",
                        reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'get_best_deals')
async def get_best_deals(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_car_ads(callback_query.message)

@dp.message()
async def send_car_ads(message: types.Message):
    with open('/Users/egor/Documents/data_science_course/project_7/data/result.json') as file:
        data = json.load(file)

    for item in data.keys():
        card = f"{hlink(data.get(item).get('make_model'), data.get(item).get('id'))}\n" \
            f"{hbold('Selling price: ')} {data.get(item).get('car_price')}\n" \
            f"{hbold('Predicted price: ')} {data.get(item).get('y_pred')}\n" \
            f"{hbold('Profit %: ')} {data.get(item).get('profit_%')}\n"

        await message.answer(card)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


