import telebot
import requests

# Tomar information (Ami ready kore diechi)
BOT_TOKEN = '8650628100:AAHBaAmEq9uNEKlTigpIrTltf9Y6Q0hA6DA'
ADMIN_CHAT_ID = 7681403289  
MOTHERPANEL_API_KEY = '460733468183c2d213b961756f65935d' 
BKASH_NAGAD_NUMBER = '01794582008' 

MOTHERPANEL_API_URL = 'https://motherpanel.com/api/v2'

bot = telebot.TeleBot(BOT_TOKEN)
user_orders = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Zuxes SMM বটে আপনাকে স্বাগতম!**\n\n"
        "আমাদের সার্ভিসগুলো এবং তাদের আইডি নিচে দেওয়া হলো:\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🆔 **Service ID: 1** -> 1000 Facebook Followers [Price: 100 Taka]\n"
        "🆔 **Service ID: 2** -> 1000 YouTube Subscribers [Price: 300 Taka]\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🛒 **অর্ডার করার নিয়ম:**\n"
        "নিচের ফরম্যাটে মেসেজ দিন:\n"
        "`/order [সার্ভিস_আইডি] [লিঙ্ক]`\n\n"
        "💡 *উদাহরণ:* `/order 1 https://facebook.com/yourpage`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['order'])
def take_order(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            raise IndexError
            
        service_id = args[1]
        link = args[2]
        
        user_orders[message.chat.id] = {'service': service_id, 'link': link}
        
        payment_text = (
            f"💵 **পেমেন্ট ভেরিফিকেশন:**\n\n"
            f"অর্ডারটি কনফার্ম করতে আমাদের বিকাশ/নগদ পার্সোনাল নাম্বারে টাকা পাঠান:\n"
            f"📱 **নাম্বার:** `{BKASH_NAGAD_NUMBER}`\n\n"
            f"টাকা পাঠানোর পর ট্রানজেকশন আইডি (TxID) টি এখানে মেসেজ আকারে পাঠান।"
        )
        bot.reply_to(message, payment_text, parse_mode='Markdown')
        bot.register_next_step_handler(message, process_payment)
    except IndexError:
        bot.reply_to(message, "❌ ভুল ফরম্যাট! সঠিক নিয়ম: `/order [সার্ভিস_আইডি] [লিঙ্ক]`")

def process_payment(message):
    chat_id = message.chat.id
    txid = message.text
    
    if txid.startswith('/'):
        bot.send_message(chat_id, "❌ ভুল ইনপুট। আবার নতুন করে অর্ডার করুন।")
        return

    if chat_id in user_orders:
        service = user_orders[chat_id]['service']
        link = user_orders[chat_id]['link']
        
        admin_msg = (
            "🔔 **নতুন অর্ডার রিকোয়েস্ট এসেছে!**\n\n"
            f"👤 কাস্টমার ID: `{chat_id}`\n"
            f"📦 সার্ভিস ID: `{service}`\n"
            f"🔗 লিঙ্ক: {link}\n"
            f"💳 TxID: `{txid}`\n\n"
            f"সব ঠিক থাকলে অর্ডার মাদার প্যানেলে পাঠাতে নিচে ক্লিক করুন:\n"
            f"`/approve {chat_id}`"
        )
        bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='Markdown')
        bot.send_message(chat_id, "✅ আপনার পেমেন্ট তথ্য জমা হয়েছে। এডমিন ভেরিফাই করলেই সার্ভিস চালু হয়ে যাবে।")

@bot.message_handler(commands=['approve'])
def approve_order(message):
    if message.chat.id == ADMIN_CHAT_ID:
        try:
            args = message.text.split()
            target_user = int(args[1])
            
            if target_user in user_orders:
                service = user_orders[target_user]['service']
                link = user_orders[target_user]['link']
                
                payload = {
                    'key': MOTHERPANEL_API_KEY,
                    'action': 'add',
                    'service': service,
                    'link': link,
                    'quantity': 1000  
                }
                
                response = requests.post(MOTHERPANEL_API_URL, data=payload).json()
                
                if 'order' in response:
                    bot.send_message(ADMIN_CHAT_ID, f"🚀 সফল হয়েছে! মাদার প্যানেল অর্ডার ID: `{response['order']}`", parse_mode='Markdown')
                    bot.send_message(target_user, "🎉 অভিনন্দন! আপনার পেমেন্ট ভেরিফাইড এবং অর্ডারটি মাদার প্যানেলে সাকসেসফুলি সাবমিট হয়েছে।")
                    del user_orders[target_user]
                else:
                    bot.send_message(ADMIN_CHAT_ID, f"❌ মাদার প্যানেল এরর: {response.get('error', 'Unknown Error')}")
            else:
                bot.send_message(ADMIN_CHAT_ID, "❌ এই আইডির কোনো পেন্ডিং অর্ডার পাওয়া যায়নি।")
        except Exception as e:
            bot.send_message(ADMIN_CHAT_ID, f"❌ ভুল কমান্ড বা এরর: {str(e)}")

bot.infinity_polling()