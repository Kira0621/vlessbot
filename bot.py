import telebot
import paramiko

BOT_TOKEN = "8723123923:AAG73I6jEGY3rd9Eq8Z_5e0rLXrYWdsCvw4"
bot = telebot.TeleBot(BOT_TOKEN)

def run_install(ip, user, password, domain):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=user, password=password)

    sftp = ssh.open_sftp()
    sftp.put("installer.sh", "/root/installer.sh")
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command(f"bash /root/installer.sh {domain}")
    result = stdout.read().decode()

    ssh.close()
    return result

@bot.message_handler(commands=['install'])
def install(message):
    bot.reply_to(message, "Send VPS info like:\nIP USER PASS DOMAIN")

@bot.message_handler(func=lambda m: True)
def handle(message):
    ip, user, password, domain = message.text.split()
    output = run_install(ip, user, password, domain)
    bot.reply_to(message, f"Done ✅\n\n{output}")

bot.infinity_polling()
