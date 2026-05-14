"""
عيار العقارية — سكريبت سحب البيانات
يسحب من: البورصة العقارية (SREM) + سكني (Sakani)
يحفظ النتيجة في: data/prices.json
"""

import json, time, random, logging
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── إعداد اللوق ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)
log = logging.getLogger("عيار-سكريبت")

# ── Headers تحاكي متصفح حقيقي ──
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

# ── الأحياء المستهدفة ──
NEIGHBORHOODS = [
    "الملقا", "حطين", "الياسمين", "القيروان",
    "السليمانية", "العليا", "الصحافة", "غرناطة",
    "النرجس", "الروضة", "التعاون", "طويق",
    "العريجاء", "شبرا", "الدرعية",
]

# ── بيانات احتياطية (fallback) لو فشل السحب ──
FALLBACK = {
    "الملقا":      {"شقة": [45000, 62000], "فيلا": [140000, 180000], "دور": [75000,  95000], "change": 4.2},
    "حطين":        {"شقة": [50000, 68000], "فيلا": [155000, 195000], "دور": [85000, 110000], "change": -1.1},
    "الياسمين":    {"شقة": [38000, 52000], "فيلا": [110000, 145000], "دور": [65000,  82000], "change": 2.8},
    "القيروان":    {"شقة": [35000, 48000], "فيلا": [100000, 135000], "دور": [58000,  75000], "change": -0.8},
    "السليمانية":  {"شقة": [52000, 72000], "فيلا": [160000, 210000], "دور": [90000, 115000], "change": 3.1},
    "العليا":      {"شقة": [55000, 75000], "فيلا": [170000, 220000], "دور": [95000, 125000], "change": 6.3},
    "الصحافة":     {"شقة": [42000, 55000], "فيلا": [115000, 148000], "دور": [68000,  85000], "change": 1.5},
    "غرناطة":      {"شقة": [40000, 54000], "فيلا": [112000, 145000], "دور": [65000,  82000], "change": 1.9},
    "النرجس":      {"شقة": [48000, 65000], "فيلا": [135000, 175000], "دور": [78000,  98000], "change": 5.4},
    "الروضة":      {"شقة": [43000, 58000], "فيلا": [120000, 155000], "دور": [70000,  88000], "change": 2.1},
    "التعاون":     {"شقة": [44000, 59000], "فيلا": [125000, 160000], "دور": [72000,  90000], "change": 1.7},
    "طويق":        {"شقة": [22000, 30000], "فيلا": [ 65000,  85000], "دور": [38000,  50000], "change": 0.5},
    "العريجاء":    {"شقة": [25000, 35000], "فيلا": [ 70000,  92000], "دور": [42000,  55000], "change": 0.9},
    "شبرا":        {"شقة": [28000, 38000], "فيلا": [ 80000, 105000], "دور": [48000,  62000], "change": 1.2},
    "الدرعية":     {"شقة": [36000, 50000], "فيلا": [105000, 140000], "دور": [60000,  78000], "change": 3.5},
}


# ══════════════════════════════════════════
#   السحب من البورصة العقارية (SREM)
# ══════════════════════════════════════════
def scrape_srem() -> dict:
    """يحاول يسحب مؤشرات الأسعار من صفحة البورصة العقارية العامة"""
    log.info("🔄 جاري السحب من البورصة العقارية...")
    results = {}

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # صفحة المؤشرات العامة (لا تحتاج تسجيل دخول)
        url = "https://srem.moj.gov.sa/realestates-info"
        r = session.get(url, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # نبحث عن أي جدول أو قسم يحتوي أسعار
        # SREM يعرض البيانات في جداول أو divs بكلاسات محددة
        tables = soup.find_all("table")
        cards  = soup.find_all(class_=lambda c: c and any(
            x in c for x in ["price", "indicator", "neighborhood", "حي", "سعر"]
        ))

        log.info(f"  وجدت {len(tables)} جداول و {len(cards)} بطاقات")

        # نحاول نقرأ الجداول
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    name = cells[0].get_text(strip=True)
                    # لو اسم الحي موجود في قائمتنا
                    for hood in NEIGHBORHOODS:
                        if hood in name:
                            try:
                                price_text = cells[1].get_text(strip=True)
                                price = int("".join(filter(str.isdigit, price_text)))
                                if 10000 < price < 500000:  # نطاق منطقي
                                    if hood not in results:
                                        results[hood] = {}
                                    results[hood]["شقة"] = [
                                        int(price * 0.85),
                                        int(price * 1.15)
                                    ]
                                    log.info(f"  ✅ {hood}: {price:,} ر.س")
                            except (ValueError, IndexError):
                                pass

        if results:
            log.info(f"✅ SREM: سحبت {len(results)} حياً")
        else:
            log.warning("⚠️ SREM: ما وجدنا بيانات منظمة — سيُستخدم الـ fallback")

    except requests.exceptions.RequestException as e:
        log.error(f"❌ SREM خطأ في الاتصال: {e}")
    except Exception as e:
        log.error(f"❌ SREM خطأ غير متوقع: {e}")

    return results


# ══════════════════════════════════════════
#   السحب من سكني
# ══════════════════════════════════════════
def scrape_sakani() -> dict:
    """يحاول يسحب بيانات الأسعار من صفحة التقارير في سكني"""
    log.info("🔄 جاري السحب من سكني...")
    results = {}

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # صفحة التقارير والبيانات العامة
        urls_to_try = [
            "https://sakani.sa/reports-and-data",
            "https://sakani.sa/app/",
        ]

        for url in urls_to_try:
            try:
                time.sleep(random.uniform(1.5, 3.0))  # تأخير عشوائي
                r = session.get(url, timeout=15)

                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")

                    # نبحث عن أسعار
                    price_elements = soup.find_all(
                        string=lambda t: t and any(
                            x in t for x in ["ر.س", "ريال", "الإيجار", "متوسط"]
                        )
                    )

                    for elem in price_elements:
                        parent_text = elem.parent.get_text(" ", strip=True)
                        for hood in NEIGHBORHOODS:
                            if hood in parent_text:
                                digits = "".join(filter(str.isdigit, parent_text.split(hood)[-1][:20]))
                                if digits and 10000 < int(digits) < 500000:
                                    if hood not in results:
                                        results[hood] = {}
                                    price = int(digits)
                                    results[hood]["شقة"] = [
                                        int(price * 0.88),
                                        int(price * 1.12)
                                    ]
                                    log.info(f"  ✅ سكني — {hood}: {price:,} ر.س")

                    if results:
                        break

            except requests.exceptions.RequestException:
                continue

        if results:
            log.info(f"✅ سكني: سحبت {len(results)} حياً")
        else:
            log.warning("⚠️ سكني: ما وجدنا بيانات منظمة — سيُستخدم الـ fallback")

    except Exception as e:
        log.error(f"❌ سكني خطأ: {e}")

    return results


# ══════════════════════════════════════════
#   دمج البيانات وحفظها
# ══════════════════════════════════════════
def merge_and_save(srem_data: dict, sakani_data: dict) -> None:
    """يدمج البيانات ويحفظ النتيجة النهائية في data/prices.json"""

    final = {}

    for hood in NEIGHBORHOODS:
        # نبدأ بالـ fallback
        entry = dict(FALLBACK.get(hood, {}))

        # نحدّث بالبيانات الحقيقية لو متوفرة
        if hood in srem_data:
            entry.update(srem_data[hood])
            entry["source"] = "srem"
        elif hood in sakani_data:
            entry.update(sakani_data[hood])
            entry["source"] = "sakani"
        else:
            entry["source"] = "fallback"

        # نحسب المتوسط لكل نوع
        for prop_type in ["شقة", "فيلا", "دور"]:
            if prop_type in entry and isinstance(entry[prop_type], list):
                mn, mx = entry[prop_type]
                entry[f"{prop_type}_avg"] = (mn + mx) // 2

        final[hood] = entry

    # نبني ملف الـ JSON النهائي
    output = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "neighborhoods": final,
        # شريط التيكر — أعلى 8 أحياء حركةً
        "ticker": [
            {
                "name": name,
                "type": "شقة",
                "avg": data.get("شقة_avg", 0),
                "change": data.get("change", 0),
                "source": data.get("source", "fallback")
            }
            for name, data in final.items()
            if data.get("شقة_avg", 0) > 0
        ][:8]
    }

    # حفظ الملف
    out_path = Path("data/prices.json")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # ملخص
    real  = sum(1 for v in final.values() if v.get("source") != "fallback")
    total = len(final)
    log.info(f"\n{'='*45}")
    log.info(f"✅ تم الحفظ في data/prices.json")
    log.info(f"📊 بيانات حقيقية: {real}/{total} حي")
    log.info(f"🕐 وقت التحديث: {output['updated_at']}")
    log.info(f"{'='*45}\n")


# ══════════════════════════════════════════
#   التشغيل الرئيسي
# ══════════════════════════════════════════
if __name__ == "__main__":
    log.info("\n🚀 بدأ سكريبت عيار العقارية\n")

    srem_data   = scrape_srem()
    time.sleep(2)
    sakani_data = scrape_sakani()

    merge_and_save(srem_data, sakani_data)
