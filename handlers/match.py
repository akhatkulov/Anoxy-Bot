from aiogram import Router, F, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User, Like
from utils.matching import get_next_profile, handle_interaction
from utils.i18n import _
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from states.search import SearchStates
from keyboards.main_menu import get_search_age_kb, get_main_menu_kb

router = Router()

def get_match_keyboard(target_id: int, lang: str):
    kb = [
        [
            types.InlineKeyboardButton(text="👎", callback_data=f"dislike_{target_id}"),
            types.InlineKeyboardButton(text="❤️", callback_data=f"like_{target_id}"),
        ],
        [
            types.InlineKeyboardButton(text=_('report', lang), callback_data=f"report_{target_id}")
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=kb)

@router.message(Command("menu"))
@router.message(Command("feed"))
async def cmd_menu(message: types.Message, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    if not user or user.is_banned: return
    await message.answer(_('main_menu_msg', user.language), reply_markup=get_main_menu_kb(user.language))

@router.callback_query(SearchStates.target_gender, F.data.startswith("search_"))
async def process_search_gender(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    gender = callback.data.split("_")[1]
    await state.update_data(search_gender=gender)
    user = await session.get(User, callback.from_user.id)
    await callback.message.edit_text(_('age_msg', user.language), reply_markup=get_search_age_kb(user.language))
    await state.set_state(SearchStates.age_range)
    await callback.answer()

@router.callback_query(SearchStates.age_range, F.data.startswith("age_"))
async def process_search_age(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    prefix, min_age, max_age = callback.data.split("_")
    await state.update_data(search_min_age=int(min_age), search_max_age=int(max_age))
    
    user = await session.get(User, callback.from_user.id)
    await callback.message.delete()
    await state.set_state(SearchStates.browsing)
    await show_profile(callback.message, user, session, state)
    await callback.answer()

async def show_profile(message: types.Message, user: User, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    # Check if we are in "likes" feed
    if data.get("feed_type") == "likes":
        await show_liked_profile(message, user, session, state)
        return

    next_profile, distance = await get_next_profile(
        session, user, 
        target_gender=data.get('search_gender') or user.target_gender,
        min_age=data.get('search_min_age') or user.target_min_age,
        max_age=data.get('search_max_age') or user.target_max_age
    )
    
    if not next_profile:
        await message.answer(
            _('no_profiles', user.language), 
            reply_markup=get_main_menu_kb(user.language)
        )
        await state.clear()
        return

    dist_text = f"{distance:.1f} km" if distance is not None else "???"
    caption = _('profile_caption', user.language, name=next_profile.name, age=next_profile.age, distance=dist_text)
    
    msg = await message.answer_photo(
        photo=next_profile.photo_id,
        caption=caption,
        reply_markup=get_match_keyboard(next_profile.id, user.language)
    )
    await state.update_data(last_profile_msg_id=msg.message_id)

@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    target_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    user = await session.get(User, user_id)
    
    is_match = await handle_interaction(session, user_id, target_id, is_like=True)
    
    if is_match:
        target = await session.get(User, target_id)
        await callback.message.answer(_('match', user.language))
        
        target_display = target.nickname if target.nickname and target.nickname != "None" else target.name
        target_profile = f'<a href="tg://user?id={target.id}">{target_display}</a>'
        await callback.message.answer(_('contact_info', user.language, profile=target_profile))
        
        user_display = user.nickname if user.nickname and user.nickname != "None" else user.name
        user_profile = f'<a href="tg://user?id={user.id}">{user_display}</a>'
        await callback.bot.send_message(
            target_id, 
            _('new_match', target.language, name=user.name, profile=user_profile)
        )
    else:
        # Batched like notifications
        target = await session.get(User, target_id)
        if target:
            target.pending_likes_count += 1
            count = target.pending_likes_count
            text = _('liked_you_batched', target.language, count=count)
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=_('view_profiles', target.language), callback_data="view_liked_profiles")],
                [types.InlineKeyboardButton(text=_('later', target.language), callback_data="later_liked_profiles")]
            ])
            
            success = False
            if target.last_like_notification_id:
                try:
                    await callback.bot.edit_message_text(
                        text=text,
                        chat_id=target.id,
                        message_id=target.last_like_notification_id,
                        reply_markup=kb
                    )
                    success = True
                except:
                    pass # Message might have been deleted
            
            if not success:
                try:
                    msg = await callback.bot.send_message(target.id, text, reply_markup=kb)
                    target.last_like_notification_id = msg.message_id
                except:
                    pass # User might have blocked the bot
            
            await session.commit()
    
    await callback.message.delete()
    await show_profile(callback.message, user, session, state)
    await callback.answer()

@router.callback_query(F.data == "view_liked_profiles")
async def view_liked_profiles(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await session.get(User, callback.from_user.id)
    if not user: return
    
    # Reset batched notification data
    user.pending_likes_count = 0
    user.last_like_notification_id = None
    await session.commit()
    
    await callback.message.delete()
    await state.set_state(SearchStates.browsing)
    await state.update_data(feed_type="likes")
    await show_liked_profile(callback.message, user, session, state)

@router.callback_query(F.data == "later_liked_profiles")
async def later_liked_profiles(callback: types.CallbackQuery):
    try: await callback.message.delete()
    except: pass
    await callback.answer()

async def show_liked_profile(message: types.Message, user: User, session: AsyncSession, state: FSMContext):
    # Fetch users who liked this user but no interaction from this user yet
    query = select(User).join(Like, User.id == Like.user_id).where(
        Like.target_id == user.id,
        Like.is_like == True,
        Like.is_match == False
    ).limit(1)
    
    result = await session.execute(query)
    next_profile = result.scalars().first()
    
    if not next_profile:
        await message.answer(
            _('no_profiles', user.language), 
            reply_markup=get_main_menu_kb(user.language)
        )
        await state.clear()
        return

    dist_text = "???"
    
    display_name = next_profile.nickname if next_profile.nickname and next_profile.nickname != "None" else next_profile.name
    profile_link = f'<a href="tg://user?id={next_profile.id}">{display_name}</a>'
    
    caption = (
        f"{_('profile_caption', user.language, name=next_profile.name, age=next_profile.age, distance=dist_text)}\n\n"
        f"<b>Bog'lanish uchun:</b>\n"
        f"👤 Profil: {profile_link}"
    )
    
    kb = [
        [types.InlineKeyboardButton(text=_('next_profile', user.language), callback_data="view_liked_profiles")],
        [types.InlineKeyboardButton(text=_('btn_back', user.language), callback_data="back_to_menu")]
    ]
    
    msg = await message.answer_photo(
        photo=next_profile.photo_id,
        caption=caption,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await state.update_data(last_profile_msg_id=msg.message_id)

@router.callback_query(F.data.startswith("dislike_"))
async def process_dislike(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    target_id = int(callback.data.split("_")[1])
    user = await session.get(User, callback.from_user.id)
    await handle_interaction(session, callback.from_user.id, target_id, is_like=False)
    await callback.message.delete()
    await show_profile(callback.message, user, session, state)
    await callback.answer()

@router.callback_query(F.data.startswith("report_"))
async def process_report(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    target_id = int(callback.data.split("_")[1])
    from core.database.models import Report
    session.add(Report(reporter_id=callback.from_user.id, target_id=target_id, reason="Bot reporting system"))
    await session.commit()
    await callback.answer("⚠️ Shikoyat qabul qilindi.", show_alert=True)
    await callback.message.delete()
    user = await session.get(User, callback.from_user.id)
    await show_profile(callback.message, user, session, state)
