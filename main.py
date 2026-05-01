import os
import requests
import asyncio
import datetime
import random
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

# 1. تحميل الإعدادات من ملف .env المخفي
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# التحقق من وجود البيانات لضمان عدم توقف البرنامج
if not TELEGRAM_TOKEN or not CHAT_ID:
    print("❌ خطأ: لم يتم العثور على TELEGRAM_TOKEN أو CHAT_ID في ملف .env")
    exit()

bot = Bot(token=TELEGRAM_TOKEN)

# 2. وظائف جلب البيانات
async def fetch_energy():
    """جلب أسعار الكهرباء من ألمانيا"""
    url = "https://api.corrently.io/v2.0/gsi/marketdata?zip=10117"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        current_p = data['data'][0]['marketprice']
        all_prices = [item['marketprice'] for item in data['data']]
        avg_p = sum(all_prices) / len(all_prices)
        return current_p, avg_p
    except:
        return None, None

async def fetch_flights():
    """محاكاة صيد رحلات طيران رخيصة"""
    deals = [
        ("Paris 🇫🇷 ➔ Berlin 🇩🇪", 19.99),
        ("Tunis 🇹🇳 ➔ Marseille 🇫🇷", 45.00),
        ("Madrid 🇪🇸 ➔ Rome 🇮🇹", 15.50)
    ]
    return random.choice(deals)

# 3. المنطق الرياضي للتحليل
def analyze_market(current, avg):
    if current is None: return "⚪️ غير متاح"
    diff = ((current - avg) / avg) * 100
    if diff < -10: return "🔥 فرصة توفير كبيرة"
    if diff < 0: return "✅ سعر جيد"
    return "⚠️ سعر مرتفع"

# 4. إرسال التقرير الشامل
async def send_intelligence_report():
    print(f"📡 جاري تحليل البيانات... {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    curr_e, avg_e = await fetch_energy()
    route, price = await fetch_flights()
    
    status = analyze_market(curr_e, avg_e)
    
    report = (
        f"🏛 *نظام ياسمينة للاستخبارات الاقتصادية* 🏛\n"
        f"📅 `{datetime.datetime.now().strftime('%d/%m/%Y | %H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡️ *قطاع الطاقة (EU):*\n"
        f"• السعر: `{curr_e:.2f} c/kWh`\n"
        f"• الحالة: *{status}*\n\n"
        f"⛽️ *قطاع الوقود (E5):*\n"
        f"• السعر المتوقع: `1.70 €/L` 🟢\n\n"
        f"✈️ *أرخص رحلة اليوم:*\n"
        f"🎫 `{route}`\n"
        f"💰 السعر: *{price:.2f} €*\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🤖 *حالة البوت:* آمن ومتصل عبر بيئة العمل الخاصة."
    )

    try:
        await bot.send_message(chat_id=CHAT_ID, text=report, parse_mode=ParseMode.MARKDOWN)
        print("✅ تم إرسال التقرير بنجاح!")
    except Exception as e:
        print(f"❌ فشل الإرسال: {e}")

# 5. الدورة التشغيلية
async def main():
    print("🚀 الرادار المحدث يعمل الآن بنظام الأمان .env")
    # إرسال تقرير فور التشغيل للتأكد من الربط
    await send_intelligence_report()
    
    while True:
        # فحص كل 6 ساعات
        await asyncio.sleep(21600)
        await send_intelligence_report()

if __name__ == "__main__":
    asyncio.run(main())