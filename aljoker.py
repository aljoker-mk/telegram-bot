
import time
import requests
import json
import re
import os
from datetime import datetime, date, timedelta
from urllib.parse import quote_plus
from pathlib import Path
import sqlite3
import telebot
from telebot import types
import threading
import random
import itertools

BASE = "http://139.99.63.204"
AJAX_PATH = "/ints/agent/res/data_smscdr.php"
LOGIN_PAGE_URL = BASE + "/ints/login"
LOGIN_POST_URL = BASE + "/ints/signin"
# ======================
# 🖥️ إعداد لوحات متعددة (2 لوحة الآن)
# ======================
DASHBOARD_CONFIGS = [
    {  # اللوحة الأولى (الأساسية)
        "name": "ALJOKER",
        "base": "http://139.99.63.204",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "aljoker",
        "password": "aljoker 135",
        "session": requests.Session(),
        "is_logged_in": False
    },
    {  # اللوحة الثانية (الاحتياطية)
        "name": "ALJOKER",
        "base": "http://109.236.84.81",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "aljoker",
        "password": "aljoker 135",
        "session": requests.Session(),
        "is_logged_in": False
    },
    {  # ✅ اللوحة الثالثة الجديدة
        "name": "ALJOKER",
        "base": "http://51.77.221.209",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "aljoker",
        "password": "aljoker 135",
        "session": requests.Session(),
        "is_logged_in": False
    },
    {
    	"name": "ALJOKER",
        "base": "http://109.236.84.81",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "aljoker",
        "password": "aljoker 135",
        "session": requests.Session(),
        "is_logged_in": False
    },
    {
    	"name": "ALJOKER",
        "base": "http://139.99.63.204",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "aljoker",
        "password": "aljoker 135",
        "session": requests.Session(),
        "is_logged_in": False
    }    	
]

# تهيئة headers موحدة
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8"
}

for dash in DASHBOARD_CONFIGS:
    dash["session"].headers.update(COMMON_HEADERS)
    login_page_url = dash["base"] + dash["login_page"]
    dash["login_page_url"] = login_page_url
    dash["login_post_url"] = dash["base"] + dash["login_post"]
    dash["ajax_url"] = dash["base"] + dash["ajax_path"]
USERNAME = "aljoker"
PASSWORD = "aljoker 135"
BOT_TOKEN = "8375502199:AAFCYbBYCCtVClsQ9zBhFFKbX2xXz5LHBAs"
CHAT_IDS = [
    "-1003101463702",
]
REFRESH_INTERVAL = 7
TIMEOUT = 100
MAX_RETRIES = 5
RETRY_DELAY = 5
IDX_DATE = 0
IDX_NUMBER = 2
IDX_SMS = 5
SENT_MESSAGES_FILE = "sent_messages.json"


ADMIN_IDS = [6987779200, 6987779200, 6987779200]  
DB_PATH = "bot.db"
FORCE_SUB_CHANNEL = None
FORCE_SUB_ENABLED = False


if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN must be set in Secrets (Environment Variables)")
if not CHAT_IDS:
    raise SystemExit("❌ CHAT_IDS must be configured")
if not USERNAME or not PASSWORD:
    print("⚠️  WARNING: SITE_USERNAME and SITE_PASSWORD not set in Secrets")
    print("⚠️  Bot will continue but login may fail")


COUNTRY_CODES = {
    "1": ("أمريكا / كندا (+1)", "🇺🇸", "USA/CANADA"),
    "7": ("كازخستان (+7)", "🇰🇿", "KAZAKHSTAN"),
    "20": ("مصر (+20)", "🇪🇬", "EGYPT"),
    "27": ("جنوب أفريقيا (+27)", "🇿🇦", "SOUTH AFRICA"),
    "30": ("اليونان (+30)", "🇬🇷", "GREECE"),
    "31": ("هولندا +(31)", "🇳🇱", "NETHERLANDS"),
    "32": ("بلجيكا (+32)", "🇧🇪", "BELGIUM"),
    "33": ("فرنسا (+33)", "🇫🇷", "FRANCE"),
    "34": ("إسبانيا (+34)", "🇪🇸", "SPAIN"),
    "36": ("هنغاريا (+36)", "🇭🇺", "HUNGARY"),
    "39": ("إيطاليا (+39)", "🇮🇹", "ITALY"),
    "40": ("رومانيا (+40)", "🇷🇴", "ROMANIA"),
    "41": ("سويسرا (+41)", "🇨🇭", "SWITZERLAND"),
    "43": ("النمسا (+43)", "🇦🇹", "AUSTRIA"),
    "44": ("المملكة المتحدة (+44)", "🇬🇧", "UK"),
    "45": ("الدنمارك (+45)", "🇩🇰", "DENMARK"),
    "46": ("السويد (+46)", "🇸🇪", "SWEDEN"),
    "47": ("النرويج (+47)", "🇳🇴", "NORWAY"),
    "48": ("بولندا (+48)", "🇵🇱", "POLAND"),
    "49": ("ألمانيا +(49)", "🇩🇪", "GERMANY"),
    "51": ("بيرو (+51)", "🇵🇪", "PERU"),
    "52": ("المكسيك +(52)", "🇲🇽", "MEXICO"),
    "53": ("كوبا (+53)", "🇨🇺", "CUBA"),
    "54": ("الأرجنتين (+54)", "🇦🇷", "ARGENTINA"),
    "55": ("البرازيل (+55)", "🇧🇷", "BRAZIL"),
    "56": ("تشيلي (+56)", "🇨🇱", "CHILE"),
    "57": ("كولومبيا (+57)", "🇨🇴", "COLOMBIA"),
    "58": ("فنزويلا (+58)", "🇻🇪", "VENEZUELA"),
    "60": ("ماليزيا +(60)", "🇲🇾", "MALAYSIA"),
    "61": ("أستراليا (+61)", "🇦🇺", "AUSTRALIA"),
    "62": ("أندونيسيا (+62)", "🇮🇩", "INDONESIA"),
    "63": ("الفلبين (+63)", "🇵🇭", "PHILIPPINES"),
    "64": ("نيوزيلندا (+64)", "🇳🇿", "NEW ZEALAND"),
    "65": ("سنغافورة (+65)", "🇸🇬", "SINGAPORE"),
    "66": ("تايلاند (+66)", "🇹🇭", "THAILAND"),
    "81": ("اليابان +(81)", "🇯🇵", "JAPAN"),
    "82": ("كوريا الجنوبية (+82)", "🇰🇷", "SOUTH KOREA"),
    "84": ("فيتنام +(84)", "🇻🇳", "VIETNAM"),
    "86": ("الصين (+86)", "🇨🇳", "CHINA"),
    "90": ("تركيا (+90)", "🇹🇷", "TURKEY"),
    "91": ("الهند (+91)", "🇮🇳", "INDIA"),
    "92": ("باكستان (+92)", "🇵🇰", "PAKISTAN"),
    "93": ("أفغانستان (+93)", "🇦🇫", "AFGHANISTAN"),
    "94": ("سيرلانكا +(+94)", "🇱🇰", "SRI LANKA"),
    "95": ("ميانمار (+95)", "🇲🇲", "MYANMAR"),
    "98": ("إيران (+98)", "🇮🇷", "IRAN"),
    "211": ("جنوب السودان (+211)", "🇸🇸", "SOUTH SUDAN"),
    "212": ("المغرب (+212)", "🇲🇦", "MOROCCO"),
    "213": ("الجزائر (+213)", "🇩🇿", "ALGERIA"),
    "216": ("تونس (+216)", "🇹🇳", "TUNISIA"),
    "218": ("ليبيا (+218)", "🇱🇾", "LIBYA"),
    "220": ("غامبيا (+220)", "🇬🇲", "GAMBIA"),
    "221": ("السنغال (+221)", "🇸🇳", "SENEGAL"),
    "222": ("موريتانيا (+222)", "🇲🇷", "MAURITANIA"),
    "223": ("مالي (+223)", "🇲🇱", "MALI"),
    "224": ("غينيا (+224)", "🇬🇳", "GUINEA"),
    "225": ("ساحل العاج", "🇨🇮", "IVORY COAST"),
    "226": ("بوركينا فاسو (+226)", "🇧🇫", "BURKINA FASO"),
    "227": ("النيجر (+227)", "🇳🇪", "NIGER"),
    "228": ("توغو (+228)", "🇹🇬", "TOGO"),
    "229": ("بنين (+229)", "🇧🇯", "BENIN"),
    "230": ("موريشيوس (+230)", "🇲🇺", "MAURITIUS"),
    "231": ("ليبيريا (+231)", "🇱🇷", "LIBERIA"),
    "232": ("سيراليون (+232)", "🇸🇱", "SIERRA LEONE"),
    "233": ("غانا (+233)", "🇬🇭", "GHANA"),
    "234": ("نيجيريا (+234)", "🇳🇬", "NIGERIA"),
    "235": ("تشاد (+235)", "🇹🇩", "CHAD"),
    "236": ("جمهورية أفريقيا الوسطى (+236)", "🇨🇫", "CENTRAL AFRICAN REP"),
    "237": ("الكاميرون (+237)", "🇨🇲", "CAMEROON"),
    "238": ("الرأس الأخضر (+238)", "🇨🇻", "CAPE VERDE"),
    "239": ("ساو تومي (+239)", "🇸🇹", "SAO TOME"),
    "240": ("غينيا الاستوائية (+240)", "🇬🇶", "EQUATORIAL GUINEA"),
    "241": ("الغابون (+241)", "🇬🇦", "GABON"),
    "242": ("الكونغو-برازافيل (+242)", "🇨🇬", "CONGO"),
    "243": ("الكونغو-كينشاسا (+243)", "🇨🇩", "DR CONGO"),
    "244": ("أنغولا (+244)", "🇦🇴", "ANGOLA"),
    "245": ("غينيا-بيساو (+245)", "🇬🇼", "GUINEA-BISSAU"),
    "248": ("سيشل (+248)", "🇸🇨", "SEYCHELLES"),
    "249": ("السودان (+249)", "🇸🇩", "SUDAN"),
    "250": ("رواندا (+250)", "🇷🇼", "RWANDA"),
    "251": ("إثيوبيا (+251)", "🇪🇹", "ETHIOPIA"),
    "252": ("الصومال (+252)", "🇸🇴", "SOMALIA"),
    "253": ("جيبوتي (+253)", "🇩🇯", "DJIBOUTI"),
    "254": ("كينيا (+254)", "🇰🇪", "KENYA"),
    "255": ("تنزانيا (+255)", "🇹🇿", "TANZANIA"),
    "256": ("أوغندا (+256)", "🇺🇬", "UGANDA"),
    "257": ("بوروندي (+257)", "🇧🇮", "BURUNDI"),
    "258": ("موزمبيق (+258)", "🇲🇿", "MOZAMBIQUE"),
    "260": ("زامبيا (+260)", "🇿🇲", "ZAMBIA"),
    "261": ("مدغشقر (+261)", "🇲🇬", "MADAGASCAR"),
    "262": ("روينيون (+262)", "🇷🇪", "REUNION"),
    "263": ("زيمبابوي (+263)", "🇿🇼", "ZIMBABWE"),
    "264": ("ناميبيا (+264)", "🇳🇦", "NAMIBIA"),
    "265": ("مالاوي (+265)", "🇲🇼", "MALAWI"),
    "266": ("ليسوتو (+266)", "🇱🇸", "LESOTHO"),
    "267": ("بوتسوانا (+267)", "🇧🇼", "BOTSWANA"),
    "268": ("إسواتيني (+268)", "🇸🇿", "ESWATINI"),
    "269": ("كومورس/جزر القمر (+269)", "🇰🇲", "COMOROS"),
    "350": ("جبل طارق (+350)", "🇬🇮", "GIBRALTAR"),
    "351": ("البرتغال (+351)", "🇵🇹", "PORTUGAL"),
    "352": ("لوكسمبورغ (+352)", "🇱🇺", "LUXEMBOURG"),
    "353": ("أيرلندا (+353)", "🇮🇪", "IRELAND"),
    "354": ("أيسلندا (+354)", "🇮🇸", "ICELAND"),
    "355": ("ألبانيا (+355)", "🇦🇱", "ALBANIA"),
    "356": ("مالطا (+356)", "🇲🇹", "MALTA"),
    "357": ("قبرص (+357)", "🇨🇾", "CYPRUS"),
    "358": ("فنلندا (+358)", "🇫🇮", "FINLAND"),
    "359": ("بلغاريا (+359)", "🇧🇬", "BULGARIA"),
    "370": ("ليتوانيا (+370)", "🇱🇹", "LITHUANIA"),
    "371": ("لاتفيا (+371)", "🇱🇻", "LATVIA"),
    "372": ("إستونيا (+372)", "🇪🇪", "ESTONIA"),
    "373": ("مولدوفا (+373)", "🇲🇩", "MOLDOVA"),
    "374": ("أرمينيا (+374)", "🇦🇲", "ARMENIA"),
    "375": ("بيلاروس (+375)", "🇧🇾", "BELARUS"),
    "376": ("أندورا (+376)", "🇦🇩", "ANDORRA"),
    "377": ("موناكو (+377)", "🇲🇨", "MONACO"),
    "378": ("سان مارينو (+278)", "🇸🇲", "SAN MARINO"),
    "380": ("أوكرانيا (+380)", "🇺🇦", "UKRAINE"),
    "381": ("صربيا (+381)", "🇷🇸", "SERBIA"),
    "382": ("مونتجرو/الجبل الأسود", "🇲🇪", "MONTENEGRO"),
    "383": ("كوسوفو (+383)", "🇽🇰", "KOSOVO"),
    "385": ("كرواتيا (+385)", "🇭🇷", "CROATIA"),
    "386": ("سلوفينيا (+386)", "🇸🇮", "SLOVENIA"),
    "387": ("البوسنا و الهرسك (+387)", "🇧🇦", "BOSNIA"),
    "389": ("مقدونيا الشمالية (+389)", "🇲🇰", "NORTH MACEDONIA"),
    "420": ("التشيك (+420)", "🇨🇿", "CZECH REPUBLIC"),
    "421": ("سلوفاكيا (+421)", "🇸🇰", "SLOVAKIA"),
    "423": ("ليختنشتاين (+423)", "🇱🇮", "LIECHTENSTEIN"),
    "500": ("جزر فوكلاند (+500)", "🇫🇰", "FALKLAND ISLANDS"),
    "501": ("بليز (+501)", "🇧🇿", "BELIZE"),
    "502": ("غواتيمالا (+502)", "🇬🇹", "GUATEMALA"),
    "503": ("السلفادور (+503)", "🇸🇻", "EL SALVADOR"),
    "504": ("هندوراس (+504)", "🇭🇳", "HONDURAS"),
    "505": ("نيكاراغوا (+505)", "🇳🇮", "NICARAGUA"),
    "506": ("كوستاريكا (+506)", "🇨🇷", "COSTA RICA"),
    "507": ("بناما (+507)", "🇵🇦", "PANAMA"),
    "509": ("هايتي (+509)", "🇭🇹", "HAITI"),
    "591": ("بوليفيا (+591)", "🇧🇴", "BOLIVIA"),
    "592": ("غيانا (+592)", "🇬🇾", "GUYANA"),
    "593": ("الإكوادور (+593)", "🇪🇨", "ECUADOR"),
    "595": ("باراغواي (+595)", "🇵🇾", "PARAGUAY"),
    "597": ("سورينام (+597)", "🇸🇷", "SURINAME"),
    "598": ("أوروغواي (+598)", "🇺🇾", "URUGUAY"),
    "670": ("تيمور - ليشتي (+670)", "🇹🇱", "TIMOR-LESTE"),
    "673": ("بروناي (+673)", "🇧🇳", "BRUNEI"),
    "674": ("ناورو (+674)", "🇳🇷", "NAURU"),
    "675": ("بابوا غينيا الجديدة (+675) ", "🇵🇬", "PAPUA NEW GUINEA"),
    "676": ("تونغا (+676)", "🇹🇴", "TONGA"),
    "677": ("جزر سليمان (+677)", "🇸🇧", "SOLOMON ISLANDS"),
    "678": ("فانواتو (+678)", "🇻🇺", "VANUATU"),
    "679": ("فيجي (+679)", "🇫🇯", "FIJI"),
    "680": ("بالاو (+680)", "🇵🇼", "PALAU"),
    "685": ("ساموا (+685)", "🇼🇸", "SAMOA"),
    "686": ("كيريباتي/كيريباس (+686)", "🇰🇮", "KIRIBATI"),
    "687": ("كاليدونيا الجديدة (+687)", "🇳🇨", "NEW CALEDONIA"),
    "688": ("توفالو (+688)", "🇹🇻", "TUVALU"),
    "689": ("بولينيزيا الفرنسية (+689)", "🇵🇫", "FRENCH POLYNESIA"),
    "691": ("ميكرونيزيا (+691)", "🇫🇲", "MICRONESIA"),
    "692": ("جزر مارشال (+692)", "🇲🇭", "MARSHALL ISLANDS"),
    "850": ("كوريا الشمالية (+850)", "🇰🇵", "NORTH KOREA"),
    "852": ("هونغ كونغ (+852)", "🇭🇰", "HONG KONG"),
    "853": ("ماكوا (+853)", "🇲🇴", "MACAU"),
    "855": ("كمبوديا (+855)", "🇰🇭", "CAMBODIA"),
    "856": ("لاوس (+856)", "🇱🇦", "LAOS"),
    "960": ("جزر المالديف (+960)", "🇲🇻", "MALDIVES"),
    "961": ("لبنان (+961)", "🇱🇧", "LEBANON"),
    "962": ("الأردن (+962)", "🇯🇴", "JORDAN"),
    "963": ("سوريا (+963)", "🇸🇾", "SYRIA"),
    "964": ("العراق (+964)", "🇮🇶", "IRAQ"),
    "965": ("الكويت (+965)", "🇰🇼", "KUWAIT"),
    "966": ("السعودية (+966)", "🇸🇦", "SAUDI ARABIA"),
    "967": ("اليمن (+967)", "🇾🇪", "YEMEN"),
    "968": ("عمان (+968)", "🇴🇲", "OMAN"),
    "970": ("فلسطين (+970)", "🇵🇸", "PALESTINE"),
    "971": ("الإمارات (+971)", "🇦🇪", "UAE"),
    "972": ("إسرائيل 👞💩 (+972)", "🇮🇱", "ISRAEL"),
    "973": ("البحرين (+973)", "🇧🇭", "BAHRAIN"),
    "974": ("قطر (+974)", "🇶🇦", "QATAR"),
    "975": ("بوتان (+975)", "🇧🇹", "BHUTAN"),
    "976": ("منغوليا (+976)", "🇲🇳", "MONGOLIA"),
    "977": ("نيبال (+977)", "🇳🇵", "NEPAL"),
    "992": ("طاجيكستان (+992)", "🇹🇯", "TAJIKISTAN"),
    "993": ("تركمانستان (+993)", "🇹🇲", "TURKMENISTAN"),
    "994": ("أذربيجان (+994)", "🇦🇿", "AZERBAIJAN"),
    "995": ("جورجيا (+995)", "🇬🇪", "GEORGIA"),
    "996": ("قرغيزستان (+996)", "🇰🇬", "KYRGYZSTAN"),
    "998": ("أوزبكستان (+998)", "🇺🇿", "UZBEKISTAN"),
}
# ======================
# 🧰 دوال إدارة قاعدة البيانات (محدثة)
# ======================
def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
# ======================
# 🧠 إنشاء قاعدة البيانات (مع جداول جديدة)
# ======================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            country_code TEXT,
            assigned_number TEXT,
            is_banned INTEGER DEFAULT 0,
            private_combo_country TEXT DEFAULT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS combos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT UNIQUE,
            numbers TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            otp TEXT,
            full_message TEXT,
            timestamp TEXT,
            assigned_to INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_url TEXT,
            ajax_path TEXT,
            login_page TEXT,
            login_post TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS private_combos (
            user_id INTEGER,
            country_code TEXT,
            numbers TEXT,
            PRIMARY KEY (user_id, country_code)
        )
    ''')
    # ✅ جدول القنوات الجديدة
    c.execute('''
        CREATE TABLE IF NOT EXISTS force_sub_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_url TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1
        )
    ''')

    # تهيئة الإعدادات القديمة (للتوافق مع البوت القديم)
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_channel', '')")
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_enabled', '0')")

    # 🔄 نقل القناة القديمة (إن وُجدت) تلقائيًا إلى الجدول الجديد
    c.execute("SELECT value FROM bot_settings WHERE key = 'force_sub_channel'")
    old_channel = c.fetchone()
    if old_channel and old_channel[0].strip():
        channel = old_channel[0].strip()
        # تأكد أنها ليست مكررة في الجدول الجديد
        c.execute("SELECT 1 FROM force_sub_channels WHERE channel_url = ?", (channel,))
        if not c.fetchone():
            enabled = 1 if get_setting("force_sub_enabled") == "1" else 0
            c.execute("INSERT INTO force_sub_channels (channel_url, description, enabled) VALUES (?, ?, ?)",
                      (channel, "القناة الأساسية", enabled))

    conn.commit()
    conn.close()

init_db()

# ======================
# 🧰 دوال إدارة قاعدة البيانات (محدثة)
# ======================


def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user(user_id, username="", first_name="", last_name="", country_code=None, assigned_number=None, private_combo_country=None):
    """
    يحفظ أو يحدّث بيانات المستخدم باستخدام استعلام واحد (INSERT OR REPLACE).
    هذا يمنع أخطاء التزامن (race conditions) في البيئات متعددة الخيوط.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # نحتاج إلى جلب البيانات القديمة التي لا نريد تغييرها إذا لم يتم توفيرها
    # هذا يمنع مسح البيانات القيمة مثل country_code عند استدعاء الدالة بمعلومات أساسية فقط
    existing_data = get_user(user_id)
    if existing_data:
        # إذا لم يتم توفير country_code جديد، استخدم القديم
        if country_code is None:
            country_code = existing_data[4]
        # إذا لم يتم توفير assigned_number جديد، استخدم القديم
        if assigned_number is None:
            assigned_number = existing_data[5]
        # إذا لم يتم توفير private_combo_country جديد، استخدم القديم
        if private_combo_country is None:
            private_combo_country = existing_data[7]

    c.execute("""
        REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_number, is_banned, private_combo_country)
        VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0), ?)
    """, (
        user_id,
        username,
        first_name,
        last_name,
        country_code,
        assigned_number,
        user_id, # يُستخدم في COALESCE لجلب حالة الحظر القديمة
        private_combo_country
    ))
    conn.commit()
    conn.close()


def ban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[6] == 1

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def get_combo(country_code, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("SELECT numbers FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        row = c.fetchone()
        if row:
            conn.close()
            return json.loads(row[0])
    c.execute("SELECT numbers FROM combos WHERE country_code=?", (country_code,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def save_combo(country_code, numbers, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?, ?, ?)",
                  (user_id, country_code, json.dumps(numbers)))
    else:
        c.execute("REPLACE INTO combos (country_code, numbers) VALUES (?, ?)",
                  (country_code, json.dumps(numbers)))
    conn.commit()
    conn.close()

def delete_combo(country_code, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("DELETE FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
    else:
        c.execute("DELETE FROM combos WHERE country_code=?", (country_code,))
    conn.commit()
    conn.close()

def get_all_combos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT country_code FROM combos")
    combos = [row[0] for row in c.fetchall()]
    conn.close()
    return combos

def assign_number_to_user(user_id, number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
    conn.commit()
    conn.close()

def get_user_by_number(number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def log_otp(number, otp, full_message, assigned_to=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?, ?, ?, ?, ?)",
              (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
    conn.commit()
    conn.close()

def release_number(old_number):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

def get_otp_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM otp_logs")
    logs = c.fetchall()
    conn.close()
    return logs

def get_user_info(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row
# --- دوال إدارة قنوات الاشتراك الإجباري (متعددة) ---
def get_all_force_sub_channels(enabled_only=True):
    """جلب القنوات (المفعلة فقط أو جميعها)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if enabled_only:
        c.execute("SELECT id, channel_url, description FROM force_sub_channels WHERE enabled = 1 ORDER BY id")
    else:
        c.execute("SELECT id, channel_url, description FROM force_sub_channels ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def add_force_sub_channel(channel_url, description=""):
    """إضافة قناة جديدة (لا تسمح بالتكرار)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO force_sub_channels (channel_url, description, enabled) VALUES (?, ?, 1)",
                  (channel_url.strip(), description.strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # قناة مكررة
    finally:
        conn.close()

def delete_force_sub_channel(channel_id):
    """حذف قناة بالرقم التعريفي"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM force_sub_channels WHERE id = ?", (channel_id,))
    changed = c.rowcount > 0
    conn.commit()
    conn.close()
    return changed

def toggle_force_sub_channel(channel_id):
    """تفعيل/تعطيل قناة"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE force_sub_channels SET enabled = 1 - enabled WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()
# ======================
# 🔐 دوال الاشتراك الإجباري
# ======================
def force_sub_check(user_id):
    """التحقق من اشتراك المستخدم في **جميع** القنوات المُفعَّلة"""
    channels = get_all_force_sub_channels(enabled_only=True)
    if not channels:
        return True  # لا توجد قنوات → لا يوجد تحقق

    for _, url, _ in channels:
        try:
            # توحيد التنسيق: @xxx بدل https://t.me/xxx
            if url.startswith("https://t.me/"):
                ch = "@" + url.split("/")[-1]
            elif url.startswith("@"):
                ch = url
            else:
                continue  # تجاهل الروابط غير الصحيحة
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print(f"[!] خطأ في التحقق من القناة {url}: {e}")
            return False  # أي فشل = غير مشترك
    return True

def force_sub_markup():
    """إنشاء زر لكل قناة مُفعَّلة + زر التحقق"""
    channels = get_all_force_sub_channels(enabled_only=True)
    if not channels:
        return None

    markup = types.InlineKeyboardMarkup()
    for _, url, desc in channels:
        text = f"📢 {desc}" if desc else "📢 اشترك في القناة"
        markup.add(types.InlineKeyboardButton(text, url=url))
    markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
    return markup
# ======================
# 🤖 إنشاء بوت Telegram
# ======================
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# 🎮 وظائف البوت التفاعلي
# ======================
def is_admin(user_id):
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "🚫 You are banned.")
        return
    if not force_sub_check(message.from_user.id):
        markup = force_sub_markup()
        if markup:
            bot.send_message(message.chat.id, "🔒 يجب الاشتراك في القناة لاستخدام البوت.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "🔒 الاشتراك الإجباري مفعل لكن لم يتم تحديد قناة!")
        return
    # إرسال إشعار للـ Admins عند دخول مستخدم جديد
    if not get_user(message.from_user.id):
        for admin in ADMIN_IDS:
            try:
                caption = f"🆕 مستخدم جديد دخل البوت:\n🆔: `{message.from_user.id}`\n👤: @{message.from_user.username or 'None'}\nالاسم: {message.from_user.first_name or ''} {message.from_user.last_name or ''}"
                if message.from_user.photo:
                    photo = bot.get_user_profile_photos(message.from_user.id).photos
                    if photo:
                        bot.send_photo(admin, photo[0][-1].file_id, caption=caption, parse_mode="Markdown")
                    else:
                        bot.send_message(admin, caption, parse_mode="Markdown")
                else:
                    bot.send_message(admin, caption, parse_mode="Markdown")
            except:
                pass
    save_user(
        message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or ""
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    user = get_user(message.from_user.id)
    private_combo = user[7] if user else None
    all_combos = get_all_combos()
    if private_combo and private_combo in COUNTRY_CODES:
        name, flag, _ = COUNTRY_CODES[private_combo]
        buttons.append(types.InlineKeyboardButton(f"{flag} {name} (Private)", callback_data=f"country_{private_combo}"))
    for code in all_combos:
        if code in COUNTRY_CODES and code != private_combo:
            name, flag, _ = COUNTRY_CODES[code]
            buttons.append(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"country_{code}"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    if is_admin(message.from_user.id):
        admin_btn = types.InlineKeyboardButton("🔐 لوحة الإدارة", callback_data="admin_panel")
        markup.add(admin_btn)
    bot.send_message(message.chat.id, "🌍 اختر الدولة 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if force_sub_check(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق! يمكنك استخدام البوت الآن.", show_alert=True)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def handle_country_selection(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
        return
    if not force_sub_check(call.from_user.id):
        markup = force_sub_markup()
        if markup:
            bot.send_message(call.message.chat.id, "🔒 يجب الاشتراك في القناة لاستخدام البوت.", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "🔒 الاشتراك الإجباري مفعل لكن لم يتم تحديد قناة!")
        return
    country_code = call.data.split("_", 1)[1]
    available_numbers = get_available_numbers(country_code, call.from_user.id)
    if not available_numbers:
        bot.edit_message_text("❌ جميع الأرقام قيد الاستخدام حاليًا.", call.message.chat.id, call.message.message_id)
        return
    assigned = random.choice(available_numbers)
    old_user = get_user(call.from_user.id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    assign_number_to_user(call.from_user.id, assigned)
    save_user(call.from_user.id, country_code=country_code, assigned_number=assigned)
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    msg_text = f"""📱 الرقم: 
    <code>{assigned}</code>
🌍 الدولة: {flag} {name}
⏳ في انتظار OTP..📱"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 تغيير الرقم ", callback_data=f"change_num_{country_code}"))
    markup.add(types.InlineKeyboardButton("🔙 تغيير الدولة", callback_data="back_to_countries"))
    bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_num_"))
def change_number(call):
    if is_banned(call.from_user.id):
        return
    if not force_sub_check(call.from_user.id):
        return
    country_code = call.data.split("_", 2)[2]
    available_numbers = get_available_numbers(country_code, call.from_user.id)
    if not available_numbers:
        bot.answer_callback_query(call.id, "❌ جميع الأرقام قيد الاستخدام.", show_alert=True)
        return
    old_user = get_user(call.from_user.id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    assigned = random.choice(available_numbers)
    assign_number_to_user(call.from_user.id, assigned)
    save_user(call.from_user.id, assigned_number=assigned)
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    msg_text = f"""📱 الرقم: 
    <code>{assigned}</code>
🌍 الدولة: {flag} {name}
⏳ في انتظار OTP..📱"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_num_{country_code}"))
    markup.add(types.InlineKeyboardButton("🔙 تغيير الدولة", callback_data="back_to_countries"))
    bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_countries")
def back_to_countries(call):
    # 1. بناء قائمة الأزرار (نفس المنطق من دالة send_welcome)
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    user = get_user(call.from_user.id)
    private_combo = user[7] if user else None
    all_combos = get_all_combos()

    # إضافة الكومبو الخاص أولاً إذا كان موجوداً
    if private_combo and private_combo in COUNTRY_CODES:
        name, flag, _ = COUNTRY_CODES[private_combo]
        buttons.append(types.InlineKeyboardButton(f"{flag} {name} (Private)", callback_data=f"country_{private_combo}"))

    # إضافة باقي الكومبوهات العامة
    for code in all_combos:
        if code in COUNTRY_CODES and code != private_combo:
            name, flag, _ = COUNTRY_CODES[code]
            buttons.append(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"country_{code}"))

    # ترتيب الأزرار في صفوف
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    # إضافة زر لوحة التحكم للمشرفين
    if is_admin(call.from_user.id):
        admin_btn = types.InlineKeyboardButton("🔐 لوحة الإدارة", callback_data="admin_panel")
        markup.add(admin_btn)

    # 2. تعديل الرسالة الحالية بدلاً من إرسال واحدة جديدة
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🌍 اختر الدولة 👇",
            reply_markup=markup
        )
    except Exception as e:
        # في حال حدوث خطأ (مثل عدم تغير محتوى الرسالة)، يتم تجاهله بأمان
        print(f"Error editing message: {e}")
        bot.answer_callback_query(call.id) # لإخفاء علامة التحميل من الزر


# ======================
# 🔐 لوحة التحكم الإدارية (محدثة)
# ======================
user_states = {}

def admin_main_menu():
    markup = types.InlineKeyboardMarkup()
    btns = [
        types.InlineKeyboardButton("📥 أضف ملف", callback_data="admin_add_combo"),
        types.InlineKeyboardButton("🗑️ احذف ملف", callback_data="admin_del_combo"),
        types.InlineKeyboardButton("📊 الاحصائيات", callback_data="admin_stats"),
        types.InlineKeyboardButton("📄 التقرير كامل", callback_data="admin_full_report"),
        types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ إلغاء حظر مستخدم", callback_data="admin_unban"),
        types.InlineKeyboardButton("📢 إذاعة للكل", callback_data="admin_broadcast_all"),
        types.InlineKeyboardButton("📨 إذاعة للمستخدمين", callback_data="admin_broadcast_user"),
        types.InlineKeyboardButton("👤 معلومات المستخدم", callback_data="admin_user_info"),
        types.InlineKeyboardButton("🔗 اشتراك إجباري", callback_data="admin_force_sub"),
        types.InlineKeyboardButton("🖥️ لوحات الأرقام", callback_data="admin_dashboards"),
        types.InlineKeyboardButton("👤 كومبو برايفت", callback_data="admin_private_combo"),
    ]
    for i in range(0, len(btns), 2):
        markup.row(*btns[i:i+2])
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel(call):
    if not is_admin(call.from_user.id):
        return
    bot.edit_message_text("🔐 لوحة الإدارة", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())

# ======================
# 📌 ميزة الاشتراك الإجباري في لوحة الإدارة
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_force_sub")
def admin_force_sub(call):
    if not is_admin(call.from_user.id):
        return

    channels = get_all_force_sub_channels(enabled_only=False)
    text = "⚙️ إدارة قنوات الاشتراك الإجباري:\n"
    text += f"إجمالي القنوات: {len(channels)}\n"
    text += "──────────────────\n"

    markup = types.InlineKeyboardMarkup()
    for ch_id, url, desc in channels:
        # جلب الحالة بدقة
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT enabled FROM force_sub_channels WHERE id=?", (ch_id,))
        enabled = c.fetchone()[0]
        conn.close()
        status = "✅" if enabled else "❌"
        btn_text = f"{status} {desc or url[:25]}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"edit_force_ch_{ch_id}"))

    markup.add(types.InlineKeyboardButton("➕ إضافة قناة", callback_data="add_force_ch"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


# --- إضافة قناة جديدة ---
@bot.callback_query_handler(func=lambda call: call.data == "add_force_ch")
def add_force_ch_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "add_force_ch_url"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_force_sub"))
    bot.edit_message_text("أرسل رابط القناة (مثل: https://t.me/xxx أو @xxx):", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_force_ch_url")
def add_force_ch_step2(message):
    url = message.text.strip()
    if not (url.startswith("@") or url.startswith("https://t.me/")):
        bot.reply_to(message, "❌ رابط غير صالح! يجب أن يبدأ بـ @ أو https://t.me/")
        return
    user_states[message.from_user.id] = {"step": "add_force_ch_desc", "url": url}
    bot.reply_to(message, "أدخل وصفًا للقناة (أو اترك فارغًا):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_force_ch_desc")
def add_force_ch_step3(message):
    data = user_states[message.from_user.id]
    url = data["url"]
    desc = message.text.strip()
    if add_force_sub_channel(url, desc):
        bot.reply_to(message, f"✅ تم إضافة القناة:\n{url}\nالوصف: {desc or '—'}")
    else:
        bot.reply_to(message, "❌ القناة موجودة مسبقًا!")
    del user_states[message.from_user.id]


# --- تعديل/حذف قناة فردية ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_force_ch_"))
def edit_force_ch(call):
    if not is_admin(call.from_user.id):
        return
    try:
        ch_id = int(call.data.split("_", 3)[3])
    except:
        return
    # جلب بيانات القناة
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT channel_url, description, enabled FROM force_sub_channels WHERE id=?", (ch_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ القناة غير موجودة!", show_alert=True)
        return

    url, desc, enabled = row
    status = "مفعلة" if enabled else "معطلة"
    text = f"🔧 إدارة القناة:\nالرابط: {url}\nالوصف: {desc or '—'}\nالحالة: {status}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ تعديل الوصف", callback_data=f"edit_desc_{ch_id}"))
    if enabled:
        markup.add(types.InlineKeyboardButton("❌ تعطيل", callback_data=f"toggle_ch_{ch_id}"))
    else:
        markup.add(types.InlineKeyboardButton("✅ تفعيل", callback_data=f"toggle_ch_{ch_id}"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"del_ch_{ch_id}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_force_sub"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_ch_"))
def toggle_ch(call):
    ch_id = int(call.data.split("_", 2)[2])
    toggle_force_sub_channel(ch_id)
    bot.answer_callback_query(call.id, "🔄 تم تغيير حالة القناة", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_ch_"))
def del_ch(call):
    ch_id = int(call.data.split("_", 2)[2])
    if delete_force_sub_channel(ch_id):
        bot.answer_callback_query(call.id, "✅ تم الحذف!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل الحذف!", show_alert=True)
    admin_force_sub(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_desc_"))
def edit_desc_step1(call):
    ch_id = int(call.data.split("_", 2)[2])
    user_states[call.from_user.id] = f"edit_desc_{ch_id}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data=f"edit_force_ch_{ch_id}"))
    bot.edit_message_text("أدخل الوصف الجديد:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), str) and user_states[msg.from_user.id].startswith("edit_desc_"))
def edit_desc_step2(message):
    try:
        ch_id = int(user_states[message.from_user.id].split("_")[2])
        desc = message.text.strip()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE force_sub_channels SET description = ? WHERE id = ?", (desc, ch_id))
        conn.commit()
        conn.close()
        bot.reply_to(message, "✅ تم تحديث الوصف!")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")
    del user_states[message.from_user.id]
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_combo")
def admin_add_combo(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "waiting_combo_file"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("📤 أرسل ملف الكومبو بصيغة TXT", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_combo_file(message):
    if not is_admin(message.from_user.id):
        return
    if user_states.get(message.from_user.id) != "waiting_combo_file":
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8')
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            bot.reply_to(message, "❌ الملف فارغ!")
            return
        first_num = clean_number(lines[0])
        country_code = None
        for code in COUNTRY_CODES:
            if first_num.startswith(code):
                country_code = code
                break
        if not country_code:
            bot.reply_to(message, "❌ لا يمكن تحديد الدولة من الأرقام!")
            return
        save_combo(country_code, lines)
        name, flag, _ = COUNTRY_CODES[country_code]
        bot.reply_to(message, f"✅ تم حفظ الكومبو لدولة {flag} {name}\n🔢 عدد الأرقام: {len(lines)}")
        del user_states[message.from_user.id]
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_combo")
def admin_del_combo(call):
    if not is_admin(call.from_user.id):
        return
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "لا توجد كومبوهات!")
        return
    markup = types.InlineKeyboardMarkup()
    for code in combos:
        if code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[code]
            markup.add(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"del_combo_{code}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("اختر الكومبو للحذف:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_combo_"))
def confirm_del_combo(call):
    if not is_admin(call.from_user.id):
        return
    code = call.data.split("_", 2)[2]
    delete_combo(code)
    name, flag, _ = COUNTRY_CODES.get(code, ("Unknown", "🌍", ""))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text(f"✅ تم حذف الكومبو: {flag} {name}", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id):
        return
    total_users = len(get_all_users())
    combos = get_all_combos()
    total_numbers = sum(len(get_combo(c)) for c in combos)
    otp_count = len(get_otp_logs())
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text(
        f"📊 إحصائيات البوت:\n"
        f"👥 المستخدمين النشطين: {total_users}\n"
        f"🌐 الدول المضافة: {len(combos)}\n"
        f"📞 إجمالي الأرقام: {total_numbers}\n"
        f"🔑 إجمالي الأكواد المستلمة: {otp_count}",
        call.message.chat.id, call.message.message_id, reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_full_report")
def admin_full_report(call):
    if not is_admin(call.from_user.id):
        return
    try:
        report = "📊 تقرير شامل عن البوت\n" + "="*40 + "\n\n"
        # المستخدمون
        report += "👥 المستخدمون:\n"
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        for u in users:
            status = "محظور" if u[6] else "نشط"
            report += f"ID: {u[0]} | @{u[1] or 'N/A'} | الرقم: {u[5] or 'N/A'} | الحالة: {status}\n"
        report += "\n" + "="*40 + "\n\n"
        # الأكواد
        report += "🔑 سجل الأكواد:\n"
        c.execute("SELECT * FROM otp_logs")
        logs = c.fetchall()
        for log in logs:
            user_info = get_user_info(log[5]) if log[5] else None
            user_tag = f"@{user_info[1]}" if user_info and user_info[1] else f"ID:{log[5] or 'N/A'}"
            report += f"الرقم: {log[1]} | الكود: {log[2]} | المستخدم: {user_tag} | الوقت: {log[4]}\n"
        conn.close()
        report += "\n" + "="*40 + "\n\n"
        report += "تم إنشاء التقرير في: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("bot_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        with open("bot_report.txt", "rb") as f:
            bot.send_document(call.from_user.id, f)
        os.remove("bot_report.txt")
        bot.answer_callback_query(call.id, "✅ تم إرسال التقرير!", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "admin_ban")
def admin_ban_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "ban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم لحظره:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "ban_user")
def admin_ban_step2(message):
    try:
        uid = int(message.text)
        ban_user(uid)
        bot.reply_to(message, f"✅ تم حظر المستخدم {uid}")
        del user_states[message.from_user.id]
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_unban")
def admin_unban_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "unban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم لفك حظره:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "unban_user")
def admin_unban_step2(message):
    try:
        uid = int(message.text)
        unban_user(uid)
        bot.reply_to(message, f"✅ تم فك حظر المستخدم {uid}")
        del user_states[message.from_user.id]
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_all")
def admin_broadcast_all_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "broadcast_all"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("أرسل الرسالة للإرسال للجميع:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_all")
def admin_broadcast_all_step2(message):
    users = get_all_users()
    success = 0
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ تم الإرسال إلى {success}/{len(users)} مستخدم")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_user")
def admin_broadcast_user_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "broadcast_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_user_id")
def admin_broadcast_user_step2(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = f"broadcast_msg_{uid}"
        bot.reply_to(message, "أرسل الرسالة:")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id, "").startswith("broadcast_msg_"))
def admin_broadcast_user_step3(message):
    uid = int(user_states[message.from_user.id].split("_")[2])
    try:
        bot.send_message(uid, message.text)
        bot.reply_to(message, f"✅ تم الإرسال للمستخدم {uid}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل: {e}")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_user_info")
def admin_user_info_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "get_user_info"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "get_user_info")
def admin_user_info_step2(message):
    try:
        uid = int(message.text)
        user = get_user_info(uid)
        if not user:
            bot.reply_to(message, "❌ المستخدم غير موجود!")
            return
        status = "محظور" if user[6] else "نشط"
        info = f"👤 معلومات المستخدم:\n"
        info += f"🆔: {user[0]}\n"
        info += f".Username: @{user[1] or 'N/A'}\n"
        info += f"الاسم: {user[2] or ''} {user[3] or ''}\n"
        info += f"الرقم المخصص: {user[5] or 'N/A'}\n"
        info += f"الحالة: {status}"
        bot.reply_to(message, info)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")
    del user_states[message.from_user.id]
@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "set_force_sub_channel")
def admin_set_force_sub_channel_step2(message):
    channel = message.text.strip()
    if not (channel.startswith("@") or channel.startswith("https://t.me/")):
        bot.reply_to(message, "❌ رابط غير صالح! يجب أن يبدأ بـ @ أو https://t.me/")
        return
    set_setting("force_sub_channel", channel)
    bot.reply_to(message, f"✅ تم تعيين القناة: {channel}")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_enable_force_sub")
def admin_enable_force_sub(call):
    set_setting("force_sub_enabled", "1")
    bot.answer_callback_query(call.id, "✅ تم تفعيل الاشتراك الإجباري!", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_disable_force_sub")
def admin_disable_force_sub(call):
    set_setting("force_sub_enabled", "0")
    bot.answer_callback_query(call.id, "❌ تم تعطيل الاشتراك الإجباري!", show_alert=True)
    admin_force_sub(call)

# ======================
# 🖥️ ميزة لوحات الأرقام المتعددة
# ======================
def get_dashboards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM dashboards")
    rows = c.fetchall()
    conn.close()
    return rows

def save_dashboard(base_url, ajax_path, login_page, login_post, username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO dashboards (base_url, ajax_path, login_page, login_post, username, password)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (base_url, ajax_path, login_page, login_post, username, password))
    conn.commit()
    conn.close()

def delete_dashboard(dash_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM dashboards WHERE id=?", (dash_id,))
    conn.commit()
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == "admin_dashboards")
def admin_dashboards(call):
    if not is_admin(call.from_user.id):
        return
    dashboards = get_dashboards()
    markup = types.InlineKeyboardMarkup()
    if dashboards:
        for d in dashboards:
            markup.add(types.InlineKeyboardButton(f"لوحة {d[0]}", callback_data=f"view_dashboard_{d[0]}"))
    markup.add(types.InlineKeyboardButton("➕ إضافة لوحة", callback_data="add_dashboard"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("🖥️ لوحات الأرقام:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_dashboard_"))
def view_dashboard(call):
    dash_id = int(call.data.split("_")[2])
    dashboards = get_dashboards()
    dash = next((d for d in dashboards if d[0] == dash_id), None)
    if not dash:
        bot.answer_callback_query(call.id, "❌ اللوحة غير موجودة!")
        return
    text = f"لوحة {dash_id}:\nBase: {dash[1]}\nUsername: {dash[5]}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"del_dashboard_{dash_id}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_dashboards"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_dashboard_"))
def del_dashboard(call):
    dash_id = int(call.data.split("_")[2])
    delete_dashboard(dash_id)
    bot.answer_callback_query(call.id, "✅ تم الحذف!", show_alert=True)
    admin_dashboards(call)

@bot.callback_query_handler(func=lambda call: call.data == "add_dashboard")
def add_dashboard_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "add_dash_base"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_dashboards"))
    bot.edit_message_text("أدخل Base URL:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_dash_base")
def add_dashboard_step2(message):
    user_states[message.from_user.id] = {"step": "ajax", "base": message.text}
    bot.reply_to(message, "أدخل AJAX Path:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "ajax")
def add_dashboard_step3(message):
    user_states[message.from_user.id]["ajax"] = message.text
    user_states[message.from_user.id]["step"] = "login_page"
    bot.reply_to(message, "أدخل Login Page URL:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "login_page")
def add_dashboard_step4(message):
    user_states[message.from_user.id]["login_page"] = message.text
    user_states[message.from_user.id]["step"] = "login_post"
    bot.reply_to(message, "أدخل Login POST URL:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "login_post")
def add_dashboard_step5(message):
    user_states[message.from_user.id]["login_post"] = message.text
    user_states[message.from_user.id]["step"] = "username"
    bot.reply_to(message, "أدخل Username:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "username")
def add_dashboard_step6(message):
    user_states[message.from_user.id]["username"] = message.text
    user_states[message.from_user.id]["step"] = "password"
    bot.reply_to(message, "أدخل Password:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "password")
def add_dashboard_step7(message):
    data = user_states[message.from_user.id]
    save_dashboard(
        data["base"],
        data["ajax"],
        data["login_page"],
        data["login_post"],
        data["username"],
        message.text
    )
    bot.reply_to(message, "✅ تم إضافة اللوحة بنجاح!")
    del user_states[message.from_user.id]

# ======================
# 👤 ميزة كومبو برايفت
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_private_combo")
def admin_private_combo(call):
    if not is_admin(call.from_user.id):
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة كومبو برايفت", callback_data="add_private_combo"))
    markup.add(types.InlineKeyboardButton("🗑️ مسح كومبو برايفت", callback_data="del_private_combo"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text("👤 كومبو برايفت:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_private_combo")
def add_private_combo_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "add_private_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_private_combo"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_private_user_id")
def add_private_combo_step2(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = f"add_private_country_{uid}"
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for code in get_all_combos():
            if code in COUNTRY_CODES:
                name, flag, _ = COUNTRY_CODES[code]
                buttons.append(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"select_private_{uid}_{code}"))
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i+2])
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_private_combo"))
        bot.reply_to(message, "اختر الدولة:", reply_markup=markup)
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_private_"))
def select_private_combo(call):
    parts = call.data.split("_")
    uid = int(parts[2])
    country_code = parts[3]
    save_user(uid, private_combo_country=country_code)
    name, flag, _ = COUNTRY_CODES[country_code]
    bot.answer_callback_query(call.id, f"✅ تم تعيين كومبو برايفت لـ {uid} - {flag} {name}", show_alert=True)
    admin_private_combo(call)

@bot.callback_query_handler(func=lambda call: call.data == "del_private_combo")
def del_private_combo_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "del_private_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_private_combo"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "del_private_user_id")
def del_private_combo_step2(message):
    try:
        uid = int(message.text)
        save_user(uid, private_combo_country=None)
        bot.reply_to(message, f"✅ تم مسح الكومبو البرايفت للمستخدم {uid}")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")
    del user_states[message.from_user.id]

# ======================
# 🆕 دالة جديدة: جلب الأرقام المتاحة (غير المستخدمة) مع دعم private
# ======================
def get_available_numbers(country_code, user_id=None):
    all_numbers = get_combo(country_code, user_id)
    if not all_numbers:
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number != ''")
    used_numbers = set(row[0] for row in c.fetchall())
    conn.close()
    available = [num for num in all_numbers if num not in used_numbers]
    return available

# ======================
# 🔄 الدالة المعدلة لإرسال OTP للمستخدم + الجروب
# ======================
def send_otp_to_user_and_group(date_str, number, sms):
    otp_code = extract_otp(sms)
    user_id = get_user_by_number(number)
    log_otp(number, otp_code, sms, user_id)
    if user_id:
        try:
            service = detect_service(sms)
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("Owner ~", url="https://t.me/XF_TX3"),
                types.InlineKeyboardButton("Channel", url="https://t.me/x_uuu_6")
            )
            bot.send_message(user_id, f"رمز OTP الخاص بك 🦂, ~ من {service}:\n🔑 <code>{otp_code}</code>", reply_markup=markup, parse_mode="HTML")
        except Exception as e:
            print(f"[!] فشل إرسال OTP للمستخدم {user_id}: {e}")
    msg = format_message(date_str, number, sms)
    send_to_telegram_group(msg)

# ======================
# 📡 دوال الاتصال بالـ Dashboard (كما هي من الملف الأصلي)
# ======================
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": BASE + "/ints/agent/SMSCDRReports",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8"
})

def retry_request(func, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    for attempt in range(max_retries):
        try:
            return func()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                print(f"⚠️  محاولة {attempt + 1}/{max_retries} فشلت: {type(e).__name__}")
                print(f"⏳ انتظار {retry_delay} ثانية قبل إعادة المحاولة...")
                time.sleep(retry_delay)
            else:
                print(f"❌ جميع المحاولات ({max_retries}) فشلت")
                raise
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
            raise

def login_for_dashboard(dash):
    print(f"[{dash['name']}] محاولة تسجيل الدخول...")
    def do_login():
        try:
            resp = dash["session"].get(dash["login_page_url"], timeout=TIMEOUT)
            match = re.search(r'What is (\d+) \+ (\d+)', resp.text)
            if not match:
                print(f"[{dash['name']}] ❌ لم يتم العثور على captcha في صفحة تسجيل الدخول")
                return False
            num1, num2 = int(match.group(1)), int(match.group(2))
            captcha_answer = num1 + num2
            print(f"[{dash['name']}] حل captcha: {num1} + {num2} = {captcha_answer}")

            payload = {
                "username": dash["username"],
                "password": dash["password"],
                "capt": str(captcha_answer)
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": dash["login_page_url"],
                "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }

            resp = dash["session"].post(dash["login_post_url"], data=payload, headers=headers, timeout=TIMEOUT)
            if ("dashboard" in resp.text.lower() or
                "logout" in resp.text.lower() or
                "/ints/agent" in resp.url or
                resp.url != dash["login_page_url"]):
                print(f"[{dash['name']}] ✅ تسجيل الدخول نجح")
                return True
            else:
                print(f"[{dash['name']}] ❌ فشل تسجيل الدخول")
                return False
        except Exception as e:
            print(f"[{dash['name']}] ❌ خطأ في تسجيل الدخول: {e}")
            raise

    try:
        return retry_request(do_login, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY)
    except:
        return False

is_logged_in = False

def build_ajax_url_for_dashboard(dash, wide_range=False):
    if wide_range:
        start_date = date.today() - timedelta(days=3650)
        end_date = date.today() + timedelta(days=1)
    else:
        start_date = date.today()
        end_date = date.today() + timedelta(days=1)

    fdate1 = f"{start_date.strftime('%Y-%m-%d')} 00:00:00"
    fdate2 = f"{end_date.strftime('%Y-%m-%d')} 23:59:59"

    q = (
        f"fdate1={quote_plus(fdate1)}&fdate2={quote_plus(fdate2)}&frange=&fclient=&fnum=&fcli=&fgdate=&fgmonth=&fgrange="
        f"&fgclient=&fgnumber=&fgcli=&fg=0&sEcho=1&iColumns=9&sColumns=%2C%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=5000"
        f"&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&mDataProp_8=8"
        f"&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_={int(time.time()*1000)}"
    )
    return dash["ajax_url"] + "?" + q

def fetch_ajax_json_for_dashboard(dash, url):
    def do_fetch():
        r = dash["session"].get(url, timeout=TIMEOUT)
        if r.status_code == 403 or ("login" in r.text.lower() and "login" in r.url.lower()):
            raise Exception("Session expired")
        r.raise_for_status()
        try:
            return r.json()
        except json.JSONDecodeError:
            raise Exception("Invalid JSON or redirected to login")

    try:
        return retry_request(do_fetch, max_retries=2, retry_delay=3)
    except Exception as e:
        if "Session expired" in str(e):
            print(f"[{dash['name']}] ⏳ الجلسة منتهية. إعادة تسجيل الدخول...")
            if login_for_dashboard(dash):
                dash["is_logged_in"] = True
                return retry_request(do_fetch, max_retries=2, retry_delay=3)
            else:
                dash["is_logged_in"] = False
                return None
        else:
            print(f"[{dash['name']}] ❌ خطأ في الجلب: {e}")
            return None

def extract_rows_from_json(j):
    if j is None:
        return []
    for key in ("data", "aaData", "rows", "aa_data"):
        if isinstance(j, dict) and key in j:
            return j[key]
    if isinstance(j, list):
        return j
    if isinstance(j, dict):
        for v in j.values():
            if isinstance(v, list):
                return v
    return []

def clean_html(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    return text

def clean_number(number):
    if not number:
        return ""
    number = re.sub(r'\D', '', str(number))
    return number

def row_to_tuple(row):
    date_str = ""
    number_str = ""
    sms_str = ""
    if isinstance(row, (list, tuple)):
        if len(row) > IDX_DATE:
            date_str = clean_html(row[IDX_DATE])
        if len(row) > IDX_NUMBER:
            number_str = clean_number(row[IDX_NUMBER])
        if len(row) > IDX_SMS:
            sms_str = clean_html(row[IDX_SMS])
    elif isinstance(row, dict):
        for k in ("date","time","datetime","dt","created_at"):
            if k in row and not date_str:
                date_str = clean_html(row[k])
        for k in ("number","msisdn","cli","from","sender"):
            if k in row and not number_str:
                number_str = clean_number(row[k])
        for k in ("sms","message","msg","body","text"):
            if k in row and not sms_str:
                sms_str = clean_html(row[k])
        if not sms_str:
            vals = list(row.values())
            if len(vals) > IDX_SMS:
                sms_str = clean_html(vals[IDX_SMS])
            elif vals:
                sms_str = clean_html(vals[-1])
    unique_key = f"{date_str}|{number_str}|{sms_str}"
    return date_str, number_str, sms_str, unique_key

def get_country_info(number):
    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
    for code, (name, flag, upper_name) in COUNTRY_CODES.items():
        if number.startswith(code):
            return name, flag, upper_name
    return "Unknown", "🌍", "UNKNOWN"

def mask_number(number):
    number = number.strip()
    if len(number) > 8:
        return number[:7] + "••" + number[-4:]
    return number

def extract_otp(message):
    patterns = [
        r'(?:code|رمز|كود|verification|تحقق|otp|pin)[:\s]+[‎]?(\d{3,8}(?:[- ]\d{3,4})?)',
        r'(\d{3})[- ](\d{3,4})',
        r'\b(\d{4,8})\b',
        r'[‎](\d{3,8})',
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            if len(match.groups()) > 1:
                return ''.join(match.groups())
            return match.group(1).replace(' ', '').replace('-', '')
    all_numbers = re.findall(r'\d{4,8}', message)
    if all_numbers:
        return all_numbers[0]
    return "N/A"

def detect_service(message):
    message_lower = message.lower()
    services = {
        "whatsapp": ["whatsapp", "واتساب", "واتس", "whats"],
        "facebook": ["facebook", "فيسبوك", "fb", "meta"],
        "instagram": ["instagram", "انستقرام", "انستا", "insta"],
        "telegram": ["telegram", "تيليجرام", "تلجرام"],
        "twitter": ["twitter", "تويتر", "x.com", "twitter/x"],
        "tiktok": ["tiktok", "تيك توك"],
        "snapchat": ["snapchat", "سناب شات", "snap"],
        "google": ["google", "جوجل", "gmail", "g-"],
        "uber": ["uber", "اوبر"],
        "careem": ["careem", "كريم"],
        "linkedin": ["linkedin", "لينكد ان", "لينكدان"],
        "youtube": ["youtube", "يوتيوب"],
        "netflix": ["netflix", "نتفليكس"],
        "amazon": ["amazon", "امازون"],
        "paypal": ["paypal", "باي بال"],
        "microsoft": ["microsoft", "مايكروسوفت", "outlook", "hotmail"],
        "apple": ["apple", "ابل", "icloud", "app store"],
        "discord": ["discord", "ديسكورد"],
        "reddit": ["reddit", "ريديت"],
        "pinterest": ["pinterest", "بينترست"],
        "twitch": ["twitch", "تويتش"],
        "spotify": ["spotify", "سبوتيفاي"],
        "viber": ["viber", "فايبر"],
        "wechat": ["wechat", "وي شات"],
        "line": ["line"],
        "signal": ["signal", "سيجنال"],
        "skype": ["skype", "سكايب"],
        "zoom": ["zoom", "زوم"],
        "teams": ["teams", "تيمز"],
        "steam": ["steam", "ستيم"],
        "ebay": ["ebay", "ايباي"],
        "alibaba": ["alibaba", "علي بابا"],
        "airbnb": ["airbnb", "اير بي ان بي"],
        "booking": ["booking", "بوكينج"],
        "shopify": ["shopify", "شوبيفاي"],
        "dropbox": ["dropbox", "دروب بوكس"],
        "onedrive": ["onedrive", "وان درايف"],
        "binance": ["binance", "بينانس"],
        "coinbase": ["coinbase", "كوين بيز"],
        "payoneer": ["payoneer", "بايونير"],
        "stripe": ["stripe", "سترايب"],
        "venmo": ["venmo", "فينمو"],
        "cashapp": ["cash app", "كاش اب"],
        "revolut": ["revolut", "ريفولوت"],
        "transferwise": ["wise", "transferwise", "وايز"],
        "tinder": ["tinder", "تيندر"],
        "bumble": ["bumble", "بامبل"],
        "yahoo": ["yahoo", "ياهو"],
        "bing": ["bing", "بينج"],
        "duckduckgo": ["duckduckgo"],
        "vk": ["vk", "vkontakte"],
        "ok": ["ok.ru", "odnoklassniki"],
        "yandex": ["yandex", "ياندكس"],
        "mailru": ["mail.ru"],
        "baidu": ["baidu", "بايدو"],
        "weibo": ["weibo", "ويبو"],
        "qq": ["qq"],
    }
    for service, keywords in services.items():
        for keyword in keywords:
            if keyword in message_lower:
                return service.upper()
    return "GENERAL"

def send_to_telegram_group(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "ADMIN", "url": "https://t.me/SAMT_963"},
            ],
            [
                {"text": "MAIN CHANNEL", "url": "https://t.me/aljoker_135"},
                {"text": "BACKUP CHANNEL", "url": "https://t.me/aljoker_13555"}
            ]
        ]
    }
    success_count = 0
    for chat_id in CHAT_IDS:
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(keyboard)
            }
            resp = requests.post(url, data=payload, timeout=10)
            if resp.status_code != 200:
                print(f"[!] فشل إرسال Telegram إلى {chat_id}: {resp.status_code}")
            else:
                print(f"[+] تم إرسال الرسالة إلى: {chat_id}")
                success_count += 1
        except Exception as e:
            print(f"[!] خطأ Telegram لـ {chat_id}: {e}")
    return success_count > 0

def html_escape(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "<")
            .replace(">", ">")
            .replace('"', "&quot;"))

def format_message(date_str, number, sms):
    country_name, country_flag, country_upper = get_country_info(number)
    masked_num = mask_number(number)
    otp_code = extract_otp(sms)
    service = detect_service(sms)
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        formatted_time = date_str
    if otp_code != "N/A":
        otp_display = html_escape(otp_code)
    else:
        otp_display = "N/A"
    sms_escaped = html_escape(sms)
    message = f"""<blockquote>{country_flag} <b>{country_name} {service} RECEIVED!</b> ✨</blockquote>
<blockquote>⏰ <b>Time:</b> {formatted_time}</blockquote>
<blockquote>🌍 <b>Country:</b> {country_name} {country_flag}</blockquote>
<blockquote>⚙️ <b>Service:</b> {service}</blockquote>
<blockquote>📞 <b>Number:</b> {masked_num}</blockquote>
<blockquote>🔑 <b>OTP:</b> {otp_display}</blockquote>
<blockquote>📩 <b>Full Message:</b>
{sms_escaped}</blockquote>"""
    return message

# ======================
# 🔄 الحلقة الرئيسية (معدلة لدعم لوحات متعددة)
# ======================
def main_loop():
    global REFRESH_INTERVAL
    REFRESH_INTERVAL = 5  # 5 ثواني لكل لوحة
    sent_messages = set()
    last_times = {dash["name"]: None for dash in DASHBOARD_CONFIGS}

    print("=" * 60)
    print("🚀 بدء مراقبة لوحتَين بالتناوب (كل 5 ثوانٍ)")
    print("=" * 60)

    # تسجيل الدخول المبدئي
    for dash in DASHBOARD_CONFIGS:
        if login_for_dashboard(dash):
            dash["is_logged_in"] = True
        else:
            print(f"[{dash['name']}] ⚠️ فشل في التسجيل الأولي — سيعاد المحاولة لاحقًا")

    # جلب آخر رسالة من كل لوحة (one-time wide fetch)
    print("\n🔍 جلب آخر رسالة من كل لوحة...")
    for dash in DASHBOARD_CONFIGS:
        try:
            url = build_ajax_url_for_dashboard(dash, wide_range=True)
            j = fetch_ajax_json_for_dashboard(dash, url)
            rows = extract_rows_from_json(j)
            if rows:
                valid_rows = [
                    row for row in rows
                    if isinstance(row, list) and len(row) > IDX_SMS and
                       (date_val := clean_html(row[IDX_DATE])) and '-' in date_val and ':' in date_val and
                       (num_val := clean_number(row[IDX_NUMBER])) and len(num_val) >= 10 and
                       (sms_val := clean_html(row[IDX_SMS])) and len(sms_val) > 5
                ]
                if valid_rows:
                    def get_datetime(row):
                        try:
                            return datetime.strptime(clean_html(row[IDX_DATE]), "%Y-%m-%d %H:%M:%S")
                        except:
                            return datetime.min
                    valid_rows.sort(key=get_datetime, reverse=True)
                    latest_row = valid_rows[0]
                    date_str, number, sms, key = row_to_tuple(latest_row)
                    if key not in sent_messages:
                        print(f"[{dash['name']}] ✅ آخر رسالة: {mask_number(number)} في {date_str}")
                        send_otp_to_user_and_group(date_str, number, sms)
                        sent_messages.add(key)
                        last_times[dash["name"]] = date_str
        except Exception as e:
            print(f"[{dash['name']}] ⚠️ خطأ في الجلب الأولي: {e}")

    print("\n✅ بدء المراقبة المستمرة (بالتناوب، كل 5 ثوانٍ)...\n" + "="*60)

    dash_cycle = itertools.cycle(DASHBOARD_CONFIGS)
    consecutive_errors = {dash["name"]: 0 for dash in DASHBOARD_CONFIGS}
    max_consecutive_errors = 5

    while True:
        dash = next(dash_cycle)
        try:
            print(f"[{dash['name']}] ⏱️ بدء دورة المراقبة...")
            if not dash["is_logged_in"]:
                print(f"[{dash['name']}] 🔁 إعادة تسجيل الدخول...")
                if login_for_dashboard(dash):
                    dash["is_logged_in"] = True
                else:
                    print(f"[{dash['name']}] ❌ فشل تسجيل الدخول — تجاوز هذه الدورة")
                    time.sleep(REFRESH_INTERVAL)
                    continue

            url = build_ajax_url_for_dashboard(dash)
            j = fetch_ajax_json_for_dashboard(dash, url)
            rows = extract_rows_from_json(j)

            if rows:
                valid_rows = [
                    row for row in rows
                    if isinstance(row, list) and len(row) > IDX_SMS and
                       (date_val := clean_html(row[IDX_DATE])) and '-' in date_val and ':' in date_val and
                       (num_val := clean_number(row[IDX_NUMBER])) and len(num_val) >= 10 and
                       (sms_val := clean_html(row[IDX_SMS])) and len(sms_val) > 5
                ]

                if valid_rows:
                    def get_datetime(row):
                        try:
                            return datetime.strptime(clean_html(row[IDX_DATE]), "%Y-%m-%d %H:%M:%S")
                        except:
                            return datetime.min
                    valid_rows.sort(key=get_datetime, reverse=True)
                    latest_row = valid_rows[0]
                    date_str, number, sms, key = row_to_tuple(latest_row)

                    if (last_times[dash["name"]] is None or date_str > last_times[dash["name"]]) and key not in sent_messages:
                        print(f"[{dash['name']}] 🆕 رسالة جديدة! الرقم: {mask_number(number)}")
                        send_otp_to_user_and_group(date_str, number, sms)
                        sent_messages.add(key)
                        last_times[dash["name"]] = date_str
                        consecutive_errors[dash["name"]] = 0
                    else:
                        print(f"[{dash['name']}] [=] لا رسائل جديدة")
                else:
                    print(f"[{dash['name']}] [=] لا رسائل صالحة")
            else:
                print(f"[{dash['name']}] [=] لا بيانات")

            # تنظيف sent_messages
            if len(sent_messages) > 1000:
                sent_messages = set(list(sent_messages)[-1000:])

        except KeyboardInterrupt:
            print("\n⛔ توقف يدوي")
            break
        except Exception as e:
            consecutive_errors[dash["name"]] += 1
            print(f"[{dash['name']}] ❌ خطأ ({consecutive_errors[dash['name']]}/{max_consecutive_errors}): {e}")
            if consecutive_errors[dash["name"]] >= max_consecutive_errors:
                print(f"[{dash['name']}] ⛔ إيقاف مؤقت للوحة بعد {max_consecutive_errors} أخطاء")
                time.sleep(30)
                consecutive_errors[dash["name"]] = 0

        time.sleep(REFRESH_INTERVAL)

# ======================
# ▶️ تشغيل البوت التفاعلي في خيط منفصل
# ======================
def run_bot():
    print("[*] Starting private bot...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    main_loop()