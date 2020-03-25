import discord
from discord.ext import commands
import datetime

TOKEN = 'NjkyNDYyMDMzMzk1Nzc3NTY2.Xnu8sQ.nX0UH4jhZrO-nNT9p6gRuCy-I7M'
bot = commands.Bot(command_prefix='$')


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!!")


@bot.command()
async def wiesel(ctx):
    file = discord.File("wiesel.jpg")
    await ctx.send("", file=file)


@bot.command()
async def quote(ctx, _quote, time=None):
    if time is None:
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
    with open('quotes.txt', 'a') as q:
        q.write(_quote + '/' + time + '\n')

    await ctx.send("Quote saved")


@bot.command()
async def clear(ctx, amount=100):
    for role in ctx.author.roles:

        if role == "Moderator" or discord.ext.commands.has_permissions(administrator=True):
            await ctx.channel.purge(limit=amount)
            await ctx.send("Channel cleared")
            return


@bot.command()
async def show_quotes(ctx):
    with open('quotes.txt') as f:
        lines = f.readlines()
        line_string = "".join(lines)
        await ctx.send(line_string)


@bot.event
async def on_ready():
    print("Bot ready")


def check_files():
    try:
        with open("quotes.txt", 'r') as _:
            pass

    except FileNotFoundError:
        with open('quotes.txt', 'w+') as _:
            pass

    try:
        with open("roles.json", 'r') as _:
            pass

    except FileNotFoundError:
        with open('roles.josn', 'w+') as _:
            pass


if __name__ == "__main__":
    check_files()
    bot.run(TOKEN)
