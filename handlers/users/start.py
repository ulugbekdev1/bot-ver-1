from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app import dp

# --- STATE-LAR ---
class RegisterState(StatesGroup):
    fullname = State()
    phone = State()
    course = State()
    faculty = State()

print("start ishladi")

# --- /start komandasi ---
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f"Salom, {message.from_user.first_name} 👋")
    await message.answer("Ro'yxatdan o'tish uchun to'liq ism, familya va sharifingizni kiriting  <i>(Abdullayev Javohir Ahmed o'g'li)</i>:")
    await RegisterState.fullname.set()


# --- F.I.Sh kiritish ---
@dp.message_handler(state=RegisterState.fullname)
async def get_fullname(message: types.Message, state: FSMContext):
    await state.update_data(fullname=message.text)

    phone_keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [types.KeyboardButton("☎️ Telefon raqamni yuborish", request_contact=True)]
        ]
    )
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_keyboard)
    await RegisterState.phone.set()

# --- Telefon raqam ---
@dp.message_handler(content_types=['contact', 'text'], state=RegisterState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)

    course_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    course_keyboard.add("1-kurs", "2-kurs", "3-kurs", "4-kurs")

    await message.answer("Kursingizni tanlang:", reply_markup=course_keyboard)
    await RegisterState.course.set()

# --- Kursni tanlash ---
@dp.message_handler(state=RegisterState.course)
async def get_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    await message.answer("Yo'nalishingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.faculty.set()

# --- Yo‘nalishni kiritish ---
@dp.message_handler(state=RegisterState.faculty)
async def get_faculty(message: types.Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    data = await state.get_data()

    text = (
        "✅ <b>Ro'yxatdan o'tish yakunlandi!</b>\n\n"
        f"👤 <b>Ism:</b> {data['fullname']}\n"
        f"📱 <b>Telefon:</b> {data['phone']}\n"
        f"🎓 <b>Kurs:</b> {data['course']}\n"
        f"🏛 <b>Yo‘nalish:</b> {data['faculty']}"
    )

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm"),
        InlineKeyboardButton("✏️ Qayta kiritish", callback_data="edit")
    )

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await state.finish()

    # --- Tugmalar uchun CALLBACKLAR ---
    @dp.callback_query_handler(lambda c: c.data == "confirm")
    async def process_confirm(callback: CallbackQuery):
        await callback.answer("✅ Tasdiqlandi!", show_alert=True)
        await callback.message.edit_reply_markup()  # Tugmalarni olib tashlaydi
        await callback.message.answer("Ma'lumotlaringiz saqlandi. Rahmat!")

    @dp.callback_query_handler(lambda c: c.data == "edit")
    async def process_edit(callback: CallbackQuery, state: FSMContext):
        await callback.answer("✏️ Ma’lumotlarni qayta kiriting.")
        await callback.message.edit_reply_markup()  # Tugmalarni olib tashlaydi

        await callback.message.answer("Iltimos, to‘liq ism, familya va sharifingizni qaytadan kiriting:")
        await RegisterState.fullname.set()


# --- Oddiy matnlarga javob ---
@dp.message_handler()
async def echo_message(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug'ini yuboring ✅")

