import os
import requests
import asyncio
import datetime
import random
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

# تحميل الإعدادات (تعمل محلياً من .env وفي GitHub من الـ Secrets)
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

async def fetch_energy():
    url = "https://api.corrently.io/v2.0/gsi/marketdata?zip=10117"
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
        if 'data' in data and len(data['data']) > 0:
            current_p = data['data'][0].get('marketprice')
            all_prices = [item.get('marketprice') for item in data['data'] if item.get('marketprice')]
            avg_p = sum(all_prices) / len(all_prices) if all_prices else None
            return current_p, avg_p
    except:
        return None, None

async def fetch_flights():
    deals = [("Paris 🇫🇷 ➔ Berlin 🇩🇪", 19.99), ("Tunis 🇹🇳 ➔ Marseille 🇫🇷", 45.00), ("Madrid 🇪🇸 ➔ Rome 🇮🇹", 15.50)]
    return random.choice(deals)

def analyze_market(current, avg):
    if current is None or avg is None: return "⚪️ الحالة: غير متوفرة"
    diff = ((current - avg) / avg) * 100
    if diff < -10: return "🔥 الحالة: فرصة توفير كبيرة"
    return "✅ الحالة: سعر جيد" if diff < 0 else "⚠️ الحالة: سعر مرتفع"

async def send_report():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing Environment Variables")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    curr_e, avg_e = await fetch_energy()
    route, price = await fetch_flights()
    
    energy_val = f"{curr_e:.2f} c/kWh" if curr_e is not None else "تحديث جاري..."
    
    report = (
        f"🏛 *نظام ياسمينة الذاتي (GitHub Cloud)* 🏛\n"
        f"📅 `{datetime.datetime.now().strftime('%d/%m/%Y | %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡️ *الطاقة:* `{energy_val}`\n"
        f"📈 *التحليل:* {analyze_market(curr_e, avg_e)}\n\n"
        f"✈️ *أرخص رحلة:* `{route}`\n"
        f"💰 السعر: *{price:.2f} €*\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🤖 *الوضع:* أتمتة كاملة (Serverless)"
    )

    await bot.send_message(chat_id=CHAT_ID, text=report, parse_mode=ParseMode.MARKDOWN)
    print("✅ Report Sent Successfully via GitHub Actions")

if __name__ == "__main__":
    # تشغيل المهمة مرة واحدة فقط
    asyncio.run(send_report())
