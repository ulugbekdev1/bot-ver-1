from aiogram import types

from loader import dp


@dp.message_handler(lambda message: not message.text.startswith("/"), state=None)
async def bot_echo(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug‘ini yuboring ✅")
