import os
import requests
import asyncio
import datetime
from dotenv import load_dotenv
from telegram import Bot

# تحميل الإعدادات
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
ID = os.getenv('CHAT_ID')

async def fetch_energy():
    """جلب البيانات مع ضمان عدم العودة بـ None أبداً"""
    url = "https://api.corrently.io/v2.0/gsi/marketdata?zip=10117"
    try:
        # رفع الـ timeout لضمان استجابة خوادم GitHub الثقيلة
        res = requests.get(url, timeout=25)
        if res.status_code == 200:
            data = res.json()
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0].get('marketprice', 0.0)
                prices = [item.get('marketprice') for item in data['data'] if item.get('marketprice')]
                avg = sum(prices) / len(prices) if prices else 0.0
                return float(current), float(avg)
    except Exception as e:
        print(f"📡 API Note: {e}")
    
    # العودة بقيم افتراضية بدلاً من None لمنع خطأ الـ Unpacking
    return 0.0, 0.0

async def send_report():
    if not TOKEN or not ID:
        print("❌ Missing Secrets in GitHub Settings!")
        return

    # استلام القيم (مضمون أنها لن تكون None الآن)
    curr_e, avg_e = await fetch_energy()
    
    # تنسيق العرض
    energy_display = f"{curr_e:.2f} c/kWh" if curr_e > 0 else "Pending Update"
    status = "✅ Stable" if (0 < curr_e <= avg_e) else "📊 Scanning"

    bot = Bot(token=TOKEN)
    report = (
        f"🏛 *نظام ياسمينة السحابي* 🏛\n"
        f"📅 `{datetime.datetime.now().strftime('%d/%m/%Y | %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ الطاقة: `{energy_display}`\n"
        f"📈 الحالة: *{status}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✅ التشغيل آلي عبر GitHub Actions"
    )

    try:
        async with bot:
            await bot.send_message(chat_id=ID, text=report, parse_mode='Markdown')
        print("✅ Process Completed Successfully")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_report())
