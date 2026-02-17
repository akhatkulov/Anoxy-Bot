from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User
from states.registration import RegistrationStates
from utils.i18n import _
from sqlalchemy import select
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()

def get_language_kb():
    kb = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇹🇯 Тоҷикӣ", callback_data="lang_tg")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    user_query = select(User).where(User.id == message.from_user.id)
    user_result = await session.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if user:
        from keyboards.main_menu import get_main_menu_kb
        await message.answer(
            _('already_reg', user.language) + "\n\n🚀 <b>Menyu:</b>", 
            reply_markup=get_main_menu_kb(user.language)
        )
        return

    # Delete the /start command message to keep clean
    try: await message.delete() 
    except: pass

    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id.isdigit():
            await state.update_data(referred_by=int(referrer_id))

    msg = await message.answer(
        "Xush kelibsiz! / ✨ Добро пожаловать! / ✨ Хуш омадед!\n\n"
        "Tilni tanlang / Выберите язык / Забонро интихоб кунед:", 
        reply_markup=get_language_kb()
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.language)

@router.callback_query(RegistrationStates.language, F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    
    # Delete language selection message
    await callback.message.delete()
    
    msg = await callback.message.answer(_('start_reg', lang))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.photo)
    await callback.answer()

@router.message(RegistrationStates.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    
    # Cleanup: Delete user's photo message and our previous bot message
    try: 
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    file_id = message.photo[-1].file_id
    filename = f"{message.from_user.id}.jpg"
    file_path = f"media/{filename}"
    
    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, file_path)
    
    await state.update_data(photo_id=file_id, photo_path=filename)
    msg = await message.answer(_('get_name', lang))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.name)

@router.message(RegistrationStates.name)
async def process_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    await state.update_data(name=message.text)
    msg = await message.answer(_('get_nickname', lang))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.nickname)

@router.message(RegistrationStates.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    nickname = message.text if message.text != "/skip" else None
    await state.update_data(nickname=nickname)
    msg = await message.answer(_('get_age', lang))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.age)

@router.message(RegistrationStates.age, F.text.regexp(r'^\d+$'))
async def process_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    age = int(message.text)
    if not (14 <= age <= 100):
        msg = await message.answer(_('invalid_age', lang))
        await state.update_data(last_msg_id=msg.message_id)
        return

    await state.update_data(age=age)
    
    kb = [
        [
            InlineKeyboardButton(text=_('male', lang), callback_data="gen_male"),
            InlineKeyboardButton(text=_('female', lang), callback_data="gen_female")
        ]
    ]
    msg = await message.answer(_('get_gender', lang), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.gender)

@router.message(RegistrationStates.age)
async def process_age_invalid(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    # Delete user's invalid message to keep clean
    try: await message.delete()
    except: pass
    
    await message.answer(_('invalid_age', lang))

@router.callback_query(RegistrationStates.gender, F.data.startswith("gen_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    gender = callback.data.split("_")[1]
    
    await state.update_data(gender=gender)
    
    kb = [
        [
            InlineKeyboardButton(text=_('targets_male', lang), callback_data="tar_male"),
            InlineKeyboardButton(text=_('targets_female', lang), callback_data="tar_female")
        ]
    ]
    await callback.message.edit_text(_('get_target', lang), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()
    await state.set_state(RegistrationStates.target_gender)

@router.callback_query(RegistrationStates.target_gender, F.data.startswith("tar_"))
async def process_target_gender(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    target = callback.data.split("_")[1]
    
    await state.update_data(target_gender=target)
    
    from keyboards.main_menu import get_search_age_kb
    await callback.message.edit_text(_('age_msg', lang), reply_markup=get_search_age_kb(lang))
    await state.set_state(RegistrationStates.target_age)
    await callback.answer()

@router.callback_query(RegistrationStates.target_age, F.data.startswith("age_"))
async def process_target_age(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data['language']
    prefix, min_age, max_age = callback.data.split("_")
    
    await state.update_data(target_min_age=int(min_age), target_max_age=int(max_age))
    
    # Location request MUST be ReplyKeyboardMarkup
    kb = [[KeyboardButton(text=_('send_location', lang), request_location=True)]]
    await callback.message.delete()
    msg = await callback.message.answer(
        _('get_location', lang), 
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    )
    await state.update_data(last_msg_id=msg.message_id)
    await callback.answer()
    await state.set_state(RegistrationStates.location)

@router.message(RegistrationStates.location, F.location)
async def process_location(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = data['language']
    
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    lat = message.location.latitude
    lon = message.location.longitude
    point = Point(lon, lat) # Point for state storage, we'll convert to PostGIS later
    
    await state.update_data(lat=lat, lon=lon)
    
    kb = [[KeyboardButton(text=_('send_phone', lang), request_contact=True)]]
    msg = await message.answer(
        _('get_phone', lang), 
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(RegistrationStates.phone)

@router.message(RegistrationStates.phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = data['language']
    
    try:
        await message.delete()
        # Remove phone keyboard
        await message.answer(_('processing', lang), reply_markup=ReplyKeyboardRemove())
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    phone = message.contact.phone_number
    point = from_shape(Point(data['lon'], data['lat']), srid=4326)

    new_user = User(
        id=message.from_user.id,
        name=data['name'],
        nickname=data['nickname'],
        age=data['age'],
        gender=data['gender'],
        target_gender=data['target_gender'],
        target_min_age=data['target_min_age'],
        target_max_age=data['target_max_age'],
        photo_id=data['photo_id'],
        photo_path=data['photo_path'],
        language=lang,
        location=point,
        phone_number=phone,
        referred_by=data.get('referred_by')
    )
    session.add(new_user)
    
    if new_user.referred_by:
        referrer = await session.get(User, new_user.referred_by)
        if referrer:
            referrer.boost_points += 10
            try: await message.bot.send_message(referrer.id, _('boost_notification', referrer.language))
            except: pass

    await session.commit()
    await state.clear()
    
    from keyboards.main_menu import get_main_menu_kb
    await message.answer(
        _('reg_done', lang) + "\n\n🚀 <b>Asosiy menyu:</b>",
        reply_markup=get_main_menu_kb(lang)
    )
