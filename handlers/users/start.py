from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, BoundFilter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from app import dp
from loader import bot
from database import insert_user, get_all_users, get_user_by_group_message, save_message_link, get_user_by_phone


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

    data = await state.get_data()
    fullname = data.get("fullname")
    group = data.get("group")
    phone = data.get("phone")
    ariza_text = data.get("ariza_text", "Matn mavjud emas")
    await insert_user(fullname, group, phone, ariza_text)
GROUP_ID = -1002976709404


@dp.message_handler(lambda message: message.text == "✅ Tasdiqlash", state=RegisterState.confirm)
async def confirm_ariza(message: types.Message, state: FSMContext):
    print("uuy")
    data = await state.get_data()
    fullname = data.get("fullname")
    group = data.get("group")
    phone = data.get("phone")
    ariza_text = data.get("ariza_text", "Matn mavjud emas")
    id = get_user_by_phone(phone)



    # Guruhga xabar yuborish
    sent_message = await bot.send_message(
        GROUP_ID,
        f"📥 <b>Yangi ariza!</b>  #{id}\n\n"
        f"👤 <b>Ism:</b> {fullname}\n"
        f"🏫 <b>Guruh:</b> {group}\n"
        f"📞 <b>Telefon:</b> {phone}\n\n"
        f"📄 <b>Ariza matni:</b> {ariza_text}"
    )

    # Foydalanuvchi ID va guruhdagi xabar ID sini bog‘lab saqlaymiz
    save_message_link(message.from_user.id, sent_message.message_id)


    await message.answer(
        "<b>✅ Arizangiz yuborildi!</b>\nTez orada javob olasiz.",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.finish()


# === 3. Guruhdagi replylarni aniqlovchi filter ===
class IsGroupReply(BoundFilter):
    key = "is_group_reply"

    def __init__(self, is_group_reply: bool = None):
        self.is_group_reply = is_group_reply

    async def check(self, message: types.Message) -> bool:
        # faqat guruhdagi reply bo‘lsa
        return bool(message.chat.type in ("group", "supergroup") and message.reply_to_message)


dp.filters_factory.bind(IsGroupReply)


# === 4. Guruhdagi replyni ushlab, foydalanuvchiga yuborish ===
@dp.message_handler(is_group_reply=True, content_types=types.ContentTypes.ANY)
async def handle_group_reply(message: types.Message):
    reply_to = message.reply_to_message
    user_id = get_user_by_group_message(reply_to.message_id)


    if not user_id:
        return await message.reply("⚠️ Bu xabar foydalanuvchiga bog‘lanmagan.")

    # --- turiga qarab foydalanuvchiga yuborish ---
    if message.text:
        await bot.send_message(
            user_id,
            f"📩 <b>Sizning arizangizga javob keldi:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
    elif message.photo:
        await bot.send_photo(
            user_id,
            photo=message.photo[-1].file_id,  # eng sifatli rasm
            caption="📩 <b>Sizning arizangizga javob sifatida rasm yuborildi.</b>",
            parse_mode="HTML"
        )
    elif message.document:
        await bot.send_document(
            user_id,
            document=message.document.file_id,
            caption="📄 <b>Sizning arizangizga fayl yuborildi.</b>",
            parse_mode="HTML"
        )
    elif message.video:
        await bot.send_video(
            user_id,
            video=message.video.file_id,
            caption="🎥 <b>Sizning arizangizga video yuborildi.</b>",
            parse_mode="HTML"
        )
    elif message.audio:
        await bot.send_audio(
            user_id,
            audio=message.audio.file_id,
            caption="🎧 <b>Sizning arizangizga audio yuborildi.</b>",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            user_id,
            "📩 Sizning arizangizga javob sifatida fayl yuborildi (qo‘llanmagan turdagi media)."
        )


# --- No command state handler ---
@dp.message_handler(lambda message: not message.text.startswith('/'), state=None)
async def echo_message(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug‘ini yuboring ✅")


# --- Oddiy matnlarga javob ---
@dp.message_handler()
async def echo_message(message: types.Message):
    await message.answer("Botdan foydalanish uchun /start buyrug'ini yuboring ✅")
