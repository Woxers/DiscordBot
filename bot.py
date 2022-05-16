import discord
import random
from discord.ext import commands
from config import settings

bot = commands.Bot(command_prefix=settings['prefix'])  # Создаем "тело" бота

@bot.event
async def on_ready():  # Event on_ready активируется когда бот готов к использованию
    print('Bot connected successfully!')

@bot.command()
async def randoms(ctx, arg):  # передаем arg аргумент (текст или же контент пользователя(не включая команду))
    try:  # Если у нас возникает ошибка при конвертировании нашего str в int, наша функция перейдет в except
        a = random.randint(0, int(arg))
    except:
        await ctx.send(f'Ошибка')  # Если в try возникает ошибка, мы возвращаем нулевое значение и пишем "Ошибка" в чат
        return
    await ctx.send(f'Ваше случайное число: {a}')  # Если всё хорошо, то функция вернет в чат наше случайное число


# Функцию выше можно модифицировать в более сложную, но более функциональную систему, но мне лень


@bot.command()
async def menu(ctx):  # Создаем комманду menu
    embed = discord.Embed(color=0xff9900, title='Help menu')  # Создание Embed
    embed.add_field(name='hello', value='bot say you hi!', inline=True)  # Добавляем контент в Embed
    await ctx.send(embed=embed)  # Отправка нашего меню сообщением


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


bot.run(settings['token'])  # Запускаем бота с помощью нашей библиотеки из файла config (опять же если он у вас есть)