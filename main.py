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
    """دالة جلب البيانات مع ضمان إعادة قيم رقمية أو أصفار عند الفشل"""
    url = "https://api.corrently.io/v2.0/gsi/marketdata?zip=10117"
    try:
        # إضافة timeout أطول لبيئة GitHub Cloud
        res = requests.get(url, timeout=20)
        if res.status_code == 200:
            data = res.json()
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0].get('marketprice')
                # حساب المتوسط بأمان
                prices = [item.get('marketprice') for item in data['data'] if item.get('marketprice')]
                avg = sum(prices) / len(prices) if prices else 0
                return current, avg
    except Exception as e:
        print(f"📡 API Warning: {e}")
    
    # في حال الفشل، نعيد أصفار بدلاً من None لمنع خطأ الـ Unpacking
    return 0.0, 0.0

async def send_report():
    if not TOKEN or not ID:
        print("❌ Secrets missing!")
        return

    # جلب البيانات (الآن آمنة تماماً)
    curr_e, avg_e = await fetch_energy()
    
    # منطق الرسالة
    energy_status = "✅ جيد" if curr_e <= avg_e and curr_e != 0 else "⚠️ مرتفع أو غير متوفر"
    energy_display = f"{curr_e:.2f} c/kWh" if curr_e != 0 else "جاري التحديث..."

    bot = Bot(token=TOKEN)
    report = (
        f"🏛 *نظام ياسمينة السحابي (V4)* 🏛\n"
        f"📅 `{datetime.datetime.now().strftime('%d/%m/%Y | %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ طاقة: `{energy_display}`\n"
        f"📊 تحليل: *{energy_status}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🤖 التشغيل: GitHub Actions Success"
    )

    try:
        # استخدام الطريقة المتوافقة مع أحدث نسخ المكتبة
        async with bot:
            await bot.send_message(chat_id=ID, text=report, parse_mode='Markdown')
        print("🚀 Success! Message sent.")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_report())
