from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

dp: Dispatcher  # bu keyinchalik import qilinadi

# /help komandasi
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = (
        "📚 Buyruqlar:\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam olish"
    )
    await message.answer(text)

# Oddiy matnlar uchun (faqat buyrug‘u bo‘lmagan xabarlar)
@dp.message_handler(lambda message: not message.text.startswith('/'))
async def echo_message(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug‘ini yuboring ✅")
