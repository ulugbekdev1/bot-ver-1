from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from app import dp


# --- STATE-LAR ---
class RegisterState(StatesGroup):
    fullname = State()
    group = State()
    phone = State()
    ariza_text = State()
    confirm = State()  # 🔵 tasdiqlash uchun state


# --- ❌ Bekor qilish tugmasi uchun umumiy handler (YUQORIDA TURISHI SHART) ---
@dp.message_handler(lambda message: message.text == "❌ Bekor qilish", state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()

    main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.row(
        KeyboardButton("📝 Ariza/Taklif"),
        KeyboardButton("ℹ️ Ma'lumot")
    )
    main_menu.row(KeyboardButton("📞 Bog'lanish"))

    await message.answer(
        "❌ Amaliyot bekor qilindi.\n\n"
        "Quyidagi menyudan tanlang:",
        reply_markup=main_menu
    )


# --- /start komandasi ---
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()

    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons.row(
        KeyboardButton("📝 Ariza/Taklif"),
        KeyboardButton("ℹ️ Ma'lumot")
    )
    buttons.row(KeyboardButton("📞 Bog'lanish"))

    await message.answer(
        "<b>Registrator Ofisi Botiga Xush kelibsiz!</b>\n\n"
        "Salom, {0} 👋\n\n"
        "Bu bot orqali siz:\n"
        "- 📝 Ariza va taklif yuborishingiz\n"
        "- ℹ️ Registrator ofisi haqida ma'lumot olishingiz mumkin\n\n"
        "Quyidagi tugmalardan foydalaning:".format(message.from_user.first_name),
        reply_markup=buttons,
        parse_mode="HTML"
    )


# --- ℹ️ Ma'lumot tugmasi uchun handler ---
@dp.message_handler(lambda message: message.text == "ℹ️ Ma'lumot")
async def info_handler(message: types.Message):
    await message.answer(
        "ℹ️ <b>Registrator ofisi haqida ma'lumot:</b>\n\n"
        "🏛 <b>Muhammad al-Xorazmiy nomidagi Toshkent axborot texnologiyalari universitetining</b> "
        "Registrator ofisi talabalarga o‘qish jarayoni bilan bog‘liq hujjatlarni tayyorlash va tasdiqlash, "
        "turli ma’lumotnomalar (transkript, buyruqdan ko‘chirma va boshqalar) berish, "
        "diplom va dublikatlarni chop etish, elektron diplomlarni tasdiqlash, "
        "talabalarni axborot tizimlarida ro‘yxatga olish, shuningdek maslahat va axborot xizmatlarini ko‘rsatish bilan shug‘ullanadi.\n\n"
        "📘 Ofis o‘z faoliyatini O‘zbekiston Respublikasi qonunlari, hukumat qarorlari, "
        "vazirliklar buyruqlari hamda universitet Nizomi asosida amalga oshiradi.\n\n"
        "👤 Ofis faoliyatiga rektor tomonidan tayinlanadigan boshliq rahbarlik qiladi "
        "va u o‘quv ishlari bo‘yicha prorektorga bo‘ysunadi.",
        parse_mode="HTML"
    )


# --- 📞 Bog‘lanish tugmasi uchun handler ---
@dp.message_handler(lambda message: message.text == "📞 Bog'lanish")
async def contact_handler(message: types.Message):
    await message.answer(
        "📞 <b>Registrator ofisi bilan bog‘lanish:</b>\n\n"
        "👤 Ofis boshlig'i: Shaxobiddinov Alisher Shopatxiddinovich\n"
        "📧 Email: a.shaxobiddinov@tuit.uz\n"
        "☎️ Telefon: (+99871) 238-64-12\n"
        "📅 Qabul vaqti: Dushanba-Juma (10:00-16:00)",
        parse_mode="HTML"
    )


# --- Ariza boshlash ---
@dp.message_handler(lambda message: message.text == "📝 Ariza/Taklif")
async def ariza_start(message: types.Message, state: FSMContext):
    cancel_btn = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn.add(KeyboardButton("❌ Bekor qilish"))

    await state.finish()
    await RegisterState.fullname.set()

    await message.answer(
        "📝 <b>Ariza/Taklif yuborish</b>\n\n"
        "Iltimos, to‘liq ismingizni kiriting:\n"
        "<i>Masalan: Ahmedov Aziz Hakimjon o‘g‘li</i>",
        parse_mode="HTML",
        reply_markup=cancel_btn
    )


# --- Ism qabul qilinib, guruh so‘raladi ---
@dp.message_handler(state=RegisterState.fullname, content_types=['text'])
async def process_fullname(message: types.Message, state: FSMContext):
    await state.update_data(fullname=message.text)

    cancel_btn = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn.add(KeyboardButton("❌ Bekor qilish"))

    await RegisterState.group.set()
    await message.answer(
        "👥 <b>Fakultet va guruh nomini kiritng:</b>\n"
        "<i>Masalan: Kiberxavfsizlik 714-23</i>",
        parse_mode="HTML",
        reply_markup=cancel_btn
    )


# --- Guruh qabul qilinib, telefon so‘raladi ---
@dp.message_handler(state=RegisterState.group, content_types=['text'])
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)

    cancel_and_contact = ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = KeyboardButton("☎️ Telefon raqamni yuborish", request_contact=True)
    cancel_and_contact.row(contact_btn)

    await RegisterState.phone.set()
    await message.answer(
        "📱 <b>Telefon raqamingizni ulashing:</b>\n"
        "Quyidagi tugma orqali telefon raqamingizni yuboring:",
        parse_mode="HTML",
        reply_markup=cancel_and_contact
    )


# --- Telefonni qabul qilish (contact yoki matn bilan) ---
@dp.message_handler(state=RegisterState.phone, content_types=['contact', 'text'])
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact and message.contact.phone_number:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)

    default_btns = ReplyKeyboardMarkup(resize_keyboard=True)
    default_btns.row(
        KeyboardButton("✅ Tasdiqlash"),
        KeyboardButton("❌ Bekor qilish")
    )

    await RegisterState.ariza_text.set()
    await message.answer(
        "✍️ <b>Ariza/Taklif matnini yozing:</b>\n\n"
        "Siz matn, rasm yoki fayllar yuborishingiz mumkin.\n"
        "Tugatgach, '✅ Tasdiqlash' tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=default_btns
    )


# --- Ariza/Taklif matni so‘raladi ---
@dp.message_handler(state=RegisterState.ariza_text, content_types=['text', 'photo', 'document'])
async def receive_ariza_text(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(ariza_text=message.text)
    elif message.caption:
        await state.update_data(ariza_text=message.caption)

    await message.answer(
        "✉️ <b>Matn qabul qilindi.</b>\n"
        "Davom eting yoki <b>✅ Tasdiqlash</b> tugmasini bosing.",
        parse_mode="HTML"
    )

    await RegisterState.confirm.set()


# --- Tasdiqlash bosilganda ---
@dp.message_handler(lambda message: message.text == "✅ Tasdiqlash", state=RegisterState.confirm)
async def confirm_ariza(message: types.Message, state: FSMContext):
    data = await state.get_data()
    fullname = data.get("fullname")
    group = data.get("group")
    phone = data.get("phone")
    ariza_text = data.get("ariza_text", "Matn mavjud emas")

    await message.answer(
        f"<b>Arizangiz yuborildi!</b>\n\n"
        f"👤 Ism: {fullname}\n"
        f"🏫 Guruh: {group}\n"
        f"📞 Telefon: {phone}\n\n"
        f"📄 <b>Ariza matni:</b> {ariza_text}",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.finish()


# --- No command state handler ---
@dp.message_handler(lambda message: not message.text.startswith('/'), state=None)
async def echo_message(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug‘ini yuboring ✅")


# --- Oddiy matnlarga javob ---
@dp.message_handler()
async def echo_message(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug'ini yuboring ✅")
