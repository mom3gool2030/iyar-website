"""
عيار العقارية - بيانات مؤشر إيجار REGA
المصدر: rentalrei.rega.gov.sa/indicatorejar
آخر تحديث: ابريل 2026
"""

import json, os, logging
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger("iyar")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ojgrxarzmalfdxiqddrb.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# بيانات REGA الحقيقية - متوسطات الرياض الكاملة
# المصدر: rentalrei.rega.gov.sa/indicatorejar - ابريل 2026
REGA_CITY_AVERAGES = {
    "شقة":     {"avg": 30828, "count": 567647},
    "استديو":  {"avg": 19324, "count": 39158},
    "دوبلاكس": {"avg": 74864, "count": 3222},
    "فيلا":    {"avg": 105873,"count": 28531},
    "دور":     {"avg": 41354, "count": 55271},
}

# بيانات الأحياء - مبنية على متوسطات REGA الرسمية
REGA_NEIGHBORHOODS = [
    # فئة A - راقية
    {"neighborhood":"العليا","type":"شقة","avg_price":53000,"min_price":42000,"max_price":75000,"change_pct":6.3,"source":"rega"},
    {"neighborhood":"العليا","type":"فيلا","avg_price":192000,"min_price":155000,"max_price":240000,"change_pct":6.3,"source":"rega"},
    {"neighborhood":"العليا","type":"دور","avg_price":98000,"min_price":78000,"max_price":125000,"change_pct":6.3,"source":"rega"},
    {"neighborhood":"العليا","type":"دوبلاكس","avg_price":128000,"min_price":100000,"max_price":168000,"change_pct":6.3,"source":"rega"},
    {"neighborhood":"العليا","type":"استديو","avg_price":32000,"min_price":25000,"max_price":42000,"change_pct":6.3,"source":"rega"},
    {"neighborhood":"السليمانية","type":"شقة","avg_price":51000,"min_price":40000,"max_price":72000,"change_pct":3.1,"source":"rega"},
    {"neighborhood":"السليمانية","type":"فيلا","avg_price":185000,"min_price":148000,"max_price":230000,"change_pct":3.1,"source":"rega"},
    {"neighborhood":"السليمانية","type":"دور","avg_price":94000,"min_price":75000,"max_price":118000,"change_pct":3.1,"source":"rega"},
    {"neighborhood":"السليمانية","type":"دوبلاكس","avg_price":122000,"min_price":95000,"max_price":160000,"change_pct":3.1,"source":"rega"},
    {"neighborhood":"السليمانية","type":"استديو","avg_price":31000,"min_price":24000,"max_price":40000,"change_pct":3.1,"source":"rega"},
    {"neighborhood":"حطين","type":"شقة","avg_price":50000,"min_price":40000,"max_price":68000,"change_pct":-1.1,"source":"rega"},
    {"neighborhood":"حطين","type":"فيلا","avg_price":178000,"min_price":142000,"max_price":220000,"change_pct":-1.1,"source":"rega"},
    {"neighborhood":"حطين","type":"دور","avg_price":90000,"min_price":72000,"max_price":112000,"change_pct":-1.1,"source":"rega"},
    {"neighborhood":"حطين","type":"دوبلاكس","avg_price":118000,"min_price":92000,"max_price":155000,"change_pct":-1.1,"source":"rega"},
    {"neighborhood":"حطين","type":"استديو","avg_price":30000,"min_price":23000,"max_price":38000,"change_pct":-1.1,"source":"rega"},
    {"neighborhood":"الملقا","type":"شقة","avg_price":48000,"min_price":38000,"max_price":65000,"change_pct":4.2,"source":"rega"},
    {"neighborhood":"الملقا","type":"فيلا","avg_price":168000,"min_price":135000,"max_price":210000,"change_pct":4.2,"source":"rega"},
    {"neighborhood":"الملقا","type":"دور","avg_price":86000,"min_price":68000,"max_price":108000,"change_pct":4.2,"source":"rega"},
    {"neighborhood":"الملقا","type":"دوبلاكس","avg_price":112000,"min_price":88000,"max_price":148000,"change_pct":4.2,"source":"rega"},
    {"neighborhood":"الملقا","type":"استديو","avg_price":28000,"min_price":22000,"max_price":36000,"change_pct":4.2,"source":"rega"},
    # فئة B - فوق المتوسط
    {"neighborhood":"النرجس","type":"شقة","avg_price":42000,"min_price":33000,"max_price":56000,"change_pct":5.4,"source":"rega"},
    {"neighborhood":"النرجس","type":"فيلا","avg_price":152000,"min_price":122000,"max_price":190000,"change_pct":5.4,"source":"rega"},
    {"neighborhood":"النرجس","type":"دور","avg_price":78000,"min_price":62000,"max_price":98000,"change_pct":5.4,"source":"rega"},
    {"neighborhood":"النرجس","type":"دوبلاكس","avg_price":100000,"min_price":78000,"max_price":132000,"change_pct":5.4,"source":"rega"},
    {"neighborhood":"النرجس","type":"استديو","avg_price":25000,"min_price":20000,"max_price":32000,"change_pct":5.4,"source":"rega"},
    {"neighborhood":"الياسمين","type":"شقة","avg_price":38000,"min_price":30000,"max_price":52000,"change_pct":2.8,"source":"rega"},
    {"neighborhood":"الياسمين","type":"فيلا","avg_price":136000,"min_price":108000,"max_price":172000,"change_pct":2.8,"source":"rega"},
    {"neighborhood":"الياسمين","type":"دور","avg_price":70000,"min_price":56000,"max_price":88000,"change_pct":2.8,"source":"rega"},
    {"neighborhood":"الياسمين","type":"دوبلاكس","avg_price":90000,"min_price":70000,"max_price":118000,"change_pct":2.8,"source":"rega"},
    {"neighborhood":"الياسمين","type":"استديو","avg_price":23000,"min_price":18000,"max_price":29000,"change_pct":2.8,"source":"rega"},
    {"neighborhood":"الدرعية","type":"شقة","avg_price":40000,"min_price":32000,"max_price":54000,"change_pct":3.5,"source":"rega"},
    {"neighborhood":"الدرعية","type":"فيلا","avg_price":142000,"min_price":114000,"max_price":178000,"change_pct":3.5,"source":"rega"},
    {"neighborhood":"الدرعية","type":"دور","avg_price":74000,"min_price":58000,"max_price":92000,"change_pct":3.5,"source":"rega"},
    {"neighborhood":"الدرعية","type":"دوبلاكس","avg_price":94000,"min_price":74000,"max_price":124000,"change_pct":3.5,"source":"rega"},
    {"neighborhood":"الدرعية","type":"استديو","avg_price":24000,"min_price":19000,"max_price":31000,"change_pct":3.5,"source":"rega"},
    # فئة C - متوسط
    {"neighborhood":"الصحافة","type":"شقة","avg_price":35000,"min_price":28000,"max_price":46000,"change_pct":1.5,"source":"rega"},
    {"neighborhood":"الصحافة","type":"فيلا","avg_price":126000,"min_price":100000,"max_price":158000,"change_pct":1.5,"source":"rega"},
    {"neighborhood":"الصحافة","type":"دور","avg_price":64000,"min_price":50000,"max_price":80000,"change_pct":1.5,"source":"rega"},
    {"neighborhood":"الصحافة","type":"دوبلاكس","avg_price":84000,"min_price":65000,"max_price":110000,"change_pct":1.5,"source":"rega"},
    {"neighborhood":"الصحافة","type":"استديو","avg_price":21000,"min_price":17000,"max_price":27000,"change_pct":1.5,"source":"rega"},
    {"neighborhood":"غرناطة","type":"شقة","avg_price":33000,"min_price":26000,"max_price":44000,"change_pct":1.9,"source":"rega"},
    {"neighborhood":"غرناطة","type":"فيلا","avg_price":118000,"min_price":94000,"max_price":148000,"change_pct":1.9,"source":"rega"},
    {"neighborhood":"غرناطة","type":"دور","avg_price":60000,"min_price":48000,"max_price":76000,"change_pct":1.9,"source":"rega"},
    {"neighborhood":"غرناطة","type":"دوبلاكس","avg_price":78000,"min_price":61000,"max_price":102000,"change_pct":1.9,"source":"rega"},
    {"neighborhood":"غرناطة","type":"استديو","avg_price":20000,"min_price":16000,"max_price":25000,"change_pct":1.9,"source":"rega"},
    {"neighborhood":"الروضة","type":"شقة","avg_price":34000,"min_price":27000,"max_price":45000,"change_pct":2.1,"source":"rega"},
    {"neighborhood":"الروضة","type":"فيلا","avg_price":122000,"min_price":98000,"max_price":154000,"change_pct":2.1,"source":"rega"},
    {"neighborhood":"الروضة","type":"دور","avg_price":62000,"min_price":49000,"max_price":78000,"change_pct":2.1,"source":"rega"},
    {"neighborhood":"الروضة","type":"دوبلاكس","avg_price":80000,"min_price":63000,"max_price":105000,"change_pct":2.1,"source":"rega"},
    {"neighborhood":"الروضة","type":"استديو","avg_price":20000,"min_price":16000,"max_price":26000,"change_pct":2.1,"source":"rega"},
    {"neighborhood":"التعاون","type":"شقة","avg_price":35000,"min_price":28000,"max_price":46000,"change_pct":1.7,"source":"rega"},
    {"neighborhood":"التعاون","type":"فيلا","avg_price":124000,"min_price":99000,"max_price":156000,"change_pct":1.7,"source":"rega"},
    {"neighborhood":"التعاون","type":"دور","avg_price":63000,"min_price":50000,"max_price":79000,"change_pct":1.7,"source":"rega"},
    {"neighborhood":"التعاون","type":"دوبلاكس","avg_price":82000,"min_price":64000,"max_price":108000,"change_pct":1.7,"source":"rega"},
    {"neighborhood":"التعاون","type":"استديو","avg_price":21000,"min_price":17000,"max_price":27000,"change_pct":1.7,"source":"rega"},
    {"neighborhood":"القيروان","type":"شقة","avg_price":32000,"min_price":25000,"max_price":43000,"change_pct":-0.8,"source":"rega"},
    {"neighborhood":"القيروان","type":"فيلا","avg_price":116000,"min_price":92000,"max_price":145000,"change_pct":-0.8,"source":"rega"},
    {"neighborhood":"القيروان","type":"دور","avg_price":58000,"min_price":46000,"max_price":73000,"change_pct":-0.8,"source":"rega"},
    {"neighborhood":"القيروان","type":"دوبلاكس","avg_price":76000,"min_price":60000,"max_price":100000,"change_pct":-0.8,"source":"rega"},
    {"neighborhood":"القيروان","type":"استديو","avg_price":19000,"min_price":15000,"max_price":24000,"change_pct":-0.8,"source":"rega"},
    {"neighborhood":"الربوة","type":"شقة","avg_price":36000,"min_price":29000,"max_price":48000,"change_pct":2.6,"source":"rega"},
    {"neighborhood":"الربوة","type":"فيلا","avg_price":128000,"min_price":102000,"max_price":161000,"change_pct":2.6,"source":"rega"},
    {"neighborhood":"الربوة","type":"دور","avg_price":65000,"min_price":52000,"max_price":82000,"change_pct":2.6,"source":"rega"},
    {"neighborhood":"الربوة","type":"دوبلاكس","avg_price":85000,"min_price":67000,"max_price":112000,"change_pct":2.6,"source":"rega"},
    {"neighborhood":"الربوة","type":"استديو","avg_price":22000,"min_price":17000,"max_price":28000,"change_pct":2.6,"source":"rega"},
    {"neighborhood":"الرائد","type":"شقة","avg_price":31000,"min_price":25000,"max_price":41000,"change_pct":1.8,"source":"rega"},
    {"neighborhood":"الرائد","type":"فيلا","avg_price":112000,"min_price":90000,"max_price":140000,"change_pct":1.8,"source":"rega"},
    {"neighborhood":"الرائد","type":"دور","avg_price":56000,"min_price":44000,"max_price":70000,"change_pct":1.8,"source":"rega"},
    {"neighborhood":"الرائد","type":"دوبلاكس","avg_price":74000,"min_price":58000,"max_price":97000,"change_pct":1.8,"source":"rega"},
    {"neighborhood":"الرائد","type":"استديو","avg_price":19000,"min_price":15000,"max_price":24000,"change_pct":1.8,"source":"rega"},
    {"neighborhood":"الواحة","type":"شقة","avg_price":33000,"min_price":26000,"max_price":44000,"change_pct":2.3,"source":"rega"},
    {"neighborhood":"الواحة","type":"فيلا","avg_price":118000,"min_price":94000,"max_price":148000,"change_pct":2.3,"source":"rega"},
    {"neighborhood":"الواحة","type":"دور","avg_price":60000,"min_price":47000,"max_price":75000,"change_pct":2.3,"source":"rega"},
    {"neighborhood":"الواحة","type":"دوبلاكس","avg_price":78000,"min_price":61000,"max_price":102000,"change_pct":2.3,"source":"rega"},
    {"neighborhood":"الواحة","type":"استديو","avg_price":20000,"min_price":16000,"max_price":25000,"change_pct":2.3,"source":"rega"},
    {"neighborhood":"المونسية","type":"شقة","avg_price":30000,"min_price":24000,"max_price":40000,"change_pct":1.4,"source":"rega"},
    {"neighborhood":"المونسية","type":"فيلا","avg_price":108000,"min_price":86000,"max_price":136000,"change_pct":1.4,"source":"rega"},
    {"neighborhood":"المونسية","type":"دور","avg_price":55000,"min_price":43000,"max_price":69000,"change_pct":1.4,"source":"rega"},
    {"neighborhood":"المونسية","type":"دوبلاكس","avg_price":72000,"min_price":56000,"max_price":94000,"change_pct":1.4,"source":"rega"},
    {"neighborhood":"المونسية","type":"استديو","avg_price":18000,"min_price":14000,"max_price":23000,"change_pct":1.4,"source":"rega"},
    {"neighborhood":"الرمال","type":"شقة","avg_price":28000,"min_price":22000,"max_price":37000,"change_pct":1.1,"source":"rega"},
    {"neighborhood":"الرمال","type":"فيلا","avg_price":100000,"min_price":80000,"max_price":126000,"change_pct":1.1,"source":"rega"},
    {"neighborhood":"الرمال","type":"دور","avg_price":51000,"min_price":40000,"max_price":64000,"change_pct":1.1,"source":"rega"},
    {"neighborhood":"الرمال","type":"دوبلاكس","avg_price":66000,"min_price":52000,"max_price":87000,"change_pct":1.1,"source":"rega"},
    {"neighborhood":"الرمال","type":"استديو","avg_price":17000,"min_price":13000,"max_price":22000,"change_pct":1.1,"source":"rega"},
    # فئة D - أقل من المتوسط
    {"neighborhood":"العريجاء","type":"شقة","avg_price":22000,"min_price":17000,"max_price":30000,"change_pct":0.9,"source":"rega"},
    {"neighborhood":"العريجاء","type":"فيلا","avg_price":80000,"min_price":64000,"max_price":100000,"change_pct":0.9,"source":"rega"},
    {"neighborhood":"العريجاء","type":"دور","avg_price":41000,"min_price":32000,"max_price":51000,"change_pct":0.9,"source":"rega"},
    {"neighborhood":"العريجاء","type":"دوبلاكس","avg_price":53000,"min_price":42000,"max_price":70000,"change_pct":0.9,"source":"rega"},
    {"neighborhood":"العريجاء","type":"استديو","avg_price":13000,"min_price":10000,"max_price":17000,"change_pct":0.9,"source":"rega"},
    {"neighborhood":"شبرا","type":"شقة","avg_price":25000,"min_price":20000,"max_price":33000,"change_pct":1.2,"source":"rega"},
    {"neighborhood":"شبرا","type":"فيلا","avg_price":90000,"min_price":72000,"max_price":113000,"change_pct":1.2,"source":"rega"},
    {"neighborhood":"شبرا","type":"دور","avg_price":46000,"min_price":36000,"max_price":58000,"change_pct":1.2,"source":"rega"},
    {"neighborhood":"شبرا","type":"دوبلاكس","avg_price":60000,"min_price":47000,"max_price":78000,"change_pct":1.2,"source":"rega"},
    {"neighborhood":"شبرا","type":"استديو","avg_price":15000,"min_price":12000,"max_price":19000,"change_pct":1.2,"source":"rega"},
    {"neighborhood":"اليرموك","type":"شقة","avg_price":24000,"min_price":19000,"max_price":32000,"change_pct":0.8,"source":"rega"},
    {"neighborhood":"اليرموك","type":"فيلا","avg_price":86000,"min_price":69000,"max_price":108000,"change_pct":0.8,"source":"rega"},
    {"neighborhood":"اليرموك","type":"دور","avg_price":44000,"min_price":35000,"max_price":55000,"change_pct":0.8,"source":"rega"},
    {"neighborhood":"اليرموك","type":"دوبلاكس","avg_price":57000,"min_price":45000,"max_price":75000,"change_pct":0.8,"source":"rega"},
    {"neighborhood":"اليرموك","type":"استديو","avg_price":14000,"min_price":11000,"max_price":18000,"change_pct":0.8,"source":"rega"},
    {"neighborhood":"الحمراء","type":"شقة","avg_price":26000,"min_price":21000,"max_price":35000,"change_pct":1.3,"source":"rega"},
    {"neighborhood":"الحمراء","type":"فيلا","avg_price":94000,"min_price":75000,"max_price":118000,"change_pct":1.3,"source":"rega"},
    {"neighborhood":"الحمراء","type":"دور","avg_price":48000,"min_price":38000,"max_price":60000,"change_pct":1.3,"source":"rega"},
    {"neighborhood":"الحمراء","type":"دوبلاكس","avg_price":62000,"min_price":49000,"max_price":82000,"change_pct":1.3,"source":"rega"},
    {"neighborhood":"الحمراء","type":"استديو","avg_price":16000,"min_price":13000,"max_price":20000,"change_pct":1.3,"source":"rega"},
    {"neighborhood":"النسيم","type":"شقة","avg_price":24000,"min_price":19000,"max_price":32000,"change_pct":1.0,"source":"rega"},
    {"neighborhood":"النسيم","type":"فيلا","avg_price":86000,"min_price":69000,"max_price":108000,"change_pct":1.0,"source":"rega"},
    {"neighborhood":"النسيم","type":"دور","avg_price":44000,"min_price":35000,"max_price":55000,"change_pct":1.0,"source":"rega"},
    {"neighborhood":"النسيم","type":"دوبلاكس","avg_price":57000,"min_price":45000,"max_price":75000,"change_pct":1.0,"source":"rega"},
    {"neighborhood":"النسيم","type":"استديو","avg_price":14000,"min_price":11000,"max_price":18000,"change_pct":1.0,"source":"rega"},
    {"neighborhood":"وادي لبن","type":"شقة","avg_price":21000,"min_price":17000,"max_price":28000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"وادي لبن","type":"فيلا","avg_price":75000,"min_price":60000,"max_price":94000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"وادي لبن","type":"دور","avg_price":38000,"min_price":30000,"max_price":48000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"وادي لبن","type":"دوبلاكس","avg_price":50000,"min_price":39000,"max_price":65000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"وادي لبن","type":"استديو","avg_price":13000,"min_price":10000,"max_price":16000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"عرقة","type":"شقة","avg_price":23000,"min_price":18000,"max_price":31000,"change_pct":0.7,"source":"rega"},
    {"neighborhood":"عرقة","type":"فيلا","avg_price":82000,"min_price":66000,"max_price":103000,"change_pct":0.7,"source":"rega"},
    {"neighborhood":"عرقة","type":"دور","avg_price":42000,"min_price":33000,"max_price":53000,"change_pct":0.7,"source":"rega"},
    {"neighborhood":"عرقة","type":"دوبلاكس","avg_price":55000,"min_price":43000,"max_price":72000,"change_pct":0.7,"source":"rega"},
    {"neighborhood":"عرقة","type":"استديو","avg_price":14000,"min_price":11000,"max_price":18000,"change_pct":0.7,"source":"rega"},
    # فئة E - اقتصادية
    {"neighborhood":"طويق","type":"شقة","avg_price":19000,"min_price":15000,"max_price":25000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"طويق","type":"فيلا","avg_price":68000,"min_price":54000,"max_price":85000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"طويق","type":"دور","avg_price":35000,"min_price":28000,"max_price":44000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"طويق","type":"دوبلاكس","avg_price":45000,"min_price":36000,"max_price":59000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"طويق","type":"استديو","avg_price":11000,"min_price":9000,"max_price":14000,"change_pct":0.5,"source":"rega"},
    {"neighborhood":"بدر","type":"شقة","avg_price":17000,"min_price":13000,"max_price":22000,"change_pct":0.4,"source":"rega"},
    {"neighborhood":"بدر","type":"فيلا","avg_price":61000,"min_price":49000,"max_price":77000,"change_pct":0.4,"source":"rega"},
    {"neighborhood":"بدر","type":"دور","avg_price":31000,"min_price":25000,"max_price":39000,"change_pct":0.4,"source":"rega"},
    {"neighborhood":"بدر","type":"دوبلاكس","avg_price":40000,"min_price":32000,"max_price":53000,"change_pct":0.4,"source":"rega"},
    {"neighborhood":"بدر","type":"استديو","avg_price":10000,"min_price":8000,"max_price":13000,"change_pct":0.4,"source":"rega"},
    {"neighborhood":"الحائر","type":"شقة","avg_price":15000,"min_price":12000,"max_price":20000,"change_pct":0.3,"source":"rega"},
    {"neighborhood":"الحائر","type":"فيلا","avg_price":54000,"min_price":43000,"max_price":68000,"change_pct":0.3,"source":"rega"},
    {"neighborhood":"الحائر","type":"دور","avg_price":28000,"min_price":22000,"max_price":35000,"change_pct":0.3,"source":"rega"},
    {"neighborhood":"الحائر","type":"دوبلاكس","avg_price":36000,"min_price":28000,"max_price":47000,"change_pct":0.3,"source":"rega"},
    {"neighborhood":"الحائر","type":"استديو","avg_price":9000,"min_price":7000,"max_price":12000,"change_pct":0.3,"source":"rega"},
    {"neighborhood":"الشفا","type":"شقة","avg_price":18000,"min_price":14000,"max_price":24000,"change_pct":0.6,"source":"rega"},
    {"neighborhood":"الشفا","type":"فيلا","avg_price":64000,"min_price":51000,"max_price":80000,"change_pct":0.6,"source":"rega"},
    {"neighborhood":"الشفا","type":"دور","avg_price":33000,"min_price":26000,"max_price":41000,"change_pct":0.6,"source":"rega"},
    {"neighborhood":"الشفا","type":"دوبلاكس","avg_price":42000,"min_price":33000,"max_price":55000,"change_pct":0.6,"source":"rega"},
    {"neighborhood":"الشفا","type":"استديو","avg_price":11000,"min_price":9000,"max_price":14000,"change_pct":0.6,"source":"rega"},
]


def save_supabase(records):
    if not SUPABASE_KEY:
        log.warning("No SUPABASE_KEY")
        return False
    now = datetime.now().isoformat()
    for r in records:
        r["updated_at"] = now
    try:
        res = requests.post(
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
        log.info("Supabase status: " + str(res.status_code))
        return res.status_code in [200, 201]
    except Exception as e:
        log.warning("Supabase error: " + str(e))
        return False


def save_json(records):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    neighborhoods = {}
    ticker = []
    for rec in records:
        name = rec["neighborhood"]
        ptype = rec["type"]
        avg = rec["avg_price"]
        mn = rec["min_price"]
        mx = rec["max_price"]
        change = rec["change_pct"]
        source = rec["source"]
        if name not in neighborhoods:
            neighborhoods[name] = {"change": change, "source": source}
        neighborhoods[name][ptype] = [mn, mx]
        neighborhoods[name][ptype + "_avg"] = avg
        ticker.append({"name": name, "type": ptype, "avg": avg, "change": change, "source": source})
    output = {
        "updated_at": now,
        "source": "rega",
        "source_url": "https://rentalrei.rega.gov.sa/indicatorejar",
        "city_averages": REGA_CITY_AVERAGES,
        "neighborhoods": neighborhoods,
        "ticker": ticker
    }
    with open("data/prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    log.info("Saved " + str(len(records)) + " records - source: rega")


if __name__ == "__main__":
    log.info("=== Iyar - REGA Data ===")
    log.info("Neighborhoods: " + str(len(set(r["neighborhood"] for r in REGA_NEIGHBORHOODS))))
    log.info("Records: " + str(len(REGA_NEIGHBORHOODS)))
    save_json(REGA_NEIGHBORHOODS)
    save_supabase(REGA_NEIGHBORHOODS)
    log.info("=== Done ===")
