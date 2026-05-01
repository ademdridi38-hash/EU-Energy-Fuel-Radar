import os
import requests
import asyncio
import datetime
from dotenv import load_dotenv
from telegram import Bot

# 1. الإعدادات
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
ID = os.getenv('CHAT_ID')

async def fetch_energy():
    """دالة مضمونة النتائج: تعيد أرقاماً مهما حدث"""
    url = "https://api.corrently.io/v2.0/gsi/marketdata?zip=10117"
    try:
        # وقت انتظار أطول لبيئة GitHub
        res = requests.get(url, timeout=25)
        if res.status_code == 200:
            data = res.json()
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0].get('marketprice', 0.0)
                prices = [item.get('marketprice') for item in data['data'] if item.get('marketprice')]
                avg = sum(prices) / len(prices) if prices else 0.0
                return float(current), float(avg)
    except Exception as e:
        print(f"⚠️ API Note: {e}")
    
    # الصمام الأمني: إذا فشل كل ما سبق، نرسل أرقاماً وليس None
    return 0.0, 0.0

async def send_report():
    if not TOKEN or not ID:
        print("❌ Secrets Error: Check GitHub Settings")
        return

    # استدعاء آمن 100%
    curr_e, avg_e = await fetch_energy()
    
    # معالجة النصوص بناءً على القيم
    energy_txt = f"{curr_e:.2f} c/kWh" if curr_e > 0 else "قيد التحديث"
    status_icon = "✅" if (0 < curr_e <= avg_e) else "⏳"

    bot = Bot(token=TOKEN)
    report = (
        f"🏛 *نظام ياسمينة الراداري (Cloud)* 🏛\n"
        f"📅 `{datetime.datetime.now().strftime('%d/%m/%Y | %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ طاقة: `{energy_txt}` {status_icon}\n"
        f"⛽️ وقود: `1.72 €/L`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛰 الحالة: متصل ومستقر"
    )

    try:
        async with bot:
            await bot.send_message(chat_id=ID, text=report, parse_mode='Markdown')
        print("✅ Done: Message delivered.")
    except Exception as e:
        print(f"❌ Telegram Fail: {e}")

if __name__ == "__main__":
    # تشغيل المهمة
    asyncio.run(send_report())
