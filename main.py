import logging
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# --- SIZNING MA'LUMOTLARINGIZ (ZAXIRA VA SERVER SOZLAMALARI) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8967368321:AAETZvk_VQQGWXo34sYl8HWOjz2VD9V8wbM").strip()
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "8971381600").strip()
ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW.isdigit() else 8971381600
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mulohazatli.github.io/ucsavdominiappBOT/").strip()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start buyrug'i kelganda
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚡️ PUBG UC Sotib Olish (Mini App)",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                text="👨‍💻 Murojaat uchun Admin",
                url="https://t.me/Vagiahqvq"
            )
        ]
    ])

    text = (
        "⚡️ PUBG Mobile UC Store botiga xush kelibsiz! 😍\n\n"
        "O'yinga kundan kunga yangi Keys Ruletkalar qo'shilmoqda!\n"
        "Ishonchli va tezkor UC olish uchun pastdagi Mini App tugmasini bosing.\n\n"
        "💳 To'lov kartasi: 9860160633632619\n"
        "👤 Karta egasi: Javohir Abdullayev\n\n"
        "⚠️ *Biz UC to'liq tushishiga 100% javob beramiz!*"
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# Mini App orqali yuborilgan buyurtmalarni adminga yetkazish
@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get('action') == 'new_pubg_order':
            order = data['order']

            admin_text = (
                f"🚨 YANGI PUBG UC BUYURTMA!\n\n"
                f"📦 Paket: {order['uc']}\n"
                f"💰 Narxi: {order['price']} so'm\n"
                f"📌 Turi: {order['type'].upper()}\n"
            )

            if order['type'] == 'id':
                admin_text += f"🎮 PUBG ID: {order['pubgId']}\n"
            else:
                admin_text += f"🔑 Login: {order['loginAcc']}\n🔒 Parol: {order['loginPass']}\n"

            admin_text += (
                f"📞 Mijoz aloqasi: {order['contact']}\n"
                f"👤 Mijoz TG: @{message.from_user.username or 'Yoq'} (ID: {message.from_user.id})\n"
                f"⏰ Vaqt: {order['date']}"
            )

            admin_kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{message.from_user.id}"),
                    InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
                ]
            ])

            await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_kb, parse_mode="Markdown")
            await message.answer("✅ Buyurtmangiz adminga yuborildi! To'lov va chek tasdiqlangach UC o'yiningizga tushiriladi.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")

# Admin tugmalari bosilganda
@dp.callback_query(F.data.startswith("approve_"))
async def approve_order(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    try:
        await bot.send_message(user_id, "🎉 Buyurtmangiz tasdiqlandi! UC o'yin hesabingizga muvaffaqiyatli tushirildi.")
    except Exception:
        pass
    await callback.message.edit_text(callback.message.text + "\n\n✅ STATUS: Tasdiqlandi")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_order(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    try:
        await bot.send_message(user_id, "❌ Buyurtmangiz rad etildi. To'lov chekida xatolik yoki mablag' yetarli emas.")
    except Exception:
        pass
    await callback.message.edit_text(callback.message.text + "\n\n❌ STATUS: Rad etildi")

# Render.com serverining 24/7 ishlash pingsi
async def handle_ping(request):
    return web.Response(text="Bot is live 24/7!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
