import os
import asyncio
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database.models import User, Like
from keyboards.admin import get_admin_main_kb, get_admin_cancel_kb, get_admin_user_kb
from states.admin import AdminStates
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

router = Router()

# Middleware-like check for admin
def is_admin(user_id: int):
    return user_id == ADMIN_ID

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("👑 **Admin Paneliga xush kelibsiz!**\nKerakli bo'limni tanlang:", reply_markup=get_admin_main_kb())

@router.callback_query(F.data == "admin_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👑 **Admin Paneliga xush kelibsiz!**\nKerakli bo'limni tanlang:", reply_markup=get_admin_main_kb())

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id): return

    # Total users
    total_users_query = select(func.count(User.id))
    total_users = (await session.execute(total_users_query)).scalar()

    # Male/Female count
    male_query = select(func.count(User.id)).where(User.gender == "male")
    female_query = select(func.count(User.id)).where(User.gender == "female")
    males = (await session.execute(male_query)).scalar()
    females = (await session.execute(female_query)).scalar()

    # Total matches
    matches_query = select(func.count(Like.id)).where(Like.is_match == True)
    total_matches = (await session.execute(matches_query)).scalar()

    stats_text = (
        "📊 **Bot Statistikasi**\n\n"
        f"👥 Umumiy foydalanuvchilar: `{total_users}`\n"
        f"♂️ Erkaklar: `{males}`\n"
        f"♀️ Ayollar: `{females}`\n"
        f"🔥 O'zaro mosliklar (Matches): `{total_matches // 2}`\n"
    )
    
    await callback.message.edit_text(stats_text, reply_markup=get_admin_cancel_kb())

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    
    await callback.message.edit_text("📢 **Xabar matnini yuboring:**\n(Hozircha faqat matnli xabar qo'llab-quvvatlanadi)", reply_markup=get_admin_cancel_kb())
    await state.set_state(AdminStates.broadcast_text)

@router.message(AdminStates.broadcast_text)
async def process_broadcast(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if not is_admin(message.from_user.id): return

    broadcast_text = message.text
    await message.answer("🚀 Xabar yuborish boshlandi...")
    
    users_query = select(User.id)
    users_result = await session.execute(users_query)
    user_ids = users_result.scalars().all()

    success = 0
    failed = 0
    
    for uid in user_ids:
        try:
            await bot.send_message(uid, broadcast_text)
            success += 1
            await asyncio.sleep(0.05) # Avoid flood limit
        except Exception:
            failed += 1
    
    await message.answer(f"✅ Tayyor!\n\nYetib bordi: `{success}`\nBloklagan: `{failed}`")
    await state.clear()

@router.callback_query(F.data == "admin_search")
async def admin_search(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.edit_text("🔍 **Foydalanuvchi ID sini yuboring:**", reply_markup=get_admin_cancel_kb())
    await state.set_state(AdminStates.search_user)

@router.message(AdminStates.search_user)
async def process_user_search(message: types.Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id): return
    
    if not message.text.isdigit():
        await message.answer("ID faqat raqamlardan iborat bo'lishi kerak!")
        return
        
    user_id = int(message.text)
    user = await session.get(User, user_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        return
        
    display_name = user.nickname if user.nickname and user.nickname != "None" else user.name
    profile_link = f'<a href="tg://user?id={user.id}">{display_name}</a>'
    
    user_info = (
        f"👤 <b>Foydalanuvchi ma'lumotlari</b>\n\n"
        f"ID: <code>{user.id}</code>\n"
        f"Profil: {profile_link}\n"
        f"Yosh: <b>{user.age}</b>\n"
        f"Jinsi: {user.gender}\n"
        f"Boost: {user.boost_points}\n"
        f"Til: {user.language}\n"
    )
    
    kb = get_admin_user_kb(user.id, user.is_banned)
    await message.answer(user_info, reply_markup=kb)

@router.callback_query(F.data == "admin_reports")
async def admin_reports(callback: types.CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id): return
    
    from core.database.models import Report
    # Get 10 latest reports
    query = select(Report).order_by(Report.created_at.desc()).limit(10)
    reports = (await session.execute(query)).scalars().all()
    
    if not reports:
        await callback.answer("Hozircha shikoyatlar yo'q.", show_alert=True)
        return
        
    text = "⚠️ **Oxirgi 10 ta shikoyat:**\n\n"
    for r in reports:
        text += f"Target: `{r.target_id}` | Reporter: `{r.reporter_id}`\n"
        
    await callback.message.edit_text(text, reply_markup=get_admin_cancel_kb())

@router.callback_query(F.data.startswith("adm_ban_"))
async def process_admin_ban(callback: types.CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id): return
    
    target_id = int(callback.data.split("_")[2])
    user = await session.get(User, target_id)
    
    if user:
        user.is_banned = not user.is_banned
        await session.commit()
        status = "bloklandi" if user.is_banned else "bandan yechildi"
        await callback.answer(f"✅ Foydalanuvchi {status}!", show_alert=True)
        # Refresh markup
        await callback.message.edit_reply_markup(reply_markup=get_admin_user_kb(user.id, user.is_banned))

@router.callback_query(F.data.startswith("adm_boost_"))
async def process_admin_boost(callback: types.CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id): return
    
    target_id = int(callback.data.split("_")[2])
    user = await session.get(User, target_id)
    
    if user:
        user.boost_points += 50
        await session.commit()
        await callback.answer(f"✅ {user.name} ga 50 boost berildi!", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.answer("Xatolik: Foydalanuvchi topilmadi.")

@router.callback_query(F.data == "admin_close")
async def admin_close(callback: types.CallbackQuery):
    await callback.message.delete()
