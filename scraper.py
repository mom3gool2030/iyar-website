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
    {"neighborhood":"الملقا","type":"شقة","min_price":45000,"max_price":62000,"avg_price":53500,"change_pct":4.2,"source":"fallback"},
    {"neighborhood":"الملقا","type":"فيلا","min_price":140000,"max_price":180000,"avg_price":160000,"change_pct":4.2,"source":"fallback"},
    {"neighborhood":"حطين","type":"شقة","min_price":50000,"max_price":68000,"avg_price":59000,"change_pct":-1.1,"source":"fallback"},
    {"neighborhood":"حطين","type":"فيلا","min_price":155000,"max_price":195000,"avg_price":175000,"change_pct":-1.1,"source":"fallback"},
    {"neighborhood":"الياسمين","type":"شقة","min_price":38000,"max_price":52000,"avg_price":45000,"change_pct":2.8,"source":"fallback"},
    {"neighborhood":"القيروان","type":"شقة","min_price":35000,"max_price":48000,"avg_price":41500,"change_pct":-0.8,"source":"fallback"},
    {"neighborhood":"السليمانية","type":"شقة","min_price":52000,"max_price":72000,"avg_price":62000,"change_pct":3.1,"source":"fallback"},
    {"neighborhood":"العليا","type":"شقة","min_price":55000,"max_price":75000,"avg_price":65000,"change_pct":6.3,"source":"fallback"},
    {"neighborhood":"الصحافة","type":"شقة","min_price":42000,"max_price":55000,"avg_price":48500,"change_pct":1.5,"source":"fallback"},
    {"neighborhood":"النرجس","type":"شقة","min_price":48000,"max_price":65000,"avg_price":56500,"change_pct":5.4,"source":"fallback"},
]

def get_token():
    log.info("Getting REGA token...")
    r = requests.post(REGA_BASE + "/GetToken", headers=HEADERS, json={}, timeout=15)
    token = r.text.strip().replace('"', '')
    log.info("Token O
