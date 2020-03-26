import discord
from discord.ext import commands
from discord.utils import get
import datetime
import json

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


@bot.command()
async def ban(ctx, target):
    if "Moderator" in ctx.author.roles or discord.ext.commands.has_permissions(administrator=True):
        user = ctx.message.mentions[0]
        id = user.id
        roles = user.roles
        unremoveable = [635131535997141004, 635129654029713448, 635129654029713448, 635119155414302731]

        await ctx.message.delete()

        with open('roles.json', 'r') as r:
            try:
                data = json.load(r)
            except json.decoder.JSONDecodeError:
                data = {}

        with open('roles.json', 'w+') as r:
            data[id] = [role.id for role in roles if role.id not in unremoveable]
            r.write(json.dumps(data))

        for role in roles:
            if role.id not in unremoveable:
                await user.remove_roles(role)

        await user.add_roles([role for role in ctx.guild.roles if role.id == 690519972123770880][0])
        await ctx.send("I brought {}, where he belongs".format(user.mention))


@bot.command()
async def unban(ctx, target):
    user = ctx.message.mentions[0]
    id = user.id
    with open('roles.json', 'r') as r:
        data = json.load(r)

    roles = data[str(id)]
    for role_id in roles:
        await user.add_roles(get(ctx.guild.roles, id=role_id))

    await user.remove_roles(get(ctx.guild.roles, id=690519972123770880))

    del data[str(id)]
    with open('roles.json', 'w+') as r:
        r.write(json.dumps(data))


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
        with open('roles.json', 'w+') as r:
            r.write(json.dumps({}))


if __name__ == "__main__":
    check_files()
    bot.run(TOKEN)
