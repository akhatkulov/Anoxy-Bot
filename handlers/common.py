from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database.models import User, Like, Report
from states.profile import ProfileEditStates
from states.search import SearchStates
from utils.i18n import _
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

router = Router()

@router.message(Command("me"))
async def cmd_me(message: types.Message, session: AsyncSession, user_id: int = None):
    target_id = user_id or message.from_user.id
    user = await session.get(User, target_id)
    if not user:
        await message.answer("Siz ro'yxatdan o'tmagansiz! /start")
        return
    
    # Cleanup: delete command message
    try: await message.delete()
    except: pass

    referral_link = f"https://t.me/{(await message.bot.get_me()).username}?start={user.id}"
    
    # Professional caption for own profile
    t_gender = _('targets_male', user.language) if user.target_gender == 'male' else _('targets_female', user.language)
    t_age = f"{user.target_min_age}-{user.target_max_age}"
    
    text = _('profile_info', user.language, 
             name=user.name, 
             age=user.age, 
             boost=user.boost_points, 
             t_gender=t_gender, 
             t_age=t_age,
             link=referral_link)
    
    kb = [
        [
            types.InlineKeyboardButton(text="📝 Ism", callback_data="edit_name"),
            types.InlineKeyboardButton(text="🔢 Yosh", callback_data="edit_age")
        ],
        [
            types.InlineKeyboardButton(text="🖼 Rasm", callback_data="edit_photo"),
            types.InlineKeyboardButton(text="📍 Manzil", callback_data="edit_location")
        ],
        [
            types.InlineKeyboardButton(text=_('btn_edit_target_gender', user.language), callback_data="edit_target_gender"),
            types.InlineKeyboardButton(text=_('btn_edit_target_age', user.language), callback_data="edit_target_age")
        ],
        [types.InlineKeyboardButton(text=_('btn_activity', user.language), callback_data="menu_activity")],
        [types.InlineKeyboardButton(text=_('btn_back', user.language), callback_data="back_to_menu")]
    ]
    
    if user.photo_id:
        await message.answer_photo(
            photo=user.photo_id,
            caption=text,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
        )
    else:
        await message.answer(
            text,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
        )

@router.callback_query(F.data == "menu_profile")
async def callback_profile(callback: types.CallbackQuery, session: AsyncSession):
    # Pass the actual user ID who clicked the button
    await callback.message.delete()
    await cmd_me(callback.message, session, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await session.get(User, callback.from_user.id)
    await state.clear()
    from keyboards.main_menu import get_main_menu_kb
    # If the current message has a photo, edit_text won't work, so delete and answer
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(_('main_menu_msg', user.language), reply_markup=get_main_menu_kb(user.language))
    else:
        await callback.message.edit_text(_('main_menu_msg', user.language), reply_markup=get_main_menu_kb(user.language))
    await callback.answer()

@router.callback_query(F.data == "menu_search")
async def menu_search_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    from handlers.match import show_profile
    from states.search import SearchStates
    user = await session.get(User, callback.from_user.id)
    await callback.message.delete()
    await state.set_state(SearchStates.browsing)
    await show_profile(callback.message, user, session, state)
    await callback.answer()

@router.callback_query(F.data == "menu_boost")
async def menu_boost_info(callback: types.CallbackQuery, session: AsyncSession):
    import os
    admin_contact = os.getenv("ADMIN_CONTACT", "@admin")
    
    user = await session.get(User, callback.from_user.id)
    referral_link = f"https://t.me/{(await callback.bot.get_me()).username}?start={user.id}"
    
    text = (
        "💎 <b>Foydali Boost ballarini to'plang!</b>\n\n"
        "Boost ballari sizning profilingizni qidiruv natijalarida eng yuqoriga chiqaradi va ko'proq odamlar sizni ko'rishini ta'minlaydi.\n\n"
        "🚀 <b>Ball yig'ish usullari:</b>\n"
        "1. <b>Referal:</b> Do'stingiz ro'yxatdan o'tsin (+10 ball)\n"
        "2. <b>Admin:</b> Admin orqali ballni sotib olish yoki sovg'a olish\n\n"
        "👇 <b>Sizning shaxsiy havolangiz:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        "🆘 <b>Boost bo'yicha savollar yoki Admin bilan bog'lanish:</b>"
    )
    
    kb = [
        [types.InlineKeyboardButton(text="👤 Admin", url=f"https://t.me/{admin_contact.replace('@', '')}")],
        [types.InlineKeyboardButton(text=_('btn_back', user.language), callback_data="back_to_menu")]
    ]
    
    await callback.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await callback.answer()

@router.callback_query(F.data == "menu_top")
async def menu_top_users(callback: types.CallbackQuery, session: AsyncSession):
    # Fetch top 10 users by boost points
    query = select(User).order_by(User.boost_points.desc()).limit(10)
    result = await session.execute(query)
    top_users = result.scalars().all()
    
    text = "📊 <b>Eng ko'p Boost ballga ega foydalanuvchilar:</b>\n\n"
    for i, user in enumerate(top_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        text += f"{medal} {i}. <b>{user.name}</b> — {user.boost_points} ball\n"
    
    if not top_users:
        text = "Hozircha reyting bo'sh."

    kb = [[types.InlineKeyboardButton(text=_('btn_back', user.language), callback_data="back_to_menu")]]
    await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@router.callback_query(F.data == "menu_activity")
async def menu_activity(callback: types.CallbackQuery, session: AsyncSession):
    user = await session.get(User, callback.from_user.id)
    kb = [
        [types.InlineKeyboardButton(text=_('btn_activity_likes', user.language), callback_data="activity_likes")],
        [types.InlineKeyboardButton(text=_('btn_activity_dislikes', user.language), callback_data="activity_dislikes")],
        [types.InlineKeyboardButton(text=_('btn_activity_reports', user.language), callback_data="activity_reports")],
        [types.InlineKeyboardButton(text=_('btn_back', user.language), callback_data="back_to_me")]
    ]
    await callback.message.delete()
    await callback.message.answer(_('btn_activity', user.language), reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@router.callback_query(F.data.startswith("activity_"))
async def process_activity_history(callback: types.CallbackQuery, session: AsyncSession):
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    if action == "likes":
        query = select(User).join(Like, User.id == Like.target_id).where(Like.user_id == user_id, Like.is_like == True).limit(20)
        title = "❤️ <b>Siz yoqtirgan profillar:</b>"
    elif action == "dislikes":
        query = select(User).join(Like, User.id == Like.target_id).where(Like.user_id == user_id, Like.is_like == False).limit(20)
        title = "👎 <b>Sizga yoqmagan profillar:</b>"
    else: # reports
        query = select(User).join(Report, User.id == Report.target_id).where(Report.reporter_id == user_id).limit(20)
        title = "⚠️ <b>Siz shikoyat qilgan profillar:</b>"
    
    result = await session.execute(query)
    users = result.scalars().all()
    
    text = f"{title}\n\n"
    if users:
        for i, user in enumerate(users, 1):
            display_name = user.nickname if user.nickname and user.nickname != "None" else user.name
            profile_link = f'<a href="tg://user?id={user.id}">{display_name}</a>'
            text += f"{i}. {profile_link}\n"
    else:
        text += "Hozircha ro'yxat bo'sh."

    kb = [[types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu_activity")]]
    await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@router.callback_query(F.data == "edit_name")
async def edit_name(callback: types.CallbackQuery, state: FSMContext):
    msg = await callback.message.answer("📝 <b>Yangi ismingizni kiriting:</b>")
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(ProfileEditStates.edit_name)
    await callback.answer()

@router.message(ProfileEditStates.edit_name)
async def process_edit_name(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    data = await state.get_data()
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    user.name = message.text
    await session.commit()
    await state.clear()
    await cmd_me(message, session)

@router.callback_query(F.data == "edit_age")
async def edit_age(callback: types.CallbackQuery, state: FSMContext):
    msg = await callback.message.answer("🔢 <b>Yangi yoshingizni kiriting:</b>")
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(ProfileEditStates.edit_age)
    await callback.answer()

@router.message(ProfileEditStates.edit_age, F.text.regexp(r'^\d+$'))
async def process_edit_age(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    data = await state.get_data()
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    age = int(message.text)
    if 14 <= age <= 100:
        user.age = age
        await session.commit()
        await state.clear()
        await cmd_me(message, session)
    else:
        await message.answer("Iltimos, haqiqiy yoshni kiriting (14-100).")

@router.message(ProfileEditStates.edit_age)
async def process_edit_age_invalid(message: types.Message):
    try: await message.delete()
    except: pass
    await message.answer("⚠️ <b>Xatolik!</b> Iltimos, yoshingizni faqat raqamlarda kiriting (masalan: 25).")

@router.callback_query(F.data == "edit_photo")
async def edit_photo(callback: types.CallbackQuery, state: FSMContext):
    msg = await callback.message.answer("🖼 <b>Yangi rasm yuboring:</b>")
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(ProfileEditStates.edit_photo)
    await callback.answer()

@router.message(ProfileEditStates.edit_photo, F.photo)
async def process_edit_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    data = await state.get_data()
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    file_id = message.photo[-1].file_id
    user.photo_id = file_id
    await session.commit()
    await state.clear()
    await cmd_me(message, session)

@router.callback_query(F.data == "edit_location")
async def edit_location(callback: types.CallbackQuery, state: FSMContext):
    kb = [[types.KeyboardButton(text="📍 Joylashuvni jo'natish", request_location=True)]]
    msg = await callback.message.answer(
        "Yangi joylashuvingizni yuboring:", 
        reply_markup=types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(ProfileEditStates.edit_location)
    await callback.answer()



@router.message(ProfileEditStates.edit_location, F.location)
async def process_edit_location(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    
    # Cleanup
    data = await state.get_data()
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, data.get('last_msg_id'))
    except: pass

    lat = message.location.latitude
    lon = message.location.longitude
    user.location = from_shape(Point(lon, lat), srid=4326)
    
    await session.commit()
    await message.answer("✅ Joylashuv muvaffaqiyatli yangilandi!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await cmd_me(message, session)

@router.callback_query(F.data == "edit_target_gender")
async def edit_target_gender(callback: types.CallbackQuery, session: AsyncSession):
    user = await session.get(User, callback.from_user.id)
    kb = [
        [
            types.InlineKeyboardButton(text=_('targets_male', user.language), callback_data="set_target_male"),
            types.InlineKeyboardButton(text=_('targets_female', user.language), callback_data="set_target_female")
        ],
        [types.InlineKeyboardButton(text=_('btn_back', user.language), callback_data="back_to_me")]
    ]
    await callback.message.edit_text(_('get_target', user.language), reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

@router.callback_query(F.data.startswith("set_target_"))
async def process_edit_target_gender(callback: types.CallbackQuery, session: AsyncSession):
    user = await session.get(User, callback.from_user.id)
    gender = callback.data.split("_")[2]
    user.target_gender = gender
    await session.commit()
    await callback.answer("✅")
    await cmd_me(callback.message, session, user_id=user.id)

@router.callback_query(F.data == "edit_target_age")
async def edit_target_age(callback: types.CallbackQuery, session: AsyncSession):
    user = await session.get(User, callback.from_user.id)
    from keyboards.main_menu import get_search_age_kb
    # We need to handle age_ callbacks differently to return to profile
    kb = get_search_age_kb(user.language)
    # Modify callback_data to distinguish from search
    for row in kb.inline_keyboard:
        for btn in row:
            if btn.callback_data.startswith("age_"):
                btn.callback_data = btn.callback_data.replace("age_", "set_age_")
            if btn.callback_data == "menu_search":
                btn.callback_data = "back_to_me"
    
    await callback.message.edit_text(_('age_msg', user.language), reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("set_age_"))
async def process_edit_target_age(callback: types.CallbackQuery, session: AsyncSession):
    user = await session.get(User, callback.from_user.id)
    parts = callback.data.split("_")  # ["set", "age", "18", "25"]
    min_age, max_age = parts[-2], parts[-1]
    user.target_min_age = int(min_age)
    user.target_max_age = int(max_age)
    await session.commit()
    await callback.answer("✅")
    await cmd_me(callback.message, session, user_id=user.id)

@router.callback_query(F.data == "back_to_me")
async def back_to_me(callback: types.CallbackQuery, session: AsyncSession):
    # If the message is a photo, edit_text won't work easily if we want to change caption
    # But usually cmd_me handles it
    await callback.message.delete()
    await cmd_me(callback.message, session, user_id=callback.from_user.id)
    await callback.answer()
