import os
from flask import Flask, request
import telebot

# جلب توكن البوت من متغيرات البيئة في Render
TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN, threaded=False)

# هنا يبدأ Flask لإنشاء webhook endpoint
app = Flask(__name__)

# ===========
#  دوال البوت
# ===========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "البوت يعمل الآن عبر Render ✔️")

# ضع كل هاندلرات البوت الأصلية هنا
# (يمكن نسخها من ملف البوت الخاص بك)


# ==========================
#  نقطة استقبال webhook
# ==========================
@app.route(f"/webhook/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/", methods=['GET'])
def index():
    return "Bot is running", 200


# تشغيل Flask محليًا فقط (Render سيشغل عبر Gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
