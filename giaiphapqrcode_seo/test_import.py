# -*- coding: utf-8 -*-
"""
test_import.py - Test import fully_auto de tim loi
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Step 1: import os, sys, json...")
import os, json, time, requests, random

print("Step 2: import schedule...")
import schedule

print("Step 3: import smtplib, unicodedata, re, urllib...")
import smtplib, unicodedata, re, urllib.parse

print("Step 4: from datetime import datetime...")
from datetime import datetime, timedelta

print("Step 5: from bs4 import BeautifulSoup...")
from bs4 import BeautifulSoup

print("Step 6: from googlesearch import search...")
try:
    from googlesearch import search
    print("  OK")
except Exception as e:
    print(f"  WARN: {e}")

print("Step 7: import google.generativeai as genai...")
try:
    import google.generativeai as genai
    print("  OK")
except Exception as e:
    print(f"  WARN: {e}")

print("Step 8: from openai import OpenAI...")
from openai import OpenAI

print("Step 9: from plyer import notification...")
try:
    from plyer import notification
    print("  OK")
except Exception as e:
    print(f"  WARN: {e}")

print("Step 10: from dotenv import load_dotenv...")
from dotenv import load_dotenv
load_dotenv()

print("Step 11: from google_indexing import notify_google_index...")
try:
    from google_indexing import notify_google_index
    print("  OK")
except Exception as e:
    print(f"  WARN: {e}")

print("Step 12: from qwen_manager import chat_with_qwen...")
from qwen_manager import chat_with_qwen
print("  OK")

print("\n=== TAT CA IMPORT THANH CONG ===")
print("Thu goi run_daily_job()...")

# Test goi ham chinh
import importlib.util
spec = importlib.util.spec_from_file_location("auto", "fully_auto_giaiphapqrcode.py")
mod = importlib.util.module_from_spec(spec)

# Chi load module, khong execute __main__
import sys
sys.modules['auto_mod'] = mod

try:
    spec.loader.exec_module(mod)
    print("Module load OK")
    print("Goi run_daily_job()...")
    mod.run_daily_job()
except SystemExit:
    pass
except Exception as e:
    print(f"LOI: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
