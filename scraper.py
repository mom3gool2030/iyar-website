import json, os, logging
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger("iyar")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ojgrxarzmalfdxiqddrb.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
REGA_BASE = "https://rentalrei.rega.gov.sa/RegaIndicatorsAPIs/api/IndicatorEjar"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Content-Type": "application/json",
    "Referer": "https://rentalrei.rega.gov.sa/",
    "Origin": "https://rentalrei.rega.gov.sa"
}

FALLBACK = [
    {"neighborhood":"\u0627\u0644\u0645\u0644\u0642\u0627","type":"\u0634\u0642\u0629","min_price":45000,"max_price":62000,"avg_price":53500,"change_pct":4.2,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u0645\u0644\u0642\u0627","type":"\u0641\u064a\u0644\u0627","min_price":140000,"max_price":180000,"avg_price":160000,"change_pct":4.2,"source":"fallback"},
    {"neighborhood":"\u062d\u0637\u064a\u0646","type":"\u0634\u0642\u0629","min_price":50000,"max_price":68000,"avg_price":59000,"change_pct":-1.1,"source":"fallback"},
    {"neighborhood":"\u062d\u0637\u064a\u0646","type":"\u0641\u064a\u0644\u0627","min_price":155000,"max_price":195000,"avg_price":175000,"change_pct":-1.1,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u064a\u0627\u0633\u0645\u064a\u0646","type":"\u0634\u0642\u0629","min_price":38000,"max_price":52000,"avg_price":45000,"change_pct":2.8,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u0642\u064a\u0631\u0648\u0627\u0646","type":"\u0634\u0642\u0629","min_price":35000,"max_price":48000,"avg_price":41500,"change_pct":-0.8,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u0633\u0644\u064a\u0645\u0627\u0646\u064a\u0629","type":"\u0634\u0642\u0629","min_price":52000,"max_price":72000,"avg_price":62000,"change_pct":3.1,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u0639\u0644\u064a\u0627","type":"\u0634\u0642\u0629","min_price":55000,"max_price":75000,"avg_price":65000,"change_pct":6.3,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u0635\u062d\u0627\u0641\u0629","type":"\u0634\u0642\u0629","min_price":42000,"max_price":55000,"avg_price":48500,"change_pct":1.5,"source":"fallback"},
    {"neighborhood":"\u0627\u0644\u0646\u0631\u062c\u0633","type":"\u0634\u0642\u0629","min_price":48000,"max_price":65000,"avg_price":56500,"change_pct":5.4,"source":"fallback"},
]

def get_token():
    log.info("Getting REGA token...")
    r = requests.post(REGA_BASE + "/GetToken", headers=HEADERS, json={}, timeout=15)
    token = r.text.strip().replace('"', '')
    log.info("Token received: " + token[:20])
    return token

def get_districts(token, city_id=21):
    log.info("Getting districts for city: " + str(city_id))
    r = requests.get(
        REGA_BASE + "/GetDistrictsByCityId?cityId=" + str(city_id),
        headers=dict(HEADERS, Authorization="Bearer " + token),
        timeout=15
    )
    data = r.json()
    log.info("Districts count: " + str(len(data)))
    return data

def get_details(token, district_id):
    r = requests.get(
        REGA_BASE + "/GetDetailsV2?districtId=" + str(district_id),
        headers=dict(HEADERS, Authorization="Bearer " + token),
        timeout=15
    )
    return r.json()

def save_supabase(records):
    if not SUPABASE_KEY:
        log.warning("No SUPABASE_KEY found")
        return False
    now = datetime.now().isoformat()
    for rec in records:
        rec["updated_at"] = now
    r = requests.post(
        SUPABASE_URL + "/rest/v1/prices",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": "Bearer " + SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        },
        json=records,
        timeout=15
    )
    log.info("Supabase status: " + str(r.status_code))
    return r.status_code in [200, 201]

def save_json(records):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    neighborhoods = {}
    ticker = []
    for rec in records:
        name = rec.get("neighborhood", "")
        ptype = rec.get("type", "")
        avg = rec.get("avg_price", 0)
        mn = rec.get("min_price", 0)
        mx = rec.get("max_price", 0)
        change = rec.get("change_pct", 0)
        source = rec.get("source", "rega")
        if name not in neighborhoods:
            neighborhoods[name] = {"change": change, "source": source}
        neighborhoods[name][ptype] = [mn, mx]
        neighborhoods[name][ptype + "_avg"] = avg
        ticker.append({"name": name, "type": ptype, "avg": avg, "change": change, "source": source})
    output = {"updated_at": now, "neighborhoods": neighborhoods, "ticker": ticker}
    with open("data/prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    log.info("Saved prices.json with " + str(len(records)) + " records")

if __name__ == "__main__":
    log.info("=== Iyar Scraper Started ===")
    records = []
    try:
        token = get_token()
        districts = get_districts(token)
        type_map = {1: "\u0634\u0642\u0629", 2: "\u0641\u064a\u0644\u0627", 3: "\u062f\u0648\u0631"}
        count = 0
        for district in districts[:30]:
            dist_id = district.get("id") or district.get("districtId")
            dist_name = district.get("nameAr") or district.get("districtNameAr", "")
            if not dist_id or not dist_name:
                continue
            try:
                details = get_details(token, dist_id)
                for prop_type_id, prop_type_name in type_map.items():
                    avg = 0
                    mn = 0
                    mx = 0
                    if isinstance(details, list):
                        for item in details:
                            if item.get("propertyType") == prop_type_id or item.get("propertyTypeId") == prop_type_id:
                                avg = item.get("avgPrice") or item.get("averagePrice") or 0
                                mn = item.get("minPrice") or 0
                                mx = item.get("maxPrice") or 0
                    elif isinstance(details, dict):
                        avg = details.get("avgPrice") or details.get("averagePrice") or 0
                        mn = details.get("minPrice") or 0
                        mx = details.get("maxPrice") or 0
                    if avg > 0:
                        records.append({
                            "neighborhood": dist_name,
                            "type": prop_type_name,
                            "min_price": mn,
                            "max_price": mx,
                            "avg_price": avg,
                            "change_pct": 0,
                            "source": "rega"
                        })
                        count += 1
            except Exception as e:
                log.warning("District " + str(dist_id) + " error: " + str(e))
        log.info("Got " + str(count) + " records from REGA")
    except Exception as e:
        log.warning("REGA failed: " + str(e))
        log.info("Using fallback data")
        records = FALLBACK

    if not records:
        records = FALLBACK

    save_json(records)
    save_supabase(records)
    log.info("=== Done ===")
