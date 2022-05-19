import discord

from discord.ext import commands

from libs import Database
from config import bot_settings, db_settings

bot = commands.Bot(command_prefix=bot_settings['prefix'])  # Создаем "тело" бота

db = Database()
user_id = "222746438814138368"
user_id1 = "1222746438814138368"
db.add_user(user_id)
db.set_status(user_id, "QUEUED")
db.set_nickname(user_id, "Woxerss")
db.set_name(user_id, "Артем")
db.update_reg_date(user_id)
if(db.check_user(user_id)):
    print("Есть в базе")
else:
    print("Нет в базе")
result = db.execute_query("SELECT * FROM users")

if (result != "ERROR"):
    for a in result:
        print(f"{a}")


db.__exit__()

@bot.event
async def on_ready():  # Event on_ready активируется когда бот готов к использованию
    print('Bot connected successfully!')

@bot.command()
async def hello(ctx):  # Создаем комманду hello
    author = ctx.message.author  # Создаем переменную author в которую занесем имя и тэг пользователя.
    await ctx.send(f'Hello, {author.mention}!')  # Используем метод .mention, который "тэгает" пользователя

@bot.command()
async def msg(ctx, *args):
    response = ""
    for arg in args: response = response + " " + arg

    user = await bot.fetch_user('222746438814138368')
    await user.send(response)


#bot.run(bot_settings['token'])  # Запускаем бота с помощью нашей библиотеки из файла config (опять же если он у вас есть)