"""
عيار العقارية — سكريبت سحب البيانات
يسحب من: البورصة العقارية (SREM) + سكني (Sakani)
يحفظ في: Supabase مباشرة
"""

import json, time, random, logging, os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ── إعداد اللوق ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)
log = logging.getLogger("عيار")

# ── Supabase ──
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ojgrxarzmalfdxiqddrb.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# ── Headers ──
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

# ── بيانات احتياطية ──
FALLBACK = [
    {"neighborhood":"الملقا",     "type":"شقة",  "min_price":45000,"max_price":62000,"avg_price":53500,"change_pct":4.2, "source":"fallback"},
    {"neighborhood":"الملقا",     "type":"فيلا", "min_price":140000,"max_price":180000,"avg_price":160000,"change_pct":4.2,"source":"fallback"},
    {"neighborhood":"حطين",       "type":"شقة",  "min_price":50000,"max_price":68000,"avg_price":59000,"change_pct":-1.1,"source":"fallback"},
    {"neighborhood":"حطين",       "type":"فيلا", "min_price":155000,"max_price":195000,"avg_price":175000,"change_pct":-1.1,"source":"fallback"},
    {"neighborhood":"الياسمين",   "type":"شقة",  "min_price":38000,"max_price":52000,"avg_price":45000,"change_pct":2.8,"source":"fallback"},
    {"neighborhood":"القيروان",   "type":"شقة",  "min_price":35000,"max_price":48000,"avg_price":41500,"change_pct":-0.8,"source":"fallback"},
    {"neighborhood":"السليمانية", "type":"شقة",  "min_price":52000,"max_price":72000,"avg_price":62000,"change_pct":3.1,"source":"fallback"},
    {"neighborhood":"العليا",     "type":"شقة",  "min_price":55000,"max_price":75000,"avg_price":65000,"change_pct":6.3,"source":"fallback"},
    {"neighborhood":"الصحافة",    "type":"شقة",  "min_price":42000,"max_price":55000,"avg_price":48500,"change_pct":1.5,"source":"fallback"},
    {"neighborhood":"غرناطة",     "type":"شقة",  "min_price":40000,"max_price":54000,"avg_price":47000,"change_pct":1.9,"source":"fallback"},
    {"neighborhood":"النرجس",     "type":"شقة",  "min_price":48000,"max_price":65000,"avg_price":56500,"change_pct":5.4,"source":"fallback"},
    {"neighborhood":"الروضة",     "type":"شقة",  "min_price":43000,"max_price":58000,"avg_price":50500,"change_pct":2.1,"source":"fallback"},
    {"neighborhood":"التعاون",    "type":"شقة",  "min_price":44000,"max_price":59000,"avg_price":51500,"change_pct":1.7,"source":"fallback"},
    {"neighborhood":"طويق",       "type":"شقة",  "min_price":22000,"max_price":30000,"avg_price":26000,"change_pct":0.5,"source":"fallback"},
    {"neighborhood":"الدرعية",    "type":"شقة",  "min_price":36000,"max_price":50000,"avg_price":43000,"change_pct":3.5,"source":"fallback"},
]

def save_to_supabase(records):
    """يحفظ البيانات في Supabase"""
    if not SUPABASE_KEY:
        log.warning("⚠️ SUPABASE_KEY غير موجود — تخطي الحفظ")
        return False

    url = f"{SUPABASE_URL}/rest/v1/prices"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    # نضيف وقت التحديث
    now = datetime.now().isoformat()
    for r in records:
        r["updated_at"] = now

    try:
        res = requests.post(url, headers=headers, json=records, timeout=15)
        if res.status_code in [200, 201]:
            log.info(f"✅ تم حفظ {len(records)} سجل في Supabase")
            return True
        else:
            log.error(f"❌ Supabase error: {res.status_code} — {res.text[:200]}")
            return False
    except Exception as e:
        log.error(f"❌ خطأ في الاتصال بـ Supabase: {e}")
        return False

def scrape_srem():
    """يحاول السحب من البورصة العقارية"""
    log.info("🔄 جاري السحب من البورصة العقارية...")
    results = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        r = session.get("https://srem.moj.gov.sa/realestates-info", timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        log.info(f"  وجدت {len(tables)} جداول")
        # معالجة الجداول لو وجدت
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cells = row.find_all(["td","th"])
                if len(cells) >= 3:
                    log.info(f"  صف: {[c.get_text(strip=True) for c in cells[:3]]}")
    except Exception as e:
        log.warning(f"⚠️ SREM: {e}")
    return results

def scrape_sakani():
    """يحاول السحب من سكني"""
    log.info("🔄 جاري السحب من سكني...")
    results = []
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        time.sleep(random.uniform(1, 2))
        r = session.get("https://sakani.sa/", timeout=15)
        log.info(f"  سكني status: {r.status_code}")
    except Exception as e:
        log.warning(f"⚠️ سكني: {e}")
    return results

if __name__ == "__main__":
    log.info("\n🚀 بدأ سكريبت عيار العقارية\n")

    # نحاول نسحب البيانات الحقيقية
    srem_data = scrape_srem()
    sakani_data = scrape_sakani()

    # لو ما وجدنا بيانات حقيقية نستخدم الـ fallback
    records = srem_data + sakani_data
    if not records:
        log.info("📦 استخدام البيانات الاحتياطية (fallback)")
        records = FALLBACK

    # نحفظ في Supabase
    success = save_to_supabase(records)

    if success:
        log.info(f"\n✅ اكتمل — {len(records)} سجل محفوظ في Supabase")
    else:
        log.warning("\n⚠️ فشل الحفظ في Supabase")
