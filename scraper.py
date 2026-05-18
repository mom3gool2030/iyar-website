name: 🔄 تحديث بيانات الأسعار

on:
  schedule:
    - cron: "0 0 * * *"
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  scrape:
    name: سحب البيانات وتحديث الموقع
    runs-on: ubuntu-latest

    steps:
      - name: 📥 سحب الكود
        uses: actions/checkout@v4

      - name: 🐍 إعداد Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: 📦 تثبيت المكتبات
        run: pip install requests beautifulsoup4 lxml

      - name: 🔍 تشغيل سكريبت السحب
        env:
          SUPABASE_URL: https://ojgrxarzmalfdxiqddrb.supabase.co
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scraper.py
