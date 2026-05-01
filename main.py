import os
import requests
import asyncio
import datetime
from dotenv import load_dotenv
from telegram import Bot

# 1. شحن الإعدادات
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
ID = os.getenv('CHAT_ID')

async def send_report():
    """الدالة المركزية - دمج الجلب والإرسال لضمان الاستقرار"""
    
    if not TOKEN or not ID:
        print("❌ Missing Secrets!")
        return

    # قيم افتراضية آمنة (Default Values)
    curr_e, avg_e = 0.0, 0.0
    energy_txt = "قيد التحديث"
    
    # محاولة جلب البيانات داخل الدالة مباشرة
    try:
        url = "https://api.corrently.io/v2.0/gsi/marketdata?zip=10117"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            data = res.json()
            if 'data' in data and len(data['data']) > 0:
                curr_e = float(data['data'][0].get('marketprice', 0.0))
                prices = [item.get('marketprice') for item in data['data'] if item.get('marketprice')]
                avg_e = sum(prices) / len(prices) if prices else 0.0
                energy_txt = f"{curr_e:.2f} c/kWh"
    except Exception as e:
        print(f"📡 API Bypass: {e}")

    # بناء التقرير
    status_icon = "✅" if (0 < curr_e <= avg_e) else "⏳"
    
    report = (
        f"🏛 *نظام ياسمينة الراداري (V5)* 🏛\n"
        f"📅 `{datetime.datetime.now().strftime('%d/%m/%Y | %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ طاقة: `{energy_txt}` {status_icon}\n"
        f"⛽️ وقود: `1.75 €/L`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛰 الحالة: تشغيل سحابي مستقر"
    )

    # إرسال التقرير
    try:
        bot = Bot(token=TOKEN)
        async with bot:
            await bot.send_message(chat_id=ID, text=report, parse_mode='Markdown')
        print("🚀 Success: Message dispatched to Telegram")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_report())
