# Tanishuv Bot (Dating Bot)

Ushbu bot `aiogram 3.x`, `PostgreSQL` va `PostGIS` yordamida yaratilgan.

## Texnologiyalar
- **Framework:** Aiogram 3.x
- **Database:** PostgreSQL + asyncpg + SQLAlchemy
- **Geo-logic:** PostGIS (masofani hisoblash uchun)
- **FSM:** Ro'yxatdan o'tish uchun

## O'rnatish

1. Loyihani klon qiling:
   ```bash
   git clone <link>
   cd anoxy_bot
   ```

2. Virtual muhitni yarating va kutubxonalarni o'rnating:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux
   pip install -r requirements.txt
   ```

3. `.env` faylini yarating va ma'lumotlarni to'ldiring:
   ```bash
   cp .env.example .env
   ```

4. Ma'lumotlar bazasida PostGIS ni yoqing:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

5. Migratsiyalarni amalga oshiring yoki bazani yarating (SQLAlchemy modelidan):
   ```python
   # create_db.py (ixtiyoriy, bazani birinchi marta yaratish uchun)
   import asyncio
   from core.database.models import Base
   from core.database.session import engine
   
   async def init_db():
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
   
   if __name__ == "__main__":
       asyncio.run(init_db())
   ```

## Xususiyatlar
- **Ko'p tilli:** O'zbek, Rus va Tojik tillarini qo'llab-quvvatlaydi.
- **Docker Compose:** Loyihani bitta buyruq bilan ishga tushirish.
- **Avtomatik Backup:** Har kuni ma'lumotlar bazasini zahiralash.
- **FSM Ro'yxatdan o'tish:** Rasm -> Ism -> Nikneym -> Yosh -> Jins -> Lokatsiya.
- **Matching:** Masofaga qarab eng yaqin foydalanuvchilarni topish.
- **Boost tizimi:** Do'stlarni taklif qilganda +10 ball. Boost balli borlar qidiruvda yuqorida chiqadi.

## Docker orqali ishga tushirish (Tavsiya etiladi)

1. `.env` faylini sozlang:
   ```bash
   cp .env.example .env
   # .env faylida BOT_TOKEN ni o'rnating
   ```

2. Docker Compose ni ishga tushiring:
   ```bash
   docker-compose up -d --build
   ```

3. Bot avtomatik ravishda bazani yaratadi va ishga tushadi. Zahira nusxalar (backups) `./backups` papkasida saqlanadi.

## Testlarni o'tkazish

Unit testlarni Docker konteyneri ichida quyidagi buyruq orqali ishga tushirishingiz mumkin:

```bash
docker-compose exec bot pytest
```

## Buyruqlar
- `/start` - Ro'yxatdan o'tish va referral havola orqali qo'shilish.
- `/feed` - Profillarni ko'rish.
- `/me` - Profil ma'lumotlari va referral link.
