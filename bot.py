import telebot
import paramiko

TOKEN = "8723123923:AAG73I6jEGY3rd9Eq8Z_5e0rLXrYWdsCvw4"
bot = telebot.TeleBot(TOKEN)

user_state = {}

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Send VPS IP")
    user_state[msg.chat.id] = {}

@bot.message_handler(func=lambda m: True)
def handler(msg):
    cid = msg.chat.id
    text = msg.text.strip()

    if 'ip' not in user_state[cid]:
        user_state[cid]['ip'] = text
        bot.reply_to(msg, "Username?")
    elif 'user' not in user_state[cid]:
        user_state[cid]['user'] = text
        bot.reply_to(msg, "Password?")
    else:
        user_state[cid]['pass'] = text
        bot.reply_to(msg, "Installing... ⏳")

        ip = user_state[cid]['ip']
        user = user_state[cid]['user']
        pw = user_state[cid]['pass']

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=user, password=pw)
            
            cmd = "wget https://raw.githubusercontent.com/Kira0621/Auto-Vless/main/install.sh -O install.sh && bash install.sh"
            stdin, stdout, stderr = ssh.exec_command(cmd)

            result = stdout.read().decode()
            bot.reply_to(msg, "✅ Done:\n" + result)

        except Exception as e:
            bot.reply_to(msg, f"Error: {e}")

bot.infinity_polling()
