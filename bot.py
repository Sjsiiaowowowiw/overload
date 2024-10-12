import telebot
import requests
from bs4 import BeautifulSoup
import time
from threading import Thread
import json
import os

bot = telebot.TeleBot('6748031892:AAFYLvQPnPcL3cOfh-BCzMcfDQF25Bzz1QE')

user_stats = {}
TOP_FILE = 'top.json'
blocked_users = {}

def generate_start_message():
    markup = telebot.types.InlineKeyboardMarkup()
    count_button = telebot.types.InlineKeyboardButton(text="COUNT", callback_data="count")
    top_button = telebot.types.InlineKeyboardButton(text="THE LEADER", callback_data="top")
    markup.add(count_button, top_button)
    
    return (
        "〽️ Welcome To HenryNET-DSTAT\n"
        "🐝 Owner: HenryNET-DEV\n", markup
    )

def generate_count_message(username):
    message = (
        f"〽️ Nosec Quý Cu To\n"
        f"🏝️ Nosec Quydepzai 🏝️\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"● Target: <blockquote>https://nosec.skibidi.sbs</blockquote>\n"
        f"🛡️ Protection Type: Nosec\n"
        f"⤷ Statistics Duration: 120 Seconds\n"
        f"⤷ Start Receiving Statistics From: {username}"
    )
    return message

def update_statistics(chat_id, username):
    target_url = "https://nosec.skibidi.sbs/nginx_status"
    total_visits = 0
    peak_visits = 0
    message_id = None
    end_time = time.time() + 120

    while user_stats.get(chat_id) == username and time.time() < end_time:
        response = requests.get(target_url)
        
        if response.status_code == 200:
            html_content = response.text
            waiting_connections = None
            for line in html_content.splitlines():
                if "Waiting" in line:
                    try:
                        waiting_connections = int(line.split(":")[1].strip().split()[0])
                    except ValueError:
                        waiting_connections = 0
            
            if waiting_connections is not None:
                peak_visits = max(peak_visits, waiting_connections)
                total_visits += waiting_connections

                current_date = time.strftime("%d/%m/%Y")
                current_time = time.strftime("%H:%M:%S")
                today = f"{current_date} {current_time}"

                result_message = (
                    f"<pre>"
                    f"🐝 Quý Đẹp Zai\n"
                    f"● Nosec Data Statistics\n"
                    f"➖➖➖➖➖➖➖➖➖➖\n"
                    f"⤷ Peak visits per second: {peak_visits}\n"
                    f"⤷ Average visits: {waiting_connections}\n"
                    f"⤷ Total visits: {total_visits}\n"
                    f"⤷ Today: {today}\n"
                    f"⤷ Nosec Data From: {username}\n"
                    f"⤷ Time Remaining: {int(end_time - time.time())} Seconds</pre>"
                )

                if message_id:
                    bot.edit_message_text(result_message, chat_id, message_id, parse_mode='HTML')
                else:
                    message = bot.send_message(chat_id, result_message, parse_mode='HTML')
                    message_id = message.message_id

                time.sleep(1)
            else:
                bot.send_message(chat_id, "Server Disconnected. Request Rejected.")
        else:
            bot.send_message(chat_id, "Server Disconnected. Request Rejected.")

    bot.send_message(chat_id, "DSTAT NOSEC Program Completed.", parse_mode='HTML')
    del blocked_users[chat_id]

@bot.message_handler(commands=['start'])
def handle_start(message):
    start_message, markup = generate_start_message()
    bot.send_message(message.chat.id, start_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["count", "top"])
def handle_callback_query(call):
    chat_id = call.message.chat.id
    username = call.from_user.username

    if call.data == "count":
        if chat_id in blocked_users:
            bot.send_message(chat_id, f"Wait A Minute. Receiving Data From @{blocked_users[chat_id]}")
            return
        
        user_stats[chat_id] = username
        blocked_users[chat_id] = username

        bot.send_message(chat_id, f"Data Request Received From @{username}")

        time.sleep(1)

        count_message = generate_count_message(username)
        bot.send_message(chat_id, count_message, parse_mode='HTML')

        Thread(target=update_statistics, args=(chat_id, username)).start()

    elif call.data == "top":
        if os.path.exists(TOP_FILE):
            with open(TOP_FILE, 'r') as f:
                top_data = json.load(f)
        else:
            top_data = {}

        if username in top_data:
            top_data[username] = user_stats.get(chat_id, 0)
        else:
            top_data[username] = 0
        
        with open(TOP_FILE, 'w') as f:
            json.dump(top_data, f, indent=4)

        sorted_top = sorted(top_data.items(), key=lambda x: x[1], reverse=True)[:10]

        top_message = "🏆 TOP DSTAT HenryNET 🏆\n"
        for i, (user, visits) in enumerate(sorted_top):
            top_message += f"Top {i+1}: @{user} | Total visits: {visits}\n"
        
        bot.send_message(chat_id, top_message, parse_mode='Markdown')

bot.polling()
